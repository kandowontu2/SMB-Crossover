"""Freeze the bounded standalone Dragon Power source packet; no native action."""
import json
import dragon_power_component_v1 as B

def main():
 out=B.OUT;root=B.ROOT;D=B.D
 notes=[
  dict(kind='literal_saved_build_failure',evidence=D.binding(out/'first-build-failure.txt'),
       correction='Explicit real native R2/R3 bindings added; final component builds'),
  dict(kind='observed_unbound_projection_drafts_no_old_binary_or_full_log_saved',
       observations=['Source984D scene-exit boundary and EC60 data table initially unresolved',
        'ED1C really falls through into external ED2C: explicit relocated JMP now emitted',
        'Single E82E leaf final A/dispatch-high forecast differed; genuine complete E82E then EC4D caller resolves real continuation without masks',
        'IRQ model software-B marker differed21/31; NV/D/I/Z/C physical flags now strict and entireSMCCODE restore asserted'],
       scope='These are transparent draft notes, not fabricated retained ROMs or literal full failing logs'),
  dict(kind='observed_unbound_fullMovement_brick_control_failure',
       first_difference=['camera0','brick','tick_index7','original0407',128,'projected5C47',0],
       cause='Draft Movement cleared pending block command every tick before a genuine consumer',
       correction='Removed both pending command clears; actual source pending-state equality passes all2160updates',
       scope='Actual console failure summarized; no old binary or full native evidence claimed'),
  dict(kind='source_audit_negative_frozen_separately',
       evidence=D.binding(root/'build/dragon-power-source-v1/first-control-negative.json'),
       correction='Authentic air steering and13/21complete attack durations were measured rather than guessed')]
 neg=out/'draft-negatives.json';neg.write_text(json.dumps(notes,indent=2)+'\n')
 leaves=[root/'src'/n for n in ['dragon_power.s','dragon_power_state.inc','dragon_power_native.inc',
  'dragon_power_host.s','dragon_power_render.s','dragon_power_contact.s','dragon_power_art.inc']]
 owned=leaves+[root/'chr/characters/dragon-power.chr',root/'docs/qa/dragon-power-component-2026-10-28.txt']
 owned +=[root/'tools'/n for n in ['dragon_power_port_v1.py','dragon_power_component_v1.py',
  'dragon_power_controls_v1.py','dragon_power_art_v1.py','dragon_power_host_controls_v1.py',
  'dragon_power_wrapper_controls_v1.py','dragon_power_freeze_v1.py']]
 receipts=[out/n for n in ['art-controls.json','source-controls.json','host-controls.json','wrapper-controls.json','layout-controls.json','draft-negatives.json']]
 products=[out/n for n in ['component.bin','art.bin','chr.bin','component.dbg','component.lbl','component.s','component.cfg','candidate.nes','first-build-failure.txt']]
 core=D.binding(out/'component.bin');art=D.binding(root/'src/dragon_power_art.inc');chr=D.binding(root/'chr/characters/dragon-power.chr')
 for p,key in [('source-controls.json','compiled'),('host-controls.json','core'),('wrapper-controls.json','core')]:
  q=json.loads((out/p).read_text());assert q[key]['sha256']==core['sha256']
 a=json.loads((out/'art-controls.json').read_text());assert a['ART']['sha256']==art['sha256']and a['CHR']['sha256']==chr['sha256']
 layout=json.loads((out/'layout-controls.json').read_text())
 assert layout['candidate']['sha256']==D.binding(out/'candidate.nes')['sha256']
 assert layout['component_debug']['sha256']==D.binding(out/'component.dbg')['sha256']
 inputs=[B.HOST.with_suffix('.'+ext)for ext in B.EXPECTED]+[D.ROM,
  root/'build/dragon-power-source-v1/handoff.json',root/'build/dragon-power-allocator-v1.json']
 inputs +=[root/'tools'/n for n in ['dragon_power_map_v1.py','dragon_power_reference_v1.py','dragon_power_allocator_v1.py']]
 inputs +=[root/'tools/audit/verify_native_relocation.py',root/'tools/Windows/cc65/bin/ca65.exe',root/'tools/Windows/cc65/bin/ld65.exe']
 for ext,h in B.EXPECTED.items():assert D.binding(B.HOST.with_suffix('.'+ext))['sha256']==h
 handoff=dict(status='FROZEN_PRIVATE_FIRST_FIGHTING_SOURCE_COMPONENT_ONLY_NO_NATIVE_OR_PLAYABLE_CLAIM',
  character=dict(raw24='Goku, authenticated US Dragon Power',Mushroom='ordinaryPole+food20 cap150; preserveshigherFlower',
   Flower='plainWave+3 cap60 with source kind-priority; preservesPole',Easy='normalstomppermission',Hard='nativeattacks'),
  core=core,candidate=layout['candidate'],all_other_parent_bytes_exact=layout['all_other_bytes_exact'],
  sizes=dict(CORE=4121,CORE_end_inclusive='86:B818',ART=1263,ART_end_inclusive='85:CDEE',CHR=8192,used_CHR_pages=6),
  finite_controls=dict(original_source_updates=1800,public_Movement_updates=2160,pickup_cases=360,
   original_health_campaigns=72,original_health_updates=9216,queued_health_cases=30,source_point_cases=588,
   rendered_poses_facings_and_wave_cases=66,foreign_calls=4080,actual_parent_IRQ_injections=578,
   source_paired_added_cycles=[1593,2136],whole_Movement_cycles=[3411,4154],render_cycles=[770,1824]),
  owned_files=[D.binding(p)for p in owned],receipts=[D.binding(p)for p in receipts],
  products=[D.binding(p)for p in products],immutable_inputs=[D.binding(p)for p in inputs],
  reproducible_commands=['python tools/dragon_power_port_v1.py','python tools/dragon_power_art_v1.py',
   'python tools/dragon_power_controls_v1.py','python tools/dragon_power_host_controls_v1.py',
   'python tools/dragon_power_wrapper_controls_v1.py','python tools/dragon_power_component_v1.py --overlay',
   'python tools/dragon_power_freeze_v1.py'],
  ROOT_next='Review source/API and recheck actual final allocator; shared integration and all native launches remain ROOT-owned',
  remaining=['actual host enemy HP/eligibility/repeat-hit and queuedblock/score/VRAM acknowledgment',
   'genuine selection/newgame/transition/pipe/pit/death and raw24dispatch/name/palette composition',
   'authentic audio driver/adapter/cue producer-consumer/mixer/sharedSFX/lifecycle/cadence',
   'remaining original inventory and explicit authored overhead-only Super/Thunder/coloredpole adaptations',
   'native coldmenu/PPU/DMA/NMI/IRQ/cadence/fullroute/replay qualification'],
  no_shared_edits_no_Mesen=True)
 p=out/'handoff.json';p.write_text(json.dumps(handoff,indent=2)+'\n')
 print(json.dumps(dict(handoff=D.binding(p),owned=len(owned),bindings=len(owned)+len(receipts)+len(products)+len(inputs)),indent=2))
if __name__=='__main__':main()
