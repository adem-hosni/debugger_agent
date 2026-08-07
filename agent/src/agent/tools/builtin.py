from langchain_core.tools import tool



@tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression safely."""
    import ast
    import operator

    operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod,
        ast.USub: operator.neg,
    }

    def eval_expr(node: ast.AST) -> float:
        if isinstance(node, ast.Constant):
            value = node.value
            if isinstance(value, int | float):
                return float(value)
            raise ValueError(f"Unsupported constant type: {type(value)}")
        elif isinstance(node, ast.BinOp):
            return operators[type(node.op)](eval_expr(node.left), eval_expr(node.right))
        elif isinstance(node, ast.UnaryOp):
            return operators[type(node.op)](eval_expr(node.operand))
        raise ValueError(f"Unsupported expression: {ast.dump(node)}")

    try:
        tree = ast.parse(expression, mode="eval")
        result = eval_expr(tree.body)
        return str(result)
    except Exception as e:
        return f"Error: {e}"



def get_default_tools() -> list:
    """Get the default set of tools for the general assistant."""
    return [calculate]
