"""
Test script to send a request to the API and print the response.
"""

from uuid import uuid4
import requests


def main() -> None:
    """
    Main function to send a request to the API and print the response.
    """
    url = "http://localhost:12345/invoke"
    data = {
        "query": "What is 3 time 6 divided by 234234",
        "session_id": uuid4().hex,
    }
    try:
        response = requests.post(url, timeout=10, json=data)
        if response.status_code == 200:
            print("Response from API:")
            print(response.text)
        else:
            print(f"API returned status code: {response.status_code}")
            print(f"Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to API: {e}")


if __name__ == "__main__":
    main()
