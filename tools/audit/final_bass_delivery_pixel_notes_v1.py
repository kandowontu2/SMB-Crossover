"""Four settled actual HUD pixel-class controls; no emulator or capture edits."""
from pathlib import Path
import argparse,collections,json
from PIL import Image
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import location

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--native',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args();assert not a.output.exists()
 cfg=json.loads((a.native/'config.json').read_text());b=scoped_load(a.native/'candidate.nes');raw=(a.native/'actual-ppu.argb').open('rb');rom=b['raw'];font=cfg['diagnostic']['CHR_offset'];rows=[]
 for item,n in[(0,607),(2,1014),(4,1425),(7,1848)]:
  raw.seek((n-1)*245760);im=Image.frombytes('RGBA',(256,240),raw.read(245760),'raw','BGRA').convert('RGB');idx=144+item;ptr=rom[location(b,'InvNameLo')+idx]+256*rom[location(b,'InvNameHi')+idx];g=b['segs'][b['syms']['InvNameLo']['seg']];off=int(g['ooffs'],0)+ptr-int(g['start'],0);tiles=list(rom[off:off+7]);page=rom[location(b,'InvHudPhysicalBanks')+item-1]if item else 236
  def classes(ids,xy):
   m=collections.defaultdict(set)
   for t,(x,y)in zip(ids,xy):
    z=rom[font+page*1024+t*16:font+page*1024+t*16+16];pixels=[((z[v]>>(7-u))&1)|(((z[v+8]>>(7-u))&1)<<1)for v in range(8)for u in range(8)]
    for k,v in zip(pixels,list(im.crop((x,y,x+8,y+8)).getdata())):m[k].add(v)
   assert all(len(v)==1 for v in m.values()),dict(m);m={k:next(iter(v))for k,v in m.items()};assert len(set(m.values()))==len(m);return m
  name=classes(tiles,[(24+i*8,8)for i in range(7)]);icon=classes([42,43,44,45],[(184,8),(192,8),(184,16),(192,16)])if item else None
  if item:assert icon[0]==name[0]and icon[1]==name[1]
  rows.append(dict(item=item,actual_PPU_ordinal=n,source_page=page,name_tiles=tiles,name_source_classes=name,icon_source_classes=icon,passed=True))
 notes=dict(passed=True,agent_visual_review=True,selected_capture_timing='Original selected-HUD label requests capture immediately when selection is observed; actual publication can still show BUSTER/previous weapon. Effect+12frame windows checked here are settled actual name/icon pixels. Earlier names in labeled selected-HUD images are retained, not CHR corruption.',actual_settled_HUD_source_pixel_classes=rows,limitations='Source2bpp classes with actualRGB inferred fromimage, not independentNESpalettemodel/allbackground/everyeffectpixel; tiny labels/densebars/bodyvisibility remainopen.')
 a.output.write_text(json.dumps(notes,indent=2)+'\n');print(json.dumps(dict(passed=True,checks=len(rows))))

if __name__=='__main__':main()
