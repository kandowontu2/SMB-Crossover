"""Reconstruct guide portraits from real menu OAM/CHR, never a color key."""
from pathlib import Path
import hashlib,json,re,sys,importlib.util,argparse
from collections import Counter,defaultdict
from PIL import Image
R=Path(__file__).resolve().parents[2];HERE=Path(__file__).parent
Q=R/'build/verification/player-guide-magazine-2026-10-24';Q.mkdir(parents=True,exist_ok=True)
ROM=R/'build/checkpoints/parodius-death-nr/candidate.nes'
PIN='2931163dd7d3c31f9a81776b16c45631a0abd2120abff4454833084825475590'
CASES=[('mario',0,0,0),('luigi',0,'MarioVariant',1),('mega-man',1,'ProtoVariant',0),('proto-man',1,'ProtoVariant',1),('samus',2,0,0),('bill',3,'BillVariant',0),('lance',3,'BillVariant',1),('link',4,'Z2Variant',0),('zelda-ii-link',4,'Z2Variant',1),('simon',5,'Cv3Variant',0),('grant',5,'Cv3Variant',1),('sypha',5,'Cv3Variant',2),('alucard',5,'Cv3Variant',3),('pit',6,0,0),('rygar',7,0,0),('scrooge',8,'DarkwingVariant',0),('darkwing',8,'DarkwingVariant',1),('bass',9,'RlVariant',0),('roll',9,'RlVariant',1),('ryu',10,0,0),('sophia',11,0,0),('kirby',12,'KbVariant',0),('meta-knight',12,'KbVariant',1),('chip',13,'CdVariant',0),('dale',13,'CdVariant',1),('little-mac',14,0,0),('mike-jones',15,0,0),('smb3-mario',16,'M3Variant',0),('smb3-luigi',16,'M3Variant',1),('vic-viper',17,'VvVariant',0),('octopus',17,'VvVariant',1),('twinbee',17,'VvVariant',2),('pentarou',17,'VvVariant',3),('leonardo',18,'TnVariant',0),('raphael',18,'TnVariant',1),('michelangelo',18,'TnVariant',2),('donatello',18,'TnVariant',3)]
def main():
 p=argparse.ArgumentParser();p.add_argument('--names',nargs='*');a=p.parse_args()
 assert hashlib.sha256(ROM.read_bytes()).hexdigest()==PIN
 labels={m[2]:int(m[1],16)for ln in ROM.with_suffix('.lbl').read_text().splitlines()if(m:=re.fullmatch(r'al ([0-9A-Fa-f]+) \.(\S+)',ln))}
 cases=[c for c in CASES if not a.names or c[0]in a.names]
 for key,slot,variant,value in cases:
  if variant=='Cv3Variant':labels[variant]=0x5fe7
  if variant=='CdVariant':labels[variant]=0x5fe1
  if variant=='M3Variant':labels[variant]=0x5fe4
  if variant=='TnVariant':labels[variant]=0x5fe6
 fields=[f'{{key="{k}",slot={s},addr={labels[v]if v else 0},variant={n}}}'for k,s,v,n in cases]
 lua='local cases={'+','.join(fields)+'}\n'+r'''
local frame,index,pending=0,1,0
local banks={};local upper=0
local function r(n)return emu.read(L[n],emu.memType.nesDebug)end
local function file(n,s)local f=assert(io.open(OUTPUT..n,'wb'));f:write(s);f:close()end
local function bytes(a,n,kind)local t={}for i=0,n-1 do t[#t+1]=string.char(emu.read(a+i,kind))end;return table.concat(t)end
emu.addMemoryCallback(function(a,v)upper=v&3 end,emu.callbackType.write,0x5130)
emu.addMemoryCallback(function(a,v)banks[a-0x5120]=v+upper*256 end,emu.callbackType.write,0x5120,0x5127)
emu.addEventCallback(function()
 local b={};local target=cases[index]
 if pending==0 and frame%12==0 then
  if r('CrossoverMenuState')~=2 then b.start=frame>=60
  else
   local current=r('CrossoverMenuIndex');local row=current<12 and current//6 or 2;local wanted=target.slot<12 and target.slot//6 or 2
   if row~=wanted then b.down=true
   elseif current~=target.slot then b.right=true
   elseif target.addr~=0 and emu.read(target.addr,emu.memType.nesDebug)~=target.variant then b.select=true
   else pending=14 end
  end
 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1;assert(frame<9000,'Menu capture bounded')
 if pending>0 then
  pending=pending-1
  if pending==0 then
   local key=cases[index].key
   file(key..'.png',emu.takeScreenshot())
   file(key..'-oam.bin',bytes(0,256,emu.memType.nesSpriteRam))
   file(key..'-palette.bin',bytes(0x3f00,32,emu.memType.nesPpuDebug))
   local chr={}for i=0,7 do chr[#chr+1]=bytes(assert(banks[i])*1024,1024,emu.memType.nesChrRom)end
   file(key..'-chr.bin',table.concat(chr));print('CAPTURE '..key)
   index=index+1;if index>#cases then emu.stop(0)end
  end
 end
end,emu.eventType.endFrame)
'''
 script=Q/'portrait-capture.lua';script.write_text(lua)
 spec=importlib.util.spec_from_file_location('guide_mesen',R/'tools/run_mesen.py');runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner);runner.ROOT=Q/'portrait-capture'
 assert runner.run(script,ROM,timeout=90)==0
 folder=runner.ROOT/'build/verification';out=HERE/'assets/edition';proof=[]
 for key,*_ in cases:
  screen=Image.open(folder/f'{key}.png').convert('RGB');oam=(folder/f'{key}-oam.bin').read_bytes();chrdata=(folder/f'{key}-chr.bin').read_bytes();pal=(folder/f'{key}-palette.bin').read_bytes();pixels={}
  for i in range(63,-1,-1):
   y,tile,attr,x=oam[i*4:i*4+4];y+=1
   if not(82<=x<176 and 144<=y<200):continue
   base=(tile&1)*4096+(tile&254)*16
   for dy in range(16):
    sy=15-dy if attr&128 else dy;raw=chrdata[base+(sy//8)*16:base+(sy//8+1)*16]
    for dx in range(8):
     sx=dx if attr&64 else 7-dx;v=((raw[sy%8]>>sx)&1)|(((raw[sy%8+8]>>sx)&1)<<1)
     if v:pixels[x+dx,y+dy]=pal[16+(attr&3)*4+v]&63
  assert pixels,key
  samples=defaultdict(Counter)
  for xy,nes in pixels.items():samples[nes][screen.getpixel(xy)]+=1
  rgb={nes:counter.most_common(1)[0][0]for nes,counter in samples.items()}
  xs=[x for x,y in pixels];ys=[y for x,y in pixels];left,top=min(xs),min(ys);im=Image.new('RGBA',(max(xs)-left+1,max(ys)-top+1))
  for (x,y),nes in pixels.items():im.putpixel((x-left,y-top),(*rgb[nes],255))
  dst=out/f'hero-{key}.png';im.save(dst)
  proof.append(dict(identity=key,pixels=len(pixels),colors={str(n):list(c)for n,c in rgb.items()},bounds=[left,top,im.width,im.height],screenshot_matches=sum(screen.getpixel(xy)==rgb[nes]for xy,nes in pixels.items()),opaque_pixels_preserved=len(pixels),asset_sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),source_png=str((folder/f'{key}.png').relative_to(R))))
 (Q/'portrait-pixel-proof.json').write_text(json.dumps(dict(ROM_sha256=PIN,method='Real controller menus. Transparency solely from nonzero 8x16 sprite pattern pixels; no screenshot color-key removal. Original OAM priority, hardwareCHR and palette observed read-only.',cases=proof),indent=2))
 print('Portraits reconstructed:',len(proof))
if __name__=='__main__':main()
