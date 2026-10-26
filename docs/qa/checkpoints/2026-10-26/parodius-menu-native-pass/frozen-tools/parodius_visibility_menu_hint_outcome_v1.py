"""Freeze ONE636f native negative, improved old site and selected PPU frames."""
from pathlib import Path
import argparse,collections,hashlib,json
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['run','ready','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);receipt=json.loads((a.run/'lifecycle-proof.json').read_text());assert receipt['ROM_sha256']=='636f2b7e2cf296f5b893fd448c8e4a47b3024fbf955980e80f134bfa33262707'and not receipt['passed']
 assert all(x is None for x in receipt['component_bindings'].values())
 rows=[json.loads(s)for s in(a.run/'oam-bus.jsonl').read_text().splitlines()];events=[json.loads(s)for s in(a.run/'lifecycle-events.jsonl').read_text().splitlines()];h=[json.loads(s)for s in(a.run/'hud-frames.jsonl').read_text().splitlines()];first=json.loads((a.run/'first-init-start-mismatch.json').read_text())
 assert first['ppu']==dict(cpu=11167584,frame=376,scanline=-1,cycle=0)and first['DMA_write_count']==172 and first['DMA_still_pending']and not first['DMA_complete']
 assert first['hardware256']==first['exact_source256']==first['current_source_RAM256']and first['source_generation']==first['game_generation']==1
 oldsite=next(q for q in rows if q['kind']=='lifecycle-init-start-before-assertion'and q['ppu']['frame']==278)
 assert oldsite['DMA_complete']and oldsite['hardware_exact_source']and oldsite['DMA_write_count']==256
 assert oldsite['DMA_completion']['ppu']==dict(cpu=8248884,frame=278,scanline=259,cycle=64)
 assert oldsite['ppu']['cpu']-oldsite['DMA_completion']['ppu']['cpu']==206
 frames=sorted(int(f.stem.removeprefix('frame-'))for f in a.run.glob('frame-*.argb'));assert frames==list(range(150,376))
 selected=[266,278,290,302,314,326,337,349,369,375];sheet=Image.new('RGB',(5*256,2*260),'#171717');draw=ImageDraw.Draw(sheet);views=[]
 for i,n in enumerate(selected):
  f=a.run/f'frame-{n:06}.argb';im=Image.frombytes('RGBA',(256,240),f.read_bytes(),'raw','BGRA').convert('RGB');dest=a.output/f'actual-PPU-{n}.png';im.save(dest);sheet.paste(im,(i%5*256,i//5*260+20));draw.text((i%5*256,i//5*260),f'Actual PPU {n}',fill='white')
  ram=next(q['start']['ram']for q in h if q['finished']['frame']==n);views.append(dict(frame=n,raw_sha256=sha(f),PNG_sha256=sha(dest),actual_RAM={k:ram[k]for k in ['SelectedCharacter','VvVariant','CrossoverBehaviorVersion','OperMode','OperMode_Task','DisableScreenFlag']}))
 sheet.save(a.output/'selected-actual-full-PPU.png')
 (a.output/'selected-frame-bindings.json').write_text(json.dumps(views,indent=2)+'\n')
 parser=[q for q in rows if q['kind']=='lifecycle-init-parser-entry'and q['ppu']['frame']==376];assert len(parser)==7 and parser[0]['offset1']==62
 (a.output/'reentry-parser.json').write_text(json.dumps(parser,indent=2)+'\n');(a.output/'old278-site.json').write_text(json.dumps(oldsite,indent=2)+'\n')
 counts=dict(collections.Counter(x['kind']for x in rows));report=ROOT/'docs/qa/parodius-menu-hint-native-hold-2026-10-25.txt'
 manifest={str(f.resolve()):sha(f)for f in a.run.rglob('*')if f.is_file()}
 for f in [a.ready/'proof.json',a.ready/'manifest.json',Path(__file__),report]:manifest[str(f.resolve())]=sha(f)
 for f in a.output.iterdir():
  if f.is_file():manifest[str(f.resolve())]=sha(f)
 (a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 proof=dict(passed=False,native_run=True,native_worker_released=True,launches=1,retries=0,ROM_sha256=receipt['ROM_sha256'],readiness_sha256=sha(a.ready/'proof.json'),actual_terminal_components=0,required_terminal_components=5,failed_component_receipt_sha256=sha(a.run/'lifecycle-proof.json'),actual_failure_PPU=first['ppu'],first_failure_sha256=sha(a.run/'first-init-start-mismatch.json'),actual_partial_DMA_writes=172,hardware_source_current256_exact=True,old278_DMA_completed_exact=True,old278_completion_before_start_CPU_cycles=206,actual_variants_observed=sorted(set(x['start']['ram']['VvVariant']for x in h if x['start']['ram']['SelectedCharacter']==18)),title_cancel_event=any(x['kind']=='menu-title-return'for x in events),reentry_lifecycle_complete=False,active_gameplay_covered=False,raw_ARGB_frames=frames,bus_kind_counts=counts,manifest_bindings=len(manifest),manifest_sha256=sha(a.output/'manifest.json'),tool_sha256=sha(Path(__file__)),limits='First toggle deadline improved in real native replay, but rebuilt-menu initial full packet fails the same unchanged guard. All226lossless frames retained. Selected10fullPPU frames are bounded review, not exhaustive visibility or a lifecycle pass. No retry/death/area/body/adoption. Source-only render-off initial-hint publication may be considered next.')
 (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=proof['manifest_sha256'],bindings=len(manifest)),indent=2))


if __name__=='__main__':main()
