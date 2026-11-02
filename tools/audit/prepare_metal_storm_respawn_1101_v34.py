from pathlib import Path
import prepare_metal_storm_death_host_1101_v34 as P
from prepare_selected_native_packet_v1 import prepare,sha

def main():
 ref=P.P.R/'tools/reference/metal_storm_natural_armor_1101_v26.lua';t=ref.read_text()
 t=t.replace('local route,ticks,initialLives=0,0,nil','local route,ticks,initialLives=0,0,nil\nlocal lost=false\nlocal respawnTicks=0')
 t=t.replace("local passed=got and spawned and matured and r('NumberofLives')==initialLives", "local passed=lost and r('NumberofLives')==initialLives-1 and r('GameEngineSubroutine')==8 and r('OperMode_Task')==3")
 t=t.replace("elseif r('NumberofLives')~=initialLives then finish('lost-life')", "elseif r('NumberofLives')<initialLives then\n   lost=true\n   if r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 and worldx()<100 then\n    respawnTicks=respawnTicks+1\n    if respawnTicks>=25 and worldx()>40 then finish('respawned-and-moving') end\n   end")
 prepare(P.O/'native-respawn-v2',P.O/'candidate.nes',t,[Path(__file__),ref],expected=sha(P.O/'candidate.nes'),timeout=90,scope='Controller-only reproduced lethal Goomba route, one life loss,25 respawn gameplay frames and resumed movement; original explosion graphics pending. No RAM writes, at most three screenshots.')
if __name__=='__main__':main()
