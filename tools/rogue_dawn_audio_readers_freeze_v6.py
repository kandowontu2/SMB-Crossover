"""Freeze measured source-compatible reader successor; no native/test execution."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
import rogue_dawn_map_v1 as ref
O=R/'build/rogue-dawn-audio-readers-v6';P=R/'build/rogue-dawn-backdrop-v1'
REPORT=R/'docs/qa/rogue-dawn-audio-readers-source-2026-10-29.json'

def main():
 assert not(O/'handoff.json').exists()
 ds={n:json.loads((O/(n+'.json')).read_text())for n in['build','controls','ordinary-controls','costs']}
 parent=json.loads((P/'handoff.json').read_text());bound={}
 for d in[parent,*ds.values()]:
  assert d['passed']
  for z in d.get('bindings',[]):
   assert ref.binding(z['path'])==z,z['path'];bound[z['path']]=z
 b,c=ds['build'],ds['controls']['checks']
 report=dict(status='FROZEN_PRIVATE_SOURCE_QUALIFIED_READER_OPTIMIZATION_NATIVE_UNRUN',passed=True,
  native_run=False,source_CPU_only=True,canonical_changes=False,candidate=b['ROM'],parent=b['parent'],
  change='Four real original LDA absolute,Y replacements now enter typed8002/8003/801A/804C readers instead of searching returnPC. Original source3BJSR spans and originalC97 sourcePC+2000 layout remain exact. Internal raw reads omit redundant result reload+restore store; exported rawreader preserves its original value/flags ABI through a separate wrapper.',
  ABI=dict(source_call='ReturnedA/NZ are the true original data byte; X/Y/C/V/D/I/SP and actualsoftware/hardware A/C maps exact. Constant operand LDA affects only transient savedP.N/Z, overwritten by final true dataLDA; all other savedP bits exact.',
    public='RdaReadRom still returns actualA/data/NZ and original X/Y/CV/DI/map behavior. Diagnostic public entry costs12CPU more; true sourcehelpers call the internal endpoint and add no call-depth layer.',
    consumers='RdaReadAbsoluteY/Absolute were unexported internal helpers; all four genuine compiled references replaced and no old helper references remain in actual newdriver/native source. No public entry silently relabeled.'),
  preserved=['All original49152 lower and8192 upper rawbytes/depotmaps, source requests/clock/RNG/pause semantics, cue priority and original authored six themes.',
             'Header/CHR/source body/world/items/palette adaptation and native backdrop helper1241 unchanged.',
             'No source tickskip, muted stream, cue suppression or room-scriptphase1 workaround.'],
  fit=dict(A62_end=b['A62_end'],A62_bytes=669,approved_bytes=729,recovered_bytes=54,
           C97_prefix_used=b['prefix_used'],C97_prefix_capacity=119,
           source_C480_DFFF_extent='7040unchanged',per_bank_delta=b['per_bank_delta'],
           common_bank63='Exactly two actual LDA immediate operands of the genuine RdsAudioFrame farcall follow its movedA62 entry.',
           bank95='Exactly one actual lowHP farcall target byte follows the movedA62 leaf; Main instructions/ordering unchanged.',
           extra_Ram_or_allocations=False),
  checks=dict(genuine_source_JSR_flags_RAM=576,exported_rawreader_ABI=216,
    original_source_vs_old_and_new_complete_NMI=612,themes=6,effects=23,
    wholeControl192_NMI_IRQ=c['complete_Control192_Main_fullNMI_IRQ'],
    ordinaryMMC3='d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb',
    ordinaryMMC5='f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833'),
  measured=dict(source_campaigns=c['612_original_source_and_actual_old_new_fullNMIs'],
     paired_quiet_theme_start=ds['costs']['cases'],
     heavy_example='Actual finite area1 theme-start full lagNMI17607->16335CPU,1272saved(7.22%). Quiet samearea7745->7408,337saved(4.35%). Initial no-reader cold tick8142->8143(+1alignment).',
     not_claimed='HardwareDMA514, DMC steals, physical PPU phase/renderdeadline, nativeFPS/lag or listening. FullMain cost remains material and unchanged in semantics. Future controller poll/Main alignment can change because NMI is shorter; no whole-replayprefix identity.'),
  preparation_negative='First builder span check omitted bank63 and rejected the genuine2-byte RdsAudioFrame target relocation. Actual compiled preimages/opcodes/old+newtarget operands are now explicitly verified. Candidatecode was unchanged by that check correction; no product failure or native run.',
  unsupported='Original area3/phase1 low-RAM note-pointer room script stays explicitly unsupported; authored SMB host never emits06EFphase1. No universal original-driver transition claim.',
  native_parent_scope='ROOT visually confirmed restored blue sky in five selected1241frames. That remains a narrow1241 native observation, not this69a reader candidate native evidence or a route clear.',
  receipts=[ref.binding(O/(n+'.json'))for n in ds],
  open=['ROOT native wholeNMI/deadline/lag/audio/render and actual acquired-item/whole1-1 progress.',
        'Actual source support/control-order diagnostic atX330 remains separate and must not be waived.',
        'Final common family/DMC union and adoption.'])
 REPORT.write_text(json.dumps(report,indent=2)+'\n')
 public=[R/n for n in ['src/rogue_dawn_audio_reader_v6.s','src/rogue_dawn_audio_reader_native_v6.inc',
  'tools/prepare_rogue_dawn_audio_readers_v6.py','tools/rogue_dawn_audio_reader_controls_v6.py',
  'tools/rogue_dawn_audio_reader_costs_v6.py','tools/rogue_dawn_audio_readers_freeze_v6.py']]+[REPORT]
 public += [O/n for n in ['main.c','entrypoint.s','private.cfg','source.patch','audio0.dep',
  'assembler-full.dep','audio.log','build.log','build.json','controls.json','ordinary-controls.json',
  'costs.json','candidate.cv3-mirror.json','flagoff-mmc3.dep','flagoff-mmc5.dep',
  'flagoff-mmc3.log','flagoff-mmc5.log']]
 owned=dict(public_files=[ref.binding(p)for p in public],reference_only_binaries=[ref.binding(O/('candidate.'+s))for s in['nes','dbg','lbl','map']]+[ref.binding(O/'audio0.o')],
   handoff_and_map_are_additional_payloads=True,no_binary_or_runtime_tree_copies=True)
 (O/'owned-files.json').write_text(json.dumps(owned,indent=2)+'\n')
 for p in public+[P/'handoff.json',O/'owned-files.json']:
  z=ref.binding(p);bound[z['path']]=z
 h=dict(passed=True,native_run=False,source_CPU_only=True,status=report['status'],
        candidate=b['ROM'],report=ref.binding(REPORT),owned_files=ref.binding(O/'owned-files.json'),
        binding_count=len(bound),bindings=[bound[k]for k in sorted(bound)])
 (O/'handoff.json').write_text(json.dumps(h,indent=2)+'\n')
 print(json.dumps(dict(handoff=ref.binding(O/'handoff.json'),report=ref.binding(REPORT),
  owned=ref.binding(O/'owned-files.json'),bindings=len(bound),public_files=len(public)),indent=2))
if __name__=='__main__':main()
