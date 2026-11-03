"""Compact exact current source/proof checkpoint; no ROM or dependency expansion."""
from pathlib import Path
import hashlib,json,sys,zipfile
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_current_cold_1102_v98 as C
O=C.O
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
 b,manifest=C.image();q=json.loads((O/'frontend-proposal-v109.json').read_text());assert manifest['passed']and q['passed']
 names=['prepare_prince_current_post_return_1102_v97.py','check_prince_current_cold_1102_v98.py','check_prince_current_cold_1102_v99.py','check_prince_current_respawn_1102_v100.py','check_prince_current_respawn_1102_v101.py','check_prince_current_game_loop_isr_1102_v102.py','check_prince_current_foreign_1102_v103.py','check_prince_current_nested_irq_1102_v104.py','prepare_prince_frontend_proposal_1102_v106.py','prepare_prince_frontend_proposal_1102_v107.py','check_prince_current_native_ingress_1102_v108.py','prepare_prince_frontend_proposal_1102_v109.py','check_prince_current_player_pipeline_1102_v110.py','check_prince_current_render_retire_1102_v111.py','check_prince_current_I1_lag_1102_v112.py','check_prince_frontend_source_1102_v113.py','check_prince_current_earned_defeat_1102_v114.py']
 sources=[R/'tools/audit'/n for n in names]+[R/'tools/reference/prince_frontend_1102_v109.inc',R/'docs/qa/prince-current-native-1102-v115.md',Path(__file__)]
 proofs=['post-return-manifest-v97.json','current-shared-cold-CPU-v99.json','post-return-respawn-CPU-v101.json','current-game-loop-ISR-CPU-v102.json','current-foreign-hot-CPU-v103.json','post-return-nested-IRQ-CPU-v104.json','current-native-ingress-CPU-v108.json','frontend-proposal-v109.json','player-pipeline-CPU-v110.json','current-render-retire-CPU-v111.json','current-I1-lag-CPU-v112.json','frontend-source-CPU-v113.json']
 for n in proofs:
  row=json.loads((O/n).read_text());assert row['passed'],n
  for path,digest in row.get('bindings',{}).items():assert sha(R/path)==digest,(n,path)
 negatives=['current-shared-cold-negative-v98.json','post-return-respawn-negative-v100.json','frontend-negative-v106.json','frontend-negative-v107.json','frontend-negative-v109.json','frontend-aliased-mask-negative-v109.json','current-earned-defeat-negative-v114.json']
 failure=json.loads((O/negatives[-1]).read_text());assert not failure['passed']and 'SMC'not in failure.get('exception','') # The actual full exception retains byte-level smc before/after.
 assert "('lagNMI', (346, 130, 195))"in failure['exception']
 components=['post-owner-v97.s','post-owner-v97.cfg','post-owner-v97.lbl','post-owner-v97.bin','post-owner-extra-v97.bin','post-selector-v97.s','post-selector-v97.cfg','post-selector-v97.lbl','post-selector-v97.bin','native-labels-v78.json']
 for name in ['resolver','masks']:
  for suffix in ['s','cfg','lbl','bin']:components.append(f'frontend-{name}-v113.{suffix}')
 previous=O/'post-return-source-v95.zip';assert sha(previous)=='0f0a47316b5f7dc9c5da6ce8c490ad0f0536747474a2a6399bf637ac80d72ae3'
 files=sources+[O/n for n in proofs+negatives+components];assert len(files)==len(set(files))
 archive=O/'current-source-v115.zip';assert not archive.exists(),'Frozen checkpoint already exists'
 with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for p in files:z.writestr(p.relative_to(R).as_posix(),p.read_bytes())
 with zipfile.ZipFile(archive)as z:
  assert len(z.namelist())==len(files)
  for p in files:assert hashlib.sha256(z.read(p.relative_to(R).as_posix())).hexdigest()==sha(p)
 out=dict(passed=True,frozen=True,ROM_written=False,menu_admitted=False,installed=False,native_ready=False,blocker='v114 actual original-earned native defeat FF-lag NMI stack/SMC overwrite; no combat ISR/native admission.',parent_memory_SHA256=manifest['parent_memory_SHA256'],gameplay_memory_SHA256=manifest['expected_memory_only_SHA256'],separate_frontend_proposal_memory_SHA256=q['expected_memory_only_SHA256'],archive=archive.relative_to(R).as_posix(),archive_SHA256=sha(archive),archive_bytes=archive.stat().st_size,archive_members=len(files),source_files_to_commit=[p.relative_to(R).as_posix()for p in sources],members={p.relative_to(R).as_posix():dict(SHA256=sha(p),bytes=p.stat().st_size)for p in files},prior_frozen_dependency=dict(durable_root='docs/qa/checkpoints/2026-11-02/prince-post-return-v95',archive_SHA256=sha(previous),not_copied_or_expanded=True),active_output=O.relative_to(R).as_posix(),next='Measure owned original-strike queue/shallower native delivery, preserve event order/multiplicity/identity/retirement and actualGameLoop FF-NMI/nestedIRQ. Root reviews menu before ROM composition and owns Mesen/install/Git. Original music/SFX mapping remains incomplete; no helpers added.')
 out['active_output_files']=sum(p.is_file()for p in O.rglob('*'));out['active_output_bytes']=sum(p.stat().st_size for p in O.rglob('*')if p.is_file());assert out['active_output_files']<1000 and out['active_output_bytes']<256000000
 (O/'current-checkpoint-v115.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k not in ['members','source_files_to_commit']}))


if __name__=='__main__':main()
