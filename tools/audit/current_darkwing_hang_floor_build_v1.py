"""Sparse private falling-Arrow floor-release fix on frozen current5a; no native."""
from pathlib import Path
import configparser,difflib,hashlib,json,subprocess,sys

ROOT=Path(__file__).resolve().parents[2];BUILD=ROOT/'build';PREFIX='darkwing_hang_floor'
sys.path[:0]=[str(ROOT/'tools/audit'),str(ROOT/'tools')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from check_tmnt_audio_fallback_oc import qualified
from prepare_cv3_dmc_mirror import prepare

BASE=BUILD/'kirby-mike-polish-production.nes'
EXPECTED='5a0a37a97e95ce3c1086f91f6000ad0157bb477f923027d39f0342d9389e6db2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    existing='--qualify-existing'in sys.argv
    assert sha(BASE)==EXPECTED
    old=scoped_load(BASE);source={n:(ROOT/'src'/n).read_text()for n in ['darkwing_core.s','darkwing_recovery.s','darkwing.s']}
    target=source['darkwing_core.s'];token='  jsr DwValidateArrow\n  bcc Lost\n  lda ScFresh'
    assert target.count(token)==1;target=target.replace(token,'  jsr DwValidateHang\n  bcc Lost\n  lda ScFresh')
    helper='''; Holding must honor the native Arrow's terrain-release gate. A falling
; actor may continue carrying/hanging in free air; its state80 is set when
; DwArrowActor finds solid scenery so the native platform no longer carries
; a rider through that scenery. Stable jump-through state80 remains legal.
.proc DwValidateHang
  jsr DwValidateArrow
  bcc Done
  lda SsMode,x
  beq Owned
  lda Enemy_State,y
  bmi Released
Owned:
  sec
Done:
  rts
Released:
  clc
  rts
.endproc
'''
    recovery=source['darkwing_recovery.s'];assert recovery.count('.popseg')==1
    recovery=recovery.replace('.popseg',helper+'.popseg')
    overlay={}
    for name,text in [('darkwing_core.s',target),('darkwing_recovery.s',recovery)]:
        p=BUILD/(PREFIX+'_'+name)
        if existing:assert p.read_text()==text
        else:assert not p.exists();p.write_text(text,newline='\n')
        overlay[name]=p
    wrapper=source['darkwing.s']
    for n,p in overlay.items():
        inc='.include "'+n+'"';assert wrapper.count(inc)==1;wrapper=wrapper.replace(inc,'.include "'+p.name+'"')
    wp=BUILD/(PREFIX+'_darkwing.s')
    if existing:assert wp.read_text()==wrapper
    else:assert not wp.exists();wp.write_text(wrapper,newline='\n')
    ep=BUILD/(PREFIX+'_entrypoint.s');raw=(ROOT/'src/entrypoint.s').read_bytes();assert raw.count(b'.include "darkwing.s"')==1
    replacement=raw.replace(b'.include "darkwing.s"',('.include "'+wp.name+'"').encode())
    if existing:assert ep.read_bytes()==replacement
    else:ep.write_bytes(replacement)
    main=BUILD/(PREFIX+'_main.c')
    if existing:assert main.read_bytes()==(ROOT/'src/main.c').read_bytes()
    else:assert not main.exists();main.write_bytes((ROOT/'src/main.c').read_bytes())
    cfg=configparser.ConfigParser();cfg.optionxform=str;cfg.read(ROOT/'build_options.ini');defs={k:v for s in cfg.values()for k,v in s.items()}
    defs.update(MAPPER_MMC3='0',MAPPER_MMC5='1',ENABLE_CROSSOVER='1',ENABLE_MMC5_EXPANDED='1')
    def build(stem,mapper=None):
        options=dict(defs);layout='smb1base-mmc5-expanded.cfg'
        if mapper:
            options.update(ENABLE_MMC5_EXPANDED='0',MAPPER_MMC3=str(int(mapper=='mmc3')),MAPPER_MMC5=str(int(mapper=='mmc5')));layout='smb1base.cfg'
        out=BUILD/(stem+'.nes');assert not out.exists()or existing
        command=[str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--cpu','6502x','-t','nes','-g','-Oisr','-vm','-T','-C',str(ROOT/layout),'--ld-args','--dbgfile,'+str(out.with_suffix('.dbg')),'--include-dir',str(ROOT),'--asm-include-dir',str(BUILD),'--asm-include-dir',str(ROOT/'src'),'--asm-include-dir',str(ROOT),'--bin-include-dir',str(ROOT),'-m',str(out.with_suffix('.map')),'-Ln',str(out.with_suffix('.lbl')),'-o',str(out)]
        for k,v in options.items():command+=['--asm-define',k+'='+v,'-D',k+'='+v]
        command += [str(main),str(ep)]
        if out.exists():return out,command
        r=subprocess.run(command,cwd=ROOT,capture_output=True,text=True);out.with_suffix('.build.log').write_text(r.stdout+r.stderr)
        assert r.returncode==0,r.stdout+r.stderr
        if not mapper:prepare(ROOT,out)
        return out,command
    out,command=build(PREFIX);new=scoped_load(out)
    assert address(new,'DwValidateHang')==0xb218
    size=int(new['syms']['DwValidateHang']['size'],0);assert size==19
    start=location(new,'DwValidateHang');assert old['raw'][start:start+size]==b'\xff'*size
    call=location(old,'DwHangUpdate::Holding')
    # Exact JSR DwValidateArrow within the pre-existing Holding prologue.
    data=old['raw'][call:call+25];needle=bytes([0x20,address(old,'DwValidateArrow')&255,address(old,'DwValidateArrow')>>8]);assert data.count(needle)==1
    call+=data.index(needle);changes=[i for i,(x,y)in enumerate(zip(old['raw'],new['raw']))if x!=y]
    assert set(changes)<=set(range(call+1,call+3))|set(range(start,start+size))and len(changes)==21
    assert all((i-16)//8192==67 for i in changes)
    prior,after=qualified(BASE),qualified(out);moved={n:(v,after.get(n))for n,v in prior.items()if after.get(n)!=v and 'LOCAL-MACRO_SYMBOL-'not in n};assert not moved,moved
    ordinary={}
    for mapper,expected in [('mmc3','d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb'),('mmc5','f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833')]:
        f,cmd=build(PREFIX+'_'+mapper+'_flagoff',mapper);assert sha(f)==expected,(mapper,sha(f));ordinary[mapper]=dict(path=str(f),sha256=sha(f),command=cmd)
    patch=BUILD/(PREFIX+'.patch');patch.write_text(''.join(''.join(difflib.unified_diff(source[n].splitlines(True),overlay[n].read_text().splitlines(True),fromfile='current5a/src/'+n,tofile='private/src/'+n))for n in overlay),newline='\n')
    files=[Path(__file__).resolve(),BASE,BASE.with_suffix('.dbg'),BASE.with_suffix('.lbl'),ROOT/'smb1base-mmc5-expanded.cfg',ROOT/'build_options.ini',ROOT/'src/entrypoint.s',ROOT/'src/main.c',ep,main,wp,patch]+list(overlay.values())+[ROOT/'src'/n for n in source]
    z=dict(passed=True,source_only=True,native_run=False,installed=False,parent_sha256=EXPECTED,candidate_sha256=sha(out),candidate=str(out),changed_bytes=len(changes),changed_banks=[67],helper=dict(pc=address(new,'DwValidateHang'),size=size,original_FF_verified=True),existing_true_symbols_exact=True,all_other_ROM_header_CHR_RAM_NMI_audio_exact=True,ordinary_flagoff_whole_exact=ordinary,source_leaves={n:str(p)for n,p in overlay.items()},wrapper=str(wp),entrypoint=str(ep),command=command,deltas=[dict(offset=i,before=old['raw'][i],after=new['raw'][i])for i in changes],bindings={str(p):sha(p)for p in files})
    receipt=BUILD/(PREFIX+'_build.json');receipt.write_text(json.dumps(z,indent=2)+'\n',newline='\n');print(json.dumps(dict(candidate=sha(out),changed_bytes=len(changes),helper_bytes=size,receipt=str(receipt),receipt_sha256=sha(receipt))))

if __name__=='__main__':main()
