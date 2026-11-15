"""Frozen role-aware Star facade: measured late edge for remaining gap roles."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
import replay_wwf_bigelow_star_gap_7a80_1115 as Previous
import replay_smb1_alts_full11_1114 as Text

R,ROM,W,N,PIN,IDENTITIES=Previous.R,Previous.ROM,Previous.W,Previous.N,Previous.PIN,Previous.IDENTITIES
Frozen,normalize=Previous.Frozen,Previous.normalize
PARENT='cd3e0f19001abb96aa8f1ba0d77addba6aa293b9093633fb737d1c4404d98e20'
EXTRA={'savage':'Savage','andre':'Andre'}


@lru_cache(maxsize=6)
def bindings(raw,key='savage'):
    old=Previous.bindings(raw,key)
    if key not in EXTRA:return old
    q=deepcopy(old);qualified=Previous.bindings(raw,'bigelow')
    q['ram']['PlatformCollisionFlag']=qualified['ram']['PlatformCollisionFlag']
    q['hooks']['PositionPlayerOnHPlat']=deepcopy(qualified['hooks']['PositionPlayerOnHPlat'])
    return q


@lru_cache(maxsize=6)
def controller(raw,key='savage'):
    assert sha256(Path(Previous.__file__).read_bytes()).hexdigest()==PARENT
    old=Previous.controller(raw,key)
    if key not in EXTRA:return old
    generic=Previous.Previous.controller(raw,'bigelow')
    assert old.split('\n',1)[1]==generic.split('\n',1)[1],'Exact original role-neutral ordinary control body'
    qualified=Previous.controller(raw,'bigelow');body=qualified.split('\n',1)[1]
    assert body.count('Real existing native helper carried Bigelow')==1
    body=body.replace('Real existing native helper carried Bigelow','Real existing native helper carried '+EXTRA[key],1)
    result='local C='+Text.lua(bindings(raw,key))+'\n'+body
    Frozen.LuaRuntime().compile(result)
    assert not any(s in result for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return result


def metadata(raw,key='savage'):
    q=Previous.metadata(raw,key);q.update(controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),parent_factory_SHA256=PARENT,
        extra_later_edge_role=key in EXTRA,unchanged_Hogan_DiBiase_Honky_Bigelow_text=True,
        scope='Role-correct compiled Savage/Andre bindings with the same qualified static-floor x+8/native-carry control recipe; other four controls exact frozen parents; native pending')
    return q


def family():return SimpleNamespace(R=R,ROM=ROM,W=W,N=N,PIN=PIN,IDENTITIES=IDENTITIES,Frozen=Frozen,normalize=normalize,bindings=bindings,controller=controller,metadata=metadata)
