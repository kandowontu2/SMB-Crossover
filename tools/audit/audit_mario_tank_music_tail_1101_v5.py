"""Actual current58 LZ byte reader over every full-roster song entry."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from prepare_mario_tank_visible_1101_v5 import O
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
import check_hogan_current_bounded_v1 as M
P=R/'build/karnov-native-platform-1101-v1';PIN='58e50db6ceead7c3706087c92d6e49014f05ff8b80b000be30c27b4e7dfa11f2'
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 b=scoped_load(P/'candidate.nes');assert sha(b['raw'])==PIN;entries={};tables=[]
 for kind in ['Area','Loop','Event','EventLoop']:
  bank,lo,hi=[location(b,'Xg'+kind+n)for n in['Banks','Lo','Hi']];rows=[]
  for i in range(63):
   tag=b['raw'][bank+i];pc=b['raw'][lo+i]+256*b['raw'][hi+i];rows.append((tag,pc))
   if i>=49:entries.setdefault((tag,pc),[]).append((kind,i))
   else:assert tag<59 or tag==address(b,'ScroogeMusicIntro')//8192,('Unexpected old-row bank',kind,i,tag)
  tables.append(dict(name=kind,rows=63,full_mask_rows=14,table_sha256=sha(bytes(x for row in rows for x in[row[0],row[1]&255,row[1]>>8]))))
 oldbus=M.Bus
 class Reads(oldbus):
  def __getitem__(self,i):
   if isinstance(i,int)and 0xa000<=i<0xc000 and getattr(self,'watch',False)and self.rawtags[1]==243:self.reads.add(i)
   return super().__getitem__(i)
 M.Bus=Reads
 try:seed=M.fresh(b)
 finally:M.Bus=oldbus
 byte=address(b,'ExpandedAudioTick::Byte');reset=address(b,'ExpandedAudioTick::ResetLz');codebank=128|((location(b,'ExpandedAudioTick')-16)//8192);assert byte>=0xc000
 allreads=set();streams=[];total=0
 for (bank,pc),consumers in entries.items():
  m=M.fork(seed);m.watch=True;m.reads=set();m.raw_page(1,128|bank);m.raw_page(2,codebank);M.put(m,CurrentBank=128|bank,CurrentBankC=codebank,XgAudioBank=bank,XgAudioDepth=0,XgAudioPtr=pc&255);m[address(b,'XgAudioPtr')+1]=pc>>8
  c=NesMPU(memory=m,pc=reset);c.p=0x31;c.sp=224
  def leaf(target):
   c.pc=target;c.stPushWord(0x5aff)
   for _ in range(2000):
    if c.pc==0x5b00:break
    assert m[c.pc]!=0,('NativeLZ reader BRK',hex(c.pc));c.step()
   else:raise AssertionError('NativeLZ byte bounded')
   assert c.sp==224;return c.a
  leaf(reset);decoded=0;frames=0
  def read():
   nonlocal decoded
   decoded+=1;assert decoded<2000000,'Per-stream decoded byte budget';return leaf(byte)
  for _ in range(500000):
   command=read()
   if command in[254,255]:break
   if command<128:frames+=command;continue
   assert command in[128,129],('Corrupt full music mask',bank,pc,command,decoded)
   bits=read()+256*read()
   for _ in range(bits.bit_count()+(command&1)):read()
   frames+=1
  else:raise AssertionError('Source frame stream terminator bound')
  assert not any(0xa195<=a<0xa200 for a in m.reads),('Proposed115 gap consumed',bank,pc)
  allreads|=m.reads;total+=decoded;streams.append(dict(bank=bank,PC=pc,typed_consumers=consumers,decoded_bytes=decoded,represented_frames=frames,terminal=command,bank115_reads=len(m.reads),bank115_end=max(m.reads)+1 if m.reads else None))
 assert allreads and min(allreads)==0xa000 and max(allreads)+1==0xa195,(min(allreads),max(allreads))
 root=R/'build/bt-ready-menu-1031-v2/joint/src';paths=[root/n for n in['expanded_audio.s','expanded_music.inc','full_roster_music.inc']]+[Path(__file__)]
 q=dict(passed=True,current_ROM_sha256=PIN,proposed_gap=[0x195,0x200],formal_grant=False,typed_source_table_rows=tables,unique_full_mask_streams=len(entries),actual_native_LZ_Byte_calls=total,actual_source_streams=streams,bank115_unique_read_addresses=len(allreads),bank115_exact_half_open=[min(allreads),max(allreads)+1],no_proposed_gap_reads=True,source_terminator_controls=True,limits=['Current mask stream entries/loops/events and actual compiled byte/LZ/bank-crossing primitives execute. Outer APU mixer and full song playback timing are not needed for this data-read boundary.','Mike native audio owner beginsA200; this receipt closes full-roster mask stream readers, while native Mike code/header consumers remain a separate previous-owner contract.'],bindings={str(p.relative_to(R)):sha(p.read_bytes())for p in paths})
 (O/'music-tail-readers.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(passed=True,unique_streams=len(entries),native_Byte_calls=total,bank115_bounds=q['bank115_exact_half_open'])))
if __name__=='__main__':main()
