"""Controller-only menu walk and native PPU/OAM capture for every identity."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import re

ROOT=Path(__file__).resolve().parents[2]
CASES=[('Mario',0,0,None,0),('Luigi',0,8,'MarioVariant',1),
       ('Mega Man',1,1,'ProtoVariant',0),('Proto Man',1,1,'ProtoVariant',1),
       ('Samus',2,2,None,0),('Bill',3,3,'BillVariant',0),('Lance',3,3,'BillVariant',1),
       ('Link',4,4,'Z2Variant',0),('Zelda II Link',4,4,'Z2Variant',1),
       ('Simon',5,5,'Cv3Variant',0),('Grant',5,5,'Cv3Variant',1),
       ('Sypha',5,5,'Cv3Variant',2),('Alucard',5,5,'Cv3Variant',3),
       ('Pit',6,6,None,0),('Rygar',7,7,None,0),
       ('Scrooge',8,12,'DarkwingVariant',0),('Darkwing',8,12,'DarkwingVariant',1),
       ('Bass',9,9,None,0),('Ryu',10,10,None,0),('Sophia',11,11,None,0),
       ('Kirby',12,13,'KbVariant',0),('Chip',13,14,'CdVariant',0),('Dale',13,14,'CdVariant',1),
       ('Little Mac',14,15,None,0),('Mike Jones',15,16,None,0),
       ('SMB3 Mario',16,17,'M3Variant',0),('SMB3 Luigi',16,17,'M3Variant',1),
       ('Vic Viper',17,18,None,0),('Leonardo',18,19,'TnVariant',0),
       ('Raphael',18,19,'TnVariant',1),('Michelangelo',18,19,'TnVariant',2),
       ('Donatello',18,19,'TnVariant',3),('Meta Knight',12,13,'KbVariant',1)]

LUA=r'''
local frame,which,phase,settled=0,1,0,0
local rapidStart=nil
local mask=0;local blankFrames=0;local browsing=false;local first=true
local function r(n)return emu.read(assert(L[n],n),emu.memType.nesDebug)end
local function file(name,data)local f=assert(io.open(OUTPUT..name,'wb'));f:write(data);f:close()end
local function bytes(start,count,kind)local t={}for i=0,count-1 do t[#t+1]=string.char(emu.read(start+i,kind))end;return table.concat(t)end
local spriteBanks={};local chrUpper=0
if SOURCE_MMC5 then
 emu.addMemoryCallback(function(a,v)chrUpper=v&3 end,emu.callbackType.write,0x5130)
 emu.addMemoryCallback(function(a,v)spriteBanks[a-0x5120]=v+chrUpper*256 end,emu.callbackType.write,0x5120,0x5127)
end
local function spriteCHR()
 if not SOURCE_MMC5 then return bytes(0,8192,emu.memType.nesPpuDebug)end
 local t={}
 for page=0,7 do
  local bank=assert(spriteBanks[page],'Unobserved MMC5 sprite bank')
  t[#t+1]=bytes(bank*1024,1024,emu.memType.nesChrRom)
 end
 return table.concat(t)
end
local trace=TRACE and assert(io.open(OUTPUT..'browsing.bin','wb'))or nil
local dmaMax=0;local dmaCount=0
local function finish()
 if trace then trace:close()end
 file('proof.json',string.format('{"identities":%d,"outlines":%s,"controller_only":true,"frames":%d,"blank_frames_while_browsing":%d,"DMA_frames_checked":%d,"latest_DMA_scanline":%d,"rapid_switch_frames":%d}',#CASES,tostring(OUTLINES),frame,blankFrames,dmaCount,dmaMax,rapidStart and frame-rapidStart or 0))
 print('PASS complete menu walk; blank browsing frames='..blankFrames);emu.stop(0)
end
emu.addMemoryCallback(function()
 if browsing and TRACE then
  local state=emu.getState();local scan=state['ppu.scanline']
  local cycle=state['ppu.cycle']
  assert(scan>=241 and scan*341+cycle+1548<261*341,'Menu OAM DMA exceeds VBlank: '..scan..':'..cycle)
  dmaMax=math.max(dmaMax,scan);dmaCount=dmaCount+1
 end
end,emu.callbackType.write,0x4014)
local function capture(case)
 local key=string.format('%02d-%s-%s',which,OUTLINES and 'on'or'off',case[1]:lower():gsub(' ','-'))
 file(key..'.png',emu.takeScreenshot())
 file(key..'-chr.bin',spriteCHR())
 file(key..'-oam.bin',bytes(0,256,emu.memType.nesSpriteRam))
 file(key..'-palette.bin',bytes(0x3f00,32,emu.memType.nesPpuDebug))
 file(key..'-nametable.bin',bytes(0x2000,1024,emu.memType.nesPpuDebug))
end
emu.addMemoryCallback(function(a,v)mask=v end,emu.callbackType.write,0x2001)
emu.addEventCallback(function()
 local b={};local menu=r('CrossoverMenuState')
 if phase==2 then
  if frame-rapidStart>=600 then finish();return end
  if frame%2==0 then
   local sequence={'right','down','select','left','up','select','right'}
   b[sequence[((frame-rapidStart)//2)%#sequence+1]]=true
  end
  emu.setInput(b,0);return
 end
 if frame%12~=0 or frame<156 then emu.setInput(b,0);return end
 if phase==0 then
  if OUTLINES and r('PlayerOutlinesOff')~=0 then
   if menu==0 then if r('CrossoverOptionsFocus')==0 then b.down=true else b.a=true end
   elseif menu==4 then if r('CrossoverOptionsFocus')==0 then b.a=true else b.up=true end end
  elseif menu==4 then b.b=true
  elseif menu==0 then if r('CrossoverOptionsFocus')~=0 then b.up=true else b.a=true end
  elseif menu==2 then phase=1;browsing=true end
 elseif phase==1 then
  local case=CASES[which];local index=r('CrossoverMenuIndex')
  local row=index<12 and index//6 or 2;local wanted=case[2]<12 and case[2]//6 or 2
  if row~=wanted then b.down=true;settled=0
  elseif index~=case[2] then b.right=true;settled=0
  elseif case[4]~=0 and emu.read(case[4],emu.memType.nesDebug)~=case[5]then b.select=true;settled=0
  elseif r('SelectedCharacter')~=case[3] then settled=0
  else
   settled=settled+1
   if settled>=4 then capture(case);which=which+1;settled=0 end
  end
  if which>#CASES then
   if RAPID then phase=2;rapidStart=frame else finish()end
  end
 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if browsing and (mask&0x18)~=0x18 then blankFrames=blankFrames+1 end
 if browsing and trace then
  for page=0,3 do
   local physical=emu.convertAddress(page*1024,emu.memType.nesPpuMemory).address
   assert(physical==4096+page*1024,'Portrait selection changed a background CHR bank')
  end
  trace:write(string.pack('<I4I2BB',frame,r('CrossoverMenuIndex'),mask,r('M3CacheProfile')),
              bytes(0,256,emu.memType.nesSpriteRam),
              bytes(0x1000,1024,emu.memType.nesPpuDebug),
              bytes(0x3f00,32,emu.memType.nesPpuDebug))
 end
 if frame>18000 then error('menu walk timed out at identity '..which..', state '..r('CrossoverMenuState'))end
end,emu.eventType.endFrame)
'''


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--outlines',action='store_true')
    parser.add_argument('--trace',action='store_true',help='Record every browsing frame for pixel-level corruption checks')
    parser.add_argument('--rapid',action='store_true',help='Follow the complete menu walk with 600 frames of rapid input')
    args=parser.parse_args();rom=args.rom.resolve();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    labels={m[2]:int(m[1],16)for line in rom.with_suffix('.lbl').read_text().splitlines()
            if(m:=re.fullmatch(r'al ([0-9a-fA-F]+) \.(\S+)',line))}
    cases=[[name,slot,char,labels[var]if var else 0,value]for name,slot,char,var,value in CASES]
    header=rom.read_bytes()[:16];mapper=(header[6]>>4)|(header[7]&0xf0)
    constants='SOURCE_MMC5='+str(mapper==5).lower()+'\nRAPID='+str(args.rapid).lower()+'\nTRACE='+str(args.trace).lower()+'\nOUTLINES='+str(args.outlines).lower()+'\nCASES={\n'
    constants+='\n'.join(' {'+','.join(json.dumps(value)for value in case)+'},'for case in cases)+'\n}\n'
    script=out/'menu-walk.lua';script.write_text(constants+LUA)
    spec=importlib.util.spec_from_file_location('menu_mesen',ROOT/'tools/run_mesen.py')
    runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner);runner.ROOT=out
    result=runner.run(script,rom,timeout=90,
                      emulator_options=['--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false'])
    report=dict(rom=str(rom),ROM_sha256=hashlib.sha256(rom.read_bytes()).hexdigest(),
                outlines=args.outlines,identities=cases,exit=result)
    (out/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    return result


if __name__=='__main__':raise SystemExit(main())
