"""Explicit installed590 input for the AE-owned transition research lease."""
from dataclasses import dataclass
from functools import cached_property
from hashlib import sha256
import compose_prince_window567_1115 as Graphics
import current_prince_body_research_ae66_1114 as Previous


@dataclass(frozen=True)
class Input:
    original:bytes
    referenceAE:bytes

    @cached_property
    def previous(self):return Previous.normalize(self.referenceAE,kind='bt-service-ae66')

    @property
    def reference1daca(self):return self.previous.reference1daca

    def metadata(self):return dict(kind='prince-graphics-590',actual_owning_CPU_ROM_SHA256=Graphics.CANDIDATE,
        exact_lease_reference_AE_SHA256=Graphics.PIN,preserve_qualified_graphics=True,
        protected_BT_service_bytes=160,protected_score_bytes=10,protected_Gimmick_bytes=192,
        source_model_only=True,outputs=0,Mesen=False)


def normalize(raw,*,kind):
    assert kind=='prince-graphics-590'and isinstance(raw,bytes)and sha256(raw).hexdigest()==Graphics.CANDIDATE
    parent=Graphics.inverse(raw);assert sha256(parent).hexdigest()==Graphics.PIN
    return Input(raw,parent)


def load(path):return normalize(path.read_bytes(),kind='prince-graphics-590')
