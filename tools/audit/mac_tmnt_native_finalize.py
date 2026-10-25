"""Bind the finite current55 Mac/TMNT review packet without installing it."""
from pathlib import Path
import argparse,hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packet',type=Path,required=True);a=p.parse_args();d=a.packet.resolve()
 build=json.loads((d/'build-proof.json').read_text());cpu=json.loads((d/'cpu-v1/proof.json').read_text())
 assert build['passed']and cpu['passed']and build['ROM_sha256']==cpu['ROM_sha256']
 evidence={};native={}
 for who in ['mac','tmnt']:
  pair=[]
  for kind in ['baseline','candidate']:
   n=f'{who}-{kind}-v1/native-proof.json';q=json.loads((d/n).read_text());pair.append(q)
   assert q['fixture_sha256']==sha(ROOT/'tools/audit/mac_tmnt_native_fixture.lua')and q['runner_sha256']==sha(ROOT/'tools/audit/mac_tmnt_native_run.py')
   assert q['ROM_sha256']==build['baseline_sha256'if kind=='baseline'else'ROM_sha256']
   assert q['passed']==(kind=='candidate')
   assert len(q['cases'])==(13 if who=='mac'else 37)
   evidence[n]=sha(d/n)
  assert [q['name']for q in pair[0]['cases']]==[q['name']for q in pair[1]['cases']]
  native[who]=dict(candidate_cases=len(pair[1]['cases']),preserved_baseline_failures=len(pair[0]['violations']),candidate_frames=pair[1]['wall_frames'],candidate_NMIs=pair[1]['nmis'],sampled_min_SP=pair[1]['min_sp_sampled_at_native_entries'],hardware_frame_count=len(pair[1]['physical_frames']))
  if who=='tmnt':
   assert pair[1]['real_block_reveals']==1 and pair[1]['native_rise_calls']==1776 and pair[1]['native_collections']==25
   native[who].update(real_question_block_reveals=1,native_rise_calls=1776,native_collections=25)
 for n in ['build-proof.json','cpu-v1/proof.json','cpu-v1/prior-regression/preserved-failures.json','implementation.patch','baseline.nes','candidate.nes']:
  evidence[n]=sha(d/n)
 files=sorted(q for q in (d/'source').rglob('*')if q.is_file())
 with zipfile.ZipFile(d/'source.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for f in files:z.write(f,str(f.relative_to(d/'source')).replace('\\','/'))
 evidence['source.zip']=sha(d/'source.zip')
 names=['tmnt_equipment.s','tmnt_equipment_draw.s','union_rare.s','collision.s','game.s','screen_render.s','little_mac_core.s','little_mac_state.inc','tmnt_state.inc','x5_profiles.s','player.s']
 primary={f'src/{n}':sha(d/'frozen/src'/n)for n in names}
 owned=['mac_tmnt_native_helpers.candidate.s','mac_tmnt_native_prepare.py','mac_tmnt_native_fixture.lua','mac_tmnt_native_run.py','mac_tmnt_native_cpu.py','mac_tmnt_native_finalize.py']
 tools={f'tools/audit/{n}':sha(ROOT/'tools/audit'/n)for n in owned}
 dependencies=['tools/build_mmc5_expanded.py','tools/run_mesen.py','tools/audit/run_mesen_isolated.py','tools/audit/vehicles_mike_mac_audit_cpu_v1.py','tools/audit/check_tmnt_render_oa.py','tools/audit/link_pit_rygar_sophia_audit_cpu.py','tools/audit/verify_native_relocation.py','tools/audit/check_tmnt_audio_fallback_oc.py','tools/audit/observe_chip_committed_write.py']
 q=dict(passed=True,adopted=False,parent_ROM_sha256=build['baseline_sha256'],ROM_sha256=build['ROM_sha256'],implementation=build,source_zip_files=len(files),evidence=evidence,native=native,primary_source_bindings=primary,owned_tools=tools,dependencies={n:sha(ROOT/n)for n in dependencies},Mesen_worker_released=True,open_limits=['Area control explicitly stages a legal marker change; no natural pipe traversal claimed.','TMNT variant matrix tests indexed health/equipment ownership, not cold-menu art/palette fidelity for all four turtles.','No audio change. Previously qualified native TMNT music proposal remains held for performance regression.','No full route/campaign/hardware, frame-rate improvement or all-weapon fidelity claim.','Mac modular gain/loss distinction assumes bounded native events; 127+ simultaneous counter changes are not qualified.'],scope='Two source-backed repairs, byte-exact ordinary controls, preserved identical-fixture baseline failures and exact-candidate native/CPU regression. ROOT must compose and rerun its exact resulting build before adoption.')
 (d/'review-binding.json').write_text(json.dumps(q,indent=2)+'\n')
 print(json.dumps(dict(passed=True,ROM_sha256=q['ROM_sha256'],review_binding_sha256=sha(d/'review-binding.json'),source_zip_sha256=evidence['source.zip'],native=native),indent=2))
if __name__=='__main__':main()
