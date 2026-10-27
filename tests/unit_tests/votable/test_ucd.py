import pytest

from nena_component_tools.internal.data.votable.ucd import InvalidUcdException, verify_ucd


def test_votable_column_only_allows_valid_ucds():
    verify_ucd('pos.eq.ra')

    with pytest.raises(InvalidUcdException):
        verify_ucd('pos.eqra')
