#!/usr/bin/env python3
from __future__ import annotations

import sys
import argparse


def parse_arguments() -> argparse.Namespace:
    from dynamicfluency.model_data import VALID_LANGUAGES

    parser = argparse.ArgumentParser(
        description="Downloads the required models to your machine."
    )
    parser.add_argument(
        "-l",
        "--language",
        help="The language to get the tagging model of",
        choices=[x for k, v in VALID_LANGUAGES.items() for x in (k, v)],
        nargs="?",
        default="en",
    )

    args = parser.parse_args()

    if args.language in VALID_LANGUAGES.values():
        [args.language] = [k for k, v in VALID_LANGUAGES.items() if v == args.language]

    if args.language not in VALID_LANGUAGES.keys():
        parser.error(f"{args.language} is not a valid language")

    return args


def main():
    print("Starting process")
    test_sentence = "This is the sentence the downloaded data will be tested on"

    # I have seen the imports fail on some people's machine,
    # when they have a particularly weird python setup
    # as both spacy and nltk can be weird with installing properly sometimes
    # In fact, those people complaining it didn't work is why this script exists.
    try:
        import nltk
    except ImportError:
        sys.stderr.write("NLTK is currently not installed (correctly)")
        raise

    try:
        import spacy
    except ImportError:
        sys.stderr.write("Spacy is currently not installed (correctly)")
        raise

    try:
        from dynamicfluency.model_data import (
            NLTK_TAGGERS,
            SPACY_MODELS,
            assert_valid_language,
            load_spacy_model,
            load_nltk_model,
        )
    except ImportError:
        sys.stderr.write("It appears DynamicFluency is not installed properly.")
        raise

    args: argparse.Namespace = parse_arguments()
    assert_valid_language(args.language)

    if args.language in NLTK_TAGGERS.keys():
        load_nltk_model(NLTK_TAGGERS[args.language])
        test_tokens = nltk.word_tokenize(test_sentence)
        print("NLTK: Tokeniser downloaded succesfully")
        _ = nltk.pos_tag(test_tokens)
        print("NLTK: Tagger downloaded succesfully")
    elif args.language in SPACY_MODELS.keys():
        nlp = load_spacy_model(SPACY_MODELS[args.language])
        _ = nlp(test_sentence)
        print("SPACY: Language downloaded succesfully")
    else:
        raise ValueError(f"Unknown or unsupported language {args.langauge}")


if __name__ == "__main__":
    main()
