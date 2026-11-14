"""Source-only exact421 compiled CF menu and normal-input full routes."""
import argparse
from hashlib import sha256
import json
from unittest.mock import patch

import replay_contra_force_full11_1114 as Factory
import check_smb1_alts_full11_1114 as Harness

W,N=Factory.W,Factory.N


def cold(raw,key):
    config=Factory.bindings(raw,key);b=dict(W.Symbols.bundle(),raw=raw)
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
    for pad in(4,4,4,1,1,1,1,1,1):W.UI.key(m,pad)
    for _ in range(config['cycle']):W.UI.key(m,32)
    assert W.UI.menu_name(m)[0]==config['name']
    assert N.get(m,'SelectedCharacter')==31 and(N.get(m,'FmGroups')>>3)&3==config['variant']
    start=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    N.invoke(m,'PauseRoutine',a=0)
    for tick in range(700):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):
            assert N.get(m,'NumberofLives')==2
            assert N.get(m,'CheatInvincible')==N.get(m,'CheatStartLevel')==0
            return m
        m.controller_pad=0;Harness.Frames.frame(m,cold=True)
    raise AssertionError('Native CF constructor bound')


def policy_components(raw,key):
    q=Factory.bindings(raw,key);runtime=Factory.Frozen.LuaRuntime(unpack_returned_tuples=True)
    runtime.globals().C=runtime.table_from(dict(variant=q['variant']))
    policy=Factory.POLICY.read_text();make=runtime.eval('function(s)return assert(load(s))()end')
    def context(**kw):
        c=dict(update=0,x=100,y=176,world=0,level=0,areaType=1,grounded=True,heldA=False)
        c.update(kw);ctx=runtime.table_from(c)
        ctx.block=lambda x,y:0x54 if y>=208 else 0
        ctx.enemy=lambda:None
        return ctx
    choose=make(policy);c=context();b,phase=choose(c)
    assert b.right and not b.a and phase=='travel'
    choose=make(policy);c=context(x=1088);c.block=lambda x,y:0 if 1104<=x<1136 else(0x54 if y>=208 else 0)
    b,phase=choose(c);assert b.a and b.right and phase=='travel'
    choose=make(policy);c=context();c.enemy=lambda:runtime.table_from(dict(slot=0,id=6,dx=60,y=176))
    shots=[]
    for age in range(12):
        c.update=age;b,phase=choose(c);assert b.down and not b.right and phase=='crouch-fire';shots.append(bool(b.b))
    settle=0 if q['variant']==2 else 4
    assert shots[settle]and shots[settle+1]and not any(shots[:settle])
    choose=make(policy);answers=choose(context(areaType=2));assert len(answers)==3 and answers[2]
    return dict(passed=True,original_class=q['variant'],travel_gap_fresh_A_and_crouch_B=True,
        genuine_Iron_startup_exception=q['variant']==2,unexpected_shortcut_rejected=True,
        decisions_only_not_physics_evidence=True)


def metadata(raw,key):
    with patch.object(Harness,'Factory',Factory):q=Harness.strict_metadata(raw,key)
    q['local_policy_components']=policy_components(raw,key)
    return q


def run(raw,key,limit=8500):
    metadata(raw,key)
    with patch.object(Harness,'Factory',Factory),patch.object(Harness,'cold',cold):
        return Harness.run(raw,key,limit)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--identity',choices=Factory.IDENTITIES,required=True)
    p.add_argument('--metadata',action='store_true');p.add_argument('--limit',type=int,default=8500);args=p.parse_args()
    raw=Factory.ROM.read_bytes();q=metadata(raw,args.identity)if args.metadata else run(raw,args.identity,args.limit)
    print(json.dumps(q,separators=(',',':')),flush=True)
    if not args.metadata:assert q['passed'],'Separate CF full-route source gate not passed'
