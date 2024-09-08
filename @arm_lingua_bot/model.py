import anthropic
import os
from dotenv import load_dotenv
load_dotenv()

key = 'api_key'
for i in range(int(os.getenv('n'))-1):
    key = os.getenv(key)

client = anthropic.Anthropic(
    api_key=os.getenv(key),
)

model = "claude-3-5-sonnet-20240620"

def claude(text, trans=False, lang=None, other=False):
    if lang:
        if other:
            system = 'Թարգմանիր ' + lang + ' այլ կերպ և հետ ուղարկիր առանց այլ բան ասելու'
        else:
            system = 'Թարգմանիր ' + lang + ' և հետ ուղարկիր առանց այլ բան ասելու'
    elif trans:
        system = 'Թարգմանիր հայերեն և հետ ուղարկիր առանց այլ բան ասելու'
    else:
        system = 'Ուղղիր տեքստը և հետ ուղարկիր առանց այլ բան ասելու'
    message = client.messages.create(
        model=model,
        max_tokens=1000,
        system=system,
        messages=[
            {"role": "user", "content": [
                {
                    "type": "text",
                    "text": text
                }
            ]}
            ]
        )
    s = message.content[0].text
    return s