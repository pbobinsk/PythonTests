import os
import logging

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("LOG_LEVEL", "DEBUG"))

logger.debug(f"OPEN_API_KEY={os.environ['OPENAI_API_KEY']}")


def testOpenAI():
    client = OpenAI()

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": "Napisz po polsku haiku o programistach Cobola."
            }
        ]
    )

    data = completion.choices[0].model_dump_json(indent=3)
    print(data) 



if __name__ == "__main__":
    print('Test OpenAI API')
    testOpenAI()

