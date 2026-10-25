"""One-shot adoption of the passing item-ID/thin-side repair, with open scope."""
from pathlib import Path
import datetime,gzip,hashlib,json,shutil
from archive_workspace_hz import inventory
ROOT=Path(__file__).resolve().parents[2];D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-item-side-pv')
LIVE=D/'candidate-v3';PACKET=D/'source-packet-final-v3b';PARENT=ROOT/'build/checkpoints/contact-pause-ps'
FINAL=ROOT/'build/checkpoints/item-side-pv';QA=ROOT/'build/verification/item-side-pv'
EXPECTED='b3dc54bc31f4edcc270fe06593f362f7423bc910155f3bd359d799e2d084c3f5'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def record(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))
def main():
 assert not FINAL.exists()and not(QA/'proof.json').exists(),'Never repeat successful adoption'
 QA.mkdir(parents=True,exist_ok=True);checks={}
 def check(name):
  p=D/name;q=json.loads(p.read_text());assert q['passed']and q['ROM_sha256']==EXPECTED,name;checks[name]=record(p);return q
 assert sha(LIVE/'candidate.nes')==EXPECTED
 q=check('inventory-cpu-v3/proof.json');assert q['ownership_public_call_cases']==118272 and q['spending_cases']==22528
 q=check('query-irq-cpu-v3/proof.json');assert q['paths']==120 and q['injected_IRQ_boundaries']==4740
 q=check('middle-cpu-v3/proof.json');assert q['cell_oracle_cases']==11880 and q['formerly_missed_thin_cells']==1008
 q=check('mixer-cpu-v3/proof.json');assert q['complete_mixer_cases']==2048
 q=check('ui-cpu-v3/proof.json');assert q['outer_cases']==2560 and q['hurt_history_boundary_cases']==2880
 q=check('static-v3/proof.json');assert q['header_and_all_CHR_exact']and q['exact_patch_and_append_ownership']and q['build_only_farcall_counter_delta']==-1
 q=check('performance-proof-v3.json');assert q['measurement_valid']and q['performance_gate_passed']and len(q['runs'])==8
 q=check('samus-native-v3/proof.json');assert q['assertions_removed']is False
 q=check('thin-native-v3/proof.json');assert q['result']['max_world_step']<=8
 before=D/'thin-baseline-v2/proof.json';old=json.loads(before.read_text());assert old['passed']and old['ROM_sha256']==sha(PARENT/'candidate.nes')and old['result']['max_world_step']==13;checks['retained_native_failure']=record(before)
 for key in ['bass','megaman']:
  q=check(key+'-cycle-v3c/proof.json');assert q['result']['physical_item_actors']==2 and q['result']['initial_selection']==0 and q['result']['selection_sequence']==[1,2,0]and q['result']['correct_selected_ammo_pool']
 entries=D/'entries-v3/results.json';q=json.loads(entries.read_text());assert q['rom_sha256']==EXPECTED and q['identities']==len(q['results'])==37 and all(x['exit']==0 for x in q['results'].values());checks['entries']=record(entries)
 for name,row in q['results'].items():
  out=D/'entries-v3'/name.lower().replace(' ','-');assert sha(out/'entry.lua')==row['script_sha256'];p=out/'build/verification/proof.json';result=json.loads(p.read_text());assert result['passed']and result['visibleFrames']>60;checks['entry-'+name]=record(p)
 routes=check('routes-v3/proof.json');assert routes['complete']and len(routes['runs'])==8 and all(x['passed']for x in routes['runs'])
 frames=0
 for row in routes['runs']:
  folder=Path(row['replay_folder']);key=row['identity']+'-'+row['mode'];q=check(folder.relative_to(D).as_posix()+'/proof.json');assert q['complete']and len(q['runs'])==1
  captured=check(folder.relative_to(D).as_posix()+'/direct-'+key+'/proof.json');review=check(folder.relative_to(D).as_posix()+'/review-'+key+'/proof.json')
  assert captured['fixed_inputs_and_trace_exact']and captured['actual_PPU_frame_ids_complete']and captured['raw_gzip_roundtrip_exact']and captured['result']['cleared']and captured['result']['deaths']==0
  assert review['strict_route']['visible_scroll_scanline31_only']and review['strict_route']['body_chr_mismatches']==0;frames+=captured['direct_frames']
 visual=check('visual-review-v3.json');assert visual['root_agent_visual_review']and all(sha(Path(p))==h for p,h in visual['images'].items())
 packet=json.loads((PACKET/'packet.json').read_text());assert packet['passed']and packet['ROM_sha256']==EXPECTED and packet['source_only_roundtrip_exact']and sha(PACKET/'source.zip')==packet['source_zip_sha256']
 assert sha(PACKET/'expanded.nes')==EXPECTED and gzip.decompress((PACKET/'candidate.dbg.gz').read_bytes())==(LIVE/'candidate.dbg').read_bytes()
 parent=json.loads((PARENT/'manifest.json').read_text());assert sha(PARENT/'candidate.nes')==parent['rom_sha256']==packet['parent_ROM_sha256']and sha(PARENT/'source.zip')==parent['source_zip_sha256']
 hashes,changes=packet['source_files'],packet['changes'];assert len(changes)==8
 for n,h in hashes.items():
  assert sha(PACKET/'source'/n)==h
  if n in changes:
   before=changes[n]['before'];assert (not(ROOT/n).exists())if before is None else sha(ROOT/n)==before,n
  else:assert sha(ROOT/n)==h,n
 previous=json.loads((ROOT/'build/verification/contact-pause-ps/proof.json').read_text());public={n:sha(ROOT/'build'/n)for n in previous['unchanged_public_ROMs']};assert public==previous['unchanged_public_ROMs']
 assert {n:packet['builds'][n]for n in ['mmc3','mmc5']}==previous['ordinary_flag_off_hashes']
 required=sum((PACKET/n).stat().st_size for n in ['source.zip','candidate.dbg.gz'])+sum((LIVE/('candidate'+e)).stat().st_size for e in ['.nes','.lbl','.map'])+1_000_000
 assert sum(n for _,n,_ in inventory(ROOT,skip_reparse=True))+required<30_000_000_000
 (QA/'adoption-plan.json').write_text(json.dumps(dict(ROM_sha256=EXPECTED,changes=changes,checks=checks,planned_checkpoint_bytes_with_margin=required),indent=2)+'\n');shutil.copy2(Path(__file__),QA/'adoption-driver.py')
 for n,row in changes.items():
  if row['before']is not None:
   backup=QA/'before'/n;backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/n,backup);assert sha(backup)==row['before']
  (ROOT/n).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(PACKET/'source'/n,ROOT/n);assert sha(ROOT/n)==row['after']
 assert all(sha(ROOT/n)==h for n,h in hashes.items())
 limits=['Private MMC5 item-ID and turtle thin-side repair; full goal remains active.',
  'Eight current-hash strict turtle1-1surface pairs and37cold entries do not certify the other identities/routes or every powerup.',
  'Bit/pool oracles and native physical Samus/Bass/Mega Man cases qualify this repair. Every-item emergence, availability, icon, SFX, ability and expiry matrix remains open.',
  'All8measured native arenas add no lag to the prior build; triple-shot stress still drops21to25draws per120updates. Constant60Hz is not established.',
  'Every physical replay frame is retained. Human overview/local-image inspection is sampled, not exhaustive frame-by-frame visual review.',
  'Native TMNT music PU stays held; current music is preserved. Kirby/Meta source music, remaining source fidelity/performance work and oversizedMMC3 parity remain open.',
  'Ordinary targets, published ROMs and player guide remain unchanged. Start fresh; earlier save states can contain incompatible code/player state.']
 proof=dict(passed=True,goal_complete=False,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),ROM_SHA256=EXPECTED,parent='contact-pause-ps',game_changes=changes,checks=checks,
  source_packet=record(PACKET/'packet.json'),source_only_rebuild_exact=True,ordinary_flag_off_hashes=previous['ordinary_flag_off_hashes'],unchanged_public_ROMs=public,
  current_strict_pairs=8,current_retained_physical_frames=frames,cold_entries=37,limitations=limits)
 (QA/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');FINAL.mkdir()
 for n in ['source.zip','candidate.dbg.gz']:shutil.copy2(PACKET/n,FINAL/n)
 for e in ['.nes','.lbl','.map']:shutil.copy2(LIVE/('candidate'+e),FINAL/('candidate'+e))
 manifest=dict(utc=proof['utc'],status='PRIVATE_ITEM_ID_AND_THIN_SIDE_REPAIR_OPEN_ROSTER_WORK',identities=37,parent_checkpoint='contact-pause-ps',rom_sha256=EXPECTED,source_files=hashes,source_zip_sha256=sha(FINAL/'source.zip'),source_bundle_rebuild=dict(exact=True,stage=str(PACKET)),evidence=record(QA/'proof.json'),limitations=limits,goal_complete=False)
 (FINAL/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');assert all(sha(ROOT/'build'/n)==h for n,h in public.items())
 used=sum(n for _,n,_ in inventory(ROOT,skip_reparse=True));assert used<30_000_000_000
 result=dict(checkpoint=str(FINAL),ROM_SHA256=EXPECTED,source_zip_sha256=manifest['source_zip_sha256'],source_files=len(hashes),workspace_bytes=used,goal_complete=False)
 (QA/'checkpoint.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':main()
