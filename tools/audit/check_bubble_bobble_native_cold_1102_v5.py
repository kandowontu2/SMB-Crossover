"""Final successor payload: complete nine-row cold/auth/retire and vector ABI."""
import json
from pathlib import Path
import check_bubble_bobble_native_proxy_1102_v5 as Q
P=Q.P;C=Q.C;N=Q.N;R=Q.R;O=Q.O;address=Q.address


def main():
 b,q,route=Q.bundle();lab=q['owner_labels'];cookie=bytes.fromhex(q['BB_cookie']);image=(O/'native-proxy.bin').read_bytes();art=(O/'native-proxy-helper.chr').read_bytes();checks={};cold=[]
 assert cookie==bytes([0xa7,39,1])+bytes.fromhex(P.sha(image+art))[:13]
 for owner in[37,39]:
  for label,fault in[('cold',None),('code-readback',(3,2048)),('helper-readback',(2,0x1320)),('WRAM-protected','locked'),('disabled-NMI',None)]:
   if owner==37 and label=='helper-readback':continue
   m=C.ready(b);N.put(m,SelectedCharacter=owner)
   if fault=='locked':m.protection=[0,0]
   elif fault:m.corrupt_at=fault
   scratch=bytes(m[3:11]);maps=list(m.rawtags);z=C.call(m,lab['CoCold'],nmi=label=='disabled-NMI')
   assert bytes(m[3:11])==scratch and maps==m.rawtags and(z['A'],z['X'],z['Y'])==(83,71,109)and m.ppuctrl==160 and m.toggle==0,(owner,label,z)
   if fault:assert not z['P']&1 and m.ram[2][0x1fe0]!=0xa7,(owner,label,z)
   else:
    assert z['P']&1 and m.ram_writes[-1]==(2,0x1fe0,0xa7)
    if owner==39:
     expected=bytearray(image);expected[0x1fe0:0x1ff0]=cookie
     assert m.ram[3]==expected and m.ram[2][:1024]==bytes(1024)and bytes(m.ram[2][4096:5120])==art and m.ppu_reads==18450
     assert bytes(m.ram[2][1024:4096])==bytes([0xa5])*3072 and bytes(m.ram[2][5120:0x1fe0])==bytes([0xa5])*(0x1fe0-5120)
     assert m.ram[2][0x1fd0:0x1fd3]==bytes([0xa5])*3
    writes=len(m.ram_writes);reads=m.ppu_reads;w=C.call(m,lab['CoCold']);assert w['P']&1 and len(m.ram_writes)==writes and m.ppu_reads==reads
   cold.append(dict(owner=owner,case=label,result=z))
 checks['actual_two_owner_cold_warm_readback_protection_NMI']=cold
 poison=0;negative=0
 for owner in[37,39]:
  m=C.ready(b);N.put(m,SelectedCharacter=owner);assert C.call(m,lab['CoCold'])['P']&1
  for bank in[2,3]:
   for i in range(16):
    n=N.fork(m);n.ram[bank][0x1fe0+i]^=1;before=[bytes(x)for x in n.ram];reads=n.ppu_reads;writes=len(n.ram_writes)
    assert not C.call(n,lab['CoCheckCode'])['P']&1 and before==[bytes(x)for x in n.ram]and reads==n.ppu_reads and writes==len(n.ram_writes);poison+=1
  for fields in[dict(SelectedCharacter=0),dict(OperMode=0),dict(FamilyMainCommit=0),dict(DisableScreenFlag=0),dict(Mirror_PPUMASK=24),dict(NmiDisable=0)]:
   n=C.ready(b);N.put(n,SelectedCharacter=owner);N.put(n,**fields);before=[bytes(x)for x in n.ram];reads=n.ppu_reads;writes=len(n.ram_writes)
   assert not C.call(n,lab['CoCold'])['P']&1 and before==[bytes(x)for x in n.ram]and reads==n.ppu_reads and writes==len(n.ram_writes);negative+=1
 checks['both_owners_both_headers_all16bytes_reject']=poison;checks['actual_cold_admission_negative_gates']=negative
 # Public versus direct vector execution, including dedicated37, uses actual
 # service implementations. Row19 remains its separate genuine ROM reset.
 vectors=0
 for identity in[0,1]:
  seed=Q.fresh(b,route,identity)
  for row in range(38):
   if row==19:continue
   a=N.fork(seed);d=N.fork(seed)
   for m in[a,d]:m.raw_page(2,2);m[address(b,'CurrentBankC')]=2
   az=C.call(a,0xa000+row*3,bank=3);dz=C.call(d,0xb029 if row==37 else 0xb08c+row*3)
   assert[az[k]for k in['A','X','Y','P']]==[dz[k]for k in['A','X','Y','P']]and a.ram==d.ram and bytes(a[3:11])==bytes(d[3:11])and a.rawtags==d.rawtags,(identity,row,az,dz)
   vectors+=1
 checks['actual_all38_rows_direct_resident_vector_differentials_except_ROM19']=vectors
 # Authentic live trap is unwound before another owner overwrites its RAM.
 m,frame,saved=Q.trap(b,route);N.put(m,SelectedCharacter=37,DisableScreenFlag=1,Mirror_PPUMASK=0,NmiDisable=255)
 z=C.call(m,lab['CoCold']);assert z['P']&1 and all(N.get(m,n)==v for n,v in saved.items())and m.ram[2][0x1fe1]==m.ram[3][0x1fe1]==37,(z,saved,Q.fields(m,0))
 checks['actual_source_trap_to_Ex_cold_restores_flag_AI_before_overwrite']=True
 # Either incomplete header blocks source retirement altogether.
 rejects=0
 for bank in[2,3]:
  m,frame,saved=Q.trap(b,route);m.ram[bank][0x1fe7]^=1;before=[bytes(x)for x in m.ram];enemy=Q.fields(m,0);C.call(m,lab['CoRetire'])
  assert before==[bytes(x)for x in m.ram]and enemy==Q.fields(m,0);rejects+=1
 checks['unauthenticated_source_retirement_no_native_writes']=rejects
 out=dict(passed=True,ROM_written=False,admitted=False,base_ROM_SHA256=P.PIN,cookie=cookie.hex(),checks=checks,scope='Final compiled payload executes in memory-only current CPU bus: all9copy/verify rows including immutable441helper, finalcommit header, warm and negative guards, source trap retirement and all38typed service vectors. No native emulator/controller/stage-clear/install claim.',bindings={p.relative_to(R).as_posix():P.sha(p.read_bytes())for p in[Path(__file__),R/'tools/audit/prepare_bubble_bobble_native_proxy_1102_v5.py',O/'native-proxy.bin',O/'native-proxy-helper.chr',O/'native-proxy-owner.bin',O/'native-proxy-routes.bin']})
 (O/'native-proxy-cold-CPU.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(passed=True,cold_cases=len(cold),header_poisons=poison,negative_gates=negative,vectors=vectors,actual_trap_to_Ex=True)))


if __name__=='__main__':main()
