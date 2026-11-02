"""Execute the loader from its actual PRG bank, never synthetic RAM code."""
import json,re
import prepare_shinobi_cartridge_1101_v2 as P
import check_hogan_current_bounded_v1 as M
from link_pit_rygar_sophia_audit_cpu import scoped_load

def main():
 b=scoped_load(P.O/'candidate.nes');b['segs']['shinobi_rom']={'start':str(0xa800),'ooffs':str(16+65*8192+0x800)}
 for n,a in P.S.labels(P.O/'resident.lbl').items():
  if n.startswith('Sh') and 0xa800<=a<0xae00:b['syms'][n]={'val':str(a),'seg':'shinobi_rom'}
 m=M.fresh(b)
 M.put(m,SelectedCharacter=36,OperMode=1,FamilyMainCommit=1,DisableScreenFlag=1,Mirror_PPUMASK=0,NmiDisable=255,Mirror_PPUCTRL=160,ReloadCHRBank=1)
 m.ppuctrl=160
 foreign=[bytes(x) for x in m.ram[:2]]
 before=m.ppu_reads;cold=M.invoke(m,'ShLoad');reads=m.ppu_reads-before
 assert cold['P']&1 and reads==18450,(cold,reads)
 assert bytes(m.ram[3][:7168])==(P.S.O/'kernel.bin').read_bytes()[:7168]
 assert bytes(m.ram[2][0x1000:0x1800])==(P.S.O/'metadata.bin').read_bytes()[:2048]
 cookie=(P.O/'shinobi-cookie.bin').read_bytes()
 for bank in [2,3]:assert bytes(m.ram[bank][0x1fe0:0x1ff0])==cookie
 assert foreign==[bytes(x) for x in m.ram[:2]]
 warm=M.invoke(m,'ShLoad');assert warm['P']&1 and m.ppu_reads-before==reads
 rejects=0
 for bank in [2,3]:
  for i in range(16):
   n=M.fork(m);n.ram[bank][0x1fe0+i]^=1
   z=M.invoke(n,'ShCheckCode');assert not z['P']&1;rejects+=1
 good=M.invoke(m,'ShCheckCode');assert good['P']&1
 retire=M.invoke(m,'ShRetire')
 assert m.ram[2][0x1fe0]==m.ram[3][0x1fe0]==0
 assert foreign==[bytes(x) for x in m.ram[:2]]
 q=dict(passed=True,ROM_sha256=P.S.sha(P.O/'candidate.nes'),actual_PRG_bank=65,cold=cold,warm=warm,buffered_PPU_reads=reads,complete_header_corruptions_rejected=rejects,foreign_RAM0_1_unchanged=True,retired_both_headers=True,scope='Actual linked cartridge ShLoad/ShCheckCode/ShRetire through native FarCallCommon, forcedblank fixture. No synthetic4000 code or PC overrides. Menu/main/native-emulator admission not yet wired.')
 (P.O/'loader-CPU.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))
if __name__=='__main__':main()
