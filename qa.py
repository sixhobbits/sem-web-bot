from wikihelper import complete_triple
from nlphelper import extract_nps
from nlphelper import extract_vbs
from nlphelper import parse
from nlphelper import extract_triple

with open("questions.txt") as f:
    items = f.read().strip().split("\n\n")

questions = []
triples = []
answers = []

for item in items:
    print(item.strip().split("\n"))
    question, triple, answer = item.strip().split("\n")
    questions.append(question)
    triples.append(triple)
    answers.append(answer)


print(questions)
print(triples)
print(answers)

for question in questions:
    print(question)
    extract_triple(question)


 



