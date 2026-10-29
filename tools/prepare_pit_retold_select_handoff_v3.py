"""Freeze only the true-Select successor, preserving the frozen v2 negative."""
from pathlib import Path
import argparse,json,sys
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import prepare_pit_retold_host_handoff_v1 as F
from sunny_integrated_controls_v1 import sha
O=R/'build/pit-retold-host-v3';F.O=O

def freeze():
 assert not(O/'handoff.json').exists()
 bindings={};data={}
 for name in['build-proof.json','closure.json','select-correction.json','controls-core-final.json','controls-gameplay.json']:
  p=O/name;d=json.loads(p.read_text());assert d.get('passed',d.get('assembled')),name
  for key in['actual_dependencies','actual_imports','bindings']:
   F.verify(d.get(key,{}));bindings.update(d.get(key,{}))
  bindings[str(p.resolve())]=sha(p);data[name]=d
 assert data['controls-gameplay.json']['actual_select_input_controls']['passed']
 assert len(data['select-correction.json']['exact_one_operand_change_vs_frozen_v2'])==1
 report=R/'docs/qa/pit-retold-host-select-successor-2026-10-29.txt'
 lines=['GB-Pit true-Select successor v3 — source-only, 2026-10-29','',
  'Correction: frozen317c v2 used Down4 in GbPitMenuNavigate, and its source menu fixture repeated that mistake. ROOT native cold-menu testing found real Select32 did not toggle. The old v2 source handoff remains immutable; its Select qualification claim is withdrawn. This is a product hook defect plus a matching fixture defect, not a gameplay or physics failure.','',
  'New candidate: '+data['build-proof.json']['candidate'],
  'Exactly one ROM operand differs from frozen317c: physical66 GbPitMenuNavigate AND immediate04->20. The standalone component uses named Select_Button copied verbatim from bound inc/constants.inc. No other PRG/CHR byte, genuine old public PC, physics, palette, weapon, body record or cache behavior changes.','',
  'New source tests use genuine NES Select32 through complete CrossoverMenuInput: press/hold/release/press/release/press, actual preview/name queues and normal NMI. The old v2 is executed too and reproduces the real no-toggle counterexample. Separate Down4 inputs must navigate identically to the actual737d parent and must not toggle either Pit variant.','',
  'All original renderer/ABI/IRQ/gameplay assertions are rerun on the new actual ROM. Fixture-only replacements are explicitly listed in controls-core-final.json and controls-gameplay.json; Down4 remains in the direct navigation matrix. Core2016 original-Pit pose ABI,2016 actual alternate DrawAll pixel cases,88 foreign complete Main and790 reached ISR seams pass. Supplemental24 normal-Pit Main,12 lives,192 consecutive Main+normalNMI,16 palette/backdrop and actual retained-pointer consumers pass.','',
  'A genuine independent fresh assembly/link reproduces this ROM. Both ordinary flag-off targets remain exact d444cac8/f4ffd248. Full new assembly dependency/import closure is bound. The approved C31/A66 tails,5KB CHR808..812 and menu-only5FE0 allocation remain unchanged.','',
  'One supplemental Down oracle first compared consumed stack writes and was too strong for the extra preserving wrapper; its original tool/raw precompletion output are retained. Final Down comparison retains all caller registers/flags/SP, complete application, final banks, ordered mapper/5SMC/application writes and excludes only consumed page1 writes.','',
  'Native v3 testing remains pending ROOT. No native run, shared source, canonical/default, settings or Downloads change performed here. The previous699 source binding count did not establish cold-native Select behavior. Existing art provenance, explicit local-base dependence, old host animation aliases/composites and source timing limits remain as frozen v2; no original GoodNES full-ROM compatibility claim.']
 report.write_text('\n'.join(lines)+'\n')
 files=[Path(__file__),report,R/'tools/prepare_pit_retold_host_v3.py',R/'tools/audit/pit_retold_host_controls_v3.py',R/'tools/prepare_pit_retold_host_handoff_v1.py',O/'component.s',O/'entrypoint.s',O/'src/entrypoint.s',O/'src/expanded.s',O/'src/character_select.s',O/'smb1base-mmc5-expanded.cfg',O/'pit-retold.chr',O/'source.patch',O/'pose-layout.json',O/'source-pose-sheet.png',O/'controls-down-stack-negative-tool.py',O/'controls-gameplay-before-down-stack-oracle.json',O/'controls-core.json',R/'build/pit-retold-host-v2/handoff.json',R/'docs/qa/pit-retold-host-source-2026-10-29.txt']
 for p in files:bindings[str(p.resolve())]=sha(p)
 F.verify(bindings)
 proof=dict(passed=True,native_run=False,source_CPU_only=True,parent_737d=data['build-proof.json']['parent'],candidate=data['build-proof.json']['candidate'],sole_change_vs_frozen_v2=data['select-correction.json']['exact_one_operand_change_vs_frozen_v2'],frozen_v2_true_Select32_negative_preserved=True,bindings=bindings,actual_ASM_dependencies=len(data['build-proof.json']['actual_dependencies']),immutable_ROM_DBG_LBL={str(O/('candidate.'+e)):sha(O/('candidate.'+e))for e in['nes','dbg','lbl']},owned_publication_files=[str(p.relative_to(R)).replace('\\','/')for p in[Path(__file__),report,R/'tools/prepare_pit_retold_host_v3.py',R/'tools/audit/pit_retold_host_controls_v3.py']])
 (O/'handoff.json').write_text(json.dumps(proof,indent=2)+'\n')
 print(json.dumps(dict(passed=True,candidate=proof['candidate'],handoff=sha(O/'handoff.json'),bindings=len(bindings))))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--phase',choices=['build','freeze'],required=True);a=p.parse_args()
 (F.build if a.phase=='build'else freeze)()
