# standard imports
import json

# third party imports
import requests


def get_top_entity_id(search_term):
    search_entites_url = "https://www.wikidata.org/w/api.php?action=wbsearchentities&search={}&language=en&format=json"
    response = requests.get(search_entites_url.format(search_term))
    page = response.content.decode("utf8")
    js = json.loads(page)
    return js


print(get_top_entity_id("Tim Cook"))
