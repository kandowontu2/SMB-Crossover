"""Freeze finite 6c69 source-only bar-readability proposal and agent image review."""
from pathlib import Path
import argparse,hashlib,json,shutil

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['proposal','rejected','failed','output','root']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 proof=json.loads((a.proposal/'proof.json').read_text());assert proof['passed']and not proof['native_run']
 manifest=json.loads((a.proposal/'manifest.json').read_text())
 for f,h in manifest.items():assert sha(f)==h,(f,h,sha(f))
 m=json.loads((a.proposal/'measurements.json').read_text());assert m['unchanged']['added_CPU_cycles']==0
 raw=(a.proposal/'proposal-parodius-hud.chr').read_bytes();assert len(raw)==3072
 facts=[]
 # Measure source whole-word bounds, without assuming a fixed character width.
 source=Path(m['original_data']['source']);old=(source/'chr/characters/parodius-hud.chr').read_bytes();ts=m['original_data']['tables']
 for v in range(3):
  boxes=[]
  for c in range(7):
   pts=[]
   for y in range(2,7):
    for x in range(1,31):
     t=ts[v*28+c*4+x//8];z=old[v*1024+t*16+y]>>(7-x%8)&1
     if z==0:pts.append((x,y))
   boxes.append(dict(left=min(x for x,y in pts),right=max(x for x,y in pts),top=min(y for x,y in pts),bottom=max(y for x,y in pts),width=max(x for x,y in pts)-min(x for x,y in pts)+1))
  facts.append(dict(variant=v+1,seven_exact_source_word_masks=True,word_bounding_boxes=boxes))
 review=dict(agent_visual_review=True,human_visual_review=False,native_run=False,
   viewed=[dict(path=str(a.proposal/n),sha256=sha(a.proposal/n))for n in ['actual548-and-tile-mock.png','source-tile-proposal-comparison.png']],
   actual_frame548_is_lossless_capture=True,mock_is_not_emulator_output=True,
   finding='Frameless positive source letters separate better in these selected previews than the solid plate; no claim of comfortable in-play reading or enlarged glyphs. All21words remain exact original letter masks; source-highlight colors/status admission retained. Current mock shows unselected meter0 only.',
   rejected_framed_mock=dict(path=str(a.rejected/'source-tile-proposal-comparison.png'),sha256=sha(a.rejected/'source-tile-proposal-comparison.png'),reason='Positive letters touch horizontal frame rows, remaining visually dense. Not selected as proposal.'),
   correction='Earlier helper metrics letter_pixel_width=3/font3x5 were nominal shorthand, not a measured fixed character width. Withdraw that fixed-width claim. Actual proportional whole-word bounds below and exact source pixel equality are authoritative. Seven-high letters plus two border rows require at least9rows, or10with the existing Gradius leading blank; existing row is8.')
 put(a.output/'agent-visual-review.json',review)
 measured=dict(letter_height_pixels=5,character_width='proportional source shapes; not assigned a fixed width',actual_word_bounds=facts,
   row_pixels=[224,8],cell_pixels=[32,8],standard_HUD_tiles_preserved_per_page=31,
   existing_spare_tiles=[5,5,8],proposal_spare_tiles=[z['spare_tiles']for z in m['proposal_rows']],
   unchanged_CHR_bytes=3072,unchanged_table_bytes=84,first_publication_queue_bytes=42,attribute_only_queue_bytes=11,
   static_added_CPU_cycles=0,static_added_PPU_writes=0,compiled_or_native_cycle_measurement=False,
   cycle_reason='Only fixed-size pattern/table data would change. PnHudQueue cell load/STA is followed by INY/INX/DEC and BNE from DEC; values never affect a branch. Queue addresses, lengths, palette/status attributes, CHR lease and all instructions stay identical. No new per-frame work.',
   source_proposal_changes=['chr/characters/parodius-hud.chr (same3072bytes)','src/parodius_hud.inc (same84bytes of cell indices)'],
   future_generator_requirement='Integrate the deterministic exact-source-letter polarity transform at the existing prepared-font stage; retain the31HUD/name/status glyphs and fixed-size three-page output. No runtime font transform.',
   all_128_meter_attribute_predicates_equal=True,actual_physical_selected_meter_coverage=False)
 put(a.output/'corrected-measurements.json',measured)
 failed=dict(source_only=True,game_defect=False,attempt=str(a.failed),preserved_tool_sha256=sha(a.failed/'failed-tool.py'),failure='Initial frame composition asserted source letter interior ended before x30. Some authentic label pixels use x30, so this assumption was rejected before proposal output. Later previews preserve the entire x1..30 word masks.')
 put(a.output/'preserved-source-preview-failure.json',failed)
 report=a.root/'docs/qa/parodius-hud-readability-source-2026-10-26.txt'
 text=f'''Parodius graphical power-bar readability: finite source-only audit, 2026-10-26

Bound to frozen6c69 ROM {proof['ROM_sha256']} and its actual EasyOctopus frame548.
No production files, ROM, settings, native worker, roster or audio were changed.

Concrete low-cost proposal: retain all seven32px cells at x16..239/y8..15,
but render the exact existing letter-hole shapes as positive foreground pixels
without the solid plate or horizontal frame. This uses the existing Gradius
bar's positive-letter polarity; it does not copy its weapon names or invent art.
All21 source word masks remain exact, including punctuation and source spelling.
The selected preview is assembled entirely from actual current game tile masks
and two RGB colors calibrated from the actual captured bar. Pixels outside the
bar remain byte-exact. It is a mock, not a new PPU capture or native pass.

The first framed positive-letter mock remains retained and rejected for quality:
letters touch its horizontal borders and stay dense. An earlier source-only
attempt also rejected a false x30-interior assumption; no letter pixels were
deleted to obtain the final preview. No failed receipt was relabeled.

Layout/capacity: 224x8px, seven32px cells, fonts396..398. Each font preserves31
standard HUD/name/status tiles. Current spare capacity is5/5/8 tiles; proposed
spare capacity is{measured['proposal_spare_tiles']}. All3072CHR bytes and84cell-table
bytes retain their sizes. First full publication stays28tiles+8attributes=42
queue bytes; attribute-only publication stays11bytes. All128 seven-bit meter
patterns retain exactly the same attributes and selected/unselected palettes.
The actual selected frame has meter0, so that enumeration is source evidence,
not physical acquisition/selection coverage.

No per-frame timing cost is added by this DATA-ONLY proposal: instructions,
iteration counts, transfer addresses/lengths, dirty protocol, font lease and
palette writes are unchanged. The cell byte is stored then INY/INX/DEC overwrites
flags before its loop branch. This is a static construction argument; no new
compiled ROM or native cycle measurement was made. A future integrated build
must verify exact address/layout confinement and displayed palette/status paths.

Limit: this does not enlarge the five-pixel-high proportional glyph shapes.
Withdraw the earlier helper's nominal fixed3px-width/3x5 shorthand: actual
whole-word bounding boxes, not a fixed character width, are measured in the
corrected receipt. Seven-high text plus two border rows needs at least9rows
(10with the current Gradius leading blank), so it cannot keep this8px framed
row. Full-size multi-row labels require a separate layout/publication/timing
design. The finite no-cost option may improve separation, but tiny-label
readability remains open until actual display/user review. Body flicker and
the failed natural Buffer2 overlap coverage are separate, unchanged findings.

Proposal and actual-tile previews:
{a.proposal}
Framed preview retained/rejected:
{a.rejected}
Final source/agent-review packet:
{a.output}
Stable reproduction (source-only): python -B tools/audit/parodius_visibility_hud_readability_v2.py --source "{source}" --rom "{Path(next(f for f in manifest if f.endswith('candidate.nes')))}" --run "{Path(m['mock']['actual_capture']).parent}" --output FRESH_EXTERNAL_DIRECTORY
'''
 report.write_text(text,encoding='utf-8')
 files={Path(f)for f in manifest}|{z for z in a.output.iterdir()if z.is_file()}|{report,Path(__file__),a.proposal/'proof.json',a.proposal/'manifest.json',a.rejected/'proof.json',a.rejected/'manifest.json',a.rejected/'source-tile-proposal-comparison.png',a.failed/'failed-tool.py'}
 finalmanifest={str(z.resolve()):sha(z)for z in sorted(files,key=str)};put(a.output/'manifest.json',finalmanifest)
 result=dict(passed=True,classification='Finite source/layout proposal and selected actual-tile mock review only',source_only=True,native_run=False,production_changes=False,goal_complete=False,
   ROM_sha256=proof['ROM_sha256'],all21_source_word_masks_exact=True,all128_status_attribute_patterns_equal=True,static_extra_CPU_cycles=0,static_extra_PPU_writes=0,
   proposed_CHR_sha256=sha(a.proposal/'proposal-parodius-hud.chr'),proposed_table_sha256=sha(a.proposal/'proposal-parodius_hud.inc'),
   agent_visual_review=True,quality_claim='Selected mock separation improves; font remains tiny and native/user readability unqualified',report_sha256=sha(report),manifest_bindings=len(finalmanifest),manifest_sha256=sha(a.output/'manifest.json'))
 put(a.output/'proof.json',result)
 checkpoint=a.root/'docs/qa/checkpoints/2026-10-26/parodius-hud-readability-source-v1';checkpoint.mkdir(parents=True,exist_ok=False)
 for src in [a.output/'proof.json',a.output/'agent-visual-review.json',a.output/'corrected-measurements.json',a.output/'preserved-source-preview-failure.json',report]:shutil.copyfile(src,checkpoint/src.name)
 put(checkpoint/'manifest.json',{str(z.relative_to(a.root)):sha(z)for z in sorted(checkpoint.iterdir())if z.is_file()})
 reviewfiles=[a.root/'tools/audit/parodius_visibility_hud_readability_v1.py',a.root/'tools/audit/parodius_visibility_hud_readability_v2.py',Path(__file__),report]+sorted(checkpoint.iterdir())
 put(a.output/'review-files.json',{str(z.resolve()):sha(z)for z in reviewfiles})
 print(json.dumps(result,indent=2));print('proof_sha256='+sha(a.output/'proof.json'));print('checkpoint_manifest_sha256='+sha(checkpoint/'manifest.json'));print('review_files_sha256='+sha(a.output/'review-files.json'))
if __name__=='__main__':main()
