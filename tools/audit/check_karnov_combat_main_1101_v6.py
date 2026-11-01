"""Exercise proposed combat in actual Main, with an explicit RAM-code fixture.

This identifies integration/stack failures before granting a carrier. It never
changes a ROM or claims that the real loader installs the proposed component.
"""
from pathlib import Path
import argparse,hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import build_karnov_combat_component_1101_v2 as B
import check_karnov_pickup_composed_1101_v4 as P
import prepare_karnov_combat_stack_1101_v3 as S
from check_tmnt_render_oa import address,location
L,H,C,V=P.L,P.H,P.C,P.V
O=R/'build/karnov-combat-main-1101-v6'
BASE=R/'build/karnov-host-resource-base-1101-v1'
EXPECTED='0162287ebf5b8fcb8a84dcf108a0d0930c4dc9d6e68928c4804bd774712e1a6c'
INTEGRATED=False
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def bundle():
    assert sha(BASE/'candidate.nes')==EXPECTED
    b=H.C.qualified(BASE/'candidate.nes')
    if INTEGRATED:return b
    for line in (O/'component.lbl').read_text().splitlines():
        a=line.split()
        if len(a)==3:
            name=a[2].lstrip('.');value=int(a[1],16)
            if name in b['syms']:assert address(b,name)==value,(name,'Native component import moved')
            else:b['syms'][name]=dict(val=hex(value))
    return b


def put(m,**kw):
    H.put(m,**kw)


def overlay(m):
    if INTEGRATED:
        # Validate the real loader's bytes; never replace executable RAM.
        b=m.bundle
        assert bytes(m.ram[3])==b['raw'][1048592+399*1024:1048592+407*1024]
        assert bytes(m.ram[2][0x900:0xe00])==b['raw'][1048592+1019*1024:1048592+1019*1024+1280]
        assert m.ram[2][0x84d]==1 and m.ram[2][0x854]==0,'Five real gameplay frames must have accepted the combat epoch'
        return
    q=json.loads((O/'assembly-stage.json').read_text());b=m.bundle
    lo=q['kernel_lease'][0]-0xa000
    m.ram[3][lo:lo+q['kernel_bytes']]=(O/'kernel.bin').read_bytes()
    lo=q['proposed_C2_code_lease'][0]-0xc000
    m.ram[2][lo:lo+q['resident_bytes']]=(O/'resident.bin').read_bytes()
    for row in [4,34]:
        at=3*row;v=address(b,'KrCombat');m.ram[3][at:at+3]=bytes([76,v&255,v>>8])
    # Explicit proposed-context reset; public vine row35 is never replaced.
    m.ram[2][0x84d]=m.ram[2][0x854]=0


def keys(m,value=0):
    put(m,SavedJoypadBits=value,SavedJoypad1Bits=value,SavedJoypad2Bits=0,
        A_B_Buttons=value&192,Left_Right_Buttons=value&3,Up_Down_Buttons=value&12,NmiDisable=255)


def boot(b):
    m=C.fresh(b);put(m,CrossoverMenuIndex=7)
    for name in ['MenuResolveCharacter','QueueSelection']:C.invoke(m,name)
    put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0)
    C.invoke(m,'CrossoverMenuInput');C.invoke(m,'DrawSelectionPreview')
    assert H.get(m,'SelectedCharacter')==34
    put(m,SavedJoypad1Bits=16,SavedJoypad2Bits=0)
    C.invoke(m,'GameMenuRoutine');C.invoke(m,'PauseRoutine',a=0)
    for n in range(600):
        if H.get(m,'OperMode_Task')==3 and H.get(m,'GameEngineSubroutine')==8:break
        keys(m);P.call(m,'GameLoop');C.consume(m)
    else:raise AssertionError('Real Select/Start/parser bound')
    for _ in range(5):keys(m);P.call(m,'GameLoop');C.consume(m)
    overlay(m);return m,n+5


def fixture(seed,kind):
    m=C.fork(seed);b=m.bundle
    for name,count in [('Enemy_Flag',6),('Enemy_State',6),('Block_State',2),('Block_RepFlag',2)]:
        at=address(b,name)
        for i in range(count):m[at+i]=0
    # A single source shot; the genuine actor/weapon update still moves it.
    m.ram[2][0x65]=0
    for i in range(27):m.ram[2][0x6e+i]=0
    for at,value in [(0x6e,0x84),(0x6f,100),(0x70,110)]:m.ram[2][at]=value
    m.ram[2][0x84d]=m.ram[2][0x854]=0
    put(m,ObjectOffset=3,Square1SoundQueue=0,Square2SoundQueue=0,MmBlockAttack=0,TimerControl=0,CheatInvincible=1)
    if kind=='goomba':
        for name,value in [('Enemy_Flag',1),('Enemy_ID',6),('Enemy_X_Position',100),('Enemy_PageLoc',0),('Enemy_Y_Position',96),('Enemy_Y_HighPos',1),('Enemy_State',0),('Enemy_BoundBoxCtrl',3)]:m[address(b,name)]=value
        if INTEGRATED:
            # Reproduce the real first-Goomba geometry. Its native control9
            # starts14px below Enemy_Y; original crouch fire occupies rows8..15
            # below its source/OAM anchor. This replaces the historical
            # synthetic control3 fixture, whose box was in the blank half.
            m[address(b,'Enemy_Y_Position')]=184
            m[address(b,'Enemy_BoundBoxCtrl')]=9
            m.ram[2][0x70]=184
    else:
        tile={'brick':0x51,'question':0x55}[kind]
        at=address(b,'Block_Buffer_1')+(104>>4)+(112-32)
        m[at]=tile;m[at+address(b,'MmSolidTerrain')-address(b,'Block_Buffer_1')]=0
    keys(m);return m


def foreground(m):
    names=['Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos',
        'Player_State','Player_X_Scroll','Player_Pos_ForScroll','Player_Y_Speed','Player_X_Speed',
        'FrameCounter','CurrentBank','CurrentBankC','ObjectOffset']
    return [bytes(z)for z in m.ram],bytes(m[3:11]),bytes(m[0x200:0x300]),bytes(m[0x15a:0x17b]),m.rawtags[:],[H.get(m,n)for n in names]


def main_checks():
    stage=json.loads(((BASE/'terrain-assembly.json')if INTEGRATED else(O/'assembly-stage.json')).read_text());assert stage['passed']
    for p,h in stage['bindings'].items():assert sha(p)==h,p
    b=bundle();seed,setup=boot(b)
    previous=V.pending_store
    def pending(mem,c,slot,op):
        if previous(mem,c,slot,op):return True
        reg=0x5115 if slot==1 else 0x5116
        value={0x8d:c.a,0x8e:c.x,0x8c:c.y}.get(mem[c.pc])
        return value is not None and bytes(mem[c.pc+1:c.pc+3])==reg.to_bytes(2,'little')and value==H.get(mem,'CurrentBank'if slot==1 else'CurrentBankC')
    V.pending_store=pending
    out=[];minimum_ISR=255
    points={}
    for name in ['KrCombat','KrCombatRom','NativeRarePlayerHeadCollisionCore','HandleEnemyFBallCol','KrPickupPrepareBody']:
        pc=address(b,name)
        bank=3 if name=='KrCombat'else 2 if name=='KrCombatRom'else((location(b,name)-16)//8192)|128
        points[pc,bank]=name
    for kind in ['goomba','brick','question']:
        start=fixture(seed,kind);m=C.fork(start);trace=[];events=[];live=[];services=[]
        def observe(mem,c,i):
            bank=mem.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else None
            trace.append((c.pc,c.sp,bank))
            if bank==157 and c.pc==address(b,'KrDispatch'):
                target=address(b,'FarcallJmpTarget_SMC')
                row=((mem[target+1]|mem[target+2]<<8)-address(b,'KrServiceVeneers'))//3
                services.append(dict(row=row,SP=c.sp,step=i))
            name=points.get((c.pc,bank))
            if name:
                events.append((name,i,c.sp,bank))
                if name=='KrCombatRom':
                    fields=['PlayerSize','CrouchingFlag','Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','Player_Y_Speed','ObjectOffset','MmBlockAttack']
                    live.append((c.sp,fields,[H.get(mem,n)for n in fields],bytes(mem[3:11]),bytes(mem[0x101+c.sp:0x112+c.sp])))
            if live and mem[c.pc]==0x60 and c.sp==live[-1][0] and bank==2:
                sp,fields,values,zp,frame=live.pop()
                assert [H.get(mem,n)for n in fields]==values and bytes(mem[3:11])==zp,'Combat native proxy leaked into the actor'
                assert bytes(mem[0x101+sp:0x112+sp])==frame,'Parked return/transport frame changed'
        c,low=P.call(m,'GameLoop',observer=observe)
        assert not live
        assert any(e[0]=='KrCombatRom'for e in events),('Main did not call proposed worker',kind,events)
        if kind=='goomba':
            assert any(e[0]=='HandleEnemyFBallCol'for e in events)and m[address(b,'Enemy_State')]&32,('Main shot did not defeat Goomba',events,m.ram[2][0x6e:0x71])
        else:
            assert any(e[0]=='NativeRarePlayerHeadCollisionCore'for e in events),('Main shot did not reach native block effects',kind,events,m.ram[2][0x6e:0x71])
            assert any(m[address(b,'Block_State')+i]for i in range(2)),('Main block lacks native animation',kind)
        cuts={next(i for i,z in enumerate(trace)if z[1]==low)}
        cuts.update(e[1]for e in events if e[0]in ['KrCombatRom','NativeRarePlayerHeadCollisionCore','HandleEnemyFBallCol','KrPickupPrepareBody'])
        worker=next(e[1]for e in events if e[0]=='KrCombatRom')
        # Include the deepest combat call even when an earlier movement call
        # has a lower SP. Preserve every copy and both TXS boundary seams.
        end=next(i for i in range(worker+1,len(trace))if trace[i][2]==2 and m.ram[2][trace[i][0]-0xc000]==0x60 and trace[i][1]==trace[worker][1])
        combatlow=min(z[1]for z in trace[worker:end+1])
        cuts.add(next(i for i in range(worker,end+1)if trace[i][1]==combatlow))
        if 'KcParkFrame'in b['syms']:
            p0,p1=address(b,'KcParkFrame'),address(b,'KcUnparkFrame')
            for i,(pc,sp,bank)in enumerate(trace):
                if bank==2 and(p0-7<=pc<=p0+14 or p1-7<=pc<=p1+14):cuts.add(i)
        interrupts=[]
        for at,which in itertools.product(sorted(cuts),['IRQ','NMI']):
            z=C.fork(start);hits=[]
            def cut(mem,c,i):
                if i!=at:return
                oldstep=c.step;observed=[c.sp]
                def stepping():
                    observed[0]=min(observed[0],c.sp);result=oldstep()
                    observed[0]=min(observed[0],c.sp);return result
                c.step=stepping
                try:hits.append(dict(passed=True,**V.interrupt(mem,c,which)))
                except Exception as e:
                    hits.append(dict(passed=False,kind=which,error=repr(e),minimum_SP=observed[0]))
                    raise RuntimeError('Captured ISR failure')from e
                finally:c.step=oldstep
            try:
                cc,ll=P.call(z,'GameLoop',observer=cut)
                assert len(hits)==1 and(cc.a,cc.x,cc.y,cc.p,cc.sp)==(c.a,c.x,c.y,c.p,c.sp)and foreground(z)==foreground(m),('Combat Main ISR resumption',kind,at,which,hits)
            except RuntimeError as e:
                assert str(e)=='Captured ISR failure'and len(hits)==1 and not hits[0]['passed']
            minimum_ISR=min(minimum_ISR,hits[0]['minimum_SP'])
            interrupts.append(dict(step=at,foreground_PC=trace[at][0],foreground_SP=trace[at][1],**hits[0]))
        out.append(dict(case=kind,minimum_Main_SP=low,minimum_combat_SP=combatlow,services=services,events=events,interrupts=interrupts))
    return dict(passed=minimum_ISR>=135 and all(x['passed']for row in out for x in row['interrupts']),setup_Main=setup,minimum_Main_ISR_SP=minimum_ISR,reserve_above_SMC=minimum_ISR-123,cases=out)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--prepare',action='store_true');ap.add_argument('--park',action='store_true');args=ap.parse_args()
    assert sha(BASE/'candidate.nes')==EXPECTED
    if args.prepare:
        O.mkdir(exist_ok=True)
        if not(O/'unparked-negative.json').exists():
            assert(O/'Main-controls.json').exists()
            (O/'unparked-negative.json').write_bytes((O/'Main-controls.json').read_bytes())
        if args.park:
            B.SRC=O/'combat-stack-v3.inc';B.SRC.write_text(S.transform_source())
        B.O=O;B.main();return
    q=dict(passed=False,ROM_sha256=EXPECTED,explicit_component_RAM_overlay=True,native=False,installed=False)
    try:q['Main']=main_checks();q['passed']=q['Main']['passed']
    except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
    q['bindings']={str(p.resolve()):sha(p)for p in [Path(__file__),Path(S.__file__),B.SRC,O/'combat-stack-v3.inc',BASE/'candidate.nes',BASE/'candidate.dbg',O/'assembly-stage.json',O/'kernel.bin',O/'resident.bin']}
    (O/'Main-controls.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps(dict(passed=q['passed'],error=q.get('error'),minimum_ISR=q.get('Main',{}).get('minimum_Main_ISR_SP'),cuts=sum(len(x['interrupts'])for x in q.get('Main',{}).get('cases',[])))));assert q['passed'],q.get('error','Main interrupt reserve')


if __name__=='__main__':main()
