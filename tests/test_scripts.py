# Currently, none of the scripts are tested.
# However, this least asserts that none of the files have syntax errors

from dynamicfluency.scripts.add_frequency_dictionary import *
from dynamicfluency.scripts.convert_aeneas_to_textgrids import *
from dynamicfluency.scripts.download_models import *
from dynamicfluency.scripts.get_database_columns import *
from dynamicfluency.scripts.make_frequencytagged_girds_from_aligned_grids import *
from dynamicfluency.scripts.make_postagged_grids_from_aligned_grids import *
from dynamicfluency.scripts.make_repetitionstagged_grids_from_postagged_grids import *
from dynamicfluency.scripts.make_syntax_grids_from_postagged_grids import *


def test_true():
    assert True
