from argparse import ArgumentParser


parser = ArgumentParser(description="Start the MCP Personal Client")
parser.add_argument(
    "service",
    type=str,
    help="The service to run (options: 'web_api', 'frontend', 'mcp_test')",
    choices=["web_api", "frontend", "mcp_test"],
)
args = parser.parse_args()

if args.service == "web_api":
    from mcp_personal.web_api.main import start_async_api

    start_async_api()
elif args.service == "frontend":
    print("Frontend service is not implemented yet.")
elif args.service == "mcp_test":
    from mcp_personal.clients.mcp import start_client

    start_client()
else:
    raise ValueError(f"Unknown service: {args.service}")
