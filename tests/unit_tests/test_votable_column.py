import pytest

from nena_component_tools.internal.data.votable_column import VOTableColumn, InvalidUcdException


def test_votable_column_only_allows_valid_ucds():
    VOTableColumn.verify_ucd('pos.eq.ra')

    with pytest.raises(InvalidUcdException):
        VOTableColumn.verify_ucd('pos.eqra')
