"""Compact authentic audio handoff; never calls a build or native process."""
import json
import dragon_power_audio_prepare_v1 as A
def main():
 D=A.D;root=A.ROOT;out=A.OUT
 owned=[root/'src/dragon_power_audio.s',root/'src/dragon_power_audio_native.inc',
  root/'tools/dragon_power_audio_prepare_v1.py',root/'tools/dragon_power_audio_controls_v1.py',
  root/'tools/dragon_power_audio_freeze_v1.py',root/'docs/qa/dragon-power-audio-2026-10-28.txt']
 products=[out/n for n in ['component.bin','component.dbg','component.lbl','component.s','component.cfg','build.json',
  'source-callback-controls.json','first-parent-silent-owner-negative.json']]
 inputs=[A.B.HOST.with_suffix('.'+ext)for ext in A.B.EXPECTED]+[D.ROM,
  root/'build/dragon-power-component-v1/handoff.json',root/'build/dragon-power-allocator-v1.json',
  root/'tools/dragon_power_map_v1.py',root/'tools/dragon_power_reference_v1.py',
  root/'tools/dragon_power_component_v1.py',root/'tools/dragon_power_host_controls_v1.py',
  root/'tools/audit/verify_native_relocation.py',root/'tools/Windows/cc65/bin/ca65.exe',root/'tools/Windows/cc65/bin/ld65.exe']
 fighting=json.loads((root/'build/dragon-power-component-v1/handoff.json').read_text())
 for name in ['owned_files','receipts','products','immutable_inputs']:
  for row in fighting[name]:assert D.binding(row['path'])==row,('frozenFightingChanged',row['path'])
 q=json.loads((out/'source-callback-controls.json').read_text());b=json.loads((out/'build.json').read_text())
 assert q['core']==D.binding(out/'component.bin')==b['compiled']
 assert b['total_bytes']==5445 and q['state_owner'].startswith('RgAudioRam')
 rec=dict(status='FROZEN_AUTHENTIC_AUDIO_SOURCE_CLOSURE_NO_SHARED_SCHEDULER_OR_NATIVE',
  core=D.binding(out/'component.bin'),extent='physical96/$60 A980..BEC4;5445of5760B',
  source_projection_bytes=5152,adapter_bytes=293,free_bytes=315,
  state='exclusive raw24 RgAudioRam137B plus RgAudioCpuZp5B; no new RAM, RgAudioZp not driver storage',
  owned_files=[D.binding(p)for p in owned],products=[D.binding(p)for p in products],immutable_inputs=[D.binding(p)for p in inputs],
  proof_summary=dict(public_source_ticks=q['public_ticks'],raw_driver_ticks=q['raw_driver_AXYP_SP_ticks'],
   raw_request_cases=q['raw_request_AXYP_SP_cases'],foreign_calls=q['foreign_calls'],
   actual_parent_IRQ=len(q['actual_parent_IRQ_injections']),actual_mixer_ticks=24,
   callback_cycles=q['callback_cycles'],source_cycles=q['original_cycles'],paired_added_cycles=q['added_cycles']),
  retained_negative='Actual parentSilent corrupted original draft RgAudioZp audio state; new base fixes real ownership, same source/mixer/IRQ controls',
  ROOT_required=['safe committed Main cue publication; no partial frozen fighting vector reads from NMI',
   'actual shared audio dispatch/Begin/Finish/previous-DMC release/scene and pause/title/death lifecycle',
   'final actual allocator/source link and native audio/render/cadence acceptance'],
  commands=['python tools/dragon_power_audio_prepare_v1.py','python tools/dragon_power_audio_controls_v1.py',
   'python tools/dragon_power_audio_freeze_v1.py'],no_Mesen_or_shared_edits=True)
 p=out/'handoff.json';p.write_text(json.dumps(rec,indent=2)+'\n')
 print(json.dumps(dict(handoff=D.binding(p),owned=len(owned),bindings=len(owned)+len(products)+len(inputs)),indent=2))
if __name__=='__main__':main()
