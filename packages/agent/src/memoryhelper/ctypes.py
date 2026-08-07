import ctypes
from ctypes import wintypes

DWORD = wintypes.DWORD
HANDLE = wintypes.HANDLE
SIZE_T = ctypes.c_size_t
CHAR_PTR = ctypes.c_char_p
INT = ctypes.c_int
LONG = ctypes.c_long
ULONG_PTR = ctypes.c_ulonglong
LPVOID = wintypes.LPVOID


class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", ctypes.c_void_p),
        ("AllocationBase", ctypes.c_void_p),
        ("AllocationProtect", wintypes.DWORD),
        ("RegionSize", SIZE_T),
        ("State", wintypes.DWORD),
        ("Protect", wintypes.DWORD),
        ("Type", wintypes.DWORD),
    ]


class Array(ctypes.Structure):
    _fields_ = [
        ("data", ctypes.POINTER(MEMORY_BASIC_INFORMATION)),
        ("size", ctypes.c_size_t),
        ("len", ctypes.c_int)
    ]
    
    def __getitem__(self, key: slice):
        return [self.data[i] for i in range(key.start, key.stop if key.stop else self.size*self.len)]
