"""Explicit ae66 research input; historical Prince packets remain frozen."""
from dataclasses import dataclass
from functools import cached_property
from hashlib import sha256
import compose_battletoads_native_service_1114 as BT
import current_prince_body_research_571_1114 as Previous


@dataclass(frozen=True)
class Input:
    original:bytes
    reference571:bytes

    @cached_property
    def previous(self):return Previous.normalize(self.reference571,kind='score-571')

    @property
    def referenceF11(self):return self.previous.referenceF11

    @property
    def reference1daca(self):return self.previous.reference1daca

    def metadata(self):return dict(kind='bt-service-ae66',public_input_SHA256=BT.CANDIDATE,
        research_reference_571_SHA256=BT.PIN,protected_BT_service_changed_bytes=160,
        protected_score_bytes=10,historical_research_not_current_delivery=True,outputs=0,Mesen=False)

    def verify_preserved_sites(self,candidate):
        assert len(candidate)==len(self.original)
        sites=[at for at,(a,b)in enumerate(zip(self.reference571,self.original,strict=True))if a!=b]
        assert len(sites)==160 and all(candidate[at]==self.original[at]for at in sites)
        return self.previous.verify_preserved_sites(candidate)


def normalize(raw,*,kind):
    assert kind=='bt-service-ae66'and isinstance(raw,bytes)and sha256(raw).hexdigest()==BT.CANDIDATE
    parent=BT.inverse(raw);assert sha256(parent).hexdigest()==BT.PIN
    return Input(raw,parent)


def load(path):return normalize(path.read_bytes(),kind='bt-service-ae66')
