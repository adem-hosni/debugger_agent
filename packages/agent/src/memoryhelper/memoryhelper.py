from .ctypes import *
import threading
import psutil
import shutil
import hashlib
import os
import json

from contextlib import suppress
from typing import Any

from .signatures import *
from .mem_flags import *

MemoryRegionsList = list[MEMORY_BASIC_INFORMATION]


class MemoryHelper:
    def __init__(self):
        self.memory_mod = c.CDLL(
            r"C:\Users\hosni\source\repos\debugger_agent\packages\memory_helper\build\memory.dll"
        )
        self._target_pe_hash: str | None = None
        self.working_directory: str | None = None
        self.c_open_process = self.bind_cfunc("open_process", open_process_sig)
        self.c_disassemble_region = self.bind_cfunc(
            "disassemble_region", disassemble_region_sig
        )
        self.c_collect_regions = self.bind_cfunc("collect_regions", collect_regions_sig)
        self.c_patch_bytes = self.bind_cfunc("patch_bytes", patch_bytes_sig)
        self.c_build_funcmap = self.bind_cfunc("build_funcmap", build_funcmap_sig)
        self.__target_handle: HANDLE = 0

    def open_process(self, process_id: int) -> HANDLE:
        return self.c_open_process(DWORD(process_id))

    def read_region_info(self, address: ULONG_PTR) -> MEMORY_BASIC_INFORMATION:
        return self.c_read_region_info(self.__target_handle, address)

    def c_disassemble_region(self, address: ULONG_PTR, size: SIZE_T) -> CHAR_PTR:
        return self.c_disassemble_region(HANDLE(self.__target_handle), size, address)

    def bind_cfunc(self, cfunc_name: str, csig: dict[Any, Any]):
        cfunc = getattr(self.memory_mod, cfunc_name)
        cfunc.argtypes = csig["argtypes"]
        cfunc.restype = csig["restype"]
        return cfunc

    def attach(self, process_name: str) -> bool:
        pids = self.get_pid_by_name(process_name)
        if len(pids) == 0 or pids[0][0] == 0:
            return False
        self.__target_handle = self.open_process(pids[0][0])
        result = self.__target_handle is not None
        if result:
            with open(pids[0][1], "rb") as file:
                self._target_pe_hash = hashlib.md5(file.read()).hexdigest()
            self.working_directory = f"output/bin/{self._target_pe_hash}"
        return result

    def get_pid_by_name(self, process_name: str):
        pids = []
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                if process_name.lower() in proc.info["name"].lower():
                    pids.append(
                        (
                            proc.info["pid"],
                            proc.exe(),
                        )
                    )
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return pids

    def collect_regions(self) -> MemoryRegionsList:
        return self.c_collect_regions(self.__target_handle)

    def disassemble_regions(self, regions: MemoryRegionsList):
        with suppress(FileNotFoundError, PermissionError):
            shutil.rmtree(self.working_directory)
        os.makedirs(self.working_directory, exist_ok=True)
        regions_per_thread = regions.len // 4
        results = []
        n_threads = 4
        for i in range(n_threads):
            t = threading.Thread(
                target=self.__disassemble_regions_worker,
                args=(
                    regions[
                        i
                        * n_threads : (
                            ((i * n_threads) + regions_per_thread)
                            if i != n_threads - 1
                            else None
                        )
                    ],
                    results,
                ),
            )
            t.start()
            t.join()
        with open(f"{self.working_directory}/mem_dump.json", "w") as f:
            f.write(json.dumps(results, indent=4))
        return results

    def patch_bytes_from_addr(self, address: LPVOID, bytes_: CHAR_PTR, size: SIZE_T):
        return self.c_patch_bytes(self.__target_handle, address, bytes_, size)

    def build_funcmap(self) -> dict:
        try:
            c_map_ptr = self.c_build_funcmap(self.__target_handle)
        except Exception as ex:
            print(ex)
        return self.__unpack_c_map(c_map_ptr)

    def __disassemble_regions_worker(self, regions: MemoryRegionsList, result: list):
        codes = []
        for r in regions:
            if r.RegionSize == 0:
                continue
            if r.BaseAddress:
                asm_result = MemoryHelper.c_disassemble_region(
                    self, ULONG_PTR(r.BaseAddress), SIZE_T(r.RegionSize)
                )
                if asm_result:
                    codes.append((r, asm_result))
        for r, code in codes:
            result.append(
                {
                    "basic_info": {
                        "BaseAddress": r.BaseAddress,
                        "AllocationBase": r.AllocationBase,
                        "AllocationProtect": r.AllocationProtect,
                        "RegionSize": r.RegionSize,
                        "State": format_state(r.State),
                        "Protect": format_protect(r.Protect),
                        "Type": format_type(r.Type),
                    },
                    "code": code.decode(),
                }
            )
            with open(f"{self.working_directory}/0x{r.BaseAddress:X}.asm", "w") as f:
                f.write(code.decode())

    def __unpack_c_map(self, c_map_ptr) -> dict:
        if not c_map_ptr:
            return {}
        struct_data = c_map_ptr.contents
        asm_string = ""
        if struct_data.asmcode:
            asm_string = struct_data.asmcode.decode("utf-8", errors="replace")
        result = {"asmcode": asm_string, "subFunctions": {}}
        count = struct_data.subCount
        if count > 0 and struct_data.subKeys and struct_data.subValues:
            keys_array = c.cast(
                struct_data.subKeys, c.POINTER(DWORD64 * count)
            ).contents
            values_array = c.cast(
                struct_data.subValues, c.POINTER(C_FunctionMap * count)
            ).contents
            for i in range(count):
                key = keys_array[i]
                sub_struct_ptr = c.POINTER(C_FunctionMap)(values_array[i])
                result["subFunctions"][f"{key:X}"] = self.__unpack_c_map(sub_struct_ptr)
        return result

    def get_last_error(self) -> int:
        return c.GetLastError()
