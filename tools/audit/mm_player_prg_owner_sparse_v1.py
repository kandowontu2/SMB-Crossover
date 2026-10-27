"""Sparse dynamic Mega/Proto player PRG-C ownership repair; never installs/runs."""
from pathlib import Path
import configparser
import difflib
import hashlib
import json
import subprocess
import sys

R=Path(__file__).resolve().parents[2];B=R/'build';PREFIX='mm_player_prg_owner'
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from prepare_cv3_dmc_mirror import prepare
from check_tmnt_audio_fallback_oc import qualified

BASE=B/'bill_early_cache.nes'
EXPECTED='9ea11eab2fc5c373a3795b013f6ed9e0d5e9781891b2ae3bf40ad2556c27b85e'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    existing="--qualify-existing"in sys.argv
    assert sha(BASE)==EXPECTED
    old=scoped_load(BASE);originals={n:(R/'src'/n).read_text()for n in ['metasprite_engine.s','megaman_weapons.s']}
    pointer=originals['metasprite_engine.s']
    token='    lda HpNativeDrawLo,y\n    sta Ptr\n  .res 5,$ea\n  :\n::HpNativePointerEnd:'
    assert pointer.count(token)==1
    pointer=pointer.replace(token,'    lda HpNativeDrawLo,y\n    sta Ptr\n .if ::ENABLE_MMC5_EXPANDED\n    jmp MmDynamicPlayerPrgOwner\n    .res 2,$ea\n .else\n    .res 5,$ea\n .endif\n  :\n::HpNativePointerEnd:')
    weapons=originals['megaman_weapons.s']
    marker='.assert *-MmReserveExit<=88,error,"Actual bank4 pool"'
    assert weapons.count(marker)==1
    helper='''.proc MmDynamicPlayerPrgOwner
  ; Taken indirect-pointer path only. Repair the actual player before its
  ; first record consumer (including outline filtering), never world actors.
  ; JMP entry/continuation adds no return-stack writes or new RAM ownership.
  cpy #0
  bne Done
  lda SelectedCharacter
  cmp #CHARACTER_MEGAMAN
  bne Done
  lda ProtoVariant
  beq Mega
  lda #.bank(ProtoArtBegin)|MMC5_PRG_ROM
  bne Publish
Mega:
  lda #.bank(SsMegaTHROWRight)|MMC5_PRG_ROM
Publish:
  BankPRGC a
Done:
  jmp HpNativePointerEnd
.endproc
'''
    weapons=weapons.replace(marker,helper+marker)
    at=16+4*8192+0x1f5a
    assert old['raw'][at:at+49]==b'\xff'*49
    end=location(old,'HpNativePointerEnd');assert old['raw'][end-5:end]==b'\xea'*5
    for name,d in old['syms'].items():
        if d.get('seg')==old['syms']['HpNativePointerEnd'].get('seg'):
            assert not address(old,'HpNativePointerEnd')-5<=int(d['val'],0)<address(old,'HpNativePointerEnd'),name
    for name in ['MmReserveExit','RlNativeRenderDispatch']:
        assert (location(old,name)-16)//8192==4
    assert address(old,'MmReserveExit')+int(old['syms']['MmReserveExit']['size'],0)==0xbf5a
    assert address(old,'RlNativeRenderDispatch')==0xbf8b
    leaves={}
    for name,text in [('metasprite_engine.s',pointer),('megaman_weapons.s',weapons)]:
        path=B/(PREFIX+'_'+name)
        if existing:assert path.read_text()==text
        else:assert not path.exists();path.write_text(text,newline='\n')
        leaves[name]=path
    ep=B/(PREFIX+'_entrypoint.s');raw=(R/'src/entrypoint.s').read_bytes()
    for name,path in leaves.items():
        token=('.include "'+name+'"').encode();assert raw.count(token)==1
        raw=raw.replace(token,('.include "'+path.name+'"').encode())
    if existing:assert ep.read_bytes()==raw
    else:assert not ep.exists();ep.write_bytes(raw)
    c=B/(PREFIX+'_main.c')
    if existing:assert c.read_bytes()==(R/'src/main.c').read_bytes()
    else:assert not c.exists();c.write_bytes((R/'src/main.c').read_bytes())
    cfg=configparser.ConfigParser();cfg.optionxform=str;cfg.read(R/'build_options.ini')
    defs={k:v for s in cfg.values()for k,v in s.items()};defs.update(MAPPER_MMC3='0',MAPPER_MMC5='1',ENABLE_CROSSOVER='1',ENABLE_MMC5_EXPANDED='1')
    out=B/(PREFIX+'.nes');assert existing==out.exists()
    cmd=[str(R/'tools/Windows/cc65/bin/cl65.exe'),'--cpu','6502x','-t','nes','-g','-Oisr','-vm','-T','-C',str(R/'smb1base-mmc5-expanded.cfg'),'--ld-args','--dbgfile,'+str(out.with_suffix('.dbg')),'--include-dir',str(R),'--asm-include-dir',str(B),'--asm-include-dir',str(R/'src'),'--asm-include-dir',str(R),'--bin-include-dir',str(R),'-m',str(out.with_suffix('.map')),'-Ln',str(out.with_suffix('.lbl')),'-o',str(out)]
    for k,v in defs.items():cmd+=['--asm-define',k+'='+v,'-D',k+'='+v]
    cmd+=[str(c),str(ep)]
    if not existing:
        run=subprocess.run(cmd,cwd=R,capture_output=True,text=True);out.with_suffix('.build.log').write_text(run.stdout+run.stderr)
        assert run.returncode==0,run.stdout+run.stderr
        prepare(R,out)
    new=scoped_load(out)
    changes=[i for i,(x,y)in enumerate(zip(old['raw'],new['raw']))if x!=y]
    assert changes and all((i-16)//8192==4 for i in changes)
    allowed=set(range(end-5,end-2))|set(range(at,at+49));assert set(changes)<=allowed
    qold,qnew=qualified(BASE),qualified(out)
    moves={str(n):[v,qnew.get(n)]for n,v in qold.items()if qnew.get(n)!=v}
    real={n:v for n,v in moves.items()if 'LOCAL-MACRO_SYMBOL-'not in n};assert not real,real
    assert address(new,'MmDynamicPlayerPrgOwner')==0xbf5a
    size=int(new['syms']['MmDynamicPlayerPrgOwner']['size'],0);assert size<=49
    patch=B/(PREFIX+'.patch');patch.write_text(''.join(''.join(difflib.unified_diff(originals[n].splitlines(True),leaves[n].read_text().splitlines(True),fromfile='current9ea/src/'+n,tofile='private/src/'+n))for n in originals),newline='\n')
    paths=[Path(__file__),BASE,BASE.with_suffix('.dbg'),BASE.with_suffix('.lbl'),R/'src/entrypoint.s',R/'src/main.c',R/'smb1base-mmc5-expanded.cfg',R/'build_options.ini',ep,c,patch]+list(leaves.values())+[R/'src'/n for n in originals]
    proof=dict(passed=True,source_only=True,native_run=False,installed=False,parent_sha256=EXPECTED,candidate_sha256=sha(out),candidate=str(out),changed_bytes=len(changes),changed_banks=[4],helper=dict(pc=0xbf5a,bytes=size,verified_FF_capacity=49),old_true_symbols_exact=True,debug_macro_changes=moves,header_CHR_NMI_audio_RAM_other_banks_exact=True,source_leaves={n:str(p)for n,p in leaves.items()},build_command=cmd,ROM_deltas=[dict(offset=i,before=old['raw'][i],after=new['raw'][i])for i in changes],bindings={str(p):sha(p)for p in paths})
    file=B/(PREFIX+'_build.json');assert not file.exists();file.write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(dict(candidate=sha(out),changed_bytes=len(changes),helper_bytes=size,proof=str(file))))


if __name__=='__main__':main()
