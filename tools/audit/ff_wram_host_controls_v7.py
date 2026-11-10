"""Actual linked FF buffered loader/ROM preview/raw3 ABI; no RAM preload."""
from pathlib import Path
import copy,hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import ff_ram3_execution_controls_v2 as C
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
O=R/'build/final-fantasy-wram-host-v13'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(m,**v):C.put(m,**v)
def get(m,n):return C.get(m,n)


def make(b):
    m=C.make(b)
    for i in range(4):m.ram[i][:]=bytes(((j*17+i*29+13)&255)for j in range(8192))
    put(m,CurrentOAMOffset=0,GuestOamRotationActive=0,RgOamRotation=0,
        X5WideChrActive=0,SsChrActive=0,InvHudActive=0,X5SpecialChrUpper=0,X5HudChrUpper=0,
        HorizontalScroll=73,VerticalScroll=32,ReloadCHRBank=1)
    for i in range(12):m[address(b,'CurrentCHRBank')+i]=20+i;m[address(b,'X5ChrMode')+i]=0
    m[address(b,'R0')]=0xa5;m[address(b,'R1')]=0x5a
    m.writes.clear();m.ram_writes.clear();return m


def start(m,name,a=0x55,x=7,y=91,p=0x71,sp=224):
    pc=address(m.bundle,name)
    m[address(m.bundle,'SafecallA_SMC')+1]=a
    m[address(m.bundle,'FarcallJmpTarget_SMC')+1]=pc&255
    m[address(m.bundle,'FarcallJmpTarget_SMC')+2]=pc>>8
    c=NesMPU(memory=m,pc=address(m.bundle,'FarCallCommon'))
    c.a=((location(m.bundle,name)-16)//8192)|128;c.x=x;c.y=y;c.p=p;c.sp=sp;c.stPushWord(0x5aff)
    return c


def finish(m,c,hook=None):
    low=c.sp
    for step in range(500000):
        if c.pc==0x5b00:break
        if hook:hook(m,c,step)
        low=min(low,c.sp);assert m[c.pc]!=0,('actual linked BRK',hex(c.pc),m.rawtags)
        c.step()
    else:raise AssertionError(('actual bounded timeout',hex(c.pc),m.rawtags))
    return c,low


def invoke(m,name,hook=None,**kw):
    old=m.rawtags[:];c=start(m,name,**kw);live=bytes(m[0x101+c.sp+2:0x200])
    c,low=finish(m,c,hook)
    assert c.sp==kw.get('sp',224) and bytes(m[0x101+c.sp:0x200])==live
    assert m.rawtags[1]==old[1] and get(m,'CurrentBank')==old[1]
    assert m.rawtags[2]==old[2] and get(m,'CurrentBankC')==old[2]
    return c,low


def native_publish(m):
    return invoke(m,'X5PublishChr')


def expected_image():
    out=bytearray((O/'ram3.bin').read_bytes());out[0x1fe0:0x1ff0]=(O/'ff-cookie.bin').read_bytes();return out


def exact(m):
    assert m.ram[3]==expected_image(),'actual verified8KB RAM3/cookie differs'
    assert m.protection==[2,1]
    assert not any(a in[0x5102,0x5103,0x5113]for a,v in m.writes)


def loader(b):
    rows=[]
    for wide,reload,ctrl in itertools.product([0,1],[0,1],[0x80,0xa0,0xa4]):
        m=make(b);put(m,X5WideChrActive=wide,ReloadCHRBank=reload,Mirror_PPUCTRL=ctrl)
        m.ppuctrl=ctrl
        for i in range(12):
            m[address(b,'CurrentCHRBank')+i]=(868+i)&255
            m[address(b,'X5ChrMode')+i]=(0x83 if i%2 else 0)
        # Nonempty native pending packet is never serviced by the copy.
        for i,v in enumerate([0x20,0x40,3,1,2,3,0]):m[address(b,'VRAM_Buffer1')+i]=v
        put(m,VRAM_Buffer1_Offset=6)
        native_publish(m);expected=m.chr_latches[:]
        fields=bytes(m[0x5c00:0x8000]);foreign=[bytes(x)for x in m.ram[:3]]
        m.writes.clear();m.ram_writes.clear();reads=m.ppu_reads
        c,low=invoke(m,'FwLoad')
        assert c.p&1 and(c.a,c.x,c.y)==(0x55,7,91)
        assert c.p&0xce==0x71&0xce
        exact(m);assert [bytes(x)for x in m.ram[:3]]==foreign
        assert bytes(m[0x5c00:0x8000])==fields,'source/globalRAM0/queue changed by loader'
        assert m.ram_writes[0]==(3,0x1fe0,0)and m.ram_writes[-1]==(3,0x1fe0,167)
        assert m.ppu_reads-reads==16400,(m.ppu_reads-reads,'buffered copy+verify')
        assert m.chr_latches==expected and m.upper==0 and m.ppuctrl==ctrl and m.toggle==0
        assert m.ppu_log[-2:]==[(0x2005,73),(0x2005,32)]
        assert get(m,'ReloadCHRBank')==reload
        nr=m.ppu_reads;nw=len(m.ram_writes);cw,_=invoke(m,'FwLoad')
        assert cw.p&1 and m.ppu_reads==nr and len(m.ram_writes)==nw
        rows.append(dict(wide=wide,reload=reload,CTRL=ctrl,cycles=c.processorCycles,warm_cycles=cw.processorCycles,minimum_SP=low))
    negatives=[]
    for name,changes in [('foreign',dict(SelectedCharacter=0)),('title',dict(OperMode=0)),
       ('active',dict(DisableScreenFlag=0)),('mask',dict(Mirror_PPUMASK=30)),('normalNMI',dict(NmiDisable=0))]:
        m=make(b);put(m,**changes);image=bytes(m.ram[3]);c,_=invoke(m,'FwLoad')
        assert not c.p&1 and bytes(m.ram[3])==image and m.ppu_reads==0
        negatives.append(name)
    m=make(b);m.corrupt_at=(3,17);c,_=invoke(m,'FwLoad')
    assert not c.p&1 and m.ram[3][0x1fe0]!=167;negatives.append('readback-corruption')
    return dict(cases=len(rows),rows=rows,negative_cases=negatives,actual_buffered_copy_verify_bytes=8192,
       exact_published_checkpoint_12_windows=True,software_queue_R0_R1_globalRAM0_unchanged=True,
       cookie_invalid_first_valid_last=True,no_RAM_preload=True)


def routes(b):
    old=C.qualified(C.P/'candidate.nes');rows=[]
    for variant,keys in itertools.product(range(4),[0,1,64,129]):
        m=make(b);invoke(m,'FwLoad');put(m,FfVariant=variant,PlayerFacingDir=1,SavedJoypadBits=keys)
        ref=C.make(old);put(ref,FfVariant=variant,PlayerFacingDir=1,SavedJoypadBits=keys)
        C.run(ref,'FfEnsure');invoke(m,'FwEnsure')
        for i in range(16):
            a,_,_=C.run(ref,'FfMovement',a=0x55,x=7,y=91,p=0x71)
            z,_=invoke(m,'FwMovement',a=0x55,x=7,y=91,p=0x71)
            assert(a.a,a.x,a.y,a.p,a.sp)==(z.a,z.x,z.y,z.p,z.sp)
            assert bytes(m[0x5c00:0x5c80])==bytes(ref[0x5c00:0x5c80])
            assert bytes(m[0x5fc1:0x5fcf])==bytes(ref[0x5fc1:0x5fcf])
        exact(m);rows.append([variant,keys])
    renders=[]
    for entry,chunk,face in itertools.product([0,35,36,71,72,107,108,143,144,157],[0,1],[1,2]):
        m=make(b);invoke(m,'FwLoad');put(m,FfSlot=face)
        z,_=invoke(m,'FwRenderChunk',a=entry,x=chunk,y=3,p=0x71)
        r=C.make(old);put(r,FfSlot=face);a,_,_=C.run(r,'FfRenderChunk',a=entry,x=chunk,y=3,p=0x71)
        assert(a.a,a.x,a.y,a.p,a.sp)==(z.a,z.x,z.y,z.p,z.sp)
        assert bytes(m[0x5c00:0x5c80])==bytes(r[0x5c00:0x5c80]) and bytes(m[3:11])==bytes(r[3:11])
        # A separate poisoned pre-load path must use only real ROM preview.
        p=make(b);put(p,FfSlot=face);q=start(p,'FwPreviewChunk',a=entry,x=chunk,y=3,p=0x71)
        # ROM preview intentionally retains original source C=ROM93 contract.
        finish(p,q);assert p.rawtags[2]==0xdd
        assert bytes(p[0x5c00:0x5c80])==bytes(r[0x5c00:0x5c80])
        assert not p.ram_writes and p.ppu_reads==0
        renders.append([entry,chunk,face])
    return dict(movement_pairs=256,source_contexts=rows,render_and_preload_ROM_preview_pairs=len(renders),
        source_AXYP_SP_state_R0_R1_exact=True,raw_C_explicitly_restored=True)


def lifecycle(b):
    m=make(b);invoke(m,'FwLoad');rows=[]
    for variant in range(4):
        put(m,FfVariant=variant);before=m.ppu_reads;invoke(m,'FwLoad');assert m.ppu_reads==before
        invoke(m,'FwEnsure');assert get(m,'FfVariant')==variant
        rows.append(['class',variant,get(m,'FfReady')])
    put(m,FfPower=2,FfEarned=2,NumberofLives=1);invoke(m,'FwEnsure');assert get(m,'FfPower')==0
    put(m,FfPower=1,FfAction=2,AreaAddrsLOffset=1);invoke(m,'FwEnsure')
    assert get(m,'FfPower')==1 and get(m,'FfAction')==0;exact(m)
    # Per-player engine transposition is not integrated yet. Code/cookie is
    # class-independent; no claim of saving FF per-player gear is made here.
    put(m,SelectedCharacter=0);invoke(m,'FwRetire');assert m.ram[3][0x1fe0]==0
    put(m,SelectedCharacter=22);invoke(m,'FwLoad');exact(m)
    for i in range(16):
        m.ram[3][0x1fe0+i]^=1;c,_=invoke(m,'FwCheck');assert not c.p&1
        m.ram[3][0x1fe0+i]^=1
    invoke(m,'FwInvalidate');assert m.ram[3][0x1fe0]==0
    # Native InitScreen genuinely executes the selected loader and original
    # MoveAllSpritesOffscreen from a cold poisoned cache.
    m=make(b);c,_=invoke(m,'InitScreen');exact(m)
    assert get(m,'ScreenRoutineTask')==1 and m.ppu_reads==16400
    return dict(rows=rows,full_cookie_poison_cases=16,source_life_area_reset=True,
        actual_InitScreen_load=True,retirement_reentry=True,newgame_invalidate_API=True,
        two_player_limit='Current loader code readiness is class/player-independent; future native newgame/player/selection hooks and per-player FF gear/state integration remain root review work, not claimed here.')


def cold_portraits(b):
    old=C.qualified(C.P/'candidate.nes');rows=[]
    for variant,power,face,outlines in itertools.product(range(4),range(3),[1,2],[0,1]):
        ref=C.make(old);C.run(ref,'FfEnsure')
        put(ref,FfVariant=variant,FfPower=power,PlayerFacingDir=face,PlayerOutlinesOff=outlines,Player_SprAttrib=0xa3)
        C.run(ref,'FfPortrait')
        m=make(b);put(m,FfVariant=variant,FfPower=power,PlayerFacingDir=face,PlayerOutlinesOff=outlines,Player_SprAttrib=0xa3)
        source=bytes(m.ram[3]);ready=get(m,'FfReady');code=[]
        c,_=invoke(m,'FwPortrait',hook=lambda mem,cpu,i:code.append((cpu.pc,mem.rawtags[1]))if 0xa000<=cpu.pc<0xc000 else None)
        assert c.p&1 and m.ppu_reads==0 and not m.ram_writes and bytes(m.ram[3])==source
        assert not any(tag==3 for pc,tag in code),'Cold portrait executed unready RAM3'
        assert get(m,'FfReady')==ready,'Display initialized gameplay source readiness'
        fields=['ObjectMetasprite','SmPosePtr','FfRenderYOffset','FfRenderPage','SmChrBank','Player_SprAttrib','FfPose']
        for n in fields:assert get(m,n)==get(ref,n),(n,variant,power,face,outlines,get(m,n),get(ref,n))
        assert bytes(m[address(b,'SmPosePtr'):address(b,'SmPosePtr')+2])==bytes(ref[address(old,'SmPosePtr'):address(old,'SmPosePtr')+2])
        a=address(b,'FfRenderBuffer');r=address(old,'FfRenderBuffer')
        assert bytes(m[a:a+64])==bytes(ref[r:r+64]),('genuine cold descriptor',variant,power,face,outlines)
        assert bytes(m[3:5])==bytes(ref[3:5])
        rows.append([variant,power,face,outlines])
    m=make(b);put(m,FfVariant=4);c,_=invoke(m,'FwPortrait');assert not c.p&1 and get(m,'ObjectMetasprite')==0
    m=make(b);put(m,SelectedCharacter=0);before=bytes(m.ram[3]);c,_=invoke(m,'FwPortrait');assert not c.p&1 and bytes(m.ram[3])==before
    return dict(actual_public_preload_portrait_cases=len(rows),rows=rows,authentic_first_chunk_and_native_attributes_exact=True,
        no_RAM3_execution_preload_or_PPU_reads=True,foreign_and_invalid_class_reject=True,
        limit='ROM portrait publishes original first chunk. Full body/optional ink and effects still require authentic iterator and aggregate native OAM ownership; no gameplay admission.')


def host_routes(b):
    import ff_host_combat_controls_v1 as K
    from ff_wram_host_isr_v4 import clone
    base=make(b);invoke(base,'FwLoad');invoke(base,'FwEnsure')
    put(base,TimerControl=0,MmDeathFlag=0,GamePauseStatus=0,ObjectOffset=4,
        ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,Player_State=0,
        CrossoverBehaviorVersion=1,Square1SoundQueue=0,Square2SoundQueue=0)
    for n in ['Enemy_Flag','Enemy_ID','Enemy_State','Enemy_X_Position','Enemy_PageLoc',
              'Enemy_Y_Position','Enemy_Y_HighPos','Enemy_BoundBoxCtrl',
              'MmEnemyHealthLo','MmEnemyHealthHi','MmEnemyFlash','FloateyNum_Control']:
        for i in range(6):K.setv(base,n,0,i)
    for i in range(address(b,'Block_Buffer_1'),address(b,'Block_Buffer_2')+208):base[i]=0
    names=['Movement','HeadWithin','Head','Feet','Side','Wall','AfterTerrain','Box','Adder','Target','Damage','Contact','Weapons','NewEnemy','Fresh','Collect','PowerupTick','Body','ImpulseAccepted']
    rows=[]
    exclude=set(range(0x100,0x200))|set(range(0x15a,0x17b))|set(range(0x5114,0x5118))
    for n,variant,flags in itertools.product(names,range(4),[0x30,0x71]):
        pair=[]
        for own in [False,True]:
            m,_=clone(base,start(base,'FwCheck'))
            put(m,FfVariant=variant,PlayerFacingDir=1+(variant&1),FfDamage=25,RgCrouch=variant&1,
                FfPower=variant%3,SavedJoypadBits=[0,1,64,129][variant],FfAction=1,
                FfTerrainPreviousY=160,FfTerrainFlags=0,FfTerrainPage=0,
                R0=1,R1=0xa6,R6=address(b,'Block_Buffer_1')&255,R7=address(b,'Block_Buffer_1')>>8)
            K.actor(m,x=0,px=144,y=160)
            if n=='Collect':
                K.actor(m,x=0,kind=address(b,'PowerUpObject'),px=144,y=160,state=0x80)
                put(m,PowerUpType=variant)
            if n=='PowerupTick':put(m,GameEngineSubroutine=9,GuestPowerupActive=1,GuestPowerupAge=58,GuestPowerupOld=0,GuestPowerupTarget=2,GuestPowerupDisplay=1)
            m.writes.clear();m.ram_writes.clear()
            kw=dict(a=0xff if n=='Contact'else 0x55,x=0,y=0,p=flags)
            if own:c,_=invoke(m,'FwHost'+n,**kw)
            else:c,_,_=C.run(m,'FfHost'+n,True,**kw)
            state=bytes(m[i]for i in range(0x8000)if i not in exclude)
            writes=[(a,v)for a,v in m.writes if a not in exclude and a not in [address(b,'CurrentBank'),address(b,'CurrentBankC')]]
            pair.append((state,writes,(c.a,c.x,c.y,c.p,c.sp),m.rawtags[:],m.ram[3][:]))
            exact(m)
        assert pair[0]==pair[1],('source linked host gate differs',n,variant,flags)
        rows.append([n,variant,flags])
    return dict(actual_loader_initialized_host_pairs=len(rows),entries=names,rows=rows,
        original143sourcebytes_native_state_ordered_application_stores_AXYP_SP_R0_R1_exact=True,
        all33SMC_are_transport_contract_not_callee_state=True,
        limit='These are real linked typed gates. Actual common selector/Main/BG/combat hooks are not installed; native admission remains pending.')


def host_graphics(b):
    from ff_wram_host_isr_v4 import clone
    base=make(b);invoke(base,'FwLoad');invoke(base,'FwEnsure');rows=[]
    for variant,power,face,frozen in itertools.product(range(4),range(3),[1,2],[0,1]):
        pair=[];maps=[]
        for own in [False,True]:
            m,_=clone(base,start(base,'FwCheck'))
            put(m,FfVariant=variant,FfPower=power,PlayerFacingDir=face,GuestPowerupActive=frozen,
                GuestPowerupDisplay=1,GameEngineSubroutine=9 if frozen else 8,Player_X_Speed=0)
            if own:c,_=invoke(m,'FwHostGraphics',a=0x55,x=0,y=0,p=0x71)
            else:c,_,_=C.run(m,'FfHostGraphics',True,a=0x55,x=0,y=0,p=0x71)
            pair.append(((c.a,c.x,c.y,c.p,c.sp),bytes(m[0x5c00:0x5c80]),bytes(m[0x5fc1:0x5fcf]),bytes(m[3:11]),get(m,'SmChrBank'),get(m,'ObjectMetasprite')))
            maps.append((m.rawtags[2],get(m,'CurrentBankC')));exact(m)
        assert pair[0]==pair[1] and maps==[(0xdd,0xdd),(0xd8,0xd8)],('host graphics descriptor/C contract',variant,power,face,frozen,maps)
        rows.append([variant,power,face,frozen])
    return dict(actual_source_graphics_pairs=len(rows),rows=rows,source_acquired_power_restored=True,
        AXYP_SP_source_descriptor_and_R0_R1_exact=True,direct_source_C93_vs_ROM_gate_restored_callerC_explicit=True)


def main():
    out=O/'loader-controls-v7.json';assert not out.exists()
    proof=dict(passed=False,native=False,RAM_preload=False,checks={})
    try:
        d=json.loads((O/'build-proof.json').read_text())
        for p,h in d['bindings'].items():assert sha(p)==h,p
        b=C.qualified(O/'candidate.nes')
        for name,fn in [('loader',loader),('routes',routes),('lifecycle',lifecycle),('cold_portraits',cold_portraits),('host_routes',host_routes),('host_graphics',host_graphics)]:
            proof['checks'][name]=fn(b);print('FF actual linked '+name+' PASS',flush=True)
        proof['passed']=True
    except Exception as e:proof.update(error=repr(e),traceback=traceback.format_exc())
    proof['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),O/'candidate.nes',O/'candidate.dbg',O/'build-proof.json',O/'ram3.bin',O/'ff-cookie.bin',Path(C.__file__)]}
    target=out if proof['passed']else O/'loader-controls-negative-v7.json';assert not target.exists()
    target.write_text(json.dumps(proof,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(passed=proof['passed'],error=proof.get('error'),path=str(target))))
    assert proof['passed']


if __name__=='__main__':main()
