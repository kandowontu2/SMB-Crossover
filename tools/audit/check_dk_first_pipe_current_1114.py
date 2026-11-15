"""Classic DK genuine opening and passive first-pipe native jump trace."""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import current_dk_gameplay_input_1114 as Input
import check_shared_world_sprite_images_1114 as Source
import check_bub_current_budget_1113 as Frames

N,W=Input.N,Input.W


def run(raw):
    parent=Input.parent(raw);held=[];original=Source.cold
    def retain(image,key):
        m=original(image,key);held.append(m);return m
    with patch.object(Source,'Factory',Input),patch.object(Source,'cold',retain):
        opening=Source.run(raw,'donkey_kong')
    assert opening['passed']and len(held)==1
    m=held[0];counts=Counter();trace=[];writers=[];calls=[];ctx=dict(cpu=None,pc=-1,tick=-1)
    fields=('Player_Y_Position','Player_Y_HighPos','Player_State','Player_X_Speed','Player_XSpeedAbsolute',
        'Player_Y_Speed','Player_Y_MoveForce','Player_YMoveForceFractional','VerticalForce','VerticalForceDown',
        'A_B_Buttons','PreviousA_B_Buttons','SavedJoypadBits','GameEngineSubroutine','NumberofLives',
        'Player_CollisionBits','JumpspringAnimCtrl','PlayerChangeSizeFlag','DkAttack','DkAge')
    def state(mm):
        return dict(Main=ctx['tick'],x=N.get(mm,'Player_X_Position')+256*N.get(mm,'Player_PageLoc'),
            pad=mm.controller_pad,**{n:N.get(mm,n)for n in fields})
    watched={W.address(m.bundle,n):n for n in('Player_State','Player_Y_Position','Player_Y_Speed')}
    points={}
    for name in('DkMovement','CrossoverVanillaMovement','PlayerPhysicsSub','CrossoverJumpProfile','JumpSwimSub','PlayerBGCollision'):
        at=W.location(m.bundle,name);points[((at-16)//8192)|128,W.address(m.bundle,name)]=name
    old_bus=type(m)
    class Bus(old_bus):
        def __setitem__(self,at,value):
            c=ctx['cpu']
            if isinstance(at,int)and at in watched and c and state(self)['x']>=380:
                pc=ctx['pc'];bank=self.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else-1
                row=dict(field=watched[at],PC=pc,bank=bank,old=self[at],new=value&255,**state(self))
                counts[watched[at]]+=1
                if len(writers)<16:writers.append(row)
                else:
                    writers.append(row)
                    if len(writers)>32:del writers[16]
            return super().__setitem__(at,value)
    def observe(mm,c):
        ctx['cpu']=c;ctx['pc']=c.pc;bank=mm.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
        name=points.get((bank,c.pc))
        if name and state(mm)['x']>=380:
            counts[name]+=1
            if len(calls)<16:calls.append(dict(name=name,PC=c.pc,bank=bank,**state(mm)))
    phase='approach';age=0;takeoff=None;m.__class__=Bus
    try:
        for tick in range(250):
            ctx['tick']=tick;ctx['cpu']=None;s=state(m)
            assert s['NumberofLives']==2 and s['GameEngineSubroutine']!=11,s
            if phase=='approach'and s['x']>=396 and s['Player_State']==0:
                phase='jump';age=0;takeoff=s
            m.controller_pad=1|(128 if phase=='jump'and age<38 else 0)
            Frames.frame(m,observe=observe,whole_pass=True);ctx['cpu']=None;age+=1
            if takeoff:
                trace.append(state(m))
                if len(trace)>32:del trace[24]
    finally:m.__class__=old_bus
    result=dict(ROM_SHA256=sha256(raw).hexdigest(),typed_input=Input.KIND,
        normalized_model_parent_SHA256=sha256(parent).hexdigest(),opening_receipt=opening['source_receipt_SHA256'],
        opening_Main=opening['source_Main_passes'],takeoff=takeoff,bounded_jump_updates=trace,
        writer_counts=dict(counts),bounded_writers=writers,bounded_calls=calls,terminal=state(m),
        pipe_crossed=state(m)['x']>488,gameplay_seeds=0,ROM_changes=0,outputs=0,Mesen_run=False)
    result['receipt_SHA256']=sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return result


if __name__=='__main__':
    raw=Input.ROM.read_bytes()
    def forbid(*args,**kwargs):raise RuntimeError('Source first-pipe attempted files/Mesen')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Source.Native,'run',forbid):
        q=run(raw)
    print('DK_FIRST_PIPE '+json.dumps(q,separators=(',',':')),flush=True)
