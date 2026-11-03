"""Compact exact source/checkpoint successor; no ROM, DBG or old tree copies."""
from pathlib import Path
import hashlib,json,sys,zipfile
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
O=R/'build/prince-actor-1101-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
SOURCES=[
 'audit_prince_quiet_audio_storage_1102_v48.py','measure_prince_collision_services_1102_v49.py',
 'prepare_prince_current_manifest_1102_v51.py','check_prince_current_foreign_1102_v52.py','check_prince_current_services_1102_v53.py',
 'prepare_prince_sunny_rebase_1102_v54.py','check_prince_sunny_services_1102_v55.py','check_prince_collision_services_1102_v56.py',
 'prepare_prince_collision_cold_1102_v57.py','check_prince_collision_cold_1102_v58.py','prepare_prince_collision_manifest_1102_v59.py',
 'check_prince_collision_shared_1102_v60.py','check_prince_current_ingress_1102_v61.py','audit_prince_collision_lifetime_1102_v62.py',
 'checkpoint_prince_collision_1102_v63.py','measure_prince_nr_gate_1102_v64.py','prepare_prince_native_manifest_1102_v65.py','check_prince_native_ingress_1102_v66.py']


def main():
 frozen=json.loads((O/'native-battle-checkpoint-v47.json').read_text());assert sha(O/'native-battle-source-v47.zip')==frozen['checkpoint_SHA256']
 for name in frozen['explicit_source_commit_files']:assert sha(R/name)==frozen['member_SHA256'][name],name
 source_paths=[R/'tools/audit'/n for n in SOURCES]+[R/'docs/qa/prince-native-collision-1102-v63.md']
 generated=['quiet-audio-code-proposal-v48.json','collision-services-measurement-v49.json','current-manifest-v51.json','current-foreign-CPU-v52.json','current-services-CPU-v53.json','sunny-rebase-manifest-v54.json','sunny-services-CPU-v55.json','collision-services-CPU-v56.json','cold-link-storage-v57.json','collision-cold-CPU-v58.json','collision-cold-negative-v58.json','collision-manifest-v59.json','collision-shared-CPU-v60.json','current-ingress-negative-v61.json','collision-lifetime-proposal-v62.json','native-nr-gate-proposal-v64.json','native-manifest-v65.json','native-ingress-CPU-v66.json','native-runtime-v49.bin','native-metadata-v49.bin','native-state-v49.bin','native-labels-v49.json','native-fresh-v49.bin','native-contact-v49.bin','cold-pool-v57.bin']
 for name in ['services','battle','proxy','public','policies','audio','small']:
  generated += [f'native-{name}-v49.{s}'for s in ['s','cfg','lbl','bin']]
 generated += [f'cold-worker-v57.{s}'for s in ['s','cfg','lbl','bin']]+[f'native-{n}-v57.lzdict'for n in ['runtime','metadata','state_code']]+[f'native-nr-gate-v64.{s}'for s in ['s','cfg','lbl','bin']]
 files={p.relative_to(R).as_posix():p.read_bytes()for p in source_paths};files.update({'generated/'+n:(O/n).read_bytes()for n in generated})
 grants=[R/'docs/qa/allocations'/n for n in ['prince-collision-lifetime-1102-v62.json','prince-native-rare-gate-1102-v64.json']]
 files.update({p.relative_to(R).as_posix():p.read_bytes()for p in grants})
 assert all(not n.endswith(('.nes','.dbg','.o','.png'))for n in files)
 target=O/'native-collision-source-v63.zip'
 with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for name,data in sorted(files.items()):z.writestr(name,data)
 with zipfile.ZipFile(target)as z:assert z.testzip()is None and all(z.read(n)==data for n,data in files.items())
 manifest=dict(passed=True,private_source_checkpoint=True,ROM_written=False,installed=False,menu_admitted=False,base_SHA256='16a9de64b18370a03885ff503141fc08edd25f3bd026d480854a1754efa1490b',memory_only_SHA256='da4a84baf1d98e6748b80c25ba5f62e14e739c3b10c10eb83c948c778e044d05',checkpoint=target.relative_to(R).as_posix(),checkpoint_SHA256=sha(target),checkpoint_bytes=target.stat().st_size,checkpoint_members=len(files),requires_frozen_v47_checkpoint_SHA256=frozen['checkpoint_SHA256'],all17_frozen_v47_source_hashes_unchanged=True,explicit_source_commit_files=[p.relative_to(R).as_posix()for p in source_paths],member_SHA256={n:hashlib.sha256(data).hexdigest()for n,data in files.items()},remaining='Actual head/side/fullplayer and death/respawn lifecycle, full-image renderer, root native menu/scene/control/firstpipe/originalledge ability/full1-1. Original music/SFX mapping/mixer incomplete. No helper added and no nightly delivery claimed.')
 (O/'native-collision-checkpoint-v63.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({k:v for k,v in manifest.items()if k not in ['member_SHA256','explicit_source_commit_files']}))


if __name__=='__main__':main()
