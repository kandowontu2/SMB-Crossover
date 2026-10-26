"""Freeze the data-only current6c69 readability build; never launch an emulator."""
from pathlib import Path
import argparse,hashlib,json,shutil

ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['candidate','parent','proposal','readability-ready','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 q=json.loads((a.candidate/'proof.json').read_text());assert q['passed']and not q['native_run']and q['different_ROM_bytes']==622 and q['actual_linked_queue_CPU_cases']==1152
 assert sha(a.parent/'candidate.nes')==q['parent_ROM_sha256']and sha(a.candidate/'candidate.nes')==q['candidate_ROM_sha256']
 assert (a.parent/'candidate.lbl').read_bytes()==(a.candidate/'candidate.lbl').read_bytes()
 source=json.loads((a.candidate/'source-manifest.json').read_text())
 for rel,h in source.items():assert sha(a.candidate/'source'/rel)==h
 for f,h in json.loads((a.readability_ready/'manifest.json').read_text()).items():assert sha(f)==h
 report=ROOT/'docs/qa/parodius-hud-readability-candidate-2026-10-26.txt'
 report.write_text(f'''Private current6c69 Parodius readability candidate, 2026-10-26

PASS source/build/data confinement and bounded actual-CPU queue equivalence.
No production/Git/Downloads/settings changes, emulator launch or adoption.
Parent6c69: {q['parent_ROM_sha256']}
Candidate: {q['candidate_ROM_sha256']}
Candidate/source/overlay/build logs and exact commands:
{a.candidate}

A fresh canonical baseline compile of the frozen872-file source reproduced
6c69 exactly before the two-file overlay. The second real canonical compile
produced the candidate. No artwork regeneration or binary patch substituted
for either compile. Prepared assets are deliberate canonical build inputs.

Exact overlay (the reviewed v4 bytes, without other changes):
chr/characters/parodius-hud.chr
  before826e23be42445e062a28b6912d2304064191bfd9a28a35ff4d294f609f18f867
  after d278c3e3f04aa95504099d6f4b6d4ffc932e745c2c8045b7227763b493fba2d0
src/parodius_hud.inc
  beforeaf397226cad12095528b5858687711e0659b91d612690248ed390cff8f04d3b7
  after 17e11b188dfed3acea7b0c646d4f8ae9bbb7b4bfa0d2643310b65ba08b03cd0f
All other870 frozen source/asset/tool/reference file bytes remain exact.
The canonical builder intentionally consumes prepared assets; the separately
frozen v4 audit generator documents deterministic regeneration of this variant.
The original-art import generator itself is unchanged, not silently repurposed.

622 actual ROM bytes differ, confined to these two DATA ranges:
22bytes in84-byte PnHud::PnHudCells: bank77 CPU$BDEF, file638463..638546.
600bytes in3072-byte PN_HUD_CHR: pages396..398, file1454096..1457167.
Every other ROM byte, header, runtime instruction and audio byte is exact.
All61205 qualified old addresses/RAM values match; the complete .lbl file is
byte-exact against both the fresh baseline and accepted6c69 parent.
All31 standard name/HUD/status tiles on each of three pages remain exact.
Only the exact21 existing label masks become positive foreground. Their
source words/proportional shapes, size, seven cells, font pages and status
palettes are not renamed/enlarged. The source-only mock remains a mock.

1152 actual linked PnHudQueue CPU comparisons cover three variants, all128
meter values, and first-label/attribute-dirty/clean paths. Full A/X/Y/P/SP,
every RAM byte, ordered write addresses/data, mapper windows and cycle counts
match except the intended28 label tile indices on first publication.
First/dirty queue lengths stay42/11bytes; all status attributes are exact.
Added queue CPU cycles0. Since the complete runtime instruction image and
transfer structure remain exact, this introduces no new per-frame work.

This is current expanded-target source/CPU qualification only. No native run,
flag-off rebuild, physical selection/acquisition, actual new-color/status
publication, transition, audio-output/performance or in-play user-readability
claim follows. The tiny-font limitation and existing body visibility and
natural Buffer2-overlap coverage findings stay open. No Chip changes combined.

Source qualification receipt: {a.candidate/'proof.json'}
Frozen readiness: {a.output}
Stable private build reproduction:
python -B tools/audit/parodius_visibility_hud_readability_candidate_v1.py --parent "{a.parent}" --proposal "{a.proposal}" --source-ready "{a.readability_ready}" --output FRESH_EXTERNAL_DIRECTORY
''',encoding='utf-8')
 files={a.candidate/'source'/rel for rel in source}
 files|={f for f in a.candidate.iterdir()if f.is_file()}
 files|={f for f in(a.candidate/'overlay').rglob('*')if f.is_file()}
 files|={a.parent/'candidate.nes',a.parent/'candidate.lbl',a.parent/'source-manifest.json',a.proposal/'proof.json',a.proposal/'manifest.json',a.proposal/'proposal-parodius-hud.chr',a.proposal/'proposal-parodius_hud.inc',a.readability_ready/'proof.json',a.readability_ready/'manifest.json',report,Path(__file__),ROOT/'tools/audit/parodius_visibility_hud_readability_candidate_v1.py',ROOT/'tools/audit/check_tmnt_render_oa.py',ROOT/'tools/audit/check_tmnt_audio_fallback_oc.py',ROOT/'tools/audit/verify_native_relocation.py'}
 compiler=ROOT/'tools/Windows/cc65';files|={f for f in(compiler/'bin').glob('*.exe')};files.add(compiler/'lib/nes.lib')
 manifest={str(f.resolve()):sha(f)for f in sorted(files,key=str)};put(a.output/'manifest.json',manifest)
 z=dict(passed=True,source_CPU_only=True,native_run=False,production_changes=False,adopted=False,parent_ROM_sha256=q['parent_ROM_sha256'],candidate_ROM_sha256=q['candidate_ROM_sha256'],fresh_baseline_compile_exact=True,
  source_overlay=q['source_overlay'],all_other870source_files_exact=True,actual_ROM_differences=622,intended_cell_table_differences=22,intended_CHR_differences=600,
  all_runtime_instructions_audio_header_and_other_ROM_exact=True,all_61205_qualified_addresses_and_RAM_exact=True,complete_label_file_exact=True,all93standard_glyph_tiles_exact=True,
  all21_source_word_masks_exact=True,all128_meter_attributes_exact=True,actual_linked_queue_cases=1152,added_CPU_cycles=0,
  candidate_proof_sha256=sha(a.candidate/'proof.json'),report_sha256=sha(report),manifest_bindings=len(manifest),manifest_sha256=sha(a.output/'manifest.json'),
  limits='Expanded canonical source builds/data-only and bounded CPU queue equivalence. No native/flagoff/audio-output/user-readability/adoption/global closure. Existing tinyfont/bodyvisibility/areaFALSE limitations remain.')
 put(a.output/'proof.json',z)
 cp=ROOT/'docs/qa/checkpoints/2026-10-26/parodius-hud-readability-candidate-v1';cp.mkdir(parents=True,exist_ok=False)
 for src,name in [(a.output/'proof.json','proof.json'),(a.candidate/'proof.json','candidate-proof.json'),(a.candidate/'sourcepatch.patch','sourcepatch.patch'),(report,report.name),(a.candidate/'overlay/src/parodius_hud.inc','proposed-parodius_hud.inc')]:shutil.copyfile(src,cp/name)
 put(cp/'manifest.json',{str(f.relative_to(ROOT)):sha(f)for f in sorted(cp.iterdir())if f.is_file()})
 review=[ROOT/'tools/audit/parodius_visibility_hud_readability_candidate_v1.py',Path(__file__),report]+sorted(cp.iterdir());put(a.output/'review-files.json',{str(f.resolve()):sha(f)for f in review})
 print(json.dumps(z,indent=2));print('proof_sha256='+sha(a.output/'proof.json'));print('checkpoint_manifest_sha256='+sha(cp/'manifest.json'));print('review_files_sha256='+sha(a.output/'review-files.json'))
if __name__=='__main__':main()
