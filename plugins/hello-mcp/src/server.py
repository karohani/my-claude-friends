"""
Hello MCP Server
MCP 서버 시스템 학습용 예제
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("hello-mcp")


@mcp.tool()
def greet(name: str = "World") -> str:
    """
    사용자에게 인사하는 도구

    Args:
        name: 인사할 대상 이름

    Returns:
        인사 메시지
    """
    return f"Hello, {name}! This is from hello-mcp server."


@mcp.tool()
def echo(message: str) -> str:
    """
    메시지를 그대로 반환하는 도구 - 디버깅/테스트용

    Args:
        message: 반환할 메시지

    Returns:
        입력받은 메시지 그대로
    """
    return f"Echo: {message}"


def main():
    mcp.run()


if __name__ == "__main__":
    main()
