"""Add and exercise authenticated Shinobi CHR request in actual resident ROM."""
import json,subprocess
import prepare_shinobi_owning_graft_1101_v1 as S
import check_hogan_current_bounded_v1 as M
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address

R=S.R;BASE=R/'build/shinobi-hurt-layout-1101-v5';O=R/'build/shinobi-chr-1101-v6'


def main():
 O.mkdir(exist_ok=True)
 assert S.sha(BASE/'candidate.nes')=='f6658fb7532dc87b1583da8f388fd8e3f1094b2bbd71ea51a5c611bb37364db9'
 b=scoped_load(BASE/'candidate.nes');raw=bytearray(b['raw'])
 src=(BASE/'resident.s').read_text()
 for n in ['CurrentCHRBank','X5ChrMode','SsChrActive','X5WideChrActive']:
  src+=f'{n}=${address(b,n):04x}\n'
 src+='.include "shinobi_chr_1101_v6.inc"\n'
 (O/'resident.s').write_text(src)
 (O/'resident.cfg').write_bytes((BASE/'resident.cfg').read_bytes())
 (O/'shinobi-cookie.bin').write_bytes((BASE/'shinobi-cookie.bin').read_bytes())
 cc=R/'tools/Windows/cc65/bin'
 for cmd in [[cc/'ca65.exe','-g','-I',R/'tools/reference','--bin-include-dir',O,O/'resident.s','-o',O/'resident.o'],[cc/'ld65.exe','-C',O/'resident.cfg',O/'resident.o','-o',O/'resident.bin','-Ln',O/'resident.lbl']]:
  subprocess.run(list(map(str,cmd)),check=True)
 resident=(O/'resident.bin').read_bytes();at=16+65*8192+0x800
 old=(BASE/'resident.bin').read_bytes()
 assert raw[at:at+1536]==old+bytes([255])*(1536-len(old))
 assert resident[:len(old)]==old and len(resident)<=1536
 raw[at:at+len(resident)]=resident
 (O/'candidate.nes').write_bytes(raw)
 for suffix in ['.lbl','.dbg']:(O/('candidate'+suffix)).write_bytes((BASE/('candidate'+suffix)).read_bytes())
 b=scoped_load(O/'candidate.nes')
 b['segs']['shinobi_rom']={'start':str(0xa800),'ooffs':str(at)}
 for n,a in S.labels(O/'resident.lbl').items():
  if n.startswith('Sh') and 0xa800<=a<0xae00:b['syms'][n]={'val':str(a),'seg':'shinobi_rom'}
 seed=M.fresh(b)
 M.put(seed,SelectedCharacter=36,OperMode=1,FamilyMainCommit=1,DisableScreenFlag=1,Mirror_PPUMASK=0,NmiDisable=255,Mirror_PPUCTRL=160,ReloadCHRBank=1)
 assert M.invoke(seed,'ShLoad')['P']&1
 accepted=0
 for flags in [0x30,0x31,0x70,0xf1]:
  for special in [0,1,255]:
   m=M.fork(seed)
   M.put(m,SsChrActive=special,X5WideChrActive=1,InvHudActive=0)
   for i in range(12):
    m[address(b,'CurrentCHRBank')+i]=17+i
    m[address(b,'X5ChrMode')+i]=0
   # Establish and remember all unrelated native hardware windows.
   M.invoke(m,'X5PublishChr');before=list(m.chr_latches)
   # Compare against the same native FarCallCommon transport; its return
   # restores A using LDA, so caller N/Z are not an invariant of this ABI.
   reference=M.invoke(M.fork(m),'ShCheckCode',p=flags)
   z=M.invoke(m,'ShChr',p=flags)
   assert [z[k] for k in ['A','X','Y','P']]==[reference[k] for k in ['A','X','Y','P']],(flags,z,reference)
   assert z['P']&1
   assert M.get(m,'ReloadCHRBank')==1 and M.get(m,'SsChrActive')==0
   M.invoke(m,'X5PublishChr')
   assert m.chr_latches[4:8]==[503,504,505,517],m.chr_latches
   assert m.chr_latches[:4]==before[:4] and m.chr_latches[8:]==before[8:]
   accepted+=1
 rejected=0
 fields=['CurrentCHRBank','X5ChrMode','SsChrActive','X5WideChrActive','ReloadCHRBank']
 def snapshot(m):return {n:[M.get(m,n,i) for i in range(12 if n in fields[:2] else 1)] for n in fields}
 for bank in [2,3]:
  for i in range(16):
   m=M.fork(seed);m.ram[bank][0x1fe0+i]^=1;before=snapshot(m)
   assert not M.invoke(m,'ShChr')['P']&1
   assert snapshot(m)==before;rejected+=1
 for char in [0,1,10,35,37,255]:
  m=M.fork(seed);M.put(m,SelectedCharacter=char);before=snapshot(m)
  assert not M.invoke(m,'ShChr')['P']&1 and snapshot(m)==before;rejected+=1
 q=dict(passed=True,ROM_sha256=S.sha(O/'candidate.nes'),resident_bytes=len(resident),accepted=accepted,rejected=rejected,
        physical_sprite_windows=[503,504,505,517],unrelated_windows_unchanged=True,installed=False,menu_unlocked=False,
        scope='Actual resident ShChr and native X5PublishChr instructions; hardware register latches modeled. Scene/main ingress and emulator display not yet tested.')
 (O/'result.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))


if __name__=='__main__':main()
