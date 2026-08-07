# Test fixtures for the agent package

SAMPLE_SYSTEM_PROMPT = """# Test System Prompt

You are a test assistant for unit testing.
"""

SAMPLE_CRACKME_ANALYSIS = """
Analyzing crackme...
Found anti-debugging checks at 0x401000
Key validation at 0x402000
"""

SAMPLE_DISASSEMBLY = """
0x401000: push ebp
0x401001: mov ebp, esp
0x401003: sub esp, 0x10
0x401006: call 0x402000
0x40100b: test eax, eax
0x40100d: jne 0x401020
"""
