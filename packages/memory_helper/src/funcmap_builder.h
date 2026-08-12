#pragma once
#include "main.hpp"
#include <map>

namespace funcmap_builder
{
    struct stFunctionMap
    {
        std::string                      asmcode;
        std::map<DWORD64, stFunctionMap> subFunctions{};
    };

    BYTE*         parse_entrypoint(HMODULE hModule, BYTE* filebuffer);
    stFunctionMap map_functions(DWORD64 dwRuntimeAddress, void* buffer);

    stFunctionMap build_funcmap(HANDLE hProcess);
};            // namespace funcmap_builder
