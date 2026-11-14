"""Explicit typed fa66 input normalization; legacy factory PINs stay frozen.

Normalization is for source/metadata reuse. A composition must call preserve()
with its own exact legacy output hash and allowed component offsets before the
result can carry the current cheat fixes. Merely normalizing is never delivery.
"""
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Literal

import compose_smb2_cheat_cold_mirror_1113 as C

POSTBG=C.Owner.PIN
CHEAT=C.CANDIDATE
KINDS={'postbg12397':POSTBG,'cheat-fa66':CHEAT}
COLD_SOURCE='e19e7796b6a525c4e8b17b08a1171574fb7563197775c44e8e84c6b3bb7bb98a'
OWNER_SOURCE=C.OWNER_SOURCE


def digest(raw):return sha256(raw).hexdigest()


def dependencies():
    assert digest(Path(C.__file__).read_bytes())==COLD_SOURCE
    assert digest(Path(C.Owner.__file__).read_bytes())==OWNER_SOURCE


def protected_envelopes():
    owner=tuple((at,len(old))for at,old,new in C.Owner.SPANS)
    gates=tuple((16+bank*8192+(C.BRIDGE&8191),len(C.CANONICAL))
                for bank in(119,120,125,127))
    return owner+gates


@dataclass(frozen=True)
class CurrentInput:
    kind:Literal['postbg12397','cheat-fa66']
    original:bytes
    postbg:bytes
    inverse_steps:tuple[str,...]

    @property
    def original_SHA256(self):return digest(self.original)

    def preserve(self,legacy_result,*,legacy_result_SHA256,allowed_component_offsets):
        """Restore current layers on an explicitly pinned legacy composition.

        allowed_component_offsets is the caller's independently qualified
        component ownership set. Every changed legacy byte must belong to it;
        even unchanged bytes in the complete cheat envelopes stay protected.
        """
        dependencies()
        assert self.kind in KINDS and digest(self.original)==KINDS[self.kind]
        assert digest(self.postbg)==POSTBG
        expected_steps=()if self.kind=='postbg12397'else('cold_mirror.inverse fa66->e8','owner.inverse e8->12397')
        assert self.inverse_steps==expected_steps,'Typed provenance must retain the exact strict inverse chain'
        assert isinstance(legacy_result,bytes)and len(legacy_result)==len(self.postbg)
        assert digest(legacy_result)==legacy_result_SHA256
        allowed=frozenset(allowed_component_offsets)
        assert all(isinstance(i,int)and 0<=i<len(legacy_result)for i in allowed)
        protected={i for at,size in protected_envelopes()for i in range(at,at+size)}
        assert not allowed&protected,'Component ownership overlaps complete current cheat envelopes'
        changed={i for i,(a,b)in enumerate(zip(self.postbg,legacy_result,strict=True))if a!=b}
        assert changed<=allowed,'Legacy result changed bytes outside its qualified component'
        assert all(legacy_result[i]==self.postbg[i]for i in protected)
        result=bytearray(legacy_result)
        current={i for i,(a,b)in enumerate(zip(self.postbg,self.original,strict=True))if a!=b}
        assert current<=protected and not changed&current
        for i in current:result[i]=self.original[i]
        result=bytes(result)
        assert all(result[i]==self.original[i]for i in range(len(result))if i not in changed)
        assert all(result[i]==legacy_result[i]for i in changed)
        assert all(result[at:at+size]==self.original[at:at+size]for at,size in protected_envelopes())
        return result,dict(input_kind=self.kind,current_input_SHA256=self.original_SHA256,
            normalized_postbg_SHA256=POSTBG,legacy_result_SHA256=legacy_result_SHA256,
            output_SHA256=digest(result),inverse_steps=list(self.inverse_steps),
            component_changed_bytes=len(changed),current_fix_changed_bytes_preserved=len(current),
            all_current_bytes_outside_component_exact=True,complete_current_cheat_envelopes_exact=True,
            new_ROM_bytes=0,outputs=0,native_qualified=False,installed=False)


def normalize(raw,*,kind:Literal['postbg12397','cheat-fa66']):
    dependencies()
    assert kind in KINDS,'Caller must choose an explicitly typed current input'
    assert isinstance(raw,bytes)and digest(raw)==KINDS[kind]
    if kind=='postbg12397':return CurrentInput(kind,raw,raw,())
    owner=C.inverse(raw)
    assert digest(owner)==C.PIN
    public=C.Owner.inverse(owner)
    assert digest(public)==POSTBG and C.proposal(C.Owner.proposal(public)[0])[0]==raw
    return CurrentInput(kind,raw,public,('cold_mirror.inverse fa66->e8','owner.inverse e8->12397'))
