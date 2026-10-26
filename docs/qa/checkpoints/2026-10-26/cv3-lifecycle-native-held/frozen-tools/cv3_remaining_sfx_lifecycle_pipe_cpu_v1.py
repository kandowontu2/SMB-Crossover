"""Source feasibility: genuine Down+A bat request and real pipe collision, no native claim."""
from pathlib import Path
import argparse,hashlib,json
from check_tmnt_render_oa import load,address
from cv3_remaining_sfx_queue256_support_v1 import init
from cv3_remaining_sfx_steady_cpu_v4 import invoke
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);b=load(a.rom);cases=[]
 for mode in[0,1]:
  q=init(b,3);q.put(CrossoverBehaviorVersion=mode,OperMode_Task=3,Player_X_Position=72,Player_PageLoc=0,Player_Y_Position=176,Player_Y_HighPos=1,PlayerSize=0,PlayerStatus=1,Player_State=0,Player_X_Speed=0,Player_Y_Speed=0,PlayerFacingDir=1,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,ScreenRight_X_Pos=255,ScreenRight_PageLoc=0,ScrollLock=1,AreaPointer=0xc2,AreaType=1,WarpZoneControl=0,GameEngineSubroutine=8,Cv3ActiveVariant=3,Cv3LastArea=0xc2,Cv3LastWorld=0,Cv3LastLife=q.get('NumberofLives'),Cv3Previous=0,SavedJoypadBits=0x84,Up_Down_Buttons=4,Left_Right_Buttons=0)
  q.set('Cv3Ready',1,2);q.set('Cv3Hearts',64,2);q.set('Cv3Health',64,2)
  for i in range(416):q.set('Block_Buffer_1',0,i);q.set('MmSolidTerrain',0,i)
  for page in range(2):
   for x in range(16):q.set('Block_Buffer_1',0x54,page*208+176+x);q.set('MmSolidTerrain',1,page*208+176+x)
  q.set('Block_Buffer_1',0x10,176+4);q.set('Block_Buffer_1',0x11,176+5)
  invoke(q,'Cv3MovementGate');movement=dict(bat=q.get('Cv3Bat'),active=q.get('Cv3NoiseActive'),head=q.get('Cv3FxQueueHead'),tail=q.get('Cv3FxQueueTail'),state=q.get('Player_State'),cachedAdder=q.get('Cv3CachedAdder'),X=q.get('Player_X_Position'),Y=q.get('Player_Y_Position'))
  assert q.get('Cv3Bat')==1 and(q.get('Cv3FxQueueHead')-q.get('Cv3FxQueueTail'))&255==1
  invoke(q,'PlayerBGCollision');collision=dict(sub=q.get('GameEngineSubroutine'),timer=q.get('ChangeAreaTimer'),R0=q.get('R0'),R1=q.get('R1'),X=q.get('Player_X_Position'),Y=q.get('Player_Y_Position'))
  assert collision['sub']==3 and collision['timer']==48,(mode,movement,collision)
  invoke(q,'AudioUpdate');assert q.get('Cv3FxNoiseID')==q.get('Cv3FxPulseID')==0x2f;assert q.get('Cv3FxQueueHead')==q.get('Cv3FxQueueTail')
  for frame in range(48):invoke(q,'VerticalPipeEntry');invoke(q,'AudioUpdate')
  assert q.get('OperMode_Task')==0 and q.get('DisableScreenFlag')>0 and q.get('Cv3FxOwned')!=0
  cases.append(dict(mode=mode,genuine_movement=movement,genuine_BG_pipe_collision=collision,real_VerticalPipeEntry_updates=48,task_after_pipe=q.get('OperMode_Task'),source_owned_before_area_load=q.get('Cv3FxOwned'),source_index=q.get('Cv3NoiseIndex'),source_pulse_frame=q.get('Cv3FxPulseFrame')))
 r=dict(passed=True,native_executed=False,ROM_sha256=sha(a.rom),cases=cases,scope='Actual assembled Down+A movement→bat source queue, native foot metatiles10/11→real HandlePipeEntry→48 real VerticalPipeEntry updates. AreaPointerC2 and pipe buffer geometry are staged only before execution, authentic1-1 enemy destination record1E,C2,00. Source bat voices remain active when task0 area loading begins. Full actual native loader/music/reset cancellation still unproved; no PPU/controller/native scene coverage claim.',tool_sha256=sha(__file__));(a.output/'proof.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
