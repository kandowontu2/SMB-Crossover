"""CPU full cold/header/foreign-unwind proof; ungranted proposal only."""
import json,sys
from pathlib import Path
import prepare_bubble_bobble_common_cold_1102_v4 as P
import check_bubble_bobble_common_cold_1102_v4 as C
import check_hogan_current_bounded_v1 as N
from check_tmnt_render_oa import address
sys.path.insert(0,str(P.R/'tools/reference'))
import bubble_bobble_native_model_1101_v3 as B
O=P.O


def main():
 base=P.scoped_load(P.ROM);assert P.sha(base['raw'])==P.PIN
 layout=json.loads((O/'common-owner-layout.json').read_text());lab=layout['labels'];cookie=bytes.fromhex(layout['BB_cookie']);image=(O/'native-private.bin').read_bytes()
 b=C.patched(base,[(123,0xaf40,(O/'common-split.bin').read_bytes()),(123,0xb9d6,(O/'common-split-map.bin').read_bytes()),(65,0xae00,(O/'common-owner.bin').read_bytes())])
 raw=bytearray(b['raw']);pages=[301,305,337,362,363,440,819,666]
 for i,page in enumerate(pages):raw[1048592+page*1024:1048592+(page+1)*1024]=image[i*1024:(i+1)*1024]
 art=(O/'native-helper.chr').read_bytes();raw[1048592+441*1024:1048592+442*1024]=art
 b['raw']=bytes(raw);results={};cases=[]
 for owner in[37,39]:
  for label,fault in [('cold',None),('readback',(3,2048)),('helper-readback',(2,0x1320)),('protected','locked'),('disabled-NMI',None)]:
   if owner==37 and label=='helper-readback':continue
   m=C.ready(b);N.put(m,SelectedCharacter=owner)
   if fault=='locked':m.protection=[0,0]
   elif fault:m.corrupt_at=fault
   scratch=bytes(m[3:11]);maps=list(m.rawtags);r=C.call(m,lab['CoCold'],nmi=label=='disabled-NMI')
   assert bytes(m[3:11])==scratch and m.rawtags==maps and(r['A'],r['X'],r['Y'])==(83,71,109),(owner,label,r)
   assert m.ppuctrl==160 and m.toggle==0
   if fault:assert not r['P']&1 and m.ram[2][0x1fe0]!=0xa7,(owner,label,r)
   else:
    assert r['P']&1 and m.ram_writes[-1]==(2,0x1fe0,0xa7),(owner,label,r,m.ram_writes[-3:])
    before=m.ppu_reads;writes=len(m.ram_writes);warm=C.call(m,lab['CoCold'])
    assert warm['P']&1 and m.ppu_reads==before and len(m.ram_writes)==writes
    if owner==39:
     assert m.ram[2][:1024]==bytes(1024)and m.ram[2][1024:4096]==bytes([0xa5])*(4096-1024)
     assert bytes(m.ram[2][4096:5120])==art and m.ram[2][5120:0x1fe0]==bytes([0xa5])*(0x1fe0-5120)
     assert m.ppu_reads==2*9216+18
     assert m.ram[2][0x1fd0:0x1fd3]==bytes([0xa5])*3
     expected=bytearray(image);expected[0x1fe0:0x1ff0]=cookie;assert m.ram[3]==expected
   cases.append(dict(owner=owner,case=label,result=r))
 results['whole_two_owner_cold_warm_failures']=cases
 # Every header byte in either physical bank is required; this service helper
 # leaves application scratch/maps/PPU and cache bytes completely unchanged.
 poison=0
 for owner in[37,39]:
  m=C.ready(b);N.put(m,SelectedCharacter=owner);assert C.call(m,lab['CoCold'])['P']&1
  for bank in[2,3]:
   for i in range(16):
    m.ram[bank][0x1fe0+i]^=1;scratch=bytes(m[3:11]);maps=list(m.rawtags);before=[bytes(r)for r in m.ram];reads=m.ppu_reads;writes=len(m.ram_writes)
    r=C.call(m,lab['CoCheckCode']);assert not r['P']&1,(owner,bank,i,r)
    assert bytes(m[3:11])==scratch and m.rawtags==maps and before==[bytes(r)for r in m.ram]and m.ppu_reads==reads and len(m.ram_writes)==writes
    m.ram[bank][0x1fe0+i]^=1;poison+=1
  assert C.call(m,lab['CoCheckCode'])['P']&1
 results['all_two_owner_header_poison_cases']=poison
 negatives=0
 for owner in[37,39]:
  for fields in[dict(SelectedCharacter=0),dict(OperMode=0),dict(FamilyMainCommit=0),dict(DisableScreenFlag=0),dict(Mirror_PPUMASK=24),dict(NmiDisable=0)]:
   m=C.ready(b);N.put(m,SelectedCharacter=owner,**{k:v for k,v in fields.items()if k!='SelectedCharacter'})
   if 'SelectedCharacter'in fields:N.put(m,SelectedCharacter=fields['SelectedCharacter'])
   before=[bytes(r)for r in m.ram];reads=m.ppu_reads;writes=len(m.ram_writes);r=C.call(m,lab['CoCold'])
   assert not r['P']&1 and before==[bytes(r)for r in m.ram]and reads==m.ppu_reads and writes==len(m.ram_writes)
   negatives+=1
 results['cold_negative_gates']=negatives
 # Start with a genuine original bubble capture in an isolated legal native
 # Goomba fixture; copy only that private source state and native enemy fields
 # into the new current3 bus. No direct source flags manufacture a trap.
 h=B.Host(0);h.terrain(lambda x,y:0x54 if y>=208 else 0)
 names=['Enemy_Flag','Enemy_ID','Enemy_State','Enemy_PageLoc','Enemy_X_Position','Enemy_Y_Position','Enemy_Y_HighPos','Enemy_X_Speed','Enemy_Y_Speed','Enemy_MovingDir','EnemyIntervalTimer']
 for n,v in [('Enemy_Flag',1),('Enemy_ID',6),('Enemy_State',0),('Enemy_PageLoc',0),('Enemy_X_Position',100),('Enemy_Y_Position',184),('Enemy_Y_HighPos',1),('Enemy_X_Speed',8),('Enemy_Y_Speed',0),('Enemy_MovingDir',1)]:h.m[h.at(n)]=v
 for f in range(30):
  h.step(64 if f==0 else 0,epoch=f)
  if h.tokens[0]:break
 assert h.tokens[0];saved=h.tokens[0]['saved'];retired=[]
 for case,foreign in enumerate([0,32,36,37,38,39]*4):
  m=C.ready(b);m.ram[2][:]=h.s;m.ram[3][:]=image
  for n in names:
   for i in range(6):m[address(b,n)+i]=h.get(n,i)
  for bank in[2,3]:m.ram[bank][0x1fe0:0x1ff0]=cookie
  N.put(m,SelectedCharacter=foreign);before_score=bytes(m[0x7dd:0x7e3]);scratch=bytes(m[3:11]);maps=list(m.rawtags)
  flags=[0x30,0x31,0x71,0xf1][case//6]
  r=C.call(m,lab['CoRetire'],flags=flags);assert bytes(m[3:11])==scratch and m.rawtags==maps
  assert(r['A'],r['X'],r['Y'],r['P']&0x7d)==(83,71,109,flags&0x7d)
  assert all(m[address(b,n)]==v for n,v in saved.items())and m.ram[2][0x320]==0 and m.ram[2][0x304]==0,(foreign,saved)
  assert m.ram[2][0x1fe0]==0 and m.ram[3][0x1fe0]==0 and bytes(m[0x7dd:0x7e3])==before_score
  retired.append(dict(selected_raw=foreign,input_P=flags,result=r,native_AI_restored=True,no_credit=True))
 results['genuine_source_trap_foreign_retirement']=retired
 # A real cold transition from a trapped BB actor to Ex must unwind native AI
 # before clearing source RAM, rather than merely revoking a header.
 m=C.ready(b);m.ram[2][:]=h.s;m.ram[3][:]=image
 for n in names:
  for i in range(6):m[address(b,n)+i]=h.get(n,i)
 for bank in[2,3]:m.ram[bank][0x1fe0:0x1ff0]=cookie
 N.put(m,SelectedCharacter=37);r=C.call(m,lab['CoCold'])
 assert r['P']&1 and all(m[address(b,n)]==v for n,v in saved.items())and m.ram[2][0x1fe1]==37 and m.ram[3][0x1fe1]==37
 results['genuine_trap_to_Ex_cold_transition']=dict(result=r,native_AI_restored_before_source_overwrite=True)
 # Invalid or foreign headers must prevent the source retirement call. Keep
 # a live token and native AI unchanged when either BB header is incomplete.
 for bank in[2,3]:
  m=C.ready(b);m.ram[2][:]=h.s;m.ram[3][:]=image
  for n in names:
   for i in range(6):m[address(b,n)+i]=h.get(n,i)
  for k in[2,3]:m.ram[k][0x1fe0:0x1ff0]=cookie
  m.ram[bank][0x1fe7]^=1;before=[bytes(r)for r in m.ram];enemy=[[m[address(b,n)+i]for i in range(6)]for n in names]
  C.call(m,lab['CoRetire']);assert before==[bytes(r)for r in m.ram]and enemy==[[m[address(b,n)+i]for i in range(6)]for n in names]
 results['unauthenticated_retirement_rejections']=2
 q=dict(passed=True,proposal_only=True,ROM_written=False,shared_source_written=False,resident_granted=False,ROM_SHA256=P.PIN,checks=results,layout=layout,scope='Actual complete proposed cold/header/auth/retirement source in an in-memory exactcurrent3 CPU bus. Raw39 remains ungranted; carriers are synthetic fixture inputs only. No service routing, scene/menu/ingress, Prince packed loader or realnative execution is claimed.',bindings={p.relative_to(P.R).as_posix():P.sha(p.read_bytes())for p in[Path(__file__),P.R/'tools/reference/bubble_bobble_common_owner_1102_v5.inc',P.R/'tools/audit/prepare_bubble_bobble_common_owner_1102_v5.py',O/'common-owner.bin',O/'common-split.bin',O/'common-split-map.bin',O/'native-private.bin']})
 (O/'common-owner-CPU.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(passed=True,cold_cases=len(cases),header_poison_cases=poison,negative_gates=negatives,foreign_genuine_trap_unwinds=len(retired),ROM_written=False)))


if __name__=='__main__':main()
