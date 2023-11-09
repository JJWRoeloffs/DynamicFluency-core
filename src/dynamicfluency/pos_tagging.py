from __future__ import annotations

from typing import List, Tuple

import nltk
from praatio.data_classes.interval_tier import IntervalTier
from praatio.utilities.utils import Interval

from dynamicfluency.helpers import entrylist_labels_to_string, make_lowercase_entrylist
from dynamicfluency.model_data import (
    NLTK_TAGGERS,
    SPACY_MODELS,
    assert_valid_language,
    load_nltk_model,
    load_spacy_model,
)


def generate_tags_from_entrylist(
    entryList: List[Interval], *, lang: str = "en"
) -> List[Tuple[str, str]]:
    assert_valid_language(lang)
    text = entrylist_labels_to_string(entryList)
    if lang in NLTK_TAGGERS.keys():
        load_nltk_model(NLTK_TAGGERS[lang])
        tokens: List[str] = nltk.word_tokenize(text)
        return nltk.pos_tag(tokens=tokens, lang=NLTK_TAGGERS[lang])
    elif lang in SPACY_MODELS.keys():
        nlp = load_spacy_model(SPACY_MODELS[lang])
        return [(token.text, token.pos_) for token in nlp(text)]
    else:
        raise ValueError(f"Unknown or unsupported language: {lang}")


# Jankyness needed because the NLTK tokenise split sometimes splits words into smaller sub-sections
def align_tags(
    tags: List[Tuple[str, str]], entryList: List[Interval]
) -> List[Interval]:
    """Make an aligned entrylist out of NLTK/SpaCy generated pos_tags and the entryList those were generated from."""

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


def make_pos_tier(
    words_tier: IntervalTier, *, name: str = "POStags", lang: str = "en"
) -> IntervalTier:
    """Makes a POS tagged tier from a textgrid tier with aligned words"""
    assert_valid_language(lang)

    lowercase_entryList = make_lowercase_entrylist(words_tier.entryList)

    tags = generate_tags_from_entrylist(lowercase_entryList, lang=lang)
    tag_entryList = align_tags(tags, lowercase_entryList)

    return words_tier.new(name=name, entryList=tag_entryList)
