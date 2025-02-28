import os, sys
import logging
import io

from pathlib import Path
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

    
    def translationTest(self,model,prompt=""):    
        completion = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Jesteś tłumaczem tekstu technicznego referatu naukowego. " +
                 "Przetłumacz fragment referatu z polskiego na angielski. " +
                 "Nie tłumacz angielskich i łacińskich słów, ani odnośników do literatury (w nawiasach kwadratowych.)" +
                 "Używaj języka uznanego w naukowo-technicznych czasopismach"},
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        return (completion.usage, completion.choices[0].message.content, completion.choices[0].finish_reason)


if __name__ == "__main__":
    logger.info('Test OpenAI API')
    if len(sys.argv) != 2:
        logger.error('Use input file name as an argument')
        exit()

    if not os.path.isfile(sys.argv[1]):
        logger.error(sys.argv[1]+' is not a file')
        exit()

    model='' # gpt-4o-mini gpt-4o
    if not model:
        logger.error('Model is required')
        exit()

    inputFile = Path(sys.argv[1]).name

    logger.info('Using file: '+inputFile)

    openapiWrapper = OpenAI_Wrapper()
    logger.debug('Wrapper created')
    # logger.info('Models:')
    # logger.info(openapiWrapper.list_models())
    logger.info('Text test:')
    
    inputText = """
Nowy postęp w wykrywaniu obecności larw Hylotrupes bajulus L. w praktycznych warunkach konstrukcji dachów metodą AE – rejestracja dwukanałowa
    """
    
    with io.open(inputFile,'r',encoding='utf8') as f:
        inputText = f.read()

    usage, outputText, finishReason = openapiWrapper.translationTest(model,prompt=inputText)
    #outputText = inputText

    # print(inputText)
    # print(outputText)
    print(usage.total_tokens)
    print(finishReason)


    with io.open('translated_'+model+'_'+inputFile,'w',encoding='utf8') as f:
        f.write(outputText)

    logger.info('Test OpenAI API done.')

