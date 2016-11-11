import json

import requests

# from textblob import TextBlob

BASE_URL = "https://www.wikidata.org/w/api.php?"


def get_url(url):
    try:
        response = requests.get(url)
        page = response.content.decode("utf8")
        return page
    except Exception as e:
        print(e)


def search(term, properties=False):
    """IN: search term - string: Search for this term
       OUT: JSON response from wikidata
    """
    url = BASE_URL + "action=wbsearchentities&search={}&language=en&format=json"
    if properties:
        url += "&type=property"
    page = get_url(url.format(term))
    js = json.loads(page)
    return js


def search_to_entity(term, properties=False):
    """IN: search term - string: Search for this term
       IN: properties - boolean: If True, search for properties instead of entity
       OUT: The entity ID for wikidata: e.g. Q42
    """
    js = search(term, properties)
    # print(js)
    return [entity.get("title") for entity in js.get("search")]


def get_entity(code):
    """IN: Wikidata code - string: Get the related wikidata entity
       OUT: JSON response from wikidata
    """
    url = BASE_URL + "action=wbgetentities&ids={}&format=json"
    page = get_url(url.format(code))
    # print(url.format(code))
    js = json.loads(page)
    return js


def get_subjects(relation_id, obj, obj_id):
    """IN: relation - string: the relation that we should look for in claims of the object obj
       IN: obj - string: the object for which we should search the claims
       OUT: the WikiData ID of the subject(s) found in the claims

       apple['entities']["Q312"]["claims"]["P169"][0]['mainsnak']['datavalue']['value']['i
d']
    """
    possible_subjects = []
    for entity in obj["entities"][obj_id]["claims"][relation_id]:
        try:
            possible_subjects.append(entity['mainsnak']['datavalue']['value']['id'])
        except Exception as e:
            print(e)

    return possible_subjects


def get_labels(subject_ids):
    labels = []
    for subject in subject_ids:
        entity = get_entity(subject)
        labels.append(entity['entities'][subject]['labels']['en']['value'])
    return labels




def complete_triple(relation, obj):
    """IN: Relation   - string: a natural langauge description of the relation
       IN: obj        - string: a natural language description of the object
       OUT: subject   - string: the name of the missing subject
       Example: complete_triple("ceo", "Apple") -> Tim Cook

    """
    property_codes = search_to_entity(relation, True)
    property_codes = [x.split(":")[1] for x in property_codes]
    entity_codes = search_to_entity(obj)


    # jprint(property_codes)
    # print(entity_codes)
    # properties = [get_entity(code) for code in property_codes]
    entities = [get_entity(code) for code in entity_codes]

    # check if any of the properties are mentioned in the claims of the entities
    subject_labels = []
    for i, entity in enumerate(entities):
        for prop in property_codes:
            if prop in entity['entities'][entity_codes[i]]['claims']:
                print(prop, "found in", entity_codes[i])
                #  print(get_subjects(prop, entity, entity_codes[i]))
                subjects = get_subjects(prop, entity, entity_codes[i])
                print(get_labels(subjects))


def get_sparql(query):
    """IN:  SPARQL Query
       OUT: JSON results of query from wikidata

       Example query: SELECT ?name ?nameLabel WHERE { {wd:Q76 wdt:P22 ?name } 
                      UNION {?name wdt:P22 wd:Q76 } . 
                      SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }}
    """
    url = 'https://query.wikidata.org/sparql?format=json&query={}'
    url = url.format(query)
    resp = requests.get(url)
    return resp.content.decode("utf8", "ignore")


def main2():
    #  print(get_sparql('SELECT ?name ?nameLabel WHERE { {wd:Q76 wdt:P22 ?name } UNION {?name wdt:P22 wd:Q76 } . SERVICE wikibase:label { bd:serviceParam wikibase:language "en" } }'))
    triples = []
    t1 = ("father", "Obama")
    t2 = ("CEO", "Apple")
    t3 = ("Owner", "Apple")
    t4 = ("product", "Apple")
    triples.append(t1)
    triples.append(t2)
    triples.append(t3)
    triples.append(t4)
    for triple in triples:
        print(triple)
        complete_triple(*triple)
        print("-------------")

def main():
    triples = []
    answers = []
    with open("questions.txt") as f:
        lines = f.read().strip().split("\n")
        for i, line in enumerate(lines):
            if line.startswith("("):
                triples.append(line)
                answers.append(lines[i+1])

    for i, triple in enumerate(triples):
        print(triple)
        print(answers[i])
        complete_triple(*triple)



if __name__ == "__main__":
    main()
