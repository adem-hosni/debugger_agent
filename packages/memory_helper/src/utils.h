#pragma once
#include <vector>
#include <Windows.h>

namespace utils
{
    struct ModuleRange
    {
        uintptr_t base;
        uintptr_t size;
    };


    std::vector<ModuleRange> GetModulesRanges(HANDLE hProcess);
    bool                     IsAddressInModule(std::vector<ModuleRange>& modules, uintptr_t addr);
    bool                     IsUserModule(HANDLE hProcess, LPVOID lpBaseAddress, DWORD dwSize);
    std::vector<ModuleRange> GetUserModules(HANDLE hProcess);
};
