from typing import Set

import nltk
import spacy

VALID_LANGUAGES = {
    "zh": "Chinese",
    "hr": "Croatian",
    "nl": "Dutch",
    "en": "English",
    "fi": "Finnish",
    "de": "German",
    "it": "Italian",
    "ko": "Korean",
    "lt": "Lithuanian",
    "pl": "Polish",
    "ro": "Romanian",
    "sv": "Swedish",
}

NLTK_TAGGERS = {
    "en": "eng",
}

SPACY_MODELS = {
    "zh": "zh_core_web_sm",
    "hr": "hr_core_news_sm",
    "nl": "nl_core_news_sm",
    "en": "en_core_web_sm",
    "fi": "fi_core_news_sm",
    "de": "de_core_news_sm",
    "it": "it_core_news_sm",
    "ko": "ko_core_news_sm",
    "lt": "lt_core_news_sm",
    "pl": "pl_core_news_sm",
    "ro": "ro_core_news_sm",
    "sv": "sv_core_news_sm",
}

NLTK_POS_TAGS = {
    "CC",
    "CD",
    "DT",
    "EX",
    "FW",
    "IN",
    "JJ",
    "JJR",
    "JJS",
    "LS",
    "MD",
    "NN",
    "NNS",
    "NNP",
    "NNPS",
    "PDT",
    "WRB",
    "WP$",
    "WP",
    "WDT",
    "VBZ",
    "VBP",
    "VBN",
    "VBG",
    "VBD",
    "VB",
    "UH",
    "TO",
    "RP",
    "RBS",
    "RB",
    "RBR",
    "PRP",
    "PRP$",
}


def assert_valid_language(lang: str) -> None:
    "A simple helper function to raise when non-valid language string is passed"

    if lang not in VALID_LANGUAGES.keys():
        raise ValueError(f"lang must be one of: {VALID_LANGUAGES.keys()}")


def load_spacy_model(model: str):
    try:
        return spacy.load(model)
    except OSError:
        spacy.cli.download(model)
        return spacy.load(model)


def load_nltk_model(model: str):
    if model == "eng":
        nltk.download("punkt", quiet=True, halt_on_error=True)
        nltk.download("averaged_perceptron_tagger", quiet=True, halt_on_error=True)
    else:
        raise ValueError(f"Language {model} not supported by NLTK")


def get_valid_tags(lang: str) -> Set[str]:
    assert_valid_language(lang)
    if lang in NLTK_TAGGERS.keys():
        return NLTK_POS_TAGS
    elif lang in SPACY_MODELS.keys():
        return {*spacy.glossary.GLOSSARY.keys()}
    else:
        raise ValueError(f"Unknown or unsuppoerted language: {lang}")
