import os
import requests
from utility.utils import log_response, LOG_TYPE_PEXEL
from utility.config import get_config


def search_images(query_string: str, orientation_landscape: bool = False):
    """Search Pexels Photos API for stock images matching the query."""
    config = get_config()
    pexels_api_key = config.get_pexels_api_key()

    url = "https://api.pexels.com/v1/search"
    headers = {
        "Authorization": pexels_api_key,
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        ),
    }
    params = {
        "query": query_string,
        "orientation": "landscape" if orientation_landscape else "portrait",
        "per_page": 15,
        "size": "large",
    }

    response = requests.get(url, headers=headers, params=params)
    json_data = response.json()
    log_response(LOG_TYPE_PEXEL, query_string, json_data)

    if response.status_code != 200:
        error_msg = json_data.get("error", f"HTTP {response.status_code}")
        raise Exception(f"Pexels Photos API error: {error_msg}. Check your PEXELS_API_KEY.")

    if "photos" not in json_data:
        raise Exception(
            "Pexels Photos API returned unexpected response (no 'photos' field)."
        )

    return json_data


def get_best_image(query_string: str, orientation_landscape: bool = False, used_images: list = []):
    """Return the URL of the best matching stock image for the query."""
    data = search_images(query_string, orientation_landscape)
    photos = data.get("photos", [])

    if not photos:
        print(f"No images found for query: {query_string}")
        return None

    # Pick the first image not already used
    for photo in photos:
        src = photo.get("src", {})
        # Use 'large2x' for high quality, fall back to 'large'
        img_url = src.get("large2x") or src.get("large") or src.get("original")
        if img_url and img_url not in used_images:
            return img_url

    # If all are used, just return the first
    src = photos[0].get("src", {})
    return src.get("large2x") or src.get("large") or src.get("original")


def generate_image_url(timed_video_searches: list, orientation_landscape: bool = False) -> list:
    """
    For each timed search term set, fetch a Pexels stock image URL.
    Returns a list of [[t1, t2], image_url] pairs — same shape as generate_video_url.
    """
    timed_image_urls = []
    used_links: list[str] = []

    for (t1, t2), search_terms in timed_video_searches:
        url = None
        for query in search_terms:
            url = get_best_image(query, orientation_landscape=orientation_landscape, used_images=used_links)
            if url:
                used_links.append(url)
                break
        timed_image_urls.append([[t1, t2], url])

    return timed_image_urls
