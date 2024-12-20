import cloudscraper
from time import sleep
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

def send_request(
        method: str,
        url: str,
        headers: dict = HEADERS,
        retries: int = 3,
        retry_delay: int = 10
):
    """
    Function for sending requests, with response validation and retries
    when failed due to rate limits.

    Argument:
        method [str]: HTTP method for the requests (e.g., get, post...).
        url [str]: URL to which the request is sent.
        headers [dict]: The request headers (defaults to HEADERS).
        retries [int]: Number of retries if rate limited (defaults to 3).
        retry_delay [int]: Seconds between retries (defaults to 10).

    Raises exception when response status code is not 200.
    """
    # Initialize a cloudscraper session
    scraper = cloudscraper.create_scraper()

    try:
        response = scraper.request(method, url, headers=headers)

        # Retry if request rate limit detected
        if response.status_code == 429:
            if retries <= 0:
                raise Exception("Too many requests sent to server. Try again later.")

            print(f"Request rate limited. Retrying in {retry_delay} seconds.")
            sleep(retry_delay)
            return send_request(method, url, headers, retries - 1, retry_delay)
        else:
            response.raise_for_status()  # Raise HTTPError if any

        return response

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        raise
