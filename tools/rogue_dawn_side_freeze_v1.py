"""Freeze the narrow half-open horizontal extent successor; no new tests."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import rogue_dawn_map_v1 as ref
P=R/'build/rogue-dawn-floor-v4';O=R/'build/rogue-dawn-side-v1'
REPORT=R/'docs/qa/rogue-dawn-side-floor-native-ready-2026-10-29.json'

def main():
 assert not(O/'handoff.json').exists(),'Immutable handoff'
 receipts={n:json.loads((O/(n+'.json')).read_text())for n in['build','controls','edges','ordinary-controls']}
 parent=json.loads((P/'handoff.json').read_text());bindings={}
 for d in[parent,*receipts.values()]:
  assert d['passed']
  for z in d.get('bindings',[]):
   assert ref.binding(z['path'])==z,z['path'];bindings[z['path']]=z
 c=receipts['controls']['checks'];native=c['actual_native_negative'];cost=c['48_foreign_actual_Main_NMI']
 # Compactly retain failed preparation assertions without copying repeated
 # successful prefix arrays or any native container/log/ROM/debug triple.
 negatives=[]
 for p in sorted(O.glob('controls-negative-*.json')):
  d=json.loads(p.read_text());negatives.append(dict(binding=ref.binding(p),error=d.get('error'),
   scope='Typed control/preparation assertion; no native or production failure. Full original remains at bound external path.'))
 report=dict(status='FROZEN_PRIVATE_HALF_OPEN_SIDE_EXTENT_NATIVE_READY_UNRUN',passed=True,
  source_CPU_only=True,native_run=False,canonical_changes=False,candidate=receipts['build']['ROM'],parent=receipts['build']['parent'],
  actual_native_negative=dict(directory='build/verification/rogue-dawn-question-target-native-easy-v1',
   result=ref.binding(R/'build/verification/rogue-dawn-question-target-native-easy-v1/result.json'),
   facts=native['final300_Mains'],reason=native['result']['reason'],
   first_question='ROOT actually reviewed used questionblock and floating typed tank; native collection did not occur. Strict guards/minSP169/zero deaths passed before stationary watchdog.',
   retained='Original df44 ready/controller/result/trace/capture remain untouched; no failed route retagged PASS.'),
  cause='At the corrected source rest centerY193/radius15, old horizontal transverse +radius samples floorY208 as a side wall. Source SideResponse consequently resets run/velocity, reproducing native X337/Y177 and VX0/255. Genuine original E89F/E8A3/E8AD/E8CE scans half-open [center-radius,center+radius), whose last source 8px row is200..207; floor208 is excluded.',
  exact_delta='Only horizontal bottom transverse sample changes from center+radius to center+radius-1 (SEC/SBC#1,3B). Top/center samples, leading edge, native head transactions, down-step/DEC030F, source physics/kernel/jump, inputs/guards/resources/audio/CHR unchanged. Genuine relink moves later A95 entries+3; no manual binary/debug patch.',
  fit=dict(A95_end='BEDD',added_bytes=3,remaining_before_fixed_death_BF00=35,
   death_BF00_BF31_exact=True,all_CHR_exact=True,new_RAM_flags_segments_leases=False,
   actual_new_main_ASM_incbin_inputs=receipts['build']['actual_ASM_incbin_inputs'],
   cached_objects='Inherited immutable audio and weapon objects with parent source/object closure; no full source/runtime trees cloned.',
   per_bank_delta=receipts['build']['per_bank_delta'],outside_A95=c['external_genuine_relocated_operands']),
  source_and_caller_controls=dict(
   actual_original_scan=ref.binding(R/'docs/qa/rogue-dawn-original-side-extent-2026-10-29.json'),
   original_cases=72,public_C94_callback_cases=360,
   post_question_comparisons='4 Easy/Hard×Left/Right,220 actual Mains per image; authentic question birth then ≥48px horizontal displacement, release/stand, fresh jump and landing. Parent identical inputs remainsX337.',
   actual_pipe_side_stop_page_edge_cases=8,foreign_Main_NMI_cases=48,
   Control192_full_lagNMI_and_genuine_IRQ_cases=12,Control192_minimum_SP=receipts['controls']['minimum_SP'],
   all_new_adjacent_instruction_seams=12,natural_Main_seam_minimum_SP=receipts['edges']['minimum_SP'],
   ordinary_MMC3='d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb',
   ordinary_MMC5='f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833'),
  costs=dict(foreign_actual_Main_CPU_delta=sorted(set(z['Main_CPU_delta']for z in cost)),
   foreign_actual_NMI_CPU_delta=sorted(set(z['NMI_CPU_delta']for z in cost)),
   own_horizontal_bottom_sample_added_CPU=4,
   note='SEC2+SBCimm2 per reached bottom sample, no new stack depth. No global FPS or lag improvement claim.'),
  coverage_correction='Frozen df44 walk/release/jump controls asserted action and vertical continuity but omitted actual X progress. Their vertical results remain valid; they did not establish horizontal walking and are not retroactively relabeled.',
  preparation_negatives=negatives,
  preparation_facts=['Initial world-left leaf expectation incorrectly allowed a probe into pageFFFF; preserved existing world-left block behavior is now an explicit negative.',
   'Initial typed page2 scene set only left camera edge; genuine GetScreenPosition now derives its right edge before actual Main. No game source change.',
   'The native stationary interval contains one neutral poll and331 Left polls across300 completed updates; the first assertion overstated every poll asLeft. Exact counts retained.',
   'Changed-instruction seam setup initially allowed genuine NMI joypad polling to replace the next input withneutral; explicit next physical pad is now supplied before the Main, as in all existing source control sequences.'],
  open=['ROOT must run fresh native successor; no native acceptance, collection, full route, every ability, full visual/audio or FPS claim.',
   'Original source room decoder/property boundaries are declared external legal geometry; no fabricated original room RAM or native RAM replay.',
   'Prior original source area3/phase1 audio roomscript limitation and authored six-normal-theme adaptation remain unchanged.',
   'SMB2 actual common NMI/DMC integration remains pending and paused for this genuine Rogue collision issue.'],
  receipts=[ref.binding(O/(n+'.json'))for n in receipts])
 REPORT.write_text(json.dumps(report,indent=2)+'\n')
 files=[R/n for n in['src/rogue_dawn_host_side_v1.s','tools/prepare_rogue_dawn_side_v1.py',
  'tools/rogue_dawn_side_source_v1.py','tools/rogue_dawn_side_controls_v1.py','tools/rogue_dawn_side_edges_v1.py',
  'tools/rogue_dawn_side_ordinary_v1.py','tools/rogue_dawn_side_freeze_v1.py',
  'docs/qa/rogue-dawn-original-side-extent-2026-10-29.json']]+[REPORT]
 files +=[O/n for n in['main.c','entrypoint.s','private.cfg','body-source.s','lifecycle-source.s','source.patch',
  'build.log','assembler-full.dep','build.json','controls.json','edges.json','ordinary-controls.json',
  'candidate.cv3-mirror.json','flagoff-mmc3.dep','flagoff-mmc5.dep','flagoff-mmc3.log','flagoff-mmc5.log']]
 owned=dict(public_files=[ref.binding(p)for p in files],handoff_and_map_additional=True,
  reference_only_binary_artifacts=[ref.binding(O/('candidate.'+e))for e in['nes','dbg','lbl','map']],
  no_Git_native_or_canonical_mutation=True)
 (O/'owned-files.json').write_text(json.dumps(owned,indent=2)+'\n')
 for p in files+[O/'owned-files.json',P/'handoff.json']:
  z=ref.binding(p);bindings[z['path']]=z
 h=dict(status=report['status'],passed=True,native_run=False,source_CPU_only=True,candidate=receipts['build']['ROM'],
  report=ref.binding(REPORT),owned_files=ref.binding(O/'owned-files.json'),
  binding_count=len(bindings),bindings=[bindings[k]for k in sorted(bindings)])
 (O/'handoff.json').write_text(json.dumps(h,indent=2)+'\n')
 print(json.dumps(dict(handoff=ref.binding(O/'handoff.json'),report=ref.binding(REPORT),owned=ref.binding(O/'owned-files.json'),bindings=len(bindings),public_files=len(files)),indent=2))
if __name__=='__main__':main()
