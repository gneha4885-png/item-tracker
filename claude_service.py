import anthropic
import json
import re
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

def extract_item_location(text: str) -> dict:
    """Send text to Claude and extract item + location as JSON"""

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        system="""You are a helpful assistant that extracts item location information.

When given a sentence, extract:
- item_name: the object being stored
- location: where it is kept (specific spot)
- room: which room it is in

Always respond with ONLY a JSON object like this:
{
  "item_name": "passport",
  "location": "blue drawer",
  "room": "bedroom"
}

If room is not mentioned, use "unknown".
If the sentence is too vague or doesn't mention an item or location, return:
{
  "item_name": "unknown",
  "location": "unknown",
  "room": "unknown"
}
Never add any extra text — only the JSON.""",
        messages=[
            {
                "role": "user",
                "content": text
            }
        ]
    )

    # Get Claude's response
    response_text = message.content[0].text.strip()

    # Remove markdown code blocks if Claude added them
    response_text = re.sub(r'```json\s*', '', response_text)
    response_text = re.sub(r'```\s*', '', response_text)
    response_text = response_text.strip()

    try:
        result = json.loads(response_text)
        return result
    except json.JSONDecodeError:
        # If Claude still returns bad JSON, return a safe default
        return {
            "item_name": "unknown",
            "location": "unknown",
            "room": "unknown"
        }

def find_item_location(query: str, items: list) -> str:
    """Search through saved items and answer user's query"""

    # If no items saved yet
    if not items:
        return "You haven't saved any item locations yet. Try saying 'I kept my keys in the kitchen'!"

    # Format items as readable text for Claude
    items_text = ""
    for i, item in enumerate(items, 1):
        items_text += f"{i}. {item['item_name']} — {item['location']} ({item['room']}) — saved on {item['timestamp'][:10]}\n"

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        system="""You are a helpful assistant that helps people find where they kept their belongings.

You will be given:
1. A list of saved item locations
2. A question from the user

Your job is to find the best matching item and answer in a friendly, natural way.

Example answer: "You kept your car keys on the kitchen counter. You saved this 2 days ago."

If no match is found, say: "I couldn't find that item in your saved locations. Try logging it first!"

If the query is too vague like 'where is everything', list all items briefly.

Always be friendly and conversational.""",
        messages=[
            {
                "role": "user",
                "content": f"My saved items:\n{items_text}\n\nMy question: {query}"
            }
        ]
    )

    return message.content[0].text