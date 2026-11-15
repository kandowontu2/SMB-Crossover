"""Explicit current-input boundary for frozen e418 source research.

This never returns an installable current proposal: cf7 keeps its 192 Gimmick
sites in the retained original. The returned reference is labeled1daca and
may feed only the unchanged private e418 recipe. Future merging must retain
the original and validate every preserved site; old factories stay strict.
"""
from dataclasses import dataclass
from functools import lru_cache
import compose_prince_body_world_1114 as Prince
import compose_gimmick_private_window7_1114 as Gimmick


@dataclass(frozen=True)
class ResearchInput:
    kind:str
    original:bytes
    reference1daca:bytes
    preserved_sites:tuple

    def verify_preserved_sites(self,candidate):
        assert isinstance(candidate,bytes)and len(candidate)==len(self.original)
        for at,old,new in self.preserved_sites:
            assert self.reference1daca[at]==old and self.original[at]==new and candidate[at]==new
        return True

    def metadata(self):
        return dict(kind=self.kind,public_input_SHA256=Prince.digest(self.original),
            research_reference_SHA256=Prince.digest(self.reference1daca),
            preserved_current_sites=len(self.preserved_sites),
            private_research_not_current_delivery=True,outputs=0,Mesen=False)


@lru_cache(maxsize=2)
def normalize(raw,*,kind):
    assert isinstance(raw,bytes)
    if kind=='dk-window7-1daca':
        assert Prince.digest(raw)==Gimmick.PIN
        reference=raw;sites=()
    else:
        assert kind=='gimmick-window7-cf7'and Prince.digest(raw)==Gimmick.CANDIDATE
        reference=Gimmick.inverse(raw);sites=Gimmick.bindings(reference)
        assert len(sites)==192 and Gimmick.proposal(reference)[0]==raw
    assert Prince.digest(reference)==Prince.PARENTS['dk-window7-1daca']
    result=ResearchInput(kind,raw,reference,sites)
    assert result.verify_preserved_sites(raw)
    return result


def load(path):
    raw=path.read_bytes();digest=Prince.digest(raw)
    kinds={Gimmick.PIN:'dk-window7-1daca',Gimmick.CANDIDATE:'gimmick-window7-cf7'}
    assert digest in kinds,'Expected exact1daca or explicitly typed currentcf7'
    return normalize(raw,kind=kinds[digest])
