import pytest

from agent.tools.builtin import calculate, get_default_tools


class TestCalculateTool:
    """Tests for the calculate tool."""

    def test_basic_addition(self):
        result = calculate("2 + 3")
        assert result == "5.0"

    def test_subtraction(self):
        result = calculate("10 - 4")
        assert result == "6.0"

    def test_multiplication(self):
        result = calculate("6 * 7")
        assert result == "42.0"

    def test_division(self):
        result = calculate("20 / 4")
        assert result == "5.0"

    def test_power(self):
        result = calculate("2 ** 3")
        assert result == "8.0"

    def test_modulo(self):
        result = calculate("10 % 3")
        assert result == "1.0"

    def test_unary_negative(self):
        result = calculate("-5")
        assert result == "-5.0"

    def test_complex_expression(self):
        result = calculate("(2 + 3) * 4")
        assert result == "20.0"

    def test_float_operations(self):
        result = calculate("10 / 3")
        assert float(result) == pytest.approx(3.333333, rel=1e-6)

    def test_invalid_expression(self):
        result = calculate("2 + ")
        assert result.startswith("Error:")

    def test_invalid_syntax(self):
        result = calculate("2 ++ 3")
        assert result.startswith("Error:")

    def test_unsupported_operation(self):
        result = calculate("2 & 3")
        assert result.startswith("Error:")


class TestGetDefaultTools:
    """Tests for get_default_tools function."""

    def test_returns_list(self):
        tools = get_default_tools()
        assert isinstance(tools, list)

    def test_contains_calculate(self):
        tools = get_default_tools()
        assert len(tools) == 1
        assert tools[0].name == "calculate"
        assert "mathematical expression" in tools[0].description.lower()
