from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Math")


@mcp.tool()
def add(a: float, b: float) -> float:
    return a + b


@mcp.tool()
def subtract(a: float, b: float) -> float:
    return a - b


@mcp.tool()
def multiply(a: float, b: float) -> float:
    return a * b


@mcp.tool()
def divide(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


@mcp.tool()
def exp(a: float, b: float) -> float:
    res: float = a**b
    return res


@mcp.tool()
def greater(a: float, b: float) -> bool:
    return a > b


if __name__ == "__main__":
    mcp.run(transport="stdio")
