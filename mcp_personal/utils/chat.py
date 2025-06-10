"""
Module to interact with the MCP Personal API for chat functionality.
"""

from uuid import uuid4
import json

import requests


def main() -> None:
    """
    Main function to start the request loop for interacting with the MCP
    Personal API. This function prompts the user for input, sends the query to
    the API, and processes the response to display messages from the AI or
    tools called by the AI.
    """
    url = "http://localhost:12345/invoke"
    session_id = uuid4().hex
    print("Starting request loop. Enter q or press Ctrl + C to stop.")
    while True:
        query = input("User: ").strip()
        if query.lower() == "q":
            print("Exiting request loop.")
            break

        if not query:
            print("Query cannot be empty. Please enter a valid query.")
            continue

        try:
            response = requests.post(
                url,
                timeout=10,
                json={"query": query, "session_id": session_id},
            )
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to API: {e}")
            return

        if response.status_code == 200:
            resp_dict = json.loads(response.text)

            for message in resp_dict.get("messages", []):
                kwargs = message["kwargs"]

                if kwargs["type"] == "ai":
                    if isinstance(kwargs["content"], list):
                        print(f"AI: {kwargs['content'][0]['text']}")
                    else:
                        print(f"AI: {kwargs['content']}")
                elif kwargs["type"] == "tool":
                    print(f"Tool called: {kwargs['name']}")
                    print(
                        f"Tool arguments: {kwargs['artifact']['call']['args']}"
                    )
                    print(f"Tool result: {kwargs['artifact']['result']}")
        else:
            print(f"API returned status code: {response.status_code}")
            print(f"Response: {response.text}")
            return


if __name__ == "__main__":
    main()
