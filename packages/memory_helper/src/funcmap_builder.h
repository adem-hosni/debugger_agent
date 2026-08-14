#pragma once
#pragma once
#include <Windows.h>
#include <map>
#include <string>

namespace funcmap_builder
{
    struct stFunctionMap
    {
        std::string                      asmcode;
        std::map<DWORD64, stFunctionMap> subFunctions{};
    };
    struct C_FunctionMap
    {
        const char*    asmcode;
        DWORD64*       subKeys;
        C_FunctionMap* subValues;
        size_t         subCount;
    };

    C_FunctionMap* ConvertToC(stFunctionMap* cppMap);
    DWORD64        parse_entrypoint(HMODULE hModule, const char* filebuffer);
    stFunctionMap  map_functions(DWORD64 dwRuntimeAddress, void* buffer);

    stFunctionMap build_funcmap(HANDLE hProcess);
};            // namespace funcmap_builder
