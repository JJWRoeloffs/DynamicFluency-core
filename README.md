# DynamicFluency-core

The base Python package for [DynamicFluency](https://github.com/JJWRoeloffs/DynamicFluency): track an L2 speaker's ability through time. 

This package is effectively a wrapper around a myriad of other projects to allow for smooth integration with Praat. Praat scripts cannot naively call any other programming language, making calling command-line executable within them the only option. This package exposes those needed scripts.

Theoretically speaking, this project can also be used as a library that exposes functions for the same functionality as the non-trivial scripts. For "documentation" of those, please just look at the scripts themselves and, if that is not specific enough, the tests. 

## Installing

This Python package can be installed with pip, requiring Python 3.9 or higher. To install, simply run:
```sh
pip install dynamicfluency
```
This does not download everything directly. Some scripts require language models to be installed, which are downloaded on demand. To download those immediately, check out the `download_models` script below.

## Exposed scripts

These are the scripts exposed by this project. All of them also have a `-h` / `--help` argument that shows a similar explanation and all of them can take arguments both with a short `-n` and a long `--argument_name` name specifier.
### Scripts meant for direct use

#### `add_frequency_dictionary`
```sh
python -m dynamicfluency.scripts.add_frequency_dictionary -t [table_name] -f [dictionary_file] -b [database_file] -s [seperator] -e [if_exists]
```

DynamicFluency makes use of a sqlite3 .db file to store corpus word frequencies. This script is to be called directly by the user if they want to add an extra corpus. (by default, DynamiFluency has `subtlexus` and `subtlexnl`) This can be to add support to another language, or because a different type of frequency data is required.

The arguments are the following
* `table_name` The name to store this dictionary under, this is the name you later need to use to retrieve it in the configuration
* `dictionary_file` The .csv that you want to add to the database. This csv should have one column "WordForms," which contains the lemmas that are actually being looked up. All other columns should contain numerical data that can be put into the output of DynamicFluency
* `database_file` The .db file you want to add the dictionary to. If you're in the main DynamicFluency directory and haven't changed this, this will be `./databases/main.db`.
    * Default: `./databases/main.db`
* `separator` The character that separates the columns in the .csv.
    * Default: `","`
* `if_exists` What to do if a table with the specified name already exists in the database. Either "fail" or "replace"
    * Default: `"fail"`
    
#### `download_models`
```sh
python -m dynamicfluency.scripts.download_models -l [language]
```
This script pre-downloads the language models needed for running the scripts (and with that DynamicFluency). Running this can be useful if you want to be able to use the system offline, or for debugging. (Something going wrong whilst downloading is one of the most common ways the system can fail.)

The argument is the following:
* `language` The language to download the models for.
    * Default: `"en"` (English)
    
### Scripts meant only for indirect use via DynamicFluency
#### `convert_aeneas_to_textgrid`
```sh
python -m dynamicfluency.scripts.convert_auneas_to_textgrid -d [directory]
```
This script looks for all `*.tokens.json` and `*.phrases.json` files in a directory and converts them to an alignment TextGrid with the same name and `.alignment.TextGrid` extension

The argument is the following:
* `directory` The directory to look & save in.
    * Default: `./output`

#### `get_database_columns`
```sh
python -m dynamicfluency.scripts.get_databse_clumns -t [table_name] -b [database] -d [directory]
```
This script exposes getting all the column names from a database table. This is needed to allow users to specify which ones they want the information from. To allow the praat script to find these columns, they are saved to `clumns_names.csv` in the specified directory.

The arguments are the following:
* `table_name` The name of the table to get the column names from
* `database` The sqlite3 .db file to read from.
    * Default: `./databases/main.db`
* `directory` The directory to save the output column_names.csv to.
    * Default: `./output`

#### `make_frequencytagged_grids_from_aligned_grids`
```sh
python -m dynamicfluency.scripts.make_frequencytagged_grids_from_aligned_grids -t [table_name] -a [alignment] -b [database] -d [directory] -i [to_ignore] -c [columns]
```
This script uses the specified frequency dictionary table from the specified sqlite3 database file to create a new textgrid from the force-aligned specified one with a tier for each specified column of that database table that contains the information from that column for the word form at that time in the original textgrid.

It finds the alignment grids to use by globbing for for all the `*.alignment.TxtGrid` files in that directory, and saves its output as `.frequency.TextGrid` files with the same name.

The arguments are the following:
* `table_name` The name of the table to get the information from
* `alignment` The type of alignment file to generate from. Either `"maus"` `"aeneas"` or `"whisper"`
* `database` The sqlite3 database file to load
    * Default: `./databases/main.db`
* `directory` The directory to find the `*.alligenment.TextGrid` files in.
    * Default: `./output`
* `to_ignore` The words to not assign any value, separated by only commas (e.g. `"uh,uhm"`)
    * Default: `None`
* `columns` The database columns to get the information from. If None/left empty, all columns of that table are selected
    * Default: `None`
    

#### `make_postagged_grids_from_aligned_grids`
```sh
python -m dynamicfluency.scripts.make_postagged_grids_from_aligned_grids -a [alignment] -d [directory] -l [language]
```
This script creates a new textgrid from the alignment textgrid that contains the words plus their Part Of Speech tag in `this_JJ, format_NNS`

It finds the alignment grids to use by globbing for all the `*.alignment.TxtGrid` files in that directory and saves them as `*.pos_tags.TextGrid` with the same name.

The arguments are the following:
* `alignment` The type of alignment file to generate from. Either `"maus"` `"aeneas"` or `"whisper"`
* `directory` The directory to find the `*.alligenment.TextGrid` files in.
    * Default: `./output`
* `language` The language to load the model from. 
    * Default: `"en"` (English)
    
#### `make_repetitionstagged_grids_from_postagged_grids`
```sh
python -m dynamicfluency.scripts.make_repetitionstagged_grids_from_postagged_grids -d [directory] -m [max_read] -i [to_ignore]
```
This script creates a new textgrid from the pos textgrid that contains two tiers, one with the repetitions, and one with the frequency distribution.

The frequency distribution is simply `nltk.FreqDist`, which each word getting assigned the value `nr_occurences / nr_words_total`.

The repetition measure is custom, it is one divided by the number of words between this word and the previous occurrence of this word. 

It finds the pos grids to use by globbing for all the `*.pos_tags.TxtGrid` files in that directory and saves them as `*.repititions.TextGrid` with the same name.

The arguments are the following:
* `directory` The directory to find the `*.pos_tags.TextGrids` files in.
    * Default: `./output`
* `max_raed` The maximum amount of words to look back for the repetitions.
    * Default: `300`
* `to_ignore` The words to not assign any value, separated by only commas (e.g. `"uh,uhm"`)
    * Default: `None`

#### `make_syntax_grids_from_postagged_grids`
```sh
python -m dynamicfluency.scripts.make_syntax_grids_from_postagged_grids -d [directory] -l [language]
```
This script creates a new textgrid from the pos textgrid that contains two point tiers, one that identifies the clausal verbs, and one that identifies all the verb phrases. 

This script is, in many ways, a stub. It is based on TAASSC, which works in a similar manner.

It finds the pos grids to use by globbing for all the `*.pos_tags.TxtGrid` files in that directory and saves them as `*.repititions.TextGrid` with the same name.

The arguments are the following:
* `directory` The directory to find the `*.pos_tags.TextGrids` files in.
    * Default: `./output`
* `language` The language to load the model from. 
    * Default: `"en"` (English)
    
## Code style

For code formatting, [Black](https://github.com/psf/black) is used with default settings. Some of the naming from [praatio](https://github.com/timmahrt/praatIO) (e.g. `entryList`) is taken over, but, generally, the Python convention for naming is taken over.
Also, I, (JJWRoeloffs,) am dyslexic, so there might be some spelling errors in the variable names and docstrings. If you find some, pull requests are welcome!

Lastly, this was my first ever Python project, (which should be especially apparent from older commits,) written for a research internship, please expect to be baffled by weird choices, and do not see this as a portfolio project. I can do better than this.
## Tests

Running the tests can be done with the following command:
```sh
# Install the current version of the package locally to be able to test it.
python3 -m pip install -e .

python3 -m pytest --cov=autobi tests/
```

These tests will download a lot of language models on the first go, as it checks all supported languages. They are going to take a few minutes the first time they're run
