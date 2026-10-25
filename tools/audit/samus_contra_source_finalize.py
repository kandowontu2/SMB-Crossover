"""Seal the finite Samus/Contra private source, CPU and native packet."""
from pathlib import Path
import argparse,hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packet',type=Path,required=True);a=p.parse_args();d=a.packet.resolve();v=d/'proposal-v2'
 build=json.loads((v/'build-proof.json').read_text());cpu=json.loads((d/'cpu-final-v1/proof.json').read_text());assert build['passed']and cpu['passed']and build['ROM_sha256']==cpu['ROM_sha256']
 evidence={};native=[]
 for kind in ['candidate','baseline','page-only-negative']:
  n=f'native-{kind}-v2/native-proof.json';q=json.loads((d/n).read_text())
  assert len(q['cases'])==16 and q['passed']==(kind=='candidate')
  assert q['fixture_sha256']==sha(ROOT/'tools/audit/samus_contra_source_native.lua')and q['runner_sha256']==sha(ROOT/'tools/audit/samus_contra_source_native.py')
  evidence[n]=sha(d/n);native.append(q)
 assert [q['name']for q in native[0]['cases']]==[q['name']for q in native[1]['cases']]==[q['name']for q in native[2]['cases']]
 assert native[0]['ROM_sha256']==build['ROM_sha256']and native[1]['ROM_sha256']==build['parent_ROM_sha256']and native[2]['ROM_sha256']==cpu['page_only_negative_ROM_sha256']
 assert len(native[1]['violations'])==len(native[2]['violations'])==8
 hardware=json.loads((d/'native-candidate-v2/chr-commit.json').read_text());assert hardware['passed']and hardware['mismatched_frames']==0
 files=sorted(q for q in (v/'source').rglob('*')if q.is_file())
 with zipfile.ZipFile(v/'source.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for f in files:z.write(f,str(f.relative_to(v/'source')).replace('\\','/'))
 for n in ['proposal-v2/source.zip','proposal-v2/implementation.patch','proposal-v2/build-proof.json','cpu-final-v1/proof.json','cpu-final-v1/preserved-failure.json','cpu-final-v1/preserved-terrain-failures.json','native-candidate-v2/chr-commit.json']:
  evidence[n]=sha(d/n)
 old,new=(v/'baseline.nes').read_bytes(),(v/'candidate.nes').read_bytes();ranges=[]
 for i,(x,y)in enumerate(zip(old,new)):
  if x!=y:
   if ranges and i==ranges[-1][-1]+1:ranges[-1].append(i)
   else:ranges.append([i])
 changes=[dict(ROM_offset=q[0],PRG_bank=(q[0]-16)//8192,old=old[q[0]:q[-1]+1].hex(),new=new[q[0]:q[-1]+1].hex())for q in ranges]
 tools={str(f.relative_to(ROOT)).replace('\\','/'):sha(f)for f in sorted((ROOT/'tools/audit').glob('samus_contra_source_*'))if f.is_file()}
 depnames=['tools/build_mmc5_expanded.py','tools/run_mesen.py','tools/audit/run_mesen_isolated.py','tools/audit/check_tmnt_render_oa.py','tools/audit/link_pit_rygar_sophia_audit_cpu.py','tools/audit/verify_native_relocation.py','tools/audit/check_tmnt_audio_fallback_oc.py','tools/audit/observe_chip_committed_write.py','tools/audit/vehicles_mike_mac_audit_cpu_v1.py']
 q=dict(passed=True,adopted=False,parent_ROM_sha256=build['parent_ROM_sha256'],ROM_sha256=build['ROM_sha256'],build=build,source_ZIP_files=len(files),evidence=evidence,changed_ranges=changes,tools=tools,dependencies={n:sha(ROOT/n)for n in depnames},native=dict(cases=16,physical_frames=native[0]['wall_frames'],NMI_guards=native[0]['nmis'],sampled_min_SP=native[0]['min_sp_sampled'],native_shot_updates=sum(len(c['positions'])for c in native[0]['cases']),world_page_crossings=sum(c['crossings']for c in native[0]['cases']),actual_Hard_Wave_pickups=sum(c['grant']for c in native[0]['cases']),raw_PPU_samples=len(native[0]['physical_frames']),hardware_CHR=hardware,identical_fixture_baseline_failures=8,identical_fixture_page_only_failures=8),CPU=cpu,Mesen_worker_released=True,limits=['Hard inventory uses actual legal mushroom/base+Long ownership129, and physically collects a mature seeded Wave actor to145. Natural item emergence is not claimed.','Easy flower tier and player positions are explicitly seeded; actual real input fires every shot.','Empty actor arena clears enemies at native update boundaries, retaining original question-block terrain for Wave pass-through.','No whole-route/hardware, all-beam/suit/Contra ability native qualification, source audio equivalence or FPS improvement claim.','Original hosted six-character source is not independently authenticated as a specific1.0 patch. Later source explicitly declares2.02.'],scope='Two confirmed Samus source-coordinate/terrain defects repaired privately. ROOT must qualify its exact composed hash before adoption. Bill/Lance source comparison and bounded CPU components are not current native playthrough certification.')
 (d/'review-binding.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(passed=True,ROM_sha256=q['ROM_sha256'],review_binding_sha256=sha(d/'review-binding.json'),source_zip_sha256=evidence['proposal-v2/source.zip'],native=q['native']),indent=2))
if __name__=='__main__':main()
