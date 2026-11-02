"""Enable Shinobi in private menu while retaining cold portrait/name selection."""
import json,subprocess
import prepare_shinobi_owning_graft_1101_v1 as S
import check_hogan_current_bounded_v1 as M
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
R=S.R;BASE=R/'build/shinobi-palette-1101-v12';O=R/'build/shinobi-menu-1101-v13'


def main():
 O.mkdir(exist_ok=True);assert S.sha(BASE/'candidate.nes')=='33bafb324e4e8e8e17be2ce5f8b80a8119a3e51b6c8ae35c414c26f3736df009'
 b=scoped_load(BASE/'candidate.nes');raw=bytearray(b['raw'])
 src=(BASE/'resident.s').read_text()+''.join(f'{n}=${address(b,n):04x}\n' for n in ['CrossoverMenuIndex','FmAlts'])
 src+='ShPriorResolve=$b38e\n.include "shinobi_menu_1101_v13.inc"\n'
 (O/'resident.s').write_text(src)
 for name in ['resident.cfg','shinobi-cookie.bin','shinobi_damage_1101_v10.inc']:(O/name).write_bytes((BASE/name).read_bytes())
 cc=R/'tools/Windows/cc65/bin'
 for cmd in [[cc/'ca65.exe','-g','-I',O,'-I',R/'tools/reference','--bin-include-dir',O,O/'resident.s','-o',O/'resident.o'],[cc/'ld65.exe','-C',O/'resident.cfg',O/'resident.o','-o',O/'resident.bin','-Ln',O/'resident.lbl']]:subprocess.run(list(map(str,cmd)),check=True)
 lab=S.labels(O/'resident.lbl');code=bytearray((O/'resident.bin').read_bytes());assert len(code)<=1536
 for row,target in [(1,'ShChr'),(5,'ShInjury'),(26,'ShColors')]:
  i=lab['ShServiceVeneers']-0xa800+row*3;t=lab[target];code[i:i+3]=bytes([76,t&255,t>>8])
 old=(BASE/'resident.bin').read_bytes();assert code[:len(old)]==old
 at=16+65*8192+0x800;raw[at:at+len(code)]=code;(O/'resident.bin').write_bytes(code)
 at=16+66*8192+0x1957+18
 before=bytes.fromhex('8d6a01a98e8d6c01a9b38d6d01a99d4c5a01');assert raw[at:at+18]==before
 call=bytearray(before);call[4]=lab['ShMenuResolve']&255;call[9]=lab['ShMenuResolve']>>8;call[14]=193
 raw[at:at+18]=call
 # Both callers consume only C: Resolve immediately replaces A on failure,
 # and CheckConfirm branches then loads its own status value. FmPending is
 # untouched for portrait/name dispatch. Unsigned (index-3)<2 accepts3/4.
 at=16+76*8192+0x1ff3;old=bytes.fromhex('2079b990074904d00118490460')
 assert raw[at:at+13]==old
 raw[at:at+13]=bytes.fromhex('2079b9900538e903c90260eaea')
 # This literal is twelve? Keep the exact13-byte source lease explicit.
 assert len(raw)==len(b['raw'])
 (O/'candidate.nes').write_bytes(raw)
 for suffix in ['.lbl','.dbg']:(O/('candidate'+suffix)).write_bytes((BASE/('candidate'+suffix)).read_bytes())
 b=scoped_load(O/'candidate.nes');m=M.fresh(b)
 M.put(m,CrossoverMenuIndex=10,FmAlts=4)
 M.invoke(m,'MenuResolveCharacter');assert M.get(m,'SelectedCharacter')==36
 M.invoke(m,'QueueSelection');M.invoke(m,'DrawSelectionPreview')
 assert M.invoke(m,'FmPending')['P']&1
 starts=0
 for button in [16,128]:
  n=M.fork(m);M.put(n,CrossoverMenuButtons=0,SavedJoypad1Bits=button,SavedJoypad2Bits=0,VRAM_Buffer1_Offset=0)
  M.invoke(n,'CrossoverMenuInput')
  assert M.get(n,'SelectedCharacter')==36 and M.get(n,'CrossoverMenuState')==0
  starts+=1
 # Retire both matching cached headers before the next selected owner resolves.
 cookie=(O/'shinobi-cookie.bin').read_bytes()
 for bank in [2,3]:m.ram[bank][0x1fe0:0x1ff0]=cookie
 M.put(m,CrossoverMenuIndex=0,FmAlts=0);M.invoke(m,'MenuResolveCharacter')
 assert m.ram[2][0x1fe0]==m.ram[3][0x1fe0]==0
 assert M.get(m,'SelectedCharacter')==0
 q=dict(passed=True,ROM_sha256=S.sha(O/'candidate.nes'),resident_bytes=len(code),Shinobi_Start_cases=starts,
        cold_portrait_pending_preserved=True,menu_exit_headers_retired=True,installed=False,native_emulator=False,
        scope='Private menu admission, cold preview and Start CPU tests. Current build needs actual controller-driven launch and runtime/table audit before delivery.')
 (O/'result.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))


if __name__=='__main__':main()
