import ctypes as c
from ctypes import wintypes

DWORD = wintypes.DWORD
HANDLE = wintypes.HANDLE
SIZE_T = c.c_size_t
CHAR_PTR = c.c_char_p
INT = c.c_int
LONG = c.c_long
ULONG_PTR = c.c_ulonglong
LPVOID = wintypes.LPVOID
DWORD64 = c.c_uint64


class MEMORY_BASIC_INFORMATION(c.Structure):
    _fields_ = [
        ("BaseAddress", c.c_void_p),
        ("AllocationBase", c.c_void_p),
        ("AllocationProtect", wintypes.DWORD),
        ("RegionSize", SIZE_T),
        ("State", wintypes.DWORD),
        ("Protect", wintypes.DWORD),
        ("Type", wintypes.DWORD),
    ]


class C_FunctionMap(c.Structure):
    pass


C_FunctionMap._fields_ = [
    ("asmcode", CHAR_PTR),
    ("subKeys", c.POINTER(DWORD64)),
    (
        "subValues",
        c.POINTER(C_FunctionMap),
    ),
    ("subCount", SIZE_T),
]


class Array(c.Structure):
    _fields_ = [
        ("data", c.POINTER(MEMORY_BASIC_INFORMATION)),
        ("size", c.c_size_t),
        ("len", c.c_int),
    ]

    def __getitem__(self, key: slice):
        return [
            self.data[i]
            for i in range(key.start, key.stop if key.stop else self.size * self.len)
        ]
