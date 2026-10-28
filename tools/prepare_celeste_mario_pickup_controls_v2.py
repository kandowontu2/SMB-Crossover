"""Exact linked six-slot Celeste pickup owner/score/IRQ controls; no native."""
from pathlib import Path
import argparse,hashlib,itertools,json,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import Arena,scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def call(q,name,x=0,sp=0xc0):
    s=q.b['syms'][name];g=q.b['segs'][s['seg']];pc=address(q.b,name);w=(pc-0x8000)//8192
    q.m.page(w,(int(g['ooffs'],0)-16)//8192)
    if w in (1,2):q.set('CurrentBank'if w==1 else'CurrentBankC',q.m.banks[w]|128)
    c=NesMPU(memory=q.m,pc=pc);c.sp=sp;c.x=x;c.p=0x71;c.stPushWord(0x5aff);low=c.sp;pcs=[]
    for _ in range(100000):
        if c.pc==0x5b00:
            assert c.sp==sp;return c,low,pcs
        bank=q.m.banks[(c.pc-0x8000)//8192]if c.pc>=0x8000 else -1
        pcs.append((c.pc,bank));c.step();low=min(low,c.sp)
    raise AssertionError(('timeout',name,hex(c.pc)))

def setup(b,slot,raw,tier,other=2):
    q=Arena(b,0);q.put(MarioVariant=4,NumberofLives=3,AreaType=1,AreaAddrsLOffset=5,
      WorldNumber=0,TimerControl=0,GamePauseStatus=0,DisableScreenFlag=1,NmiDisable=255,Sprite0HitDetectFlag=0)
    call(q,'CmInit');q.put(CmTier=tier,PlayerStatus=tier,CmPalette=7,ObjectOffset=slot,
      ScreenLeft_X_Pos=80,ScreenLeft_PageLoc=1)
    for i in range(6):
        for n,v in [('PowerUpType',other),('Enemy_Flag',1),('Enemy_ID',0x2e),('Enemy_State',0x80),
          ('Enemy_X_Position',100+7*i),('Enemy_PageLoc',1),('Enemy_Y_Position',140+i),
          ('FloateyNum_Control',0x44),('FloateyNum_Timer',0x23),('FloateyNum_X_Pos',0x66),('FloateyNum_Y_Pos',0x55)]:q.set(n,v,i)
    q.set('PowerUpType',raw,slot);q.m.writes=[]
    return q

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--old',type=Path,default=R/'build/celeste-mario-module/candidate.nes');p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    b=scoped_load(a.rom);old=scoped_load(a.old);rows=[];negatives=[];interrupts=[]
    for slot,raw,tier,other in itertools.product(range(6),[0,1],range(3),[2,3]):
        q=setup(b,slot,raw,tier,other);before=bytes(q.m[0x1c1:0x200]);otherbefore={n:[q.get(n,i)for i in range(6)]for n in ['Enemy_Flag','Enemy_ID','Enemy_State','FloateyNum_Control','FloateyNum_Timer','FloateyNum_X_Pos','FloateyNum_Y_Pos','PowerUpType']}
        c,low,pcs=call(q,'CmPickup',slot)
        assert c.p&1 and c.x==slot and q.get('CmTier')==min(tier+1,2)and q.get('PlayerStatus')==min(tier+1,2)
        assert q.get('CmPalette')==0 and q.get('ObjectOffset')==slot
        assert q.get('Enemy_Flag',slot)==q.get('Enemy_ID',slot)==q.get('Enemy_State',slot)==0
        assert [q.get(n,slot)for n in ['FloateyNum_Control','FloateyNum_Timer','FloateyNum_X_Pos','FloateyNum_Y_Pos']]==[6,48,20+7*slot,140+slot]
        for n,vals in otherbefore.items():
            for i in range(6):
                if i!=slot or n=='PowerUpType':assert q.get(n,i)==vals[i],(slot,n,i)
        assert bytes(q.m[0x1c1:0x200])==before
        assert sum(pc==address(b,'EraseEnemyObject')for pc,_ in pcs)==1
        assert sum(pc==address(b,'ScorePopupSetup')for pc,_ in pcs)==1
        sfx=address(b,'Square2SoundQueue');assert [(at,v)for at,v in q.m.writes if at==sfx]==[(sfx,address(b,'Sfx_PowerUpGrab'))]
        rows.append(dict(slot=slot,type=raw,other_actor_types=other,old_tier=tier,new_tier=q.get('CmTier'),score_tag=6,one_erase_one_score_one_SFX=True,minimum_SP=low))
    for slot,raw,tier in itertools.product(range(6),[2,3],range(3)):
        q=setup(b,slot,raw,tier,0);initial=bytes(q.m[:0x100])+bytes(q.m[0x200:0x800])+bytes(q.m[0x5c00:0x6000])
        c,_,pcs=call(q,'CmPickup',slot)
        assert not c.p&1 and c.x==slot
        assert initial==bytes(q.m[:0x100])+bytes(q.m[0x200:0x800])+bytes(q.m[0x5c00:0x6000])
        assert sum(pc==address(b,'EraseEnemyObject')for pc,_ in pcs)==0
        # Source-native fallback handles Star/1Up once, not a fabricated
        # tier grant. Popup1Up only awards its life later in its native owner.
        _,_,fallback=call(q,'MarioSourcePowerupCollision',slot)
        assert sum(pc==address(b,'EraseEnemyObject')for pc,_ in fallback)==1
        assert q.get('CmTier')==tier and q.get('PlayerStatus')==tier
        if raw==2:assert q.get('StarInvincibleTimer')==0x23 and q.get('FloateyNum_Control',slot)==6
        else:assert q.get('FloateyNum_Control',slot)==11
        negatives.append(dict(slot=slot,type=raw,tier=tier,leaf_declines_without_mutation=True,real_native_fallback_erase_once=True))
    counterexamples=[]
    for raw,other in [(1,2),(2,0)]:
        values=[]
        for bundle in [old,b]:
            q=setup(bundle,5,raw,0,other);c,_,_=call(q,'CmPickup',5)
            values.append(dict(carry=bool(c.p&1),tier=q.get('CmTier'),flag=q.get('Enemy_Flag',5),score=q.get('FloateyNum_Control',5)))
        assert values[0]!=values[1];counterexamples.append(dict(actual_slot=5,actual_type=raw,unrelated_slot0_type=other,old=values[0],fixed=values[1]))
    # Actual fixed nested native helper entry/returns, interrupted on both
    # sides of the real release/rare score call, preserve live caller state.
    for slot in [0,5]:
        q=setup(b,slot,1,1);_,_,pcs=call(q,'CmPickup',slot)
        seams=[next((pc,bank)for pc,bank in pcs if pc==address(b,n))for n in ['CmPickup','EraseEnemyObject','ScorePopupSetup']]
        for kind,lag,(target,bank_)in itertools.product(['IRQ','NMI'],[False,True],seams):
            q=setup(b,slot,1,1);q.put(NmiDisable=255 if lag else 0);fired=[False];lo=[255];oldstep=NesMPU.step
            smc=[address(b,n)+d for n,d in [('NextBank_SMC',1),('SafecallA_SMC',1),('FarcallJmpTarget_SMC',1),('FarcallJmpTarget_SMC',2),('SafereturnA_SMC',1)]]
            def step(c):
                bank=q.m.banks[(c.pc-0x8000)//8192]if c.pc>=0x8000 else -1
                if not fired[0]and c.pc==target and bank==bank_:
                    fired[0]=True
                    snapshot=lambda:(c.a,c.x,c.y,c.p&207,c.sp,c.pc,tuple(q.m.banks),q.get('CurrentBank'),q.get('CurrentBankC'),bytes(q.m[z]for z in smc),bytes(q.m[0x101+c.sp:0x200]))
                    before=snapshot()
                    if kind=='NMI':c.nmi()
                    else:c.stPushWord(c.pc);c.stPush(c.p&~c.BREAK|c.UNUSED);c.p|=c.INTERRUPT;c.pc=address(b,'IrqScrollSplit')
                    for _ in range(50000):
                        lo[0]=min(lo[0],c.sp);oldstep(c)
                        if c.pc==before[5]and c.sp==before[4]:break
                    else:raise AssertionError(('interrupt-timeout',kind,hex(c.pc)))
                    assert snapshot()==before
                oldstep(c)
            NesMPU.step=step
            try:c,low,_=call(q,'CmPickup',slot)
            finally:NesMPU.step=oldstep
            assert fired[0]and c.x==slot and q.get('CmTier')==2 and q.get('FloateyNum_Control',slot)==6
            interrupts.append(dict(slot=slot,kind=kind,lag=lag,PC=target,bank=bank_,minimum_SP=min(low,lo[0]),AXYP_SP_banks_5SMC_live_stack_exact=True))
    core=next(g for g in b['segs'].values()if g.get('name')=='"CELESTE_MARIO_CORE"')
    assert int(core['start'],0)==0xb000 and int(core['size'],0)<=4096
    proof=dict(passed=True,native_run=False,ROM_sha256=sha(a.rom),old_ROM_sha256=sha(a.old),accepted=rows,declined_and_fallback=negatives,old_counterexamples=counterexamples,interrupts=interrupts,core_bytes=int(core['size'],0),
      limits=['Leaf owner and genuine nested native helper CPU contracts only. Host admission/actor emergence remains ROOT integration work.','No natural collection, visible PPU, cadence or native gameplay claim.'],
      bindings=[dict(path=str(f),sha256=sha(f))for f in [Path(__file__),a.rom,a.rom.with_suffix('.dbg'),a.old,a.old.with_suffix('.dbg'),R/'src/celeste_mario_core.s']])
    a.output.write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=True,accepted=len(rows),declined=len(negatives),interrupts=len(interrupts),core_bytes=proof['core_bytes'])))
if __name__=='__main__':main()
