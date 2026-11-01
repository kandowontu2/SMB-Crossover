"""Freeze compact Tank source/component proof, explicitly not a playable build."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[2];O=R/'build/mario-tank-host-1101-v2'
sha=lambda b:hashlib.sha256(b).hexdigest()

def main():
 names=['host-assembly.json','host-CPU-controls.json','terrain-CPU-controls.json','compiled-call-map.json','native-callpaths-CPU.json','owning-source-edits.json','art-resource-audit.json','shoe-mask-candidate.json']
 q={n:json.loads((O/n).read_text())for n in names}
 for n in names:
  if n not in ['owning-source-edits.json']:assert q[n]['passed'],n
 assert q['host-assembly.json']['component_bytes']==908
 assert not q['compiled-call-map.json']['leases_granted']and not q['owning-source-edits.json']['ROM_gate_implemented']
 for v in q.values():
  for rel,digest in v.get('bindings',{}).items():
   p=R/rel if rel.startswith('tools')else O/rel
   assert p.is_file()and sha(p.read_bytes())==digest,(rel,'stale')
 for rel,digest in q['host-assembly.json']['source_bindings'].items():assert sha((R/rel).read_bytes())==digest
 tools=['prepare_mario_tank_host_1101_v2.py','check_mario_tank_host_1101_v2.py','check_mario_tank_terrain_1101_v2.py','audit_mario_tank_callmap_1101_v2.py','check_mario_tank_callpaths_1101_v2.py','audit_mario_tank_art_1101_v2.py','prepare_mario_tank_shoe_masks_1101_v2.py','freeze_mario_tank_host_1101_v2.py']
 refs=['mario_tank_host_1101_v2.inc','mario_tank_terrain_1101_v2.inc']
 inputs=[R/'tools/audit'/n for n in tools]+[R/'tools/reference'/n for n in refs]
 inputs+=[O/n for n in names+['host.bin','host.cfg','host.s','host.lbl','shoe-mask-candidate.chr','shoe-mask-review.png','native-Mario-source-poses.png']]
 donor=json.loads((R/'build/mario-tank-source-1101-v1/handoff.json').read_text())
 handoff=dict(component='Mario the Tank native-host source proposal v2',status='source_CPU_passed_not_admitted',base_ROM_sha256=q['host-assembly.json']['base_ROM_sha256'],root_current_image_binding_required=True,code_bytes=908,host_bytes=403,terrain_bytes=505,physical_RAM_bank=2,code_offset=0x1600,A2_code_alias=0xb600,C2_code_alias=0xd600,context_offset=0x880,A2_context_alias=0xa880,C2_context_alias=0xc880,context_bytes=12,actual_transport='Existing FarCallCommon rawbank2; native nested callbacks restore A2. C-window retains nativeROM12. Normal farcall macro OR128 cannot be used for this rawRAM2 entry.',
  identity=dict(SelectedCharacter=0,MarioVariant=7,menu_admitted=False),leases_granted=False,ROM_gates_implemented=False,cold_loader_implemented=False,native_emulator=False,installed=False,
  implemented=['Exact donor SMB movement via existing CrossoverVanillaMovement, rather than current Flash Mario source physics.','Native small->big->boots progression, native F8/C4 growth milestones, boots immunity and original1000point eligible enemy contact defeat/piranha quirk.','Original256-cell terrain protection, one source cell per actual movement update, actual head/side cell coordinates including page carry, native debris/score/SFX. No player-coordinate proxy or question item dispatch.','Head retains native above-coin behavior; side retains above coin. Existing two native debris slots protect active bouncing item slots.','908B source callbacks assembled and executed through real rawRAM2 A-window farcalls, including167native parser frames/normalNMIs then13Tank GameLoops and actual question-cell head hit.'],
  art=dict(body_reused_bytes=4096,body_growth_bytes=0,body_identical_to_donor=True,shoe_only_masks=19,mask_bytes=608,pickup_bytes=64,total_extra_graphics_bytes=672,per_pose_extra_OAM_max=2,all56_pose_facing_pixel_reconstructions=True,semantic_visual_admission=False),
  tests={n:{k:v for k,v in q[n].items()if k.endswith('cases')or k in ['parser_GameLoop_calls','Tank_GameLoop_frames','minimum_GameLoop_fixture_SP','minimum_owned_entry_SP','native_C_map_retained']}for n in ['host-CPU-controls.json','terrain-CPU-controls.json','native-callpaths-CPU.json']},
  important_negative_findings=['MaaAfterBG is Maaa-only on the current actual Main route. Resetting Tank terrain budget there was an unreachable proposal; fixed by resetting at genuine MtHostMovement before restoring incoming A/P.','Direct C2 code target is unsafe with real QueueSelection C-windowROM12. A2 rawbank2 transport removes that extra C mapper requirement; the conditional code still requires realROM admission/header/cold-loader gates.','Only a preloaded source arena may use the10 direct compiled fixture span substitutions. Shared callbacks must deny before loading or another character cache may occupy RAM2.','Native side shortcut is27B, not29B;18B call+9B padding retains its public tail.','All native4KB Mario body matches original donor; however apparent blank native tile cells and Karnov448B carrier are not enough or not yet granted for908Bcode+672B art. No new page was assumed.','Minimum GameLoop arena SP164 starts from the explicit SP224 harness. It is not actual outer Main/ISR/12-byte reserve qualification.'],
  remaining=['RealROM exact identity/full-header gates on every shared callback before A2 entry; original foreign owners retained on miss.','Forced-blank authenticated loader/readback/complete cookie publication, retirement/scene/title/lives ownership and final root-image import rebind.','Verified ROM/carrier and code/context ownership. Metal500/501/502 closure is pending, not a lease.','Publish672B graphics through a proven free sprite window, aligned boots prepass before native body, authentic pickup replacement, normal/lag NMI paired publication.','Select7 cycle/name/roster/lives admission plus actual native complete Main/IRQ seams and visual gameplay validation.'],
  source_donor_packet=dict(path='build/mario-tank-source-1101-v1/source-and-proof.zip',sha256='4ba9b8bcb8706e906749bde18619fd1dcdfff39cba259a0ed45bfc49bdeafac5',donor_sha256='3396476ef485407414484f038b1e9f4e3a3bac2c1ce45f64f31d119b6e7a3c4e',author='AleFunky',source='https://github.com/AleFunky/mariothetank',commit='a0f6383f8c0989f1bf60a19e7504d8c2e03c666d'),
  storage='Small aggregate receipts/two review PNGs only; no ROM/full debug/object/tree copies in this packet. No emulator capture.')
 (O/'handoff.json').write_text(json.dumps(handoff,indent=2)+'\n')
 (O/'handoff.md').write_text('Mario the Tank: source component, not playable admission\n\n908B source code (403host+505terrain), physicalRAM2offset1600/A2B600.12conditional context bytes use A2A880, never literal C880 while C remains nativeROM12. Existing FarCallCommon rawbank2 transports and restores the worker/native callbacks. Cold loading, complete owner headers and realROM deny-before-load gates are still required.\n\nCPU:70foreign host comparisons;84contact cases;4inactive blooper controls;8injury;12pickup;16growth;128native movement;512tile classification;120world side/page boundaries plus120one-cell limits;6pressure/protection gates;32head effects;11head protected/coin controls;280foreign head/side comparisons. Native admittedMario0 Start/parser ran167GameLoops/normalNMIs, then explicit Tank7 fixture ran13GameLoops and destroyed a real question-cell from below. Minimum arenaSP164 is not an outerMain/ISR reserve claim.\n\nGraphics: native4096B body equals donor exactly;0body growth.19shoe-only masks (608B) plus original64B boots pickup remain unallocated.56pose/facing pixel reconstructions pass, maximum2extraOAM sprites. Overlay is a user-requested adaptation absent from original worn-body code. Review PNG highlights selected source shoe pixels; it does not certify runtime publication.\n\nThe original donor uses four debris slots. This proposal uses the two native host slots and protects bouncing blocks with GuestClaimBlockSlot. Busy host queues defer destruction. No player geometry proxy, remote item release or NMI scratch alias is used.\n\nDo not apply the direct in-memory compiled substitutions to a delivered ROM: they assume RAM2 code is already loaded. RealROM gates must admit exact Mario0/variant7 and complete header before entry, retaining foreign old callbacks. Source leases, loader, retirement, sprite window, menu/lives names/admission, actual outerMain/ISR and native visuals remain. Shared root/O/Downloads/Git untouched.\n',encoding='utf-8')
 inputs +=[O/'handoff.json',O/'handoff.md']
 records=[]
 for p in inputs:
  rel=p.relative_to(R).as_posix()if p.is_relative_to(R/'tools')else p.relative_to(O).as_posix()
  records.append(dict(path=rel,sha256=sha(p.read_bytes()),bytes=p.stat().st_size))
 packet=O/'source-proof.zip'
 with zipfile.ZipFile(packet,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for p,row in zip(inputs,records):z.write(p,row['path'])
 receipt=dict(passed=True,frozen=True,component_only=True,installed=False,carrier_granted=False,packet=dict(path=str(packet.relative_to(R)),sha256=sha(packet.read_bytes()),bytes=packet.stat().st_size,members=len(records)),handoff_sha256=sha((O/'handoff.json').read_bytes()),files=records)
 (O/'freeze.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items()if k!='files'}))

if __name__=='__main__':main()
