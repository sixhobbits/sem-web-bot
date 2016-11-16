from wikihelper import complete_triple
from wikihelper import complete_triple_sparql
from nlphelper import extract_nps
from nlphelper import extract_vbs
from nlphelper import parse
from nlphelper import extract_triple
import config

import logging

# set up logging
logging.basicConfig(level=config.log_level)
logger = logging.getLogger(__name__)


def answer_from_file(filename="questions.txt"):
    with open("questions.txt") as f:
        items = f.read().strip().split("\n\n")

    questions = []
    triples = []
    answers = []

    # populate lists 
    for item in items:
        print(item.strip().split("\n"))
        question, triple, answer = item.strip().split("\n")
        questions.append(question)
        triples.append(triple)
        answers.append(answer)
    
    # answer each question
    for question in questions:
        print(question)
        triple = extract_triple(question)
        print(triple)
        try:
            relation = triple[0]
            entity = triple[1]
            answer = complete_triple_sparql(relation, entity)[0]
            print(answer)
        except Exception as e:
            print("Couldn't answer")
        print("---")


def answer_question(question):
    logger.info(question)
    triple = extract_triple(question)
    logger.info(triple)
    if not triple:
       return {"status": "no_triple"}
    answer = complete_triple_sparql(triple[0], triple[1])
    if not answer:
        return {"status":"no_answer", "triple":triple}
    return {"status":"answered", "triple": triple, "answer":answer}



def test():
    sentence = "Who's the Director General of Apple?"
    triple = extract_triple(sentence)
    logger.info(triple)
    answer = complete_triple_sparql(triple[0], triple[1])
    logger.info(answer)

    sentence = "What does Apple design?"
    triple = extract_triple(sentence)
    print(triple)
 

if __name__ == "__main__":
    answer_from_file()
