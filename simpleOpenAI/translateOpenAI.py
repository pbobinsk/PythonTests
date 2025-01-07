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

    def translationTest(self,prompt=""):    
        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Jesteś tłumaczem tekstu referatu naukowego. " +
                 "Przetłumacz fragment referatu naukowego z polskiego na angielski. " +
                 "Nie tłumacz angielskich i łacińskich słów, ani odnośników do literatury (w nawiasach kwadratowych.)"},
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        return (completion.usage, completion.choices[0].message.content)


if __name__ == "__main__":
    logger.info('Test OpenAI API')
    if len(sys.argv) != 2:
        logger.info('Use input file name as an argument')
        exit()

    if not os.path.isfile(sys.argv[1]):
        logger.info(sys.argv[1]+' is not a file')
        exit()

    inputFile = Path(sys.argv[1]).name

    logger.info('Using file: '+inputFile)

    openapiWrapper = OpenAI_Wrapper()
    logger.debug('Wrapper created')
    # logger.info('Models:')
    # logger.info(openapiWrapper.list_models())
    logger.info('Text test:')
    
    inputText = """
Metoda Detection of Acoustic Emission (AE)  cieszy się kilku dekad zainteresowaniem przy wykrywaniu i badaniu życia owadów niszczących drewno. Od ponad czterech dekad prowadzone są badania nad wykrywaniem old house borer (Hylotrupes bajulus L.) przy u życiu Detection of Acoustic emission (AE) [Kerner i in. 1980, Pallaske 1988, Plinke 1991, Schofield 2011, Krajewski et al. 2012, Brandstetter et al. 2015, Creemers 2015,  Bilski et. al. 2017, Nowakowska et al. 2017, Krajewski et al. 2020, Krajewski et al. 2024, Krajewski et al. 2024]. Ten gatunek chrząszcza jest bardzo rozprzestrzeniony na świecie [Becker 1949, Becker 1949,  Becker 1970] a w Europie środkowej i północnej powoduje największe zagrożenie dla drewnianych konstrukcji budowlanych [Wichmand 1941, Becker 1949, Becker 1949, Krajewski 1995], pomimo obserwowanego zmniejszania liczby budynków opanowanych w niektórych regionach Europy w ostatnim czasie [Dominik 2005]. 
    """
    
    with io.open(inputFile,'r',encoding='utf8') as f:
        inputText = f.read()


    usage, outputText = openapiWrapper.translationTest(prompt=inputText)
    #outputText = inputText

    print(inputText)
    print(outputText)
    print(usage.total_tokens)


    with io.open('translated_'+inputFile,'w',encoding='utf8') as f:
        f.write(outputText)

    logger.info('Test OpenAI API done.')

