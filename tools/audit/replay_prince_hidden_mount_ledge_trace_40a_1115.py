"""Read-only first hanging-mode writer and actual cap terrain queries."""
from functools import lru_cache
import replay_prince_hidden_mount_standing_40a_1115 as Previous
from replay_prince_natural_stock_40a_1115 import lua,LuaRuntime

C,N,W,PIN=Previous.C,Previous.N,Previous.W,Previous.PIN

@lru_cache(maxsize=1)
def controller(raw,mode='oneup',jump=8):
    text=Previous.controller(raw,mode,jump);parts=C.Packet.extract(raw)[1];pc=0xb310
    hook=dict(pc=pc,address=3*8192+(pc&8191),bytes=list(parts[0][pc-0xa000:pc-0xa000+8]),private=True)
    observer=r'''
stock.last_points={}
stockHook(@HOOK@,function(cpu)
 if not stock.active or stock.ledge_writer then return end
 local q={PC=cpu['cpu.pc'],SP=cpu['cpu.sp'],query_x=source(0x1369,3)+256*source(0x136a,3),query_y=source(0x136b,3),source_row=source(0x7c),source_cell=source(0x7d)+256*source(0x7e),source_actor_x=source(0x60f)+256*source(0x610),source_actor_y=source(0x611),state=stockState()}
 stockReturn(cpu,function(ret,returned)
  q.return_PC=ret.pc;q.return_SP=ret.sp;q.A=returned['cpu.a'];q.X=returned['cpu.x'];q.Y=returned['cpu.y'];q.P=returned['cpu.ps']or returned['cpu.p']
  q.surface=source(0x7f)+256*source(0x80);q.source_kind=source(0x9f)
  stock.last_points[#stock.last_points+1]=q;if #stock.last_points>8 then table.remove(stock.last_points,1)end
 end)
end)
emu.addMemoryCallback(guarded(function(at,value)
 if not stock.active or stock.ledge_writer or value~=2 or source(0x616)~=8 or not mapped(0xc618,2)then return end
 local cpu=emu.getState();local pc=cpu['cpu.pc'];local map=emu.convertAddress(pc);local bytes={}
 for i=-1,6 do bytes[#bytes+1]=read(pc+i)end
 local points={};for _,q in ipairs(stock.last_points)do points[#points+1]=q end
 stock.ledge_writer={reported_PC=pc,opcode_PC=pc-1,SP=cpu['cpu.sp'],A=cpu['cpu.a'],X=cpu['cpu.x'],Y=cpu['cpu.y'],map=map,bytes=bytes,before=source(0x618),value=value,state=stockState(),points=points}
end),emu.callbackType.write,0xc618)
'''.replace('@HOOK@',lua(hook))
    old='local function naturalStockTick()\n';assert text.count(old)==1
    trace=r''' if stock.ledge_writer then final=stockState();finish(false,'Diagnostic complete: first actual action8 mode2 writer and terrain queries');return true end
 if stock.active and not stock.cap_tiles then
  stock.cap_tiles={};for _,y in ipairs({96,112,128,144})do for _,x in ipairs({912,928,944})do stock.cap_tiles[#stock.cap_tiles+1]={x=x,y=y,tile=tile(x,y)}end end
  stock.cap_tiles[#stock.cap_tiles+1]={x=1024,y=128,tile=tile(1024,128)}
 end
'''
    text=text.replace(old,observer+'\n'+old+trace,1)
    LuaRuntime().compile(text);return text

def metadata(raw,mode='oneup',jump=8):
    return dict(ROM_SHA256=PIN,Lua_SHA256=C.digest(controller(raw,mode,jump).encode()),required_native_variant=3,
        ordinary_controls_unchanged=True,diagnostic_only=True,first_mode2_writer_and_last8_actual_PointRead_calls=True,
        no_gameplay_seeds=True,native_ready=False,outputs=0,Mesen=False)
