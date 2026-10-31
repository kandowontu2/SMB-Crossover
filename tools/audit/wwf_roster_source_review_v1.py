"""Extract original WrestleMania bodies/themes without touching a host ROM.

Renderer packets are executed from original ROM instructions, then checked
against the original pointer records. Music checks execute the original
initialization and tick entry points. No Mesen launch or global lease.
"""
from pathlib import Path
import argparse
import hashlib
import json
import struct
import sys

from PIL import Image, ImageDraw
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler

R=Path(__file__).resolve().parents[2]
O=R/'build/wwf-roster-source-review-v1'
ROM=Path('C:/NES/WWF WrestleMania (USA).nes')
PRIOR=Path('C:/Users/kando/Documents/ChatGPT/mario in kid icarus/wwf')
SHA='0d294769d55984684f8fe3299f47b7f4da8667b1dabb94ab8e4c620750bf7f87'
NAMES=['Ted DiBiase','Bam Bam Bigelow','Honky Tonk Man','Randy Savage','Andre the Giant','Hulk Hogan']

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(name,x):(O/name).write_text(json.dumps(x,indent=2)+'\n')
def raw():
 b=ROM.read_bytes();assert hashlib.sha256(b).hexdigest()==SHA
 assert len(b)==131088 and b[4]==8 and b[5]==0 and (b[6]>>4|b[7]&0xf0)==7
 return b[16:]
def word(b,a):return int.from_bytes(b[a-0x8000:a-0x7ffe],'little')

class Bus:
 def __init__(self,bank):
  self.m=[0]*65536;self.m[0x8000:]=bank
  self.reads=set();self.writes=set();self.apu=[]
 def __getitem__(self,a):
  if isinstance(a,slice):return self.m[a]
  self.reads.add(a);return self.m[a]
 def __setitem__(self,a,v):
  assert isinstance(a,int)and a<0x8000,('Original routine wrote ROM',a)
  self.writes.add(a);self.m[a]=v
  if 0x4000<=a<=0x4017:self.apu.append((a,v))

def call(bus,pc,x=0,limit=100000):
 c=MPU(memory=bus,pc=pc);c.x=x;c.sp=253;c.stPushWord(0x7eff)
 for _ in range(limit):
  if c.pc==0x7f00:return c.processorCycles
  assert bus.m[c.pc]!=0,('BRK',hex(c.pc))
  c.step()
 raise AssertionError(('CPU bound',hex(pc),hex(c.pc)))

def tables(prg):
 b=prg[:32768];out=[]
 for i,name in enumerate(NAMES):
  desc=word(b,0xbb28+2*i);d=b[desc-0x8000:desc-0x8000+80]
  bank,selector=d[7],d[8]
  root_header={1:0x83a2,2:0x8910,3:0x8062}[bank]+selector
  native=prg[bank*32768:(bank+1)*32768]
  base=word(native,root_header);step=2 if bank==3 else 4
  count=(word(native,base)-base)//step
  assert 12<=count<=24
  groups=[word(native,base+g*step)for g in range(count)]
  out.append(dict(id=i,name=name,descriptor=desc,descriptor_hex=d.hex(),bank=bank,
   selector=selector,root_header=root_header,root=base,step=step,groups=groups,
   palette=list(d[1:4]),alternate_palette=list(d[4:7]),mirror_width=d[0],theme=d[0x40],script_table=int.from_bytes(d[21:23],'little'),
   hurt_actions=list(d[0x25:0x27]),down_action=d[0x34],pin_action=d[0x10]))
  out[-1]['original_input_action_selectors']=[dict(input=name,side_action=d[0x0a+j],rope_action=d[0x29+j])for j,name in enumerate(['A','B','Up','Down','A+B','Up+A','Down+A','Up+B','Down+B','Up+A+B','Down+A+B'])]
 return out

def pixels(pattern):
 return [[((pattern[y]>>(7-x))&1)|(((pattern[y+8]>>(7-x))&1)<<1)for x in range(8)]for y in range(8)]

def pack16(parts,tiles):
 final={}
 for part in reversed(parts):
  for y,row in enumerate(pixels(tiles[part['tile']])):
   for x,value in enumerate(row):
    if value:final[part['x']+x,part['y']+y]=(value,part['attribute_low_bit'])
 packed=[];roles=[]
 for role in [0,1]:
  points={xy:value for xy,(value,palette)in final.items()if palette==role}
  choices=[]
  if not points:
   roles.append((points,[(0,0,0,set())]));continue
  for ox in range(8):
   for oy in range(16):
    cells={((x-ox)//8,(y-oy)//16)for x,y in points}
    choices.append((len(cells),ox,oy,cells))
  roles.append((points,sorted(choices,key=lambda q:q[:3])))
 chosen=[q[1][0]for q in roles]
 def occupancy(option):
  return [sum(cy*16+option[2]<=y<cy*16+option[2]+16 for cx,cy in option[3])for y in range(-72,24)]
 occ=[occupancy(q)for q in chosen]
 peak=max(a+b for a,b in zip(*occ))
 if peak>8:
  # Preserve exact pixels/roles while jointly choosing both grid phases.
  # A few standalone phase minima unnecessarily exceed eight sprites.
  limit=sum(q[0]for q in chosen)+4
  candidates=[[(q,occupancy(q))for q in z[1]]for z in roles]
  best=None
  for a,oa in candidates[0]:
   for b,ob in candidates[1]:
    if a[0]+b[0]>limit:continue
    p=max(x+y for x,y in zip(oa,ob))
    key=(max(0,p-8),a[0]+b[0],p,a[:3],b[:3])
    if best is None or key<best[0]:best=(key,[a,b])
  chosen=best[1]
 for role,((points,_),option)in enumerate(zip(roles,chosen)):
  _,ox,oy,cells=option
  for cx,cy in sorted(cells,key=lambda q:(q[1],q[0])):
   tx,ty=cx*8+ox,cy*16+oy
   pattern=bytes(sum(((points.get((tx+x,ty+y),0)>>plane)&1)<<(7-x)for x in range(8))for half in range(2)for plane in range(2)for yy in range(8)for y in [half*8+yy])
   packed.append(dict(x=tx,y=ty,role=role,pattern=pattern))
 rebuilt={}
 for cell in packed:
  for half in range(2):
   for y,row in enumerate(pixels(cell['pattern'][half*16:(half+1)*16])):
    for x,value in enumerate(row):
     if value:rebuilt[cell['x']+x,cell['y']+half*8+y]=(value,cell['role'])
 assert rebuilt==final,'8x16 raster and palette-role conversion'
 return packed

def assets():
 assert not (O/'handoff.json').exists(),'Frozen asset leaf is immutable'
 O.mkdir(parents=True,exist_ok=True);prg=raw();chars=tables(prg)
 boundaries={k:set()for k in range(1,4)}
 for c in chars:
  bank=c['bank'];b=prg[bank*32768:(bank+1)*32768]
  boundaries[bank].update(c['groups']+[c['root'],c['root_header']])
  boundaries[bank].update(word(b,t)for t in c['groups'])
 unique=[];unique_index={};packed_tiles=[];packed_index={};poses=[];cycles=[];all_refs=set();portraits=bytearray()
 palette_path=R/'tools/Windows/NEXXT 3.0/defaults/nes.pal'
 palette_bytes=palette_path.read_bytes();assert len(palette_bytes)>=192
 palette_rgb={i:tuple(palette_bytes[i*3:i*3+3])for i in range(64)}
 for c in chars:
  bank=c['bank'];b=prg[bank*32768:(bank+1)*32768];frames=[]
  for group,t in enumerate(c['groups']):
   end=min(n for n in boundaries[bank]if n>t)
   count=(end-t)//2;assert 1<=count<=16,(c['name'],group,hex(t),hex(end),count)
   for frame in range(count):
    rec=word(b,t+frame*2);assert 0x8000<=rec<0xff00
    bus=Bus(b);bus.m[0x6d]=group;bus.m[0x6e]=frame
    cost=call(bus,0x8003,c['selector']);cycles.append(cost)
    parts=[]
    for j in range(20):
     at=rec-0x8000+j*4;lo,hi,dy,dx=b[at:at+4]
     if dx==0x80:break
     ptr=lo|((hi|0x80)<<8)
     pattern=b[ptr-0x8000:ptr-0x8000+16];assert len(pattern)==16
     assert bytes(bus.m[0x200+j*16:0x210+j*16])==pattern
     attr=(hi>>7)&1  # Native ASL; ROL; AND1 preserves original bit7.
     assert bus.m[0x340+j*3:0x343+j*3]==[dy,dx,attr]
     if pattern not in unique_index:unique_index[pattern]=len(unique);unique.append(pattern)
     parts.append(dict(tile=unique_index[pattern],x=dx if dx<128 else dx-256,
       y=-dy if dy<128 else 256-dy,attribute_low_bit=attr,source_bank=bank,source_address=ptr))
     all_refs.add((bank,ptr))
    assert parts and bus.m[0x341+len(parts)*3]==0x80
    # Execute the genuine OAM owner prefix as well. This catches signed
    # geometry mistakes (e.g. native dyFF is +1 after wrapped subtraction).
    display=Bus(prg[:32768]);display.m[0x340:0x380]=bus.m[0x340:0x380]
    display.m[0x2a]=(c['id']+1)%6;display.m[0x2b]=c['id']
    display.m[0x2c]=96;display.m[0x2e]=200;display.m[0x32]=group
    cpu=MPU(memory=display,pc=0xa62e)
    for _ in range(10000):
     if cpu.pc==0xa704:break
     cpu.step()
    else:raise AssertionError('Original OAM prefix bound')
    for j,part in enumerate(parts):
     sy,tile,attr,sx=display.m[0x400+j*4:0x404+j*4]
     assert sx==(display.m[0x72]+part['x'])&255
     assert sy==(display.m[0x73]+part['y'])&255
     assert attr&1==part['attribute_low_bit']
    out=dict(character=c['id'],group=group,frame=frame,record=rec,parts=parts,
      source_packet_bytes=len(parts)*16,CPU_cycles=cost,
      width=c['mirror_width']if bank==3 else b[c['root']-0x8000+group*4+2])
    cells=pack16(parts,unique)
    for cell in cells:
     pat=cell.pop('pattern')
     if pat not in packed_index:packed_index[pat]=len(packed_tiles);packed_tiles.append(pat)
     cell['pair']=packed_index[pat]
    out['packed_8x16_cells']=cells
    poses.append(out);frames.append(out)
  c['pose_count']=len(frames);c['groups_count']=len(c['groups'])
  c['frame_counts']=[sum(q['group']==g for q in frames)for g in range(len(c['groups']))]
  c['unique_source_tiles']=len({(q['source_bank'],q['source_address'])for f in frames for q in f['parts']})
  c['packed_8x16_unique_pairs']=len({q['pair']for f in frames for q in f['packed_8x16_cells']})
  c['packed_8x16_cells_per_pose']=[min(len(f['packed_8x16_cells'])for f in frames),max(len(f['packed_8x16_cells'])for f in frames)]
  # One compact source renderer atlas per wrestler. Coordinates/2bpp index
  # come from native records; original per-sprite palette-role bit retained.
  sheet=Image.new('RGB',(12*96,((len(frames)+11)//12)*112),'#333333');dr=ImageDraw.Draw(sheet)
  colors=[[ (0,0,0)]+[palette_rgb.get(v,(255,0,255))for v in c[k]]for k in ['palette','alternate_palette']]
  for n,f in enumerate(frames):
   x=n%12*96;y=n//12*112;dr.text((x+2,y+2),f"{f['group']}:{f['frame']}",fill='white')
   for part in reversed(f['parts']):
    pat=pixels(unique[part['tile']]);tx=x+16+part['x'];ty=y+96+part['y']
    for yy,row in enumerate(pat):
     for xx,v in enumerate(row):
      if v and 0<=tx+xx<sheet.width and 0<=ty+yy<sheet.height:sheet.putpixel((tx+xx,ty+yy),colors[part['attribute_low_bit']][v])
  sheet.save(O/f"wrestler-{c['id']}-source-poses.png")
  ptr=word(prg[:32768],0x8e10+c['id']*2)
  portrait=prg[ptr-0x8000:ptr-0x8000+576];assert len(portrait)==576
  portraits+=portrait;c['portrait_source']=ptr;c['portrait_bytes']=576
 (O/'wrestlers-unique.chr').write_bytes(b''.join(unique))
 (O/'wrestlers-8x16.chr').write_bytes(b''.join(packed_tiles))
 pages=[]
 for f in sorted(poses,key=lambda q:(-len({c['pair']for c in q['packed_8x16_cells']}),q['character'],q['group'],q['frame'])):
  need={c['pair']for c in f['packed_8x16_cells']}
  options=[(len(need-set(page)),i)for i,page in enumerate(pages)if len(need|set(page))<=32]
  if options:page=min(options)[1]
  else:page=len(pages);pages.append([])
  for pair in sorted(need):
   if pair not in pages[page]:pages[page].append(pair)
  f['packed_page']=page
  for cell in f['packed_8x16_cells']:cell['page_tile']=pages[page].index(cell['pair'])*2
  f['packed_max_sprites_per_scanline']=max(sum(c['y']<=y<c['y']+16 for c in f['packed_8x16_cells'])for y in range(-72,24))
 page_blob=b''.join(b''.join(packed_tiles[pair]for pair in page)+bytes(1024-32*len(page))for page in pages)
 for f in poses:
  for cell in f['packed_8x16_cells']:
   at=f['packed_page']*1024+cell['page_tile']*16
   assert page_blob[at:at+32]==packed_tiles[cell['pair']]
 (O/'wrestlers-pages.chr').write_bytes(page_blob)
 (O/'portraits.chr').write_bytes(portraits)
 (O/'native-descriptors.bin').write_bytes(b''.join(bytes.fromhex(c['descriptor_hex'])for c in chars))
 put('wrestlers.json',dict(original_ROM=SHA,characters=chars,poses=poses,
  unique_pattern_tiles=len(unique),unique_pattern_bytes=len(unique)*16,
  packed_8x16_unique_pairs=len(packed_tiles),packed_8x16_CHR_bytes=len(packed_tiles)*32,
  host_1KiB_pose_pages=len(pages),host_paged_CHR_bytes=len(page_blob),
  packed_max_sprites_per_scanline=max(f['packed_max_sprites_per_scanline']for f in poses),
  RGB_preview_palette=dict(path=str(palette_path),sha256=sha(palette_path)),
  renderer_checks=dict(passed=True,poses=len(poses),CPU_cycles=[min(cycles),max(cycles)],
   exact_original_CPU_packet_geometry_and_pattern_bytes=True,original_A62E_OAM_positions_and_palette_roles_checked=True,all_packed_8x16_rasters_and_palette_roles_exact=True,
   valid_frame_directory_boundaries='All original group/frame tables, root headers and record starts; no invalid pose IDs seeded.'),
  scope='Original body raster and palette-role assets. Portraits are original576B pages. No host, native playable proof, collision adaptation or global resource lease.'))
 print(json.dumps(dict(poses=len(poses),unique_tiles=len(unique),CHR_bytes=len(unique)*16,
  by_wrestler=[dict(name=c['name'],groups=c['groups_count'],poses=c['pose_count'],theme=c['theme'])for c in chars]),indent=2))

def music(frames):
 prg=raw();chars=tables(prg);bank=prg[2*32768:3*32768]
 rows=[];all_rom_reads=set()
 for c in chars:
  bus=Bus(bank);call(bus,0xe22e);bus.m[1]=c['theme'];initial=call(bus,0xe249)
  costs=[];apu_count=0;digest=hashlib.sha256();states={};loop=None;first_inactive=None
  for f in range(frames):
   bus.apu=[];costs.append(call(bus,0xe4de));apu_count+=len(bus.apu)
   for a,v in bus.apu:digest.update(struct.pack('<IHB',f,a,v))
   state=bytes(bus.m[0x500:0x5c0])+bytes([bus.m[2]])
   if first_inactive is None and all(bus.m[0x500+j*4]==0 for j in range(4)):first_inactive=f
   if loop is None and state in states:loop=[states[state],f]
   states[state]=f
  code_reads=[a for a in bus.reads if a>=0x8000]
  all_rom_reads.update(code_reads)
  ram_reads=[a for a in bus.reads if a<0x800 and not 0x100<=a<0x200]
  ram_writes=[a for a in bus.writes if a<0x800 and not 0x100<=a<0x200]
  assert all(0<=a<=8 or 0x500<=a<=0x5bf for a in ram_writes),ram_writes
  assert apu_count>100
  rows.append(dict(id=c['id'],name=c['name'],song=c['theme'],ticks=frames,
   channel_pointers=[word(bank,0xe900+c['theme']*8+j*2)for j in range(4)],tempo=bank[0x6222+c['theme']],
   init_cycles=initial,tick_cycles=[min(costs),max(costs)],APU_writes=apu_count,
   APU_write_trace_sha256=digest.hexdigest(),first_repeated_audio_state=loop,
   first_all_music_channels_inactive_tick=first_inactive,
   final_music_channel_flags=[bus.m[0x500+j*4]for j in range(4)],
   actual_RAM_read_addresses=sorted(ram_reads),actual_RAM_write_addresses=sorted(ram_writes),
   actual_ROM_read_min=min(code_reads),actual_ROM_read_max=max(code_reads)))
 # Conservative source bundles preserve original absolute pointers. These are
 # input assets, not assigned ROM banks or a claimed relocatable driver.
 slices=[('audio-low-original.bin',0x8018,0x88d7),('audio-driver-tables-original.bin',0xe222,0xe960),('audio-high-original.bin',0xe960,0xf83c)]
 assert all(any(a<=z<e for n,a,e in slices)for z in all_rom_reads)
 for name,start,end in slices:(O/name).write_bytes(bank[start-0x8000:end-0x8000])
 put('music.json',dict(original_ROM=SHA,passed=True,rows=rows,
  source_spans=[dict(file=n,bank=2,start=a,end=z,bytes=z-a)for n,a,z in slices],
  span_bytes=sum(z-a for n,a,z in slices),music_init=0xe249,music_tick=0xe4de,clear=0xe22e,
  all_six_theme_actual_ROM_reads_inside_extracted_spans=True,
  original_wrestler_song_binding='bank0:D1F6..D204 and D25C..D26A copy descriptor40 to BD/BE; B46C..B470 starts winner song through A227→bank2:8006→E249.',
  scope='Bounded instruction/APU-write checks of original music; no native audible, full-loop, relocation, source-fidelity-after-adaptation or NMI deadline verdict. These source bundles have not acquired any host bank/RAM lease.'))
 print(json.dumps(dict(passed=True,ticks_per_song=frames,source_bytes=sum(z-a for n,a,z in slices),rows=[{k:v for k,v in q.items()if k not in ['actual_RAM_read_addresses','actual_RAM_write_addresses']}for q in rows]),indent=2))

def moves():
 prg=raw();b=prg[:32768];chars=tables(prg);rows=[]
 for c in chars:
  for selector in c['original_input_action_selectors']:
   buttons=selector['input'].split('+');mask=sum(dict(A=128,B=64,Up=8,Down=4)[q]for q in buttons)
   bus=Bus(b);bus.m[0x2a]=(c['id']+1)%6;bus.m[0x2b]=c['id']
   bus.m[0x2c:0x30]=[96,128,180,180]
   bus.m[0x0d]=mask;bus.m[0x0e]=mask&192
   cost=call(bus,0xaf4d)
   assert bus.m[0x3e]==selector['side_action'],(c['name'],selector,bus.m[0x3e])
   rows.append(dict(character=c['id'],name=c['name'],input=selector['input'],requested_native_action=bus.m[0x3e],CPU_cycles=cost))
 scripts=b[0xf01e-0x8000:0xfe50-0x8000]
 (O/'native-action-directories-scripts.bin').write_bytes(scripts)
 put('moves.json',dict(passed=True,source_CPU_only=True,native_run=False,rows=rows,
  checks='66 neutral native ring selector cases execute original AF4D through original B11F descriptor lookup; action request3E matches descriptor offsets0A..14.',
  original_A='Kick according to established prior native controller verification.',original_B='Punch according to established prior native controller verification.',
  pin='Native Down+A selector uses descriptor10; native pin mechanics also require fallen opponent, position/contact and referee scripts.',
  script_bundle=dict(bank=0,start=0xf01e,end=0xfe50,bytes=len(scripts)),
  scope='Original selector and raw script assets only. Wrestling move names/special effects, full interpreter semantics and proposed platform controls require separate host adaptation. Do not identify a real-world signature move from a screenshot.'))
 print('Original native input-selector cases passed:',len(rows))

def disassembly():
 prg=raw();specs=[(0,0xd1a5,0xd284),(0,0xb44d,0xb473),(0,0xc65b,0xc6b0),(0,0xa62e,0xa70b),
 (0,0xaf4d,0xb14d),(0,0xbb28,0xbcc9),(1,0x83a6,0x847e),(2,0x8914,0x89ec),(3,0x806f,0x8146),(2,0xe222,0xe960)]
 lines=[]
 for bank,start,end in specs:
  lines.append(f'; Original physical32K bank{bank}, CPU{start:04X}..{end:04X}; bytes included for audit.\n')
  m=MPU();m.memory[0x8000:]=prg[bank*32768:(bank+1)*32768];d=Disassembler(m)
  while start<end:
   n,s=d.instruction_at(start);lines.append(f'{start:04X}  '+bytes(m.memory[start:start+n]).hex(' ').ljust(9)+' '+s+'\n');start+=n
 (O/'original-call-paths.asm.txt').write_text(''.join(lines))

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['assets','music','moves','disassembly']);p.add_argument('--frames',type=int,default=2400);a=p.parse_args()
 if a.action=='assets':assets()
 elif a.action=='music':music(a.frames)
 elif a.action=='moves':moves()
 else:disassembly()
