"""Exercise combined armor hit/recovery through actual native union callbacks."""
import json
import prepare_metal_storm_hurt_host_1101_v24 as P
import check_hogan_current_bounded_v1 as M
from link_pit_rygar_sophia_audit_cpu import scoped_load

def main():
 q=json.loads((P.O/'assembly.json').read_text())
 for p,h in q['bindings'].items():assert P.P.sha(p)==h,p
 b=scoped_load(P.O/'candidate.nes');m=M.fresh(b)
 for bank,off,name in [(3,0,'native-actor.bin'),(2,0xd00,'native-render.bin')]:
  data=(P.O/name).read_bytes();m.ram[bank][off:off+len(data)]=data;m.ram[bank][0x1fe0:0x1ff0]=bytes.fromhex(q['cookie'])
 M.put(m,SelectedCharacter=35,OperMode=1,GameEngineSubroutine=8,CurrentPlayer=0,NumberofLives=2,Player_X_Position=40,Player_PageLoc=0,Player_Y_Position=176,Player_Y_HighPos=1,FrameCounter=1,GamePauseStatus=0,SavedJoypadBits=0)
 M.invoke(m,'HuMovement');assert m.ram[2][0x800]==167
 m.ram[2][0x5d0]=128;m.ram[2][0x648]=0;m.ram[2][0x660]=0;m.ram[2][0x630]=0
 status=M.invoke(m,'HuInjuryStatus');assert status['A']==1
 hit=M.invoke(m,'HuInjury');assert hit['P']&1 and m.ram[2][0x34]==2 and m.ram[2][0x648]==128
 fields=[0x33,0x34,0x35,0x5d0,0x648,0x74b];rows=[];duplicate=paused=0
 for tick in range(212):
  M.put(m,FrameCounter=(tick+2)&255,GamePauseStatus=0)
  result=M.invoke(m,'HuMovement');assert result['P']&1
  state=[m.ram[2][a] for a in fields];rows.append(state)
  if tick<32:assert state[1]==2 and state[3]==128 and state[5]==0,(tick,state)
  else:assert state[1]==0 and state[3]==0 and state[5]==max(211-tick,0),(tick,state)
  assert state[4]==(128 if tick<211 else 0),(tick,state)
  if tick<211:
   m.ram[2][0x7e7]=0
   M.invoke(m,'HuInjury')
   assert [m.ram[2][a] for a in fields]==state and m.ram[2][0x7e7]==0
  M.invoke(m,'HuMovement');assert [m.ram[2][a] for a in fields]==state;duplicate+=1
  M.put(m,FrameCounter=(tick+3)&255,GamePauseStatus=1)
  M.invoke(m,'HuMovement');assert [m.ram[2][a] for a in fields]==state;paused+=1
 assert M.invoke(m,'HuInjuryStatus')['A']==0
 result=dict(passed=True,ROM_sha256=q['ROM_sha256'],combined_recovery_updates=len(rows),duplicate_callbacks=duplicate,paused_callbacks=paused,final_source_fields=dict(zip(map(hex,fields),rows[-1])),fixture='Compiled caches/header manually seeded; actual constructor, injury/status and movement callbacks execute. Armor is a fixture, not a collected pickup. Not native emulator proof.',scope='Source armor-hit recovery only. Rendering/audio/enemy effects, lethal damage, powerups and full-level/native checks incomplete. Not installed.')
 (P.O/'hurt-CPU.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
