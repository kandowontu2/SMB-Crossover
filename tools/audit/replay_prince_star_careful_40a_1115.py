"""Use actual original careful-step decisions to align the Star head column."""
from functools import lru_cache
import replay_prince_natural_stock_fast_40a_1115 as Previous

C,N,W,PIN=Previous.C,Previous.N,Previous.W,Previous.PIN

@lru_cache(maxsize=1)
def controller(raw,mode='star',jump=8):
    assert mode=='star'and jump==8 and C.digest(raw)==PIN
    text=Previous.controller(raw,mode,jump)
    def change(a,b):
        nonlocal text
        assert text.count(a)==1,a[:100];text=text.replace(a,b,1)
    fixture=Previous.fixture(raw)
    line=next(line for line in fixture.splitlines()if line.startswith('local freshStepHooks='))
    selectors=line.replace('local freshStepHooks=','local stockStepHooks=',1)
    install=r'''
@SELECTORS@
stock.step_decisions={}
for _,h in ipairs(stockStepHooks)do
 stockHook({pc=h.pc,address=3*8192+(h.pc&8191),bytes=h.bytes,private=true},function(cpu)
  if not stock.active or stock.phase~='fine-step'then return end
  assert(#stock.step_decisions<16,'Finite original careful-step decisions')
  stock.step_decisions[#stock.step_decisions+1]={kind=h.kind,PC=h.pc,SP=cpu['cpu.sp'],half_distance=source(0x4f),state=stockState()}
 end)
end
'''.replace('@SELECTORS@',selectors)
    change('local function naturalStockTick()\n',install+'\nlocal function naturalStockTick()\n')
    old=" elseif stock.phase=='approach'then\n  local target=STOCK.x-8;if stock.attempts==0 then target=target-20 end\n  if s.x<target-3 then pad=1 elseif s.x>target+3 then pad=2 else stockPhase('release',0)end"
    new=r''' elseif stock.phase=='approach'or stock.phase=='fine-settle'then
  pad=0
  if floor(s)and idle(s)and s.action==0 then
   -- Actual native head adder8 must land in the authored16px column.
   local hx=s.x+8
   if hx>=STOCK.x and hx<STOCK.x+16 then stockPhase('release',0)
   else
    stock.step_start=#stock.step_decisions;stockPhase('fine-step',hx<STOCK.x and 65 or 66)
   end
  end
 elseif stock.phase=='fine-step'then
  if #stock.step_decisions>stock.step_start then stockPhase('fine-settle',0)end'''
    change(old,new)
    # Trace only actual head queries during the requested reach. The shared
    # entry's foot adders52/53 and earlier braking frames are separate paths.
    b=dict(W.Symbols.bundle(),raw=raw);head=W.address(b,'BlockBufferAdderData')+6
    change(' if s.pose~=78 and vy<128 then return end',
        f" if stock.phase~='jump'or cpu['cpu.y']~=read({head})then return end")
    Previous.LuaRuntime().compile(text);return text

def metadata(raw,mode='star',jump=8):
    return dict(ROM_SHA256=PIN,Lua_SHA256=C.digest(controller(raw,mode,jump).encode()),required_native_variant=3,
        ordinary_original_careful_steps=True,actual_fresh_selector_witness=True,head_column_from_native_adder8=True,
        no_gameplay_seeds=True,native_ready=False,outputs=0,Mesen=False)
