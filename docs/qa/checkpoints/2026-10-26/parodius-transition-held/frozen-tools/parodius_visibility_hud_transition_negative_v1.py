"""Freeze two original failed5354 lifecycle runs; no native verdict repair."""
from pathlib import Path
import argparse,csv,hashlib,json
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['preparation','ready','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);profiles=[];files=set()
 for kind in ['death','area']:
  run=a.preparation/kind/'baseline-early';receipt=json.loads((run/'lifecycle-proof.json').read_text());assert not receipt['passed']and all(v is None for v in receipt['component_bindings'].values())
  assert'Actual body immutable record alias'in(run/'host.log').read_text();events=list(map(json.loads,(run/'lifecycle-events.jsonl').read_text().splitlines()));hud=list(map(json.loads,(run/'hud-frames.jsonl').read_text().splitlines()));trace=list(csv.DictReader((run/'trace.csv').open()));frames=sorted(int(f.stem.removeprefix('frame-'))for f in run.glob('frame-*.argb'))
  kills=[q for q in events if q['kind']=='actual-KillPlayer'];deaths=[q for q in events if q['kind']=='actual-death-owner'];targets=[q for q in events if q['kind']=='natural-enterable-pipe-found'];requests=[q for q in events if q['kind']=='actual-native-pipe-request'];loads=[q for q in events if q['kind']=='actual-area-data-loaded']
  active=next(q['finished']['frame']for q in hud if q['start']['ram']['OperMode']==1 and q['start']['ram']['GameEngineSubroutine']==8);font=next(q['finished']['frame']for q in hud if q['start']['ram']['InvHudActive']==3 and q['start']['ram']['OperMode']==1 and q['start']['chr'][8]==396)
  selected=sorted(set(n for n in [278,active,font,font+1,477,500,510,511,512,513,1177,1178,1179,1200,1300,1500,1556,1557,1558,1559]if n in frames));out=a.output/kind;out.mkdir();sheet=Image.new('RGB',(5*256,((len(selected)+4)//5)*260),'#151515');draw=ImageDraw.Draw(sheet);bindings=[]
  for i,n in enumerate(selected):
   raw=run/f'frame-{n:06}.argb';im=Image.frombytes('RGBA',(256,240),raw.read_bytes(),'raw','BGRA').convert('RGB');dest=out/f'actual-PPU-{n}.png';im.save(dest);sheet.paste(im,(i%5*256,i//5*260+20));draw.text((i%5*256,i//5*260),f'{kind} actual {n}',fill='white');bindings.append(dict(frame=n,raw_sha256=sha(raw),PNG_sha256=sha(dest)))
  sheet.save(out/'selected-actual-full-PPU.png');(out/'selected-frame-bindings.json').write_text(json.dumps(bindings,indent=2)+'\n')
  evidence=dict(kind=kind,kills=kills,native_death_owners=deaths,pipe_targets=targets,native_pipe_requests=requests,actual_loaded_areas=loads,last_trace=trace[-1],first_active_frame=active,first_custom_HUD_frame=font,raw_first=frames[0],raw_last=frames[-1],raw_count=len(frames),unlogged_native_failing_pointer=True,unlogged_exact_assertion_stamp=True,classification='UNCHANGED_BODY_ALIAS_ASSERTION_AFTER_REAL_DEATH; observer metadata/source-owner diagnosis pending; no ROM defect inferred',all5_terminal_components_absent=True)
  if targets:
   targetx=targets[0]['x']+8;start=targets[0]['ppu']['frame'];window=[q for q in trace if int(q['frame'])>=start]
   evidence['pipe_controller_window']=dict(target_PlayerX=targetx,target_PlayerY=targets[0]['top']-8,frames=len(window),x_min=min(int(q['x'])for q in window),x_max=max(int(q['x'])for q in window),near_target_frames=[q for q in window if abs(int(q['x'])-targetx)<=1],last24=window[-24:],limits='Trace/inputs evidence only. A detected metatile pair does not prove native pipe entry or physical reachability.')
  (out/'evidence.json').write_text(json.dumps(evidence,indent=2)+'\n');profiles.append(dict(kind=kind,passed=False,run_receipt_sha256=sha(run/'lifecycle-proof.json'),raw_frames=len(frames),last_actual_saved_frame=frames[-1],actual_KillPlayer=kills[0]['ppu']if kills else None,actual_VvDeathStart=deaths[0]['ppu']if deaths else None,required_components_present=0,required_components=5,selected_frames=selected,evidence_sha256=sha(out/'evidence.json'),sheet_sha256=sha(out/'selected-actual-full-PPU.png')));files.update(f.resolve()for f in run.rglob('*')if f.is_file())
 for f in [a.ready/'proof.json',a.ready/'manifest.json',a.preparation/'proof.json',Path(__file__)]:files.add(f.resolve())
 for name in ['parodius_death.s','parodius_death_art.inc','vic_render.s']:
  f=a.preparation/'frozen/source/src'/name;files.add(f.resolve())
 files.update(f.resolve()for f in a.output.rglob('*')if f.is_file());manifest={str(f):sha(f)for f in sorted(files,key=str)};(a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 proof=dict(passed=False,native_run=True,launches=2,retries=0,worker_released=True,ROM_sha256=receipt['ROM_sha256'],profiles=profiles,manifest_bindings=len(manifest),manifest_sha256=sha(a.output/'manifest.json'),tool_sha256=sha(Path(__file__)),limits='Two exact authorized original runs, both false, all raw prefixes/five missing components preserved. Source body metadata131live records omits the separate death-pose family; actual failing pointer/owner snapshot was not logged before original assertion, so source/CPU attribution remains separate. Selected actual visual review still required. No new native grant/retry, guard weakening, ROM defect, life/restart/area/Buffer2/adoption/fullgoal verdict.')
 (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof,indent=2));print('proof_sha256='+sha(a.output/'proof.json'))


if __name__=='__main__':main()
