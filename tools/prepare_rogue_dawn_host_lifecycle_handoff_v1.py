"""Freeze private lifecycle with real consumed-input closure and exact scope."""
from pathlib import Path
import json,subprocess,sys
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import rogue_dawn_map_v1 as ref
import prepare_rogue_dawn_host_body_handoff_v1 as previous
O=R/'build/rogue-dawn-host-lifecycle-v1'
REPORT=R/'docs/qa/rogue-dawn-host-lifecycle-f56a-source-2026-10-28.json'

def main():
 assert not(O/'handoff.json').exists(),'Frozen lifecycle unit'
 build=json.loads((O/'build.json').read_text());checks={n:json.loads((O/n).read_text())for n in['controls.json','edge-controls.json','ordinary-controls.json']}
 for proof in[build,*checks.values()]:
  assert proof['passed']
  for row in proof['bindings']:assert ref.binding(row['path'])==row,row['path']
 # Authentic cc65 inputs, distinct from the actual ca65 ASM/incbin list.
 cmd=[str(R/'tools/Windows/cc65/bin/cc65.exe'),'--cpu','6502x','-t','nes','-g','-Oisr','-T','-I',str(R),'--create-full-dep',str(O/'c-full.dep'),'-o',str(O/'c-closure.s')]
 old=build['commands'][0]
 for i,v in enumerate(old):
  if v=='-D':cmd+=['-D',old[i+1]]
 cmd += [str(O/'main.c')]
 p=subprocess.run(cmd,cwd=R,capture_output=True,text=True);(O/'c-closure.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stdout+p.stderr
 adeps=previous.dependencies(O/'assembler-full.dep');cdeps=previous.dependencies(O/'c-full.dep');assert len(adeps)==493 and len(cdeps)==10
 paths=list(dict.fromkeys(adeps+cdeps));primary=checks['controls.json']['checks'];edges=checks['edge-controls.json']['checks']
 def costs(rows):
  values=[r['CPU_delta']for r in rows];return dict(minimum=min(values),maximum=max(values),distinct=sorted(set(values)))
 ordinary=checks['ordinary-controls.json']['rows']
 summary=dict(
  status='PRIVATE source-qualified lifecycle/injury/visibility successor; NOT playable or native admission',native_run=False,
  ROM=ref.binding(O/'candidate.nes'),parent=ref.binding(R/'build/rogue-dawn-host-body-v1/candidate.nes'),shared_family_parent=ref.binding(R/'build/roster-shared-celeste-small-chr-v1.nes'),
  layout=dict(new_code_physical_bank=95,start='B803',exclusive_end=build['life_end'],bytes=build['life_bytes'],free_before_root_BF00=build['life_free_to_descriptor_tail'],root_death_records='BF00..BF31 / C95DF00..DF31',death_CHR_page=689,new_RAM_bytes=0,exact_owner='SelectedCharacter2 AND RdVariant1 before every source-overlay read',old_public_PCs='exact; compile-time farcall count only differs'),
  intended_hook_changes=build['old_hook_spans'],literal_frozen_spans=build['literal_frozen_spans'],
  source_and_adaptation=dict(
   original_source_ROM=ref.binding(ref.ROM),source_core='Original CORE4090/AUX508/C94ART3150/C94bridge175 remain literal. Only service3 JMP target changes in existing A95 prefix.',
   source_draw='372 actual old pose/F7/facing/P callback comparisons retain fullAXYP/radius/pointer/C94 and virtual-context-B X exactly.',
   death_draw='Source frame35 (hex) genuine draw callback selects distinct rightDF00/leftDF19 descriptors while C94 remains mapped for callback return. Radius0/0, authentic virtual prior cursor0 source returnX24/Y12. Final body graphics and first record mapC95. No frozen ContextB table edit.',
   death_art=ref.binding(R/'build/rogue-dawn-death-art-v1/handoff.json'),death_asset_report=ref.binding(R/'docs/qa/rogue-dawn-death-art-source-2026-10-28.json'),
   ordinary_contact='Explicit authored SMB ordinary-contact8HP, genuine sourceBCD arithmetic/Suit4HP; no Hard multiplier. Full enemy eligibility and actual native contact remain separate from projectile damage HP mapping.',
   eligible_actor_IDs_hex=['00','01','02','03','04','05','06','07','08','09','0A','0B','0D','0E','0F','11','12','14','33'],
   class_limits='Only native ObjectOffset0..4, Enemy_Flag1 and not Enemy_State bit20; IDs01/04 are explicitly listed native table entries with unnamed/NoInitCode provenance, not an invented named enemy. Native flying-green10, Podoboo0C, Bowser2D/flame15, firebars1B..20, hammers/misc and unknown classes are NOT admitted by this contact unit. Returning protected is a bounded implementation blocker for playable admission, not a claim these hazards are harmless.',
   recoil='Actual full-page attacker relation sets sourceHit20 or28; negative sourceContactFlags80 invokes authentic50-clock/F7 blink. Source clock/action/recoil continuation remains literal.',
   life='Explicit approved SMB adaptation: retain gear/tanks/maxmissiles/currentmissiles, refill source tank-capacityBCD health on real life loss; scene resets only active/action. Fresh game resets original defaults/BCD99. No life-mismatch detector, AreaPointer snapshot or new marker.',
   death_clock='Genuine native KillPlayer97D6 -> source death start -> actual PlayerDeath original SamusDeathUpdate180/150 host clock -> native PlayerLoseLife. This host clock is an explicit SMB transition adaptation; no generic Samus motion or original Rogue room timing claim.',
   source_audio='OPEN. Root identified actual original C0D9->C215->A49A770/A776/B3B4 plus six lower songbanks. These tests initialize real host native audio only to qualify interrupts, not Rogue audio playback.'),
  lifecycle_contracts=dict(
   fresh='Real NrFreshGameInit last-child target, after original generic clearing; private owner must already be selected. Continue skips this native fresh owner. This packet does not implement a menu variant toggle.',
   area='Real InitializeArea target calls genuine complete MegaManResetArea before source initialization, skips old Z2 overlay clear, then permits original InitializeMemory and real data setup. Explicit MmDeathFlag snapshot identifies death; HP0 also refills legal cap without discarding earned equipment.',
   active='Both real GuestGameRoutinesBridge paths normalize stale legacy hurt/size aliases before genuine GameRoutines. Rogue UI slot skips dormant native Samus inventory so it cannot write the source overlay. Native PauseRoutine stays original.',
   visibility='SourceF7 hides; admitted current source frames show. Actual Main no longer needs GuestHurtKind/InjuryTimer/MMdeath/powerup0 preconditions. MmDeathFlag is only cleared as stale in live engine8/action<7; genuine engine11 death is retained.',
   source_resources='CPU arenas explicitly initialize owned source resources/actors as declared inputs, not genuine native earned collection. No native acquisition claim.',
   future_union='Frozen constructor42B remains124AD9B..ADC4, conflicts with B private router finish. Proposed approved future rehomeADA4..ADCD is not applied here. Future52B GuestGameRoutinesBridge must retain RdLifeCheatRoutines and RdLifeGameRoutines targets, not copy this old E overlay.'),
  actual_counts={k:len(v)if isinstance(v,list)else v for k,v in primary.items()},
  edge_counts={k:len(v)if isinstance(v,list)else v for k,v in edges.items()},
  actual_stack=dict(all_controls_minimum_SP=min(checks['controls.json']['minimum_SP'],checks['edge-controls.json']['minimum_SP']),full_Main_contact_natural_injury_SP=238,full_Main_contact_minimum_SP=min(x['minimum_SP']for x in primary['actual_full_Main_enemy_contact_injury_admission']),full_Main_initial_area_minimum_SP=min(x['minimum_SP']for x in primary['genuine_IdleLoop_Main_initial_area_caller']),full_Main_death_minimum_SP=min(x['minimum_SP']for x in primary['continuous_full_Main_NMI_death_clock_and_real_life_loss']),direct_reset_entry_SP=224,direct_full_InitializeArea_entry_SP=240,protected_constructor_stack_floor=128),
  costs=dict(foreign_full_Main_vs_frozen_body_CPU=costs(edges['all_foreign_full_Main_application_ordered_writes_AXYP_banks']),foreign_public_caller_CPU={name:costs([x for x in edges['foreign_real_public_return_callers']if x['caller']==name])for name in sorted(set(x['caller']for x in edges['foreign_real_public_return_callers']))},unchanged_source_callback_new_dispatch_CPU=costs(edges['all_old_source_draw_callback_returns_and_context_exact']),no_zero_cost_FPS_deadline_claim=True),
  ordinary_flagoff=[dict(mapper=r['mapper'],ROM=r['ROM'])for r in ordinary],
  input_closure=dict(actual_ASM_incbin_files=len(adeps),actual_C_preprocessor_files=len(cdeps),unique_consumed_files=len(paths),C_command=cmd,ASM_command=build['commands'][0],scope='Genuine ca65/cc65 full-dependency outputs; exact linker/build tools/postprocessor also bound. Sparse caller staging only; no full source/runtime copy.'),
  retained_negatives=dict(body_handoff=ref.binding(R/'build/rogue-dawn-host-body-v1/handoff.json'),body_address_erratum=ref.binding(R/'build/rogue-dawn-host-body-v1/hook-address-erratum.json'),immediate_ControlStep192=ref.binding(R/'build/rogue-dawn-host-transactions-v3/control-SP192-negative.json'),standalone_flush192=ref.binding(R/'build/rogue-dawn-host-deferred-v1/control-SP192-deferred-negative.json'),two_Proto_typed_catchup_FALSEs=ref.binding(R/'build/rogue-dawn-host-body-v1/body-edge-controls.json'),scope='All old packets/negatives remain literal. The old flush192 standalone negative is a separate contract from safe callback-only ControlStep192/natural Main. Two Proto catch-up fixtures remain unqualified and no product/shared audio cause is accepted.'),
  still_open=['Actual physical PPUMASK/deadline/DMA/CHR/OAM/visible-pixel native qualification','Fresh menu/RdVariant acquisition and private router/body constructor union','Typed emerging item contact/art/announcement and actual earned gear campaign','Source beam/missile/bomb/Screw HP/freeze/boss consumers and all ordinary native classes','Hazard/boss contact damage classes not listed above','Authentic Rogue audio driver/data/SFX closure','Full playable/game room/SMB transition and mode coverage'],
  old_lifecycle_scope='This successor closes bounded real native-owner CPU paths only. It does not retag earlier body-only packet as lifecycle/native qualified.')
 REPORT.write_text(json.dumps(summary,indent=2)+'\n')
 extras=[Path(__file__),REPORT,O/'build.json',O/'controls.json',O/'edge-controls.json',O/'ordinary-controls.json',O/'c-full.dep',O/'c-closure.s',O/'c-closure.log',R/'tools/Windows/cc65/bin/cc65.exe',R/'tools/Windows/cc65/lib/nes.lib',O/'candidate.cv3-mirror.json',R/'tools/prepare_rogue_dawn_host_body_handoff_v1.py']
 tools=['prepare_rogue_dawn_host_lifecycle_v1.py','rogue_dawn_host_lifecycle_controls_v1.py','rogue_dawn_host_lifecycle_edges_v1.py','rogue_dawn_host_lifecycle_ordinary_v1.py','prepare_rogue_dawn_host_lifecycle_handoff_v1.py']
 extras += [R/'tools'/n for n in tools]+[Path(x['path'])for x in build['bindings']]
 extras += [Path(x['path'])for d in checks.values()for x in d['bindings']]
 extras += [R/'build/rogue-dawn-host-body-v1/hook-address-erratum.json',R/'build/rogue-dawn-host-body-v1/body-edge-controls.json',R/'build/rogue-dawn-host-transactions-v3/control-SP192-negative.json',R/'build/rogue-dawn-host-deferred-v1/control-SP192-deferred-negative.json']
 bindings=[ref.binding(p)for p in dict.fromkeys(paths+extras)]
 owned=[R/'src/rogue_dawn_host_lifecycle.s',REPORT,*[R/'tools'/n for n in tools]]
 owned += [O/n for n in ['entrypoint.s','main.c','private.cfg','player.s','luigi_native.s','megaman_weapons.s','object.s','new_roster_dispatch.s','zelda2_link_platform.s','legacy-player-prg.s','control-include.s','services-include.s','art-include.inc','bridge-include.s','movement-flush.s','game.s','guest_injury.s','guest_body_contact.s','collision.s','megaman_death.s','source.patch','assembler-full.dep','c-full.dep','c-closure.s','c-closure.log','build.json','controls.json','edge-controls.json','ordinary-controls.json','candidate.cv3-mirror.json']]
 packet=dict(passed=True,source_only=True,native_run=False,playable_admission=False,ROM_sha256=build['ROM_sha256'],report=ref.binding(REPORT),bindings=bindings,owned_publication_files=[ref.binding(p)for p in owned],runtime_artifacts_no_public_copies=[ref.binding(O/('candidate'+s))for s in['.nes','.dbg','.lbl','.map']],preserved_old_negative_contracts=True)
 (O/'handoff.json').write_text(json.dumps(packet,indent=2)+'\n')
 print(json.dumps(dict(ROM_sha256=build['ROM_sha256'],handoff_sha256=ref.digest((O/'handoff.json').read_bytes()),report_sha256=ref.digest(REPORT.read_bytes()),bindings=len(bindings),owned=len(owned),ASM_inputs=len(adeps),C_inputs=len(cdeps))))
if __name__=='__main__':main()
