"""Explicit16a input boundary; frozen590 and older APIs stay strict."""
from dataclasses import dataclass
from functools import cached_property
import compose_prince_body_transition_590_1115 as C


@dataclass(frozen=True)
class Input:
    original:bytes
    reference590:bytes

    @cached_property
    def previous(self):return C.Plan.Current.normalize(self.reference590,kind='prince-graphics-590')

    @property
    def referenceAE(self):return self.previous.referenceAE

    def metadata(self):return dict(kind='prince-body-transition-16a',actual_owning_CPU_ROM_SHA256=C.CANDIDATE,
        exact_inverse_parent_SHA256=C.PIN,preserve_current590_graphics=True,all_unowned_physical_bytes_exact590=True,
        source_qualification_only=True,native_qualified=False,installed=False,outputs=0,Mesen=False)


def normalize(raw,*,kind):
    assert kind=='prince-body-transition-16a'and isinstance(raw,bytes)and C.digest(raw)==C.CANDIDATE
    parent=C.inverse(raw);assert C.digest(parent)==C.PIN
    return Input(raw,parent)
