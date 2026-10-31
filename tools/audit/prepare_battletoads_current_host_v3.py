"""BT-owned dfdb source leaf: actual cartridge cold loader/cache, still pending."""
from pathlib import Path
import hashlib, json, re, shutil, subprocess, sys

R=Path(__file__).resolve().parents[2]
P=R/'build/coherent62-lives-fixes-v1'
O=R/'build/battletoads-current-host-v3'
J=O/'joint'
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)


def command(c,name):
    v=validate(c,J,cwd=R)
    z=subprocess.run(c,cwd=R,text=True,capture_output=True)
    write(O/(name+'.json'),json.dumps(dict(command=c,validated_outputs=v,returncode=z.returncode,
        stdout=z.stdout,stderr=z.stderr),indent=2)+'\n')
    assert z.returncode==0,(name,z.stderr)


def preflight():
    h=P/'handoff.json'
    assert sha(h)=='fae1ec38db9525a645a8907fd92608978de15f0f7cf4b12088cee0e0f0393a1c'
    # The exact authoritative hash above is checked before any source copy.
    raw=(P/'joint/candidate.nes').read_bytes()
    assert sha(P/'joint/candidate.nes')=='dfdb194ac73438ae8deb05b5fc93f241b1109d45a84b3ad333d0e632008d7fc7'
    segs=[];aliases=[]
    for l in (P/'joint/candidate.dbg').read_text().splitlines():
        if not l.startswith(('seg\t','sym\t')):continue
        d=dict(re.findall(r'(\w+)=("[^"]*"|[^,]+)',l.split('\t',1)[1]))
        if l.startswith('seg\t') and d.get('oname','').endswith('candidate.nes"') and 'ooffs'in d:
            segs.append(dict(name=d['name'].strip('"'),start=int(d['ooffs']),end=int(d['ooffs'])+int(d['size'],0)))
        if l.startswith('sym\t') and 'val'in d and 'seg'not in d:aliases.append(d)
    spans=[]
    for bank,a,b in [(93,0xdc0,0xfa7),(87,0x1020,0x1100),(72,0x1011,0x1100)]:
        start,end=16+bank*8192+a,16+bank*8192+b
        hit=[x for x in segs if x['start']<end and start<x['end']]
        abs_alias=[x for x in aliases if any(base+a<=int(x['val'],0)<base+b for base in [0xa000,0xc000])]
        assert not hit and not abs_alias,(bank,hit,abs_alias)
        data=raw[start:end];assert set(data)=={255}
        spans.append(dict(physical_bank=bank,first_offset=a,end_offset_exclusive=b,bytes=b-a,
            preimage_sha256=hashlib.sha256(data).hexdigest(),live_segments=hit,absolute_aliases=abs_alias))
    a,b=16+0x100000+915*1024,16+0x100000+927*1024
    assert set(raw[a:b])=={0} and not[x for x in segs if x['start']<b and a<x['end']]
    return dict(status='ROOT_GRANTED_PRIVATE_BT_PARTITION_VERIFIED_ON_ACTUAL_DFDB',
        authority='Root message: selected RAM3 family33 and CHR915..<927 approved; exactly three Quick retained unemitted ranges partitioned to BT after current closure; no widening/global RAM/native grant.',
        parent_ROM=sha(P/'joint/candidate.nes'),parent_handoff=sha(h),ROM=spans,
        CHR=dict(first=915,body_end=919,end_exclusive=927,preimage_sha256=hashlib.sha256(raw[a:b]).hexdigest()),
        RAM=dict(temporal_bank=3,family=33,new_global_RAM0_bytes=0,cookie='BFE0..<BFF0 A7/family33/version/fingerprint; invalid-first/valid-last',
            source_state='BEE0..<BF55',host_budget='BF60..<BFA0'),
        menu_variant=dict(address='Existing FmGroups',bit=5,owner='Battletoads only',
            conditional='CF toggle must preserve high3 bits; Start preserve20 onlyslot23; no menu edits in this loader stage'),
        source_consumer_closure='Actual final-ROM-linked DBG spans and all bankless numeric symbol aliases excluded from both A/C views; source-linked BT-only object added, all old public values/foreign bytes checked after link',
        preserve=['Benj901..<915 and own PRG62/state','all existing62 readiness/menu/art','FF/Ar/Quick caches/retirement','32KB header','5113/5102/5103'],
        bindings={str(p.resolve()):sha(p)for p in [h,P/'joint/candidate.nes',P/'joint/candidate.dbg',P/'joint/private.cfg',
            R/'build/battletoads-host-resource-proposal-v1/proposal.json',
            R/'docs/qa/checkpoints/2026-10-30/arthur-quick-private-allocation/root-review-and-reservations.json']})


MACRO='''
.macro BtFar Target,Mode
 sta SafecallA_SMC+1
 lda #<Target
 sta FarcallJmpTarget_SMC+1
 lda #>Target
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(Target)|$80)
 .if .xmatch({Mode},{jmp})
 jmp FarCallCommon
 .else
 jsr FarCallCommon
 .endif
.endmacro
'''


def sources():
    B=J/'bt';B.mkdir()
    source=(R/'build/battletoads-playable-core-v3/core.s').read_text()
    defined=set(re.findall(r'^([A-Za-z_][A-Za-z_0-9]*):',source,re.M))|set(re.findall(r'^([A-Za-z_][A-Za-z_0-9]*)\s*=',source,re.M))
    names={n:'BtSrc_'+n for n in defined if not n.startswith('Bt')}
    source=re.sub(r'\b[A-Za-z_][A-Za-z_0-9]*\b',lambda m:names.get(m[0],m[0]),source)
    write(B/'core.s',source)
    write(B/'art.s',(R/'build/battletoads-small-core-assets-v1/art.s').read_text())
    src=(P/'joint/loader.s').read_text()
    loader=src[src.index('FwCheck:'):src.index('; Actual area/life service19')]
    # FwRetire's owner22 conditional is not copied. BtRetire always retires
    # only a validated family33 cache before any new publication.
    x=loader.index('FwRetire:');y=loader.index('FwInvalidate:',x)
    loader=loader[:x]+loader[y:]
    loader=loader.replace('Fw','Bt').replace('cmp #22','cmp #33').replace('adc #$7d','adc #$97')
    loader=loader.replace('jsr X5PublishChr','BtFar X5PublishChr,jsr')
    loader=loader.replace('BtInvalidate:','BtRetire:\nBtInvalidate:')
    write(B/'loader.s','''
.setcpu "6502"
.macpack longbranch
.import SelectedCharacter,OperMode,DisableScreenFlag,NmiDisable
.import Mirror_PPUMASK,Mirror_PPUCTRL,HorizontalScroll,VerticalScroll
.import CurrentBank,CurrentBankC,ReloadCHRBank,X5PublishChr
.import FarCallCommon,FarcallJmpTarget_SMC,SafecallA_SMC
.importzp R0,R1
.export BtLoad,BtCheck,BtRetire,BtInvalidate,BtCookie
.export BtCopy256,BtVerify256,BtPublishCookie,BtMapPage,BtRestoreContext,BtRestorePPU
.segment "BT_ROM_LOADER"
'''+MACRO+loader+'''
BtCookie:.incbin "'''+(B/'cookie.bin').as_posix()+'''"
.assert *<=$afa7,lderror,"Exact BT487B Quick partition"
''')
    write(B/'cookie.bin', '')
    (B/'cookie.bin').write_bytes(bytes(16))
    # Each row JSR retains an exact3B table ABI. Router consumes only that
    # extra returnPC, checks the real16B cookie and tail-enters actual raw3.
    write(B/'router.s','''
.setcpu "6502"
.import BtCheck,BtCacheServices,FarCallCommon,FarcallJmpTarget_SMC
.import SafecallA_SMC,SafereturnA_SMC,NextBank_SMC
.export BtServiceVeneers,BtServiceUnavailable,BtRouter
.segment "BT_ROM_ROUTER"
BtServiceVeneers:
.repeat 36
 jsr BtRouter
.endrepeat
BtServiceUnavailable:clc
 rts
'''+MACRO+'''
BtRouter:
 php
 pha
 txa
 pha
 tya
 pha
 BtFar BtCheck,jsr
 bcc BtRouterBad
 tsx
 lda $0105,x                ; own rowJSR returnlo, after four saved bytes
 sec
 sbc #<(BtServiceVeneers+2)
 clc
 adc #<BtCacheServices
 sta FarcallJmpTarget_SMC+1
 lda #>BtCacheServices
 sta FarcallJmpTarget_SMC+2
 lda #3
 sta NextBank_SMC+1
 pla
 tay
 pla
 tax
 pla
 sta SafecallA_SMC+1
 pla
 sta SafereturnA_SMC+1       ; temporary sourceP, covered by real33B SMC ISR save
 pla
 pla                        ; consume ONLY own rowJSR frame
 lda SafereturnA_SMC+1
 pha
 lda SafecallA_SMC+1
 plp
 jmp FarCallCommon+3
BtRouterBad:
 pla
 tay
 pla
 tax
 pla
 sta SafecallA_SMC+1
 pla
 and #$fe
 sta SafereturnA_SMC+1
 pla
 pla
 lda SafereturnA_SMC+1
 pha
 lda SafecallA_SMC+1
 plp
 rts
.assert *<=$b100,lderror,"Exact BT224B Quick partition"
.assert >BtServiceVeneers=>(BtServiceVeneers+109),lderror,"RowJSR same-page subtract"
.assert .lobyte(BtCacheServices)=0,lderror,"Cache row offset exact"
''')
    api='''
.setcpu "6502"
.import BtInit,BtPhysicsStep,BtSrc_Object_RamSlotID_tmp
.importzp R0
.exportzp BtScriptPtr
BtScriptPtr=R0
.export BtState,BtHostCamera,BtHostTerrain,BtHostHit,BtSoundDeath
.export BtCacheServices,BtConstruct,BtCoreStep,BtHostReady,BtHostState,BtCacheInvalid
.segment "BT_CACHE_API"
BtCacheServices:
'''
    for i in range(36):api+=' jmp '+('BtConstruct'if i==15 else'BtCacheUnavailable')+'\n'
    api+='''
.segment "BT_CACHE_HOST"
BtConstruct:
 jsr BtInit
 lda #0
 ldx #63
BtClearHost:sta BtHostState,x
 dex
 bpl BtClearHost
 lda #1
 sta BtHostReady
 rts
BtCoreStep:
 stx BtSrc_Object_RamSlotID_tmp
 jmp BtPhysicsStep
; Explicit unimplemented host boundaries: this stage is only cold loading.
BtHostCamera:rts
BtHostTerrain:rts
BtHostHit:rts
BtSoundDeath:rts
BtCacheUnavailable:clc
 rts
.segment "BT_CACHE_STATE"
BtState:.res 117,0
.segment "BT_CACHE_HOST_STATE"
BtHostState:
BtHostReady:.res 64,0
.segment "BT_CACHE_INVALID_COOKIE"
BtCacheInvalid:.res 16,0
'''
    write(B/'api.s',api)
    # Temporary ROM-only placeholder export, NOT a claimed visible portrait.
    write(B/'preview.s','''
.setcpu "6502"
.export BtPortraitPending
.segment "BT_ROM_PREVIEW"
BtPortraitPending:clc
 rts
.assert *<=$b100,lderror,"Exact BT239B Quick partition"
''')
    (B/'stream.bin').write_bytes(bytes(8192))
    write(B/'stream.s','.segment "BT_STREAM"\n.incbin "'+(B/'stream.bin').as_posix()+'"\n.segment "BT_CHR"\n.incbin "'+(R/'build/battletoads-small-core-assets-v1/art.chr').as_posix()+'"\n')


def configure():
    p=J/'private.cfg';s=p.read_text()
    changes={
        'X5_NEW_5D:start=$a000,size=$fa7,type=ro,file=%O,fill=yes,fillval=$ff,bank=$5d;':
        'X5_NEW_5D:start=$a000,size=$dc0,type=ro,file=%O,fill=yes,fillval=$ff,bank=$5d;\n BT_ROM_LOADER_MEM:start=$adc0,size=$1e7,type=ro,file=%O,fill=yes,fillval=$ff,bank=$5d;',
        'X5_NEW_57: start=$a000, size=$2000, type=ro, file=%O, fill=yes, fillval=$ff, bank=$57;':
        'X5_NEW_57:start=$a000,size=$1020,type=ro,file=%O,fill=yes,fillval=$ff,bank=$57;\n BT_ROM_ROUTER_MEM:start=$b020,size=$e0,type=ro,file=%O,fill=yes,fillval=$ff,bank=$57;\n BT_57_TAIL:start=$b100,size=$f00,type=ro,file=%O,fill=yes,fillval=$ff,bank=$57;',
        'X5_NEW_48: start=$a000, size=$2000, type=ro, file=%O, fill=yes, fillval=$ff, bank=$48;':
        'X5_NEW_48:start=$a000,size=$1011,type=ro,file=%O,fill=yes,fillval=$ff,bank=$48;\n BT_ROM_PREVIEW_MEM:start=$b011,size=$ef,type=ro,file=%O,fill=yes,fillval=$ff,bank=$48;\n BT_48_TAIL:start=$b100,size=$f00,type=ro,file=%O,fill=yes,fillval=$ff,bank=$48;',
        'ROGUE_AUDIO_PAGES_8: load=X5_NEW_57,':'ROGUE_AUDIO_PAGES_8: load=BT_57_TAIL,',
        'ROGUE_AUDIO_PAGES_9: load=X5_NEW_48,':'ROGUE_AUDIO_PAGES_9: load=BT_48_TAIL,',
        'UNALLOCATED_CHR_MEM:start=$e1400,size=$1ec00,type=ro,fill=yes,file=%O,fillval=$00;':
        'BENJ_RETAINED_CHR_MEM:start=$e1400,size=$3800,type=ro,fill=yes,file=%O,fillval=$00;\n BT_CHR_MEM:start=$e4c00,size=$1000,type=ro,fill=yes,file=%O,fillval=$00;\n BT_STREAM_MEM:start=$e5c00,size=$2000,type=ro,fill=yes,file=%O,fillval=$00;\n UNALLOCATED_CHR_MEM:start=$e7c00,size=$18400,type=ro,fill=yes,file=%O,fillval=$00;'
    }
    for a,b in changes.items():assert s.count(a)==1,a;s=s.replace(a,b)
    memory=' BT_CACHE_MEM:start=$a000,size=$2000,bank=3,type=ro,file="'+(J/'bt/cache.bin').as_posix()+'",fill=yes,fillval=$ff;\n'
    s=s.replace('MEMORY {','MEMORY {\n'+memory,1)
    segments='''
 BT_ROM_LOADER:load=BT_ROM_LOADER_MEM,type=ro;
 BT_ROM_ROUTER:load=BT_ROM_ROUTER_MEM,type=ro;
 BT_ROM_PREVIEW:load=BT_ROM_PREVIEW_MEM,type=ro;
 BT_CHR:load=BT_CHR_MEM,type=ro;
 BT_STREAM:load=BT_STREAM_MEM,type=ro;
 BT_CACHE_API:load=BT_CACHE_MEM,type=ro,start=$a000;
 BT_CORE:load=BT_CACHE_MEM,type=ro;
 BT_ART_META:load=BT_CACHE_MEM,type=ro;
 BT_CACHE_HOST:load=BT_CACHE_MEM,type=ro;
 BT_CACHE_STATE:load=BT_CACHE_MEM,type=ro,start=$bee0;
 BT_CACHE_HOST_STATE:load=BT_CACHE_MEM,type=ro,start=$bf60;
 BT_CACHE_INVALID_COOKIE:load=BT_CACHE_MEM,type=ro,start=$bfe0;
'''
    assert 'SEGMENTS {'in s;s=s.replace('SEGMENTS {','SEGMENTS {\n'+segments,1)
    write(p,s)


def main():
    assert not O.exists()
    grant=preflight()
    shutil.copytree(P/'joint',J,ignore=shutil.ignore_patterns('*.o','candidate.nes','candidate.dbg','candidate.lbl','candidate.map'))
    for p in J.rglob('*'):
        if p.is_file()and p.suffix in ['.s','.inc','.cfg']:
            write(p,p.read_text().replace(str(P/'joint'),str(J)).replace((P/'joint').as_posix(),J.as_posix()))
    write(O/'root-grant-and-partition.json',json.dumps(grant,indent=2)+'\n')
    sources();configure()
    cc=R/'tools/Windows/cc65/bin'
    def assemble(name):command([str(cc/'ca65.exe'),'-g','-o',str(J/'bt'/f'{name}.o'),str(J/'bt'/f'{name}.s')],f'bt-{name}-build')
    for n in ['core','art','api','loader','router','preview','stream']:assemble(n)
    link=json.loads((P/'final-link.json').read_text())['command'][:]
    for flag in ['-o','-Ln','-C','-m','--dbgfile','--mapfile']:
        if flag in link:link[link.index(flag)+1]=str(J/Path(link[link.index(flag)+1]).name)
    if '--ld-args'in link:
        k=link.index('--ld-args')+1;v=link[k].split(',')
        for i in range(1,len(v),2):v[i]=str(J/Path(v[i]).name)
        link[k]=','.join(v)
    link += [str(J/'bt'/f'{n}.o')for n in ['core','art','api','loader','router','preview','stream']]
    command(link,'initial-link')
    cache=(J/'bt/cache.bin').read_bytes();assert len(cache)==8192 and cache[0x1fe0:0x1ff0]==bytes(16)
    cookie=bytes([0xa7,33,1,117])+hashlib.sha256(cache).digest()[:12]
    (J/'bt/cookie.bin').write_bytes(cookie);(J/'bt/stream.bin').write_bytes(cache)
    assemble('loader');assemble('stream');command(link,'final-link')
    assert (J/'bt/cache.bin').read_bytes()==cache
    from prepare_cv3_dmc_mirror import prepare
    prepare(R,J/'candidate.nes')
    raw=(J/'candidate.nes').read_bytes();base=(P/'joint/candidate.nes').read_bytes();assert len(raw)==len(base)
    allowed=[(16+bank*8192+a,16+bank*8192+b)for bank,a,b in [(93,0xdc0,0xfa7),(87,0x1020,0x1100),(72,0x1011,0x1100)]]
    allowed += [(16+0x100000+915*1024,16+0x100000+927*1024)]
    diffs=[i for i,(a,b)in enumerate(zip(base,raw))if a!=b]
    assert all(any(a<=i<b for a,b in allowed)for i in diffs), 'Unexpected foreign/header/mirror mutation'
    assert raw[:16]==base[:16]
    for name in ['ram3.bin','ff-cookie.bin','code.bin','data.bin']:assert sha(J/name)==sha(P/'joint'/name)
    def labels(p):return {m[2]:int(m[1],16)for l in p.read_text().splitlines()if(m:=re.fullmatch(r'al ([a-fA-F0-9]+) \.([^ ]+)',l))}
    old,new=labels(P/'joint/candidate.lbl'),labels(J/'candidate.lbl')
    assert all(n in new and new[n]==v for n,v in old.items()),'Old global symbol moved'
    q=dict(status='SOURCE_LINKED_BT_LOADER_AND_CORE_ONLY_PENDING_NATIVE_ADAPTERS',source=True,native=False,
        candidate=sha(J/'candidate.nes'),parent=sha(P/'joint/candidate.nes'),changed_bytes=len(diffs),
        existing62_readiness_menu_CHR_header_and_all_public_values_exact=True,
        original_core_cache_bytes=8192,code_loaded_through_real_buffered_PPU_path=True,
        host_stub_boundaries_and_ROM_preview_pending=True,shared_raw33_and_menu_variant_not_integrated=True,
        cold_loader_controls_pending=True,grant=str((O/'root-grant-and-partition.json').resolve()),
        bindings={str(p.resolve()):sha(p)for p in [Path(__file__),P/'handoff.json',O/'root-grant-and-partition.json',J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',J/'private.cfg',J/'bt/cache.bin',J/'bt/stream.bin',J/'bt/cookie.bin']+list((J/'bt').glob('*.s'))})
    write(O/'source-stage.json',json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))


if __name__=='__main__':main()
