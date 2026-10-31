"""Real dfdb-derived Bowser split loader/row/retire CPU+mapper/PPU checks, no preload."""
from pathlib import Path
import copy,hashlib,itertools,json,re,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import ff_wram_host_controls_v7 as H
import ff_host_pickups_vectors_v2 as V
from arthur_cache_host_controls_v1 import OverlayMemory
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
O=R/'build/bowser-split-workers-v2';J=O/'joint'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def make(b,**extra):
    m=OverlayMemory(b)
    for i in range(4):m.ram[i][:]=bytes(((j*17+i*29+13)&255)for j in range(8192))
    H.put(m,CurrentBank=m.rawtags[1],CurrentBankC=m.rawtags[2],SelectedCharacter=27,
        OperMode=1,DisableScreenFlag=1,Mirror_PPUMASK=0,Mirror_PPUCTRL=160,NmiDisable=255,
        FamilyMainCommit=1,NumberofLives=2,AreaType=1,AreaAddrsLOffset=0,WorldNumber=0,
        Player_Y_Position=160,Player_Y_HighPos=1,Player_X_Position=120,Player_PageLoc=0,
        PlayerFacingDir=1,PlayerOutlinesOff=1,GameEngineSubroutine=8,GamePauseStatus=0,
        VRAM_Buffer_AddrCtrl=0,VRAM_Buffer1_Offset=0,VRAM_Buffer2_Offset=0,GuestAudioCharacter=0,
        CurrentOAMOffset=0,GuestOamRotationActive=0,RgOamRotation=0,X5WideChrActive=0,
        SsChrActive=0,InvHudActive=0,X5SpecialChrUpper=0,X5HudChrUpper=0,
        HorizontalScroll=73,VerticalScroll=32,ReloadCHRBank=1)
    for i in range(12):m[address(b,'CurrentCHRBank')+i]=20+i;m[address(b,'X5ChrMode')+i]=0
    H.put(m,R0=165,R1=90,**extra);m.ppuctrl=H.get(m,'Mirror_PPUCTRL')
    m.writes.clear();m.ram_writes.clear();return m


def fork(m):
    z=OverlayMemory(m.bundle)
    list.__setitem__(z,slice(None),list.__getitem__(m,slice(None)))
    for k,v in vars(m).items():setattr(z,k,v if k=='bundle'else copy.deepcopy(v))
    z.writes.clear();z.ram_writes.clear();return z


def flags(value):return 0x30|sum(bit for i,bit in enumerate([1,2,4,8,64,128])if value>>i&1)


def call(m,name,slot=None,**kw):
    c=H.start(m,name,**kw)
    if slot is not None:
        pc=address(m.bundle,name)+slot*3
        m[address(m.bundle,'FarcallJmpTarget_SMC')+1]=pc&255
        m[address(m.bundle,'FarcallJmpTarget_SMC')+2]=pc>>8
    c,low=H.finish(m,c)
    assert c.sp==kw.get('sp',224)
    return c,low


def main():
    out=O/'loader-controls.json';assert not out.exists()
    q=dict(passed=False,source_CPU=True,native=False,no_RAM3_preload=True,host_menu_and_Main_unmodified=True)
    try:
        b=H.C.qualified(J/'candidate.nes');image=(J/'bowser.bin').read_bytes();cookie=(J/'bowser/cookie.bin').read_bytes()
        expected=bytearray(image);expected[0x1fe0:0x1ff0]=cookie
        loader=[];seed=None
        for wide,reload,ctrl in itertools.product([0,1],[0,1],[128,160,164]):
            m=make(b,X5WideChrActive=wide,ReloadCHRBank=reload,Mirror_PPUCTRL=ctrl)
            for i in range(12):m[address(b,'CurrentCHRBank')+i]=(868+i)&255;m[address(b,'X5ChrMode')+i]=131 if i%2 else 0
            H.invoke(m,'X5PublishChr');checkpoint=m.chr_latches[:]
            before=bytes(m[0x5c00:0x8000]);foreign=[bytes(x)for x in m.ram[:3]]
            m.writes.clear();m.ram_writes.clear();nr=m.ppu_reads
            c,low=call(m,'BwLoad')
            assert c.p&1 and(c.a,c.x,c.y)==(85,7,91)
            assert c.p&0xce==0x71&0xce
            assert m.ram[3]==expected and[bytes(x)for x in m.ram[:3]]==foreign
            assert bytes(m[0x5c00:0x8000])==before
            assert m.ram_writes[0]==(3,0x1fe0,0)and m.ram_writes[-1]==(3,0x1fe0,167)
            assert m.ppu_reads-nr==16400
            assert m.chr_latches==checkpoint and m.upper==0 and m.ppuctrl==ctrl and m.toggle==0
            assert m.ppu_log[-2:]==[(0x2005,73),(0x2005,32)]
            assert H.get(m,'ReloadCHRBank')==reload and m.protection==[2,1]
            assert not any(a in[0x5102,0x5103,0x5113]for a,v in m.writes)
            nr=m.ppu_reads;nw=len(m.ram_writes);cw,_=call(m,'BwLoad')
            assert cw.p&1 and m.ppu_reads==nr and len(m.ram_writes)==nw
            loader.append(dict(wide=wide,reload=reload,CTRL=ctrl,CPU=c.processorCycles,warmCPU=cw.processorCycles,minimum_SP=low))
            if seed is None:seed=fork(m)
        negative=[]
        for n,values in [('foreign',dict(SelectedCharacter=0)),('FFowner',dict(SelectedCharacter=22)),
            ('title',dict(OperMode=0)),('active',dict(DisableScreenFlag=0)),('mask',dict(Mirror_PPUMASK=30)),
            ('normalNMI',dict(NmiDisable=0)),('notbusy',dict(FamilyMainCommit=0))]:
            m=make(b,**values);old=bytes(m.ram[3]);c,_=call(m,'BwLoad')
            assert not c.p&1 and bytes(m.ram[3])==old and m.ppu_reads==0
            negative.append(n)
        for n,locked,corrupt in [('locked',True,None),('verify',False,(3,17))]:
            m=make(b);m.protection=[0,0]if locked else[2,1];m.corrupt_at=corrupt
            c,_=call(m,'BwLoad');assert not c.p&1 and m.ram[3][0x1fe0]!=167
            negative.append(n)
        checks=[]
        for bad in [-1]+list(range(16)):
            m=fork(seed)
            if bad>=0:m.ram[3][0x1fe0+bad]^=1
            for f in range(64):
                z=fork(m);c,_=call(z,'BwCheck',p=flags(f))
                assert(c.a,c.x,c.y,c.sp)==(85,7,91,224)
                assert c.p&0xcf==(flags(f)&0x4c)|(int(bad<0))
                assert not z.ram_writes
                checks.append([bad,f,bool(c.p&1)])
        routes=[]
        for valid,slot,f in itertools.product([0,1],range(37),[0,63]):
            m=fork(seed)
            if not valid:m.ram[3][0x1fe0]=0
            hits=[];c=H.start(m,'BwServiceVeneers',p=flags(f))
            pc=address(b,'BwServiceVeneers')+3*slot
            m[address(b,'FarcallJmpTarget_SMC')+1]=pc&255;m[address(b,'FarcallJmpTarget_SMC')+2]=pc>>8
            def observe(mem,c,step):
                if 0xa000<=c.pc<0xc000 and mem.rawtags[1]==3:hits.append(c.pc)
            c,low=H.finish(m,c,observe)
            assert c.sp==224 and m.rawtags[1]==seed.rawtags[1] and m.rawtags[2]==seed.rawtags[2]
            assert bool(hits)==bool(valid and slot<36),(valid,slot,hits[:4])
            if hits:assert hits[0]==address(b,'BwCacheServices')+slot*3
            if valid:assert not c.p&1
            else:assert not c.p&1 and(c.a,c.x,c.y)==(85,7,91)
            routes.append(dict(valid=valid,slot=slot,flags=f,CPU=c.processorCycles,minimum_SP=low,cache_instructions=len(hits)))
        retire=[]
        for family in [0,9,22,27,32,33]:
            m=fork(seed);m.ram[3][0x1fe1]=family;old=[bytes(x)for x in m.ram]
            call(m,'BwRetire')
            assert m.ram[3][0x1fe0]==(0 if family==27 else 167)
            assert[bytes(x)for x in m.ram[:3]]==old[:3]
            retire.append(family)
        q.update(passed=True,cold_loader_cases=len(loader),loader=loader,reject_cases=negative,
            full64flags_all16cookie_byte_pairs=len(checks),checks=checks,typed_row_pairs=len(routes),routes=routes,
            actual_Raw3_source_constructor=False,all36_services_explicitly_decline=True,retirement_families=retire,all_existing62_code_header_menu_CHR_outside_owned_spans_exact=True,
            limit='Actual split native-imported loader/typedROMrow/retire only; all36 services decline, genuine physics source remains separate until native contacts join; no cold menu/Main/admission claim')
    except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
    q['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),Path(H.__file__),Path(V.__file__),O/'source-stage.json',
        J/'candidate.nes',J/'candidate.dbg',J/'bowser.bin',J/'bowser/cookie.bin',J/'bowser/load.s',J/'bowser/router.s']}
    out.write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['loader','checks','routes','bindings','traceback']}));assert q['passed'],q.get('error')


if __name__=='__main__':main()
