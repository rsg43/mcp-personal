"""
Module for a simple math server using FastMCP.
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="Math", host="0.0.0.0", port=54321)


@mcp.tool()
def add(a: float, b: float) -> float:
    """
    Adds two numbers together.

    :param a: The first number.
    :type a: float
    :param b: The second number.
    :type b: float
    :return: The sum of the two numbers.
    :rtype: float
    """
    return a + b


@mcp.tool()
def subtract(a: float, b: float) -> float:
    """
    Subtracts the second number from the first.

    :param a: The number to subtract from.
    :type a: float
    :param b: The number to subtract.
    :type b: float
    :return: The result of the subtraction.
    :rtype: float
    """
    return a - b


@mcp.tool()
def multiply(a: float, b: float) -> float:
    """
    Multiplies two numbers together.

    :param a: The first number.
    :type a: float
    :param b: The second number.
    :type b: float
    :return: The product of the two numbers.
    :rtype: float
    """
    return a * b


@mcp.tool()
def divide(a: float, b: float) -> float:
    """
    Divides the first number by the second.

    :param a: The numerator.
    :type a: float
    :param b: The denominator.
    :type b: float
    :return: The result of the division.
    :rtype: float
    :raises ValueError: If the denominator is zero.
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


@mcp.tool()
def exp(a: float, b: float) -> float:
    """
    Raises `a` to the power of `b`.

    :param a: The base number.
    :type a: float
    :param b: The exponent.
    :type b: float
    :return: The result of `a` raised to the power of `b`.
    :rtype: float
    """
    res: float = a**b
    return res


@mcp.tool()
def greater(a: float, b: float) -> bool:
    """
    Compares two numbers and returns True if `a` is greater than `b`.

    :param a: The first number.
    :type a: float
    :param b: The second number.
    :type b: float
    :return: True if `a` is greater than `b`, otherwise False.
    :rtype: bool
    """
    return a > b


if __name__ == "__main__":
    mcp.run(transport="sse")
