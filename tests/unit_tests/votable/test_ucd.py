import pytest

from nena_component_tools.internal.data.votable.ucd import InvalidUcdException, verify_ucd, InvalidColumnTypeException, \
    verify_not_time_system_ucd, check_if_ucd_composed_word_includes_coordinate_system_ucd_word


def test_votable_column_only_allows_valid_ucds():
    verify_ucd('pos.eq.ra')

    with pytest.raises(InvalidUcdException):
        verify_ucd('pos.eqra')


def test_verify_not_time_system_ucd_composed_word():
    verify_not_time_system_ucd('time.period')

    with pytest.raises(InvalidColumnTypeException):
        verify_not_time_system_ucd('time.epoch')


def test_check_if_ucd_composed_word_includes_coordinate_system_ucd_word():
    assert check_if_ucd_composed_word_includes_coordinate_system_ucd_word('pos.eq.dec')
    assert not check_if_ucd_composed_word_includes_coordinate_system_ucd_word('time.epoch')
