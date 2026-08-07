#include "funcs.h"
#include <string>
#include <vector>
#include <Psapi.h>

#define NT_SUCCESS(Status) (((NTSTATUS)(Status)) >= 0)

struct ModuleRange
{
    uintptr_t base;
    uintptr_t size;
};

HANDLE funcs::open_process(DWORD process_id)
{
    HANDLE hProcess = ::OpenProcess(PROCESS_ALL_ACCESS, FALSE, process_id);
    if (hProcess == NULL)
    {
        printf("Failed to open process with ID %lu. Error: %lu\n", process_id, GetLastError());
        return NULL;
    }
    return hProcess;
}

bool get_code_section(HANDLE hProcess, PVOID base, DWORD& outRva, DWORD& outSize)
{
    IMAGE_DOS_HEADER dos{};
    SIZE_T           br = 0;
    if (!NT_SUCCESS(SysNtReadVirtualMemory(hProcess, base, &dos, sizeof(dos), &br)) || dos.e_magic != IMAGE_DOS_SIGNATURE)
        return false;

    IMAGE_NT_HEADERS nt{};
    PVOID            ntAddr = (PVOID)((BYTE*)base + dos.e_lfanew);
    if (!NT_SUCCESS(SysNtReadVirtualMemory(hProcess, ntAddr, &nt, sizeof(nt), &br)) || nt.Signature != IMAGE_NT_SIGNATURE)
        return false;

    DWORD                count = min(nt.FileHeader.NumberOfSections, 64u);
    IMAGE_SECTION_HEADER sec[64]{};
    PVOID                secAddr = (PVOID)((BYTE*)ntAddr + sizeof(IMAGE_NT_HEADERS));
    if (!NT_SUCCESS(SysNtReadVirtualMemory(hProcess, secAddr, sec, sizeof(IMAGE_SECTION_HEADER) * count, &br)))
        return false;

    for (DWORD i = 0; i < count; i++)
    {
        if (sec[i].Characteristics & IMAGE_SCN_MEM_EXECUTE)
        {
            outRva = sec[i].VirtualAddress;
            outSize = sec[i].Misc.VirtualSize;
            return true;
        }
    }
    return false;
}

// Returns just the main module (index 0 from EnumProcessModules is always the process's own exe).
std::vector<ModuleRange> GetMainModuleRange(HANDLE hProcess)
{
    std::vector<ModuleRange> modules;
    HMODULE                  hMods[1];
    DWORD                    cbNeeded;

    if (EnumProcessModules(hProcess, hMods, sizeof(hMods), &cbNeeded))
    {
        MODULEINFO mi;
        if (GetModuleInformation(hProcess, hMods[0], &mi, sizeof(mi)))
            modules.push_back({reinterpret_cast<uintptr_t>(mi.lpBaseOfDll), mi.SizeOfImage});
    }
    return modules;
}

bool IsAddressInModule(std::vector<ModuleRange>& modules, uintptr_t addr)
{
    for (auto& m : modules)
    {
        if (addr >= m.base && addr < m.base + m.size)
            return true;
    }
    return false;
}

funcs::Array funcs::collect_regions(HANDLE hProcess)
{
    auto ranges = GetMainModuleRange(hProcess);

    Array result{};
    if (hProcess == nullptr || hProcess == INVALID_HANDLE_VALUE)
        return result;

    std::vector<MEMORY_BASIC_INFORMATION> temp;
    temp.reserve(256);

    BYTE*                    address = nullptr;
    MEMORY_BASIC_INFORMATION mbi{};
    static const BYTE* const maxAddress = reinterpret_cast<const BYTE*>(0x00007FFFFFFEFFFFULL);
    constexpr DWORD          EXEC = PAGE_EXECUTE | PAGE_EXECUTE_READ | PAGE_EXECUTE_READWRITE | PAGE_EXECUTE_WRITECOPY;

    while (address < maxAddress)
    {
        SIZE_T q = VirtualQueryEx(hProcess, address, &mbi, sizeof(mbi));
        if (q == 0)
        {
            if (GetLastError() == ERROR_INVALID_PARAMETER)
                break;
            address += 0x1000;
            continue;
        }
        if (mbi.RegionSize == 0)
        {
            address += 0x1000;
            continue;
        }

        BYTE* nextAddress = reinterpret_cast<BYTE*>(mbi.BaseAddress) + mbi.RegionSize;

        bool ok = mbi.State == MEM_COMMIT && (mbi.Protect & EXEC) && !(mbi.Protect & (PAGE_NOACCESS | PAGE_GUARD)) &&
                  (mbi.Type == MEM_IMAGE || mbi.Type == MEM_PRIVATE);

        // Keep MEM_PRIVATE exec regions (JIT/shellcode, not tied to any module) unconditionally,
        // but only keep MEM_IMAGE regions that belong to the main module (skip system DLLs).
        if (ok && mbi.Type == MEM_IMAGE)
        {
            ok = IsAddressInModule(ranges, reinterpret_cast<uintptr_t>(mbi.BaseAddress));
        }

        if (ok)
        {
            MEMORY_BASIC_INFORMATION entry = mbi;
            if (mbi.Type == MEM_IMAGE)
            {
                DWORD rva = 0, size = 0;
                if (get_code_section(hProcess, mbi.AllocationBase, rva, size) && size > 0)
                {
                    printf("found code section \n");
                    entry.BaseAddress = (BYTE*)mbi.AllocationBase + rva;
                    entry.RegionSize = size;
                }
            }
            temp.push_back(entry);
        }

        address = nextAddress;
    }

    if (temp.empty())
        return result;

    auto* buffer = static_cast<MEMORY_BASIC_INFORMATION*>(malloc(sizeof(MEMORY_BASIC_INFORMATION) * temp.size()));
    if (!buffer)
        return result;

    memcpy(buffer, temp.data(), sizeof(MEMORY_BASIC_INFORMATION) * temp.size());
    result.data = reinterpret_cast<char*>(buffer);
    result.size = temp.size();
    result.len = static_cast<int>(temp.size());
    return result;
}

char* funcs::disassemble_region(HANDLE hProcess, SIZE_T size, ULONG_PTR address)
{
    if (size == 0)
        return nullptr;

    PVOID  buffer = nullptr;
    SIZE_T regionSize = size;
    if (!NT_SUCCESS(SysNtAllocateVirtualMemory(GetCurrentProcess(), &buffer, 0, &regionSize, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE)))
        return nullptr;

    SIZE_T bytesRead = 0;
    if (!NT_SUCCESS(SysNtReadVirtualMemory(hProcess, (PVOID)address, buffer, size, &bytesRead)) || bytesRead == 0)
    {
        SIZE_T freeSize = 0;
        SysNtFreeVirtualMemory(GetCurrentProcess(), &buffer, &freeSize, MEM_RELEASE);
        return nullptr;
    }

    std::vector<std::pair<DWORD, std::string>> lines;
    lines.reserve(size / 3);

    ZyanUSize                    offset = 0;
    ZydisDisassembledInstruction instr;
    char                         buf[256];

    while (offset < size)
    {
        DWORD      ip = static_cast<DWORD>(address) + static_cast<DWORD>(offset);
        ZyanStatus status = ZydisDisassembleIntel(ZYDIS_MACHINE_MODE_LONG_64, ip, reinterpret_cast<const uint8_t*>(buffer) + offset, size - offset, &instr);

        if (!ZYAN_SUCCESS(status))
        {
            sprintf_s(buf, sizeof(buf), "db %02X", static_cast<uint8_t>(((char*)buffer)[offset]));
            lines.emplace_back(ip, buf);
            offset += 1;
            continue;
        }
        lines.emplace_back(ip, instr.text);
        offset += instr.info.length;
    }

    SIZE_T freeSize = 0;
    SysNtFreeVirtualMemory(GetCurrentProcess(), &buffer, &freeSize, MEM_RELEASE);

    std::string output;
    output.reserve(lines.size() * 24);
    size_t i = 0;
    while (i < lines.size())
    {
        bool   isDb = lines[i].second.rfind("db ", 0) == 0;
        size_t j = i;
        if (isDb)
        {
            while (j < lines.size() && lines[j].second.rfind("db ", 0) == 0)
                j++;
        }
        else
        {
            while (j < lines.size() && lines[j].second == lines[i].second)
                j++;
        }
        size_t run = j - i;

        if (run >= 4)
        {
            if (isDb)
                sprintf_s(buf, sizeof(buf), "%08X  db ... (%zu bytes, through %08X)\n", lines[i].first, run, lines[j - 1].first);
            else
                sprintf_s(buf, sizeof(buf), "%08X  %s   (x%zu, through %08X)\n", lines[i].first, lines[i].second.c_str(), run, lines[j - 1].first);
            output += buf;
        }
        else
        {
            for (size_t k = i; k < j; k++)
            {
                sprintf_s(buf, sizeof(buf), "%08X  %s\n", lines[k].first, lines[k].second.c_str());
                output += buf;
            }
        }
        i = j;
    }

    char* result = static_cast<char*>(malloc(output.size() + 1));
    if (result)
        memcpy(result, output.c_str(), output.size() + 1);
    return result;
}