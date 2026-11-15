"""Classic DK genuine opening and passive first-pipe native jump trace."""
from collections import Counter
from hashlib import sha256
import argparse
import json
from pathlib import Path
from unittest.mock import patch

import current_dk_gameplay_input_1114 as Input
import check_shared_world_sprite_images_1114 as Source
import check_bub_current_budget_1113 as Frames

N,W=Input.N,Input.W


def run(raw,*,head_cause=False,retry=False):
    parent=Input.parent(raw);held=[];original=Source.cold
    def retain(image,key):
        m=original(image,key);held.append(m);return m
    with patch.object(Source,'Factory',Input),patch.object(Source,'cold',retain):
        opening=Source.run(raw,'donkey_kong')
    assert opening['passed']and len(held)==1
    m=held[0];counts=Counter();trace=[];writers=[];calls=[]
    ctx=dict(cpu=None,pc=-1,tick=-1,head_pending=None,last_head=None,first_abort=None)
    fields=('Player_Y_Position','Player_Y_HighPos','Player_State','Player_X_Speed','Player_XSpeedAbsolute',
        'Player_Y_Speed','Player_Y_MoveForce','Player_YMoveForceFractional','VerticalForce','VerticalForceDown',
        'A_B_Buttons','PreviousA_B_Buttons','SavedJoypadBits','GameEngineSubroutine','NumberofLives',
        'Player_CollisionBits','JumpspringAnimCtrl','PlayerChangeSizeFlag','DkAttack','DkAge')
    def state(mm):
        return dict(Main=ctx['tick'],x=N.get(mm,'Player_X_Position')+256*N.get(mm,'Player_PageLoc'),
            pad=mm.controller_pad,**{n:N.get(mm,n)for n in fields})
    watched={W.address(m.bundle,n):n for n in('Player_State','Player_Y_Position','Player_Y_Speed')}
    head_at=W.location(m.bundle,'BillBGHeadConsumer')
    head_point=((head_at-16)//8192)|128,W.address(m.bundle,'BillBGHeadConsumer')
    def cells(mm):
        table=W.location(mm.bundle,'MTileAttribute');block=W.address(mm.bundle,'Block_Buffer_1')
        rows=[]
        for x in(384,400,416,432,448):
            for y in(128,144,160,176):
                at=block+(x//256%2)*208+((y-32)//16)*16+(x%256//16)
                tile=mm[at];rows.append(dict(x=x,y=y,tile=tile,attribute=raw[table+tile]))
        return rows
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
                if head_cause and watched[at]=='Player_Y_Speed'and self[at]>=128 and value&255<128 and ctx['first_abort']is None:
                    ctx['first_abort']=dict(row,last_actual_head_return=ctx['last_head'],
                        scratch={n:N.get(self,n)for n in('R2','R3','R4','R5','R6','R7','Local_eb','PlayerSize','CrouchingFlag')},
                        authored_cells=cells(self))
                    print('DK_FIRST_UPWARD_ABORT '+json.dumps(ctx['first_abort'],separators=(',',':')),flush=True)
                if len(writers)<16:writers.append(row)
                else:
                    writers.append(row)
                    if len(writers)>32:del writers[16]
            return super().__setitem__(at,value)
    def observe(mm,c):
        ctx['cpu']=c;ctx['pc']=c.pc;bank=mm.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
        if head_cause:
            pending=ctx['head_pending']
            if pending and(c.pc,c.sp,bank)==pending:
                ctx['last_head']=dict(tile=c.a,A=c.a,X=c.x,Y=c.y,P=c.p,PC=c.pc,bank=bank,
                    scratch={n:N.get(mm,n)for n in('R2','R3','R4','R5','R6','R7','Local_eb')},**state(mm))
                ctx['head_pending']=None
            if(bank,c.pc)==head_point:
                ret=(mm[0x100+((c.sp+1)&255)]+256*mm[0x100+((c.sp+2)&255)]+1)&65535
                tag=mm.rawtags[(ret-0x8000)//8192]if ret>=0x8000 else-1
                assert ctx['head_pending']is None
                ctx['head_pending']=(ret,(c.sp+2)&255,tag)
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
    negative_terminal=state(m);successor=None
    if retry:
        assert 417<=negative_terminal['x']<=418 and negative_terminal['Player_State']==0
        retrace=[];reack=None
        for j in range(120):
            ctx['tick']=250+j;ctx['cpu']=None
            m.controller_pad=1|(128 if 2<=j<40 else 0)
            Frames.frame(m,observe=observe,whole_pass=True);ctx['cpu']=None;s=state(m)
            assert s['NumberofLives']==2 and s['GameEngineSubroutine']==8,s
            if j==2:
                assert s['A_B_Buttons']==s['PreviousA_B_Buttons']==128 and s['Player_State']==1 and s['Player_Y_Speed']>=128,s
                reack=s
            if len(retrace)<12:retrace.append(s)
            if s['x']>=512 and s['Player_State']==0:break
        successor=dict(ordinary_two_update_A_release_then_RightA38=True,takeoff_ack=reack,
            first12_updates=retrace,updates=j+1,terminal=s,
            full_body_past_first_pipe_and_grounded=s['x']-13>479 and s['Player_State']==0)
        assert successor['full_body_past_first_pipe_and_grounded'],successor
    result=dict(ROM_SHA256=sha256(raw).hexdigest(),typed_input=Input.KIND,
        normalized_model_parent_SHA256=sha256(parent).hexdigest(),opening_receipt=opening['source_receipt_SHA256'],
        opening_Main=opening['source_Main_passes'],takeoff=takeoff,bounded_jump_updates=trace,
        writer_counts=dict(counts),bounded_writers=writers,bounded_calls=calls,terminal=negative_terminal,
        pipe_crossed=negative_terminal['x']>488,ordinary_rejump_successor=successor,
        gameplay_seeds=0,ROM_changes=0,outputs=0,Mesen_run=False)
    if head_cause:
        result={k:v for k,v in result.items()if k not in('bounded_writers','bounded_calls','bounded_jump_updates')}
        result.update(first_upward_abort=ctx['first_abort'],
            first8_jump_updates=trace[:8],same_retained_controls=True)
    result['receipt_SHA256']=sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--head-cause',action='store_true');p.add_argument('--retry',action='store_true');a=p.parse_args()
    raw=Input.ROM.read_bytes()
    def forbid(*args,**kwargs):raise RuntimeError('Source first-pipe attempted files/Mesen')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Source.Native,'run',forbid):
        q=run(raw,head_cause=a.head_cause,retry=a.retry)
    print('DK_FIRST_PIPE '+json.dumps(q,separators=(',',':')),flush=True)
