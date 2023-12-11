import re
from typing import List
from nltk import sent_tokenize
import nltk
nltk.download('punkt')


from utils.console import print_step
from utils.voice import sanitize_text


# working good
def posttextparser(obj) -> List[str]:
    text: str = re.sub("\n", " ", obj)

    sentences = sent_tokenize(text)

    newtext: list = []

    for sentence in sentences:
        if sanitize_text(sentence):
            newtext.append(sentence)

    return newtext
