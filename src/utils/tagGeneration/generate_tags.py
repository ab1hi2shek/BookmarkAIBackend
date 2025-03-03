import os
from src.utils.tagGeneration.fetch_page_content import fetch_page_content
from src.models.tag_model import TAG_CREATOR
import requests

# Initialize OpenAI client correctly
local_api_key = "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"
PERPLEXITY_API_KEY = os.getenv("OPENAI_API_KEY", local_api_key)

TAG_COUNT = 10

def generate_tags(url, title, content, allUserTags):

    if not url:
        return ["Could not get url"]

    suggested_selected_tag_list, user_tag_list = get_user_and_selected_tags(allUserTags)
    prompt = generate_prompt(title, content, user_tag_list, suggested_selected_tag_list, url)

    print(prompt)

    # Correct API call using perplexity
    response = requests.post(
        "https://api.perplexity.ai/chat/completions",
        headers={"Authorization": f"Bearer {PERPLEXITY_API_KEY}", "Content-Type": "application/json"},
        json={"model": "sonar", "messages": [{"role": "user", "content": prompt}], "max_tokens": 100}
    )

    # Parse the response
    tags = response.json().get("choices", [])[0].get("message", {}).get("content", "").split(",")
    return [tag.strip() for tag in tags]


def generate_prompt(title, content, user_tags, suggested_selected_tags, url):
    return f"""
    Generate exactly {TAG_COUNT} relevant tags for a bookmark based on the following details:
    
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
