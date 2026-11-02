"""Wire source death pose/timer into native death and one-life handoff."""
import hashlib,json,subprocess
import prepare_shinobi_owning_graft_1101_v1 as S
import check_hogan_current_bounded_v1 as M
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
R=S.R;BASE=R/'build/shinobi-damage-1101-v10';O=R/'build/shinobi-death-1101-v11'


def main():
 O.mkdir(exist_ok=True);assert S.sha(BASE/'candidate.nes')=='6d43da1f12248a1763ad3d8c68353611f72342e3b32a9294f7ff30b14b61014a'
 b=scoped_load(BASE/'candidate.nes');raw=bytearray(b['raw'])
 klab=S.labels(R/'build/shinobi-hurt-layout-1101-v5/component.lbl')
 names=['R0','FrameCounter','GamePauseStatus','GameEngineSubroutine']
 text=''.join(f'{n}=${address(b,n):04x}\n' for n in names)
 text+=f'ShAnimatorInit=${klab["Sh_83AB"]:04x}\nShAnimatorTick=${klab["Sh_836F"]:04x}\n'
 text+=(R/'tools/reference/shinobi_death_1101_v11.s').read_text()
 (O/'death.s').write_text(text)
 (O/'death.cfg').write_text('MEMORY { D:start=$d608,size=$98,file=%O; } SEGMENTS { DEATH:load=D,type=ro; }')
 cc=R/'tools/Windows/cc65/bin'
 def compile(args):subprocess.run(list(map(str,args)),check=True)
 compile([cc/'ca65.exe',O/'death.s','-o',O/'death.o'])
 compile([cc/'ld65.exe','-C',O/'death.cfg',O/'death.o','-o',O/'death.bin','-Ln',O/'death.lbl'])
 labels=S.labels(O/'death.lbl');code=(O/'death.bin').read_bytes()
 assert len(code)<=152
 at=16+1048576+517*1024+0x208
 assert raw[at:at+152]==bytes(152)
 raw[at:at+len(code)]=code
 # Five-byte status leaf occupies the verified final8 bytes of kernel grant.
 at=16+1048576+515*1024+0x3f8
 assert raw[at:at+8]==bytes(8)
 raw[at:at+5]=bytes.fromhex('a9013860ea')
 for row,target in [(6,0xbbf8),(7,labels['ShDeathStart']),(8,labels['ShDeathTick'])]:
  at=16+1048576+506*1024+row*3
  assert raw[at]==76
  raw[at:at+3]=bytes([76,target&255,target>>8])
 def page(p):return raw[16+1048576+p*1024:16+1048576+(p+1)*1024]
 payload=b''.join(page(p) for p in [506,507,508,509,510,513,515,516,517,503,504,505,517])
 (O/'shinobi-cookie.bin').write_bytes(bytes([167,36,1])+hashlib.sha256(payload).digest()[:13])
 damage=(R/'tools/reference/shinobi_damage_1101_v10.inc').read_text()
 needle=' sta $c038\n jmp ShInjuryHandled'
 assert damage.count(needle)==1
 damage=damage.replace(needle,' sta $c038\n ShRomFar ShDeathVeneer,193\n jmp ShInjuryHandled')
 damage+='\nShDeathVeneer=ShServiceVeneers+21\n'
 (O/'shinobi_damage_1101_v10.inc').write_text(damage)
 (O/'resident.s').write_bytes((BASE/'resident.s').read_bytes());(O/'resident.cfg').write_bytes((BASE/'resident.cfg').read_bytes())
 compile([cc/'ca65.exe','-g','-I',O,'-I',R/'tools/reference','--bin-include-dir',O,O/'resident.s','-o',O/'resident.o'])
 compile([cc/'ld65.exe','-C',O/'resident.cfg',O/'resident.o','-o',O/'resident.bin','-Ln',O/'resident.lbl'])
 lab=S.labels(O/'resident.lbl');resident=bytearray((O/'resident.bin').read_bytes());assert len(resident)<=1536
 for row,target in [(1,'ShChr'),(5,'ShInjury')]:
  at=lab['ShServiceVeneers']-0xa800+row*3;t=lab[target];resident[at:at+3]=bytes([76,t&255,t>>8])
 start=16+65*8192+0x800;raw[start:start+len(resident)]=resident
 (O/'resident.bin').write_bytes(resident);(O/'candidate.nes').write_bytes(raw)
 for suffix in ['.lbl','.dbg']:(O/('candidate'+suffix)).write_bytes((BASE/('candidate'+suffix)).read_bytes())
 b=scoped_load(O/'candidate.nes');b['segs']['shinobi_rom']={'start':str(0xa800),'ooffs':str(start)}
 for n,a in lab.items():
  if n.startswith('Sh') and 0xa800<=a<0xae00:b['syms'][n]={'val':str(a),'seg':'shinobi_rom'}
 m=M.fresh(b);M.put(m,SelectedCharacter=36,OperMode=1,FamilyMainCommit=1,DisableScreenFlag=1,Mirror_PPUMASK=0,NmiDisable=255,Mirror_PPUCTRL=160,NumberofLives=2)
 M.invoke(m,'ShScene');m.ram[2][0x539]=0
 assert M.invoke(m,'HuInjuryStatus')['A']==1
 M.put(m,FrameCounter=10,GameEngineSubroutine=8,GamePauseStatus=0)
 M.invoke(m,'HuInjury')
 assert m.ram[2][0x300]==7 and m.ram[2][0x408]==200 and M.get(m,'GameEngineSubroutine')==11
 for tick in range(1,201):
  M.put(m,FrameCounter=(10+tick)&255);M.invoke(m,'HuDeath')
  assert M.get(m,'GameEngineSubroutine')==(6 if tick==200 else 11)
  assert m.ram[2][0x408]==200-tick
  before=bytes(m.ram[2][:0x811]);M.invoke(m,'HuDeath');assert bytes(m.ram[2][:0x811])==before
  M.put(m,FrameCounter=(11+tick)&255,GamePauseStatus=1);M.invoke(m,'HuDeath');assert bytes(m.ram[2][:0x811])==before
  M.put(m,GamePauseStatus=0)
 assert M.get(m,'NumberofLives')==2
 M.invoke(m,'GameRoutines');assert M.get(m,'NumberofLives')==1
 M.put(m,OperMode=1,FamilyMainCommit=1,DisableScreenFlag=1,Mirror_PPUMASK=0,NmiDisable=255)
 M.invoke(m,'ShScene');assert m.ram[2][0x800]==167 and m.ram[2][0x539]==6 and m.ram[2][0x38]==0
 q=dict(passed=True,ROM_sha256=S.sha(O/'candidate.nes'),death_bytes=len(code),resident_bytes=len(resident),updates=200,duplicate_checks=200,pause_checks=200,one_native_life_loss=True,new_life_source_reset=True,installed=False,menu_unlocked=False,
        scope='Actual HuInjuryStatus/HuInjury/HuDeath and GameRoutines; native life loss and scene constructor verified in CPU fixture. Native emulator visuals/audio/contact and full1-1 remain pending.')
 (O/'result.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))


if __name__=='__main__':main()
