from spacy.en import English
from nltk.corpus import wordnet
import logging
import config

# get a parser
nlp = English()

# set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tags that we probably don't want in our noun phrases
blacklist_tags = set(["DT"])

# Verbs that are probably not relations
blacklist_verbs = set("is 's are be been being 're does do".split())

# We should have at least one of these for a phrase to really be considered an NP
noun_tags = set("NN NNS NNP NNPS VBG".split()) # VBG (gerund) can count as noun
verb_tags = set("VB VBZ VBP VBD VBN".split())

# proper nouns are more likely to be 
pnoun_tags = set("NNP NNPS".split())


def get_nps(parsed):
    """Gets the noun phrases from a sentence"""
    return list(parsed.noun_chunks)


def parse(sentence):
    """Parses a sentence for POS, NE, etc"""
    return nlp(sentence)


def prune_nps(nps):
    """Removes incorrect NPs (NPs which contain no nouns)"""
    pruned = []
    for np in nps:
        tags = [x.tag_ for x in np]
        for noun_tag in noun_tags:
            if noun_tag in tags:
                pruned.append(np)
                break
    return pruned


def clean_nps(nps):
    """Removes determiners from NPs""" 
    cleaned_nps = []
    for np in nps:
        cleaned = []
        for word in np:
            if word.tag_ not in blacklist_tags:
                cleaned.append(word)
        cleaned_nps.append(cleaned)
    return cleaned_nps


def get_vbs(parsed):
    """Gets a list of tokens which are tagged as verbs"""
    return [word for word in parsed if word.tag_ in verb_tags]


def prune_vbs(verbs):
    """Gets all the verbs not in our blacklist"""
    return [word for word in verbs if word.text.lower() not in blacklist_verbs]


def clean_vbs(verbs):
    """Placeholder in case we do more cleaning. For now do nothing"""
    return verbs


def extract_nps(parsed):
    """Gets NPs, prunes the incorrect ones, remove DTs"""
    nps = get_nps(parsed)
    pruned = prune_nps(nps)
    clean = clean_nps(pruned)
    return clean


def extract_vbs(parsed):
    """Gets the verbs from a parsed sentence"""
    vbs = get_vbs(parsed)
    pruned = prune_vbs(vbs)
    clean = clean_vbs(pruned)
    return clean


def count_proper_nouns(np):
    """Counts how many proper nouns are in a noun phrase"""
    return len([x for x in np if x.tag_ in pnoun_tags])

 
def get_most_nnp(nps):
    """Gets the index and count of the noun phrase containing the most proper nouns"""
    counts_with_indices = [(count_proper_nouns(np), i) for i, np in enumerate(nps)]
    counts_with_indices = sorted(counts_with_indices, reverse=True)
    return counts_with_indices[0]


def get_synsets(np):
    # TODO
    pass


def get_index_of_entity(nps):
    # Given a list of noun phrases, this tries to work out which is the entity
    # e.g. [["headquarters"], ["Warner","Bros"]] should return 1

    # if we only have one NP, that's our entity
    if len(nps) == 1:
        return 0

    # first try to find the noun phrase with the most proper nouns
    most_nnp = get_most_nnp(nps)  # get (nnp_count, index)

    # if one our nps had at least one NNP, then we take that as the entity
    if most_nnp[0] > 0:
        return most_nnp[1]
    
    # otherwise, the noun phrase with the smallest synset is taken as the entity
    # TODO
    # otherwise guess
    return len(nps)-1


def get_index_of_relation(nps):
    return 0  # TODO


def get_nouns(parsed):
    nouns = [x for x in parsed if x.tag_ in noun_tags]
    return nouns


def get_entity_relation_pos(np):
    # If we have a possessive (e.g. Obama's Father) then 
    # we split on the possessive and return the second part as relation
    # and the first part as entity
    logger.debug("get_entity_relation_pos()")
    if not len(np) >= 3:
        return None
    try:
        pos_index = [x.tag_ for x in np].index("POS")
        logger.debug("pos_index")
        if pos_index == 0 or pos_index == len(np) - 1:
            return None  # If the possessive is at the end or beginning, we can't split
        relation = np[pos_index+1:]
        entity = np[:pos_index]
        logger.debug("POS: ")
        logger.debug((relation, entity))
        return (relation, entity)
    except ValueError as ve:
        logger.debug("No Possessive in noun phrase")
        return None 
    



def extract_triple(sentence):
    parsed = parse(sentence)
    nps = extract_nps(parsed)
    logger.debug(nps)
    vbs = extract_vbs(parsed)
    entity = None
    relation = None
    
    # get entity
    if len(nps) > 0:

        # special case for possessives
        logger.debug(len(nps))
        if len(nps) == 1:
            rel_en = get_entity_relation_pos(nps[0])
            if rel_en:
                relation = " ".join([x.text for x in rel_en[0]])
                entity = " ".join([x.text for x in rel_en[1]])
                return (relation, entity)

        np_index = get_index_of_entity(nps)
        entity = nps[np_index]
        del nps[np_index]
    else:
        # look for any noun: (NP extraction isn't reliable)
        nouns = get_nouns(parsed)
        if len(nouns) > 0:
            entity = [nouns[0]]
        # can't find any noun - give up
        logger.log(logging.INFO, "Can't find noun")
        return None

    # get relation
    # if we still have leftover nps after getting an entity, then get relation
    logger.debug(nps)
    if len(nps) > 0:
        relation_index = get_index_of_relation(nps)
        relation = nps[relation_index]
    elif len(vbs) > 0:
        relation_index = get_index_of_relation(vbs)
        relation = [vbs[relation_index]]
    else:
        # no nouns or verbs for relation, give up
        logger.log(logging.INFO, "Can't find relation")
        return None 
    relation_text = ' '.join([x.text for x in relation])
    entity_text = ' '.join([x.text for x in entity])
    return (relation_text, entity_text)



  