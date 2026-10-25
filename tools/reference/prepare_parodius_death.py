"""Install the original common Parodius death art in unused family pages.

The original selects skin10 and character-specific group0 animations. Source
colors use private player colors and declared shared-world quantization.
Run after prepare_parodius_art.py; never consume a live body/pickup page.
"""
from pathlib import Path
import hashlib,json
import export_parodius_art as art

ROOT=Path(__file__).resolve().parents[2]
PAGES=[892,956,1020]


def install():
 raw,cpu=art.native.source_cpu();records=art.records(raw)
 manifest_path=ROOT/'reference/parodius-nes/art/packed/manifest.json'
 manifest=json.loads(manifest_path.read_text())
 target=ROOT/'chr/characters/parodius.chr';data=bytearray(target.read_bytes())
 assert hashlib.sha256(data).hexdigest()==manifest['CHR_sha256']
 used={p['body_chr']+i for p in manifest['pools']for i in range(4)}
 assert not used.intersection(PAGES),'Reserved death pages must remain unused'
 old=manifest.get('death',{});animations=art.native.native_animations(cpu);details={}
 chr_source=raw[131088:]
 palettes={1:[0x30,0x15,0x08],2:[0x30,0x28,0x06],3:[0x21,0x03,0x06]}
 lines=['; Original Parodius character-specific group0 death records / skin10.',
        '.pushseg','.segment "VIC_GFX"']
 for variant,page in enumerate(PAGES,1):
  animation=cpu.memory[0x932e+variant];frames=sorted(set(animations[animation]['data'][:-1:2]));pool=[];packed={}
  assert frames==list(range(frames[0],frames[-1]+1))
  override=1 if variant==2 else None
  mapping={c:(0,i+1)for i,c in enumerate(palettes[variant])}
  if variant==3:mapping.update({0x30:(2,2),0x28:(2,3)})
  for frame in frames:
   parts=[]
   for p in records[frame]['parts']:
    px=art.pixels(chr_source,p['tile'],[10,4,11,5,0,0,0,0]);colors=art.PALETTES[override if override is not None else p['attr']&3]
    for target_palette in sorted({mapping[colors[v]][0]for row in px for v in row if v}):
     layer=[[mapping[colors[v]][1]if v and mapping[colors[v]][0]==target_palette else 0 for v in row]for row in px]
     tile=bytes(sum(((layer[y+8*b][x]>>plane)&1)<<(7-x)for x in range(8))for b in range(2)for plane in range(2)for y in range(8))
     if tile not in pool:pool.append(tile)
     parts.append([pool.index(tile)*2,(p['attr']&0xc0)|target_palette,(p['dy']+8)&255,(p['dx']+8)&255])
   packed[str(frame)]=parts;lines.append(f'PnDeathPose{frame}:.byte {len(parts)*4}')
   for part in parts:lines.append(' .byte '+','.join(map(str,part)))
  assert len(pool)<=32
  at=(page-manifest['first_chr'])*1024
  assert old.get('family_chr')==PAGES or data[at:at+1024]==bytes(1024),'Do not overwrite unowned graphics'
  data[at:at+1024]=b''.join(pool).ljust(1024,b'\0')
  for suffix,op in [('Lo','<'),('Hi','>')]:lines.append(f'PnDeathRecord{suffix}V{variant}:.byte '+','.join(op+'PnDeathPose'+str(f)for f in frames))
  details[str(variant)]=dict(animation=animation,frames=frames,palette_override=override,
   private_palette=palettes[variant],records=packed,pairs=len(pool),source_animation_data=animations[animation]['data'])
 for suffix,op in [('Lo','<'),('Hi','>')]:
  for half in('Lo','Hi'):lines.append(f'PnDeathRecord{half}Addr{suffix}:.byte '+','.join(op+f'PnDeathRecord{half}V{v}'for v in(1,2,3)))
 lines+=['PnDeathFirstFrames:.byte '+','.join(str(details[str(v)]['frames'][0])for v in(1,2,3)),
  'PnDeathFrameCounts:.byte '+','.join(str(len(details[str(v)]['frames']))for v in(1,2,3)),
  'PnDeathAnimationIDs:.byte '+','.join(str(details[str(v)]['animation'])for v in(1,2,3)),
  '.segment "VIC_WORLD"','PnDeathPalettes:.byte '+','.join(str(c)for v in(1,2,3)for c in palettes[v]),'.popseg']
 (ROOT/'src/parodius_death_art.inc').write_text('\n'.join(lines)+'\n')
 target.write_bytes(data)
 manifest['CHR_sha256']=hashlib.sha256(data).hexdigest()
 manifest['death']=dict(source_skin=10,source_group=0,family_chr=PAGES,variants=details,
  quantization='Octopus/TwinBee source colors exact. Pentarou yellow28 maps to shared yellow27; other four colors exact. NPC palettes unchanged.')
 manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps(dict(variants={v:d['frames']for v,d in details.items()},pages=PAGES,CHR_sha256=manifest['CHR_sha256'])))


if __name__=='__main__':install()
