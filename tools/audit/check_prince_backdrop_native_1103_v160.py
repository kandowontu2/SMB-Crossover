"""Current159 fullcold and actual native entrance/color/status consumers."""
from pathlib import Path
from collections import Counter
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_strike_cold_1103_v131 as C
import prepare_prince_backdrop_manifest_1103_v159 as M
import check_prince_strike_actual_1103_v134 as A
N,O,I=C.N,C.O,C.I


def loaded():
 base,q=M.image();m,out=C.cold(base,38)
 N.put(m,NmiDisable=1,DisableScreenFlag=0,TimerControl=0,AreaType=1,Player_Rel_XPos=48,Player_Rel_YPos=176,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,ScreenRight_X_Pos=255,ScreenRight_PageLoc=0,Mirror_PPUMASK=30)
 m[0x2001]=30
 return base,m,json.loads((O/'native-labels-v153.json').read_text())


def environment():
 A.C.loaded=loaded;A.C.image=M.image;return A.environment()


def first8():
 base,seed,lab=loaded();m=N.fork(seed)
 N.put(m,Player_Y_Position=0,Player_Y_HighPos=0,PlayerEntranceCtrl=2,AltEntranceControl=0,ScreenLeft_PageLoc=0,AreaType=1,GameTimerSetting=1,FetchNewGameTimerFlag=1)
 I.invoke(m,193,0xb08c+3*36);assert m.ram[2][0x84]+256*m.ram[2][0x85]==0xff20
 N.invoke(m,'Entrance_GameTimerSetupCore',a=83,x=0,y=0,p=0x21);assert N.get(m,'Player_Y_Position')==176 and N.get(m,'GameEngineSubroutine')==7
 N.invoke(m,'PlayerEntrance',a=83,x=0,y=0,p=0x21);assert N.get(m,'GameEngineSubroutine')==8
 N.put(m,OperMode_Task=3,NmiDisable=255,DisableScreenFlag=0,TimerControl=0,Mirror_PPUMASK=30,ScreenRight_X_Pos=255,ScreenRight_PageLoc=0);m[0x2001]=30;A.U.T.terrain(m,lambda x,y:0x54 if y>=208 else 0)
 return environment(),m,lab


def main():
 base,manifest=M.image();runtime,meta,state=M.B.images();lab=json.loads((O/'native-labels-v153.json').read_text());live=(O/'native-live-v149.bin').read_bytes();install=(O/'native-installer-v153.bin').read_bytes()
 seed,cold=C.cold(base,38);want=bytearray(runtime);want[0x1fa3:0x1fd8]=live
 assert bytes(seed.ram[3][:8159])==want and bytes(seed.ram[2][0x800:0x800+len(meta)])==meta
 audio=bytearray(state[1375:1529]);audio[:25]=install;assert bytes(seed.ram[2][0x766:0x800])==audio and bytes(seed.ram[2][0x200:0x235])==bytes(53)
 # The unchanged full manager restores each legitimate caller C mapping.
 m=N.fork(seed);C.fields(m,38);m.raw_page(2,201);N.put(m,CurrentBankC=201);out=I.invoke(m,193,0xae00,(83,71,109,0x21));assert out['regs'][3]&1 and m.rawtags[2]==201 and N.get(m,'CurrentBankC')==201
 # Inject one explicit CPU readback fault, never a native state outcome.
 actual=N.NesMPU;fault=[]
 class Fault(actual):
  def step(self):
   m=self.memory
   if not fault and m.rawtags[2]==2 and self.pc==0xc76e:
    m.ram[3][0x1fa3+self.y]^=1;fault.append([self.pc,self.y,self.sp])
   return super().step()
 m=N.fork(seed);m.ram[2][0x1fe0]=m.ram[3][0x1fe0]=0;C.fields(m,38);N.NesMPU=Fault
 try:failed=I.invoke(m,193,0xae00,(83,71,109,0x21))
 finally:N.NesMPU=actual
 assert fault and not failed['regs'][3]&1 and m.ram[2][0x1fe0]==m.ram[3][0x1fe0]==0
 retry=I.invoke(m,193,0xae00,(83,71,109,0x21));assert retry['regs'][3]&1 and bytes(m.ram[3][0x1fa3:0x1fd8])==live and bytes(m.ram[2][0x200:0x235])==bytes(53)
 points={}
 for name in ['GetPlayerColors','X5QueueAreaBackdrop','CrossoverPatchStatusName','WriteGameText']:
  points[I.address(base,name),((I.location(base,name)-16)//8192)|128]=name
 points[lab['PpNativeColors'],2]='PpNativeColors';points[lab['PpLiveName'],3]='PpLiveName';events=Counter()
 class Trace(actual):
  def step(self):
   tag=self.memory.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else None
   if(self.pc,tag)in points:events[points[self.pc,tag]]+=1
   return super().step()
 colors=names=0;N.NesMPU=Trace
 try:
  for area in range(4):
   for control in [0,1,2,3,4,5,6,7]:
    for offset in [0,0x48,0x4d,0x4e,0x6f,0x70]:
     m=N.fork(seed);N.put(m,AreaType=area,BackgroundColorCtrl=control,VRAM_Buffer1_Offset=offset);before=[bytes(z)for z in m.ram];smc=bytes(m[0x15a:0x17b]);scratch=bytes(m[3:11]);expected=N.fork(m)
     N.invoke(expected,'X5QueueAreaBackdrop',a=83,x=71,y=109,p=0x21)
     pos=N.get(expected,'VRAM_Buffer1_Offset');at=I.address(base,'VRAM_Buffer1')
     if pos<0x4e:
      for i,v in enumerate([0x3f,0x11,3,0x27,0x16,0x20]):expected[at+pos+i]=v
      N.put(expected,VRAM_Buffer1_Offset=pos+6);expected[at+pos+6]=0
     expected_packet=bytes(expected[at:at+0x90]);out=N.invoke(m,'GetPlayerColors',a=83,x=71,y=109,p=0x21)
     assert bytes(m[at:at+0x90])==expected_packet and N.get(m,'VRAM_Buffer1_Offset')==N.get(expected,'VRAM_Buffer1_Offset'),(area,control,offset)
     # The packet is a documented synchronous gateway scratch lease;
     # instruction-kind/slot and packet bytes are its only private writes.
     allowed=set(range(0x200,0x20d))|{lab['PpNativeCallSlot']+1-0xc000,lab['PpNativeCallKind']+1-0xc000}
     assert all(a==z or bank==2 and index in allowed for bank in range(4)for index,(a,z)in enumerate(zip(before[bank],m.ram[bank])))
     assert out['A']==83 and out['X']==71 and out['Y']==109 and out['P']&1 and bytes(m[3:11])==scratch and bytes(m[0x15a:0x15a+1])==smc[:1]
     colors+=1
  for value in range(8):
   for flags in [0x20,0x21,0x60,0xa1]:
    m=N.fork(seed);at=I.address(base,'VRAM_Buffer1');m[at:at+64]=[0x9d]*64;out=N.invoke(m,'CrossoverPatchStatusName',a=value,x=71,y=109,p=flags)
    assert(out['A'],out['X'],out['Y'])==(value,71,109)
    assert bytes(m[at+11:at+18])==(bytes([25,27,18,23,12,14,36])if value==0 else bytes([0x9d])*7),(value,bytes(m[at+11:at+18]),out)
    names+=1
  m=N.fork(seed);N.put(m,CurrentPlayer=0,NumberOfPlayers=0);N.invoke(m,'WriteGameText',a=0,x=71,y=109,p=0x21);at=I.address(base,'VRAM_Buffer1');assert bytes(m[at+11:at+18])==bytes([25,27,18,23,12,14,36])
 finally:N.NesMPU=actual
 e,m,labels=first8();out=e['run'](m,'GameLoop',labels);assert N.get(m,'Player_Y_Position')==176 and m.ram[2][0x84]+256*m.ram[2][0x85]==208
 x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc');xs=[]
 for epoch in range(48):
  m.controller_pad=1;N.put(m,SavedJoypad1Bits=1,SavedJoypadBits=1);e['run'](m,'GameLoop',labels);xs.append(N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'));assert N.get(m,'NumberofLives')==2 and N.get(m,'Player_Y_Position')==176
 assert xs[-1]>x
 q=dict(passed=True,CPU_only=True,source_code_injected=False,ROM_written=False,memory_SHA256=manifest['expected_memory_only_SHA256'],fullcold_CPU=cold['CPU'],complete_runtime_metadata_state_exact=True,cold_caller_Cwindow_201_restored=True,installer_readback_fault=fault,failed_headers_unpublished=True,retry_originalcold_restored=True,actual_native_palette_cases=colors,actual_status_callers=names,complete_WriteGameText_name=True,actual_ingress_counts=dict(events),actual_entrance_Y=176,first8_foot=208,Right_updates=48,Right_X=[x,xs[-1]],Right_first16=xs[:16],scope='Actual159 fullsourcebacked decoder/currentcookies/headerpublication. Source-declared native target CE:A296 reaches unchanged native backdrop for four themes/eight background selectors/six buffer bounds, then authentic Prince sprite palette. Actual CrossoverPatchStatusName and complete WriteGameText now write PRINCE only for message0 and preserve AX/Y. Genuine native entrance7->8 coordinates are resynchronized once before original sourcephase0;48Rightupdates advance without postFreshposition/outcome seed. Isolated CPU terrain/header inputs are explicit; no Mesen or fullstage/native-playable claim.',bindings={p.relative_to(R).as_posix():M.sha(p.read_bytes())for p in [Path(__file__),Path(M.__file__),O/'backdrop-manifest-v159.json',O/'backdrop-binding-v157.json',O/'backdrop-pool-v158.json',O/'native-installer-v153.s',O/'live-cold-CPU-v156.json',R/'src/characters.s',R/'src/screen_render.s']})
 (O/'backdrop-native-CPU-v160.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','Right_first16']}))


if __name__=='__main__':
 try:main()
 except Exception as error:
  (O/'backdrop-native-negative-v160.json').write_text(json.dumps(dict(passed=False,exception=repr(error)),indent=2)+'\n');raise
