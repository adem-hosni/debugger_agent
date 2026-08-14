__all__ = [
    "open_process_sig",
    "collect_regions_sig",
    "disassemble_region_sig",
    "patch_bytes_sig",
    "build_funcmap_sig",
]

from typing import Any
from .ctypes import *


def get_signature(argtypes: list[Any] = [], restype: Any | None = None):
    """
    Configures and returns a specific function signature from a loaded DLL.
    """
    return {
        "argtypes": argtypes,
        "restype": restype,
    }


open_process_sig = get_signature([DWORD], HANDLE)
disassemble_region_sig = get_signature([HANDLE, SIZE_T, ULONG_PTR], CHAR_PTR)
collect_regions_sig = get_signature([HANDLE], Array)
patch_bytes_sig = get_signature([HANDLE, LPVOID, CHAR_PTR, SIZE_T])
build_funcmap_sig = get_signature([HANDLE], c.POINTER(C_FunctionMap))
