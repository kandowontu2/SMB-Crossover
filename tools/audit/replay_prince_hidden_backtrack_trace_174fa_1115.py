"""Read-only first cap-flight backtrack and actual hidden-block terrain calls."""
from functools import lru_cache
import current_prince_stock_174fa_1115 as Current
import replay_prince_hidden_mount_fresh_A_40a_1115 as Previous
from replay_prince_natural_stock_40a_1115 import lua,LuaRuntime

C,N,W,PIN=Current.C,Current.N,Current.W,Current.PIN

@lru_cache(maxsize=1)
def controller(raw,mode='oneup',jump=8):
    assert mode=='oneup'and jump==8
    parent=Current.reference(raw);text=Current.bind(Previous.controller(parent,mode,jump),raw,parent)
    parts=C.Packet.extract(raw)[1]
    def hook(pc,size=8):return dict(pc=pc,address=3*8192+(pc&8191),bytes=list(parts[0][pc-0xa000:pc-0xa000+size]),private=True)
    assert parts[0][0x1f9c:0x1fa0]==bytes.fromhex('ad9fc060')
    observer=r'''
stock.wall_points={};stock.material_returns={}
local function nearFlight()
 local s=stockState();return stock.phase=='standing-flight'and s.x>=980 and s.x<1040 and not stock.first_backtrack
end
stockHook(@POINT@,function(cpu)
 if not nearFlight()then return end
 local q={PC=cpu['cpu.pc'],SP=cpu['cpu.sp'],query_x=source(0x1369,3)+256*source(0x136a,3),query_y=source(0x136b,3),source_row=source(0x7c),source_cell=source(0x7d)+256*source(0x7e),state=stockState()}
 stockReturn(cpu,function(ret,returned)
  q.return_PC=ret.pc;q.return_SP=ret.sp;q.A=returned['cpu.a'];q.X=returned['cpu.x'];q.Y=returned['cpu.y'];q.P=returned['cpu.ps']or returned['cpu.p'];q.attribute=read(0xef36+q.A)
  stock.wall_points[#stock.wall_points+1]=q;if #stock.wall_points>8 then table.remove(stock.wall_points,1)end
 end)
end)
stockHook(@RETURN@,function(cpu)
 if not nearFlight()then return end
 local sp=cpu['cpu.sp'];local caller=(read(0x100+((sp+1)&255))+256*read(0x100+((sp+2)&255))+1)&65535
 stock.material_returns[#stock.material_returns+1]={PC=cpu['cpu.pc'],SP=sp,caller=caller,A=cpu['cpu.a'],P=cpu['cpu.ps']or cpu['cpu.p'],kind=source(0x9f),surface=source(0x7f)+256*source(0x80),source_cell=source(0x7d)+256*source(0x7e),source_row=source(0x7c),state=stockState()}
 if #stock.material_returns>8 then table.remove(stock.material_returns,1)end
end)
local function captureBacktrack(kind,at,value)
 if not nearFlight()then return end
 local s=stockState();if s.x<1000 or s.x>=1033 then return end
 local before=kind=='source'and(source(0x60f)+256*source(0x610))or s.x
 local after=value+256*(kind=='source'and source(0x610)or read(0x5c));local delta=after-before
 if delta> -8 or delta< -64 then return end
 local cpu=emu.getState();local pc=cpu['cpu.pc'];local bytes={};for i=-1,6 do bytes[#bytes+1]=read(pc+i)end
 local points={};for _,q in ipairs(stock.wall_points)do points[#points+1]=q end
 local materials={};for _,q in ipairs(stock.material_returns)do materials[#materials+1]=q end
 stock.first_backtrack={kind=kind,at=at,before=before,after=after,delta=delta,reported_PC=pc,opcode_PC=pc-1,SP=cpu['cpu.sp'],A=cpu['cpu.a'],X=cpu['cpu.x'],Y=cpu['cpu.y'],map=emu.convertAddress(pc),bytes=bytes,state=s,source_actor_y=source(0x611),points=points,materials=materials,hidden_tile=tile(1024,128),hidden_attribute=read(0xef36+96)}
end
emu.addMemoryCallback(guarded(function(at,value)if mapped(0xc60f,2)then captureBacktrack('source',at,value)end end),emu.callbackType.write,0xc60f)
emu.addMemoryCallback(guarded(function(at,value)captureBacktrack('native',at,value)end),emu.callbackType.write,0x75)
'''.replace('@POINT@',lua(hook(0xb310))).replace('@RETURN@',lua(hook(0xbf9f,4)))
    old='local function naturalStockTick()\n';assert text.count(old)==1
    text=text.replace(old,observer+'\n'+old+" if stock.first_backtrack then final=stockState();finish(false,'Diagnostic complete: first actual cap-flight backtrack writer and point results');return true end\n",1)
    LuaRuntime().compile(text);return text

def metadata(raw,mode='oneup',jump=8):
    return dict(ROM_SHA256=PIN,Lua_SHA256=C.digest(controller(raw,mode,jump).encode()),required_native_variant=3,
        typed_174fa_to_40a_binding_only=True,actual_CPU_preserves_all_52_Bub_bytes=True,
        ordinary_fresh_A_inputs_unchanged=True,diagnostic_only=True,no_gameplay_seeds=True,native_ready=False,outputs=0,Mesen=False)
