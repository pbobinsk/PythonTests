import os
import logging

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("LOG_LEVEL", "DEBUG"))


def testOpenAI():
    client = OpenAI()
    
#    print(list(map(lambda x:x.id,client.models.list())))
    
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": "Napisz po polsku haiku o programistach brainfuck."
            }
        ]
    )

    data = completion.choices[0].message.content
    print(data) 



if __name__ == "__main__":
    print('Test OpenAI API')
    testOpenAI()

