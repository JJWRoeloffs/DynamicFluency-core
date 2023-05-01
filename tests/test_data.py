from __future__ import annotations
import nltk

import pytest
from pathlib import Path

from dynamicfluency.data import DATAFILE, get_valid_tags
from dynamicfluency.languages import (
    SPACY_MODELS,
    NLTK_TAGGERS,
    VALID_LANGUAGES,
    assert_valid_language,
    load_nltk_model,
    load_spacy_model,
)


class TestDataFile:
    def test_data_files(self):
        assert isinstance(DATAFILE, Path)
        assert DATAFILE.exists()
        assert DATAFILE.is_file()
        assert DATAFILE.suffix == ".csv"
        assert DATAFILE.is_absolute()
        assert not DATAFILE.is_reserved()

    def test_data_tags(self):
        tags = get_valid_tags()
        assert isinstance(tags, list)
        assert tags
        for tag in tags:
            assert isinstance(tag, str)


class TestLanguageDicts:
    def test_correct_keys(self):
        assert {**SPACY_MODELS, **NLTK_TAGGERS}.keys() == VALID_LANGUAGES.keys()

    def test_validity_check_pass(self):
        for lang in VALID_LANGUAGES:
            assert_valid_language(lang)

    def test_validity_check_fail(self):
        with pytest.raises(ValueError):
            assert_valid_language("ja")


class TestModelsAvailable:
    def test_spacy_models_available(self):
        for model in SPACY_MODELS.values():
            nlp = load_spacy_model(model)
            assert nlp("blah blah")

    def test_nltk_models_available(self):
        for model in NLTK_TAGGERS.values():
            load_nltk_model(model)
            tokens = nltk.pos_tag(tokens=["blah", "blah"], lang=model)
            assert tokens
