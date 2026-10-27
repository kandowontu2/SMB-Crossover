"""Private completed-base producer cache; preserve the held cold-cache donor."""
from pathlib import Path
import argparse
import difflib
import hashlib
import json
import shutil
import subprocess
import sys
import traceback
from check_tmnt_audio_fallback_oc import qualified
from link_pit_rygar_sophia_audit_cpu import scoped_load

R=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
P=D/'robot-cold-palette-candidate-v2'
ROOT=D/'root-current-roster-composition-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:Path(p).write_text(json.dumps(z,indent=2)+'\n')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    out=a.output.resolve();assert not out.is_relative_to(R);out.mkdir(parents=True,exist_ok=False)
    try:
        assert sha(P/'candidate.nes')=='0ba628a76f02d4610c2608acd63cdd2a877e6e9a9eb667496a3efa1c655c1927'
        original=json.loads((P/'source-manifest.json').read_text());source=out/'source'
        for rel,h in original.items():
            f=P/'source'/rel;assert sha(f)==h,rel
            target=source/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,target)
        helper=source/'src/robot_cold_palette_cache.s';before=helper.read_text()
        needle='''  phx
  lda GameEngineSubroutine'''
        assert before.count(needle)==1
        new='''  phx
  ; A complete default GetColors body row is the normal palette source too.
  ; Preserve cold Ss admission below, including its stricter charge-zero rule.
  lda SelectedCharacter
  cmp #CHARACTER_MEGAMAN
  bne ColdCache
  lda InvSelected+CHARACTER_MEGAMAN
  bne ColdCache
  lda GuestPowerupActive
  ora StarInvincibleTimer
  bne ColdCache
  lda MmChargeFrames
  cmp #33
  bcs ColdCache
  lda VRAM_Buffer1_Offset
  cmp #19
  bcc ColdCache
  cmp #84
  bcs ColdCache
  ldx #1
  lda PlayerStatus
  cmp #2
  bne BaseCache
  inx
BaseCache:
  stx MmLastPalette
ColdCache:
  lda GameEngineSubroutine'''
        helper.write_text(before.replace(needle,new))
        manifest={rel:sha(source/rel)for rel in original};changed=[rel for rel,h in original.items()if manifest[rel]!=h]
        assert changed==['src/robot_cold_palette_cache.s']
        put(out/'source-manifest.json',manifest)
        (out/'incremental-source.patch').write_text(''.join(difflib.unified_diff(before.splitlines(True),helper.read_text().splitlines(True),fromfile='0ba/src/robot_cold_palette_cache.s',tofile='private/src/robot_cold_palette_cache.s')))
        raw=(P/'candidate.nes').read_bytes();free=16+78*8192+0xba7;end=16+78*8192+0xc00
        assert raw[free:end]==bytes([255])*(end-free)
        root_raw=(ROOT/'candidate.nes').read_bytes();assert root_raw[16+78*8192+0xb60:end]==bytes([255])*160
        command=[sys.executable,'-B',str(source/'tools/build_mmc5_expanded.py'),'--workspace',str(source),'--compiler',str(R/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(out/'candidate.nes')]
        run=subprocess.run(command,cwd=source,capture_output=True,text=True)
        put(out/'build.json',dict(command=command,exit=run.returncode,stdout=run.stdout,stderr=run.stderr))
        assert run.returncode==0,run.stdout+run.stderr
        b=scoped_load(out/'candidate.nes');s=b['syms']['RobotColdPaletteCommit'];start=int(s['val'],0);size=int(s['size'],0)
        assert start==0xab60 and size<=160
        q=qualified(ROOT/'candidate.nes');newq=qualified(out/'candidate.nes')
        assert all(newq.get(n)==v for n,v in q.items())
        oldq=qualified(P/'candidate.nes');moves={n:dict(old=v,new=newq.get(n))for n,v in oldq.items()if newq.get(n)!=v}
        assert all(n.startswith('RobotColdPaletteCommit::')for n in moves),moves
        data=(out/'candidate.nes').read_bytes();delta=[i for i,(x,y)in enumerate(zip(data,raw))if x!=y]
        assert len(data)==len(raw)and all(16+78*8192+0xb60<=i<end for i in delta)
        total=[i for i,(x,y)in enumerate(zip(data,root_raw))if x!=y]
        put(out/'proof.json',dict(built=True,source_only=True,native_run=False,qualified=False,
            parent_ROM_sha256=sha(P/'candidate.nes'),ROOT_parent_ROM_sha256=sha(ROOT/'candidate.nes'),ROM_sha256=sha(out/'candidate.nes'),
            incremental_changed_source=changed,incremental_ROM_bytes=len(delta),total_ROM_bytes_vs_ROOT=len(total),changed_banks=[78],
            helper_start=hex(start),helper_bytes=size,helper_end_exclusive=hex(start+size),actual_reserved_bytes=160,
            previous_remaining89B_before_edit_all_FF=True,all_ROOT_qualified_symbols_exact=True,ROOT_qualified_symbols=len(q),
            genuine_moved_donor_private_labels=moves,all_other_PRG_CHR_RAM_exact=True,NMI_changed=False,new_RAM_bytes=0,
            source_manifest_sha256=sha(out/'source-manifest.json'),patch_sha256=sha(out/'incremental-source.patch'),tool_sha256=sha(__file__),
            limits='Only assembled capacity/code ownership so far. Cache classification must be source/CPU qualified, including exact tier2MmPaletteIndex dead-state exception and complete caller. No native grant/recovery/wholegoal claim.'))
        print((out/'proof.json').read_text())
    except BaseException as e:
        put(out/'failure.json',dict(native_run=False,error=repr(e),traceback=traceback.format_exc(),tool_sha256=sha(__file__)))
        shutil.copyfile(__file__,out/'failed-tool.py');raise


if __name__=='__main__':main()
