"""Explicit score571 research boundary; frozen F11/Prince APIs remain strict."""
from dataclasses import dataclass
from hashlib import sha256
from functools import cached_property
import compose_native_floatey_score_1114 as Score
import current_prince_body_research_f11_1114 as Previous


@dataclass(frozen=True)
class Input:
    original:bytes
    referenceF11:bytes

    @cached_property
    def previous(self):return Previous.normalize(self.referenceF11,kind='bt-camera-f11')

    @property
    def reference1daca(self):return self.previous.reference1daca

    def metadata(self):return dict(kind='score-571',public_input_SHA256=Score.CANDIDATE,
        research_reference_F11_SHA256=Score.PIN,protected_score_bytes=10,
        historical_research_not_current_delivery=True,outputs=0,Mesen=False)

    def verify_preserved_sites(self,candidate):
        assert candidate[Score.AT:Score.AT+10]==Score.NEW
        return self.previous.verify_preserved_sites(candidate)


def normalize(raw,*,kind):
    assert kind=='score-571'and isinstance(raw,bytes)and sha256(raw).hexdigest()==Score.CANDIDATE
    parent=Score.inverse(raw);assert sha256(parent).hexdigest()==Score.PIN
    return Input(raw,parent)


def load(path):return normalize(path.read_bytes(),kind='score-571')
