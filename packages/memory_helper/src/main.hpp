#pragma once
#pragma once
#include <Windows.h>

#if defined(_WIN32) || defined(_WIN64)
    #define MEMORY_API __declspec(dllexport)
#else
    #define MEMORY_API __attribute__((visibility("default")))
#endif

#ifdef __cplusplus
extern "C"
{
#endif

    typedef struct
    {
        char*  data;
        size_t size;
        int    len;
    } Array;

    typedef struct
    {
        const char*    asmcode;
        void*          subKeys;
        void*          subValues;
        size_t         subCount;
    } C_FunctionMap;

    MEMORY_API HANDLE        open_process(DWORD process_id);
    MEMORY_API Array         collect_regions(HANDLE hProcess);
    MEMORY_API char*         disassemble_region(HANDLE hProcess, size_t size, ULONG_PTR start_address);
    MEMORY_API void          patch_bytes(HANDLE hProcess, void* lpAddress, const char* bytes, size_t size);
    MEMORY_API C_FunctionMap* build_funcmap(HANDLE hProcess);

#ifdef __cplusplus
}
#endif
