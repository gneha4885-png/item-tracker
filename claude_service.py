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
    
    # Parse as JSON
    return json.loads(response_text)