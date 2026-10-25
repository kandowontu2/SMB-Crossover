"""Cold controller capture of Bass preview, idle, walk, and five firing poses."""
from pathlib import Path
import argparse,subprocess,sys
R=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
o=a.output.resolve();o.mkdir(parents=True,exist_ok=False)
script=o/'capture.lua'
script.write_text('OUT='+repr(o.as_posix()+'/')+'\n'+r'''
local f,phase,arrived,entered=0,0,0,nil
local function r(n)return emu.read(assert(L[n],n),emu.memType.nesDebug)end
local function shot(n)local q=assert(io.open(OUT..n..'.png','wb'));q:write(emu.takeScreenshot());q:close()end
local csv=assert(io.open(OUT..'poses.csv','w'));csv:write('frame,t,pose,bank,ptr,x,y,status\n')
emu.addEventCallback(function()
 local b={}
 if phase==0 then b.start=f==60;if r('CrossoverMenuState')==2 then phase=1 end
 elseif phase==1 and f%12==0 then
  local i=r('CrossoverMenuIndex')
  if i<6 then b.down=true elseif i~=9 then b.right=true else phase=2;arrived=f end
 elseif phase==2 and f>arrived+35 then
  shot('selection')
  local q=assert(io.open(OUT..'menu-ppu.bin','wb'));for i=0x2000,0x23ff do q:write(string.char(emu.read(i,emu.memType.nesPpuDebug)))end;q:close()
  q=assert(io.open(OUT..'menu-pal.bin','wb'));for i=0x3f00,0x3f1f do q:write(string.char(emu.read(i,emu.memType.nesPpuDebug)))end;q:close()
  q=assert(io.open(OUT..'menu-chr.bin','wb'));for i=0,0xfff do q:write(string.char(emu.read(i,emu.memType.nesPpuDebug)))end;q:close()
  b.a=true;phase=3
 elseif entered then
  local t=f-entered
  b.right=t>=30 and t<78
  b.left=t>=92 and t<116
  b.a=t>=128 and t<150
  b.b=t>=190 and t<340
  if t>=220 and t<250 then b.up=true
  elseif t>=250 and t<280 then b.up=true;b.right=true
  elseif t>=280 and t<310 then b.down=true;b.right=true
  elseif t>=310 and t<340 then b.down=true end
 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 f=f+1
 if phase==3 and r('OperMode')==1 and r('GameEngineSubroutine')==8 then entered=f;phase=4;shot('entry')end
 if entered then
  local t=f-entered
  csv:write(table.concat({f,t,r('RgPose'),r('SmChrBank'),r('SmPosePtr')+256*emu.read(L.SmPosePtr+1,emu.memType.nesDebug),r('Player_X_Position'),r('Player_Y_Position'),r('PlayerStatus')},',')..'\n')
  if t%4==0 then shot(string.format('pose-%03d',t))end
  if t==360 then csv:close();emu.stop(0)end
 end
 assert(f<1600,'capture timed out')
end,emu.eventType.endFrame)
''')
subprocess.run([sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(o),str(script),str(a.rom.resolve()),'--timeout','40','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false'],cwd=R,check=True)
