import anthropic
from dotenv import load_dotenv

# Load your API key from .env file
load_dotenv()

# Create Claude client
client = anthropic.Anthropic()

# Send a message to Claude
message = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "I kept my passport in the blue drawer in the bedroom. Extract the item and location from this sentence and return as JSON only."
        }
    ]
)

# Print Claude's response
print(message.content[0].text)