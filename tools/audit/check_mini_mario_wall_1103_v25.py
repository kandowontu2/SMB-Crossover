"""Isolated native-buffer fixture for the explicit wall-jump host adaptation.

Not a native GameCore/Mesen traversal. No terrain/actor placed in a cartridge.
"""
from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import prepare_mini_mario_world_1103_v11 as W
import prepare_mini_mario_host_1103_v22 as H
import check_mini_mario_step_1103_v18 as T
R,O=W.R,H.O

def main():
 q=json.loads((O/'mini-host-v22.json').read_text());data=(O/'mini-host-v22.bin').read_bytes();L=q['labels'];S=H.symbols();records=[]
 for height in[32,48,64,80]:
  m=T.memory(data,L,0);attrs=(R/'build/mini-mario-native-tile-1103-v13/native-attributes.bin').read_bytes();m.memory[0xd300:0xd400]=attrs;m.memory[0xd000:0xd160]=(R/'build/mini-mario-art-1103-v12/engine-animation-index.bin').read_bytes();m.memory[0xd160:0xd239]=(R/'build/mini-mario-art-1103-v12/engine-animation-frames.bin').read_bytes();solid=next(i for i,v in enumerate(attrs)if v&3==1 and i!=0x26)
  for y in range(208-height,208,16):m.memory[0x300+((y&240)-32)+6]=solid
  for n,v in dict(GameEngineSubroutine=8,Player_X_Position=40,Player_PageLoc=0,Player_Y_Position=176,Player_Y_HighPos=1).items():m.memory[S[n]]=v
  T.call(m,L['MiniHostFresh']);started=False;jumps=0;events=[];lastq=0;miny=255;finished=False
  for frame in range(220):
   worldx=m.memory[S['Player_X_Position']]|m.memory[S['Player_PageLoc']]<<8
   if worldx>=70:started=True
   keys=0x41
   if started:
    cling=(m.memory[0xc24c]&8)and not(m.memory[0xc24c]&1)and(m.memory[0xc220:0xc222]==[0,0])
    if not(cling and lastq!=12 and(m.memory[0xc249]&128)):keys|=128
   m.memory[S['FrameCounter']]=frame&255;m.memory[S['SavedJoypadBits']]=keys;T.call(m,L['MiniHostMain'])
   nq=m.memory[0xc228]
   if nq==12 and lastq!=12:
    jumps+=1;events.append(dict(epoch=frame,kind='original_queued_JUMP_INIT',X=m.memory[S['Player_X_Position']],Y=m.memory[S['Player_Y_Position']],wall_contact=m.memory[0xc24c]))
   lastq=nq;miny=min(miny,m.memory[S['Player_Y_Position']])
   if m.memory[S['Player_X_Position']]>=120:
    finished=True;break
  records.append(dict(isolated_fixture=True,wall_left=96,wall_top=208-height,height=height,updates=frame+1,cleared=finished,jump_requests=jumps,min_canvasY=miny,events=events))
  assert finished,(height,records[-1])
 out=dict(passed=True,component_SHA256=W.sha(data),fixtures=records,scope='Private host Main and actual MiniNativeTile over in-memory native BlockBuffer fixture only. No generic nativeBGCollision/side/feet interference included, no native/Mesen helper or1-1 acceptance. All jumps use original source JUMP_INIT and original constants; wallcling/freshA admission is the explicitly authorized host adaptation.')
 (O/'mini-wall-CPU-v25.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
