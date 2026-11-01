"""Actual linked Kirby Main/native defeat/ISR checks, one private cartridge."""
from pathlib import Path
import collections,copy,hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import check_hogan_current_bounded_v1 as C
import ff_wram_host_controls_v7 as H
import ff_host_pickups_vectors_v2 as V
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
O=R/'build/kirby-owner-main-1101-v2';PIN='c864e46a8f333ab7a936c8d8f330944041a3eff12bc6dd4d9ba96892144ff3c7';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def baseline_bundle(new):
    q=json.loads((O/'rollback-witness.json').read_text());raw=bytearray(new['raw']);syms=copy.deepcopy(new['syms'])
    for row in q['changes']:
        at=row['start'];before=bytes.fromhex(row['old']);assert bytes(raw[at:at+len(before)])==bytes.fromhex(row['new']);raw[at:at+len(before)]=before
    for name,row in q['moved_symbols'].items():syms[name]=row['old']
    for name in q['added_symbols']:del syms[name]
    assert hashlib.sha256(raw).hexdigest()==q['original_ROM_sha256'];return dict(raw=bytes(raw),syms=syms,segs=new['segs'])

class Observe:
    def __init__(self,b):
        self.points={};self.counts=collections.Counter();self.events=[];self.low=(255,0,0,0)
        for name in['KbInputs','KbMovement','KbWeapons','KbWeapons::Suction','KbWeapons::CopyAttack','KbWeapons::EnemyContacts','KbShellEnemyContact','KbBodyContact','KbBodyDispatch::Kirby','KbFamilyForEnemy','KbFamilyForEnemy::FamilyFlags','KbInjuryStart','KbDropCopy','ShellOrBlockDefeat','HandleEnemyFBallCol','SetupFloateyNumber','EraseEnemyObject','KbInhaleVertical','MkWeapons']:
            if name in b['syms']:self.points[address(b,name),((location(b,name)-16)//8192)|128]=name
    def __call__(self,m,c,i):
        tag=m.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else -1
        if c.sp<self.low[0]:self.low=(c.sp,i,c.pc,tag)
        name=self.points.get((c.pc,tag))
        if name:self.counts[name]+=1;self.events.append(dict(name=name,step=i,SP=c.sp,PC=c.pc,bank=tag,X=c.x,Y=c.y))

def call(m,name,observer=None):
    if name!='GameLoop':
        c=H.start(m,name,p=0x31);c,low=H.finish(m,c,observer);assert c.sp==224;return c,low
    # Real reset keeps its profiling JSR IdleLoop frame live forever.
    # Execute that exact JSR plus IdleLoop's PHA/JSR, not an invented outer
    # FarCallCommon at an arbitrary API SP. Native confirmed entry is$FA.
    b=m.bundle;start=address(b,'Start');size=int(b['syms']['Start']['size'],0);caller=start+size-3;idle=address(b,'IdleLoop');loop=address(b,'GameLoop')
    assert bytes(m[caller:caller+3])==bytes([32,idle&255,idle>>8])
    code=bytes(m[idle:idle+16]);pattern=bytes([32,loop&255,loop>>8]);pos=code.index(pattern);assert code[pos-1]==0x48 and code[pos+3]==0x68
    stop=idle+pos+4;c=NesMPU(memory=m,pc=caller);c.a=85;c.x=7;c.y=91;c.p=0x31;c.sp=255;low=255;entries=0
    for step in range(500000):
        if c.pc==stop:break
        if observer:observer(m,c,step)
        if c.pc==loop:assert c.sp==250;entries+=1
        low=min(low,c.sp);assert m[c.pc]!=0,('Actual parent Main BRK',hex(c.pc),m.rawtags);c.step()
    else:raise AssertionError(('Actual parent Main bound',hex(c.pc)))
    assert entries==1 and c.sp==253
    return c,low

def keys(m,value):
    H.put(m,SavedJoypadBits=value,SavedJoypad1Bits=value,SavedJoypad2Bits=0,A_B_Buttons=value&192,Left_Right_Buttons=value&3,Up_Down_Buttons=value&12,NmiDisable=255)

def main_step(m,value=0):
    keys(m,value);m.writes.clear();m.ram_writes.clear();m.ppu_log.clear();o=Observe(m.bundle);c,low=call(m,'GameLoop',o);return c,low,o

def cold(b):
    m=C.fresh(b);at=location(b,'X5MenuCharacters');chars=b['raw'][at:at+32];index=chars.index(13)
    H.put(m,CrossoverMenuIndex=index)
    for name in['MenuResolveCharacter','QueueSelection']:C.invoke(m,name)
    assert H.get(m,'SelectedCharacter')==13
    H.put(m,SavedJoypad1Bits=16,SavedJoypad2Bits=0);C.invoke(m,'GameMenuRoutine');C.invoke(m,'PauseRoutine',a=0)
    for setup in range(600):
        if H.get(m,'OperMode_Task')==3 and H.get(m,'GameEngineSubroutine')==8:break
        main_step(m);C.consume(m)
    else:raise AssertionError('Kirby actual Select/Start/parser bound')
    # Let the original entry movement land before a data-only legal scene.
    for _ in range(40):main_step(m);C.consume(m)
    assert H.get(m,'KbHealth')==6 and H.get(m,'KbCopy')==0 and H.get(m,'KbMouth')==0 and H.get(m,'KbHurt')==0
    return m,dict(menu_index=index,parser_Main=setup,settle_Main=40,normal_NMI=setup+40)

def scene(m,facing=1):
    b=m.bundle
    for name in['Block_Buffer_1','MmSolidTerrain','MmBrickHealth']:
        at=address(b,name)
        for i in range(416):m[at+i]=0
    for page,row,col in itertools.product(range(2),[11,12],range(16)):m[address(b,'Block_Buffer_1')+page*208+row*16+col]=0x54
    for i in range(6):m[address(b,'Enemy_Flag')+i]=0;m[address(b,'Enemy_CollisionBits')+i]=0
    H.put(m,Player_X_Position=112,Player_PageLoc=0,Player_Y_Position=176,Player_Y_HighPos=1,Player_State=0,PlayerFacingDir=facing,Player_MovingDir=facing,Player_CollisionBits=255,MmOldX=112,
      ScreenLeft_PageLoc=0,ScreenLeft_X_Pos=0,ScreenRight_PageLoc=0,ScreenRight_X_Pos=255,ScrollLock=1,ScrollThirtyTwo=0,AreaParserTaskNum=0,Player_X_Speed=0,Player_Y_Speed=0,Player_X_MoveForce=0,Player_Y_MoveForce=0,CrossoverBehaviorVersion=1)
    for name,count in[('MmVX',3),('MmVY',3),('MmXFraction',2),('MmYFraction',2)]:
        for i in range(count):m[address(b,name)+i]=0

def actor(m,kind,x,y=184,slot=0):
    for name,value in dict(Enemy_Flag=1,Enemy_ID=kind,Enemy_State=0,Enemy_X_Position=x&255,Enemy_PageLoc=x>>8,Enemy_Y_Position=y,Enemy_Y_HighPos=1,Enemy_X_Speed=0,Enemy_Y_Speed=0,Enemy_Y_MoveForce=0,Enemy_MovingDir=2,Enemy_BoundBoxCtrl=9,EnemyOffscrBitsMasked=0,Enemy_CollisionBits=0,MmEnemyHealthLo=0,MmEnemyHealthHi=0,MmEnemyFlash=0,RgEnemyStun=0).items():m[address(m.bundle,name)+slot]=value

def fg(m):
    # Lag NMI legitimately advances audio and may consume sound queues. Keep
    # every Kirby byte, map/SMC, world tile and live native actor field exact;
    # V.interrupt separately verifies live ZP and complete caller/page1 ABI.
    names=['SelectedCharacter','Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','Player_State','Player_X_Scroll','Player_Pos_ForScroll','Player_X_Speed','Player_Y_Speed','InjuryTimer','GameEngineSubroutine','FrameCounter','CurrentBank','CurrentBankC','ScreenLeft_X_Pos','ScreenLeft_PageLoc']
    actors=[]
    for name in['Enemy_Flag','Enemy_State','Enemy_ID','Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position','Enemy_Y_HighPos','Enemy_X_Speed','Enemy_Y_Speed','Enemy_BoundBoxCtrl','FloateyNum_Control']:
        at=address(m.bundle,name);actors.append(bytes(m[at:at+6]))
    at=address(m.bundle,'Block_Buffer_1')
    return([bytes(z)for z in m.ram],bytes(m[3:11]),bytes(m[0x200:0x300]),bytes(m[0x15a:0x17b]),bytes(m[0x5c00:0x5ca0]),H.get(m,'KbVariant'),m.rawtags[:],[H.get(m,n)for n in names],actors,bytes(m[at:at+416]))

def inhale_case(seed,side,B,record=False):
    m=C.fork(seed);scene(m);actor(m,6,120 if side=='front'else 104)
    c,low,o=main_step(m,B);result=dict(side=side,B=B,health=H.get(m,'KbHealth'),hurt=H.get(m,'KbHurt'),action=H.get(m,'KbAction'),age=H.get(m,'KbActionAge'),body_contacts=o.counts['KbBodyContact'],injury_entries=o.counts['KbInjuryStart'],minimum_SP=low,minimum_instruction=o.low,events=o.events)
    return m,result

def earned_copy(seed,family,facing,target_kind=6):
    m=C.fork(seed);scene(m,facing);actor(m,address(m.bundle,'GreenKoopa'if family==2 else'RedKoopa'),140 if facing==1 else 84)
    counts=collections.Counter();minimum=255;saved=[];rows=[]
    for age in range(100):
        c,low,o=main_step(m,64);minimum=min(minimum,low);counts.update(o.counts);C.consume(m)
        if H.get(m,'KbMouth'):break
    else:raise AssertionError(('Native inhale acquisition bound',family,facing,H.get(m,'KbHealth'),H.get(m,'KbAction'),H.get(m,'KbActionAge')))
    assert H.get(m,'KbHealth')==6 and H.get(m,'KbMouthCopy')==family;capture_updates=age+1
    main_step(m,4);C.consume(m);assert H.get(m,'KbCopy')==family and H.get(m,'KbMouth')==0
    # The held controller is released naturally; copy/cooldown/action/health
    # are never seeded. The source may still show its swallow animation.
    main_step(m,0);C.consume(m);actor(m,target_kind,212 if facing==1 else 32)
    for age in range(70):
        keys(m,64 if age==0 else 0);origin=C.fork(m);c,low,o=main_step(m,64 if age==0 else 0);minimum=min(minimum,low);counts.update(o.counts)
        if o.counts['KbShellEnemyContact']or o.counts['ShellOrBlockDefeat']:
            if o.counts['ShellOrBlockDefeat']or not saved:saved=[(origin,C.fork(m),(c.a,c.x,c.y,c.p,c.sp),o,age)]
        if o.counts['ShellOrBlockDefeat']:
            result=dict(copy=family,facing=facing,target_kind=target_kind,earned_inhale_updates=capture_updates,kill_update=age+1,health=H.get(m,'KbHealth'),enemy_state=H.get(m,'Enemy_State'),score=H.get(m,'FloateyNum_Control'),SFX=H.get(m,'Square1SoundQueue'),minimum_Main_SP=minimum,source_counts=dict(counts));assert H.get(m,'KbHealth')==6 and H.get(m,'Enemy_State')&32 and H.get(m,'KbShotType')==0
            return result,saved
        C.consume(m)
    raise AssertionError(('Grounded copied shell did not reach native defeat',family,facing,target_kind,H.get(m,'KbShotType'),H.get(m,'Enemy_State')))

def interrupts(samples):
    minimum=255;rows=[];previous=V.pending_store
    def pending(m,c,slot,op):
        if previous(m,c,slot,op):return True
        target=0x5115 if slot==1 else 0x5116;value={0x8d:c.a,0x8e:c.x,0x8c:c.y}.get(m[c.pc])
        return value is not None and bytes(m[c.pc+1:c.pc+3])==target.to_bytes(2,'little')and value==H.get(m,'CurrentBank'if slot==1 else'CurrentBankC')
    V.pending_store=pending
    try:
        for origin,expected,regs,observer,case in samples:
            cuts={observer.low[1]}|{e['step']for e in observer.events if e['name']in['KbBodyContact','KbBodyDispatch::Kirby','KbFamilyForEnemy','KbFamilyForEnemy::FamilyFlags','KbShellEnemyContact','ShellOrBlockDefeat']}
            for cut,kind in itertools.product(sorted(cuts),['IRQ','NMI']):
                m=C.fork(origin);events=[]
                def inject(mem,c,i):
                    if i==cut:
                        before=bytes(mem[0x15a:0x17b]);initial=dict(case=case,cut=i,foreground_SP=c.sp,PC=c.pc,bank=mem.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else -1,NmiDisable=H.get(mem,'NmiDisable'),IRQ_mask=bool(c.p&4),input=H.get(mem,'SavedJoypadBits'));worst=[c.sp,c.pc,None];original=c.step
                        def track():
                            if c.sp<worst[0]:worst[:]=[c.sp,c.pc,mem.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else -1]
                            return original()
                        c.step=track
                        try:row=V.interrupt(mem,c,kind)
                        except Exception as e:
                            after=bytes(mem[0x15a:0x17b]);delta=[dict(address=0x15a+j,before=a,after=b)for j,(a,b)in enumerate(zip(before,after))if a!=b]
                            raise AssertionError(('ISR boundary failure',initial,kind,repr(e),dict(minimum_SP=worst[0],PC=worst[1],bank=worst[2]),delta))from e
                        finally:del c.step
                        events.append(dict(**initial,**row))
                c,low=call(m,'GameLoop',inject);assert len(events)==1
                assert(c.a,c.x,c.y,c.p,c.sp)==regs and fg(m)==fg(expected),('Actual Kirby Main ISR resumption',case,cut,kind)
                minimum=min(minimum,events[0]['minimum_SP']);rows.append(dict(events[0]))
    finally:V.pending_store=previous
    return dict(passed=minimum>=135,cases=len(rows),minimum_ISR_SP=minimum,reserve_above_SMC=minimum-123,rows=rows)

def main():
    q=dict(passed=False,source_CPU=True,native_emulator=False,installed=False,ROM_sha256=PIN)
    try:
        assert sha(O/'candidate.nes')==PIN;new=qualified(O/'candidate.nes');old=baseline_bundle(new);oldseed,oldstart=cold(old);seed,start=cold(new)
        outcomes=[];samples=[]
        for side,B in[('front',64),('front',0),('rear',64)]:
            _,a=inhale_case(oldseed,side,B);m,b=inhale_case(seed,side,B);outcomes.append(dict(old=a,new=b))
            assert a['body_contacts']==0 and b['body_contacts'],('Actual missing/rerouted service',a,b)
            if side=='front'and B==64:assert a['health']==5 and b['health']==6 and b['injury_entries']==0
            else:assert a['health']==b['health']==5
        # Capture exact first fresh-B Main for IRQ/lagNMI resumption.
        m=C.fork(seed);scene(m);actor(m,6,120);keys(m,64);origin=C.fork(m);c,low,o=main_step(m,64);samples.append((origin,C.fork(m),(c.a,c.x,c.y,c.p,c.sp),o,'fresh-B-front'))
        earned=[]
        for family,facing,target in itertools.product([2,3],[1,2],[6,0]):
            row,saved=earned_copy(seed,family,facing,target);earned.append(row);samples.extend([(a,b,c,d,f'copy{family}-face{facing}-target{target}')for a,b,c,d,_ in saved])
        native_path=R/'build/kirby-owner-native-1101-v2/stack/capture/result.json';native=json.loads(native_path.read_text());assert native['ROM_sha256']==PIN and native['actual_Main_entry_SP']=={'250':True}
        rootat=location(new,'Start');rootsize=int(new['syms']['Start']['size'],0);idleat=location(new,'IdleLoop')
        q.update(old_base_reconstructed_from_compact_delta=True,actual_Select_Start_parser=dict(old=oldstart,new=start),inhale_contacts=outcomes,earned_shells=earned,actual_Main_caller=dict(reset_initial_SP=255,reset_LDXFF_TXS_bytes=new['raw'][rootat:rootat+13].hex(),Start_tail_JSR_PC=address(new,'Start')+rootsize-3,Start_tail_JSR_bytes=new['raw'][rootat+rootsize-3:rootat+rootsize].hex(),IdleLoop_prefix=new['raw'][idleat:idleat+16].hex(),GameLoop_entry_SP=250,observed_native_entry_SP=native['actual_Main_entry_SP'],native_entry_updates=native['updates'],native_entry_witness_path=str(native_path),native_entry_witness_sha256=sha(native_path),stop='Actual IdleLoop PLA immediately after GameLoop RTS; next CMP/catch-up policy is not normalized or executed in this one-update interrupt proof.'),scope='Actual full cartridge reset-tail JSR/IdleLoop PHA+JSR/GameLoop/parentPLA, real Select/Start/native parser/weapons/collision/defeat/score/SFX/IRQ/NMI instructions. Source caller depth is independently anchored to nativeSPFA on965updates. Only declared flat terrain/player position/NPC data fixtures; no ability/health/shot/result or executable overlays. LagNMI counter may legitimately trigger a later catch-up; this test verifies the interrupted GameLoop return before that comparison. Full-stage/audio qualification remains separate.')
        q['interrupts']=interrupts(samples);q['passed']=True
        assert q['interrupts']['passed'],('Actual Main/ISR12B reserve',q['interrupts']['minimum_ISR_SP'])
    except Exception as e:q.update(passed=False,error=repr(e),traceback=traceback.format_exc())
    q['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),O/'candidate.nes',O/'candidate.dbg',O/'owner-link.json',O/'rollback-witness.json',R/'tools/audit/check_hogan_current_bounded_v1.py',R/'tools/audit/ff_wram_host_controls_v7.py',R/'tools/audit/ff_host_pickups_vectors_v2.py']+([native_path]if'native_path'in locals()else[])}
    (O/'Main-CPU.json').write_text(json.dumps(q,indent=2)+'\n');shown={k:v for k,v in q.items()if k not in['bindings','traceback']}
    if'interrupts'in shown:shown['interrupts']={k:v for k,v in shown['interrupts'].items()if k!='rows'}
    if'inhale_contacts'in shown:shown['inhale_contacts']=[{k:{n:v for n,v in r.items()if n!='events'}for k,r in row.items()}for row in shown['inhale_contacts']]
    print(json.dumps(shown));assert q['passed'],q.get('error')
if __name__=='__main__':main()
