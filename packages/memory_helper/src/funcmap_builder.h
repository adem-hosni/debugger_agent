#pragma once
#include <Windows.h>
#include <map>
#include <string>
#include <set>

#define NT_SUCCESS(Status) (((NTSTATUS)(Status)) >= 0)

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
    DWORD64        parse_entrypoint(DWORD64 dwProcessBase, const char* filebuffer);
    stFunctionMap  map_functions(HANDLE hProcess, DWORD64 dwRuntimeAddress, std::set<DWORD64>& visitedAddresses);

    stFunctionMap build_funcmap(HANDLE hProcess);
};            // namespace funcmap_builder
