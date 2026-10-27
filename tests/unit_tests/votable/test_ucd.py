import pytest

from nena_component_tools.internal.data.votable.ucd import InvalidUcdException, verify_ucd, InvalidColumnTypeException, \
    verify_not_time_system_ucd


def test_votable_column_only_allows_valid_ucds():
    verify_ucd('pos.eq.ra')

    with pytest.raises(InvalidUcdException):
        verify_ucd('pos.eqra')


def test_verify_not_time_column():
    verify_not_time_system_ucd('time.period')

    with pytest.raises(InvalidColumnTypeException):
        verify_not_time_system_ucd('time.epoch')
