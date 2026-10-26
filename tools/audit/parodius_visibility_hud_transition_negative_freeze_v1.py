"""Additive selected visual/source context for two preserved native negatives."""
from pathlib import Path
import argparse,hashlib,json
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['negative','ready','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);z=json.loads((a.negative/'proof.json').read_text());assert z['passed']is False and z['launches']==2 and z['worker_released'];files=set()
 for d in [a.negative,a.ready]:
  m=json.loads((d/'manifest.json').read_text());assert all(sha(f)==h for f,h in m.items());files.update(Path(f).resolve()for f in m);files.update(f.resolve()for f in d.iterdir()if f.is_file())
 report=ROOT/'docs/qa/parodius-hud-transition-native-hold-2026-10-26.txt'
 review=dict(reviewed=True,scope='30selected actual wholePPU frames only',profiles=[dict(kind=q['kind'],frames=q['selected_frames'],sheet_sha256=q['sheet_sha256'])for q in z['profiles']],conclusion='Selected menus/firstHUD stable; deathprefix descends intofloor, area target already behind right-edge hero then stale duringautoscroll. No death-animation frame captured after actualowner. No ROMdefect or fullvisualclearance inferred.',source_limit='Original missing-body-alias assertion logs no pointer/bytes/PC snapshot. Separate13death records/CHR owner must be source/CPU-qualified before an observer successor.',report_sha256=sha(report),worker_released=True)
 (a.output/'visual-review.json').write_text(json.dumps(review,indent=2)+'\n');files.update(f.resolve()for f in [report,Path(__file__),a.output/'visual-review.json']);manifest={str(f):sha(f)for f in sorted(files,key=str)};(a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 proof=dict(passed=False,native_run=True,launches=2,retries=0,worker_released=True,ROM_sha256=z['ROM_sha256'],negative_sha256=sha(a.negative/'proof.json'),visual_review_sha256=sha(a.output/'visual-review.json'),report_sha256=sha(report),manifest_bindings=len(manifest),manifest_sha256=sha(a.output/'manifest.json'),tool_sha256=sha(Path(__file__)),limits='Both native failures retained/all5components absent. Selected30PPU/sourcecontext only; no native retry/grant/guardrelaxation/ROMdefect/lifecycleresult/adoption. New death metadata/controller source work must be separate.')
 (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof,indent=2));print('proof_sha256='+sha(a.output/'proof.json'))


if __name__=='__main__':main()
