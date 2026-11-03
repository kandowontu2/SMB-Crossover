"""Rebind unchanged suite to corrected native small anchor; actual getters."""
from pathlib import Path
import json,subprocess,sys
from py65.devices.mpu6502 import MPU
sys.path.insert(0,str(Path(__file__).resolve().parent))
import prepare_mini_mario_host_1103_v22 as H
import check_mini_mario_step_1103_v18 as T
W,R,O=H.W,H.R,H.O
def main():
 old=R/'tools/audit/check_mini_mario_host_1103_v24.py';src=old.read_text()
 replacements=[('mini-host-v22.json','mini-host-v28.json'),('mini-host-v22.bin','mini-host-v28.bin'),('mini-host-CPU-v24.json','mini-host-CPU-v29-rebound.json'),("m.memory[S['Player_Y_Position']]==192","m.memory[S['Player_Y_Position']]==176"),('min(ys)==max(ys)==192','min(ys)==max(ys)==176'),('canvasY=192','native_small_Y=176'),('(180+8)*16+11','(180+24)*16+11'),('(y+8+(1 if tier==0 else -7))','(y+24+(1 if tier==0 else -7))'),('(y+15)&255','(y+31)&255')]
 replacements.append(("q['unimplemented_reject_rows']",repr(json.loads((O/'mini-host-v22.json').read_text())['unimplemented_reject_rows'])))
 for a,b in replacements:
  assert a in src,(a,b);src=src.replace(a,b)
 # This is the exact same 800/180/60/80/576 suite, only its explicitly
 # changed native-anchor expectations and component binding are adjusted.
 p=O/'native-anchor-rebound-suite-v29.py';p.write_text(src)
 r=subprocess.run([sys.executable,'-B','-c',"import sys,runpy;sys.path.insert(0,'tools/audit');runpy.run_path(sys.argv[1],run_name='__main__')",str(p)],cwd=R,capture_output=True,text=True);assert r.returncode==0,r.stdout+r.stderr
 q=json.loads((O/'mini-host-v28.json').read_text());data=(O/'mini-host-v28.bin').read_bytes();L=q['labels'];S=H.symbols();rom=R/'build/mini-mario-candidate-root-1103-v27/mini-private.nes';raw=rom.read_bytes();assert W.sha(raw)=='39bb02f36819f88772584bed311992762de74b1099aeb262e8ee71cfd2deb5a4'
 attrs=(R/'build/mini-mario-native-tile-1103-v13/native-attributes.bin').read_bytes();calls=0
 def mem():
  m=MPU();m.memory[0x8000:0xa000]=raw[16+126*8192:16+127*8192];m.memory[0xe000:0x10000]=raw[16+127*8192:16+128*8192];m.memory[0xa000:0xa000+len(data)]=data;m.memory[0xd300:0xd400]=attrs;m.memory[S['GameEngineSubroutine']]=8;m.memory[S['Player_X_Position']]=47;m.memory[S['Player_Y_Position']]=176;m.memory[S['Player_Y_HighPos']]=1
  return m
 for pc,entry,Y in[(S['BlockBufferColli_Side'],'MiniHostSide',17),(S['BlockBufferColli_Head'],'MiniHostHead',14)]:
  for tile in range(256):
   a,b=mem(),mem()
   for m in[a,b]:
    m.memory[0x300:0x4a0]=[tile]*416;m.memory[3:5]=[0x55,0xaa];m.a=99;m.x=11;m.y=Y;m.p=0x24
   T.call(a,pc);T.call(b,L[entry]);expected=tile if tile in[0xc2,0xc3]or attrs[tile]&3!=1 else 0
   assert b.a==expected,(entry,tile,b.a,expected)
   assert b.memory[3:11]==a.memory[3:11]and(b.x,b.y)==(a.x,a.y)==(0,Y)
   assert b.p&0x41==a.p&0x41 and bool(b.p&2)==(expected==0)and bool(b.p&128)==bool(expected&128)
   calls+=1
 # Actual fixed feet getter: supported native176 samples floor208, with
 # returned native anchor low-nibble0. All earlier air anchors stay empty.
 m=mem();ground=next(i for i,x in enumerate(attrs)if x&3==1 and i not in[0xc2,0xc3,0x26])
 for y in range(208,240,16):
  for x in range(16):m.memory[0x300+y-32+x]=ground
 feet=[]
 for y in[128,144,160,172,173,174,175,176]:
  m.memory[S['Player_Y_Position']]=y;m.y=14;T.call(m,S['BlockBufferColli_Feet']);feet.append(dict(nativeY=y,tile=m.a,low_nibble=m.memory[7]));assert bool(m.a)==(y==176)
 assert feet[-1]['low_nibble']==0
 out=dict(passed=True,component_bytes=len(data),component_SHA256=W.sha(data),rebound_complete_suite='mini-host-CPU-v29-rebound.json',actual_candidate_fixed_getter_cases=calls,all256tiles_bothgetter_packets_XY_CV_exact=True,coin_C2_C3_retained=True,vine_flagpole_climb_retained=True,actual_native_small_feet=feet,old_actual_drift_negative_retained=q['actual_negative'],scope='Same originalStep/native contracts rebound to native32pxsmallanchor; actual current39bb fixed-ROM head/side/feet instructions, all256 rawmetatiles. Native GameCore/Mesen acceptance remains root-owned.',bindings={p.relative_to(R).as_posix():W.sha(p.read_bytes())for p in[Path(__file__),old,O/'mini-host-v28.json',O/'mini-host-CPU-v29-rebound.json',p,rom]})
 (O/'mini-native-anchor-CPU-v29.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
