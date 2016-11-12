from spacy.en import English


nlp = English()

# Tags that we probably don't want in our noun phrases
blacklist_tags = set(["DT"])

# Verbs that are probably not relations
blacklist_verbs = set("is 's are be been being 're".split())

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
    """Removes determiners from NPs and returns stringified version"""
    cleaned_nps = []
    for np in nps:
        cleaned = []
        for word in np:
            if word.tag_ not in blacklist_tags:
                cleaned.append(word)
        cleaned_nps.append(cleaned)
    return cleaned_nps


def get_vbs(parsed):
    return [word for word in parsed if word.tag_ in verb_tags]


def prune_vbs(verbs):
    pruned = []
    for verb in verbs: 
        if verb.text.lower() not in blacklist_verbs:
            pruned.append(verb)
    return pruned


def clean_vbs(verbs):
    cleaned_verbs = []
    for verb in verbs:
        cleaned_verbs.append(verb)
    return cleaned_verbs


def extract_nps(parsed):
    nps = get_nps(parsed)
    pruned = prune_nps(nps)
    clean = clean_nps(pruned)
    return clean


def extract_vbs(parsed):
    vbs = get_vbs(parsed)
    pruned = prune_vbs(vbs)
    clean = clean_vbs(pruned)
    return clean


def count_proper_nouns(np):
    return len([x for x in np if x.tag_ in pnoun_tags])

 
def get_most_nnp_index(nps):
    # Returns the index of the np with the most proper nouns
    counts_with_indices = [(count_proper_nouns(np), i) for i, np in enumerate(nps)]
    counts_with_indices = sorted(counts_with_indices, reverse=True)
    return counts_with_indices[0][1]

def get_index_of_entity(nps):
    # Given a list of noun phrases, this tries to work out which is the entity
    # e.g. [["headquarters"], ["Warner","Bros"]] should return 1
    
    # first try to find the noun phrase with the most proper nouns
    best_index = 0
    most_nnps = 0
    for np in nps:
        pass




def extract_triple(sentence):
    print('extracting triple')
    parsed = parse(sentence)
    nps = extract_nps(parsed)
    vbs = extract_vbs(parsed)
    print(nps)
    print(vbs)
    print(get_most_nnp_index(nps))
    print("---")

    
