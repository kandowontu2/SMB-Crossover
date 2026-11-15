"""Bigelow-only use of the frozen later-edge/native-carry input recipe."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
import replay_wwf_honky_star_gap_7a80_1115 as Previous
import replay_smb1_alts_full11_1114 as Text

R,ROM,W,N,PIN,IDENTITIES=Previous.R,Previous.ROM,Previous.W,Previous.N,Previous.PIN,Previous.IDENTITIES
Frozen,normalize=Previous.Frozen,Previous.normalize
PARENT='2cfb4f215c16b53e466c23c2f0339f9d9d0d5e85d964316ede5de4a48525e8c8'


@lru_cache(maxsize=6)
def bindings(raw,key='bigelow'):
    if key!='bigelow':return Previous.bindings(raw,key)
    q=deepcopy(Previous.bindings(raw,key));qualified=Previous.bindings(raw,'honky')
    q['ram']['PlatformCollisionFlag']=qualified['ram']['PlatformCollisionFlag']
    q['hooks']['PositionPlayerOnHPlat']=deepcopy(qualified['hooks']['PositionPlayerOnHPlat'])
    return q


@lru_cache(maxsize=6)
def controller(raw,key='bigelow'):
    assert sha256(Path(Previous.__file__).read_bytes()).hexdigest()==PARENT
    old=Previous.controller(raw,key)
    if key!='bigelow':return old
    # The original per-role policies differ only in their strict menu/cookie
    # config. Prove that before reusing the measured later-edge body.
    generic_honky=Previous.Previous.controller(raw,'honky')
    assert old.split('\n',1)[1]==generic_honky.split('\n',1)[1]
    qualified=Previous.controller(raw,'honky');body=qualified.split('\n',1)[1]
    assert body.count('Real existing native helper carried Honky')==1
    body=body.replace('Real existing native helper carried Honky','Real existing native helper carried Bigelow',1)
    result='local C='+Text.lua(bindings(raw,key))+'\n'+body
    Frozen.LuaRuntime().compile(result)
    assert not any(s in result for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return result


def metadata(raw,key='bigelow'):
    q=Previous.metadata(raw,key);q.update(controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),parent_factory_SHA256=PARENT,
        bigelow_only_later_edge=key=='bigelow',unchanged_other_role_control_text=True,
        scope='Bigelow-specific same qualified Honky late-floor x+8/helper-carry recipe, actual role2 menu/cookie bindings; unchanged other roles, native pending')
    return q


def family():return SimpleNamespace(R=R,ROM=ROM,W=W,N=N,PIN=PIN,IDENTITIES=IDENTITIES,Frozen=Frozen,normalize=normalize,bindings=bindings,controller=controller,metadata=metadata)
