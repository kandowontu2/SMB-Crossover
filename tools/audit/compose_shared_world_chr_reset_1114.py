"""Root-granted29B area CHR reset, typed421 composition/inverse in memory only."""
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

import current_smb2_hidden_input_1114 as Current
import measure_shared_world_chr_reset_1114 as Measure

R=Path(__file__).resolve().parents[2]
PIN=Current.HIDDEN
CANDIDATE='82ec0446873b28af458e7686fec87938feaf798a0a893b44e4dccfd071ccfd63'
GRANT=R/'docs/qa/allocations/shared-world-chr-reset-1114.json'
GRANT_SHA='76b4de7eefd18406d81bce95875e4cf30cd1383be05b625f7817efdfba25eda9'
MEASURE_SHA='599a6213847c3726a18b1894586c151f47c5ab7e53f51e75a42bbf50dd831e64'


def digest(raw):return sha256(raw).hexdigest()


def allocation():
    data=GRANT.read_bytes();assert digest(data)==GRANT_SHA
    q=json.loads(data)
    assert q['parent_SHA256']==PIN and q['measurement_tool_SHA256']==MEASURE_SHA
    assert digest(Path(Measure.__file__).read_bytes())==MEASURE_SHA
    s=q['span'];at,end=s['file_half_open'];old=bytes.fromhex(s['preimage_hex']);new=bytes.fromhex(s['proposed_hex'])
    assert (at,end,len(old),len(new))==(1034867,1034896,29,29)
    assert digest(old)==s['preimage_SHA256']and digest(new)==s['proposed_SHA256']
    return q,at,old,new


@lru_cache(maxsize=1)
def bindings(raw):
    assert isinstance(raw,bytes)and digest(raw)==PIN
    q,at,old,new=allocation();source=Measure.measure(raw)
    assert source['span']['old_hex']==old.hex()and source['span']['proposed_hex']==new.hex()
    assert raw[at:at+29]==old and raw[at+29:at+36].hex()==q['retained_suffix']['hex']
    typed=Current.normalize(raw,kind='hidden-421')
    assert typed.postbg[at:at+29]==old
    protected={i for start,size in Current.protected_envelopes()for i in range(start,start+size)}
    allowed=frozenset(range(at,at+29));assert not allowed&protected
    return typed,at,old,new,source


def proposal(raw):
    typed,at,old,new,source=bindings(raw)
    # Apply only this exact grant to the qualified legacy input, then use the
    # existing small typed wrapper as sole owner of preserving all176 fixes.
    legacy=typed.postbg[:at]+new+typed.postbg[at+29:]
    result,info=typed.preserve(legacy,legacy_result_SHA256=digest(legacy),
        allowed_component_offsets=range(at,at+29))
    assert digest(result)==CANDIDATE
    changed={i for i,(a,b)in enumerate(zip(raw,result,strict=True))if a!=b}
    assert len(changed)==28 and changed<=set(range(at,at+29))
    assert all(result[i]==raw[i]for i in range(len(raw))if i not in changed)
    assert result[at+29:at+36]==raw[at+29:at+36]
    return result,dict(info,allocation_SHA256=GRANT_SHA,owning_parent_SHA256=PIN,
        candidate_SHA256=CANDIDATE,changed_bytes=len(changed),granted_bytes=29,
        inverse_mutable_Downloads_dependency=False,isolated_macro_CPU_cases=source['CPU_cases'],
        source_qualification_complete=True,source_scope='Granted29B common reset only; private player window conflicts excluded',
        native_qualified=False,installed=False,outputs=0)


def inverse(raw):
    assert isinstance(raw,bytes)and digest(raw)==CANDIDATE
    _,at,old,new=allocation();assert raw[at:at+29]==new
    parent=raw[:at]+old+raw[at+29:]
    assert digest(parent)==PIN
    assert proposal(parent)[0]==raw
    return parent


def load_current_image(path=None):
    """Explicit CLI boundary; portable after either exact421 or82ec delivery."""
    raw=(Measure.C.ROM if path is None else Path(path)).read_bytes()
    if digest(raw)==PIN:return proposal(raw)[0]
    assert digest(raw)==CANDIDATE,'Expected exact421 or exact private82ec'
    assert proposal(inverse(raw))[0]==raw
    return raw


if __name__=='__main__':
    candidate=load_current_image();parent=inverse(candidate);_,info=proposal(parent)
    print(json.dumps(info,separators=(',',':')),flush=True)
