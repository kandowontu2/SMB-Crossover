"""Publish the actual pre-step native camera witness for private raw41."""
from pathlib import Path
import json,re,subprocess,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import prepare_mini_mario_host_1103_v22 as H
import check_mini_mario_step_1103_v18 as T
from py65.devices.mpu6502 import MPU
W,R,O=H.W,H.R,H.O
def main():
 src=(O/'mini-host-v28.s').read_text();S=H.symbols();src=f'Player_Pos_ForScroll=${S["Player_Pos_ForScroll"]:04x}\n'+src
 needle=' lda Player_Y_Position\n sta MiniOldY\n';assert src.count(needle)==1
 src=src.replace(needle,needle+''' lda Player_X_Position
 sec
 sbc ScreenLeft_X_Pos
 sta Player_Pos_ForScroll
''')
 p=O/'mini-host-v30';p.with_suffix('.s').write_text(src);p.with_suffix('.cfg').write_bytes((O/'mini-host-v28.cfg').read_bytes());cc=R/'tools/Windows/cc65/bin'
 for cmd in[[cc/'ca65.exe',p.with_suffix('.s'),'-o',p.with_suffix('.o')],[cc/'ld65.exe','-C',p.with_suffix('.cfg'),p.with_suffix('.o'),'-o',p.with_suffix('.bin'),'-Ln',p.with_suffix('.lbl')]]:
  r=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert r.returncode==0,r.stderr
 data=p.with_suffix('.bin').read_bytes();L={n:int(v,16)for v,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',p.with_suffix('.lbl').read_text(),re.M)};assert len(data)==4977
 # NativeCPU Main: the exact pre-step integer relative X is published for
 # all camera low phases, worldpages and legal scroll follow positions.
 attrs=(R/'build/mini-mario-native-tile-1103-v13/native-attributes.bin').read_bytes();idx=(R/'build/mini-mario-art-1103-v12/engine-animation-index.bin').read_bytes();frames=(R/'build/mini-mario-art-1103-v12/engine-animation-frames.bin').read_bytes();cases=0
 for camera in[0,1,15,16,127,128,255,256,511,1024,2048,3072]:
  for relative in[0,40,79,80,81,111,112,200,239]:
   m=T.memory(data,L,0);m.memory[0xd300:0xd400]=attrs;m.memory[0xd000:0xd160]=idx;m.memory[0xd160:0xd239]=frames;T.call(m,L['MiniHostFresh']);world=camera+relative
   for n,v in dict(GameEngineSubroutine=8,Player_X_Position=world&255,Player_PageLoc=world>>8,Player_Y_Position=176,Player_Y_HighPos=1,ScreenLeft_X_Pos=camera&255,ScreenLeft_PageLoc=camera>>8,SavedJoypadBits=65).items():m.memory[S[n]]=v
   T.call(m,L['MiniHostMain']);assert m.memory[S['Player_Pos_ForScroll']]==relative,(camera,relative,m.memory[S['Player_Pos_ForScroll']]);cases+=1
 # Same source Step/code prefix: camera publication lies exclusively in
 # hostMain after complete source/kernel/renderer/animation sections.
 old=(O/'mini-host-v28.bin').read_bytes();oldq=json.loads((O/'mini-host-v28.json').read_text());at=L['MiniHostMain']-0xa000;assert data[114:at]==old[114:at]
 out=dict(passed=True,bytes=len(data),SHA256=W.sha(data),labels=L,vectors=[int.from_bytes(data[i*3+1:i*3+3],'little')for i in range(38)],CPU_camera_witness_cases=cases,Player_Pos_ForScroll=S['Player_Pos_ForScroll'],source_kernel_render_animate_prefix_exact=True,added_host_bytes=9,scope='Actual pre-step integer player screenX published exactly like X5NewMovementFinish for native ScrollHandler threshold80. No source physics, native scroll force or border rules changed. Actual fullstage root acceptance pending.',old_actual_negative='build/mini-mario-full11-packet-1103-v28/full11/capture/result.json',bindings={p.relative_to(R).as_posix():W.sha(p.read_bytes())for p in[Path(__file__),O/'mini-host-v28.s',O/'mini-native-anchor-CPU-v29.json',R/'src/player.s',R/'src/x5_bounce.s']})
 (O/'mini-host-v30.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k]for k in['passed','bytes','SHA256','labels','CPU_camera_witness_cases','Player_Pos_ForScroll']}))
if __name__=='__main__':main()
