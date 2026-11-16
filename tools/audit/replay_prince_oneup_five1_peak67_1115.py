"""Use the authenticated action4 peak and observe actual contact boxes."""
from functools import lru_cache
import replay_prince_oneup_five1_contact67_1115 as Previous
from replay_prince_natural_stock_40a_1115 import LuaRuntime

C,PIN=Previous.C,Previous.PIN

@lru_cache(maxsize=1)
def controller(raw,mode='oneup',jump=8):
    text=Previous.controller(raw,mode,jump)
    assert C.digest(text.encode())=='4aa2785760ac1aa4c90fd66a7875e97a5374bccf11ff108fbcb97ce80bba15f5'
    old='gap>=70 and gap<=90';assert text.count(old)==1;text=text.replace(old,'gap>=116 and gap<=124',1)
    # Read-only boxes are observed at the existing first injury writer.
    old="local cpu=emu.getState();stock.stage2_hp_writes[#stock.stage2_hp_writes+1]={reported_PC=cpu['cpu.pc'],SP=cpu['cpu.sp'],before=source(0x6cf),after=value,state=stockState(),actors=stage2Actors(),phase=stock.phase}"
    new="""local cpu=emu.getState();local p=STOCK.ram.BoundingBox_UL_XPos;local boxes={}
 for i=0,5 do local e=stockActor(i);if e.flag~=0 then local b=p+4*(i+1);boxes[#boxes+1]={slot=i,id=e.id,x=e.x,y=e.y,box={read(b),read(b+1),read(b+2),read(b+3)}}end end
 local owner=emu.convertAddress(cpu['cpu.pc'])
 stock.stage2_hp_writes[#stock.stage2_hp_writes+1]={reported_PC=cpu['cpu.pc'],SP=cpu['cpu.sp'],mapped=owner,before=source(0x6cf),after=value,state=stockState(),actors=stage2Actors(),phase=stock.phase,player_box={read(p),read(p+1),read(p+2),read(p+3)},enemy_boxes=boxes}"""
    assert text.count(old)==1;text=text.replace(old,new,1)
    LuaRuntime().compile(text);return text

def metadata(raw,mode='oneup',jump=8):
    q=Previous.metadata(raw,mode,jump);q.update(Lua_SHA256=C.digest(controller(raw,mode,jump).encode()),
        enemy_gap_window=[116,124],basis='Action4 authored peak42 lies between actual early contact40 and late contact43',
        read_only_native_boxes_at_original_injury_writer=True)
    return q
