"""Separate C87-only removal of proved dead private intermediate operations."""
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

PARENT='e5951e94c4b6d9d5acf1257d894ce31ce86ff5784f3ccb8aa3db00b8291d274b'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--parent',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();assert not a.output.exists()and not a.output.resolve().is_relative_to(ROOT)
    assert sha(a.parent/'candidate.nes')==PARENT
    a.output.mkdir(parents=True);s=a.output/'source';shutil.copytree(a.parent/'source',s,ignore=shutil.ignore_patterns('__pycache__'))
    path=s/'src/tmnt_sweep_fast.s';old=path.read_text();text=old
    original='''.repeat 8,I
 lda GuestFxApu+7-I
 sta GuestExpansionApu+7-I
.endrepeat'''
    replacement='''.repeat 8,I
.if 7-I<>2 && 7-I<>3
 ; Both source-clock routes later overwrite2/3 before any output/reader.
 lda GuestFxApu+7-I
 sta GuestExpansionApu+7-I
.endif
.endrepeat'''
    assert text.count(original)==1;text=text.replace(original,replacement)
    original=''' ; Exact8-bit specialization. Last SBC cannot overflow for P>=18.
 sec
 sbc #1'''
    replacement=''' ; CMP18 already proves carry1. Last SBC cannot overflow for P>=18.
 sbc #1'''
    assert text.count(original)==1;text=text.replace(original,replacement)
    original=''' lda #0
 sta GuestSweepPeriod+1
 sta GuestSweepDelta+1'''
    replacement=''' lda #0
 ; PeriodHi was proved zero and is not modified on this small route.
 sta GuestSweepDelta+1'''
    assert text.count(original)==1;text=text.replace(original,replacement)
    original='''Wide:
 sec
 lda GuestSweepPeriod'''
    replacement='''Wide:
 ; CMP0 already proves carry1 for every nonzero high byte.
 lda GuestSweepPeriod'''
    assert text.count(original)==1;text=text.replace(original,replacement)
    original=''' ldx #8
 tay
 cpx #8
 rts'''
    replacement=''' ldx #8
 tay
 ; Private caller consumes only X8/Y=finalA/V/D/I. Its REAL CPX8 owns
 ; every final C/N/Z result after restoring the original C-window bank.
 rts'''
    assert text.count(original)==1;text=text.replace(original,replacement)
    path.write_text(text)
    command=[sys.executable,'-B',str(s/'tools/build_mmc5_expanded.py'),'--workspace',str(s),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(a.output/'candidate.nes')]
    r=subprocess.run(command,cwd=s,capture_output=True,text=True);(a.output/'build.log').write_text(r.stdout+r.stderr)
    assert r.returncode==0,(r.stdout+r.stderr)[-4000:]
    before,after=(a.parent/'candidate.nes').read_bytes(),(a.output/'candidate.nes').read_bytes()
    changes={n:sum(x!=y for x,y in zip(before[16+n*8192:16+(n+1)*8192],after[16+n*8192:16+(n+1)*8192]))for n in range(128)}
    changes={n:v for n,v in changes.items()if v};assert set(changes)=={87}
    assert before[:16]==after[:16]and before[1048592:]==after[1048592:]
    assert before[16+87*8192:16+87*8192+0x1500]==after[16+87*8192:16+87*8192+0x1500]
    qb,qa=qualified(a.parent/'candidate.nes'),qualified(a.output/'candidate.nes')
    moved={str(n):[v,qa.get(n)]for n,v in qb.items()if qa.get(n)!=v}
    assert all(n.startswith("('TnExpansionFlushFast',")and n!="('TnExpansionFlushFast',)"for n in moved),moved
    assert address(load(a.output/'candidate.nes'),'TnExpansionFlushFast')==0xd500
    prep=json.loads((a.parent/'preparation.json').read_text());prep['candidate_ROM_sha256']=sha(a.output/'candidate.nes');(a.output/'preparation.json').write_text(json.dumps(prep,indent=2)+'\n')
    patch=''.join(difflib.unified_diff(old.splitlines(True),text.splitlines(True),fromfile='a/src/tmnt_sweep_fast.s',tofile='b/src/tmnt_sweep_fast.s'))
    (a.output/'review.patch').write_text(patch)
    proof=dict(prepared=True,native_run=False,accepted=False,parent_ROM_sha256=PARENT,candidate_ROM_sha256=sha(a.output/'candidate.nes'),
               changed_PRG_bytes=changes,source_changes={'src/tmnt_sweep_fast.s':dict(before_sha256=sha(a.parent/'source/src/tmnt_sweep_fast.s'),after_sha256=sha(path))},
               only_genuine_new_helper_private_labels_move=moved,all_old_public_entries_RAMP_CHR_otherbanks_exact=True,
               source_C87_initial_2_3_images_dead_until_literal_unconditional_replacement=True,
               small_C_and_Phi0_proved_by_preceding_CMP_branches=True,private_CN_Z_dead_before_real_wrapper_CPX8=True,
               provisional_small_path_cycle_saving=24,actual_savings_still_require_whole_caller_measurement=True,
               checker_sha256=sha(Path(__file__)))
    (a.output/'preparation-live-math.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))


if __name__=='__main__':main()
