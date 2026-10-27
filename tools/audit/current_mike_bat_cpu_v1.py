"""Finite current bat clocks, all13 source campaigns, full callers and actual IRQ."""
from pathlib import Path
import hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];B=R/'build';sys.path.insert(0,str(R/'tools/audit'))
import current_mike_bat_candidate_v1 as build
import current_mike_earned_remainder_prepare_v2 as remainder
from link_pit_rygar_sophia_audit_cpu import Arena,scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
FLAGS=[0x20|(i&15)|((i&16)<<2)|((i&32)<<2)for i in range(64)]
sha=build.sha;put=build.put

def invoke(q,name,p=0x30,x=0,y=0,a=0,ref=None,irq=None):
    b=q.b;pc=address(b,name);q.m.page((pc-0x8000)//8192,(location(b,name)-16)//8192)
    if 0xa000<=pc<0xe000:q.set('CurrentBank'if pc<0xc000 else'CurrentBankC',q.m.banks[(pc-0x8000)//8192]|128)
    c=NesMPU(memory=q.m,pc=pc);c.a,c.x,c.y,c.p,c.sp=a,x,y,p,253;c.stPushWord(0x5aff)
    q.m.writes=[];trace=[]
    for idx in range(100000):
        if c.pc==0x5b00:break
        bank=q.m.banks[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
        if ref:ref(q,c,bank)
        if idx==irq:
            saved=(c.pc,c.a,c.x,c.y,c.p&207,c.sp,tuple(q.m.banks),bytes(q.m[:256]+q.m[512:8192]+q.m[0x5c00:0x8000]))
            assert not c.p&4;start=len(q.m.writes);c.irq()
            for _ in range(500):
                if c.pc==saved[0]and c.sp==saved[5]:break
                c.step()
            else:raise AssertionError('Real IRQ return timeout')
            restored=(c.pc,c.a,c.x,c.y,c.p&207,c.sp,tuple(q.m.banks),bytes(q.m[:256]+q.m[512:8192]+q.m[0x5c00:0x8000]))
            assert saved==restored,('Real IRQ damaged context',idx,hex(saved[0]))
            assert all(at in [0x2005,0x2006,0x5128,0x5130]or 256<=at<512 for at,v in q.m.writes[start:])
            del q.m.writes[start:]
        trace.append((idx,c.pc,bank));c.step()
    else:raise AssertionError(('Timeout',name,hex(c.pc)))
    assert c.sp==253
    return c,trace

def state(q,c):
    # Only dead lower stack cells differ after new real helper calls; preserve
    # both caller-live cells1FE/1FF and every application byte/SMC/bank/register.
    # Bits4/5 are the emulator's synthetic B/U image, not CPU status latches;
    # PHP/PLP sets B in that model. All six real hardware flags remain exact.
    return(c.a,c.x,c.y,c.p&207,c.sp,bytes(q.m[:256]+q.m[510:0x8000]),tuple(q.m.banks))

def seed(b,kind=0,age=0,face=1,offset=0,rotation=0):
    q=Arena(b,16);q.put(TimerControl=0,MmDeathFlag=0,PlayerFacingDir=face,Player_X_Position=112,Player_PageLoc=0,Player_Y_Position=160,
        ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,GameEngineSubroutine=8,JnUiDirty=0,CurrentOAMOffset=offset,GuestOamRotationActive=int(rotation!=0),RgOamRotation=rotation,
        JnAttack=0,JnPressed=0,JnWeapon=kind,JnDrawFirst=0,JnSlot=5)
    q.set('JnShotKind',kind,5);q.set('JnShotAge',age,5);q.set('JnShotVX',0 if kind in [1,4,7]else 253 if face==2 else 3,5)
    q.set('JnShotX',98 if face==2 else 134,5);q.set('JnShotPage',0,5);q.set('JnShotY',176,5)
    for i in range(256):q.m[512+i]=(73*i+29)&255
    return q

def main():
    output=B/'mike_bat_controls.json';result=dict(passed=False,native_run=False)
    try:
        proof=json.loads((B/'mike_bat_build.json').read_text());old,new=scoped_load(build.BASE),scoped_load(B/'mike_bat.nes')
        assert sha(build.BASE)==build.EXPECTED and sha(B/'mike_bat.nes')==proof['candidate_sha256']
        frames=proof['original_frames'];draws=[];weapons=[];irqrows=[]
        # Validate all four current CHR pairs against the authenticated original
        # native pattern bank. No palette/visible-line equivalence is inferred.
        original=build.ORIGINAL.read_bytes();asset=(R/'chr/characters/mike-jones.chr').read_bytes();pairs=[]
        for native,packed in [(48,20),(50,22),(52,24),(54,26)]:
            src=original[16+262144+251*1024+native*16:16+262144+251*1024+native*16+32]
            dst=asset[2048+packed*16:2048+packed*16+32];assert src==dst
            assert new['raw'][16+1048576+710*1024+packed*16:16+1048576+710*1024+packed*16+32]==dst
            pairs.append(dict(native_pair=native,packed_pair=packed,sha256=hashlib.sha256(dst).hexdigest()))
        def batptr(q):
            i=q.get('JnShotAge',5)-1+(30 if q.get('PlayerFacingDir')==2 else 0)
            assert 0<=i<60
            return new['raw'][location(new,'JnBatRecordLo')+i]+256*new['raw'][location(new,'JnBatRecordHi')+i]
        def ref(q,c,bank):
            if bank==98 and c.pc==address(old,'JnDraw::Next')-3 and q.get('JnShotKind',c.x)==4 and 1<=q.get('JnShotAge',c.x)<=30:
                ptr=batptr(q);off=16+97*8192+ptr-0xc000
                list.__setitem__(q.m,slice(ptr,ptr+5),new['raw'][off:off+5])
                q.set('R0',ptr&255);q.set('R1',ptr>>8)
        for kind,face,age,offset,rotation in itertools.product(range(1,14),[1,2],[1,4,7,11],[0,248,252],[0,240]):
            x=seed(old,kind,age,face,offset,rotation);y=seed(new,kind,age,face,offset,rotation)
            c,_=invoke(x,'JnDraw',ref=ref if kind==4 else None);d,t=invoke(y,'JnDraw')
            assert state(x,c)==state(y,d),('Full draw state',kind,face,age,offset,rotation,[(hex(i),x.m[i],y.m[i])for i in range(0x8000)if x.m[i]!=y.m[i]and not256<=i<510][:12])
            assert [(a,v)for a,v in x.m.writes if 512<=a<768]==[(a,v)for a,v in y.m.writes if 512<=a<768]
            draws.append(dict(kind=kind,delta=d.processorCycles-c.processorCycles))
        for face,age,flags in itertools.product([1,2],range(1,31),FLAGS):
            x=seed(old,4,age,face);y=seed(new,4,age,face)
            c,_=invoke(x,'JnDraw',p=flags,ref=ref);d,t=invoke(y,'JnDraw',p=flags)
            assert state(x,c)==state(y,d),('Bat full draw flags/timeline',face,age,flags)
            ptr=batptr(y);off=16+97*8192+ptr-0xc000;row=frames['3'if face==2 else'2'][age-1]
            assert new['raw'][off:off+5]==bytes([4,row['tile']-28,row['attribute'],0,0])
        # Other12 timings and complete weapon outcomes are exact; new direct
        # helpers add cycles, never source events or clocks for those families.
        for kind,age,flags in itertools.product([k for k in range(1,14)if k!=4],[0,1,5,11,18,29],FLAGS):
            x=seed(old,kind,age);y=seed(new,kind,age)
            x.put(JnAttack=5,JnWeapon=kind);y.put(JnAttack=5,JnWeapon=kind)
            x.set('JnAmmo',10,max(0,kind-4));y.set('JnAmmo',10,max(0,kind-4))
            c,_=invoke(x,'JnWeapons',p=flags);d,_=invoke(y,'JnWeapons',p=flags)
            assert state(x,c)==state(y,d),('Other weapon full caller state',kind,age,flags,(c.a,c.p),(d.a,d.p))
            weapons.append(dict(kind=kind,delta=d.processorCycles-c.processorCycles))
        for kind,flags in itertools.product([k for k in range(1,14)if k!=4],FLAGS):
            x=seed(old,kind,1);y=seed(new,kind,1)
            for q in [x,y]:
                q.put(JnAttack=5,JnWeapon=kind)
                for i in range(6):q.set('JnShotKind',2,i);q.set('JnShotAge',1,i)
                q.set('JnAmmo',10,max(0,kind-4))
            c,_=invoke(x,'JnWeapons',p=flags);d,_=invoke(y,'JnWeapons',p=flags)
            assert state(x,c)==state(y,d),('Other weapon fullpool caller',kind,flags)
            weapons.append(dict(kind=kind,delta=d.processorCycles-c.processorCycles))
        # Complete actual edge-triggered bat clocks, both faces: no age/attack/
        # shot/stock changes during the observed timeline.
        clocks=[]
        for face in [1,2]:
            q=seed(new,0,0,face);q.set('JnShotKind',0,5);q.put(JnSelected=1,JnWeapon=0,JnPressed=64);q.set('JnAmmo',10,0)
            rows=[]
            for tick in range(32):
                if tick:q.set('JnPressed',0)
                invoke(q,'JnWeapons');live=[i for i in range(6)if q.get('JnShotKind',i)==4]
                assert len(live)==(1 if tick<30 else 0)
                if live:assert q.get('JnShotAge',live[0])==tick+1
                assert q.get('JnAmmo',0)==9
                assert bool(q.get('JnAttack'))==(tick<31)
                rows.append(dict(tick=tick,live=bool(live),attack=q.get('JnAttack'),shot_age=q.get('JnShotAge',5)))
            clocks.append(dict(face=face,rows=rows))
        # Real IRQ injections at every executed instruction of all five helpers
        # under the true whole caller, including stacked PHP/PHA and both paths.
        seen=set()
        for name,cfg in [('JnDraw',dict(kind=4,age=12,face=2)),('JnDraw',dict(kind=5,age=4)),('JnWeapons',dict(kind=0)),('JnWeapons',dict(kind=4,age=8)),('JnWeapons',dict(kind=4,age=17))]:
            q=seed(new,**cfg)
            if name=='JnWeapons':q.put(JnSelected=1,JnPressed=64,JnWeapon=4);q.set('JnAmmo',10,0)
            c,t=invoke(q,name,p=0x61)
            spans=[(address(new,n),address(new,n)+int(new['syms'][n]['size'],0))for n in ['JnBatBeginAttack','JnBatReleaseIfDue','JnBatAttackLimit','JnBatContactIfActive','JnBatSelectRecord']]
            for idx,pc,bank in t:
                if bank==98 and any(a<=pc<z for a,z in spans)and pc not in seen:
                    seen.add(pc);z=seed(new,**cfg)
                    if name=='JnWeapons':z.put(JnSelected=1,JnPressed=64,JnWeapon=4);z.set('JnAmmo',10,0)
                    d,_=invoke(z,name,p=0x61,irq=idx)
                    differences=[i for i in range(32768)if q.m[i]!=z.m[i]and not 256<=i<510]
                    assert differences==[]or set(differences)<={0x2005,0x2006,0x5128,0x5130},('Unexpected IRQ difference',name,hex(pc),[(hex(i),q.m[i],z.m[i])for i in differences])
                    for at in differences:list.__setitem__(z.m,at,q.m[at])
                    assert state(q,c)==state(z,d),('IRQ caller flags',name,hex(pc),c.p,d.p)
                    irqrows.append(dict(pc=pc,caller=name,actual_hardware_latch_differences=differences))
        # Fresh all53 earned components on BOTH exact builds. Existing remainder
        # correction is reused literally; no new mechanics assertions removed.
        ns={'__file__':str(remainder.OLD),'__name__':'_bat_current_campaign'}
        exec(compile(remainder.change(remainder.OLD.read_text(),remainder.PY_PAIRS),str(remainder.OLD),'exec'),ns)
        campaigns=[]
        for b in [old,new]:
            h,_=ns['hooks_for'](b)
            for n,v in dict(Collect='JnCollectPickup',Injury='JnInjury',Defeat='JnDefeat',Reflect='JnReflectMagic',DropCollect='JnUpdateDrops::Collect').items():
                h[n]=dict(pc=address(b,v),banks=[(location(b,v)-16)//8192],bytes=list(b['raw'][location(b,v):location(b,v)+3]))
            original_invoke=Arena.invoke;cycles=[]
            def measured(q,name,*args,**kwargs):
                ans=original_invoke(q,name,*args,**kwargs)
                if name=='GameLoop':cycles.append(ans[0].processorCycles)
                return ans
            Arena.invoke=measured
            try:campaign=ns['campaign'](b,False,ns['plan_for'](False),h,address(b,'BulletBill_CannonVar'))
            finally:Arena.invoke=original_invoke
            assert campaign['passed']and len(cycles)==campaign['full_GameLoop_calls']
            campaigns.append(dict(ROM_sha256=hashlib.sha256(b['raw']).hexdigest(),complete_GameLoop_CPU=dict(calls=len(cycles),sum=sum(cycles),mean=sum(cycles)/len(cycles),min=min(cycles),max=max(cycles)),**campaign))
        foreign=[]
        for char in [i for i in range(20)if i!=16]:
            x=Arena(old,char);y=Arena(new,char)
            c,_=invoke(x,'RosterWeapons',p=0x61);d,_=invoke(y,'RosterWeapons',p=0x61)
            assert state(x,c)==state(y,d)and c.processorCycles==d.processorCycles,('Foreign complete dispatch',char)
            foreign.append(char)
        result.update(passed=True,parent_sha256=sha(build.BASE),candidate_sha256=sha(B/'mike_bat.nes'),CHR_pairs=pairs,foreign_RosterWeapons_exact=foreign,
            full_draw_cases=len(draws)+3840,other12_full_weapon_cases=len(weapons),IRQ_boundaries=len(irqrows),bat_clocks=clocks,
            draw_cycle_delta=dict(min=min(r['delta']for r in draws),max=max(r['delta']for r in draws)),
            other12_weapon_cycle_delta=dict(min=min(r['delta']for r in weapons),max=max(r['delta']for r in weapons)),
            campaigns=campaigns,limits='Source CPU only; native pixels/cadence remain unrun. Reference injects only intended new bat record/pointer before unchanged original renderer; no opcode substitution. Dead stack<=1FD excluded, caller-live1FE/1FF exact. SMB reach and record origins retained; palette fidelity unproved.')
    except Exception as e:
        result.update(error=repr(e),traceback=traceback.format_exc());put(output,result);raise
    put(output,result);print(json.dumps({k:v for k,v in result.items()if k not in ['campaigns','bat_clocks','CHR_pairs']}))

if __name__=='__main__':main()
