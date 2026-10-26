"""Add selected visual review to the immutable failed death/restart receipt."""
from pathlib import Path
import argparse,hashlib,json
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['negative','viewed-sheet','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);z=json.loads((a.negative/'proof.json').read_text());assert not z['passed'] and z['launches']==1 and z['worker_released']
 assert sha(a.viewed_sheet)==sha(a.negative/'selected-full-PPU.png')
 files=set();m=json.loads((a.negative/'manifest.json').read_text())
 for f,h in m.items():assert sha(f)==h;files.add(Path(f).resolve())
 files.update(f.resolve()for f in a.negative.iterdir()if f.is_file())
 report=ROOT/'docs/qa/parodius-death-restart-hud-hold-2026-10-26.txt'
 review=dict(human_visual_review=True,selected_actual_whole_PPU_frames=20,selected_frame_bindings_sha256=sha(a.negative/'selected-frames.json'),
             sheet_sha256=sha(a.negative/'selected-full-PPU.png'),viewed_equivalent_sheet_sha256=sha(a.viewed_sheet),
             finding='Native death515..634 custom-label tiles display with worldfont0; restart813 repeats after pending cancellation. Original blank/font assertions remain required. Body death art changes normally in selected frames; no new body CHR defect claimed.',
             scope='20selected actual wholePPU frames, not every-frame/source-fidelity clearance',report_sha256=sha(report))
 (a.output/'visual-review.json').write_text(json.dumps(review,indent=2)+'\n');files.update(f.resolve()for f in [Path(__file__),report,a.output/'visual-review.json'])
 manifest={str(f):sha(f)for f in sorted(files,key=str)};(a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 q=dict(passed=False,native_run=True,launches=1,retries=0,worker_released=True,ROM_sha256=z['ROM_sha256'],
        original_negative_sha256=sha(a.negative/'proof.json'),manifest_bindings=len(manifest),manifest_sha256=sha(a.output/'manifest.json'),
        visual_review_sha256=sha(a.output/'visual-review.json'),report_sha256=sha(report),
        limits='Original failure813 and actual death515/restart813 glyph mismatch held. No retry, area qualification, new native grant, production/adoption or complete goal verdict.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2));print('proof_sha256='+sha(a.output/'proof.json'))


if __name__=='__main__':main()
