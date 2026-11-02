"""Observe actual Metal draw/reservation ordering without changing game memory."""
import re
from pathlib import Path
from prepare_selected_native_packet_v1 import R, prepare, sha

O = R / 'build/metal-oam-order-1102-v2'
P = R / 'build/metal-graphics-diagnostic-1102-v1/native'
S = R / 'build/metal-storm-idle-shots-1101-v41'
ROM = R / 'build/excitebike-pose-1101-v3/current4.nes'


def main():
    O.mkdir(exist_ok=True)
    labels = {n: int(a, 16) for a, n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',
                                                 (S / 'component.lbl').read_text(), re.M)}
    constants = '\n'.join(f'local {n}={labels[n]}' for n in ['MsEmitPacket', 'MsRBody'])
    observer = r'''
local order={};local orderCounts={};local badAlignment={}
local function record(name)
 if phase~='idle' and phase~='walk' then return end
 if r('SelectedCharacter')~=35 then return end
 orderCounts[name]=(orderCounts[name]or 0)+1
 local off=r('CurrentOAMOffset')
 if (off&3)~=0 then badAlignment[name]=(badAlignment[name]or 0)+1 end
 if orderCounts[name]>3 then return end
 local p=r('SmPosePtr')+256*r('SmPosePtr',1)
 local packet=r('R0')+256*r('R1')
 order[#order+1]=string.format('{"name":%q,"frame":%d,"epoch":%d,"oam_offset":%d,"rotation":%d,"guest_rotation":%d,"player_start":%d,"pose_pointer":%d,"pose_length":%d,"packet":%d,"packet_length":%d,"r4_7":[%d,%d,%d,%d]}',name,frame,r('FrameCounter'),off,r('RgOamRotation'),r('GuestOamRotationActive'),r('RgOamPlayerStart'),p,emu.read(p,emu.memType.nesDebug),packet,emu.read(packet,emu.memType.nesDebug),r('R4'),r('R5'),r('R6'),r('R7'))
end
for name,at in pairs({draw_entry=MsRenderDraw,body_entry=MsRBody,emit_entry=MsEmitPacket})do
 emu.addMemoryCallback(function()if r('CurrentBankC')==2 then record(name)end end,emu.callbackType.exec,at)
end
for name,label in pairs({reservation='RosterProjectileOamReady',native_render='MetaspriteRenderLoop'})do
 emu.addMemoryCallback(function()if r('CurrentBank')==132 then record(name)end end,emu.callbackType.exec,assert(L[label],label))
end
'''
    text = (P / 'controller.lua').read_text(encoding='utf-8')
    marker = 'local function finish(reason)'
    assert text.count(marker) == 1
    text = text.replace(marker, constants + '\n' + observer + '\n' + marker)
    text = text.replace('dmas~=120 and dmas~=200', 'dmas~=30 and dmas~=70')
    marker = ' emu.stop(passed and 0 or 1)'
    assert text.count(marker) == 1
    text = text.replace(marker, '''
 local ac={};for k,v in pairs(orderCounts)do ac[#ac+1]=string.format('%q:%d',k,v)end
 local bc={};for k,v in pairs(badAlignment)do bc[#bc+1]=string.format('%q:%d',k,v)end
 local f=assert(io.open(OUTPUT..'ordering.json','w'));f:write(string.format('{"counts":{%s},"misaligned":{%s},"first_events":[%s]}',table.concat(ac,','),table.concat(bc,','),table.concat(order,',')));f:close()
 emu.stop(passed and 0 or 1)''')
    prepare(O / 'native', ROM, text, [Path(__file__), P / 'controller.lua',
            S / 'component.lbl', S / 'component.s'], expected=sha(ROM), timeout=90,
            allow_interactive=True,
            scope='Exact cf passive actual draw/reservation ordering and alignment counters. '
                  'At most three events per entry and three DMA snapshots in small JSON receipts; '
                  'one PNG, no emulated writes, no graphical success claim.')


if __name__ == '__main__':
    main()
