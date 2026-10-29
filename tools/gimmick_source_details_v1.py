"""Additive Gimmick original audio/palette/art evidence and read-only fit proposal."""
import collections,hashlib,json,sys
from pathlib import Path
from PIL import Image,ImageDraw
import gimmick_source_audit_v1 as G
R=G.R;REF=G.REF;B=R/'build';OUT=B/'gimmick-source-details-v1.json'
PARENT=B/'kamikaze-mario-host-v4/candidate.nes'

class Audio(G.Original):
 def __init__(self):
  self.select=0;self.psg_select=0;self.psg=[];self.data_banks=[]
  super().__init__(7)
 def __setitem__(self,p,v):
  if p==0x8000:self.select=v&15;self.writes.append((p,v));return
  if p==0xa000:
   self.writes.append((p,v))
   if self.select in[10,11]:
    bank=v&31;self.data_banks.append((self.select,bank));start=0xa000 if self.select==10 else 0xc000
    list.__setitem__(self,slice(start,start+8192),G.PRG[bank*8192:(bank+1)*8192])
   else:raise AssertionError(('unexpected audio mapper command',self.select,v))
   return
  if p==0xc000:self.psg_select=v&15;self.writes.append((p,v));return
  if p==0xe000:self.psg.append((self.psg_select,v));self.writes.append((p,v));return
  super().__setitem__(p,v)

def audio():
 cases=[]
 for request in [0x0d,0x10,0x15,0x17,0x1c,0x3e]:
  m=Audio();G.run(m,0x8000);m[0x70]=request;m[0x71]=1;cycles=[];hw=set();readbanks=set()
  for _ in range(64):
   c,tr=G.run(m,0x8009,limit=30000);cycles.append(c.processorCycles)
   hw.update(p for p,v in m.writes if 0x4000<=p<=0x4017)
  cases.append(dict(request=hex(request),callbacks=64,cycles=[min(cycles),max(cycles)],PSG_registers=sorted({p for p,v in m.psg}),PSG_stores=len(m.psg),native_APU=[hex(p)for p in sorted(hw)],data_PRG_banks=sorted(set(m.data_banks)),state_RAM='source0600..07FF plus actual70..8x control/pointers; complete live-range/IRQ/port closure remains unqualified'))
 return dict(init=dict(bank=7,CPU='8000'),callback=dict(bank=7,CPU='8009',actual_NMI_caller='31:EA9C',other_literal_caller='31:EC53 IRQ/split branch; scheduling must be resolved before port'),cases=cases,
  physical_limit='Source directly uses Sunsoft5B register-selectC000/dataE000 in addition to native APU. This is not an MMC5-compatible register substitution. Exact voice/envelope/noise usage and the additional5B tone allocation require a separate approved audio design; no channel suppression is proposed.',
  limits='Original code only, typed request71=1/70=id, exact PRG data mapping command0A; no full original NMI/IRQ/analogAPU/DMC-fetch/native capture. Hardware writes are recorded, not synthesized.')

def palette():
 m=G.Original();idx=m[0xe8ae];assert idx
 m[0xe9]=idx;c,tr=G.run(m,0xec6d)
 p=[v for at,v in m.writes if at==0x2007];assert len(p)==32
 return dict(stage0_room_variant0_palette_index=idx,actual_selector='31:E660 from31:E8AE[stage*8|roomLow3]',actual_publisher='31:EC6D',actual_sprite_palette_bytes=p[16:],all32_bytes=p,
  palette0=p[16:20],palette1=p[20:24],palette2=p[24:28],palette3=p[28:32],scope='Actual source palette publisher, typed stage0/roomlow0 selector; not all stages or a native visible epoch. Existing world/enemy host palettes must remain authoritative outside explicitly assigned hero/star slots.')

def preview(proof):
 rows=proof['hero_frames'];cols=11;scale=2;W=cols*56;H=2*76
 im=Image.new('RGB',(W,H),(64,72,80));d=ImageDraw.Draw(im)
 for i,row in enumerate(rows):
  x0=(i%cols)*56+28;y0=(i//cols)*76+55
  d.rectangle((i%cols*56+1,i//cols*76+1,i%cols*56+54,i//cols*76+74),outline=(180,180,180))
  d.text((i%cols*56+4,i//cols*76+3),str(i),fill='white')
  for yo,tile,attr,xo in row['parts']:
   dx=xo-256 if xo>=128 else xo;dy=yo-256 if yo>=128 else yo
   page=row['CHR_page'];base=page*1024+(tile&0x3e)*16
   for y in range(16):
    yy=15-y if attr&128 else y;at=base+(yy//8)*16+(yy%8)
    a,b=G.CHR[at],G.CHR[at+8]
    for x in range(8):
     xx=x if attr&64 else 7-x;color=((a>>xx)&1)|(((b>>xx)&1)<<1)
     if color:d.point((x0+dx+x,y0+dy+y),fill=[None,(35,35,35),(150,150,150),(250,250,250)][color])
 im=im.resize((W*scale,H*scale),Image.Resampling.NEAREST)
 path=B/'gimmick-original-hero-poses-v1.png';im.save(path)
 return dict(file=G.bind(path),description='All22 source hero records with actual source CHR pages12/13; original 8x16 geometry, attribute flips and transparent2bpp masks. Grayscale represents source bitplane classes, NOT a claimed final NES/world palette or host renderer.')

def allocator():
 sys.path.insert(0,str(R/'tools/audit'))
 from link_pit_rygar_sophia_audit_cpu import scoped_load
 from check_tmnt_render_oa import address,location
 b=scoped_load(PARENT);assert G.sha(b['raw'])=='737d71af449b70a73b1d13f228efb6cfa819ea027219f605344861fb0e2b0624'
 start=location(b,'X5MenuCharacters');count=address(b,'X5MenuPresent')-address(b,'X5MenuCharacters');present=location(b,'X5MenuPresent')
 assert count==28
 menu=dict(slots=count,requested_slot25=dict(actual_raw=b['raw'][start+25],present=b['raw'][present+25]),raw26_present=False)
 assert b['raw'][present+25]==0 and 26 not in b['raw'][start:start+count]
 # Actual emitted source extents, not a claim that FF padding within another
 # owner's segment is free. Existing/future approved leases stay excluded.
 occupied=[False]*1048576
 for seg in b['segs'].values():
  if 'ooffs'not in seg or not int(seg['size'],0):continue
  lo=int(seg['ooffs'],0)-16;hi=lo+int(seg['size'],0)
  if lo<0 or lo>=1048576:continue
  occupied[lo:min(hi,1048576)]=[True]*(min(hi,1048576)-lo)
 # Explicit protected future leases supplied by owners; whole uncertain
 # banks are conservative exclusions, not an invitation to consume padding.
 protected={0,4,5,22,26,62,63,67,70,71,72,74,78,79,80,81,83,84,85,86,87,88,90,93,94,95,96,97,98,116,117,118,119,120,121,124,125,126,127}
 gaps=[]
 for bank in range(128):
  if bank in protected:continue
  p=bank*8192;i=0
  while i<8192:
   if occupied[p+i]or b['raw'][16+p+i]!=255:i+=1;continue
   lo=i
   while i<8192 and not occupied[p+i]and b['raw'][16+p+i]==255:i+=1
   if i-lo>=1024:gaps.append(dict(bank=bank,offset=[hex(lo),hex(i)],bytes=i-lo,A_window=[hex(0xa000+lo),hex(0xa000+i)],C_window=[hex(0xc000+lo),hex(0xc000+i)]))
 return dict(parent=G.bind(PARENT),DBG=G.bind(PARENT.with_suffix('.dbg')),MAP=G.bind(PARENT.with_suffix('.map')),menu=menu,
  unallocated_source_extent_FF_candidates=gaps,
  proposal=dict(CORE_bytes=6144,ART_bytes=3072,CHR_bytes=4096,active_RAM_bytes=128,persistent_RAM='Prefer12 owner-exclusive bytes, actual span NOT allocated. If no persistent space remains, reserve those12 within active128 and explicitly retain across own scenes/lives; coldmenu/newgame constructor before every private read, no global overlay marker.',
   audio='Source C07 driver and banked song data need separate full closure/5B allocation; no8KB estimate is treated as approved fit.',
   actual_lease_status='NO PRG/CHR/RAM allocated or mutated. Candidate gaps are only emitted-owner/FF evidence on immutable737d; final root live/private reservations and raw26 admission must be reconciled before approval. Do not infer current ac126 layout from this parent.'),
  protected_whole_banks=sorted(protected))

def main():
 assert not OUT.exists()
 base=B/'gimmick-source-audit-v1.json';proof=json.loads(base.read_text())
 # Correct the generic preview metadata additively: star records use BOTH
 # current hero slot0 (pages12/13) and star slot1(page8), not page8 alone.
 star_slots=sorted({((p[1]&1)*4)+((p[1]&0xfe)//64)for row in proof['star_frames']for p in row['parts']})
 assert star_slots==[0,1]
 a=audio();pal=palette();fit=allocator();pic=preview(proof)
 result=dict(status='READ_ONLY_PORT_PLAN_NOT_IMPLEMENTED_OR_ALLOCATED',native=False,base=G.bind(base),original=G.bind(G.ROM),tool=G.bind(__file__),audio=a,palette=pal,allocation=fit,preview=pic,
  additive_correction=dict(base_field='star_frames[*].CHR_page=8 is only the dedicated star slot1 page; NOT a whole-record pixel binding',actual_tile_dependencies=dict(PPU_slot0='current hero E1 page12 or13',PPU_slot1='E2 page8'),original_mapper_publisher='31:F06B writes E1/E2 to FME7 regs0/1',host_obligation='Preserve per-part source tile-page dependency, including hurt/pose page changes; configurable host physical page, no fixed generic star-page assumption.'),
  retained_source_control_setup_findings=['First horizontal open-loop run fell below original map and returned through native death path before pre-terrain stop. Horizontal tests explicitly retype stableY each isolated step; no standing/terrain claim.',
   'Initial50-update freefall exceeded valid source region for short jump. Bounded30-update source arc captures every tested apex without pretending native landing.',
   'Initial bounce oracle incorrectly treated EORFF/CLC/ADC09 as negation+9. Actual result is -previousVY+8; observed48->216 retained in base proof.'],
  bindings=[G.bind(REF/'GIMMICK-JPN3.asm'),G.bind(REF/'GIMMICK-JPN14.asm'),G.bind(REF/'GIMMICK-JPN15.asm')])
 OUT.write_text(json.dumps(result,indent=2)+'\n',newline='\n')
 print(json.dumps(dict(status=result['status'],proof=G.bind(OUT),gaps=fit['unallocated_source_extent_FF_candidates'],palette0=pal['palette0'],audio=a['cases'],preview=pic['file'])))
if __name__=='__main__':main()
