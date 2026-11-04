"""Prepare a controller-only Roll smoke test for the shared dispatch repair."""
import argparse
from pathlib import Path
import subprocess
import sys

from check_tmnt_render_oa import location
from observe_chip_committed_write import lua
from prepare_mini_mario_native_power_1103_v56 import address, bundle
from prepare_selected_native_packet_v1 import R, prepare, sha


OBSERVER = r'''
local frame, updates, calls, returns, pads, peak = 0,0,0,0,0,0
local entered, done, pending = false,false,nil
local callbacks = {}
local function read(a) return emu.read(a,emu.memType.nesDebug) end
local function r(name) return read(L[name]) end
local function json(v)
 if type(v)=='table' then local t={};for k,x in pairs(v)do t[#t+1]=string.format('%q',k)..':'..json(x)end;return '{'..table.concat(t,',')..'}'end
 if type(v)=='string'then return string.format('%q',v)end
 return tostring(v)
end
local function finish(ok,why)
 if done then return end;done=true
 local q={passed=ok,reason=why,ROM_sha256=C.ROM_sha256,controller_only=true,
  script_RAM_writes=false,physical_frames=frame,updates=updates,
  weapon_calls=calls,weapon_returns=returns,protected_pad_entries=pads,
  peak_projectiles=peak,health=r('RlHealth'),energy=r('RlEnergy')}
 local f=assert(io.open(OUTPUT..'result.json','w'));f:write(json(q)..'\n');f:close()
 if ok then local p=assert(io.open(OUTPUT..'roll-weapons.png','wb'));p:write(emu.takeScreenshot());p:close()end
 print(ok and 'PASS Roll cold menu and native weapon loop' or why);emu.stop(ok and 0 or 1)
end
local function guard(fn)return function(...)
 if done then return end;local ok,why=pcall(fn,...);if not ok then finish(false,tostring(why))end
end end
local function check(ok,why)assert(ok,why)end
local function mapped(pc,bank)
 local p=emu.convertAddress(pc)
 return p and p.memType==emu.memType.nesPrgRom and p.address==bank*8192+(pc&8191)
end
emu.addMemoryCallback(guard(function()
 if not entered or not mapped(C.weapon_pc,C.weapon_bank)then return end
 check(not pending,'Previous Roll weapon call completed');calls=calls+1
 local state=emu.getState();local sp=state['cpu.sp']
 local ret=(read(256+((sp+1)&255))+256*read(256+((sp+2)&255))+1)&65535
 local p=assert(emu.convertAddress(ret));pending={pc=ret,sp=(sp+2)&255,memory=p.memType,physical=p.address}
 if not callbacks[ret]then callbacks[ret]=true;emu.addMemoryCallback(guard(function()
  if not pending then return end
  local s=emu.getState();local a=emu.convertAddress(s['cpu.pc'])
  if s['cpu.pc']==pending.pc and s['cpu.sp']==pending.sp and a and a.memType==pending.memory and a.address==pending.physical then
   returns=returns+1;pending=nil
  end
 end),emu.callbackType.exec,ret)end
end),emu.callbackType.exec,C.weapon_pc)
emu.addMemoryCallback(guard(function()
 if not entered or not mapped(0xb53a,79)then return end
 check(read(0xb53a)==0x4c and read(0xb53b)==0x4c and read(0xb53c)==0xb5,'Roll skips the reused padding through its native continuation')
 pads=pads+1
end),emu.callbackType.exec,0xb53a)
emu.addMemoryCallback(guard(function()
 if not mapped(C.game_pc,C.game_bank)or r('OperMode')~=1 or r('OperMode_Task')~=3 or r('GameEngineSubroutine')~=8 then return end
 check(r('SelectedCharacter')==9 and r('RlVariant')==1,'Actual cold-selected Roll')
 entered=true;updates=updates+1
 local n=0;for i=0,3 do if read(L.MmBulletType+i)~=0 then n=n+1 end end;peak=math.max(peak,n)
 check(r('RlHealth')==28 and r('RlEnergy')==28,'Idle free buster retains Roll health and energy')
end),emu.callbackType.exec,C.game_pc)
emu.addEventCallback(guard(function()
 local keys={}
 if not entered and frame>=120 and frame%12==0 then
  if r('CrossoverMenuState')~=2 then keys.start=true
  elseif r('CrossoverMenuIndex')<6 then keys.down=true
  elseif r('CrossoverMenuIndex')~=9 then keys.right=true
  elseif r('RlVariant')~=1 then keys.select=true
  else keys.a=true end
 elseif entered and updates%24<4 then keys.b=true end
 emu.setInput(keys,0)
end),emu.eventType.inputPolled)
emu.addEventCallback(guard(function()
 frame=frame+1;check(frame<2400,'Bounded Roll cold launch and weapon smoke')
 if updates>=120 then
  check(calls>=100 and returns>=99 and pads>=99,'Actual Roll weapon loops return through the protected continuation')
  check(peak>0,'Real B presses create Roll projectiles')
  finish(true,'Cold menu, free buster and native weapon tail pass')
 end
end),emu.eventType.endFrame)
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    image = bundle(args.rom.read_bytes())
    names = ['SelectedCharacter', 'OperMode', 'OperMode_Task', 'GameEngineSubroutine',
             'CrossoverMenuState', 'CrossoverMenuIndex', 'RlVariant', 'RlHealth',
             'RlEnergy', 'MmBulletType']
    config = dict(ROM_sha256=sha(args.rom), weapon_pc=address(image, 'RlWeapons'),
                  weapon_bank=(location(image, 'RlWeapons')-16)//8192,
                  game_pc=address(image, 'GameCoreRoutine'),
                  game_bank=(location(image, 'GameCoreRoutine')-16)//8192)
    text = 'local L='+lua({name:address(image,name) for name in names})
    text += '\nlocal C='+lua(config)+'\n'+OBSERVER
    prepare(args.output, args.rom, text, [Path(__file__)],
            expected=config['ROM_sha256'], timeout=120, allow_interactive=True,
            scope='Controller-only cold menu Roll selection, 120 active updates, free buster, '
                  'actual weapon entry/return and protective padding jump. One PNG. No RAM seeds.')
    return subprocess.call([sys.executable, '-B', args.output/'run.py'])


if __name__ == '__main__':
    raise SystemExit(main())
