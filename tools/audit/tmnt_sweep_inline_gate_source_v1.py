"""Separate composition-layout probe; preserve the frozen645 sweep packet."""
from pathlib import Path
import argparse
import difflib
import json
import shutil
import subprocess
import sys
from check_tmnt_render_oa import load,address
from check_tmnt_audio_fallback_oc import qualified
from tmnt_native_storage_driver import ROOT,sha

PARENT='64504f58b7fee3382f9c661e0274c20f5ebdcb8ef0da8d59aae0fcc751629c5d'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ready',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();assert not a.output.exists()and not a.output.resolve().is_relative_to(ROOT)
    assert sha(a.ready/'candidate.nes')==PARENT
    b=load(a.ready/'candidate.nes');size=int(b['syms']['GuestAudioFinish']['size'],0)
    a.output.mkdir(parents=True);s=a.output/'source';shutil.copytree(a.ready/'source',s,ignore=shutil.ignore_patterns('__pycache__'))
    path=s/'src/guest_audio.s';text=path.read_text()
    old='''    lda GuestMixOwner
    beq Native
    lda GuestFxApu+I
    jmp Value
Native:
    lda GuestNativeApu+I
Value:''' 
    assert text.count(old)==1
    text=text.replace(old,''' .if ::ENABLE_MMC5_EXPANDED && ::MAPPER_MMC5 && C < 2
    ; This channel's genuine owner store above is unconditionally zero.
    lda GuestNativeApu+I
 .else
'''+old.replace('Value:','')+''' .endif
Value:''')
    old='''    lda GuestMixChanged
   .if ::MAPPER_MMC5
    and #((1 << C) & 8)
   .else
    and #(1 << C)
   .endif
    bne Write
    lda GuestMixOwner
    beq NativeDirty
    lda GuestFxDirty+I
    jmp Dirty
NativeDirty:
    lda GuestNativeDirty+I
Dirty:''' 
    assert text.count(old)==1
    text=text.replace(old,''' .if ::ENABLE_MMC5_EXPANDED && ::MAPPER_MMC5 && C < 2
    ; The deleted mix-change AND#0 is constant; only native dirtiness lives.
    lda GuestNativeDirty+I
 .else
'''+old.replace('Dirty:\n','Dirty:\n',1).removesuffix('Dirty:')+''' .endif
Dirty:''')
    # Define a real global entry in post-RTS space. Its old private gate labels
    # legitimately move into this explicit nested scope; no callable aliases.
    helper=s/'src/tmnt_sweep_fast.s';h=helper.read_text()
    gate=h.split('.proc TnExpansionSweepGate\n',1)[1].split('.endproc',1)[0]
    h='; New private C87 run alias'+h.split('; New private C87 run alias',1)[1]
    helper.write_text(h)
    inline='''\n.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5
::TnExpansionSweepGate:
.scope TnSweepInlineGate
'''+gate+'''.endscope
.assert *-::TnExpansionSweepGate=38,lderror,"Real relocated38B gate"
 .res '''+str(size)+'''-(*-::GuestAudioFinish),$ea
.endif
'''
    begin=text.index('.proc GuestAudioFinish');end=text.index('.endproc',begin)
    text=text[:end]+inline+text[end:];path.write_text(text)
    path=s/'smb1base-mmc5-expanded.cfg';cfg=path.read_text()
    line='    TN_SWEEP_GATE:load=PRG_EXTRA,start=$bfda,type=ro;\n';assert cfg.count(line)==1
    path.write_text(cfg.replace(line,''))
    command=[sys.executable,'-B',str(s/'tools/build_mmc5_expanded.py'),'--workspace',str(s),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(a.output/'candidate.nes')]
    r=subprocess.run(command,cwd=s,capture_output=True,text=True);(a.output/'build.log').write_text(r.stdout+r.stderr)
    assert r.returncode==0,(r.stdout+r.stderr)[-4000:]
    c=load(a.output/'candidate.nes');qb,qa=qualified(a.ready/'candidate.nes'),qualified(a.output/'candidate.nes')
    moved={str(n):[v,qa.get(n)]for n,v in qb.items()if qa.get(n)!=v}
    assert all(n.startswith("('TnExpansionSweepGate',")for n in moved),moved
    assert int(c['syms']['GuestAudioFinish']['size'],0)==size
    oldraw,newraw=b['raw'],c['raw'];changes={n:sum(x!=y for x,y in zip(oldraw[16+n*8192:16+(n+1)*8192],newraw[16+n*8192:16+(n+1)*8192]))for n in range(128)}
    changes={n:v for n,v in changes.items()if v};assert set(changes)=={29}
    assert newraw[16+29*8192+0x1fda:16+30*8192]==bytes([255])*38
    gatepc=address(c,'TnExpansionSweepGate');native=address(c,'GuestAudioNativeFlush')
    assert address(c,'GuestAudioFinish')<gatepc<gatepc+38<=native
    assert oldraw[1048592:]==newraw[1048592:]
    patch='';manifest={}
    for n in['src/guest_audio.s','src/tmnt_sweep_fast.s','smb1base-mmc5-expanded.cfg']:
        before,after=a.ready/'source'/n,s/n;manifest[n]=dict(before_sha256=sha(before),after_sha256=sha(after))
        patch+=''.join(difflib.unified_diff(before.read_text().splitlines(True),after.read_text().splitlines(True),fromfile='a/'+n,tofile='b/'+n))
    (a.output/'review.patch').write_text(patch)
    prep=json.loads((a.ready/'preparation.json').read_text());prep['candidate_ROM_sha256']=sha(a.output/'candidate.nes');(a.output/'preparation.json').write_text(json.dumps(prep,indent=2)+'\n')
    proof=dict(prepared=True,accepted=False,native_run=False,parent_ROM_sha256=PARENT,candidate_ROM_sha256=sha(a.output/'candidate.nes'),
               changed_PRG_bytes=changes,all_other_banks_audio_CHR_exact=True,moved_new_private_gate_labels=moved,
               GuestAudioFinish_public_size_preserved=size,new_real_gate_address=gatepc,
               original_A29_BFDA38_tail_restored_FF=True,space_reserved_for_0c45_Cv3FxOwnerInit=True,
               source_changes=manifest,additional_bank_trips=False,checker_sha256=sha(Path(__file__)),
               still_requires_fresh_complete_mixer_outer_CPU_and_0c45_composition=True)
    (a.output/'layout-preparation.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))


if __name__=='__main__':main()
