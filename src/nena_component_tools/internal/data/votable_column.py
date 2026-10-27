from astropy.units import Unit
from astropy.io.votable.ucd import check_ucd
import numpy.typing as npt


class InvalidUcdException(Exception):
    pass

class VOTableColumn:
    def __init__(self):
        pass

    @classmethod
    def new(cls, name: str, ucd: str, unit: Unit, array: npt.NDArray):

        return cls()

    @staticmethod
    def verify_ucd(ucd_string: str):
        is_valid = check_ucd(ucd_string, check_controlled_vocabulary=True)
        if not is_valid:
            raise InvalidUcdException(f'`{ucd_string}` is not a valid controlled vocabulary UCD. '
                                      f'See `https://ivoa.net/documents/UCD1+/20241218/EN-UCDlist-1.6-20241218.html'
                                      f'#sec:list` for valid options.')
