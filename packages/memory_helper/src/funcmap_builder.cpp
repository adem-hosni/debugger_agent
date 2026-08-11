#include <fstream>
#include <sstream>
#include "funcmap_builder.h"
#include "utils.h"

BYTE* funcmap_builder::parse_entrypoint(BYTE* filebuffer)
{
    IMAGE_DOS_HEADER* dosHeader = (IMAGE_DOS_HEADER*)filebuffer;
    if (dosHeader->e_magic != IMAGE_DOS_SIGNATURE)
        return nullptr;
    IMAGE_NT_HEADERS* ntHeaders = (IMAGE_NT_HEADERS*)(filebuffer + dosHeader->e_lfanew);
    if (ntHeaders->Signature != IMAGE_NT_SIGNATURE)
        return nullptr;
    DWORD                 entryRVA = ntHeaders->OptionalHeader.AddressOfEntryPoint;
    IMAGE_SECTION_HEADER* sec = IMAGE_FIRST_SECTION(ntHeaders);
    DWORD                 fileOffset = 0;
    for (int i = 0; i < ntHeaders->FileHeader.NumberOfSections; i++, sec++)
    {
        if (entryRVA >= sec->VirtualAddress && entryRVA < sec->VirtualAddress + sec->Misc.VirtualSize)
        {
            fileOffset = entryRVA - sec->VirtualAddress + sec->PointerToRawData;
            break;
        }
    }

    BYTE* entryBytes = filebuffer + fileOffset;

    return entryBytes;
}

funcmap_builder::stFunctionMap funcmap_builder::map_functions(DWORD64 dwRuntimeAddress, void* buffer)
{
    stFunctionMap functionMap;

    ZydisDecoder decoder;
    ZydisDecoderInit(&decoder, ZYDIS_MACHINE_MODE_LONG_64, ZYDIS_STACK_WIDTH_64);

    ZydisFormatter formatter;
    ZydisFormatterInit(&formatter, ZYDIS_FORMATTER_STYLE_INTEL);

    ZyanUSize               offset = 0;
    ZydisDecodedInstruction instr;
    ZydisDecodedOperand     operands[ZYDIS_MAX_OPERAND_COUNT];

    std::string output;
    for (int i = 0; i < 20 && ZYAN_SUCCESS(ZydisDecoderDecodeFull(&decoder, buffer, 0x20, &instr, operands)); i++)
    {
        char buf[256];
        ZydisFormatterFormatInstruction(&formatter, &instr, operands, instr.operand_count_visible, buf, sizeof(buf), dwRuntimeAddress + offset, NULL);

        char addrbuf[32];
        memset(addrbuf, 0, sizeof(addrbuf));
        sprintf(addrbuf, "%016llX  ", dwRuntimeAddress + offset);
        output += addrbuf;
        output += buf;
        output += "\n";

        if (instr.meta.category == ZYDIS_CATEGORY_COND_BR || (instr.meta.category == ZYDIS_CATEGORY_UNCOND_BR && instr.mnemonic == ZYDIS_MNEMONIC_JMP))
        {
            if (operands[0].type == ZYDIS_OPERAND_TYPE_IMMEDIATE)
            {
                ZyanU64 target_address = 0;
                ZydisCalcAbsoluteAddress(&instr, &operands[0], dwRuntimeAddress, &target_address);

                functionMap.subFunctions[(DWORD64)target_address] = map_functions(target_address, (BYTE*)buffer + offset + instr.length);
            }
        }
        offset += instr.length;
    }

    functionMap.asmcode = output;

    return functionMap;
};

funcmap_builder::stFunctionMap funcmap_builder::build_funcmap(HANDLE hProcess)
{
    auto mods = utils::GetUserModules(hProcess);

    char  szFilePath[MAX_PATH];
    DWORD dwSize = MAX_PATH;

    if (QueryFullProcessImageName(hProcess, NULL, szFilePath, &dwSize))
    {
        std::ifstream      file(szFilePath);
        std::ostringstream ss;
        ss << file.rdbuf();
        const char* filebuffer = ss.str().c_str();
        BYTE*       entrypoint_address = parse_entrypoint((BYTE*)filebuffer);

        return map_functions((DWORD64)entrypoint_address, entrypoint_address);
    }
    return (stFunctionMap) nullptr;
}
