"""Freeze label-only52 and53 source, prepare one standalone52 native test."""
from pathlib import Path
import json
import build_celeste_exact_menu_name_v3 as B
import arthur_body_fair_budget_v7 as Q
R=B.R;O=R/'build/celeste-menu-name-current-v2';N=O/'joint'
def main():
 for spec in B.CASES:
  p=R/'build'/spec[0];out=p/'handoff.json';assert not out.exists()
  for name in ['source-proof.json','menu-controls-v2.json']:
   d=json.loads((p/name).read_text());assert d['passed']
   for path,v in d['bindings'].items():assert B.sha(path)==v,path
  d=dict(status='FROZEN_EXACT_CELESTE_MENU_LABEL_SOURCE_NATIVE_PENDING',native=False,ready_count=spec[2],candidate=B.sha(p/'joint/candidate.nes'),parent=json.loads((p/'source-proof.json').read_text())['parent'],only12_ROM_bytes_changed=True,all_CHR_header_gameplay_NMI_shared_dispatch_exact=True,source_patch=str((p/'source.patch').resolve()),source_semantics='Existing cold KmQueueName selected0 variant4 takes direct SAMEA81 NameIndex with A44; existing authenticated Names44 unchanged. Other79 actual menu states/application exact; 5x64flags own publisher compared with actual selected name worker. Unsupported variant/status behavior retained.',limits=['No native qualification yet.','Ready53 descendant retains separately frozen Arthur native movement/jump/attack negative; this label fix does not repair/admit Arthur.'],bindings={str(q.resolve()):B.sha(q)for q in list(p.rglob('*'))+[Path(__file__),R/'tools/audit/celeste_exact_menu_name_controls_v2.py',R/'build'/spec[1]/'joint/candidate.nes']if q.is_file()})
  out.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(dict(packet=spec[0],handoff=B.sha(out),candidate=d['candidate'],ready=spec[2])),flush=True)
 source=R/'tools/audit/celeste_exact_name_native_v1.lua';driver=O/'native-driver-v1.lua';b=B.scoped_load(N/'candidate.nes');at=B.location(b,'NrQueueSelectName::Names')+44*16;expected=b['raw'][at:at+16]
 driver.write_text(f'CELESTE_ROM_SHA256="{B.sha(N/"candidate.nes")}"\nCELESTE_EXPECTED_NAME={{{",".join(map(str,expected))}}}\ndofile([=[{source.as_posix()}]=])\n',newline='\n')
 actual=R/'tools/audit/capture_budget.py';budget=O/'native-capture-budget-v1.py';budget.write_text(actual.read_text().replace('RUN_BYTES = 2_000_000_000','RUN_BYTES = 536_870_912').replace('receipt = preflight(output)','receipt = preflight(output, reserved_bytes=RUN_BYTES, reserved_files=RUN_FILES)'),newline='\n');module=Q.load(budget)
 proof=module.preflight(O/'native/cold-label-v1',reserved_bytes=536870912,reserved_files=64);(O/'storage-preflight-v1.json').write_text(json.dumps(proof,indent=2)+'\n')
 d=dict(status='PREPARED_NOT_RUN_ROOT_REVIEW_AND_ONE_GRANT_REQUIRED',candidate=B.sha(N/'candidate.nes'),handoff=B.sha(O/'handoff.json'),command='python tools/audit/run_celeste_exact_name_native_v1.py --launch',config=dict(max_physical_frames=600,screenshots=2,files=64,reserved_bytes=536870912,timeout_seconds=60,AllZeros=True,normal8sprites=True,script_RAM_writes=False),options=['--doNotSaveSettings','--nes.removeSpriteLimit=false','--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false'],bindings={str(p.resolve()):B.sha(p)for p in [Path(__file__),source,driver,budget,Path(Q.__file__),R/'tools/audit/run_celeste_exact_name_native_v1.py',R/'tools/run_mesen.py',actual,O/'handoff.json',O/'storage-preflight-v1.json',N/'candidate.nes',N/'candidate.dbg',N/'candidate.lbl']})
 (O/'native-prepared-v1.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(dict(prepared=B.sha(O/'native-prepared-v1.json'),candidate=d['candidate'],config=d['config'])))
if __name__=='__main__':main()
