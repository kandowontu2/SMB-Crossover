"""Separate explicit f11 research boundary; older cf7/default APIs stay strict."""
from dataclasses import dataclass
from functools import lru_cache
import current_prince_body_research_input_1114 as Previous
import compose_battletoads_camera_handoff_1114 as BT


@dataclass(frozen=True)
class ResearchInput:
    kind:str
    original:bytes
    previous:Previous.ResearchInput
    protected_BT_spans:tuple

    @property
    def reference1daca(self):return self.previous.reference1daca

    def verify_preserved_sites(self,candidate):
        assert isinstance(candidate,bytes)and len(candidate)==len(self.original)
        assert self.previous.verify_preserved_sites(candidate)
        for at,old,new in self.protected_BT_spans:
            assert self.previous.original[at:at+len(old)]==old
            assert candidate[at:at+len(new)]==self.original[at:at+len(new)]==new
        return True

    def metadata(self):
        return dict(kind=self.kind,public_input_SHA256=BT.digest(self.original),
            research_reference_SHA256=BT.digest(self.reference1daca),
            preserved_current_changed_sites=244,Gimmick_sites=192,BT_changed_sites=52,
            BT_full_preimage_bytes=56,private_research_not_current_delivery=True,outputs=0,Mesen=False)


@lru_cache(maxsize=1)
def normalize(raw,*,kind):
    assert isinstance(raw,bytes)and kind=='bt-camera-f11'and BT.digest(raw)==BT.CANDIDATE
    cf7=BT.inverse(raw);assert BT.digest(cf7)==BT.PIN
    previous=Previous.normalize(cf7,kind='gimmick-window7-cf7')
    result=ResearchInput(kind,raw,previous,BT.spans())
    assert result.verify_preserved_sites(raw)
    return result


def load(path):return normalize(path.read_bytes(),kind='bt-camera-f11')
