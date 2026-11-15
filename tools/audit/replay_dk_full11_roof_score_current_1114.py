"""Strict571 DK controller: frozenb68 binding plus measured near-floor walk."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path

import compose_native_floatey_score_1114 as Score
import replay_dk_full11_roof_takeoff_current_1114 as Previous

R,ROM,W,N=Previous.R,Previous.ROM,Previous.W,Previous.N
PIN=Score.CANDIDATE
Frozen,IDENTITIES=Previous.Frozen,Previous.IDENTITIES
OLD_LUA_SHA='b68be24df93f6f56668cccf00beeb79e8d732a7536e2daf2a957837d99a99176'
SOURCE_SHA='0c61cec89cf5f6b20042a0b2be98e3dc5ff01b9ad7bd7985442efced510f996c'
SCORE_SHA='874ccac3b0771241c1cc84aea9ee4bde02d00bcfeb843a2d5e836a8a48a176a7'


@lru_cache(maxsize=1)
def parent(raw,*,kind='native-score-571-classic-dk'):
    assert kind=='native-score-571-classic-dk'and isinstance(raw,bytes)and sha256(raw).hexdigest()==PIN
    assert sha256(Path(Score.__file__).read_bytes()).hexdigest()==SCORE_SHA
    old=Score.inverse(raw);assert sha256(old).hexdigest()==Previous.PIN
    assert Score.proposal(old)[0]==raw
    return old


@lru_cache(maxsize=1)
def normalize(raw):return Previous.normalize(parent(raw))


@lru_cache(maxsize=1)
def bindings(raw,key='donkey_kong'):
    old=parent(raw);q=deepcopy(Previous.bindings(old,key));q['sha']=PIN
    for h in q['hooks'].values():
        at=16+h['offset'];assert raw[at:at+len(h['bytes'])]==bytes(h['bytes'])
        if'bank'in h:
            at=16+h['bank']*8192;digest=sha256(raw[at:at+8192]).hexdigest()
            if h['bank']!=126:assert digest==h['bank_SHA256']
            h['bank_SHA256']=digest
    return q


@lru_cache(maxsize=1)
def rebound_b68_controller(raw,key='donkey_kong'):
    assert sha256(Path(Previous.__file__).read_bytes()).hexdigest()==SOURCE_SHA
    old=parent(raw);text=Previous.controller(old,key);assert sha256(text.encode()).hexdigest()==OLD_LUA_SHA
    prefix='local C='+Frozen.lua(Previous.bindings(old,key))+'\n';assert text.startswith(prefix)
    rebound='local C='+Frozen.lua(bindings(raw,key))+'\n'+text[len(prefix):]
    assert rebound.split('\n',1)[1]==text.split('\n',1)[1]
    return rebound


@lru_cache(maxsize=1)
def controller(raw,key='donkey_kong'):
    text=rebound_b68_controller(raw,key)
    once=Previous.Previous.Previous.Previous.Previous.Base.once
    text=once(text,'local dkRoofBridgeDone=false','local dkRoofBridgeDone=false\nlocal dkRoofWalkTrace={}')
    old="""   assert(c.yHigh==1 and c.y<=112 and c.grounded,'Retain actual first roof support until its qualified edge')
   if c.x<1506 then
    wanted={right=true,b=false,a=false}"""
    new="""   local tile=c.block(1504,144)
   assert(c.yHigh==1 and c.y>=112 and c.y<=116 and(c.grounded or c.state==2)
    and c.x-13<=1519 and c.x+29>=1504 and tile==0x58,'True first roof overlap inside native five-pixel landing band')
   dkRoofWalkTrace[#dkRoofWalkTrace+1]={Main=updates,frame=frame,poll=polls,x=c.x,y=c.y,state=c.state,
    grounded=c.grounded,tile=tile,SavedJoypadBits=r('SavedJoypadBits'),A_B_Buttons=r('A_B_Buttons'),
    PreviousA_B_Buttons=r('PreviousA_B_Buttons'),DkPrevious=r('DkPrevious')}
   if #dkRoofWalkTrace>16 then table.remove(dkRoofWalkTrace,9)end
   if c.x<1506 or not c.grounded then
    assert(c.x<=1510,'Actual native ground regained before measured roof takeoff ends')
    wanted={right=true,b=false,a=false}"""
    text=once(text,old,new)
    text=once(text,'qualified_roof_edge_requested=dkRoofBridgeDone,',
        'roof_walk_trace=dkRoofWalkTrace,qualified_roof_edge_requested=dkRoofBridgeDone,')
    Frozen.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return text


def metadata(raw,key='donkey_kong'):
    q=Previous.metadata(parent(raw),key)
    q.update(ROM_SHA256=PIN,controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        typed_input='native-score-571-classic-dk',model_parent_SHA256=Previous.PIN,
        frozen_b68_rebound_SHA256=sha256(rebound_b68_controller(raw,key).encode()).hexdigest(),
        frozen_b68_body_unchanged_before_explicit_guard_correction=True,
        source_walk_correction='allow state2 only in112..116 landing band with real1504/Y144 tile58 and actual full-body overlap; require actual native ground for1506..1510 takeoff',
        maximum_roof_walk_trace_rows=16,score10_and_all_prior_changes_preserved=True)
    return q
