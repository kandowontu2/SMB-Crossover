"""Original ROM palette authority and HP flag-reader semantics, compact only."""
from collections import Counter
from pathlib import Path
import copy,hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import prince_original_cpu_1101_v1 as P
from recover_prince_core_1101_v1 import O


def main():
 c=P.boot();pal=[];palcount=0;saved=P.Bus.__setitem__
 def write(m,a,v):
  nonlocal palcount
  if isinstance(a,int)and 0x2000<=a<0x4000 and a&7==7 and 0x3f10<=m.pa(m.v)<0x3f20:
   palcount+=1
   if len(pal)<32:pal.append(dict(PPU=m.pa(m.v),value=v&255,bank=7 if c.pc>=0xc000 else m.bank,CPU_PC_during_store=c.pc))
  return saved(m,a,v)
 P.Bus.__setitem__=write
 try:
  for frame in range(900):P.frame(c,16 if 120<=frame<123 or 300<=frame<303 or 600<=frame<603 else 0)
 finally:P.Bus.__setitem__=saved
 m=c.memory;assert m[0x60e]&0x80 and m[0x6cf]>0
 palette=list(m.ppu[0x3f10:0x3f20]);attrs=sorted({m.oam[i+2]&3 for i in range(0,256,4)if m.oam[i]<240})
 start=dict(actor=list(m[0x60e:0x61c]),HP=m[0x6cf],source6D2=m[0x6d2],source6DC=m[0x6dc],sprite_palette=palette,visible_original_palette_indices=attrs)
 fixture=copy.deepcopy(c);original=(fixture.pc,fixture.sp,fixture.a,fixture.x,fixture.y,fixture.p,fixture.memory.bank);fixture.memory.switch(5)
 hp_before=fixture.memory[0x6cf];actor_before=bytes(fixture.memory[0x60e:0x61c]);out=P.call(fixture,0x8574,a=83,x=71,y=109,p=0x31)
 assert fixture.memory[0x6cf]==hp_before-1 and bytes(fixture.memory[0x60e:0x61c])==actor_before
 direct=dict(before_HP=hp_before,after_HP=fixture.memory[0x6cf],source6D2=fixture.memory[0x6d2],source6DC=fixture.memory[0x6dc],actor_state_unchanged=True,registers_CPU=list(out))
 fixture.pc,fixture.sp,fixture.a,fixture.x,fixture.y,fixture.p,bank=original;fixture.memory.switch(bank)
 active=False;readers=Counter();writers=Counter();get=P.Bus.__getitem__;put=P.Bus.__setitem__
 def read(mm,a):
  if active and isinstance(a,int)and a in [0x6d2,0x6dc]and fixture.pc>=0x8000:
   pc=fixture.pc-1;bank=7 if pc>=0xc000 else mm.bank;readers[f'{bank}:{pc:04X}:{a:04X}']+=1
  return get(mm,a)
 def store(mm,a,v):
  if active and isinstance(a,int)and a in [0x6d2,0x6dc]and fixture.pc>=0x8000:
   pc=fixture.pc-1;bank=7 if pc>=0xc000 else mm.bank;writers[f'{bank}:{pc:04X}:{a:04X}:{v&255:02X}']+=1
  return put(mm,a,v)
 P.Bus.__getitem__=read;P.Bus.__setitem__=store;rows=[]
 try:
  for frame in range(16):
   active=True;P.frame(fixture,0);active=False
   rows.append(dict(frame=frame,HP=fixture.memory[0x6cf],source6D2=fixture.memory[0x6d2],source6DC=fixture.memory[0x6dc],action=fixture.memory[0x616],mode=fixture.memory[0x618],pose=fixture.memory[0x617]))
 finally:P.Bus.__getitem__=get;P.Bus.__setitem__=put
 # Read/store PC is one byte past the opcode while py65 resolves absolute
 # operands. Bind every recorded address back to original binary bytes.
 sites=[];rom=P.donor()
 for key in sorted(set(':'.join(k.split(':')[:3])for k in readers)|set(':'.join(k.split(':')[:3])for k in writers)):
  bank,pc,addr=key.split(':');bank=int(bank);pc=int(pc,16);addr=int(addr,16);offset=16+bank*16384+(pc&16383);data=rom[offset:offset+3]
  sites.append(dict(bank=bank,PC=pc,field=addr,original_bytes=data.hex(),absolute_operand_matches=int.from_bytes(data[1:3],'little')==addr,read_count=readers.get(key,0),write_examples={k:v for k,v in writers.items()if k.startswith(key+':')}))
 q=dict(passed=True,source_CPU_only=True,native_host=False,ROM_written=False,donor_SHA256=P.SHA,natural_original_start_frames=900,natural_state=start,source_sprite_palette_PPU_3F10_3F20=palette,source_palette_write_count=palcount,bounded_original_palette_writes=pal,original_8574_fixture=direct,original_NMI_continuation_after_HP_only_fixture=rows,original_6D2_6DC_reader_writer_sites=sites,semantics='Original8574 alone decrements playerHP, publishes6D2=1/6DC=8 and does not modify actor action/mode/script. These flags are not by themselves proved native-contact grace or reaction predicates. Follow actual original readers/callers before mapping hurt.',scope='Natural original reset/menu/play palette bytes plus one explicit original8574 instruction fixture and16 genuine original NMI/main continuations. No host outcome seeding, native contact policy, invented cooldown or implemented palette/health adapter.',bindings={(p.relative_to(R).as_posix()if p.is_relative_to(R)else str(p)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),Path(P.__file__),P.DONOR]})
 (O/'palette-health-authority-v29.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','bounded_original_palette_writes','original_NMI_continuation_after_HP_only_fixture']}))


if __name__=='__main__':main()
