"""Finite remaining-service/resource report for the private DK Jr v3 slice."""
import json,re
from pathlib import Path
import prepare_dkjr_native_world_1102_v3 as P
R=P.R;O=P.O


def main():
 layout=json.loads((O/'native-world-v3-layout.json').read_text());cpu=json.loads((O/'native-world-v3-CPU.json').read_text());assert cpu['passed']
 for rel,sha in cpu['bindings'].items():assert P.P.sha((R/rel).read_bytes())==sha,rel
 source=(O/'native-world-v3.s').read_text();calls={};pc=None
 for line in source.splitlines():
  m=re.match(r'D_([0-9a-f]{4}):',line)
  if m:pc=int(m[1],16)
  m=re.match(r' (?:jsr|jmp) DImport_([0-9a-f]{4})\b',line)
  if m:calls.setdefault(m[1].upper(),[]).append(pc)
 roles={
  'CDFD':('pause/title/demo tail','Native active/pause/scene gate must own this. Original donor pause PPU/control path cannot run in SMB.','native-phase-admission'),
  'CEC9':('short source audio-mailbox request','Closed by exact original CEC9..CED4; native audio channel publication remains separate.','closed-original-source'),
  'CED4':('original score-threshold extra life and HUD','Native score/one-up lifecycle must own credit; original score digits and original HUD cannot be reused as native state.','native-score-life'),
  'CEF4':('original UI blink, fruit motion and enemy AI schedule','Keep original DBB3 fruit motion; native enemy AI already owns native enemies. Replace this mixed donor phase with typed native fruit transactions.','native-fruit-phase'),
  'CF62':('original defeat terminal/life and player/scene change','Exactly-once native death/life handoff at original defeat terminal; preserve native current player/respawn/scene lifecycle.','native-death-life'),
  'CF9D':('original stage-exit rectangle and forced direction','Native flagpole/castle/area transitions own progression; original C4FC goal rectangles are donor coordinates.','native-scene-goal'),
  'EC17':('expired source popup OAM cleanup','Closed by exact original EC17..EC3B; touches only original private OAM, not native score or native OAM.','closed-original-source'),
  'ECB7':('jump-over-enemy bonus admission and popup','Actual original call occurs during jump movement. Must close before a full native movement/Main can execute without oracle services. Needs native enemy rectangle and native score callback.','native-jump-bonus'),
  'ED44':('fruit-hit score chain and popup','Native victim defeat/score credit once, while preserving original 9E/9F chain and 05C7 progression.','native-fruit-credit'),
  'ED7B':('fruit-release score and popup','Native credit at original fruit release event; no B attack or fabricated projectile.','native-fruit-credit'),
  'EDAB':('donor demo input sequencer','Native demo/attract owns input; admitted gameplay must select source4E=0, never execute donor demo scripting.','native-phase-admission'),
  'EFCE':('donor rectangle/nametable queue writer','Fruit source touch uses original donor background addresses. Host fruit presentation/removal must bind its own world transaction, not forward donor VRAM packets.','native-fruit-presentation'),
  'F1C5':('donor one-tile nametable queue writer','Host restoration/attribute publication for source fruit event; preserve native VRAM queue and stage tiles.','native-fruit-presentation')}
 assert len(roles)==13 and set(calls)==set(roles)-{'CEC9','EC17'}
 imports=[]
 for name,(role,need,status)in roles.items():imports.append(dict(original_entry=int(name,16),role=role,status=status,remaining_direct_callers=calls.get(name,[]),next_native_requirement=need))
 q=dict(passed=True,source_only=True,native_playable=False,ROM_written=False,base_ROM_SHA256=P.PIN,component_SHA256=layout['code_SHA256'],component_bytes=layout['component_bytes'],header_reserved_spare=layout['private_code_spare'],original_instruction_bytes=3800,original_imports_audited=13,original_imports_closed_in_v3=2,remaining_imports=11,import_table=imports,private_API={n:pc for n,pc in layout['labels'].items()if n.startswith('DkjrNative')or n=='DkjrNormalizePad'},resource_request_status='MEASUREMENT_ONLY_NO_GRANT',code_runtime_half_open=[0xa000,0xa000+layout['component_bytes']],private_state_half_open=[0xc000,0xc900],immutable_art_bytes=1728,nominal_carriers=dict(code=8,art=2,total=10),not_included_in_fit=['114B tentative38-row vector','native Main/event/velocity/collision policies','native renderer/CHR/palette/HUD leaves','remaining service adapters','resident cold loader/retirement/router/cookies','menu/alternate selector'],next_order=['Bind actual platform attachment/carry event and native current-bbox production, preserving original fractions and source Land(top-17).','Close actual jumping ECB7 admission, native fullbody/head/side/contact and original defeat-terminal/native life handoff; then implement native Main, with explicit source fruit phase freeze.','Provide native fruit world producer, hanging/falling presentation and native victim/credit transaction; original source touch/fall/hit timing stays authoritative.','Measure complete native vector/render/lifecycle fit before proposing exact free carriers, conditional RAM, rawID, menu alternate or common loader admission.'],menu_path=dict(current_Donkey_Kong_slot=27,current_rawID=28,DKJr_absent=True,proposed_path='New alternate under existing DK family, only after source-proven selector/rawID and frontend grant; no bit assumed free.'),helpers=dict(placed=False,original_jump_rise=15,need='Cannot clear32/48/64px pipes by ordinary jump. First implement original native support/climb behavior, then propose existing native platform helpers and qualify actual crossings.'),credits='Donkey Kong Jr., Nintendo,1982/1983; original NES World Rev1 source instructions and original CHR/palettes. No replacement sprite art.',bindings={p.relative_to(R).as_posix():P.P.sha(p.read_bytes())for p in[Path(__file__),O/'native-world-v3-CPU.json',O/'native-world-v3-layout.json']},scope='Finite13-entry service audit, actual compiled private world/control/coordinate leaves and current-native reader/source bindings. Native owner/scene/IRQ/OAM/Main/contact/fruit/life and1-1 qualification remain incomplete.')
 (O/'native-world-v3-readiness.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:q[k]for k in['passed','component_bytes','header_reserved_spare','original_imports_audited','original_imports_closed_in_v3','remaining_imports','resource_request_status']}))


if __name__=='__main__':main()
