#include "main.hpp"


MEMORY_API HANDLE open_process(DWORD process_id)
{
	return funcs::open_process(process_id);
}


MEMORY_API funcs::Array collect_regions(HANDLE hProcess)
{
	return funcs::collect_regions(hProcess);
}


MEMORY_API char* disassemble_region(HANDLE hProcess, SIZE_T size, ULONG_PTR address)
{
	return funcs::disassemble_region(hProcess, size, address);
}

MEMORY_API void patch_bytes(HANDLE hProcess, LPVOID lpAddress, const char* bytes, size_t size)
{
	return funcs::patch_bytes(hProcess, lpAddress, bytes, size);
}



int main()
{
	return 0;
}
