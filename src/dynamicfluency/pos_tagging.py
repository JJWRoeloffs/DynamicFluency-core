from __future__ import annotations

from collections import namedtuple
from typing import List, Union

import nltk
from praatio.data_classes.textgrid_tier import TextgridTier

from dynamicfluency.helpers import entrylist_labels_to_string, make_lowercase_entrylist


def generate_tags_from_entrylist(entryList: List[namedtuple]) -> List[Union[str, str]]:

    text = entrylist_labels_to_string(entryList)
    tokens: List[str] = nltk.word_tokenize(text)
    return nltk.pos_tag(tokens)


# Jankyness needed because the NLTK tokenise split sometimes splits words into smaller sub-sections
def allign_tags(
    tags: List[Union[str, str]], entryList: List[namedtuple]
) -> List[namedtuple]:
    """Make an alligned entrylist out of NLTK generated pos_tags and the entryList those were generated from."""

    new_entryList = []
    for entry in entryList:
        if not entry.label:
            new_entryList.append(entry._replace(label=""))
            continue
        word = ""
        label = ""
        while entry.label != word:
            word += tags[0][0]
            label = " ".join([label, "_".join(tags[0])])
            tags.pop(0)
        new_entryList.append(entry._replace(label=label.strip()))
    return new_entryList


def make_pos_tier(words_tier: TextgridTier, *, name: str = "POStags") -> TextgridTier:
    """Makes a POS tagged tier from a textgrid tier with alligned words"""

    nltk.download("punkt", quiet=True, halt_on_error=True)
    nltk.download("averaged_perceptron_tagger", quiet=True, halt_on_error=True)

    lowercase_entryList = make_lowercase_entrylist(words_tier.entryList)

    tags = generate_tags_from_entrylist(lowercase_entryList)
    tag_entryList = allign_tags(tags, lowercase_entryList)

    return words_tier.new(name=name, entryList=tag_entryList)
