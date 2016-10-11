import json

import requests

from textblob import TextBlob

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
    return [entity.get("title") for entity in js.get("search")]


def get_entity(code):
    """IN: Wikidata code - string: Get the related wikidata entity
       OUT: JSON response from wikidata
    """
    url = BASE_URL + "action=wbgetentities&ids={}&format=json"
    page = get_url(url.format(code))
    print(url.format(code))
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
        possible_subjects.append(entity['mainsnak']['datavalue']['value']['id'])
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
       Example: complete_triple(ceo, Apple) -> Tim Cook

    """
    property_codes = search_to_entity(relation, True)
    property_codes = [x.split(":")[1] for x in property_codes]
    entity_codes = search_to_entity(obj)

    # properties = [get_entity(code) for code in property_codes]
    entities = [get_entity(code) for code in entity_codes]

    # check if any of the properties are mentioned in the claims of the entities
    subject_labels = []
    for i, entity in enumerate(entities):
        for prop in property_codes:
            if prop in entity['entities'][entity_codes[i]]['claims']:
                # print(prop, "found in", entity_codes[i])
                # print(get_subjects(prop, entity, entity_codes[i]))
                subjects = get_subjects(prop, entity, entity_codes[i])
                print(get_labels(subjects))




def main():
    print(complete_triple("father", "Obama"))


if __name__ == "__main__":
    main()
