"""Current three-owner full shared cold, headers and cross-owner retirement."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools/reference')]
import prepare_prince_current_post_return_1102_v97 as M
import check_prince_successor_services_1102_v27 as I
import check_prince_post_return_cold_1102_v90 as C
N,O=I.N,M.O;address=I.address


def image():
 q=json.loads((O/'post-return-manifest-v97.json').read_text());M.validate(q);base,_=M.parent();assert M.sha(base['raw'])==q['parent_memory_SHA256'];raw=bytearray(base['raw'])
 for row in q['patches']:
  at=row['file_offset'];before=bytes.fromhex(row['old_hex']);after=bytes.fromhex(row['new_hex']);assert raw[at:at+len(before)]==before;raw[at:at+len(after)]=after
 assert M.sha(raw)==q['expected_memory_only_SHA256'];return dict(base,raw=bytes(raw)),q


def fields(m,owner):
 m.raw_page(2,2);N.put(m,CurrentBankC=2,SelectedCharacter=owner,OperMode=1,OperMode_Task=3,GameEngineSubroutine=8,GamePauseStatus=0,FrameCounter=0,Player_X_Position=48,Player_PageLoc=0,Player_Y_Position=176,Player_Y_HighPos=1,NmiDisable=255,DisableScreenFlag=1,Mirror_PPUMASK=0,Mirror_PPUCTRL=160,FamilyMainCommit=1,ReloadCHRBank=0,NumberofLives=2)
 m.ppuctrl=160;m[0x2001]=0


def clear(m):
 for name in ['writes','ram_writes','ppu_log','blocked']:setattr(m,name,[])


def cold(base,owner):
 N.Bus=C.C.V.ControllerBus;m=N.fresh(base)
 for bank in [2,3]:m.ram[bank][:]=bytes([0x9d])*8192;m.ram[bank][0x1fe0:0x1ff0]=bytes(16)
 fields(m,owner);out=I.invoke(m,193,0xae00,(83,71,109,0x21));assert out['regs'][3]&1,('Full shared cold failed',owner,out['regs'])
 assert bytes(m.ram[2][0x1fe0:0x1ff0])==bytes(m.ram[3][0x1fe0:0x1ff0])and m.ram[2][0x1fe0]==0xa7
 assert out['regs'][:3]==[83,71,109]and out['regs'][4]==224
 clear(m);return m,out


def main():
 base,manifest=image();seeds={};rows=[];lab=M.A.L.P.T.labels(O/'post-owner-v97.lbl');cookies={37:'CoExCookie',38:'PrCookie',39:'CoBBCookie'}
 for owner in [37,38,39]:
  print('Actual complete current cold owner',owner,flush=True);m,out=cold(base,owner);seeds[owner]=N.fork(m);at=16+65*8192+lab[cookies[owner]]-0xa000;cookie=base['raw'][at:at+16]
  assert bytes(m.ram[2][0x1fe0:0x1ff0])==bytes(m.ram[3][0x1fe0:0x1ff0])==cookie
  if owner==38:
   h=C.host(base);assert bytes(m.ram[2][:0x800])==bytes(h.s[:0x800]),[(hex(i),a,z)for i,(a,z)in enumerate(zip(m.ram[2][:0x800],h.s[:0x800]))if a!=z][:12]
   assert bytes(m.ram[2][0x766:0x800])==(O/'native-state-v78.bin').read_bytes()[-154:]
  rows.append(dict(owner=owner,CPU=out['CPU'],minimum_SP=out['minSP'],cookie=cookie.hex(),both_complete_headers=True))
 # Every actual predecessor owner retires before the next full load. Foreign
 # selection still retires a valid old overlay; it never enters unowned code.
 transitions=[]
 for old in [37,38,39]:
  for new in [37,38,39]:
   m=N.fork(seeds[old]);fields(m,new);out=I.invoke(m,193,0xae00,(83,71,109,0x21));assert out['regs'][3]&1,(old,new,out['regs'])
   assert bytes(m.ram[2][0x1fe0:0x1ff0])==bytes(seeds[new].ram[2][0x1fe0:0x1ff0])and bytes(m.ram[3][0x1fe0:0x1ff0])==bytes(seeds[new].ram[3][0x1fe0:0x1ff0])
   transitions.append(dict(old=old,new=new,CPU=out['CPU'],minimum_SP=out['minSP']))
  m=N.fork(seeds[old]);N.put(m,SelectedCharacter=0);out=I.invoke(m,193,0xae0b,(83,71,109,0x21));assert out['regs'][3]&1 and m.ram[2][0x1fe0]==m.ram[3][0x1fe0]==0
  if old==38:assert m.ram[2][0xab]==m.ram[2][0xaa]==0
  assert out['regs'][:3]==[83,71,109]
 rejected=0
 for owner in [37,38,39]:
  for bank in [2,3]:
   for index in range(16):
    m=N.fork(seeds[owner]);m.ram[bank][0x1fe0+index]^=1;before=[bytes(z)for z in m.ram];out=I.invoke(m,193,0xb08c,(83,71,109,0x21));assert not out['regs'][3]&1 and before==[bytes(z)for z in m.ram]and out['regs'][:3]==[83,71,109],(owner,bank,index,out['regs']);rejected+=1
 q=dict(passed=True,CPU_only=True,ROM_written=False,qualified_current_shared_cold=True,native_emulator=False,parent_memory_SHA256=manifest['parent_memory_SHA256'],memory_only_SHA256=manifest['expected_memory_only_SHA256'],cold=rows,all_ordered_owner_transitions=transitions,foreign_selected_retirement_cases=3,bad_header_bytes_rejected_without_private_write=rejected,Prince_complete_constructor_and_audio_code_exact=True,Ex37_original_carry_negative_corrected=True,scope='Actual complete531B manager, existing resident worker and Prince typed decoder/current payload/header publication execute on exact Bub66+Prince97 memory image. All three owners and nine ordered retirement/cold transitions; foreign-selected retirement; every header byte rejects actual public movement before private writes. No ROM/menu/install/native emulator claim. Trapped-native-AI populated retirement, current hot/death/respawn/ISR/native mechanics remain separate.',bindings={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),Path(M.__file__),O/'post-return-manifest-v97.json',O/'post-owner-v97.s',O/'post-owner-extra-v97.bin',O/'post-selector-v97.bin',O/'post-return-cold-CPU-v90.json']})
 (O/'current-shared-cold-CPU-v98.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','all_ordered_owner_transitions']}))


if __name__=='__main__':
 try:main()
 except Exception as error:
  (O/'current-shared-cold-negative-v98.json').write_text(json.dumps(dict(passed=False,CPU_only=True,exception=repr(error)),indent=2)+'\n');raise
