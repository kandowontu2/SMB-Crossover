"""Bind hidden point, Wall increment and kind20 to one material invocation."""
from functools import lru_cache
import replay_prince_hidden_falsewall_latch_174fa_1115 as Previous
from replay_prince_natural_stock_40a_1115 import lua,LuaRuntime

C,N,W,PIN=Previous.C,Previous.N,Previous.W,Previous.PIN

@lru_cache(maxsize=1)
def controller(raw,mode='oneup',jump=8):
    text=Previous.controller(raw,mode,jump)
    assert C.digest(text.encode())=='9eecbc04c511c30ee7e3993b1a076af52da40ba8e9557b44f73fc39b4ef5cc0d'
    def change(a,b):
        nonlocal text
        assert text.count(a)==1,a[:100];text=text.replace(a,b,1)
    change("local q={PC=cpu['cpu.pc'],SP=cpu['cpu.sp'],query_x=",
        "local q={material_serial=stock.material_active and stock.material_serial or 0,PC=cpu['cpu.pc'],SP=cpu['cpu.sp'],query_x=")
    change('if(q.A==95 or q.A==96)and #stock.hidden_points<4 then',
        'if(q.A==95 or q.A==96)then')
    change('   stock.hidden_points[#stock.hidden_points+1]=q\n',
        '   stock.latest_hidden=q;if #stock.hidden_points<4 then stock.hidden_points[#stock.hidden_points+1]=q end\n')
    old=""" if not stock.first_hidden_material and cpu['cpu.a']==20 then
  local points={};for _,q in ipairs(stock.hidden_points)do if q.state.Prince_returns==stock.prince_returns then points[#points+1]=q end end
  if #points>0 then stock.first_hidden_material={material=stock.material_returns[#stock.material_returns],hidden_points=points,consumer_mapping=emu.convertAddress(caller)}end
 end
"""
    new=r''' local point=stock.latest_hidden
 if not stock.first_hidden_material and cpu['cpu.a']==20 and point and point.material_serial==stock.material_serial then
  stock.first_hidden_material={material_serial=stock.material_serial,material=stock.material_returns[#stock.material_returns],hidden_point=point,consumer_mapping=emu.convertAddress(caller),wall_increment=stock.first_hidden_wall_increment}
 end
 stock.material_active=false
'''
    change(old,new)
    part=C.Packet.extract(raw)[1][0];pc=0xbde5
    entry=dict(pc=pc,address=3*8192+(pc&8191),bytes=list(part[pc-0xa000:pc-0xa000+8]),private=True)
    observer=r'''
stock.material_serial=0
stockHook(@ENTRY@,function(cpu)
 if not nearFlight()then return end
 stock.material_serial=stock.material_serial+1;stock.material_active=true
end)
emu.addMemoryCallback(guarded(function(at,value)
 if not nearFlight()or stock.first_hidden_wall_increment or value~=1 or source(0x8c)~=0 or not mapped(0xc08c,2)then return end
 local q=stock.latest_hidden;if not q or q.material_serial~=stock.material_serial then return end
 local cpu=emu.getState();local pc=cpu['cpu.pc'];local bytes={};for i=-1,6 do bytes[#bytes+1]=read(pc+i)end
 stock.first_hidden_wall_increment={material_serial=stock.material_serial,PC=pc-1,reported_PC=pc,SP=cpu['cpu.sp'],A=cpu['cpu.a'],X=cpu['cpu.x'],Y=cpu['cpu.y'],map=emu.convertAddress(pc),bytes=bytes,before=source(0x8c),value=value,state=stockState(),hidden_point=q}
end),emu.callbackType.write,0xc08c)
'''.replace('@ENTRY@',lua(entry))
    change('local function naturalStockTick()\n',observer+'\nlocal function naturalStockTick()\n')
    LuaRuntime().compile(text);return text

def metadata(raw,mode='oneup',jump=8):
    return dict(ROM_SHA256=PIN,Lua_SHA256=C.digest(controller(raw,mode,jump).encode()),required_native_variant=3,
        typed_174fa_actual_execution=True,all_52_Bub_bytes_preserved=True,ordinary_controls_unchanged=True,
        exact_material_invocation_hidden_point_wall_increment_kind20=True,diagnostic_only=True,no_gameplay_seeds=True,native_ready=False,outputs=0,Mesen=False)
