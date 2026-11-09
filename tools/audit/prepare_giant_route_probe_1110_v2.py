"""Add exact stop/impede/crush witnesses to the unchanged route probe."""
from pathlib import Path
import prepare_giant_route_probe_1110 as P

original=P.prepare


def instrument(output,rom,source,refs,**options):
 source=source.replace('local probe,lastProbe={},-1','local events={}\nlocal probe,lastProbe={},-1',1)
 source=source.replace('terminal=state(),probe=probe,','terminal=state(),events=events,probe=probe,',1)
 at=source.index('hook(C.main,')
 source=source[:at]+'''local function witness(kind)
 if x()<2370 or x()>2600 or #events>=200 then return end
 local row=state();local cpu=emu.getState();row.kind=kind
 row.vx=r('Player_X_Speed');row.vy=r('Player_Y_Speed');row.yp=r('Player_Y_HighPos')
 row.a=cpu['cpu.a'];row.cx=cpu['cpu.x'];row.cy=cpu['cpu.y'];row.pc=cpu['cpu.pc']
 row.zp={};for i=0,11 do row.zp[#row.zp+1]=ram(i) end
 row.stack={};for i=1,6 do row.stack[#row.stack+1]=ram(256+((cpu['cpu.sp']+i)&255)) end
 row.pointer=ram(9)+256*ram(10); row.tile=ram(row.pointer+ram(5))
 events[#events+1]=row
end
hook(0x9d20,emu.memType.nesPrgRom,126*8192+(0x9d20&8191),function() witness('StopPlayerMove') end)
hook(0x9de5,emu.memType.nesPrgRom,126*8192+(0x9de5&8191),function() witness('ImpedePlayerMove') end)
hook(0xb174,emu.memType.nesPrgRom,90*8192+(0xb174&8191),function() witness('GiantCrushAsBrick') end)
''' + source[at:]
 return original(output,rom,source,refs|{Path(__file__)},**options)


P.prepare=instrument
if __name__=='__main__':P.main()
