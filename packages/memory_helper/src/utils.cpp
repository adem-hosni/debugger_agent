#include "utils.h"
#include <string>
#include <algorithm>
#include <Psapi.h>

std::vector<utils::ModuleRange> utils::GetModulesRanges(HANDLE hProcess)
{
    std::vector<ModuleRange> modules;
    HMODULE                  hMods[1];
    DWORD                    cbNeeded;

    if (K32EnumProcessModules(hProcess, hMods, sizeof(hMods), &cbNeeded))
    {
        MODULEINFO mi;
        if (K32GetModuleInformation(hProcess, hMods[0], &mi, sizeof(mi)))
            modules.push_back({reinterpret_cast<uintptr_t>(mi.lpBaseOfDll), mi.SizeOfImage});
    }
    return modules;
}

bool utils::IsAddressInModule(std::vector<utils::ModuleRange>& modules, uintptr_t addr)
{
    for (auto& m : modules)
    {
        if (addr >= m.base && addr < m.base + m.size)
            return true;
    }
    return false;
}


bool utils::IsUserModule(HANDLE hProcess, LPVOID lpBaseAddress, DWORD dwSize)
{
    MODULEINFO mi;
    if (K32GetModuleInformation(hProcess, (HMODULE)lpBaseAddress, &mi, sizeof(mi)))
    {
        wchar_t path[MAX_PATH] = {};
        if (!GetModuleFileNameExW(hProcess, (HMODULE)mi.lpBaseOfDll, path, MAX_PATH))
            return false;            // couldn't resolve, treat as unknown/non-system

        wchar_t systemDir[MAX_PATH], windowsDir[MAX_PATH];
        GetSystemDirectoryW(systemDir, MAX_PATH);
        GetWindowsDirectoryW(windowsDir, MAX_PATH);

        std::wstring lowerPath = path;
        std::wstring sys = systemDir;
        std::wstring win = windowsDir;
        std::transform(lowerPath.begin(), lowerPath.end(), lowerPath.begin(), ::towlower);
        std::transform(sys.begin(), sys.end(), sys.begin(), ::towlower);
        std::transform(win.begin(), win.end(), win.begin(), ::towlower);

        return !(lowerPath.find(sys) == 0 || lowerPath.find(win + L"\\syswow64") == 0 || lowerPath.find(win + L"\\winsxs") == 0);

    }
    return false;
}

std::vector<utils::ModuleRange> utils::GetUserModules(HANDLE hProcess)
{
    std::vector<utils::ModuleRange> userModules;
    auto mods = utils::GetModulesRanges(hProcess);
    for (const auto& m : mods)
    {
        if (utils::IsUserModule(hProcess, (LPVOID)m.base, (DWORD)m.size))
            userModules.push_back(m);
    }
    return userModules;
}
