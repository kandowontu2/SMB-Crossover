"""Offline eight-control RGB packet with the separately corrected VicHard fixture."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--parent',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);batch=a.parent/'hud-static-native-controls-v1';z=json.loads((batch/'proof.json').read_text());assert len(z['profiles'])==7 and not z['native_assertions_passed']and not z['profiles'][-1]['passed'];profiles=z['profiles'][:-1]+[dict(name='vic-hard',packet=str(a.parent/'hud-static-vic-hard-corrected-v1')),dict(name='twinbee-easy',packet=str(a.parent/'hud-static-native-diagnostic-v1/twinbee-easy'))];rows=[]
 for profile in profiles:
  name=profile['name'];packet=Path(profile['packet']);prep=json.loads((packet/'preparation.json').read_text());run=Path(prep['script']).parent;assert json.loads((run/'scroll-proof.json').read_text())['passed'];rgb=a.parent/('hud-static-RGB-diagnostic-v1'if name=='twinbee-easy'else'hud-static-controls-RGB-v1')/name
  if not(rgb/'proof.json').exists():
   r=subprocess.run([sys.executable,'-B',str(ROOT/'tools/audit/parodius_visibility_hud_rgb_v1.py'),'--packet',str(packet),'--output',str(rgb)],capture_output=True,text=True);assert r.returncode==0,r.stdout+r.stderr
  q=json.loads((rgb/'proof.json').read_text());assert q['source_mask_passed'];frames=[json.loads(s)for s in(run/'hud-frames.jsonl').read_text().splitlines()];events=[json.loads(s)for s in(run/'hud-events.jsonl').read_text().splitlines()];leases=[e for e in events if e['kind']=='write-InvHudActive'and e['value']and e['ram']['SelectedCharacter']==18 and e['ram']['VvVariant']==prep['variant']and e['ram']['OperMode']==1 and e['ram']['GameEngineSubroutine']==8];first_lease=leases[0]['ppu']['frame']if leases else None
  first=q['first_published_frame'];sheet=rgb/'first-publication-full-PPU.png';chosen=None
  if prep['variant']==0:
   first=next(v['finished']['frame']for v in frames if v['start']['ram']['InvHudActive']);chosen=list(range(max(440,first-3),min(633,first+4)+1));sheet=a.output/(name+'-first-captured-HUD-full-PPU.png');im=Image.new('RGB',(1024,520),'#202020');draw=ImageDraw.Draw(im)
   for i,n in enumerate(chosen):
    raw=run/f'frame-{n:06}.argb';cell=Image.frombytes('RGBA',(256,240),raw.read_bytes(),'raw','BGRA').convert('RGB');x=i%4*256;y=i//4*260;im.paste(cell,(x,y+20));draw.text((x,y),f'Actual PPU {n}',fill='white')
   im.save(sheet)
  else:chosen=list(range(first-3,first+5))
  rows.append(dict(name=name,packet=str(packet),mode=prep['mode'],variant=prep['variant'],RGB_proof=str(rgb/'proof.json'),RGB_proof_sha256=sha(rgb/'proof.json'),full_PPU_sheet=str(sheet),full_PPU_sheet_sha256=sha(sheet),full_PPU_sheet_frames=chosen,HUD_sheet=str(rgb/'all-HUD-frames.png'),HUD_sheet_sha256=sha(rgb/'all-HUD-frames.png'),first_recorded_lease_write_frame=first_lease,first_captured_active_frame=first,published_source_mask_frames=q['published_label_frames'],mask_mismatches=q['mask_mismatches'],lease_frame_has_raw_capture=first_lease is not None and(run/f'frame-{first_lease:06}.argb').exists(),Vic0_limit='Unchanged variant0 control: Parodius28-cell glyph oracle does not apply; captured HUD/full-PPU visual review only.'if prep['variant']==0 else None))
 q=dict(source_checks_passed=True,human_visual_review=False,native_run=False,ROM_sha256=z['ROM_sha256'],profiles=rows,tool_sha256=sha(Path(__file__)),retained_failed_batch_sha256=sha(batch/'proof.json'),limits='Offline source masks plus selected-frame/HUD-sheet human review still required. Original menu-only VicHard failure remains failed; fresh corrected fixture is separate. No source oracle is claimed for unchanged Vic0 glyphs, nor any lease before capture440. No exhaustive full-frame/body/DMC/lifecycle verdict.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8');print(json.dumps(q,indent=2))

if __name__=='__main__':main()
