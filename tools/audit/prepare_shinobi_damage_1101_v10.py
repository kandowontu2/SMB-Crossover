"""Connect native injury to original Shinobi health and knockback initializer."""
import hashlib,json,subprocess
import prepare_shinobi_owning_graft_1101_v1 as S
import check_hogan_current_bounded_v1 as M
from link_pit_rygar_sophia_audit_cpu import scoped_load
R=S.R;BASE=R/'build/shinobi-route-1101-v8';RES=R/'build/shinobi-scene-1101-v7';O=R/'build/shinobi-damage-1101-v10'


def main():
 O.mkdir(exist_ok=True);assert S.sha(BASE/'candidate.nes')=='12db8aa78ac0fb5de9591fdf34a82a1b0c13a94106cf3b430660c1091072deb7'
 raw=bytearray((BASE/'candidate.nes').read_bytes());prior=S.labels(RES/'resident.lbl')
 klab=S.labels(R/'build/shinobi-hurt-layout-1101-v5/component.lbl')
 at=16+1048576+506*1024+108
 assert raw[at]==76
 raw[at:at+3]=bytes([76,klab['Sh_DA1B']&255,klab['Sh_DA1B']>>8])
 def page(n):return raw[16+1048576+n*1024:16+1048576+(n+1)*1024]
 kernel=b''.join(page(p) for p in [506,507,508,509,510,513,515])
 meta=page(516)+page(517);art=page(503)+page(504)+page(505)+page(517)
 (O/'shinobi-cookie.bin').write_bytes(bytes([167,36,1])+hashlib.sha256(kernel+meta+art).digest()[:13])
 src=(RES/'resident.s').read_text()+'.include "shinobi_damage_1101_v10.inc"\n'
 (O/'resident.s').write_text(src);(O/'resident.cfg').write_bytes((RES/'resident.cfg').read_bytes())
 cc=R/'tools/Windows/cc65/bin'
 for cmd in [[cc/'ca65.exe','-g','-I',R/'tools/reference','--bin-include-dir',O,O/'resident.s','-o',O/'resident.o'],[cc/'ld65.exe','-C',O/'resident.cfg',O/'resident.o','-o',O/'resident.bin','-Ln',O/'resident.lbl']]:subprocess.run(list(map(str,cmd)),check=True)
 labels=S.labels(O/'resident.lbl');resident=bytearray((O/'resident.bin').read_bytes());assert len(resident)<=1536
 for row,target in [(1,'ShChr'),(5,'ShInjury')]:
  i=labels['ShServiceVeneers']-0xa800+row*3;t=labels[target]
  resident[i:i+3]=bytes([76,t&255,t>>8])
 # v8 CHR veneer edit must survive resident rebuild. Only append, new cookie
 # and injury/CHR veneers may differ from the previous resident.
 start=16+65*8192+0x800;old=raw[start:start+1145]
 allowed=set(range(prior['ShCookie']-0xa800,prior['ShCookie']-0xa800+16))
 allowed.update(range(prior['ShServiceVeneers']-0xa800+15,prior['ShServiceVeneers']-0xa800+18))
 assert all(a==b or i in allowed for i,(a,b) in enumerate(zip(old,resident)))
 raw[start:start+len(resident)]=resident;(O/'resident.bin').write_bytes(resident)
 (O/'candidate.nes').write_bytes(raw)
 for suffix in ['.lbl','.dbg']:(O/('candidate'+suffix)).write_bytes((BASE/('candidate'+suffix)).read_bytes())
 b=scoped_load(O/'candidate.nes');b['segs']['shinobi_rom']={'start':str(0xa800),'ooffs':str(start)}
 for n,a in labels.items():
  if n.startswith('Sh') and 0xa800<=a<0xae00:b['syms'][n]={'val':str(a),'seg':'shinobi_rom'}
 seed=M.fresh(b);M.put(seed,SelectedCharacter=36,OperMode=1,FamilyMainCommit=1,DisableScreenFlag=1,Mirror_PPUMASK=0,NmiDisable=255,Mirror_PPUCTRL=160)
 M.invoke(seed,'ShScene');cases=0
 for hp in range(7):
  for face in [0,4]:
   m=M.fork(seed);m.ram[2][0x539]=hp;m.ram[2][0x363]=face
   scratch=bytes(range(0xa0,0xa8));m[3:11]=scratch
   z=M.invoke(m,'HuInjury');assert z['P']&1 and bytes(m[3:11])==scratch
   assert m.ram[2][0x539]==max(0,hp-1)
   if hp:
    assert m.ram[2][0x413]==16 and m.ram[2][0x300]==6
    assert m.ram[2][0x3fd]&3==(1 if face else 2),(hp,face,m.ram[2][0x3fd])
    before=m.ram[2][0x539];M.invoke(m,'HuInjury');assert m.ram[2][0x539]==before
   else:assert m.ram[2][0x38]&2
   cases+=1
 for field,value in [(0x413,10),(0x413,16),(0x460,2),(0x54c,1),(0x54d,1),(0x38,2)]:
  m=M.fork(seed);m.ram[2][field]=value
  assert M.invoke(m,'HuInjury')['P']&1 and m.ram[2][0x539]==6;cases+=1
 rejected=0
 for bank in [2,3]:
  for i in range(16):
   m=M.fork(seed);m.ram[bank][0x1fe0+i]^=1;before=bytes(m.ram[2][:0x811])
   assert not M.invoke(m,'HuInjury')['P']&1
   assert bytes(m.ram[2][:0x811])==before;rejected+=1
 q=dict(passed=True,ROM_sha256=S.sha(O/'candidate.nes'),cases=cases,resident_bytes=len(resident),
        corrupt_headers_rejected=rejected,
        installed=False,menu_unlocked=False,scope='Actual HuInjury applies source health semantics and authentic DA1B knockback; immunity gates and R0..7 preserved. Death bit only: native death/life handoff, SFX, actual enemy contacts and full play remain pending.')
 (O/'result.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))


if __name__=='__main__':main()
