"""Finite original-ROM damage/freeze/item-art evidence; proposal, no host edits."""
from pathlib import Path
import itertools,json,sys
R=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import rogue_dawn_map_v1 as ref
import prepare_rogue_dawn_art_v1 as art
from verify_native_relocation import NesMPU
O=R/'build/rogue-dawn-host-transactions-v3'

def prefix(m,pc,stop,a=0,x=0,y=0):
 c=NesMPU(memory=m,pc=pc);c.sp=0xf0;c.a,c.x,c.y=a,x,y;c.stPushWord(0x5aff)
 trace=[]
 for _ in range(10000):
  if c.pc==stop:return c,trace
  assert m[c.pc]!=0,hex(c.pc)
  trace.append(c.pc);c.step()
 raise AssertionError(('source timeout',hex(c.pc)))

def main():
 raw=ref.ROM.read_bytes();assert ref.digest(raw)==ref.EXPECTED
 hp=[]
 for bank,typ,sign in itertools.product([2,4,6,8,10],range(16),[0,128]):
  m=art.Memory(ref.cpu_image(raw,lower_bank=bank));m[0x6b02]=typ;m[0x40f]=sign
  c,tr=prefix(m,0xf85a,0x5b00)
  base=m[0x962b+typ];assert m[0x40b]==((base<<1)&255 if sign else base)
  hp.append(dict(area=bank,type=typ,signed_subtype=bool(sign),base=base,actual=m[0x40b]))
 damage=[]
 for weapon,gear,flags,stock in itertools.product([1,2,3,7,10,11,0x81],[0,0x40,0x80,0xc0],[0,0x40],range(1,10)):
  m=art.Memory(ref.cpu_image(raw,lower_bank=2));m[0x40e]=weapon;m[0x6878]=gear;m[0x0a]=flags;m[0x40b]=stock
  c,tr=prefix(m,0xda92,0xf60f)
  decrement=4 if(weapon==3 and gear&0xc0)or(weapon==11 and flags&0x40)else 2 if weapon in [2,3]else 1
  # Four sequential DECs stop at the first actual zero, never wrap below it.
  assert m[0x40b]==max(0,stock-decrement),(weapon,gear,flags,stock,m[0x40b])
  damage.append(dict(weapon=weapon,gear=gear,flags=flags,before=stock,after=m[0x40b],CPU=c.processorCycles))
 freeze=[]
 for clock in range(8):
  m=art.Memory(ref.cpu_image(raw,lower_bank=2));m[0x404]=0x20;m[0x40e]=3;m[0x0a]=0x10;m[0x6b02]=4;m[0x6af4]=2;m[0x40b]=2;m[0x4b]=0
  c,tr=prefix(m,0xf536,0x5b00)
  assert [m[0x6af4],m[0x40c],m[0x40d],m[0x40b]]==[4,2,64,2]
  m[0x404]=0;m[0x40e]=0;decrements=[]
  for tick in range(1,514):
   m[0x2d]=(clock+tick)&255;before=m[0x40d]
   c,tr=prefix(m,0xf43e,0xf480)
   if 0xf456 in tr:decrements.append(tick)
   if m[0x6af4]!=4:break
  assert tick==512-clock and len(decrements)==64 and m[0x6af4]==2
  freeze.append(dict(initial_clock_mod8=clock,active_updates=tick,actual_counter_decrements=len(decrements),first_decrement=decrements[0],last_decrement=decrements[-1],restored_action=m[0x6af4],restored_native_timer=m[0x40d]))
 # Actual object producerA603 selects50..59; actual original decoder sees
 # source object slot40, not a player pose or host8x16 allocator. Palette-cycle
 # and the producer's special second-part overrides remain explicit metadata.
 frames=[];pairs=[]
 for item in range(10):
  m=art.Memory(ref.cpu_image(raw,lower_bank=2));slot=0x40;m[0x4b]=slot;m[0x55]=0;m[0x340]=1;m[0x343]=0x50+item;m[0x34d]=128;m[0x34e]=128;m[0x49]=2;m[0x6b]=0x80
  for i in range(0x200,0x300,4):m[i]=248
  c=art.call(m,0xde4a)
  parts=[list(m[i:i+4])for i in range(0x200,0x200+m[0x5b],4)]
  if item in[2,6,7]and len(parts)>1:parts[1][2]=1 if item==7 else 0
  pixels=art.source_pixels(raw,parts);chunks=[]
  if pixels:
   for attr in sorted({a for v,a in pixels.values()}):
    for y in range((min(y for x,y in pixels)//16)*16,max(y for x,y in pixels)+1,16):
     for x in range((min(x for x,y in pixels)//8)*8,max(x for x,y in pixels)+1,8):
      p=art.encode(pixels,x,y,attr)
      if any(p):
       if p not in pairs:pairs.append(p)
       chunks.append(dict(pair=pairs.index(p),attr=attr,x=x,y=y))
  frames.append(dict(item=item,frame=0x50+item,source8x8_parts=parts,opaque_pixels=len(pixels),host8x16_parts=chunks,decoder_CPU=c.processorCycles))
 assert len(pairs)<=64
 # Authenticated audio is not equal to old Metroid driver/data. Comparison is
 # read-only, not an import, allocation or a playable-audio claim.
 base=ref.BASE.read_bytes();audio=[]
 for physical in[3,5,7,9,11]:
  x=raw[16+physical*8192+0x13b4:16+(physical+1)*8192]
  options=[]
  for bank in range(8):
   y=base[16+bank*16384+0x33b4:16+(bank+1)*16384]
   options.append(dict(stock16Kbank=bank,differing_bytes=sum(a!=b for a,b in zip(x,y))))
  audio.append(dict(physical8Kbank=physical,original_range='B3B4..BFFF',bytes=len(x),sha256=ref.digest(x),closest_stock=sorted(options,key=lambda r:r['differing_bytes'])[:2]))
 data=dict(passed=True,source_only=True,native_run=False,source_ROM=ref.binding(ref.ROM),HP_constructor=dict(entry='63:F85A',HP_table='current real area962B',signed_subtype='source040F bit7 doubles modulo256; FF sentinel is not normal HP',cases=hp),damage=dict(entry='62:DA92',real_continuation='63:F60F; prefix stops before native enemy death/draw owner',cases=len(damage),case_SHA256=ref.digest(json.dumps(damage,sort_keys=True).encode()),rules=['ordinary beam/type1=1','Wave/type2=2','Ice/type3 damage branch=4 with actual Ice/Wave gear; first freeze branch does not damage','bomb/type10=1','missile/type11=1 normally,4 for actual source$0B missile property','Screw is not DA92 generic damage: actual F282/CD9C eligibility and F5D3..F5DC type81 terminal branch must remain distinct']),freeze=dict(first_contact='F536/F515: source counter40/state4/saved previous action',update='F43E/F450:64 decrements only Clock&7==0, then restore previous action and native969B timer',rows=freeze,next_hit='state4 skips new freeze into F579/DA92 and actual hurt/damage/thaw; original property exceptions remain required'),SMB_mapping_proposal=dict(approved=False,ordinary_HP={'Goomba':2,'Koopa':4,'Piranha':4,'Spiny':4,'HammerBro':8,'Lakitu':8},classification='Explicit SMB enemy-to-source class adaptation using genuine source HP values1/2/4/8, not native Rogue species equality',missile_special='Source040E=0B is the missile weapon/action kind, NOT an enemy species. Its4-debit branch additionally requires source040F mini-boss bit40; propose ordinary1 and an explicitly assigned Bowser mini-boss mapping4 only after approval',signed_double='Source040F bit80 is tough/doubleHP; bit40 is mini-boss. Do not equate Hard mode with either flag; propose no tough subtype until a real host class is declared',armor='Preserve real Buzzy/Bullet/native immunity decisions as declared host mapping; source properties/timers are separate requirements',Screw='Dedicated actual gear+air-spin admission and source eligibility, then real ShellOrBlockDefeat terminal owner only',actor_lifetime='Existing real Enemy_Flag/ID/YHigh plus native init/erase HP/freeze clears, no seeded target HP/Enemy_State outcome'),item_art_proposal=dict(approved=False,actual_producer='61:A603 selects(type&0F)|50; A614 draws before actual DC7F contact; no acquisition from this decoder test',frames=frames,unique_8x16_pairs=len(pairs),pattern_bytes=len(pairs)*32,reserved_Rogue_pages_used=9,already_reserved_unused_pages=7,request='No additional CHR reservation: one existing blank page inside680..695 suffices. Do not modify frozen art; append new authenticated item asset/recipe after approval.',descriptor_request='C94 art+175B bridge has no descriptor room. Request ~150B from approved A95 free tail, accessed through actual C95 mirror and restored before C94 control callbacks; this needs separate exact first-consumer hooks.',palette='Keep original cycle80..83 and special second-part overrides for item2/6/7; actual host palette leases/priority still open'),audio_closure=dict(approved=False,rows=audio,required='Real original driver/data relocation, original0600..068D workspace/ZP/APU ownership and acknowledgement/mixer before clearing private source request bytes; not old raw2 Metroid fallback',no_additional_allocation=True),bindings=[ref.binding(p)for p in[Path(__file__),ref.ROM,ref.BASE,R/'tools/prepare_rogue_dawn_art_v1.py']])
 data['item_art_proposal']['request']='No additional CHR reservation: '+str((len(pairs)+31)//32)+' existing blank pages inside680..695 suffice. Do not modify frozen art; append new authenticated item asset/recipe after approval.'
 out=O/'original-actor-item-proposal.json';out.write_text(json.dumps(data,indent=2)+'\n')
 print(json.dumps(dict(passed=True,HP_cells=len(hp),damage_cells=len(damage),freeze_updates=[r['active_updates']for r in freeze],item_pairs=len(pairs),item_bytes=len(pairs)*32,proposal=str(out))))
if __name__=='__main__':main()
