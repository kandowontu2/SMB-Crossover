"""Exercise actual native death dispatch, duplicate ticks and pause."""
import json
import prepare_metal_storm_death_host_1101_v34 as P
import check_hogan_current_bounded_v1 as M
from link_pit_rygar_sophia_audit_cpu import scoped_load

def main():
 b=scoped_load(P.O/'candidate.nes');m=M.fresh(b)
 for bank,at,file in [(3,0,'native-actor.bin'),(2,0xd00,'native-render.bin'),(2,0x1ba0,'native-extra.bin')]:
  data=(P.O/file).read_bytes();m.ram[bank][at:at+len(data)]=data
 for bank in [2,3]:m.ram[bank][0x1fe0:0x1ff0]=(P.O/'native-cookie.bin').read_bytes()
 M.put(m,SelectedCharacter=35,OperMode=1,GameEngineSubroutine=8,FrameCounter=10,GamePauseStatus=0,Player_X_Position=120,Player_Y_Position=176,Player_Y_HighPos=1,NumberofLives=2)
 m.ram[2][0x800]=167;m.ram[2][0x480]=120;m.ram[2][0x4b0]=176
 M.invoke(m,'HuDeathStart');assert m.ram[2][0x34]==2
 M.put(m,GameEngineSubroutine=11)
 transitions=[];previous=None
 for tick in range(1,143):
  M.put(m,FrameCounter=(10+tick)&255);M.invoke(m,'HuDeath')
  state=bytes(m.ram[2][:2048]);engine=M.get(m,'GameEngineSubroutine')
  view=[state[a] for a in [0x35,0x4e0,0x4f8,0x53]]
  if view!=previous:transitions.append([tick,*view]);previous=view
  assert engine==(6 if tick==142 else 11),(tick,engine,view)
  M.invoke(m,'HuDeath');assert bytes(m.ram[2][:2048])==state,'duplicate'
  M.put(m,GamePauseStatus=1,FrameCounter=(11+tick)&255);M.invoke(m,'HuDeath');assert bytes(m.ram[2][:2048])==state,'pause'
  M.put(m,GamePauseStatus=0)
 assert M.get(m,'NumberofLives')==2,'callback must not decrement independently'
 assert m.ram[2][0x35]==4
 M.invoke(m,'GameRoutines')
 assert M.get(m,'NumberofLives')==1,('native life loss',M.get(m,'NumberofLives'))
 q=dict(passed=True,ROM_sha256=P.P.sha(P.O/'candidate.nes'),actual_host_callbacks=True,updates=142,duplicate_checks=142,pause_checks=142,transition_rows=transitions,life_loss_handoff_engine=6,actual_GameRoutines_life_decrement=True,scope='Authenticated cache fixture, actual HuDeathStart/HuDeath and GameRoutines ROM dispatch. Original death state progression, engine6 handoff and one life decrement proven. Native respawn and explosion pixels not verified.')
 (P.O/'death-CPU.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items() if k!='transition_rows'}))
if __name__=='__main__':main()
