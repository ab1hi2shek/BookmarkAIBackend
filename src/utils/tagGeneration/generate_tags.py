import os
from src.utils.tagGeneration.fetch_page_content import fetch_page_content
from src.models.tag_model import TAG_CREATOR
import requests
from dotenv import load_dotenv

def generate_tags(tag_count, url, title, content, allUserTags):

    if not url:
        return ["Could not get url"]

    suggested_selected_tag_list, user_tag_list = get_user_and_selected_tags(allUserTags)
    prompt = generate_prompt(tag_count, title, content, user_tag_list, suggested_selected_tag_list, url)

    # Correct API call using perplexity
    response = requests.post(
        "https://api.perplexity.ai/chat/completions",
        headers={"Authorization": f"Bearer {get_api_key()}", "Content-Type": "application/json"},
        json={"model": "sonar", "messages": [{"role": "user", "content": prompt}], "max_tokens": 100}
    )

    # Parse the response
    tags = response.json().get("choices", [])[0].get("message", {}).get("content", "").split(",")
    return [tag.strip() for tag in tags]

def get_api_key():
    """Load API key from environment variables or .env file"""
    
    # ✅ Load .env only in local development (not on Vercel)
    if os.getenv("VERCEL") != "1":
        env_loaded = load_dotenv()
        if not env_loaded:
            print("❌ Failed to load .env file!")

    api_key = os.getenv("PERPLEXITY_API_KEY")

    if not api_key:
        print("❌ ERROR: PERPLEXITY_API_KEY is missing!")
    else:
        print(f"✅ API Key Loaded: {api_key[:5]}...")  # Only show part of the key for security

    return api_key


def generate_prompt(tag_count, title, content, user_tags, suggested_selected_tags, url):
    return f"""
    Generate exactly {tag_count} relevant tags for a bookmark based on the following details:
    
    Url: {url}
    Title: {title}
    Content: {content}
    
    User's previous tags history: {', '.join(user_tags)}
    
    The user has liked these tags (they have selected these in past): {', '.join(suggested_selected_tags)}

    Provide only the tags, separated by commas. Generate relevant tags, prioritizing single-word tags. If a concept requires more clarity, use multiword tags joined by underscores (e.g., machine_learning). Ensure a balanced mix of single and multiword tags.
    """

def get_user_and_selected_tags(user_tags):
    suggested_selected_tag_list = []
    user_tag_list = []
    for tag in user_tags:
        user_tag_list.append(tag["tagName"])
        if tag["creator"] == TAG_CREATOR.SERVICE.value:
            suggested_selected_tag_list.append(tag["tagName"])

    return suggested_selected_tag_list, user_tag_list
