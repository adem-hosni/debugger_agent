#define _CRT_SECURE_NO_WARNINGS

#include <fstream>
#include <sstream>
#include <Zydis/Zydis.h>
#include "kernel_calls.hpp"
#include "funcmap_builder.h"
#include "utils.h"

funcmap_builder::C_FunctionMap* funcmap_builder::ConvertToC(stFunctionMap* cppMap)
{
    auto* cMap = new C_FunctionMap();
    cMap->asmcode = cppMap->asmcode.c_str();
    cMap->subCount = cppMap->subFunctions.size();
    if (cMap->subCount > 0)
    {
        cMap->subKeys = new DWORD64[cMap->subCount];
        cMap->subValues = new C_FunctionMap[cMap->subCount];
        size_t i = 0;
        for (auto& [key, value] : cppMap->subFunctions)
        {
            cMap->subKeys[i] = key;
            cMap->subValues[i] = *ConvertToC(&value);
            i++;
        }
    }
    else
    {
        cMap->subKeys = nullptr;
        cMap->subValues = nullptr;
    }
    return cMap;
}

DWORD64 funcmap_builder::parse_entrypoint(DWORD64 dwProcessBaseAddress, const char* filebuffer)
{
    IMAGE_DOS_HEADER* dosHeader = (IMAGE_DOS_HEADER*)filebuffer;
    if (dosHeader->e_magic != IMAGE_DOS_SIGNATURE)
        return 0;
    IMAGE_NT_HEADERS* ntHeaders = (IMAGE_NT_HEADERS*)(filebuffer + dosHeader->e_lfanew);
    if (ntHeaders->Signature != IMAGE_NT_SIGNATURE) 
        return 0;
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
    return (DWORD64)dwProcessBaseAddress + entryRVA;
}

funcmap_builder::stFunctionMap funcmap_builder::map_functions(HANDLE hProcess, DWORD64 dwRuntimeAddress, std::set<DWORD64>& visitedAddresses)
{
    printf("Mapping function at address: %p", (PVOID)dwRuntimeAddress);
    MEMORY_BASIC_INFORMATION MemoryRegion{};
    SIZE_T                   returnLength = 0;
    if (!NT_SUCCESS(SysNtQueryVirtualMemory(hProcess, (PVOID)dwRuntimeAddress, MemoryBasicInformation, &MemoryRegion, sizeof(MemoryRegion), &returnLength)))
    {
        printf("Failed to query function memory at address: %p\n", (PVOID)dwRuntimeAddress);
        return {};
    }
    printf(" Region Size: 0x%zx bytes\n", MemoryRegion.RegionSize);
    std::vector<BYTE> buffer(MemoryRegion.RegionSize, 0);
    if (!NT_SUCCESS(SysNtReadVirtualMemory(hProcess, (PVOID)dwRuntimeAddress, buffer.data(), MemoryRegion.RegionSize, NULL)))
    {
        printf("Failed to read function memory at address: %p\n", (PVOID)dwRuntimeAddress);
        return {};
    }
    stFunctionMap functionMap;
    ZydisDecoder  decoder;
    ZydisDecoderInit(&decoder, ZYDIS_MACHINE_MODE_LONG_64, ZYDIS_STACK_WIDTH_64);
    ZydisFormatter formatter;
    ZydisFormatterInit(&formatter, ZYDIS_FORMATTER_STYLE_INTEL);
    ZyanUSize               offset = 0;
    ZydisDecodedInstruction instr;
    ZydisDecodedOperand     operands[ZYDIS_MAX_OPERAND_COUNT];
    std::string             output;
    while (offset < MemoryRegion.RegionSize &&
           ZYAN_SUCCESS(ZydisDecoderDecodeFull(&decoder, buffer.data() + offset, MemoryRegion.RegionSize - offset, &instr, operands)))
    {
        ZyanU64 current_instr_address = dwRuntimeAddress + offset;
        char    buf[256];
        ZydisFormatterFormatInstruction(&formatter, &instr, operands, instr.operand_count_visible, buf, sizeof(buf), current_instr_address, NULL);
        char addrbuf[32];
        sprintf_s(addrbuf, sizeof(addrbuf), "%016llX  ", current_instr_address);
        output += addrbuf;
        output += buf;
        output += "\n";
        if (instr.meta.category == ZYDIS_CATEGORY_COND_BR || instr.meta.category == ZYDIS_CATEGORY_UNCOND_BR || instr.meta.category == ZYDIS_CATEGORY_CALL)
        {
            if (instr.operand_count > 0 && operands[0].type == ZYDIS_OPERAND_TYPE_IMMEDIATE)
            {
                ZyanU64 target_address = 0;
                if (ZYAN_SUCCESS(ZydisCalcAbsoluteAddress(&instr, &operands[0], current_instr_address, &target_address)))
                {
                    DWORD64 target64 = (DWORD64)target_address;
                    if (visitedAddresses.find(target64) == visitedAddresses.end())
                    {
                        visitedAddresses.insert(target64);
                        functionMap.subFunctions[target64] = map_functions(hProcess, target64, visitedAddresses);
                    }
                }
            }
        }
        if (instr.mnemonic == ZYDIS_MNEMONIC_INT3 && (offset + instr.length < MemoryRegion.RegionSize))
        {
            if (buffer[offset + instr.length] == 0xCC)
            {
                offset += instr.length;
                break;
            }
        }
        offset += instr.length;
    }
    functionMap.asmcode = output;
    return functionMap;
}

funcmap_builder::stFunctionMap funcmap_builder::build_funcmap(HANDLE hProcess)
{
    auto  mods = utils::GetUserModules(hProcess);
    char  szFilePath[MAX_PATH];
    DWORD dwSize = MAX_PATH;
    if (QueryFullProcessImageName(hProcess, NULL, szFilePath, &dwSize))
    {
        std::ifstream      file(szFilePath, std::ios::binary);
        std::ostringstream ss;
        ss << file.rdbuf();
        auto              str = ss.str();
        const char*       filebuffer = str.data();
        DWORD64           entrypoint_address = parse_entrypoint((DWORD64)mods[0].base, filebuffer);
        std::set<DWORD64> visitedAddresses;
        return map_functions(hProcess, entrypoint_address, visitedAddresses);
    }
    return {};
}
