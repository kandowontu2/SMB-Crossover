"""Compare the complete UI service chain and linked Main, never a no-op leaf."""
from pathlib import Path
import itertools,json,sys,traceback,copy
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import arthur_physical_clock_context_v2 as V
import arthur_joint_live_isr_v5 as I
import arthur_physical_clock_isr_v6 as J
from arthur_physical_clock_controls_v2 import fresh,electrical_nmi,static
import ff_upper_fx_windows_controls_1030_v2 as U
from sunny_integrated_controls_v1 import registers,smc_at
A=V.A;H=U.H;O=R/'build/new-roster-ui-source-route-1030-v5'
P=R/'build/current-character-composition-v2/joint';sha=U.sha


def signature(q,c):
    ignore=set(range(256,512))|set(range(0x5114,0x5118))|set(smc_at(q.b))|{
        A.address(q.b,'CurrentBank'),A.address(q.b,'CurrentBankC')}
    writes=[(a,v)for a,v in q.m.writes if a not in ignore]
    return A.C.M.fastapp(q),registers(c),q.m.rawtags[:],[bytes(x)for x in q.m.ram],writes


def ui(old,new):
    bases=[A.C.setup(b,0)for b in[old,new]];rows=[]
    # Every raw selector plus all status flags for the changed owners. UI
    # fixtures intentionally include cold/unready source owners; active FF
    # and Arthur are separately tested using their genuine constructors.
    cases=[(ch,p,joy,hurt,hud)for ch,p,joy,hurt,hud in itertools.product(range(256),[0x30],[0,32],[0],[0,1])]
    cases +=[(ch,p,129,0,0)for ch,p in itertools.product(range(20,33),range(256))]
    cases +=[(ch,0x71,255,hurt,1)for ch,hurt in itertools.product(range(33),[1,7])]
    for ch,p,joy,hurt,hud in cases:
        pair=[];cost=[]
        for b,base in zip([old,new],bases):
            q=I.clone(base);q.put(SelectedCharacter=ch,SavedJoypad1Bits=joy,InvPrevious=32,
                GuestHurtTicks=hurt,GuestHurtKind=4,InvHudActive=hud,InvDirty=0,
                NativeStatusPending=0,X5BounceOwner=0,FamilyMainCommit=1)
            q.m.writes=[]
            c,tr,mn=A.call(q,'X5BounceUiDispatch',a=53,x=7,y=91,p=p)
            pair.append(signature(q,c));cost.append(c.processorCycles)
        assert pair[0]==pair[1],('actual UI parity',ch,p,joy,hurt,hud,
            [i for i,(a,z)in enumerate(zip(pair[0],pair[1]))if a!=z])
        rows.append([ch,p,joy,hurt,hud,cost[1]-cost[0]])
    return dict(passed=True,actual_UI_pairs=len(rows),CPU_delta=[min(r[-1]for r in rows),max(r[-1]for r in rows)],rows=rows,
        full_application_ordered_writes_AXYP_SP_rawmaps_RAM_payloads_exact=True,
        every_raw_selector_all256flags_for_newowners_and_hurt_input_histories=True)


def hud(old,new):
    bases=[A.C.setup(b,0)for b in[old,new]];rows=[]
    for x,p,value in itertools.product([0,13,14,16,17,19,20,32,255],range(256),[0,1,255]):
        result=[];cost=[]
        for b,q in zip([old,new],bases):
            q.put(InvHudActive=value)
            c,tr,mn=A.call(q,'X5OwnInventoryUi::HudRead',a=53,x=x,y=91,p=p)
            result.append(registers(c));cost.append(c.processorCycles)
        assert result[0]==result[1],('HUD read flag/return contract',x,p,value,result)
        rows.append([x,p,value,cost[1]-cost[0]])
    return dict(passed=True,actual_HudRead_pairs=len(rows),CPU_delta=[min(r[-1]for r in rows),max(r[-1]for r in rows)],
        actual_all256flags_and_NZCVDI_contract_exact=True,rows=rows)


def arthur(old,new):
    bases=[fresh(b)for b in[old,new]];gates=[V.C.L.L.load_nmi(b)for b in[old,new]];rows=[]
    for age in range(1,19):
        normal=(age-1)%3==0;keys=1|(128 if 7<=age<10 or 16<=age<19 else 0)
        pair=[];cost=[]
        for b,q,g in zip([old,new],bases,gates):
            q.put(NmiDisable=0 if normal else 255,FamilyMainCommit=0 if normal else 1,
                VRAM_Buffer_AddrCtrl=0,VRAM_Buffer1_Offset=0)
            electrical_nmi(q,g,keys)
            if not normal:continue
            q.put(NmiDisable=255,FamilyMainCommit=1,VRAM_Buffer_AddrCtrl=0,VRAM_Buffer1_Offset=0)
            q.m.writes=[];c,tr,mn,ann,events=A.M.run_linked(q,'GameLoop')
            assert tr.count(A.point(b,'ArStep'))==1
            pair.append(signature(q,c));cost.append(c.processorCycles)
        if normal:
            assert pair[0]==pair[1],('actual Arthur Main',age)
            rows.append([age,*cost,cost[1]-cost[0]])
    return dict(passed=True,actual_Arthur_Main_real_serial_NMI_pairs=len(rows),rows=rows,
        CPU_delta=[min(r[-1]for r in rows),max(r[-1]for r in rows)],source_physics_body_world_OAM_queues_and_state_exact=True)


def ff():
    rows=[]
    bundles=[H.C.qualified(p)for p in[P/'candidate.nes',O/'candidate.nes']]
    for variant,mode,joy in itertools.product(range(4),['base','star','upgrade'],[0,129]):
        results=[];cost=[];counts=[]
        for b in bundles:
            m=U.M.setup(b);H.put(m,FfVariant=variant,FfPaletteAck=255,VRAM_Buffer1_Offset=0,
                GuestPowerupActive=int(mode=='upgrade'),GuestPowerupAge=7,
                StarInvincibleTimer=3 if mode=='star'else 0,FrameCounter=8,
                SavedJoypadBits=joy,SavedJoypad1Bits=joy,A_B_Buttons=joy&192,Left_Right_Buttons=joy&3)
            m.writes.clear();calls=[]
            def observe(mem,c,i):
                if c.pc==H.address(b,'FwPaletteTick')and mem.rawtags[1]==190:calls.append(c.pc)
            c,_=U.M.invoke_main(m,observe)
            # Use the same exact whole-state signature as FF foreign-Main
            # controls; only standard stack/SMC/PRG transport is transient.
            result=U.F.signature(m,c);results.append(result);cost.append(c.processorCycles);counts.append(len(calls))
        assert counts==[1,1],('FF source palette tick retained',variant,mode,joy,counts)
        assert results[0]==results[1],('actual FF Main parity',variant,mode,joy)
        rows.append([variant,mode,joy,*cost,cost[1]-cost[0]])
    return dict(passed=True,actual_FF_Main_pairs=len(rows),source_palette_tick_always_once=True,
        CPU_delta=[min(r[-1]for r in rows),max(r[-1]for r in rows)],rows=rows)


def isr(b):
    base=fresh(b);base.put(NmiDisable=255,FamilyMainCommit=1,NativeStatusPending=0,X5BounceOwner=0)
    q=I.clone(base);c=I.start(q,'X5BounceUiDispatch');cuts=[];seen=set()
    for step in range(20000):
        if c.pc==0x5b00:break
        tag=q.m.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else -1
        if tag==214 and(0xa786<=c.pc<0xa79c or c.pc==A.address(b,'X5OwnInventoryUi::HudRead')+10):
            if c.pc not in seen:
                seen.add(c.pc);z=I.clone(q);d=copy.copy(c);d.memory=z.m;cuts.append((step,c.pc,z,d))
        c.step()
    else:raise AssertionError('bounded UI discovery')
    assert len(cuts)>=8,('all appended restore/farcall instruction cuts',len(cuts))
    rows=[]
    for step,pc,state,cpu in cuts:
        for kind in['NMI','IRQ']:
            q=I.clone(state);d=copy.copy(cpu);d.memory=q.m
            if kind=='IRQ'and d.p&d.INTERRUPT:continue
            r=J.interrupt(q.m,d,kind);I.run(q,d)
            assert d.sp==240 and q.get('ArHostReady')==167
            rows.append(dict(step=step,PC=pc,**r))
    return dict(passed=True,actual_lag_NMI_IRQ_cuts=len(rows),snapshots=len(cuts),rows=rows,
        live_AXYP_SP_SMC33_page1_maps_and_only_authorized_physical_clock_writes=True)


def main():
    out=O/'controls-v2.json';assert not out.exists();proof=dict(passed=False,native=False,admitted=False,checks={})
    try:
        h=json.loads((O/'source-closure.json').read_text())
        for p,v in h['bindings'].items():assert sha(p)==v,p
        old,new=[A.scoped_load(p)for p in[P/'candidate.nes',O/'candidate.nes']]
        for name,fn in[('UI',lambda:ui(old,new)),('HudRead',lambda:hud(old,new)),
                       ('ArthurMain',lambda:arthur(old,new)),('FFMain',ff),('ISR',lambda:isr(new))]:
            proof['checks'][name]=fn();print(name,'PASS',flush=True)
        proof['passed']=True
    except Exception as e:proof.update(error=repr(e),traceback=traceback.format_exc())
    proof['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),Path(V.__file__),Path(I.__file__),Path(J.__file__),Path(U.__file__),
        O/'source-closure.json',P/'candidate.nes',P/'candidate.dbg',O/'candidate.nes',O/'candidate.dbg']}
    target=out if proof['passed']else O/'controls-negative-v2.json';assert not target.exists()
    target.write_text(json.dumps(proof,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(passed=proof['passed'],checks=list(proof['checks']),error=proof.get('error'),path=str(target))),flush=True)
    assert proof['passed']


if __name__=='__main__':main()
