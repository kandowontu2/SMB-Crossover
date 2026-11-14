"""Natural hidden1UP with original kind3 admission and source ceiling stop."""
import argparse
from hashlib import sha256
import json
from unittest.mock import patch

import compose_smb2_hidden_response_1114 as C
import replay_smb2_hidden_oneup_1113 as Frozen


def controller(raw,variant=0):
    parent=C.inverse(raw);public=C.Cache.public_image(parent)
    text=Frozen.controller(public,variant)
    once=Frozen.Terrain.Frozen.Flag.Root.once
    text=once(text,Frozen.PIN,C.CANDIDATE)
    # Original SMB1 admits emerging kind3 from state6; no artificial high-bit
    # maturity fence is introduced into the game or observer.
    text=once(text,"a.state>=128 and a.flag==1 and a.id==46,'Real mature natural1UP collector'",
        "a.state>=6 and a.flag==1 and a.id==46,'Original native kind3 collector admission'")
    text=text.replace('head/birth/mature collector/','head/birth/original collector/')
    b=dict(C.W.Symbols.bundle(),raw=raw)
    names=('S2AY','S2Collision','S2HeadY','Player_Y_Speed','S2N8F7A')
    text=once(text,'local F={','local F={'+','.join(n+'='+str(C.W.address(b,n))for n in names)+',')
    name='S2N8F7A';at=C.W.location(b,name)
    text=once(text,'local oneupHooks={','local oneupHooks={'+name+'={offset='+str(at-16)+',hex="'+raw[at:at+12].hex()+'"},')
    point='oneup.head={s=s,source=oneupSource(),tile=c[\'cpu.a\'],launch=oneup.last_jump}'
    text=once(text,point,point+'''
 assert(oneup.ceiling,'Original source ceiling observer precedes native head')
 assert(r('S2VY')==0 and r('S2AY')==0 and r('Player_Y_Speed')==0,'Original source/native ceiling velocity zero')''')
    marker='-- Observe every actual GameLoop return, including the native catch-up caller.'
    observer='''emu.addMemoryCallback(guard(function()
 if not game or not oneupHook('S2N8F7A')or r('S2HeadY')~=128 then return end
 local s=state();if s.x<1000 or s.x>1048 or r('S2VY')<128 then return end
 assert(not oneup.ceiling,'Single real hidden source ceiling stop')
 oneup.ceiling={s=s,source=oneupSource(),collision=r('S2Collision'),headY=r('S2HeadY')}
 assert(oneup.ceiling.collision~=0,'Actual source ceiling collision bits')
end),emu.callbackType.exec,F.S2N8F7A)
'''
    text=once(text,marker,observer+'\n'+marker)
    point=" assert(s.world==0 and s.level==0,'Unmodified authored1-1')"
    text=once(text,point,point+'''
 if oneup.head and not oneup.pickup and s.x>=1000 and s.x<=1048 then
  assert(s.y>=oneup.head.s.y,'No continued upward passage through revealed hidden block')
 end''')
    Frozen.Terrain.Frozen.Flag.Root.Base.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','loadState','saveState','takeScreenshot'))
    return text


def source_run(raw,variant=0,limit=2800):
    assert sha256(raw).hexdigest()==C.CANDIDATE
    with patch.object(Frozen.OldReplay,'controller',lambda image,v,mode:controller(image,v)),patch.object(Frozen.Runner,'PIN',C.CANDIDATE):
        q=Frozen.Runner.run_controller(raw,variant,'natural-hidden-response',limit)
    receipt=q.pop('receipt')or{}
    q.update(reason=receipt.get('reason'),all_returned_Main=receipt.get('all_returned_Main'),
        oneup=receipt.get('oneup'),physical_native_claim=False)
    return q


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--variant',choices=tuple(map(str,range(8)))+('all',),default='0')
    p.add_argument('--cpu',action='store_true');p.add_argument('--limit',type=int,default=2800);args=p.parse_args()
    raw=C.proposal(C.Cache.parent_image())[0]
    for variant in(range(8)if args.variant=='all'else(int(args.variant),)):
        q=source_run(raw,variant,args.limit)if args.cpu else dict(ROM_SHA256=C.CANDIDATE,variant=variant,
            controller_SHA256=sha256(controller(raw,variant).encode()).hexdigest(),outputs=0,Mesen_run=False)
        print(json.dumps(q,separators=(',',':')),flush=True)
        if args.cpu:assert q['passed'],'Natural hidden1UP response scope remains unqualified'
