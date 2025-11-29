from __future__ import annotations

import numpy as np

from ..math_core.fields import Array
from .sensory import ParsedSensory

def glyphs_to_forcing(glyphs: ParsedSensory, shape: tuple[int, ...]) -> Array:
    """
    Converts glyphs to forcing terms h_u and h_v.
    This is a placeholder implementation.
    """
    return np.zeros(shape + (2,))
