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
    components = parse_ucd(ucd_string)
    ucd_components = set(map(lambda x: x[1], components))
    if not ucd_components.isdisjoint(['time.epoch', 'time.crossing', 'time.start', 'time.end']):
        raise InvalidColumnTypeException(f'`{ucd_string}` contains a time which should be related to a time system. '
                                         f'Use `VOTableTimeColumn` for this time column.')
