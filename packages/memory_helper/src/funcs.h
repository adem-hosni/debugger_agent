#pragma once
#include <Windows.h>
#include "kernel_calls.hpp"
#include <Zydis/Zydis.h>

namespace funcs
{
    struct Array
    {
        char*  data;
        SIZE_T size;
        int    len;
    };

    HANDLE open_process(DWORD process_id);
    Array  collect_regions(HANDLE hProcess);
    char*  disassemble_region(HANDLE hProcess, SIZE_T size, ULONG_PTR start_address);
    void   patch_bytes(HANDLE hProcess, LPVOID address, const char* bytes, SIZE_T size);
}            // namespace funcs
