"""Freeze only the qualified private native-background successor; no tests/native."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
import rogue_dawn_map_v1 as ref
O=R/'build/rogue-dawn-backdrop-v1';P=R/'build/rogue-dawn-scheduler-v5'
REPORT=R/'docs/qa/rogue-dawn-native-backdrop-source-2026-10-29.json'

def main():
 assert not(O/'handoff.json').exists(),'Frozen unit'
 names=['build','controls','foreign-controls','ordinary-controls']
 ds={n:json.loads((O/(n+'.json')).read_text())for n in names}
 old=json.loads((P/'handoff.json').read_text());bound={}
 for d in [old,*ds.values()]:
  assert d['passed']
  for z in d.get('bindings',[]):
   assert ref.binding(z['path'])==z,z['path'];bound[z['path']]=z
 b=ds['build'];checks=ds['controls']['checks'];foreign=ds['foreign-controls']
 report=dict(status='FROZEN_PRIVATE_NATIVE_BACKDROP_SOURCE_QUALIFIED_NATIVE_UNRUN',
  passed=True,source_CPU_only=True,native_run=False,canonical_changes=False,
  candidate=b['ROM'],parent=b['parent'],
  cause='Exact owned GetPlayerColors dispatch bypassed native BackgroundColors restoration while correctly retaining source body3F11 colors. Lives-screen black backdrop persisted into SMB overworld. Original native pilot remains terminalFALSE; this source fix needs new native wholeframe validation.',
  change='Actual A95 RdBodyQueuePalette becomes a genuine18B tailfarcall to A121BF00 helper. Single atomic3F10/4 packet contains the native area/control background plus the existing authentic source three body colors. NativePPU3F10 mirrors3F00. No source palette0F universal publication.',
  leases=dict(helper=b['palette_helper'],A95_end=b['A95_end'],fixed_death_BF00_exact=True,
              A121_item_BE00_BEFD_exact=True,CHR_and_source_raw_audio_views_exact=True,
              RAM='none added',A63_B600_B800='not allocated or used',
              nominal_item_tail='Original A121BE00..BFFF512B is explicitly subdivided: BE00..BEFD authenticitem/drop data unchanged; BF00..BF5E code95B; BF5F..BF6F unused within approved112Bcap.'),
  native_color_table=b['native_BG_provenance'],
  enqueue_contract='Only offsets0..76 accept the complete7B packet plus terminator within existing84B queue. Offset>=77 preserves every queue byte, offset and pendingRdColorRequest; clearsrequest only after successful completeenqueue. Prefix/suffix canaries exact.',
  source_checks=dict(queue_cases=192,foreign_color_callers=24,
     genuine_color_caller_to_fullNMI_PPU=6,complete_Main_Star_transform_area_contexts=6,
     foreign_complete_Main_NMI=48,
     new_palette_deep_Main_NMI_IRQ=checks['natural_Main_added_palette_fullNMI_IRQ'],
     original_Control192_NMI_IRQ=checks['retained_Control192_real_lagNMI_IRQ'],
     ordinary_MMC3='d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb',
     ordinary_MMC5='f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833'),
  source_cost=dict(Rogue_palette_publication_Main_CPU_added=92,
     foreign_GetPlayerColors_CPU_added=0,
     foreign_complete_Main_CPU_added=sorted(set(x['Main_CPU_delta']for x in foreign['rows'])),
     foreign_complete_NMI_CPU_added=sorted(set(x['NMI_CPU_delta']for x in foreign['rows'])),
     note='Actual measured+1 foreignMain relativef467 is A95 relocation/page alignment. Existing source scheduler/foreign overhead remains additional. Palette packet grows by one actualPPUbyte; no universal native deadline or lag claim.'),
  compilation=dict(main_helper_actual_ASM_incbin_inputs=b['actual_ASM_incbin_inputs'],
     inherited='Three genuine frozen audioobjects and qualified UIweaponobject reused with their verified614-binding parent source/object closure. No manual DBG or source/runtime tree copies.',
     genuine_debug_triple=[ref.binding(O/('candidate.'+s))for s in ['dbg','lbl','map']]),
  retained_preparation_negatives=[
     'first-helper.log: external BANK-byte relocation needed explicit lowbyte cast; assembly rejected before candidate.',
     'first-build.log: old lifecycle fixed-body-tail assertion required declared successorB7CC after replacing73B by18B; genuine later code relocated and all actual imports relinked.',
     'controls-negative-1.json: CPU fixture left NmiDisableFF, so real lagNMI correctly did not publishVRAM.',
     'controls-negative-2.json: after genuine normalNMI, palette parser correctly canonicalized3F10 to physical3F00; oracle used unmirroredkey. Current publication check uses real physicalmirror; no native guard changed.'
  ],
  open=['New ROOT-only native palette/sky proof, renderdeadline and performance/audio listening.',
        'Current standing-controller discovery remains separate; no morph/pickup/routeclear claim from these source controls.',
        'No adoption/default/settings/shared-source changes. Original f467/614 packet and native negatives remain immutable.'],
  receipts=[ref.binding(O/(n+'.json'))for n in names])
 REPORT.write_text(json.dumps(report,indent=2)+'\n')
 source=[R/'src/rogue_dawn_host_backdrop_v1.s',R/'tools/prepare_rogue_dawn_backdrop_v1.py',
  R/'tools/rogue_dawn_backdrop_controls_v1.py',R/'tools/rogue_dawn_backdrop_foreign_v1.py',
  R/'tools/rogue_dawn_backdrop_freeze_v1.py',REPORT]
 payload=[O/n for n in ['entrypoint.s','body-source.s','lifecycle-source.s','main.c','private.cfg',
  'source.patch','backdrop.dep','assembler-full.dep','helper.log','build.log','first-helper.log','first-build.log',
  'controls-negative-1.json','controls-negative-2.json','candidate.cv3-mirror.json',
  'build.json','controls.json','foreign-controls.json','ordinary-controls.json',
  'flagoff-mmc3.dep','flagoff-mmc5.dep','flagoff-mmc3.log','flagoff-mmc5.log']]
 public=source+payload
 owned=dict(status='EXACT_OWNED_FILES_NO_GIT_MUTATION',public_files=[ref.binding(p)for p in public],
  handoff_and_map_are_additional_payloads=True,reference_only_binary_artifacts=[ref.binding(O/('candidate.'+s))for s in ['nes','dbg','lbl','map']]+[ref.binding(O/'backdrop.o')],
  note='No public ROM/DBG/object copies; frozen parent614 packet is reused through hash refs, not duplicated.')
 (O/'owned-files.json').write_text(json.dumps(owned,indent=2)+'\n')
 for p in public+[O/'owned-files.json',P/'handoff.json']:
  z=ref.binding(p);bound[z['path']]=z
 h=dict(status=report['status'],passed=True,source_CPU_only=True,native_run=False,
  candidate=b['ROM'],report=ref.binding(REPORT),owned_files=ref.binding(O/'owned-files.json'),
  bindings=[bound[k]for k in sorted(bound)],binding_count=len(bound))
 (O/'handoff.json').write_text(json.dumps(h,indent=2)+'\n')
 print(json.dumps(dict(handoff=ref.binding(O/'handoff.json'),report=ref.binding(REPORT),
  owned=ref.binding(O/'owned-files.json'),bindings=len(bound),public_files=len(public)),indent=2))
if __name__=='__main__':main()
