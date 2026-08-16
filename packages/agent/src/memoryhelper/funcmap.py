__all__ = ["FunctionNode", "FunctionMap"]

from typing import Any, Self

class FunctionNode:
    def __init__(self, offset: str, asm_code: str):
        self.offset = offset
        self.asm_code = asm_code
        self.inner_nodes: set[FunctionNode] = set()

    def find_node(self, offset: str) -> Self | None:
        if offset == self.offset:
            return self
        for inner_node in self.inner_nodes:
            if inner_node.find_node(offset):
                return inner_node

    def parse_inner_nodes(self, node_map: dict[str, Any]):
        for offset, v in node_map.get("subFunctions", {}).items():
            node = FunctionNode(offset, v["asmcode"])
            node.parse_inner_nodes(v)
            self.inner_nodes.add(node)


class FunctionMap(FunctionNode):
    def __init__(self, node_map: dict[str, Any]):
        super().__init__("0", node_map["asmcode"])
        self.parse_inner_nodes(node_map)
