__all__ = ["FunctionNode", "FunctionMap"]

from typing import Any, Self

class FunctionNode:
    def __init__(self, offset: str, asm_code: str):
        self.offset = offset.lower()
        self.asm_code = asm_code
        self.inner_nodes: set[FunctionNode] = set()

    def find_node(self, offset: str) -> Self | None:
        offset = f"{int(offset, base=16):x}"
        if offset == self.offset or offset == "0x" + self.offset:
            return self
        for inner_node in self.inner_nodes:
            if inner_node.find_node(offset):
                return inner_node
        return self.find_node_by_instr_offset(offset)

    def find_node_by_instr_offset(self, offset: str):
        if self.asm_code.lower().find(offset.lower() + "  "):
            return self
        for inner_node in self.inner_nodes:
            if inner_node.find_node_by_instr_offset(offset):
                return inner_node

    def parse_inner_nodes(self, node_map: dict[str, Any]):
        for offset, v in node_map.get("subFunctions", {}).items():
            node = FunctionNode(offset, v["asmcode"])
            self.inner_nodes.add(node)
            node.parse_inner_nodes(v)


class FunctionMap(FunctionNode):
    def __init__(self, node_map: dict[str, Any]):
        super().__init__("0", node_map["asmcode"])
        self.parse_inner_nodes(node_map)
