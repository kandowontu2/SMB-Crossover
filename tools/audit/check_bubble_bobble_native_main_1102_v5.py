"""Actual native GameCoreRoutine in bounded legal CPU arenas; no emulator."""
import json,sys
from pathlib import Path
import check_bubble_bobble_native_proxy_1102_v5 as Q
P=Q.P;N=Q.N;C=Q.C;R=Q.R;O=Q.O;address=Q.address
sys.path.insert(0,str(R/'tools/reference'))
import bubble_bobble_native_model_1101_v3 as Original


def main():
 b,q,route=Q.bundle();checks={};cls=N.NesMPU;calls={};trace=[];tail=[]
 names=['GameCoreRoutine','PlayerCtrlRoutine','HuMovement','HuBody','HuGraphics','HuDraw','HuFullBox','HuHead','HuSide','HuWeaponTail','PlayerGfxHandler','DrawAllMetasprites','MegaManFullShotBank','BoundingBoxCore','ShellOrBlockDefeat','EnemiesAndLoopsCore','RunEnemyObjectsCore','DrawMetasprite']
 points={(((Q.Q.Q.location(b,n)-16)//8192)|128,address(b,n)):n for n in names if n in b['syms']}
 for name in['BbNativeUpdate','BbNativeDraw','BbNativeFullBox','BbNativeBodyContact']:
  points[(3,q['labels'][name])]=name
 class Trace(cls):
  def step(self):
   if self.pc>=0x8000:
    key=(self.memory.rawtags[(self.pc-0x8000)//8192],self.pc);name=points.get(key)
    if name:
     calls[name]=calls.get(name,0)+1
     if len(trace)<120:trace.append([name,self.a,self.x,self.y,N.get(self.memory,'GameEngineSubroutine')])
     if N.get(self.memory,'FrameCounter')==83:tail.append([name,N.get(self.memory,'Player_X_Position'),N.get(self.memory,'Player_PageLoc'),N.get(self.memory,'ScreenLeft_X_Pos'),N.get(self.memory,'Player_X_Scroll')])
   return cls.step(self)
 N.NesMPU=Trace
 try:
  rows=[]
  for identity in[0,1]:
   m=Q.fresh(b,route,identity);N.put(m,CurrentPlayer=0,AreaParserTaskNum=7,TimerControl=0,GameTimerCtrlTimer=24,GameTimerExpiredFlag=0,WorldNumber=0,LevelNumber=0,DisableIntermediate=1)
   oracle=Original.Host(identity,leaves=False);oracle.terrain(lambda x,y:0x54 if y>=208 else 0)
   for i,v in enumerate([4,0,0]):m[address(b,'GameTimerDisplay')+i]=v
   start=N.get(m,'Player_X_Position');ys=[];sizes=(N.get(m,'PlayerSize'),N.get(m,'PlayerStatus'));cycles=[]
   for frame in range(84):
    keys=1|(128 if frame==20 else 0)
    N.put(m,FrameCounter=frame,SavedJoypadBits=keys,SavedJoypad1Bits=keys,VRAM_Buffer1_Offset=0)
    z=N.invoke(m,'GameCoreRoutine',a=85,x=0,y=0,p=0x31);cycles.append(z['CPU']);ys.append(N.get(m,'Player_Y_Position'))
    oracle.step(keys,epoch=frame)
    assert N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc')==oracle.worldx()and N.get(m,'Player_Y_Position')==oracle.worldy()-256,('Original whole-frame transport',identity,frame)
    actor=0x42 if identity else 0x2e
    assert bytes(m.ram[2][actor:actor+20])==bytes(oracle.s[actor:actor+20]),('Original actor state',identity,frame)
    assert N.get(m,'GameEngineSubroutine')==8 and N.get(m,'NumberofLives')==2,(identity,frame,trace,N.get(m,'GameEngineSubroutine'))
    assert N.get(m,'CurrentOAMOffset')%4==0 and N.get(m,'RgOamRotation')%4==0
    assert m[address(b,'ObjectMetasprite')]==0 and N.get(m,'SmPosePtr')+256*N.get(m,'SmPosePtr',1)==address(b,'ObjectMetasprite')
    assert N.get(m,'CurrentCHRBank',4)==185 and N.get(m,'X5ChrMode',4)==129
   world=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc');camera=N.get(m,'ScreenLeft_X_Pos')+256*N.get(m,'ScreenLeft_PageLoc')
   assert min(ys)==133 and N.get(m,'Player_Y_Position')==176 and world==oracle.worldx()==start+56,(identity,min(ys),ys[-1],world,camera,tail)
   assert sizes==(N.get(m,'PlayerSize'),N.get(m,'PlayerStatus'))
   rows.append(dict(identity=identity,frames=84,x=N.get(m,'Player_X_Position'),apex=min(ys),landed_y=ys[-1],lives=2,mean_CPU=sum(cycles)/len(cycles),max_CPU=max(cycles)))
  checks['actual_native_Main_idle_walk_original_jump']=rows
  lifecycle=[]
  for identity in[0,1]:
   m=Q.fresh(b,route,identity);N.put(m,CurrentPlayer=0,AreaParserTaskNum=7,TimerControl=0,GameTimerCtrlTimer=24,GameTimerExpiredFlag=0,WorldNumber=0,LevelNumber=0,DisableIntermediate=1)
   for i,v in enumerate([4,0,0]):m[address(b,'GameTimerDisplay')+i]=v
   Q.Q.enemy(m,x=100,y=184);N.invoke(m,'InitGoomba',x=0);m[address(b,'Enemy_X_Speed')]=8
   trapped=None;released=None;flag_before=Q.fields(m,0)['Enemy_Flag'];defeats=calls.get('ShellOrBlockDefeat',0)
   for frame in range(70):
    keys=64 if frame==0 else 0
    N.put(m,FrameCounter=frame,SavedJoypadBits=keys,SavedJoypad1Bits=keys,VRAM_Buffer1_Offset=0)
    N.invoke(m,'GameCoreRoutine',a=85,x=0,y=0,p=0x31)
    if m.ram[2][0x320]and trapped is None:
     trapped=frame;pose=N.get(m,'EnemyMetasprite');assert pose>0 and N.get(m,'Enemy_Flag')==128
     # Native position transport moves the player away after actual capture;
     # no private bubble/token/trap timer is supplied by the fixture.
     N.put(m,Player_X_Position=32)
    if trapped is not None:
     if not m.ram[2][0x320]:released=frame;break
     assert N.get(m,'EnemyMetasprite')==pose and N.get(m,'CurrentOAMOffset')%4==0,(identity,frame,trapped,pose,N.get(m,'EnemyMetasprite'),N.get(m,'Enemy_Flag'),m.ram[2][0x320],N.get(m,'CurrentOAMOffset'))
   assert trapped is not None and released==trapped+39 and N.get(m,'Enemy_Flag')==flag_before and calls.get('ShellOrBlockDefeat',0)==defeats,(identity,trapped,released,Q.fields(m,0))
   assert N.get(m,'NumberofLives')==2 and N.get(m,'GameEngineSubroutine')==8
   lifecycle.append(dict(identity=identity,trap_frame=trapped,original_timeout_release_frame=released,native_victim_pose=pose,positive_flag_restored=flag_before,lives=2))
  checks['actual_Main_original_shot_trap_native_suspension_art_timeout']=lifecycle
 finally:N.NesMPU=cls
 for name in['GameCoreRoutine','HuMovement','BbNativeUpdate','BbNativeDraw','BbNativeFullBox','HuHead','HuSide','MegaManFullShotBank','DrawAllMetasprites']:assert calls.get(name),('Unreached Main ingress',name,calls,trace)
 out=dict(passed=True,ROM_written=False,shared_source_written=False,admitted=False,base_ROM_SHA256=P.PIN,checks=checks,actual_Main_ingress_counts=calls,layout=q,scope='Actual native GameCoreRoutine in an explicit legal flat-room CPU arena; AreaParserTaskNum7 suppresses new parser activity and game timer starts400. Entire player/graphics/enemy-loop/object/DrawAll path runs. No Mesen/controller/parser/stage-clear/IRQ or installation claim.',bindings={p.relative_to(R).as_posix():P.sha(p.read_bytes())for p in[Path(__file__),R/'tools/audit/prepare_bubble_bobble_native_proxy_1102_v5.py',O/'native-proxy.bin',O/'native-proxy-helper.chr',O/'native-proxy-ports.bin',O/'native-proxy-bbox.bin']})
 (O/'native-proxy-Main-CPU.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(passed=True,checks=checks,actual_Main_ingress_counts=calls)))


if __name__=='__main__':main()
