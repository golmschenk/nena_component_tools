from astropy.io.votable.ucd import check_ucd, parse_ucd


class InvalidUcdException(Exception):
    pass


class InvalidColumnTypeException(Exception):
    pass


def verify_ucd(ucd_string: str) -> None:
    is_valid = check_ucd(ucd_string, check_controlled_vocabulary=True)
    if not is_valid:
        raise InvalidUcdException(f'`{ucd_string}` is not a valid controlled vocabulary UCD. '
                                  f'See `https://ivoa.net/documents/UCD1+/20241218/EN-UCDlist-1.6-20241218.html'
                                  f'#sec:list` for valid options.')


def verify_not_time_system_ucd(ucd_string: str) -> None:
    has_time_system_ucd = check_if_ucd_composed_word_includes_time_system_ucd_word(ucd_string)
    if has_time_system_ucd:
        raise InvalidColumnTypeException(f'`{ucd_string}` contains a time which should be related to a time system. '
                                         f'Use `VOTableTimeColumn` for this time column.')


def check_if_ucd_composed_word_includes_time_system_ucd_word(ucd_string: str) -> bool:
    time_system_ucds = ['time.epoch', 'time.crossing', 'time.start', 'time.end']
    has_time_system_ucd = check_if_any_ucd_words_are_in_ucd_composed_word(time_system_ucds, ucd_string)
    return has_time_system_ucd


def check_if_ucd_composed_word_includes_coordinate_system_ucd_word(ucd_string: str) -> bool:
    coordinate_system_ucds = ['pos.eq.ra', 'pos.eq.dec']
    has_time_system_ucd = check_if_any_ucd_words_are_in_ucd_composed_word(coordinate_system_ucds, ucd_string)
    return has_time_system_ucd


def check_if_any_ucd_words_are_in_ucd_composed_word(time_system_ucds: list[str], ucd_string: str) -> bool:
    components = parse_ucd(ucd_string)
    ucd_components = set(map(lambda x: x[1], components))
    has_time_system_ucd = not ucd_components.isdisjoint(time_system_ucds)
    return has_time_system_ucd
