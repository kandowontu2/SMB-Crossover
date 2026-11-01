"""Current58 typed native art table/record domains beside Tank's four loans."""
from pathlib import Path
import hashlib,itertools,json,re,sys,zipfile
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from prepare_mario_tank_visible_1101_v5 import O
from audit_mario_tank_music_tail_1101_v5 import P,PIN
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
import check_hogan_current_bounded_v1 as M
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 b=scoped_load(P/'candidate.nes');assert sha(b['raw'])==PIN;tables=[];records={};rows=[]
 def data(name,n):at=location(b,name);return b['raw'][at:at+n]
 def peek(bank,pc,n):assert 0xc000<=pc and pc+n<=0xe000;at=16+bank*8192+pc-0xc000;return b['raw'][at:at+n]
 def record(bank,pc,lo,hi):
  n=peek(bank,pc,1)[0];assert n%4==0 and n<=252 and lo<=pc and pc+1+n<=hi,(bank,hex(pc),n,hex(lo),hex(hi));records[(bank,pc)]=(n+1,sha(peek(bank,pc,n+1)));return pc+1+n
 def split(prefix,count,bank,lo,hi,banks=None):
  lows=data(prefix+'Lo',count);highs=data(prefix+'Hi',count);ends=[]
  for i,(a,z)in enumerate(zip(lows,highs)):
   if banks is None or (banks[i]&127)==bank:ends.append(record(bank,a+256*z,lo,hi))
  tables.append(dict(table=prefix,entries=count,target_bank_entries=len(ends),bank=bank,maximum_record_end=max(ends)));return max(ends)
 def interleaved(name,count,bank,lo,hi):
  d=data(name,count*2);ends=[]
  for i in range(0,len(d),2):
   pc=d[i]+256*d[i+1];assert lo<=pc<hi
   # Gimmick deliberately retains its original zero-Y-terminated format,
   # not the host's count header. The real emitter advances exactly4bytes.
   for offset in range(0,256,4):
    assert pc+offset<hi
    if peek(bank,pc+offset,1)==b'\0':break
   else:raise AssertionError(('Gimmick unterminated record',hex(pc)))
   n=offset+1;records[(bank,pc)]=(n,sha(peek(bank,pc,n)));ends.append(pc+n)
  tables.append(dict(table=name,entries=count,bank=bank,original_zero_Y_terminated=True,maximum_record_end=max(ends)))
 # Every native Samus pose/status, crouch, death debris, MM damage spark and
 # generated special-shot artwork index. Include all source table entries,
 # rather than only frames observed in one stage.
 for face in ['Left','Right']:
  split('SamusPose'+face,93,13,0xc000,0xdfc3)
  split('SamusCrouch'+face,6,13,0xc000,0xdfc3)
  split('SsArt'+face,115,13,0xc000,0xdfc3,data('SsArtBanks',115))
 split('SamusGuts',24,13,0xc000,0xdfc3);split('MmHurtFx',4,13,0xc000,0xdfc3)
 for name in ['SsNativeBrick','SsNativeChunk']:record(13,address(b,name),0xc000,0xdfc3)
 assert address(b,'SsNativeChunk')+1+data('SsNativeChunk',1)[0]==0xdfc3
 rows.append(dict(bank=13,typed_pointer_families=10,source_indices=dict(SamusPose='3status×31',SamusCrouch='3status×2',SamusGuts='4families×6',MmHurtFx='4sparks',SsArt='all115generatedIDs'),maximum_record_end=0xdfc3,proposed_gap=[0x1fc3,0x2000],old_art_records_closed=True))
 # Gimmick uses explicit22/66 guards before its word tables. Effects derive
 # their index from the top2bits, and the palette is a fixed sixteen-byte row.
 interleaved('GmHeroTable',22,73,0xd920,0xdfbe);interleaved('GmStarTable',66,73,0xd920,0xdfbe);interleaved('GmEffectTable',4,73,0xd920,0xdfbe)
 assert address(b,'GmStage0Palette')+16==0xdfbe
 rows.append(dict(bank=73,typed_word_tables=dict(hero=22,star=66,effect=4),palette_half_open=[address(b,'GmStage0Palette'),0xdfbe],other_indexed_data=dict(GmHeroPage=22,GmHurtFrame=26),maximum_record_end=0xdfbe,proposed_gap=[0x1fbe,0x2000],old_art_records_closed=True))
 # DK's nine body poses and six native barrel phases use exact split tables.
 split('DkPose',9,12,0xdb13,0xdfad);split('DkBarrel',6,12,0xdb13,0xdfad);record(12,address(b,'DkMenuRecord'),0xdb13,0xdfad)
 assert address(b,'DkBarrelPalette')+4==address(b,'DkArtEnd')and address(b,'DkMenuName')+int(b['syms']['DkMenuName']['size'],0)==0xdfad
 rows.append(dict(bank=12,typed_split_tables=dict(body=9,barrel=6),direct_menu_record=True,body_palette=4,barrel_palette=4,name_callback_half_open=[address(b,'DkMenuName'),0xdfad],proposed_gap=[0x1fad,0x2000],old_art_records_closed=True))
 # Bank68 also contains Darkwing's earlier C000..DB09 atlas. Close every
 # body/weapon record, every animation base+phase, before considering Maaa.
 for face in ['L','R']:
  split('DwPose'+face,71,68,0xc000,0xdb09);split('DwWeapon'+face,30,68,0xc000,0xdb09)
 base=data('DwAnimationBase',42);last=data('DwAnimationLast',42);weapon=data('DwWeaponBase',42);animations=0
 for i in range(42):
  for phase in range(last[i]+1):assert base[i]+phase<71;animations+=1
 assert all(v<30 for v in weapon)
 # Native Mario's legal object metasprites0..62 map to exactly49 six-part
 # packets,49 pages/heads and three neck cells. Neck length affects OAM/Y,
 # never the table selector; every possible length gives at most32 segments.
 frame=data('MaaFrameMap',63);heads=data('MaaHeads',49);pages=data('MaaPages',49);assert len(set(frame))==49 and max(frame)<49
 assert address(b,'MaaTiles')+49*6==address(b,'MaaNeckRepeat')and address(b,'MaaNeckRepeat')+3==address(b,'MaaNeckOdd')and address(b,'MaaNeckOdd')+3==0xdecc
 assert all(0<=((p-(813&255))&255)<3 for p in pages)
 oldbus=M.Bus
 class Reads(oldbus):
  def __getitem__(self,i):
   if isinstance(i,int)and 0xc000<=i<0xe000 and getattr(self,'watch',False)and self.rawtags[2]in[140,196]:self.reads.add(i)
   return super().__getitem__(i)
 M.Bus=Reads
 try:m=M.fresh(b)
 finally:M.Bus=oldbus
 m.watch=True;m.reads=set();m.raw_page(2,140);M.put(m,CurrentBankC=140,VRAM_Buffer1_Offset=0)
 M.invoke(m,'DkMenuName')
 # Actual shared far-call name emitter reads exactly the final16-byte name.
 name_reads=m.reads&set(range(0xdf9d,0xe000));assert name_reads==set(range(0xdf9d,0xdfad))
 rows[2]['actual_terminal_name_reads']=sorted(name_reads)
 m.watch=True;m.reads=set();m.raw_page(2,196);M.put(m,CurrentBankC=196,SelectedCharacter=0,MarioVariant=2,OperMode=1,OperMode_Task=3,CrossoverMenuState=0,Player_Y_HighPos=1,Player_Y_Position=96,Player_Rel_XPos=112,Player_SprAttrib=0)
 c=NesMPU(memory=m,pc=address(b,'MaaBodyDraw'));c.p=0x31;c.sp=224;calls=0
 def leaf(name):
  c.pc=address(b,name);c.stPushWord(0x5aff)
  for _ in range(10000):
   if c.pc==0x5b00:break
   assert m[c.pc]!=0,('ActualMaaa reader BRK',hex(c.pc));c.step()
  else:raise AssertionError('ActualMaaa leaf bound')
  assert c.sp==224
 for pose,face,length in itertools.product(range(63),[1,2],[0,1,7,8,9,31,127,255]):
  M.put(m,ObjectMetasprite=pose,PlayerFacingDir=face,MaaaLength=length,CurrentOAMOffset=0,R3=0,R4=112,R5=0,R6=96,R7=1)
  for i in range(64):m[address(b,'Sprite_Data')+4*i]=248
  leaf('MaaBodyDraw');leaf('MaaDrawNeck');calls+=2
 assert not any(0xdecc<=a<0xdf20 for a in m.reads)
 rows.append(dict(bank=68,Darkwing_body_weapon_records=202,Darkwing_animation_phase_cases=animations,Maaa_frame_map_entries=63,Maaa_distinct_poses=49,Maaa_parts_per_pose=6,Maaa_neck_variants=3,Maaa_all256_lengths_bounded_to32_segments=True,actual_Maaa_body_neck_calls=calls,actual_old_ROM_read_max=max(m.reads)+1,maximum_record_end=0xdecc,proposed_gap=[0x1ecc,0x1f20],old_art_records_closed=True))
 mapping=json.loads((O/'remaining-tail-source-map.json').read_text());sources={}
 for row in mapping['remaining_review']:
  if row['bank']in[12,13,68,73]:
   for f in row['source_definitions']:sources[f['path']]=f['sha256']
 root=R/'build/bt-ready-menu-1031-v2/joint/src'
 for n in ['samus.s','samus_metasprites.inc','samus_weapons.s','samus_crouch_collision.s','special_weapons.s','special_art.inc','megaman_injury.s','megaman_injury_art.inc','darkwing_core.s','darkwing_weapons.s','darkwing_art.inc']:
  p=root/n;sources[str(p)]=sha(p.read_bytes())
 q=dict(passed=True,current_ROM_sha256=PIN,formal_grant=False,old_art_reader_rows=rows,typed_pointer_tables=tables,unique_record_count=len(records),record_digest=sha(json.dumps(sorted((k,v)for k,v in records.items())).encode()),source_bindings=sources,limits=['All declared source-legal indexed art records and terminal data extents are checked against actual58 compiled tables. Maaa C-window routines execute natively with boundary lengths.','This receipt does not itself allocate ROM. The typed caller index/source contracts, any shared old generic data reader, source producer endpoint caps and current full bank identity remain subject to parent review.','DK final44B name callback and Maaa ART routines are code mixed with art. Their exact terminal CFG/JSR contracts must remain part of the parent whole-owner review, rather than being inferred from data table bounds.'],bindings={str(Path(__file__).relative_to(R)):sha(Path(__file__).read_bytes())})
 (O/'art-tail-readers.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(passed=True,records=len(records),tables=len(tables),Maaa_native_calls=calls,art_banks=[r['bank']for r in rows])))
if __name__=='__main__':main()
