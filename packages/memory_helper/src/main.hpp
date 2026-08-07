#pragma once
#include "funcs.h"

#if defined(_WIN32) || defined(_WIN64)
    #define MEMORY_API __declspec(dllexport)
#else
    #define MEMORY_API __attribute__((visibility("default")))
#endif

#ifdef __cplusplus
extern "C"
{
#endif

    MEMORY_API HANDLE open_process(DWORD process_id);
    MEMORY_API funcs::Array collect_regions(HANDLE hProcess);
    MEMORY_API char*        disassemble_region(HANDLE hProcess, SIZE_T size, ULONG_PTR start_address);
    MEMORY_API void        patch_bytes(HANDLE hProcess, LPVOID lpAddress, const char* bytes, size_t size);

#ifdef __cplusplus
}
#endif
