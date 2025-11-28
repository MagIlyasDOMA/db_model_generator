from pathlib import Path
from typing import Union, Optional, Literal
from .constants import LANGUAGES

__all__ = [
    'PathLike',
    'PathLikeOrNone',
    'NullStr',
    'NullBool',
    'LanguageCodeType',
    'Union',
    'Optional'
]

PathLike = Union[str, Path]
PathLikeOrNone = Optional[PathLike]
NullStr = Optional[str]
NullBool = Optional[bool]
LanguageCodeType = Literal[*LANGUAGES.keys()]
