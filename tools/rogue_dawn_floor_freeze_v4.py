"""Freeze the qualified source-floor/native-ready successor, without tests."""
from pathlib import Path
import json,re,sys
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import rogue_dawn_map_v1 as ref
from prepare_rogue_dawn_host_body_handoff_v1 import dependencies
O=R/'build/rogue-dawn-floor-v4';P=R/'build/rogue-dawn-audio-readers-v6'
REPORT=R/'docs/qa/rogue-dawn-source-floor-native-ready-2026-10-29.json'

def main():
 assert not(O/'handoff.json').exists(),'Immutable source unit'
 names=['build','controls','support-controls','stack-layout-controls','ordinary-controls']
 ds={n:json.loads((O/(n+'.json')).read_text())for n in names}
 parent=json.loads((P/'handoff.json').read_text());bound={}
 for d in[parent,*ds.values()]:
  assert d['passed']
  for z in d.get('bindings',[]):
   assert ref.binding(z['path'])==z,z['path'];bound[z['path']]=z
 refs=[]
 for p in dependencies(O/'assembler-full.dep'):
  try:lines=Path(p).read_text().splitlines()
  except(UnicodeError,OSError):continue
  refs.extend(dict(path=str(p),line=i,text=l.strip())for i,l in enumerate(lines,1)
   if re.search(r'\bRdHsSupport(?:Query)?\b',l)and not l.lstrip().startswith(';'))
 code=(R/'src/rogue_dawn_host_floor_v4.s').read_text()
 assert code.count('Case 6,RdHsSupport')==1
 assert code.count(' jsr RdHsSupportQuery')==1
 assert code.count('.proc RdHsSupport\n RdHsSave\n.endproc')==1
 c=ds['controls']['checks'];s=ds['support-controls']['checks'];stack=ds['stack-layout-controls']
 costs=c['48_actual_foreign_Main_NMI_exact']
 report=dict(status='FROZEN_PRIVATE_SOURCE_FLOOR_CORRECTION_NATIVE_READY_UNRUN',passed=True,
  native_run=False,source_CPU_only=True,canonical_changes=False,candidate=ds['build']['ROM'],parent=ds['build']['parent'],
  first_native_symptom='ROOT1241 pilots retained X330..331/Y175..176, action1, gravity26/0, valid floor54/attribute41, freshA ignored. No native firstpickup or routeclear was claimed.',
  exact_cause='Original E4A3 tests current aligned bottom before committing the next downwardpixel. Host tested bottom+1, leaving center192/radius15/bottom207 on floor208. Source E37A then rearmsgravity1A; next grounded run tick CDBF resets animation and skipsCD3C jump/CF55 stand. Four-Main gravity/animation loop is reproduced through complete actualMain, independently of routepolicy.',
  corrections=[
   'Only the host downward terrain sample changes from center+radius+1 to current center+radius; original source jump/action/physics bytes unchanged. Resting center193/radius15/bottom208 matches authenticated source alignment.',
   'Separate authenticated omission restored: E4EC decrements jumpDistance on each committed downwardpixel, inverse of genuine E49E upwardincrement. 00->FF wraps; blockedpixel does not decrement. RunCCC9/CCDC/CCEC animation consumes this signed net upwarddistance.',
   'Remove redundant nested support scratch saving. Public service6 retains its complete save/restoration. Geometry service9/14 invokes a clobbering private query under its enclosing save, then rederives its live axis from immutable serviceID; no extra stackbyte or newflag. LDA/EOR/BEQ select public/private return while preserving querycarry.'
  ],
  callback_semantics='Carryset means one source pixel committed; carryclear blocked. Public AXYP exceptC and six private temporaries exact. Native platform owners unchanged. Only genuine MOVE-UP can queue native head transactions; original native first-solid/row/page and flush remain authoritative.',
  actual_compiled_support_consumers=refs,
  fit=dict(added_A95_bytes=17,A95_end='BEDA',bytes_before_fixed_BF00=38,
   death_BF00_BF31_exact=True,new_RAM_flags_segments_or_leases=False,
   compiler_actual_ASM_incbin_inputs=ds['build']['actual_ASM_incbin_inputs'],
   cached_objects='Existing69a audio0, scheduler audio1/audio2, backdrophelper and qualified UIweaponobject reused with parent684binding source/object closure;500 actual newmainASM inputs, not a fabricated510 total.',
   outside_A95='Exactly33 changedbytes are32 genuine address operand relocations of+17, including one C94bridgeJSR. Existing spans/opcodes/publicPCs retained; A95 following symbols genuinely relinked. Body/lifecycle tailasserts are declared successor values; fixeddeathBF00 exact.',
   per_bank_delta=ds['build']['per_bank_delta']),
  source_controls=dict(original_genuine_down_owner=108,actual_bridge_page_flags_and_wrap=180,
   complete_Main_walk_release_jump_descent_landing=dict(cases=4,modes=[0,1],facings=[0,1],Mains_each=112),
   real_question_underside_then_landing=6,public_support_ABI=16,native_platform_landing_carry=42,
   foreign_complete_Main_NMI=48,action_pad_Control192_full_lagNMI_realIRQ=12,
   minimum_stack=stack['minimum_SP'],running_actual_natural_Main=c['actual_deep_Control192_Main_full_lagNMI_IRQ'],
   ordinary_MMC3='d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb',
   ordinary_MMC5='f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833'),
  cost_limits=dict(foreign_Main_CPU_delta=sorted(set(z['Main_CPU_delta']for z in costs)),
   foreign_NMI_CPU_delta=sorted(set(z['NMI_CPU_delta']for z in costs)),
   support_public_CPU_delta=sorted(set(z['CPU_delta']for z in s['16_actual_public_support_ABI'])),
   note='No zero-cost or universal FPS claim. Source-query LDA/EOR return discrimination adds CPU; redundant pushes are removed. Audio/readers69a and clock/request semantics remain literal; real lag remains to measure.'),
  retained_negatives=dict(stack_packet=ref.binding(O/'retained-stack-negatives.json'),
   original_run_trace=ref.binding(R/'docs/qa/rogue-dawn-run-support-trace-2026-10-29.json'),
   source_original_down=ref.binding(R/'docs/qa/rogue-dawn-original-down-pixel-2026-10-29.json'),
   distinction='All standalone192 failures retained:56e3actualSMC damage;1ad1newpublicquery min126;950cairMorph min127; parent69aairMorph actualSMC damage. Finaldf44 all12 tested action/pad cuts >=128. No native failure retagged or guard relaxed.',
   preparation='Prior context used ordinary brick51 then required permanent used-block replacement; actualhead ran and brick correctly restored51. Correct native questionblockC1 now tested. Missing Pythonimport and fixed-tail/source-span prep rejections retained separately; no game workaround.'),
  native_handoff=dict(menu='Same actual Samus slot, Selectalternate Rogue Dawn, rawSelectedCharacter2/RdVariant1, numericEasy0 orHard1. ROOT uses existing coldmenu/strict bounded producer; no cheats or outcome/state writes.',
   command_policy='ROOT owns fresh handoff-bound native preparation/launch. Reuse literal strict runtime/camera/PPU guard and existing7000frame standing-only route; no extra native command launched here.',
   real_debug_triple=[ref.binding(O/('candidate.'+e))for e in['dbg','lbl','map']]),
  open=['Fresh ROOT native movement/head/pickup/route/wholePPU proof, real NMI deadline and audio performance/listening.',
   'No everypowerup/allabilities/fullworld claim. Source exact local floor/control does not certify native controller route.',
   'Original area3phase1 remains unsupported roomscript; existing explicit authored six-theme mapping unchanged.',
   'Menu/global/default/settings/canonical adoption unchanged.'],
  receipts=[ref.binding(O/(n+'.json'))for n in names])
 REPORT.write_text(json.dumps(report,indent=2)+'\n')
 files=[R/n for n in [
  'src/rogue_dawn_host_floor_v1.s','src/rogue_dawn_host_floor_v2.s','src/rogue_dawn_host_floor_v4.s',
  'tools/prepare_rogue_dawn_floor_v1.py','tools/prepare_rogue_dawn_floor_v2.py','tools/prepare_rogue_dawn_floor_v4.py',
  'tools/rogue_dawn_run_support_trace_v1.py','tools/rogue_dawn_floor_source_v1.py',
  'tools/rogue_dawn_floor_controls_v1.py','tools/rogue_dawn_floor_controls_v2.py','tools/rogue_dawn_floor_controls_v4.py',
  'tools/rogue_dawn_floor_stack_v4.py','tools/rogue_dawn_floor_ordinary_v2.py','tools/rogue_dawn_floor_ordinary_v4.py',
  'tools/rogue_dawn_floor_negatives_v1.py','tools/rogue_dawn_floor_freeze_v4.py',
  'docs/qa/rogue-dawn-run-support-trace-2026-10-29.json','docs/qa/rogue-dawn-original-down-pixel-2026-10-29.json']]+[REPORT]
 files += [O/n for n in['main.c','entrypoint.s','private.cfg','body-source.s','lifecycle-source.s','source.patch',
  'build.log','assembler-full.dep','build.json','controls.json','support-controls.json','stack-layout-controls.json',
  'ordinary-controls.json','retained-stack-negatives.json','candidate.cv3-mirror.json',
  'flagoff-mmc3.dep','flagoff-mmc5.dep','flagoff-mmc3.log','flagoff-mmc5.log']]
 # Earlier candidates stay in place; public only compact actual negatives,
 # never duplicate their ROM/DBG/capture trees into the checkpoint.
 files += [R/'build/rogue-dawn-floor-v1/controls-negative-1.json',
  R/'build/rogue-dawn-floor-v2/context-preparation-negative.json']
 owned=dict(public_files=[ref.binding(p)for p in files],handoff_and_map_are_additional_payloads=True,
  reference_only_binary_artifacts=[ref.binding(O/('candidate.'+e))for e in['nes','dbg','lbl','map']],
  no_Git_or_native_or_canonical_mutation=True)
 (O/'owned-files.json').write_text(json.dumps(owned,indent=2)+'\n')
 for p in files+[O/'owned-files.json',P/'handoff.json']:
  z=ref.binding(p);bound[z['path']]=z
 h=dict(status=report['status'],passed=True,source_CPU_only=True,native_run=False,
  candidate=ds['build']['ROM'],report=ref.binding(REPORT),owned_files=ref.binding(O/'owned-files.json'),
  binding_count=len(bound),bindings=[bound[k]for k in sorted(bound)])
 (O/'handoff.json').write_text(json.dumps(h,indent=2)+'\n')
 print(json.dumps(dict(handoff=ref.binding(O/'handoff.json'),report=ref.binding(REPORT),
  owned=ref.binding(O/'owned-files.json'),bindings=len(bound),public_files=len(files)),indent=2))
if __name__=='__main__':main()
