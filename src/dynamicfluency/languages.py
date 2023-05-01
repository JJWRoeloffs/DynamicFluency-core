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
    "ru": "Russian",
    "sv": "Swedish",
}

NLTK_TAGGERS = {
    "en": "eng",
    "ru": "rus",
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
    if model == "rus":
        nltk.download("averaged_perceptron_tagger_ru", quiet=True, halt_on_error=True)
    else:
        nltk.download("averaged_perceptron_tagger", quiet=True, halt_on_error=True)
