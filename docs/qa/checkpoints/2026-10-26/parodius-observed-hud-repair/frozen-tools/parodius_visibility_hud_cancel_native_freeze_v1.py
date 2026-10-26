"""Freeze one F35 native death run without repairing its missing sixth receipt."""
from pathlib import Path
import argparse, collections, hashlib, json
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[2]
SHA='f35f0ec2f70d5dcb6eb1bbfcbd84359d9f6da68c39719d75217aed149edb0631'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rows=lambda p:[json.loads(s) for s in Path(p).read_text().splitlines()]


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['run','ready','old-run','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 z=json.loads((a.run/'lifecycle-proof.json').read_text());cfg=json.loads((a.run/'config.json').read_text())
 assert z['ROM_sha256']==SHA and not z['passed'] and z['runner_exit']==0
 absent='hud-lease-native-result.json';assert z['component_bindings'][absent]is None and not(a.run/absent).exists()
 assert all(q['passed'] for n,q in z['components'].items()if n!=absent)
 pair=rows(a.run/'hud-lease-frames.jsonl');assert pair and pair[-1]['ppu']['frame']==2200
 counts=collections.Counter();seen=set()
 for q in pair:
  assert q['passed'] and q['mode']==0 and q['variant']==1
  frame=q['ppu']['frame'];assert frame not in seen and q['ppu']['scanline']==-1;seen.add(frame)
  custom=q['labels']==cfg['hud_labels']['1'] and q['font']==396
  blank=q['labels']==[36]*28 and q['font']==0
  assert custom or blank
  assert q['classification']==('custom-pair'if custom else'native-blank')
  counts[q['classification']]+=1
 assert counts['custom-pair']>=45 and not(a.run/'first-HUD-lease-pair-mismatch.json').exists()
 script=(a.run/'run.lua').read_text();stop=script.index('emu.stop(0)');lease=script.index('local PLC=assert(PARODIUS_VISIBILITY)')
 finish=script.index("PLC.output..'hud-lease-native-result.json'")
 assert stop<lease<finish
 hud=rows(a.run/'hud-frames.jsonl');life=rows(a.run/'lifecycle-events.jsonl')
 keyframes=[514,515,520,548,612,634,635,638,640,642,655,800,810,811,812,813,814,815,830,2200]
 frames={q['finished']['frame']:q for q in hud}
 selected=[456,458,459,460]+keyframes
 sheet=Image.new('RGB',(6*256,4*260),'#202020');draw=ImageDraw.Draw(sheet);samples=[]
 for i,n in enumerate(selected):
  f=a.run/f'frame-{n:06d}.argb';im=Image.frombytes('RGBA',(256,240),f.read_bytes(),'raw','BGRA').convert('RGB')
  x,y=i%6*256,i//6*260;sheet.paste(im,(x,y+20));draw.text((x,y),str(n),fill='white')
  samples.append(dict(frame=n,path=str(f.resolve()),sha256=sha(f)))
 sheet.save(a.output/'selected-full-PPU.png')
 for n in [515,813,815,2200]:
  Image.frombytes('RGBA',(256,240),(a.run/f'frame-{n:06d}.argb').read_bytes(),'raw','BGRA').save(a.output/f'frame-{n:06d}.png')
 (a.output/'selected-frames.json').write_text(json.dumps(samples,indent=2)+'\n')
 # The original negative ends at813. Compare only actual saved RGB bytes and
 # report the finite prefix; a different ROM is not required to be identical.
 prefix=[];first=None
 for f in sorted(a.old_run.glob('frame-*.argb')):
  q=a.run/f.name
  if sha(f)!=sha(q):first=f.name;break
  prefix.append(dict(name=f.name,sha256=sha(f)))
 (a.output/'unchanged-RGB-prefix.json').write_text(json.dumps(prefix,indent=2)+'\n')
 offline=dict(passed=True,native_component_receipt=False,classification='Offline replay of already-written native startFrame observations; no missing receipt backfill',
              observed_pairs=len(pair),classifications=dict(counts),first_frame=pair[0]['ppu']['frame'],last_frame=pair[-1]['ppu']['frame'],
              actual_mode=0,actual_variant=1,all_original_row_assertions_passed=True,independent_predicate_replay_passed=True,
              missing_native_receipt=absent,source_registration_order=dict(original_stop_character_offset=stop,lease_layer_character_offset=lease,lease_finalizer_character_offset=finish),
              diagnosis='The lease endFrame finalizer is registered after the original native endFrame callback that calls emu.stop(0). All observed startFrame pair assertions ran; the later finalizer did not produce its receipt. This is an observation finalization defect, not a demonstrated ROM defect.')
 (a.output/'offline-pair-reaggregation.json').write_text(json.dumps(offline,indent=2)+'\n')
 evidence=dict(passed=False,native_run=True,launches=1,retries=0,worker_released=True,ROM_sha256=SHA,
               original_aggregate=z,missing_sixth_component=absent,offline_pair_reaggregation=offline,
               key_frame_metadata={str(n):frames[n]for n in keyframes},lifecycle_events=life,
               saved_actual_RGB_frames=len(list(a.run.glob('frame-*.argb'))),same_RGB_prefix_frames=len(prefix),first_differing_saved_RGB=first,
               limits='Five native terminal components pass, but required sixth native receipt is missing and aggregate remains false. Offline pair replay is separate evidence. One actual Easy0/Octopus1 death/restart profile; no Hard/area/Buffer2-hold/DMC/global performance/body readability/adoption or whole-goal verdict.')
 (a.output/'evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
 files={f.resolve()for f in a.run.iterdir()if f.is_file()}|{f.resolve()for f in a.output.iterdir()if f.is_file()}
 m=json.loads((a.ready/'manifest.json').read_text())
 for f,h in m.items():assert sha(f)==h;files.add(Path(f).resolve())
 files.update([Path(__file__).resolve(),(a.ready/'proof.json').resolve(),(a.ready/'manifest.json').resolve(),(a.old_run/'lifecycle-proof.json').resolve()])
 manifest={str(f):sha(f)for f in sorted(files,key=str)};(a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 q=dict(passed=False,native_run=True,launches=1,retries=0,worker_released=True,ROM_sha256=SHA,
        ready_sha256=sha(a.ready/'proof.json'),original_aggregate_sha256=sha(a.run/'lifecycle-proof.json'),
        evidence_sha256=sha(a.output/'evidence.json'),offline_pair_reaggregation_sha256=sha(a.output/'offline-pair-reaggregation.json'),
        original_five_passed=True,sixth_native_receipt_missing=True,offline_observed_pairs=len(pair),offline_classifications=dict(counts),
        selected_actual_whole_PPU_frames=len(selected),human_visual_review=False,manifest_bindings=len(manifest),manifest_sha256=sha(a.output/'manifest.json'),limits=evidence['limits'])
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2));print('proof_sha256='+sha(a.output/'proof.json'))


if __name__=='__main__':main()
