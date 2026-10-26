"""Freeze bounded source-only Chip hot-control proposal; no native launch."""
from pathlib import Path
import argparse,collections,difflib,hashlib,json,shutil,subprocess,sys
import py65.devices.mpu6502
from check_tmnt_audio_fallback_oc import qualified
from chip_hot_control_prepare_v4 import D,ROOT
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def binding(p):return dict(path=str(Path(p).resolve()),sha256=sha(p),bytes=Path(p).stat().st_size)
def main():
 p=argparse.ArgumentParser();p.add_argument('--candidate-dir',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);c=a.candidate_dir;rom=c/'candidate.nes';expected='ad925721081781707649152922582c590b239a187bc19c4666f2816a00b6ec9f';assert sha(rom)==expected==sha(c/'canonical/candidate.nes')
 for name,h in [('ordinary-mmc3','d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb'),('ordinary-mmc5','f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833')]:assert sha(c/(name+'.nes'))==h
 receipts=[]
 for name in ['player-cpu-v2','inputs-cpu-v1','side-cpu-v1','foreign-cpu-v1','irq-v1','irq-v2']:
  q=c/name/'proof.json';z=read(q);assert z['passed']and z['ROM_sha256']==expected;receipts.append(binding(q))
 parent=D/'root-chip-native-adapter-v6/candidate.nes';qb=qualified(parent);qa=qualified(rom);exceptions={('X5OwnMovement','Legacy'),('TnFastSideGate','CheckMac'),('MegaManFullShotBank','OtherSide'),('CrossoverSourceSideProbe','OwnZ2Side'),('Z2NativeSideSelector',)};changed={k:(v,qa.get(k))for k,v in qb.items()if qa.get(k)!=v};assert set(changed)==exceptions
 sources=[];patch=[]
 for n in ['x5_bounce.s','characters.s','megaman_weapons.s','tmnt_probe_gates.s']:
  rel='src/'+n;before=subprocess.run(['git','show','HEAD:'+rel],cwd=ROOT,capture_output=True,check=True).stdout;frozen=(D/'cv3-remaining-current50b-v1/baseline-source'/rel).read_bytes();after=(c/'source'/rel).read_bytes();assert before==frozen;assert before.count(b'\r\n')==before.count(b'\n')and after.count(b'\r\n')==after.count(b'\n')
  for folder,data in [('original',before),('new',after)]:q=a.output/folder/rel;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(data)
  sources.append(dict(relative_path=rel,before_sha256=hashlib.sha256(before).hexdigest(),after_sha256=hashlib.sha256(after).hexdigest(),original_Git_CRLF_preserved=True,before_CRLF_lines=before.count(b'\r\n'),after_CRLF_lines=after.count(b'\r\n')));patch+=list(difflib.unified_diff(before.decode().splitlines(True),after.decode().splitlines(True),fromfile='a/'+rel,tofile='b/'+rel))
 (a.output/'implementation.patch').write_bytes(''.join(patch).encode())
 (a.output/'source-manifest.json').write_text(json.dumps(sources,indent=2)+'\n')
 raw=parent.read_bytes();new=rom.read_bytes();assert raw[:16]==new[:16]and raw[16+128*8192:]==new[16+128*8192:];diff={str(k):sum(x!=y for x,y in zip(raw[16+k*8192:16+(k+1)*8192],new[16+k*8192:16+(k+1)*8192]))for k in range(128)};diff={k:v for k,v in diff.items()if v};assert diff=={'86':125,'89':23,'125':11,'126':32,'127':11};assert all((raw[16+125*8192+i]!=new[16+125*8192+i])==(raw[16+127*8192+i]!=new[16+127*8192+i])for i in range(8192))
 # Only resident selector/prefix bytes differ in the fixed clone. Every source
 # sample, manager, vector and other retained native audio byte remains exact.
 bindings=[]
 for suffix in ['.nes','.dbg','.lbl','.map','.build.json','.build.log','.cv3-mirror.json']:
  bindings.append(binding(rom.with_suffix(suffix)))
 for x in receipts:bindings.append(x)
 for name in ['preparation.json','symbol-differences.json','canonical/candidate.nes','canonical/candidate.build.json','canonical/candidate.build.log','ordinary-mmc3.nes','ordinary-mmc5.nes','side-cpu-v1/cases.json','inputs-cpu-v1/cases.json']:
  bindings.append(binding(c/name))
 for q in sorted((c/'source').rglob('*')):
  if q.is_file():bindings.append(binding(q))
 tools=sorted(Path(__file__).parent.glob('chip_hot_control_*.py'))
 for q in tools:bindings.append(binding(q))
 for rel in ['tools/build_mmc5_expanded.py','tools/prepare_cv3_dmc_mirror.py','tools/audit/check_tmnt_render_oa.py','tools/audit/check_tmnt_audio_fallback_oc.py','tools/audit/verify_native_relocation.py','tools/Windows/cc65/bin/cl65.exe']:
  bindings.append(binding(ROOT/rel))
 for rel in ['tools/Windows/cc65/bin/cc65.exe','tools/Windows/cc65/bin/ca65.exe','tools/Windows/cc65/bin/ld65.exe','tools/Windows/cc65/lib/nes.lib']:
  bindings.append(binding(ROOT/rel))
 for q in sorted((ROOT/'tools/Windows/cc65/asminc').rglob('*')):
  if q.is_file():bindings.append(binding(q))
 bindings.append(binding(sys.executable));bindings.append(binding(py65.devices.mpu6502.__file__))
 for rel in ['source-manifest.json','implementation.patch']:bindings.append(binding(a.output/rel))
 negatives=[]
 for folder,phase,cause in [('chip-hot-control-v1','parent rebuild','Missing original Chip NSF incbin; compiler stopped.'),('chip-hot-control-v2','source replacement','Original one-space X5OwnMovement text did not match draft two-space literal.'),('chip-hot-control-v3','source replacement','Original two-space resident selector text did not match draft three-space literal.'),('chip-hot-control-v4','post-build layout','Initial expected bank set omitted mandatory mirrored bank125; original candidate assembled. Strict subsequent CPU control rejected four changed SMC bytes.')]:
  q=D/folder/'failure.json'
  if not q.exists():q.write_text(json.dumps(dict(passed=False,phase=phase,cause=cause),indent=2)+'\n')
  negatives.append(binding(q))
 for rel in ['player-cpu-v2/proof.json','side-cpu-v1/proof.json','candidate.nes']:
  q=D/'chip-hot-control-v4'/rel;negatives.append(binding(q))
 assert not read(D/'chip-hot-control-v4/player-cpu-v2/proof.json')['passed']
 proof=dict(source_ready=True,native_executed=False,accepted=False,parent_ROM_sha256=sha(parent),candidate_ROM_sha256=expected,source_delta_files=4,original_Git_EOL_preserved=True,changed_PRG_banks=diff,all_header_CHR_and_other_banks_exact=True,fixed_mirror_changes_match_original_resident_bytes=True,all_audio_samples_and_audio_source_banks_exact=True,retained_qualified_symbols=len(qb)-len(changed),genuine_private_symbol_exceptions=[dict(symbol=list(k),old=v[0],new=v[1])for k,v in changed.items()],exceptions_explanation='Removed old private Legacy/OwnZ2Side and former solecaller JSRed selector after actual entry protocol replacement; CheckMac and OtherSide are genuine moved internal branch labels. No fake callable aliases. All public procedure entries/spans and other61832 qualified symbols stay fixed.',strict_CPU_receipts=receipts,source_contract='Chip authentic movement within original pre-step camera wrapper; genuine final Tn→Z2 side route retained. Side fallback A reload uses standard caller-owned SafecallA with no intervening calls; turtle/Mac leaves load A before consuming it. Actual mapperIRQ/RTI97 reached boundaries passes full resumed state. No new RAM/sample/music clock changes.',measured_CPU_saving=658,foreign_movement_continuation_cases=15360,complete_caller_input_cases=256,side_component_cases=168,scope='SOURCE/CPU READY ONLY on frozen8b4, not composed current6c69 and not native lag closure. Original1931-cycle first-boundary deficit exceeds658 saving; fullMain CPU model24/48cycle gap remains held in separate attribution packet. No native grant/process or production mutation.',retained_negatives=negatives,source_inventory_files=sum(1 for x in(c/'source').rglob('*')if x.is_file()),bindings=bindings,tool_sha256=sha(__file__))
 (a.output/'readiness-source-only.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(source_ready=True,readiness_sha256=sha(a.output/'readiness-source-only.json'),bindings=len(bindings),source_files=proof['source_inventory_files'],ROM_sha256=expected,native_executed=False)))
if __name__=='__main__':main()
