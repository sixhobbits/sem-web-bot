import json
import requests
import logging
import config


BASE_URL = "https://www.wikidata.org/w/api.php?"

# set up logging
logging.basicConfig(level=config.log_level)
logger = logging.getLogger(__name__)


def get_url(url):
    try:
        response = requests.get(url)
        page = response.content.decode("utf8")
        return page
    except Exception as e:
        logger.info(e)


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
    js = json.loads(page)
    return js


def get_objects(relation_id, sub, sub_id):
    """IN: relation - string: the relation that we should look for in the subject
       IN: sub      - string: the subject whose relations we search
       IN: sub_id   - the ID of the subject whose relations we search
       OUT: the WikiData ID of the objects for the claims
    """
    possible_objects = []


def get_subjects(relation_id, obj, obj_id):
    """IN: relation - string: the relation that we should look for in claims of the object obj
       IN: obj      - string: the object for which we should search the claims
       OUT: the WikiData ID of the subject(s) found in the claims

       apple['entities']["Q312"]["claims"]["P169"][0]['mainsnak']['datavalue']['value']['i
d']
    """
    possible_subjects = []
    for entity in obj["entities"][obj_id]["claims"][relation_id]:
        try:
            possible_subjects.append(entity['mainsnak']['datavalue']['value']['id'])
        except Exception as e:
            logger.info(e)
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
    entities = [get_entity(code) for code in entity_codes]

    # check if any of the properties are mentioned in the claims of the entities
    subject_labels = []
    for i, entity in enumerate(entities):
        for prop in property_codes:
            if prop in entity['entities'][entity_codes[i]]['claims']:
                subjects = get_subjects(prop, entity, entity_codes[i])
                subject_labels += subjects
    return subject_labels


def build_sparql(relations, entities):
    """IN: relations: list of relation codes
       IN: entities:  list of entity codes
       OUT: query:    a string of the SPARQL query to match any combination of the relation and entity
    """
    template = """SELECT ?x ?xLabel WHERE {{ 
{}
    SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" }}
}}"""

    # build a bunch of union statements 
    body = ""
    first_line = True  # don't add UNION to first line'
    for entity in entities:
        for relation in relations:
            line = "{{?x wdt:{} wd:{} }}\n".format(relation, entity)
            line2 = "{{wd:{} wdt:{} ?x }}\n".format(entity, relation)
            if first_line:
                first_line = False
            else:
                body += "    UNION "
            body += line2
            body += "    UNION"
            body += line
    logger.debug(template.format(body))
    return template.format(body)


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


def complete_triple_sparql(relation, obj):
    property_codes = search_to_entity(relation, True)
    property_codes = [x.split(":")[1] for x in property_codes]
    entity_codes = search_to_entity(obj)

    # build all possibilities into a sparql query
    query = build_sparql(property_codes, entity_codes)

    # get result of sparql
    q_result = get_sparql(query)
    js = json.loads(q_result)
    labels = []
    for result in js["results"]["bindings"]:
        try:
            labels.append(result["xLabel"]["value"])
        except KeyError as ke:
            pass
    return labels