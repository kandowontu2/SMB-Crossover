"""Freeze only compact Bass source/results; never copy a source tree/capture."""
from pathlib import Path
import hashlib,json
from check_tmnt_audio_fallback_oc import qualified
from check_tmnt_render_oa import address
from link_pit_rygar_sophia_audit_cpu import scoped_load
from bass_corner_source_cpu_v1 import setup,run,fixed
R=Path(__file__).resolve().parents[2];B=R/'build';P=R/'tools/audit/proposals'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
q=json.loads((B/'bass_corner_working_result.json').read_text())
cpu=json.loads((B/'bass_corner_source_controls.json').read_text())
ordinary=json.loads((B/'bass_corner_flagoff_controls.json').read_text())
assert q['exit']==0 and cpu['passed']and ordinary['passed']
assert cpu['candidate_sha256']==q['candidate_ROM_sha256']==sha(B/'bass_corner_private.nes')
old=qualified(B/'smb-crossover-mmc5-expanded.nes');new=qualified(B/'bass_corner_private.nes')
exceptions={'Z2PostBGBodyBridge::Done','Z2PostBGBodyBridge::Handle','_FARCALL_COUNT'}
exceptions|={'KbLegacyExpandedCollisionAdder::'+n for n in ['Short','Yes','Crouch','Medium','Luigi','Scrooge']}
exceptions|={'KbLegacyExpandedCollisionBox::'+n for n in ['Short','Crouch','Medium','Done','Scrooge']}
changed={'::'.join(n):[v,new.get(n)]for n,v in old.items()if new.get(n)!=v}
assert set(changed)==exceptions,changed
assert set(map(int,q['changed_banks']))=={71,72,78,89}and q['all_other_header_CHR_exact']
bs=[scoped_load(B/n)for n in ['smb-crossover-mmc5-expanded.nes','bass_corner_private.nes']]
costs=[]
for state,vy,body in [(0,0,12),(1,65536,13),(1,-5*65536,13)]:
 row=[]
 for b in bs:
  x=setup(b,Player_State=state,Player_Y_Position=160,Player_Y_Speed=(vy>>16)&255,Player_BoundBoxCtrl=body)
  fixed(x,'MmVY',vy,3);c,_,_=run(x,'PlayerBGCollision');row.append(c.processorCycles)
 costs.append(dict(state=state,source_vy_Q16=vy,body=body,baseline=row[0],candidate=row[1],delta=row[1]-row[0]))
primary={}
for rel in q['source_changed_files']:
 f=R/rel
 if f.exists():primary[rel]=sha(f)
assert sha(B/'smb-crossover-mmc5-expanded.nes')==q['base_ROM_sha256']
files=[P/'bass_corner_source.patch',P/'bass_corner_profile.inc',B/'bass_corner_working_result.json',
 B/'bass_corner_source_controls.json',B/'bass_corner_flagoff_controls.json',B/'bass_corner_history.jsonl',
 B/'bass_corner_private.nes',B/'bass_corner_private.dbg',B/'bass_corner_private.lbl',B/'bass_corner_private.map',
 R/'tools/audit/bass_corner_sparse_build_v1.py',R/'tools/audit/bass_corner_source_cpu_v1.py',
 R/'tools/audit/bass_corner_flagoff_v1.py',Path(__file__),R/'docs/qa/inventory-timing-adoption-2026-10-26.json',
 R/'reference/crossover2/source.swf',R/'reference/crossover2/extracted/scripts/com/smbc/characters/Bass.as',
 R/'reference/crossover2/extracted/scripts/com/smbc/characters/Character.as',
 R/'reference/crossover2/extracted/scripts/com/smbc/data/HitTester.as']
files += [B/n for n in ['bass_corner_kirby_legacy.s','bass_corner_kirby.s','bass_corner_profile.inc','bass_corner_tmnt_probe_gates.s',
 'bass_corner_tmnt.s','bass_corner_zelda2_link_platform.s','bass_corner_entrypoint.s','bass_corner.cfg','bass_corner_main.c']]
proof=dict(passed=True,source_only=True,native_run=False,adopted=False,source_copies=0,new_output_trees=0,
 baseline_ROM=q['base_ROM_sha256'],candidate_ROM=q['candidate_ROM_sha256'],
 actual_changed_banks=q['changed_banks'],CHR_header_other_PRG_exact=True,
 old_qualified_symbols=len(old),unchanged_qualified_symbols=len(old)-len(changed),
 genuine_private_symbol_changes=changed,all_old_RAM_addresses_unchanged=True,
 primary_changed_file_base_hashes=primary,source_overlay_files=q['source_changed_files'],
 counts=cpu['counts'],getter_foreign_costs=cpu['costs'],whole_Bass_empty_BG_costs=costs,
 ordinary_target_hashes={r['mapper']:r['actual']for r in ordinary['rows']},
 scope='Source repair for Bass9/variant0 ordinary rising, previous-horizontal-overlap ceiling contacts; live Q16 separation through actual native block effects. Genuine wall code remains exact.',
 limits=['No native/PPU/cadence qualification; extra foreground cost is material.',
 'Simultaneous diagonal calcAxis corners retain conservative side behavior; this does not implement the full original collision solver.',
 'Hurt/sliding ceiling response retains legacy ownership; authenticated pose profiles are tested separately.',
 'Under-HUD half-pixel head admission remains the existing outer integer cutoff.',
 'Old ce635 raw/snapshots were deleted independently; no deleted evidence was reconstructed. Selected original geometry/failure JSON survives.',
 'Private source was compiled from explicit3b primary inputs. Reproduce later from the3b adoption revision plus sparse patch; future primary menus are a separate composition.'],
 bindings={str(f.resolve()):sha(f)for f in files})
out=B/'bass_corner_final_source.json';out.write_text(json.dumps(proof,indent=2)+'\n')
print(json.dumps(dict(proof=str(out),sha256=sha(out),candidate=proof['candidate_ROM'],costs=costs,bindings=len(files)),indent=2))
