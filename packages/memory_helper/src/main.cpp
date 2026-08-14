#include "main.hpp"
#include "main.hpp"
#include "funcs.h"
#include "funcmap_builder.h"

extern "C" {

MEMORY_API HANDLE open_process(DWORD process_id)
{
    return funcs::open_process(process_id);
}

MEMORY_API Array collect_regions(HANDLE hProcess)
{
    funcs::Array result = funcs::collect_regions(hProcess);
    return {result.data, result.size, result.len};
}

MEMORY_API char* disassemble_region(HANDLE hProcess, size_t size, ULONG_PTR address)
{
    return funcs::disassemble_region(hProcess, size, address);
}

MEMORY_API void patch_bytes(HANDLE hProcess, void* lpAddress, const char* bytes, size_t size)
{
    funcs::patch_bytes(hProcess, lpAddress, bytes, size);
}

MEMORY_API C_FunctionMap* build_funcmap(HANDLE hProcess)
{
    funcmap_builder::stFunctionMap funcmap = funcmap_builder::build_funcmap(hProcess);
    funcmap_builder::C_FunctionMap* c_funcmap = funcmap_builder::ConvertToC(&funcmap);
    return reinterpret_cast<C_FunctionMap*>(c_funcmap);
}

}  // extern "C"

int main()
{
    return 0;
}
