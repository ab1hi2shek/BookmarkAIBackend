import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

# Define the constant for the maximum content length
MAX_CONTENT_LENGTH = 1000

def fetch_page_content(url):
    """Fetch page title and main content from the given URL using BeautifulSoup and lxml parser."""
    page_content = create_page_content()

    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    page_content = create_page_content()
    if response.status_code != 200:
        return page_content

    soup = BeautifulSoup(response.text, "lxml")
    page_content["image"] = fetch_relevant_image(url, soup)
    page_content["title"] = fetch_title(soup)

    # Clean up the page by removing unnecessary elements
    soup = remove_unwanted_elements(soup)
    page_content["content"] = " ".join(soup.stripped_strings)[:MAX_CONTENT_LENGTH]

    return page_content


def create_page_content(title="", content="", image=""):
    """Create and return a dictionary representing the page content."""
    return {
        "title": title,
        "content": content,
        "image": image
    }


def fetch_title(soup):
    """Fetch the title from the meta tags or the <title> tag in the HTML."""
    # Try to get the Open Graph title (og:title)
    if (meta_title := soup.find("meta", property="og:title")):
        return meta_title.get("content", "")
    
    # Try to get the title from the meta tag with name='title'
    elif (meta_title := soup.find("meta", attrs={"name": "title"})):
        return meta_title.get("content", "")
    
    # If neither, fall back to the <title> tag in the HTML
    elif soup.title:
        return soup.title.string.strip()
    
    # If no title is found, return an empty string
    return ""


def fetch_relevant_image(url, soup):
    """Fetch the relevant image (og:image or <img> tag) from the given URL's HTML."""
    # Try to get the Open Graph image (og:image)
    og_image = soup.find("meta", property="og:image")
    if og_image:
        img_url = og_image.get("content")
        # If the URL is relative, make it absolute by joining with the base URL
        return urljoin(url, img_url)

    # If no Open Graph image, find the first <img> tag with an image src
    img_tag = soup.find("img")
    if img_tag and img_tag.get("src"):
        return img_tag["src"]

    return None  # No image found


def remove_unwanted_elements(soup):
    """Remove elements like navigation, footers, forms, ads, etc., using regex matching."""
    
    # Define regex patterns for unwanted selectors (Only match class and ID attributes)
    unwanted_patterns = [
        r".*nav.*", r".*header.*", r".*footer.*", r".*aside.*", r".*form.*", r".*input.*", r".*button.*", r".*banner.*", r".*tracking.*", r".*sponsored.*",  # Element types
        r".*signup.*", r".*subs.*", r".*register.*", r".*login.*", r".*terms.*", r".*privacy.*", r".*contact.*", r".*about.*",  # Signup/Login/Subscription
        r".*social.*", r".*share.*", r".*follow.*", r".*media.*", r".*tweet.*", r".*like.*",  # Social media buttons
        r".*popup.*", r".*modal.*", r".*overlay.*", r".*newsletter.*", r".*subs.*", r".*alert.*",  # Popups and overlays
        r".*ads.*", r".*advert.*", r".*promo.*", r".*sidebar.*", r".*interstitial.*", r".*call-to-action.*",  # Ads & promotions
        r".*cookie.*", r".*consent.*", r".*disclaimer.*", r".*analytics.*", r".*tracking.*", r".*widget.*",  # Cookie banners, tracking
        r".*comment.*", r".*related.*", r".*trending.*", r".*breaking.*", r".*more_articles.*"  # Related content
    ]

    
    # Loop through all elements and remove those matching any unwanted patterns
    for tag in soup.find_all(True):
        try:
            # If the tag is None, skip it
            if tag is None:
                continue

            class_attr = " ".join(tag.get("class", []))  # Join class list if it exists
            id_attr = tag.get("id", "")  # Get ID or empty string

            # Match class or ID against unwanted patterns
            if any(re.search(pattern, class_attr, re.IGNORECASE) for pattern in unwanted_patterns) or \
               any(re.search(pattern, id_attr, re.IGNORECASE) for pattern in unwanted_patterns):
                tag.decompose()  # Remove the tag from the soup
                continue  # Skip further processing

        except Exception as e:
            # Log or print exception if necessary for debugging
            continue

    return soup
