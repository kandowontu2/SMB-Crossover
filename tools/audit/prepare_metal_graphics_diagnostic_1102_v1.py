"""Observe current Metal cached graphics, pointer lifetime, CHR and OAM."""
import json
import re
from pathlib import Path
from prepare_selected_native_packet_v1 import R, prepare, sha

O = R / 'build/metal-graphics-diagnostic-1102-v1'
P = R / 'build/empty-screen-lag-1102-v1/metal-storm'
S = R / 'build/metal-storm-idle-shots-1101-v41'
ROM = R / 'build/excitebike-pose-1101-v3/current4.nes'


def main():
    O.mkdir(exist_ok=True)
    labels = {n: int(a, 16) for a, n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',
                                                 (S / 'component.lbl').read_text(), re.M)}
    constants = '\n'.join(f'local {n}={labels[n]}' for n in ['MsRenderDraw', 'MsRenderGraphics', 'MsRenderColors'])
    observer = r'''
local graphics={};local counts={draw=0,graphics=0,colors=0};local dmas=0
local chr,upper={},0
local function physical(off)return emu.read(2*8192+off,emu.memType.nesWorkRam)end
local function header(bank)
 local a={};for i=0,15 do a[#a+1]=string.format('%02x',emu.read(bank*8192+0x1fe0+i,emu.memType.nesWorkRam))end
 return table.concat(a,'')
end
emu.addMemoryCallback(function(_,v)upper=(v&3)*256 end,emu.callbackType.write,0x5130)
emu.addMemoryCallback(function(at,v)chr[at-0x5120]=v+upper end,emu.callbackType.write,0x5120,0x512b)
for name,at in pairs({draw=MsRenderDraw,graphics=MsRenderGraphics,colors=MsRenderColors})do
 emu.addMemoryCallback(function()if (phase=='idle' or phase=='walk')and r('SelectedCharacter')==35 and r('CurrentBankC')==2 then counts[name]=counts[name]+1 end end,emu.callbackType.exec,at)
end
emu.addMemoryCallback(function(_,page)
 if phase~='idle' and phase~='walk' then return end
 dmas=dmas+1
 if dmas~=1 and dmas~=120 and dmas~=200 then return end
 local p=r('SmPosePtr')+256*r('SmPosePtr',1)
 local cells={};for i=0,252,4 do
  local at=page*256+i;local y=emu.read(at,emu.memType.nesDebug)
  if y<240 then cells[#cells+1]=string.format('[%d,%d,%d,%d]',y,emu.read(at+1,emu.memType.nesDebug),emu.read(at+2,emu.memType.nesDebug),emu.read(at+3,emu.memType.nesDebug))end
 end
 local pages={};for i=0,11 do pages[#pages+1]=chr[i]or-1 end
 graphics[#graphics+1]=string.format('{"frame":%d,"phase":%q,"native_x":%d,"native_y":%d,"native_rel_x":%d,"native_rel_y":%d,"ObjectMetasprite":%d,"SmPosePtr":%d,"pointer_logical_byte":%d,"pointer_physical_C2_byte":%d,"raw_A":%d,"raw_C":%d,"C2_header":%q,"C3_header":%q,"source_x":%d,"source_y":%d,"source_active":%d,"source_pose":%d,"source_frame":%d,"CHR":[%s],"visible_OAM":[%s]}',frame,phase,wx(),r('Player_Y_Position'),r('Player_Rel_XPos'),r('Player_Rel_YPos'),r('ObjectMetasprite'),p,emu.read(p,emu.memType.nesDebug),physical(p&8191),r('CurrentBank'),r('CurrentBankC'),header(2),header(3),physical(0x480),physical(0x4b0),physical(0x510),physical(0x4e0),physical(0x4f8),table.concat(pages,','),table.concat(cells,','))
end,emu.callbackType.write,0x4014)
'''
    text = (P / 'controller.lua').read_text(encoding='utf-8')
    marker = 'local function finish(reason)'
    assert text.count(marker) == 1
    text = text.replace(marker, constants + '\n' + observer + '\n' + marker)
    marker = ' out:close();emu.stop(passed and 0 or 1)'
    assert text.count(marker) == 1
    text = text.replace(marker, ''' out:close()
 local g=assert(io.open(OUTPUT..'graphics.json','w'));g:write(string.format('{"counts":{"draw":%d,"graphics":%d,"colors":%d},"samples":[%s]}',counts.draw,counts.graphics,counts.colors,table.concat(graphics,',')));g:close()
 emu.stop(passed and 0 or 1)''')
    prepare(O / 'native', ROM, text, [Path(__file__), P / 'controller.lua', P / 'capture/result.json',
            S / 'component.lbl', S / 'component.s'], expected=sha(ROM), timeout=90,
            allow_interactive=True,
            scope='Exact current cf. Passive bank-qualified Metal renderer entries and three DMA OAM/CHR/header '
                  'snapshots using physical nesWorkRam for cache fields. Same empty opening controller, '
                  'one PNG, no emulated writes or rendering completion claim.')


if __name__ == '__main__':
    main()
