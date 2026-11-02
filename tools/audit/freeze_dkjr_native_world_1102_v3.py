"""Freeze only qualified private DK Jr v3 inputs and aggregate proof."""
import json,shutil,zipfile
from pathlib import Path
import prepare_dkjr_native_world_1102_v3 as P
R=P.R;O=P.O


def main():
 cpu=json.loads((O/'native-world-v3-CPU.json').read_text());ready=json.loads((O/'native-world-v3-readiness.json').read_text());assert cpu['passed']and ready['passed']
 for receipt in[cpu,ready]:
  for rel,h in receipt['bindings'].items():assert P.P.sha((R/rel).read_bytes())==h,rel
 source=[R/'tools/audit'/n for n in['prepare_dkjr_native_world_1102_v3.py','check_dkjr_native_world_1102_v3.py','report_dkjr_native_world_1102_v3.py','freeze_dkjr_native_world_1102_v3.py']]
 generated=[O/('native-world-v3'+suffix)for suffix in['.s','.cfg','.bin','.lbl','-layout.json','-source-layout.json','-source-CPU.json','-CPU.json','-readiness.json']]
 packet=O/'native-world-v3-qualified.zip';files=source+generated
 with zipfile.ZipFile(packet,'w',zipfile.ZIP_DEFLATED,9)as z:
  for p in files:z.write(p,p.relative_to(R).as_posix())
 checkpoint=R/'docs/qa/checkpoints/2026-11-02/dkjr-native-world-v3'
 q=dict(passed=True,source_only=True,native_playable=False,ROM_written=False,archive_SHA256=P.P.sha(packet.read_bytes()),archive_bytes=packet.stat().st_size,component_SHA256=ready['component_SHA256'],component_bytes=ready['component_bytes'],private_code_spare=ready['header_reserved_spare'],inherited_checkpoint='docs/qa/checkpoints/2026-11-02/dkjr-native-source-v2',inherited_archive_SHA256='d292dfc4c453e7c29235ccebcef93adab37ca248e98214153f4c167b0310300e',files={p.relative_to(R).as_posix():dict(SHA256=P.P.sha(p.read_bytes()),bytes=p.stat().st_size)for p in files},source_files=[p.relative_to(R).as_posix()for p in source],CPU_cases={k:cpu[k]for k in['source_regression','controller_original_and_native_cases','local_source_service_cases','coordinate_cases','native_query_cases']},resources=dict(original_private_state_bytes=2048,measurement_context_bytes=256,immutable_art_bytes=1728,code_pages_nominal=8,art_pages_nominal=2,host_granted=False),scope='Compiled current-native BlockBuffer/growing-vine/platform geometry, donor control normalization, private popup/audio leaves and typed anchor transport. Independent source CPU proof plus finite service audit. Actual Main, carry/contact/fruit/life ports, native rendering/IRQ/owner/menu/resources and1-1 are not qualified.')
 manifest=O/'native-world-v3-qualified.json';manifest.write_text(json.dumps(q,indent=2)+'\n');checkpoint.mkdir(parents=True,exist_ok=True)
 for src,name in[(packet,'inputs.zip'),(manifest,'manifest.json')]:
  dst=checkpoint/name
  if dst.exists():assert dst.read_bytes()==src.read_bytes()
  else:shutil.copyfile(src,dst)
  assert dst.read_bytes()==src.read_bytes()
 print(json.dumps(dict(passed=True,checkpoint=checkpoint.relative_to(R).as_posix(),archive_bytes=q['archive_bytes'],archive_SHA256=q['archive_SHA256'],component_bytes=q['component_bytes'],CPU_cases=q['CPU_cases'],git_files=[*q['source_files'],(checkpoint/'inputs.zip').relative_to(R).as_posix(),(checkpoint/'manifest.json').relative_to(R).as_posix()])))


if __name__=='__main__':main()
