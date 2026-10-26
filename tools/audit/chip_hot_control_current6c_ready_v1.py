"""Freeze one current6c69-based Chip optimization for independent native checks."""
from pathlib import Path
import argparse,hashlib,json,shutil,sys
import py65.devices.mpu6502
from chip_hot_control_prepare_v4 import D,ROOT
from check_tmnt_audio_fallback_oc import qualified
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def bind(p):return dict(path=str(Path(p).resolve()),sha256=sha(p),bytes=Path(p).stat().st_size)
def read(p):return json.loads(Path(p).read_text())
def main():
 p=argparse.ArgumentParser();p.add_argument('--candidate-dir',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);c=a.candidate_dir;rom=c/'candidate.nes';parent=c/'parent-rebuild.nes';base=D/'world-firebar-padding-v2';expected='22fdf1f6ed7e70f87344cc17733f76da60e376ebfc9314c2cb9358587dd45fcf';ps='6c69e506b45c8420cf57a62b868f89c0fe86d308c0ee55655b48e8f44af9521a';assert sha(rom)==expected and sha(parent)==ps
 historical=D/'chip-hot-control-current6c-v1';assert sha(historical/'candidate.nes')==expected and sha(historical/'parent-rebuild.nes')==ps
 prep=read(c/'preparation.json');assert prep['candidate_ROM_sha256']==expected and not prep['held_Chip_music_imported'];snapshot=read(base/'source-manifest.json');assert all(sha(base/'source'/n)==h for n,h in snapshot.items());changed={n for n,h in snapshot.items()if sha(c/'source'/n)!=h};manifest=read(D/'chip-hot-control-v5/freeze-v2/source-manifest.json');assert changed==set(x['relative_path']for x in manifest)
 sources=[]
 for row in manifest:
  rel=row['relative_path'];old=base/'source'/rel;new=c/'source'/rel;assert sha(old)==row['before_sha256']and sha(new)==row['after_sha256']and sha(ROOT/rel)==sha(old)
  for d,q in [('original',old),('new',new)]:out=a.output/d/rel;out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(q,out)
  sources.append(dict(relative_path=rel,before_sha256=sha(old),after_sha256=sha(new),raw_source_EOL_preserved=True))
 (a.output/'source-manifest.json').write_text(json.dumps(sources,indent=2)+'\n');shutil.copyfile(D/'chip-hot-control-v5/freeze-v2/implementation.patch',a.output/'implementation.patch')
 checks=[]
 for n in ['caller-cpu-v1','inputs-cpu-v1','side-cpu-v1','foreign-cpu-v1','irq-v1']:
  q=c/n/'proof.json';r=read(q);assert r['passed']and r['ROM_sha256']==expected
  if n!='irq-v1':assert r['parent_ROM_sha256']==ps
  checks.append(bind(q))
 for n,h in [('ordinary-mmc3','d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb'),('ordinary-mmc5','f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833')]:assert sha(c/(n+'.nes'))==h
 old=parent.read_bytes();new=rom.read_bytes();assert old[:16]==new[:16]and old[16+128*8192:]==new[16+128*8192:];diff={str(k):sum(x!=y for x,y in zip(old[16+k*8192:16+(k+1)*8192],new[16+k*8192:16+(k+1)*8192]))for k in range(128)};diff={k:v for k,v in diff.items()if v};assert diff=={'86':125,'89':23,'125':11,'126':32,'127':11};assert all((old[16+125*8192+i]!=new[16+125*8192+i])==(old[16+127*8192+i]!=new[16+127*8192+i])for i in range(8192))
 qo,qn=qualified(parent),qualified(rom);exceptions={('X5OwnMovement','Legacy'),('TnFastSideGate','CheckMac'),('MegaManFullShotBank','OtherSide'),('CrossoverSourceSideProbe','OwnZ2Side'),('Z2NativeSideSelector',)};moved={k:(v,qn.get(k))for k,v in qo.items()if qn.get(k)!=v};assert set(moved)==exceptions
 protected=prep['current_protected_source_files_exact'];assert all((c/'source'/n).read_bytes()==(base/'source'/n).read_bytes()for n in protected)
 bindings=[]
 for pfx in ['candidate','parent-rebuild','ordinary-mmc3','ordinary-mmc5']:
  for suf in ['.nes','.dbg','.lbl','.map','.build.json','.build.log']:
   bindings.append(bind(c/(pfx+suf)))
 for rel in ['preparation.json','candidate.cv3-mirror.json','parent-rebuild.cv3-mirror.json','symbol-differences.json','inputs-cpu-v1/cases.json','side-cpu-v1/cases.json']:bindings.append(bind(c/rel))
 bindings+=checks
 for q in sorted((c/'source').rglob('*')):
  if q.is_file():bindings.append(bind(q))
 for q in sorted(Path(__file__).parent.glob('chip_hot_control_current6c_*.py')):bindings.append(bind(q))
 for rel in ['tools/audit/chip_hot_control_cpu_v2.py','tools/audit/chip_hot_control_prepare_v4.py','tools/audit/check_tmnt_render_oa.py','tools/audit/check_tmnt_audio_fallback_oc.py','tools/audit/verify_native_relocation.py','tools/build_mmc5_expanded.py','tools/prepare_cv3_dmc_mirror.py','tools/Windows/cc65/bin/cl65.exe','tools/Windows/cc65/bin/cc65.exe','tools/Windows/cc65/bin/ca65.exe','tools/Windows/cc65/bin/ld65.exe','tools/Windows/cc65/lib/nes.lib']:bindings.append(bind(ROOT/rel))
 for q in sorted((ROOT/'tools/Windows/cc65/asminc').rglob('*')):
  if q.is_file():bindings.append(bind(q))
 for n in ['configuration.json','profile-snapshots.jsonl','profile-snapshots.ram']:bindings.append(bind(D/'chip-idle-profiler-v1/fixture-v4'/n))
 bindings+=[bind(sys.executable),bind(py65.devices.mpu6502.__file__),bind(base/'source-manifest.json'),bind(base/'candidate.nes'),bind(D/'chip-hot-control-v5/freeze-v2/readiness-source-only.json'),bind(historical/'failure.json'),bind(historical/'candidate.nes'),bind(historical/'candidate.build.json'),bind(a.output/'source-manifest.json'),bind(a.output/'implementation.patch')]
 proof=dict(source_ready=True,native_executed=False,accepted=False,production_mutated=False,parent_ROM_sha256=ps,candidate_ROM_sha256=expected,exact_two_independent_parent_and_candidate_compiles=True,source_delta_files=sources,current_source_snapshot_files_verified=len(snapshot),only_four_raw_source_changes=True,held_music_dependency=False,protected_current_source_files_exact=protected,changed_PRG_banks=diff,header_CHR_all_other_PRG_and_accepted_display_bank4_exact=True,fixed_clone_resident_delta_exact=True,ordinary_mapper_builds_unchanged=True,CPU_checks=checks,complete_caller_saving_cycles=658,foreign_movement_saving_cycles=20,retained_qualified_symbols=len(qo)-len(moved),genuine_private_exceptions=[dict(symbol=list(k),old=v[0],new=v[1])for k,v in moved.items()],symbol_scope='Three genuinely removed private/helper labels after actual protocol replacement and two moved internal branches; all other61200 symbols exact, no fake aliases. Public procedures retain entries/spans.',CPU_input_scope='Fresh execution of actual composed/current-parent code using the same historical8b4 captured-state CPU arenas. These are controlled source/CPU inputs, not newly captured current-parent native states or traversal evidence. Full caller/RAM/SMC/mapper and unchanged real foreign continuation entry verified; LmMovementGate is a common dispatcher continuation.',retained_negative='Private current6c-v1 compiled both exact hashes but postbuild verification named nonexistent cv3_remaining_sfx.s. Validation-only failure retained; v2 used actual cv3_remaining_source_fx.s and independently rebuilt. Earlier4e52 strictSMC failure remains rejected.',native_remaining='No Mesen launch, native cadence or lag-closure claim. This is one exact current candidate for ROOT native checks.',bindings=bindings,tool_sha256=sha(__file__))
 (a.output/'readiness-source-only.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(source_ready=True,ROM_sha256=expected,readiness_sha256=sha(a.output/'readiness-source-only.json'),bindings=len(bindings),retained_symbols=proof['retained_qualified_symbols'])))
if __name__=='__main__':main()
