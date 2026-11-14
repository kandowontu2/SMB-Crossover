"""Explicit current input boundary for DK resource/source models only.

Normalization supplies the frozen421 model. It does not authorize composing
or delivering a DK result without a separate29-byte-preserving wrapper.
"""
from hashlib import sha256
from pathlib import Path

import compose_shared_world_chr_reset_1114 as Reset

NIGHTLY=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
KINDS=('hidden-421','world-chr-82')


def normalize(raw,*,kind):
    assert isinstance(raw,bytes)
    actual=sha256(raw).hexdigest()
    if kind=='hidden-421':
        assert actual==Reset.PIN,'Explicit hidden-421 input required'
        normalized=raw
    elif kind=='world-chr-82':
        assert actual==Reset.CANDIDATE,'Explicit world-chr-82 input required'
        normalized=Reset.inverse(raw)
    else:raise ValueError('Unknown DK review input kind')
    assert sha256(normalized).hexdigest()==Reset.PIN
    return normalized,dict(actual_input_SHA256=actual,explicit_kind=kind,
        normalized_frozen421_SHA256=Reset.PIN,source_models_only=True,
        new_DK_composition_requires_qualified_macro_preservation=True)


def read(*,kind):return normalize(NIGHTLY.read_bytes(),kind=kind)
