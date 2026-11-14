"""Separate421 successor: completed-Main input decisions and second-gap trace."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import json

import replay_smb3_alts_full11_1114 as Frozen

PIN,ROM,W,N=Frozen.PIN,Frozen.ROM,Frozen.W,Frozen.N
IDENTITIES=Frozen.IDENTITIES
normalize=Frozen.normalize
FROZEN_SOURCE='ebf11f132514c1e49e8c7945825ae53131d6edaf5be08e0229ac1b5135f41a25'
TRACE=Frozen.Frozen.R/'tools/playthroughs/smb3_mainclock_trace_1114.lua'
TRACE_SHA='b94944c9a1579619d20cc5196808ce97dadf1f27a0c4bab30735eb177fd37b18'
LUA_SHA={('toad3',True):'52d028149999b274f3640dc9e601f7ea02a7e04a90b0abdc5b8cccb50ad5d87e',
    ('toad3',False):'21f03ec3f4f2a9d69b5ac6ac53a468a4d0252d533e2e533108cc45aad7421e5f',
    ('peach3',False):'30e533cd1d43814653dc87fa712aa92fcd3b58caafb2362e6e3d5f662a91130d'}


@lru_cache(maxsize=4)
def bindings(raw,key,damage_probe=False):
    assert key in IDENTITIES and type(damage_probe)is bool and sha256(raw).hexdigest()==PIN
    assert sha256(Path(Frozen.__file__).read_bytes()).hexdigest()==FROZEN_SOURCE
    q=deepcopy(Frozen.bindings(raw,key));b=dict(W.Symbols.bundle(),raw=raw)
    q['damage_probe']=damage_probe
    q['smc_return_pc']=W.address(b,'FarcallJmpTarget_SMC')+3
    assert q['smc_return_pc']==0x016e
    for n in('SavedJoypadBits','M3Growth','ObjectOffset','InjuryTimer','GuestHurtKind'):
        q['ram'][n]=W.address(b,n)
    n='M3Injury';at=W.location(b,n)
    q['hooks'][n]=dict(pc=W.address(b,n),offset=at-16,bytes=list(raw[at:at+8]))
    return q


def once(text,before,after):return Frozen.once(text,before,after)


@lru_cache(maxsize=4)
def controller(raw,key,damage_probe=False):
    q=bindings(raw,key,damage_probe);old=Frozen.controller(raw,key)
    assert sha256(old.encode()).hexdigest()==Frozen.LUA_SHA[key]
    if TRACE_SHA is not None:assert sha256(TRACE.read_bytes()).hexdigest()==TRACE_SHA
    _,body=old.split('\n',1);text='local C='+Frozen.Frozen.lua(q)+'\n'+body
    if key=='toad3'and not damage_probe:
        text=once(text,"local form=c.r('M3Form');if form~=0 and form~=4 then return base(c)end", "local form=c.r('M3Form') -- Mount the existing cap for every native form.")
    text=once(text,'local function finish(reason)',
        'local clockInput,clockDecide={},nil\nlocal moveToken,moveReturns,moveEntries=nil,0,0\nlocal gapFirst,gapTail,gapTakeoffs,gapEvents={}, {}, {},0\nlocal grew,damaged,injury,smallFar=false,false,nil,nil\nlocal function finish(reason)')
    text=once(text,'full_nonshortcut1_1=not not(flag and castle and entrance),game_state_writes=false',
        'navigation_clock="completed Main snapshots",movement_entries=moveEntries,movement_returns=moveReturns,gap_trace_first=gapFirst,gap_trace_tail=gapTail,gap_takeoffs=gapTakeoffs,gap_trace_events=gapEvents,post_damage=damaged,native_injury=injury,small_far_bank=smallFar,damage_probe=C.damage_probe,full_nonshortcut1_1=not not(flag and castle and entrance),game_state_writes=false')
    point=' and m3Calls>0 and m3Steps>0 and m3Next>=25'
    text=once(text,point,point+' and(not C.damage_probe or(damaged and injury and smallFar))')
    text=once(text,'frame=frame,poll=polls,char=17','frame=updates,poll=updates,char=17')
    text=once(text,'lastA=lastA,grounded=',"lastA=(r('M3Previous')&128)~=0,grounded=")
    marker='emu.addEventCallback(guard(function()\n polls=polls+1'
    text=once(text,marker,TRACE.read_text()+'\n'+marker)
    text=once(text,"if menuDone then b=active()and r('LevelNumber')==0 and controls(context())or{}end",'if menuDone then b=clockInput end')
    point=' pendingReturn=nil;updates=updates+1\n m3Owner()'
    text=once(text,point,point+'\n if clockDecide then clockDecide()end')
    Frozen.Frozen.LuaRuntime().compile(text)
    assert not any(v in text for v in('emu.write','emu.setState','io.open','saveState','loadState','takeScreenshot'))
    assert sha256(text.encode()).hexdigest()==LUA_SHA[key,damage_probe]
    return text


def metadata(raw,key,damage_probe=False):
    q=Frozen.metadata(raw,key);text=controller(raw,key,damage_probe)
    q.update(controller_SHA256=sha256(text.encode()).hexdigest(),frozen_parent_Lua_SHA256=Frozen.LUA_SHA[key],
        frozen_parent_source_SHA256=FROZEN_SOURCE,navigation_clock='completed Main state only; physical polls apply cached buttons',
        second_gap_trace_cap=dict(first=32,last=64,takeoffs=8),damage_probe=damage_probe,
        damage_probe_uses_real_actor_contact_and_never_seeds_form=True,
        trace_source_SHA256=sha256(TRACE.read_bytes()).hexdigest())
    return q


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--identity',choices=IDENTITIES,required=True)
    p.add_argument('--damage-probe',action='store_true');args=p.parse_args()
    print(json.dumps(metadata(ROM.read_bytes(),args.identity,args.damage_probe),separators=(',',':')),flush=True)
