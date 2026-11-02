"""Compact durable checkpoint for the source-only DK Jr extension."""
import json,shutil,zipfile
from pathlib import Path
import prepare_dkjr_native_source_1102_v2 as P
R=P.R;O=P.O


def main():
 cpu=json.loads((O/'CPU.json').read_text());assert cpu['passed']
 for rel,h in cpu['bindings'].items():assert P.sha((R/rel).read_bytes())==h,rel
 source=[R/'tools/audit'/n for n in['prepare_dkjr_native_source_1102_v2.py','check_dkjr_native_source_1102_v2.py','freeze_dkjr_native_source_1102_v2.py']]
 generated=[O/n for n in['component.s','component.cfg','component.bin','component.lbl','layout.json','CPU.json']]
 files=source+generated;packet=O/'qualified.zip'
 with zipfile.ZipFile(packet,'w',zipfile.ZIP_DEFLATED,9)as z:
  for p in files:z.write(p,p.relative_to(R).as_posix())
 q=dict(passed=True,source_only=True,native_playable=False,archive_SHA256=P.sha(packet.read_bytes()),archive_bytes=packet.stat().st_size,files={p.relative_to(R).as_posix():dict(SHA256=P.sha(p.read_bytes()),bytes=p.stat().st_size)for p in files},source_files=[p.relative_to(R).as_posix()for p in source],inherited_checkpoint='docs/qa/checkpoints/2026-11-02/dkjr-source-core-v1',component_bytes=6053,added_original_instruction_bytes=596,original_private_state_bytes=2048,measurement_context_bytes=216,CPU_cases=2740,scope='Exact original terrain/phase/contact code plus typed source-format rectangle binder. No native terrain/vine producer or remaining phase imports, resource/owner/menu/hardware integration is claimed.')
 out=O/'qualified.json';out.write_text(json.dumps(q,indent=2)+'\n')
 dest=R/'docs/qa/checkpoints/2026-11-02/dkjr-native-source-v2';dest.mkdir(parents=True,exist_ok=True)
 for src,name in[(packet,'inputs.zip'),(out,'manifest.json')]:
  target=dest/name
  if target.exists():assert target.read_bytes()==src.read_bytes()
  else:shutil.copyfile(src,target)
  assert target.read_bytes()==src.read_bytes()
 print(json.dumps(dict(passed=True,checkpoint=dest.relative_to(R).as_posix(),archive_bytes=q['archive_bytes'],archive_SHA256=q['archive_SHA256'],git_files=[*q['source_files'],(dest/'inputs.zip').relative_to(R).as_posix(),(dest/'manifest.json').relative_to(R).as_posix()])))


if __name__=='__main__':main()
