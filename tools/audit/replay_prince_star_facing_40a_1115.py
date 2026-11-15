"""Grounded Star alignment with actual facing before original careful steps."""
from functools import lru_cache
import replay_prince_star_careful_40a_1115 as Previous

C,N,W,PIN=Previous.C,Previous.N,Previous.W,Previous.PIN

@lru_cache(maxsize=1)
def controller(raw,mode='star',jump=8):
    text=Previous.controller(raw,mode,jump)
    def change(a,b):
        nonlocal text
        assert text.count(a)==1,a[:100];text=text.replace(a,b,1)
    change("if floor(s)and s.x<1504 then stockPhase('approach',1)end","if floor(s)then stockPhase('approach',0)end")
    change("   if hx>=STOCK.x and hx<STOCK.x+16 then stockPhase('release',0)",
        "   if hx>=STOCK.x and hx<STOCK.x+16 then stock.head_position={state=s,head_x=hx,tile=tile(hx,STOCK.y)};stockPhase('release',0)")
    change("    stock.step_start=#stock.step_decisions;stockPhase('fine-step',hx<STOCK.x and 65 or 66)",
        "    local direction=hx<STOCK.x and 1 or 2;local facing=direction==1 and 255 or 0\n    if s.facing~=facing then stock.face_target=facing;stock.face_pad=direction;stockPhase('fine-face',direction)\n    else stock.step_start=#stock.step_decisions;stockPhase('fine-step',direction|64)end")
    change(" elseif stock.phase=='fine-step'then",
        " elseif stock.phase=='fine-face'then\n  pad=stock.face_pad;if s.facing==stock.face_target then stockPhase('fine-settle',0)end\n elseif stock.phase=='fine-step'then")
    b=dict(W.Symbols.bundle(),raw=raw);head=W.address(b,'BlockBufferAdderData')+6
    old=f" if stock.phase~='jump'or cpu['cpu.y']~=read({head})then return end"
    change(old,f" if stock.phase~='jump'or cpu['cpu.y']~=read({head})or s.pose<68 or s.pose>78 then return end")
    parts=C.Packet.extract(raw)[1];pc=0xaa51
    hook=dict(pc=pc,address=3*8192+(pc&8191),bytes=list(parts[0][pc-0xa000:pc-0xa000+8]),private=True)
    install=r'''
stock.action_admissions={}
stockHook(@HOOK@,function(cpu)
 if not stock.active or stock.phase~='jump'or cpu['cpu.y']~=0 then return end
 if #stock.action_admissions>=12 then return end
 stock.action_admissions[#stock.action_admissions+1]={requested=cpu['cpu.a'],PC=cpu['cpu.pc'],SP=cpu['cpu.sp'],state=stockState(),
  source_actor_y=source(0x611),source_actor_x=source(0x60f)+256*source(0x610),
  source_cell_x=source(0x7d)+256*source(0x7e),source_kind=source(0x9f),surface=source(0x7f)+256*source(0x80)}
end)
'''.replace('@HOOK@',Previous.Previous.Base.lua(hook))
    change('local function naturalStockTick()\n',install+'\nlocal function naturalStockTick()\n')
    Previous.Previous.LuaRuntime().compile(text);return text

def metadata(raw,mode='star',jump=8):
    return dict(ROM_SHA256=PIN,Lua_SHA256=C.digest(controller(raw,mode,jump).encode()),required_native_variant=3,
        ordinary_careful_steps_after_actual_facing=True,native_head_column_and_action_query_witnesses=True,
        no_gameplay_seeds=True,native_ready=False,outputs=0,Mesen=False)
