from __future__ import annotations

from typing import TypeAlias

import numpy as np

Array: TypeAlias = np.ndarray

def make_random_psi(shape: tuple[int, ...]) -> Array:
    """Creates a random ψ field with unit magnitude."""
    phase = np.random.uniform(0, 2 * np.pi, size=shape)
    return np.exp(1j * phase)
