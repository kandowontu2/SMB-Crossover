"""Exact-composed authenticated pickup CPU tests; no code/RAM overlays."""
from pathlib import Path
import argparse,collections,hashlib,itertools,json,shutil,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
O=R/'build/karnov-pickup-composed-1101-v4';BASE=R/'build/karnov-host-resource-base-1101-v1'
OLD='e8d35a95ffe8e396dc1d8b32ca78d57d376fc14de9a2f4b37754012448fde09a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
import battletoads_current_loader_controls_v1 as L
import ff_wram_host_controls_v7 as H
import check_hogan_current_bounded_v1 as C
import ff_host_pickups_vectors_v2 as V
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
from recover_karnov_actor_1101_v1 import ROM,EXPECTED
from check_karnov_actor_1101_v1 import Memory

def source_fixture(m,values):
    """Only declared actor/data fixtures; never executable RAM/cache overlay."""
    for field,value in values.items():m.ram[2][field]=value

class TransportObserver:
    def __init__(self,b):
        self.b=b;self.live=[];self.counts=collections.Counter();self.events=[];self.low=(255,0,0,0)
        self.resident=((location(b,'KrDispatch')-16)//8192)|128;self.start=address(b,'KrDispatch');self.end=address(b,'KrDispatchReturn');self.veneer=address(b,'KrServiceVeneers');self.target=address(b,'FarcallJmpTarget_SMC');self.points={}
        for name in ['KrPickupPrepare','KrPickupPrepareBody','KrPickupMature','KrPickupCollect','KrPickupSuperFireball','KrPickupGrantOption','UnionPwrUpCore','SetupPowerUp']:
            if name in b['syms']:self.points[address(b,name),3 if name=='KrPickupMature'else((location(b,name)-16)//8192)|128]=name
    def __call__(self,m,c,step):
        b=self.b
        if c.pc<0x8000:return
        tag=m.rawtags[(c.pc-0x8000)//8192]
        if c.sp<self.low[0]:self.low=(c.sp,step,c.pc,tag)
        if tag==self.resident and c.pc==self.start:
            target=m[self.target+1]|m[self.target+2]<<8
            row=(target-self.veneer)//3
            self.live.append((row,bytes(m[0x15a:0x17b]),bytes(m[3:11]),m.rawtags[2],H.get(m,'CurrentBankC')))
        if tag==self.resident and c.pc==self.end:
            assert self.live,'Return without authenticated service entry'
            row,smc,zp,oldc,shadow=self.live.pop()
            if row in [20,23,24]:
                assert bytes(m[0x15a:0x17b])==smc,('Composed service SMC',row)
                assert bytes(m[3:11])==zp,('Composed service R0..R7',row)
                assert(m.rawtags[2],H.get(m,'CurrentBankC'))==(oldc,shadow),('Composed C2 caller map',row)
                self.counts[row]+=1
        name=self.points.get((c.pc,tag))
        if name:self.events.append((name,step,c.sp,tag))

def call(m,name,row=None,observer=None,**kw):
    c=H.start(m,name,**kw)
    if row is not None:
        pc=address(m.bundle,name)+3*row;m[address(m.bundle,'FarcallJmpTarget_SMC')+1]=pc&255;m[address(m.bundle,'FarcallJmpTarget_SMC')+2]=pc>>8
    oldmaps=m.rawtags[:];c,low=H.finish(m,c,observer)
    assert c.sp==kw.get('sp',224)and m.rawtags[1]==oldmaps[1]and m.rawtags[2]==H.get(m,'CurrentBankC'),(name,'Native return/map',m.rawtags,oldmaps)
    return c,low

def object_fields(m,slot=5,kind=0,state=128,x=173,y=160):
    b=m.bundle
    H.put(m,ObjectOffset=slot,VRAM_Buffer1_Offset=0,Square2SoundQueue=0,PlayerStatus=0,StarInvincibleTimer=0,TimerControl=0)
    for n,v in [('Enemy_Flag',1),('Enemy_ID',46),('Enemy_State',state),('PowerUpType',kind),('Enemy_Y_HighPos',1),('Enemy_Y_Position',y),('Enemy_PageLoc',0),('Enemy_X_Position',x),('Enemy_BoundBoxCtrl',3)]:m[address(b,n)+slot]=v
    H.put(m,ScreenLeft_X_Pos=21,ScreenLeft_PageLoc=0,ScreenRight_X_Pos=20,ScreenRight_PageLoc=1)

def cold(b):
    m=L.make(b,SelectedCharacter=34,FmAlts=1,CurrentPlayer=0)
    call(m,'InitScreen')
    assert m.ram[2][address(b,'KrReady')&8191]==167
    expected=b['raw'][1048592+399*1024:1048592+407*1024]
    assert bytes(m.ram[3])==expected,'Cold loader did not install actual ROM image'
    return m

def donor_run(state,kind,item=0,flags=0x71):
    raw=ROM.read_bytes();m=Memory();m[:2048]=state;m[0xc000:]=raw[16+14*8192:16+16*8192];m[0xa000:0xc000]=raw[16+11*8192:16+12*8192]
    c=NesMPU(memory=m,pc=0xad79 if kind=='fireball'else 0xef61);c.a=item;c.x=7;c.y=91;c.p=flags;c.sp=224;c.stPushWord(0x5afe);events=[]
    for _ in range(2000):
        if c.pc==0x5aff:break
        if c.pc==0xadb1 or c.pc==0xc81d:
            if c.pc==0xc81d:events.append(c.a)
            c.pc=(c.stPopWord()+1)&65535;continue
        assert m[c.pc]!=0,('Original donor BRK',hex(c.pc));c.step()
    else:raise AssertionError('Donor bound')
    return bytes(m[:2048]),events

def source_compare(expected,m):
    skip=set(range(0x100,0x200))|{0x58,0x59,0x7fe,0x7ff}|set(range(0xb4,0xba))|set(range(0x58f,0x5a3))|set(range(0x5af,0x5c3))
    delta=[i for i in range(2048)if i not in skip and expected[i]!=m.ram[2][i]]
    assert not delta,('Earned donor/private state',[(hex(i),expected[i],m.ram[2][i])for i in delta[:10]])

def core_checks(b,expected):
    q=dict(passed=False,ROM_sha256=expected,no_code_overlay=True,native_emulator=False,installed=False)
    stage=json.loads((BASE/'terrain-assembly.json').read_text());assert stage['passed']and stage.get('pickups')
    seed=cold(b);observer=TransportObserver(b);code=bytes(seed.ram[3]);native_low=224;source_pairs=0;spawn=0;digest=hashlib.sha256()
    # Actual authenticated service transport, all source health/shot encodings
    # and all10original options; native cleanup/SFX/score run after exact donor.
    for kind,health,weapon,cycle in itertools.product([0,1],[0,64,128,192],[0,1,2,8],[0,9]):
        m=L.fork(seed);object_fields(m);m[address(b,'PowerUpType')+5]=kind
        source_fixture(m,{0x68:health|(2 if weapon&12 else 0),0x69:37,0x65:weapon,0x860:cycle,0xba:0x49,0x40b:0x99,0x70f:0,0x710:0})
        before=bytes(m.ram[2][:2048]);base=m.ram[2][0x68]&3 if weapon&12 else weapon&3
        option=kind==1 and not health&128 and base>=2
        oracle,events=donor_run(before,'option'if option else'fireball',cycle)
        oldmaps=m.rawtags[:];c,low=call(m,'KrServiceVeneers',row=24,x=5,observer=observer);native_low=min(native_low,low)
        source_compare(oracle,m);assert bytes(m.ram[3])==code
        assert H.get(m,'PlayerStatus')==0 and H.get(m,'Square2SoundQueue')==32
        assert m[address(b,'Enemy_Flag')+5]==0 and m[address(b,'Enemy_ID')+5]==0
        assert m[address(b,'FloateyNum_Control')+5]==(11 if option and cycle==9 else 6)
        assert m[address(b,'FloateyNum_X_Pos')+5]==152
        assert all(m[address(b,n)+5]==0 for n in ['InvPickupOwner','InvPickup','InvRisePhase','InvPickupSaveLo','InvPickupSaveHi'])
        assert m.ram[2][0x860]==((cycle+1)%10 if option else cycle)
        if events:assert m.ram[2][address(b,'KrSoundEvent')&8191]==events[-1]
        digest.update(bytes(m.ram[2][:256]));source_pairs+=1
    for item,stock in itertools.product(range(10),[0,9,0x49,0x99]):
        m=L.fork(seed);object_fields(m,kind=1);source_fixture(m,{0x68:0,0x65:2,0x860:item,0xba:0x49,0x40b:stock,0xbb:stock,0xbc:stock,0xbd:stock,0xbe:stock,0xbf:stock,0x70f:0,0x710:7})
        oracle,_=donor_run(bytes(m.ram[2][:2048]),'option',item)
        c,low=call(m,'NrPickup',x=5,observer=observer);native_low=min(native_low,low);source_compare(oracle,m);source_pairs+=1
    for health,weapon,saved,kind in itertools.product([0,128],[0,1,2,8,12],[0,1,2],[0,2,3]):
        m=L.fork(seed);object_fields(m,kind=kind);source_fixture(m,{0x68:health|saved,0x65:weapon})
        before=bytes(m.ram[2][:2048]);c,low=call(m,'UnionPwrUpCore',x=5,observer=observer);native_low=min(native_low,low)
        base=saved if weapon&12 else weapon&3;want=kind if kind>=2 else int(not health and bool(base))
        assert m[address(b,'PowerUpType')+5]==want and bytes(m.ram[2][:2048])==before
        assert m[address(b,'Enemy_State')+5]==1 and m[address(b,'Enemy_Flag')+5]==1
        spawn+=1
    mature=0
    for kind,state in itertools.product(range(4),[0,1,6,17,127,128]):
        m=L.fork(seed);object_fields(m,kind=kind,state=state);before=bytes(m.ram[2][:2048])
        c,low=call(m,'NrPickupCollision',x=5,observer=observer);native_low=min(native_low,low)
        assert bool(c.p&1)==bool(kind>=2 or state>=128)and bytes(m.ram[2][:2048])==before;mature+=1
    negative=0
    for owner,bank,offset in [(34,2,0x1fe1),(34,3,0x1fef),(0,None,None)]:
        for row in [20,23,24]:
            m=L.fork(seed);object_fields(m);H.put(m,SelectedCharacter=owner)
            if bank is not None:m.ram[bank][offset]^=1
            before=bytes(m.ram[2][:2048]);c,_=call(m,'KrServiceVeneers',row=row,x=5,observer=observer)
            assert not c.p&1 and bytes(m.ram[2][:2048])==before and m[address(b,'Enemy_Flag')+5]==1;negative+=1
    # A genuine same-life scene preserves cycle; a lost-life/new-player scene
    # goes through the new source constructor Reset, not a test-side clear.
    m=L.fork(seed);m.ram[2][0x860]=7;call(m,'InitScreen');assert m.ram[2][0x860]==7
    H.put(m,NumberofLives=1);call(m,'InitScreen');assert m.ram[2][0x860]==0
    assert not observer.live
    q.update(passed=True,donor_sha256=EXPECTED,donor_contact_pairs=source_pairs,actual_Union_spawn_cases=spawn,actual_maturity_cases=mature,actual_cookie_foreign_rejections=negative,authenticated_service_calls=dict(observer.counts),minimum_API_SP=native_low,earned_trace_sha256=digest.hexdigest(),same_life_preserves_cycle=True,new_life_resets_cycle=True,scope='Actual final ROM loader/authenticated resident/final service routes/ROM29 workers and native object consumers; only declared actor/object/data fixtures, no executable overlay. Full donor earned state compared excluding legacyHUD/dispatch/stack boundaries. Main/emergence/old-owner/ISR checks are separate below.')
    return q,seed

def old_owner_checks(old,new):
    # Strong byte ownership proof first: all changed ROM bytes must belong to
    # Karnov's existing source-funded resident lease or its8KB CHRcode carrier.
    ranges=[(location(old,'KrResidentBegin'),location(old,'KrResidentLimit')),(1048592+399*1024,1048592+407*1024)]
    operands=set();relocations=[]
    # These existing native farcall sites target private functions after the
    # shortened dispatcher. Verify the entire unchanged template and actual
    # old/new target tuple before admitting only the three immediate bytes.
    for caller,target,offsets,size in [('InitScreen','KrSceneInit',[12,17,22],48),('FmResolve::Native','KrMenuResolve',[4,9,14],20),('FmStartFlags','KrStartFlags',[4,9,14],20)]:
        at=location(old,caller);assert at==location(new,caller)and address(old,caller)==address(new,caller)
        oldbytes=old['raw'][at:at+size];newbytes=new['raw'][at:at+size]
        for b,data in [(old,oldbytes),(new,newbytes)]:
            value=address(b,target);assert[data[i]for i in offsets]==[value&255,value>>8,((location(b,target)-16)//8192)|128]
            assert all(data[i-1]==0xa9 for i in offsets)
        assert all(a==z for i,(a,z)in enumerate(zip(oldbytes,newbytes))if i not in offsets),(caller,'Farcall template changed')
        operands.update(at+i for i in offsets)
        relocations.append(dict(caller=caller,callee=target,offsets=offsets,before=address(old,target),after=address(new,target)))
    changed=0
    assert len(old['raw'])==len(new['raw'])
    for i,(a,z)in enumerate(zip(old['raw'],new['raw'])):
        if a!=z:assert any(lo<=i<hi for lo,hi in ranges)or i in operands,('Foreign ROM byte changed',hex(i));changed+=1
    cases=0;digest=hashlib.sha256()
    for owner,alts,kind,state in itertools.product(range(34),[0,255],[0,1,2,3],[1,128]):
        if owner==7 and alts&1:continue # current Karnov alias, intentionally changed
        outcomes=[]
        for b in [old,new]:
            m=L.make(b,SelectedCharacter=owner,FmAlts=alts,FmGroups=0,MarioVariant=0);object_fields(m,kind=kind,state=state)
            regs=[]
            for name in ['NrPrepare','NrPickupCollision','NrPickup']:
                c,_=call(m,name,x=5);regs.append((c.a,c.x,c.y,c.p,c.sp))
            low=bytes(m[3:0x100])+bytes(m[0x200:0x800])+bytes(m[0x5c00:0x8000])
            outcomes.append((regs,low,[bytes(z)for z in m.ram],m.rawtags[:],m.chr_latches[:]))
        assert outcomes[0]==outcomes[1],('Existing owner item consumer changed',owner,alts,kind,state)
        digest.update(outcomes[0][1]);cases+=1
    return dict(passed=True,raw_owner_contexts=cases,byte_changes=changed,Karnov_owned_ROM_intervals=ranges,verified_private_callee_operand_relocations=relocations,trace_sha256=digest.hexdigest(),scope='All raw0..33 owners, both alternate-bit patterns and all4native types/immature+mature fixtures; Karnov alias7/odd excluded. Actual shared pickup consumers equal in registers/application RAM/RAMbanks/maps/CHR. Changed ROM outside owned leases is restricted to target immediates in three exact existing farcall templates for relocated private Karnov callees. This is not complete old-owner gameplay or every valid alternate admission.')

def emergence_checks(b):
    seed=cold(b);rows=[];observer=TransportObserver(b)
    for weapon in [0,2]:
        m=L.fork(seed);source_fixture(m,{0x65:weapon,0x68:0,0x69:37,0x860:0})
        object_fields(m,state=1,x=173,y=120)
        H.put(m,Player_X_Position=32,Player_PageLoc=0,Player_Y_Position=176,Player_Y_HighPos=1,Player_Rel_XPos=11,Player_Rel_YPos=176,Player_OffscreenBits=0,CrouchingFlag=0)
        call(m,'KrServiceVeneers',row=16)
        before=bytes(m.ram[2][:2048]);call(m,'UnionPwrUpCore',x=5,observer=observer)
        assert bytes(m.ram[2][:2048])==before
        expectedkind=int(bool(weapon));assert m[address(b,'PowerUpType')+5]==expectedkind
        miny=120;states=[];low=224
        for tick in range(100):
            H.put(m,FrameCounter=tick,CurrentOAMOffset=0,TimerControl=0)
            c,sp=call(m,'PowerUpObjHandler',x=5,observer=observer);low=min(low,sp)
            state=m[address(b,'Enemy_State')+5];y=m[address(b,'Enemy_Y_Position')+5]
            states.append((tick,state,y));miny=min(miny,y)
            assert bytes(m.ram[2][:2048])==before,'Emergence automatically collected a powerup'
            assert m[address(b,'Enemy_Flag')+5]==1,('Unexpected native object removal',weapon,tick,state,y,observer.events[-5:])
            if state&128:break
        else:raise AssertionError(('Actual visible emergence did not finish',states[-5:]))
        assert miny==103 and states[-1][1]&128,('Preserved native17-pixelrise',states[-5:],miny)
        # A real body bounding box overlaps the emerged object; the native
        # handler must route contact through RemainingNormalPlayerCollision,
        # HandlePowerUpCollision and the authenticated collection service.
        x=m[address(b,'Enemy_X_Position')+5];y=m[address(b,'Enemy_Y_Position')+5]
        H.put(m,Player_X_Position=x,Player_PageLoc=0,Player_Y_Position=y,Player_Y_HighPos=1,Player_Rel_XPos=(x-21)&255,Player_Rel_YPos=y,Player_State=0,Player_OffscreenBits=0,InjuryTimer=0,FrameCounter=100,TimerControl=0)
        call(m,'KrServiceVeneers',row=16)
        for t in range(4):
            H.put(m,FrameCounter=100+t,CurrentOAMOffset=0)
            c,sp=call(m,'PowerUpObjHandler',x=5,observer=observer);low=min(low,sp)
            if not m[address(b,'Enemy_Flag')+5]:break
        assert not m[address(b,'Enemy_Flag')+5],('Actual emerged-body contact did not collect',weapon,x,y)
        if weapon==0:assert m.ram[2][0x65]==1
        else:assert m.ram[2][0xbd]==1 and m.ram[2][0x8f]&1 and m.ram[2][0x860]==1
        assert H.get(m,'Square2SoundQueue')==32 and m[address(b,'FloateyNum_Control')+5]==6
        rows.append(dict(source_weapon=weapon,item_type=expectedkind,emergence_updates=len(states),rise_pixels=120-miny,contact_updates=t+1,minimum_SP=low,final_source65=m.ram[2][0x65],boots_stock=m.ram[2][0xbd]))
    return dict(passed=True,cases=rows,actual_service_calls=dict(observer.counts),scope='Real UnionPwrUpCore and unchanged nativePowerUpObjHandler perform their17-pixelvisible emergence without an award; moving the declared player/body coordinate fixture into contact executes native collision and authenticated collection. No executable overlay, controller-earned block hit or native emulator video claim.')

def main_checks(b):
    m=C.fresh(b);H.put(m,CrossoverMenuIndex=7)
    for name in ['MenuResolveCharacter','QueueSelection']:C.invoke(m,name)
    H.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0)
    C.invoke(m,'CrossoverMenuInput');C.invoke(m,'DrawSelectionPreview');assert H.get(m,'SelectedCharacter')==34
    H.put(m,SavedJoypad1Bits=16,SavedJoypad2Bits=0);C.invoke(m,'GameMenuRoutine');C.invoke(m,'PauseRoutine',a=0)
    minimum=224;total=0;normal_NMIs=0;saved=[];summaries=[]
    def step(keys=0,keep=False):
        nonlocal minimum,total,normal_NMIs
        H.put(m,SavedJoypadBits=keys,SavedJoypad1Bits=keys,SavedJoypad2Bits=0,A_B_Buttons=keys&192,Left_Right_Buttons=keys&3,Up_Down_Buttons=keys&12,NmiDisable=255)
        m.writes.clear();m.ram_writes.clear();m.ppu_log.clear();origin=C.fork(m)
        observer=TransportObserver(b);c,low=call(m,'GameLoop',observer=observer);minimum=min(minimum,low)
        assert not observer.live
        names={e[0]for e in observer.events}
        if 'KrPickupPrepareBody'in names:names.add('KrPickupPrepare')
        if keep or names&{'KrPickupPrepare','KrPickupCollect'}:
            saved.append((origin,C.fork(m),observer,(c.a,c.x,c.y,c.p,c.sp),total))
            summaries.append(dict(Main=total,input=keys,minimum_SP=low,minimum_instruction=dict(zip(['SP','step','PC','bank'],observer.low)),events=observer.events,source65=m.ram[2][0x65],source68=m.ram[2][0x68]))
        C.consume(m);normal_NMIs+=1;total+=1
        return names
    for setup in range(600):
        if H.get(m,'OperMode_Task')==3 and H.get(m,'GameEngineSubroutine')==8:break
        step()
    else:raise AssertionError('Actual Select/Start/parser bound')
    for _ in range(5):step()
    H.put(m,CheatInvincible=1) # declared route fixture; item source state untouched
    def worldx():return H.get(m,'Player_X_Position')+256*H.get(m,'Player_PageLoc')
    for walk in range(360):
        if worldx()>=328:break
        step(1)
    else:raise AssertionError(('First-block approach bound',worldx()))
    for _ in range(2):step()
    spawned=False
    for jump in range(50):
        names=step(128 if jump<22 else 0)
        if 'KrPickupPrepare'in names:spawned=True;break
    assert spawned,('Controller head-hit did not spawn first native block',worldx(),H.get(m,'Player_Y_Position'))
    collected=False
    for follow in range(180):
        slots=[i for i in range(6)if m[address(b,'Enemy_Flag')+i]and m[address(b,'Enemy_ID')+i]==46]
        if not slots:
            if m.ram[2][0x65]==1:collected=True;break
            raise AssertionError(('Native item vanished without earned source upgrade',follow,worldx()))
        slot=slots[0];itemx=m[address(b,'Enemy_X_Position')+slot]+256*m[address(b,'Enemy_PageLoc')+slot]
        target=min(itemx-8,414)
        keys=1 if worldx()<target-1 else 2 if worldx()>target+1 else 0
        names=step(keys)
        if 'KrPickupCollect'in names:collected=True;break
    assert collected and m.ram[2][0x65]==1 and m.ram[2][0x68]==0,('Controller-earned first mushroom',collected,m.ram[2][0x65],m.ram[2][0x68])
    # Source earned-triple and Kmark counter are declared state fixtures for
    # the deepest option branch. The actual Main object/collision consumer,
    # authenticated transport, source grant and native effects remain real.
    source_fixture(m,{0x65:2,0x68:0,0x69:37,0x860:9,0xba:0x49,0x40b:0x99})
    slot=5
    for n,v in [('Enemy_Flag',1),('Enemy_ID',46),('Enemy_State',128),('PowerUpType',1),('Enemy_PageLoc',H.get(m,'Player_PageLoc')),('Enemy_X_Position',H.get(m,'Player_X_Position')),('Enemy_Y_HighPos',1),('Enemy_Y_Position',H.get(m,'Player_Y_Position')),('Enemy_BoundBoxCtrl',3),('Enemy_SprAttrib',0)]:m[address(b,n)+slot]=v
    names=step(0,keep=True)
    assert 'KrPickupGrantOption'in names and m.ram[2][0x860]==0 and m.ram[2][0xba]==0,('Actual Main deepest option grant',names,m.ram[2][0x860],m.ram[2][0xba])
    previous=V.pending_store
    def pending(mem,c,slot,op):
        if previous(mem,c,slot,op):return True
        reg=0x5115 if slot==1 else 0x5116;value={0x8d:c.a,0x8e:c.x,0x8c:c.y}.get(mem[c.pc])
        return value is not None and bytes(mem[c.pc+1:c.pc+3])==reg.to_bytes(2,'little')and value==H.get(mem,'CurrentBank'if slot==1 else'CurrentBankC')
    V.pending_store=pending
    def fg(mem):
        fields=['Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','Player_State','Player_X_Scroll','Player_Pos_ForScroll','Player_Y_Speed','Player_X_Speed','FrameCounter','CurrentBank','CurrentBankC']
        return [bytes(z)for z in mem.ram],bytes(mem[0x200:0x300]),bytes(mem[3:11]),bytes(mem[0x15a:0x17b]),mem.rawtags[:],[H.get(mem,n)for n in fields]
    interrupt_rows=[];minimum_ISR=255
    for origin,expected,observer,regs,frame in saved:
        cuts={observer.low[1]}
        for name,at,sp,tag in observer.events:
            if name in ['SetupPowerUp','KrPickupPrepare','KrPickupPrepareBody','KrPickupCollect','KrPickupSuperFireball','KrPickupGrantOption']:cuts.add(at)
        for cut,kind in itertools.product(sorted(cuts),['IRQ','NMI']):
            z=C.fork(origin);events=[]
            def interrupt(mem,c,i):
                if i==cut:
                    foreground=dict(PC=c.pc,SP=c.sp,bank=mem.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else None)
                    events.append(dict(foreground=foreground,**V.interrupt(mem,c,kind)))
            c,low=call(z,'GameLoop',observer=interrupt)
            assert(c.a,c.x,c.y,c.p,c.sp)==regs and fg(z)==fg(expected),('Main pickup ISR resumption',frame,cut,kind,events)
            assert len(events)==1
            minimum_ISR=min(minimum_ISR,events[0]['minimum_SP']);interrupt_rows.append(dict(Main=frame,cut=cut,**events[0]))
    return dict(passed=minimum_ISR-0x7b>=12,real_Select_Start=True,source_code_loaded_from_ROM=True,total_Main_updates=total,setup_Main=setup,normal_NMIs=normal_NMIs,controller_earned_block_spawn=True,controller_earned_mushroom=True,invincibility_route_fixture=True,deepest_option_state_fixture=True,minimum_Main_SP=minimum,minimum_Main_ISR_SP=minimum_ISR,reserve_above_SMC=minimum_ISR-0x7b,actual_Main_ISR_cases=len(interrupt_rows),Main_events=summaries,interrupts=interrupt_rows,scope='Real Select/Start/native parser/Main/NMI. D-pad/A head-hit the first actual1-1question block, native item rises and is collected through real body contact; route invincibility is a declared cheat fixture. An earned-triple/Kmark-counter/object fixture exercises deepest actual Main option contact. IRQ/lagNMI cuts at real spawn/pickup/grant/minimum-stack instructions restore allforeground state/SMC/maps; passing requires12-byte SMC reserve. Native emulator/video/acoustic/full-stage qualification is separate.')
def capture():
    assert sha(BASE/'candidate.nes')==OLD
    target=O/'old-base';target.mkdir(parents=True,exist_ok=True)
    for n in ['candidate.nes','candidate.dbg']:shutil.copyfile(BASE/n,target/n)
    assert sha(target/'candidate.nes')==OLD
    q=dict(passed=True,old_ROM_sha256=OLD,old_DBG_sha256=sha(target/'candidate.dbg'),scope='Single exact pre-pickup ROM/DBG pair authorized by root for actual old-owner differential; no source tree/archive copy')
    (O/'baseline.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))
def main():
    p=argparse.ArgumentParser();p.add_argument('--capture-baseline',action='store_true');p.add_argument('--expected');p.add_argument('--only',default='core');args=p.parse_args()
    if args.capture_baseline:capture();return
    assert args.expected and sha(BASE/'candidate.nes')==args.expected,'Exact terminal composed candidate required'
    q=dict(passed=False,ROM_sha256=args.expected,no_code_overlay=True,native_emulator=False,installed=False)
    try:
        assert sha(ROM)==EXPECTED and sha(O/'old-base/candidate.nes')==OLD
        b=H.C.qualified(BASE/'candidate.nes')
        if 'core'in args.only.split(','):q['core'],_=core_checks(b,args.expected)
        if 'old'in args.only.split(','):q['old_owners']=old_owner_checks(H.C.qualified(O/'old-base/candidate.nes'),b)
        if 'emergence'in args.only.split(','):q['emergence']=emergence_checks(b)
        if 'main'in args.only.split(','):
            q['Main']=main_checks(b)
            assert q['Main']['passed'],('Actual pickup Main ISR12-byte reserve',q['Main']['minimum_Main_ISR_SP'],q['Main']['reserve_above_SMC'])
        q['passed']=True
    except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
    q['bindings']={str(x.resolve()):sha(x)for x in [Path(__file__),BASE/'candidate.nes',BASE/'candidate.dbg',BASE/'terrain-assembly.json',ROM,O/'old-base/candidate.nes',O/'old-base/candidate.dbg']}
    (O/('composed-'+args.only.replace(',','-')+'.json')).write_text(json.dumps(q,indent=2)+'\n')
    shown={k:v for k,v in q.items()if k not in ['bindings','traceback']}
    if 'Main'in shown:shown['Main']={k:v for k,v in shown['Main'].items()if k not in ['Main_events','interrupts']}
    print(json.dumps(shown));assert q['passed'],q.get('error')
if __name__=='__main__':main()
