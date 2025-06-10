"""
Main entry point for the MCP Personal Client. It allows the user to start
different services such as the web API or frontend.

Example usage:
    python -m mcp_personal web_api
"""

from argparse import ArgumentParser


parser = ArgumentParser(description="Start the MCP Personal Client")
parser.add_argument(
    "service",
    type=str,
    help="The service to run (options: 'web_api', 'frontend')",
    choices=["web_api", "frontend"],
)
args = parser.parse_args()

if args.service == "web_api":
    from mcp_personal.web_api.main import start_async_api

    start_async_api()
elif args.service == "frontend":
    print("Frontend service is not implemented yet.")
else:
    raise ValueError(f"Unknown service: {args.service}")
