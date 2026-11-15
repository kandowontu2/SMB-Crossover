"""Same controls with immutable first hidden-solid point and consumer latches."""
from functools import lru_cache
import replay_prince_hidden_backtrack_trace_174fa_1115 as Previous
from replay_prince_natural_stock_40a_1115 import LuaRuntime

C,N,W,PIN=Previous.C,Previous.N,Previous.W,Previous.PIN

@lru_cache(maxsize=1)
def controller(raw,mode='oneup',jump=8):
    text=Previous.controller(raw,mode,jump)
    assert C.digest(text.encode())=='7e9ff5d67463e071556fbae13b42c0449d0b097eefe999238145faf3b74138e3'
    def change(a,b):
        nonlocal text
        assert text.count(a)==1,a[:100];text=text.replace(a,b,1)
    change('stock.wall_points={};stock.material_returns={}',
        'stock.wall_points={};stock.material_returns={};stock.hidden_points={}')
    old="q.attribute=read(0xef36+q.A)\n"
    new=r'''q.attribute=read(0xef36+q.A)
  if(q.A==95 or q.A==96)and #stock.hidden_points<4 then
   q.attribute_mapping=emu.convertAddress(0xef36+q.A);q.cell_x=q.query_x&65520;q.cell_y=q.query_y&240
   q.consumer_mapping=emu.convertAddress(ret.pc);q.projection_width=source(0x70f);q.source_foot_x=source(0x4bc);q.source_body_y=source(0x6f1);q.source_body_width=source(0x4c3)
   q.native_bbox_cache={read(STOCK.ram.BoundingBox_UL_XPos),read(STOCK.ram.BoundingBox_UL_XPos+1),read(STOCK.ram.BoundingBox_UL_XPos+2),read(STOCK.ram.BoundingBox_UL_XPos+3)}
   stock.hidden_points[#stock.hidden_points+1]=q
  end
'''
    change(old,new)
    old=' if #stock.material_returns>8 then table.remove(stock.material_returns,1)end\n'
    new=r''' if not stock.first_hidden_material and cpu['cpu.a']==20 then
  local points={};for _,q in ipairs(stock.hidden_points)do if q.state.Prince_returns==stock.prince_returns then points[#points+1]=q end end
  if #points>0 then stock.first_hidden_material={material=stock.material_returns[#stock.material_returns],hidden_points=points,consumer_mapping=emu.convertAddress(caller)}end
 end
 if #stock.material_returns>8 then table.remove(stock.material_returns,1)end
'''
    change(old,new)
    LuaRuntime().compile(text);return text

def metadata(raw,mode='oneup',jump=8):
    return dict(ROM_SHA256=PIN,Lua_SHA256=C.digest(controller(raw,mode,jump).encode()),required_native_variant=3,
        typed_174fa_actual_execution=True,all_52_Bub_bytes_preserved=True,ordinary_controls_unchanged=True,
        first_5F_60_points_and_matching_kind20_latched=True,diagnostic_only=True,no_gameplay_seeds=True,native_ready=False,outputs=0,Mesen=False)
