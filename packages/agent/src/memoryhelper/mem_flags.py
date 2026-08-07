# --- State (mutually exclusive, single value) ---
MEM_STATE = {
    0x1000: "MEM_COMMIT",
    0x2000: "MEM_RESERVE",
    0x10000: "MEM_FREE",
}

# --- Type (mutually exclusive, single value) ---
MEM_TYPE = {
    0x1000000: "MEM_IMAGE",
    0x40000: "MEM_MAPPED",
    0x20000: "MEM_PRIVATE",
}

# --- Protect: base protection values (mutually exclusive) ---
PAGE_PROTECT_BASE = {
    0x01: "PAGE_NOACCESS",
    0x02: "PAGE_READONLY",
    0x04: "PAGE_READWRITE",
    0x08: "PAGE_WRITECOPY",
    0x10: "PAGE_EXECUTE",
    0x20: "PAGE_EXECUTE_READ",
    0x40: "PAGE_EXECUTE_READWRITE",
    0x80: "PAGE_EXECUTE_WRITECOPY",
}

# --- Protect: modifier flags (combinable via OR with a base value) ---
PAGE_PROTECT_MODIFIERS = {
    0x100: "PAGE_GUARD",
    0x200: "PAGE_NOCACHE",
    0x400: "PAGE_WRITECOMBINE",
}


def format_state(state: int) -> str:
    return MEM_STATE.get(state, f"UNKNOWN_STATE(0x{state:X})")


def format_type(type_: int) -> str:
    if type_ == 0:
        return "-"  # free regions report Type == 0
    return MEM_TYPE.get(type_, f"UNKNOWN_TYPE(0x{type_:X})")


def format_protect(protect: int) -> str:
    if protect == 0:
        return "-"  # free regions report Protect == 0

    base_flag = protect & 0xFF
    base = PAGE_PROTECT_BASE.get(base_flag, f"UNKNOWN_PROTECT(0x{base_flag:X})")

    modifiers = [name for bit, name in PAGE_PROTECT_MODIFIERS.items() if protect & bit]

    if modifiers:
        return f"{base} | {' | '.join(modifiers)}"
    return base


def format_region(r) -> str:
    """r is a MEMORY_BASIC_INFORMATION instance (or anything with .BaseAddress/.RegionSize/.State/.Protect/.Type)."""
    return (
        f"0x{r.BaseAddress:016X}  size=0x{r.RegionSize:X}  "
        f"state={format_state(r.State):12}  "
        f"protect={format_protect(r.Protect):35}  "
        f"type={format_type(r.Type)}"
    )
