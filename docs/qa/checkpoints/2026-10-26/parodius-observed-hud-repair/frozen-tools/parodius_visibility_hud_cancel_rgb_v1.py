"""Independently replay all saved F35 displayed pairs against actual RGB glyph masks."""
from pathlib import Path
from collections import Counter,defaultdict
import argparse,hashlib,json
from PIL import Image,ImageDraw
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rows=lambda p:[json.loads(s)for s in Path(p).read_text().splitlines()]


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['run','old-run','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 raw=(a.run/'candidate.nes').read_bytes();pairs=rows(a.run/'hud-lease-frames.jsonl')
 frames={q['finished']['frame']:q for q in rows(a.run/'hud-frames.jsonl')};checks=[];colors=defaultdict(Counter)
 for q in pairs:
  n=q['ppu']['frame'];s=frames[n]['start'];assert q['ppu']==s['ppu']and q['font']==s['chr'][8]and q['labels']==s['labels']
  f=a.run/f'frame-{n:06d}.argb';im=Image.frombytes('RGBA',(256,240),f.read_bytes(),'raw','BGRA').convert('RGB')
  bg=im.getpixel((0,8));assert bg==im.getpixel((255,8));bad=[]
  for tile,t in enumerate(s['labels']):
   x0=(tile+2)*8;physical=s['chr'][8+t//64];at=1048592+physical*1024+(t%64)*16;data=raw[at:at+16]
   pal=(s['attrs'][(tile+2)//4]>>(((tile+2)&2)))&3
   for y in range(8):
    for x in range(8):
     px=(data[y]>>(7-x)&1)|((data[y+8]>>(7-x)&1)<<1);color=s['palette'][0 if px==0 else pal*4+px]&63
     actual=im.getpixel((x0+x,8+y));colors[color][actual]+=1
     if (color!=(s['palette'][0]&63))!=(actual!=bg):bad.append([x0+x,8+y,color,list(actual),list(bg)])
  assert not bad,('Actual source glyph/RGB mismatch',n,bad[:8])
  checks.append(dict(frame=n,classification=q['classification'],hardware_font=q['font'],raw_sha256=sha(f),mask_pixels=28*64,mask_mismatches=0))
 color_rows={str(k):[dict(RGB=list(rgb),pixels=c)for rgb,c in v.items()]for k,v in colors.items()}
 assert all(len(v)==1 for v in color_rows.values()),color_rows
 (a.output/'frames.json').write_text(json.dumps(checks,indent=2)+'\n')
 selected=[('5354 death515',a.old_run/'frame-000515.argb'),('F35 death515',a.run/'frame-000515.argb'),
           ('5354 restart813',a.old_run/'capture-scroll-000813.argb'),('F35 restart813',a.run/'frame-000813.argb')]
 sheet=Image.new('RGB',(512,520),'#202020');draw=ImageDraw.Draw(sheet);bindings=[]
 for i,(label,f)in enumerate(selected):
  im=Image.frombytes('RGBA',(256,240),f.read_bytes(),'raw','BGRA').convert('RGB');x,y=i%2*256,i//2*260;sheet.paste(im,(x,y+20));draw.text((x,y),label,fill='white')
  bindings.append(dict(label=label,path=str(f.resolve()),sha256=sha(f)))
 sheet.save(a.output/'before-after-full-PPU.png');(a.output/'before-after-bindings.json').write_text(json.dumps(bindings,indent=2)+'\n')
 out=dict(passed=True,native_run=False,classification='Independent offline actual captured RGB/CHR/PPU metadata replay; missing native sixth receipt remains missing',
          ROM_sha256=sha(a.run/'candidate.nes'),actual_mode=0,actual_variant=1,observed_frames=len(checks),
          frame_classifications=dict(Counter(q['classification']for q in checks)),mask_pixels=len(checks)*28*64,mask_mismatches=0,
          actual_metadata_cross_checks=len(checks),first_frame=checks[0]['frame'],last_frame=checks[-1]['frame'],
          observed_color_classes=color_rows,frames_sha256=sha(a.output/'frames.json'),before_after_sheet_sha256=sha(a.output/'before-after-full-PPU.png'),
          hud_pair_rows_sha256=sha(a.run/'hud-lease-frames.jsonl'),hud_frame_rows_sha256=sha(a.run/'hud-frames.jsonl'),
          tool_sha256=sha(Path(__file__)),human_visual_review=False,
          limits='All1574 saved displayed pair rows only; actual RGB glyph masks on HUD row8..15 and observed color-class consistency. No absolute RGB calibration or tiny-label readability verdict, no entire-screen/per-frame art clearance. Original native aggregate stays false; no missing-file backfill, rerun, Hard/area/Buffer2-hold/DMC/global performance/adoption verdict.')
 (a.output/'proof.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));print('proof_sha256='+sha(a.output/'proof.json'))


if __name__=='__main__':main()
