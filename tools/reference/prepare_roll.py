"""Pack the supplied mobile Roll pixels; retain source poses and both facings."""
from pathlib import Path
import hashlib,json,re
from PIL import Image
from roll_sprite_packing import pack_layers

ROOT=Path(__file__).resolve().parents[2]
FIRST=364
POOL_CHR=[364,368,372,376,304,336]
FRAMES=[('stand',(0,0,26,34),(11,32)),('blink',(26,0,59,34),(43,32)),
 ('walk1',(90,0,123,34),(107,32)),('walk2',(123,0,155,34),(139,32)),('walk3',(155,0,187,34),(171,32)),
 ('jump',(187,0,215,34),(203,32)),('shoot',(12,36,47,72),(27,70)),
 ('shoot_walk1',(47,36,83,72),(63,70)),('shoot_walk2',(83,36,117,72),(95,70)),
 ('shoot_walk3',(117,36,151,72),(127,70)),('shoot_jump',(151,36,188,72),(163,70)),
 ('climb1',(12,76,37,111),(27,110)),('climb2',(37,76,62,111),(51,110)),
 ('climb3',(62,76,87,111),(75,110)),('climb_shoot',(87,76,119,111),(99,110)),
 ('hurt1',(122,76,158,111),(139,110)),('hurt2',(158,76,194,111),(171,110))]
SHOTS=[('pellet',(48,119,56,125),(52,122)),('health-small',(62,116,72,126),(67,121)),
 ('burst-pink',(114,117,143,127),(128,122)),('burst-white',(146,117,175,127),(160,122)),
 ('health-large',(77,112,93,128),(85,120))]

def encode(px):
 return bytes(sum(((px[y+b*8][x]>>plane)&1)<<(7-x)for x in range(8))
              for b in range(2)for plane in range(2)for y in range(8))
def canonical(px):
 return min((encode([[px[15-y if f&128 else y][7-x if f&64 else x]for x in range(8)]for y in range(16)]),f)
            for f in(0,64,128,192))

def main():
 source=ROOT/'reference/new-roster-art/rollsheet_mobile1.png';image=Image.open(source).convert('RGBA')
 # Native palette1 changes in underground/water rooms. Keep the green bow in
 # the private palette, and share the fixed world white/red and face colors.
 color={(8,8,8):(3,1),(248,184,0):(0,2),(248,56,0):(2,1),
        (248,224,168):(3,2),(0,168,0):(0,1),(248,248,248):(2,2),(168,16,0):(3,3),
        (248,120,248):(0,3),(248,184,248):(2,2)}
 def decode_regular(frame,outlined=False,shot=False):
  _,box,anchor=frame;parts=[]
  ox,oy=anchor
  for dy in range(-32 if not shot else -8,16,16):
   for dx in range(-16 if not shot else -24,24,8):
    layers={p:[[0]*8 for _ in range(16)]for p in range(4)}
    for y in range(16):
     for x in range(8):
      sx,sy=ox+dx+x,oy+dy+y
      if not(box[0]<=sx<box[2]and box[1]<=sy<box[3]):continue
      rgba=image.getpixel((sx,sy))
      if not rgba[3]:continue
      if shot and frame[0].startswith('burst-'):
       # A29px two-palette beam uses all8 sprites on its scanlines and hides
       # the player's torso. Quantize each authentic flash frame to one
       # source tone, retaining every opaque pixel with only4 sprites.
       p,value=(0,3)if frame[0]=='burst-pink'else(2,2)
      else:p,value=color[rgba[:3]]
      layers[p][y][x]=value
    if not outlined and not shot:
     layer=layers[3]
     if not any(v>=2 for row in layer for v in row):layers[3]=[[0]*8 for _ in range(16)]
    for p,px in layers.items():
     if not any(any(row)for row in px):continue
     tile,flip=canonical(px);parts.append((tile,p^flip,dy+(0 if shot else 32),dx+(0 if shot else 8)))
  return parts
 def decode(frame,outlined=False,shot=False):
  if shot:return decode_regular(frame,outlined,True)
  _,box,(ox,oy)=frame
  layers={p:{}for p in range(4)}
  for sy in range(box[1],box[3]):
   for sx in range(box[0],box[2]):
    rgba=image.getpixel((sx,sy))
    if rgba[3]:
     p,value=color[rgba[:3]];layers[p][sx-ox,sy-oy]=value
  if not outlined:
   # Keep exactly the old off-setting's visible pixels. Repacking must not
   # reintroduce a previously omitted ink-only mask around the player.
   colored_cells={((x+16)//8,(y+32)//16)for(x,y),v in layers[3].items()if v>=2}
   layers[3]={at:v for at,v in layers[3].items()if v>=2 or((at[0]+16)//8,(at[1]+32)//16)in colored_cells}
  parts=[]
  for px,p,dy,dx in pack_layers(layers):
   tile,flip=canonical(px);parts.append((tile,p^flip,dy+32,dx+8))
  return parts
 decoded={(f,o):decode(frame,bool(o))for f,frame in enumerate(FRAMES)for o in(0,1)}
 buckets=[]
 for f in range(len(FRAMES)):
  needed={p[0]for o in(0,1)for p in decoded[f,o]}
  for bucket in buckets:
   if len(bucket['tiles']|needed)<=64:bucket['frames'].append(f);bucket['tiles']|=needed;break
  else:buckets.append(dict(frames=[f],tiles=needed))
 assert len(buckets)<=len(POOL_CHR),('Roll exceeds audited unused CHR spans',len(buckets))
 shot_tiles=[];shot_records=[]
 for frame in SHOTS:
  parts=[]
  for tile,attr,dy,dx in decode(frame,shot=True):
   if tile not in shot_tiles:shot_tiles.append(tile)
   parts.append([0xc1+2*shot_tiles.index(tile),attr,dy&255,dx&255])
  shot_records.append(parts)
 # Retain the existing source-derived Crossover energy-capsule artwork.
 # Copy its pixels into the private shot window instead of changing the
 # native enemy/Bowser CHR window to display a drop.
 special=(ROOT/'src/special_art.inc').read_text()
 families=list(map(int,re.search(r'SsArtFamilies:\s*\.byte ([\d,\s]+)\s+SsArtBanks:',special).group(1).replace('\n','').split(',')))
 native_chr=(ROOT/'chr/characters/special-weapons-mmc5.chr').read_bytes()
 capsule_sources=[]
 for art_id in (68,66):
  body=re.search(r'SsArt'+str(art_id)+r'Right:\s*\.byte \d+\s+((?: \.byte [^\n]+\n)+)',special).group(1)
  parts=[]
  for tile,attr,dy,dx in re.findall(r'\{\$([0-9a-f]+)\}, \{SPRITE_BANK_4\}, \$([0-9a-f]+), (-?\d+), (-?\d+)',body):
   tile,attr=int(tile,16),int(attr,16);offset=families[art_id]*2048+1024+tile*16
   data=native_chr[offset:offset+32];assert len(data)==32
   if data not in shot_tiles:shot_tiles.append(data)
   parts.append([0xc1+2*shot_tiles.index(data),attr,int(dy)&255,int(dx)&255])
  assert parts
  shot_records.append(parts);capsule_sources.append(dict(art_id=art_id,family=families[art_id],parts=parts))
 assert len(shot_tiles)<=32
 shot_page=b''.join(shot_tiles).ljust(1024,b'\0')
 fixed=(ROOT/'chr/mmc5/sprites_mario.chr').read_bytes()[1024:2048]
 binary=[];records={};pool_for={};lines=['; Supplied mobile Roll pixels, generated by prepare_roll.py.','.pushseg','.segment "ROLL_ART"','RlArtBegin:']
 for n,bucket in enumerate(buckets):
  tiles=sorted(bucket['tiles']);binary.append(b''.join(tiles[:32]).ljust(1024,b'\0')+fixed+b''.join(tiles[32:]).ljust(1024,b'\0')+shot_page)
  for f in bucket['frames']:
   pool_for[f]=n
   for o in(0,1):
    for facing in(1,2):
     parts=[]
     for tile,attr,dy,dx in decoded[f,o]:
      t=tiles.index(tile);t=(t%32)*2+(0x81 if t>=32 else 0)
      if facing==2:dx=8-dx;attr^=64
      parts.append([t,attr,dy&255,dx&255])
     records[f'{f}-{o}-{facing}']=parts;label=f'RlP{f}O{o}D{facing}'
     lines.append(label+':.byte '+str(len(parts)*4))
     lines+=[' .byte '+','.join(map(str,p))for p in parts]
 for facing in(1,2):
  for suffix,operator in(('Lo','<'),('Hi','>')):
   lines.append(f'RlPose{facing}{suffix}:.byte '+','.join(operator+f'RlP{f}O{o}D{facing}'for f in range(len(FRAMES))for o in(0,1)))
 lines.append('RlPosePools:.byte '+','.join(str(pool_for[f])for f in range(len(FRAMES))))
 lines.append('RlPoolChrLo:.byte '+','.join(str(v&255)for v in POOL_CHR))
 lines.append('RlPoolChrHi:.byte '+','.join(str(v>>8)for v in POOL_CHR))
 shot_left_records=[]
 for n,parts in enumerate(shot_records):
  lines.append(f'RlShot{n}:.byte '+str(len(parts)*4));lines+=[' .byte '+','.join(map(str,p))for p in parts]
  left=[[tile,attr^64,dy,(-((dx+128)%256-128)-8)&255]for tile,attr,dy,dx in parts]
  shot_left_records.append(left)
  lines.append(f'RlShot{n}Left:.byte '+str(len(left)*4));lines+=[' .byte '+','.join(map(str,p))for p in left]
 lines+=['RlDeathReservation:.byte 96','RlShotLo:.byte '+','.join('<RlShot'+str(n)for n in range(len(shot_records))),
         'RlShotHi:.byte '+','.join('>RlShot'+str(n)for n in range(len(shot_records))),
         'RlShotLeftLo:.byte '+','.join('<RlShot'+str(n)+'Left'for n in range(len(shot_records))),
         'RlShotLeftHi:.byte '+','.join('>RlShot'+str(n)+'Left'for n in range(len(shot_records))),'.popseg']
 (ROOT/'src/roll_art.inc').write_text('\n'.join(lines)+'\n')
 out=ROOT/'chr/characters/roll.chr';out.write_bytes(b''.join(binary).ljust(24576,b'\0'))
 def occupancy(parts):
  rows=[0]*80
  for _,_,dy,_ in parts:
   for y in range(dy,dy+16):rows[y]+=1
  return dict(sprites=len(parts),peak_scanline=max(rows))
 packing=[dict(frame=f,outline=o,before=occupancy(decode_regular(frame,bool(o))),after=occupancy(decoded[f,o]))for f,frame in enumerate(FRAMES)for o in(0,1)]
 report=dict(source_url='https://sprites-inc.com/sprite.php?local=Classic/Roll/Mobile/',source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
             CHR_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),first_chr=FIRST,bytes=24576,pool_chr=POOL_CHR,frames=FRAMES,shots=SHOTS,
             records=records,pool_for=pool_for,pools=[dict(frames=b['frames'],pairs=len(b['tiles']))for b in buckets],shot_records=shot_records,shot_left_records=shot_left_records,packing=packing,
             palettes=[[26,40,36],[26,48,39],[22,48,39],[15,55,23]],capsule_sources=capsule_sources,
             capsule_source_sha256=hashlib.sha256(native_chr).hexdigest(),
             charge_color_policy='The two source beam flash frames quantize to magenta24 and white30. Both retain every opaque source pixel and use4 sprites instead of8, preserving player visibility.',
             scope='Original supplied pixels/poses and hardware mirrors; NES color quantization, optional additional ink masks; unused sheet is not treated as a moveset.')
 dest=ROOT/'reference/roll-mobile';dest.mkdir(exist_ok=True);(dest/'art.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(dict(body_pools=report['pools'],shot_pairs=len(shot_tiles),bytes=24576)))

if __name__=='__main__':main()
