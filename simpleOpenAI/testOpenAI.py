import os
import logging

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("LOG_LEVEL", "DEBUG"))


class OpenAI_Wrapper:
    def __init__(self):
        self.client = OpenAI()

    def list_models(self):
        return list(map(lambda x:x.id,self.client.models.list()))

    def completionTest(self,prompt="Escreva haiku sobre programadores em polaco"):    
        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        return completion.choices[0].message.content

    def audioTest(self,audioFilePath):
        audio_file= open(audioFilePath, "rb")
        transcription = self.client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )
        return transcription.text

if __name__ == "__main__":
    logger.info('Test OpenAI API')
    openapiWrapper = OpenAI_Wrapper()
    logger.debug('Wrapper created')
    logger.info('Models:')
    logger.info(openapiWrapper.list_models())
    logger.info('Text test:')
    logger.info(openapiWrapper.completionTest())
    logger.info('Audio test:')
    logger.info(openapiWrapper.audioTest('harvard.wav'))
    logger.info('Test OpenAI API done.')

