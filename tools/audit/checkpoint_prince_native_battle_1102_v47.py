"""Compact exact source/receipt/code checkpoint; no ROM, DBG or art tree."""
from pathlib import Path
import hashlib,json,sys,zipfile
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import prepare_prince_successor_manifest_1102_v26 as M
O=M.O
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
 names=['recover_prince_player_reaction_1102_v31.py','measure_prince_palette_contact_1102_v32.py','record_prince_contact_continuation_1102_v33.py','recover_prince_combat_tail_1102_v34.py','audit_prince_carrier514_1102_v35.py','check_prince_combat_tail_1102_v36.py','prepare_prince_pose_grid_1102_v37.py','check_prince_pose_grid_native_1102_v38.py','measure_prince_native_proxy_1102_v40.py','check_prince_native_proxy_1102_v41.py','measure_prince_native_link_1102_v42.py','check_prince_native_link_1102_v43.py','prepare_prince_cold_link_1102_v44.py','check_prince_cold_link_1102_v45.py','audit_prince_battle_lifetime_1102_v46.py','checkpoint_prince_native_battle_1102_v47.py']
 sources=[R/'tools/audit'/n for n in names]+[R/'docs/qa/prince-native-battle-1102-v47.md']
 receipts=['player-reaction-CPU-v31.json','player-policies-measurement-v32.json','contact-continuation-negative-v33.json','combat-tail-recovery-v34.json','extra-carrier514-v35.json','extra514-smb3-v35.json','extra514-publication-v35.json','combat-tail-CPU-v36.json','pose-grid-CPU-v37.json','pose-grid-native-CPU-v38.json','native-proxy-measurement-v40.json','native-proxy-negative-v41.json','native-proxy-CPU-v41.json','native-link-measurement-v42.json','native-link-CPU-v43.json','cold-link-storage-v44.json','cold-link-CPU-v45.json','battle-lifetime-proposal-v46.json']
 for name in receipts:
  q=json.loads((O/name).read_text())
  for key,digest in q.get('bindings',{}).items():assert sha(R/key)==digest,(name,key)
 generated=['combat-original-v34.bin','prince-pose-grid-v37.bin','pose-grid-helper-v37.bin','grid-render-v37.bin','grid-render-labels-v37.lbl','native-runtime-v42.bin','native-metadata-v42.bin','native-contact-v42.bin','native-fresh-v42.bin','native-labels-v42.json']
 for stem in ['combat-tail-v34','native-proxy-v40','native-battle-v40','native-services-v42','native-battle-v42','native-proxy-v42','native-public-v42','native-policies-v42','cold-worker-v44']:generated.extend(stem+suffix for suffix in ['.s','.cfg','.lbl','.bin'])
 members={p.relative_to(R).as_posix():p for p in sources}
 members.update({'receipts/'+n:O/n for n in receipts});members.update({'generated/'+n:O/n for n in generated});assert len(members)==len(sources)+len(receipts)+len(generated)
 archive=O/'native-battle-source-v47.zip'
 with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for name,path in sorted(members.items()):assert path.is_file(),path;z.writestr(name,path.read_bytes())
 with zipfile.ZipFile(archive)as z:
  assert set(z.namelist())==set(members)
  for name,path in members.items():assert z.read(name)==path.read_bytes(),name
 assert archive.stat().st_size<160000
 files=[p for p in O.rglob('*')if p.is_file()];q=dict(passed=True,private_source_checkpoint=True,ROM_written=False,installed=False,menu_admitted=False,base_SHA256=M.A.PIN,checkpoint=archive.relative_to(R).as_posix(),checkpoint_SHA256=sha(archive),checkpoint_bytes=archive.stat().st_size,checkpoint_members=len(members),explicit_source_commit_files=[p.relative_to(R).as_posix()for p in sources],member_SHA256={name:sha(path)for name,path in sorted(members.items())},active_output=O.relative_to(R).as_posix(),active_output_bytes=sum(p.stat().st_size for p in files),active_output_files=len(files),physical=dict(granted_pages=44,used=44254,spare=802),RAM2=dict(metadata_bytes=6050,end=0xdfa2,remaining_before_shared_clock=46),qualified=dict(original_battle_differentials=2976,original_code_bytes=695,native_service_ISR_cuts=2122,grid_render_ISR_cuts=1754,actual_typed_cold=True),required='Root exact tail/renderer/cold fragment amendment; source-derived remaining native collision/pickup/death-loop policies; actual new manager/cookie foreign/auth/fresh/scene before root native queue. No helper placed.')
 (O/'native-battle-checkpoint-v47.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['member_SHA256','explicit_source_commit_files']}));print(json.dumps(q['explicit_source_commit_files']))


if __name__=='__main__':main()
