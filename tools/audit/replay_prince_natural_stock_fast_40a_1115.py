"""New strict40a stock controls using root's exact immutable E161 fixture."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import inspect
import replay_prince_natural_stock_40a_1115 as Base
import replay_prince_natural_stock_returns_40a_1115 as Returns
import replay_prince_natural_stock_hold_40a_1115 as Hold

C,N,W,PIN,LuaRuntime=Base.C,Base.N,Base.W,Base.PIN,Base.LuaRuntime
FIXTURE=C.R/'tools/reference/prince40a_full_e161_1115.lua'
FIXTURE_SHA='e1614ed60e1bb2d3990df26c4f1f16e97fcda6a744ca9950bf346cc2a3ddbc2f'

def fixture(raw):
    assert C.digest(raw)==PIN
    data=FIXTURE.read_bytes();assert len(data)==92961 and b'\r'not in data and C.digest(data)==FIXTURE_SHA
    assert C.digest(Path(Base.Frozen.__file__).read_bytes())==Base.FROZEN_SHA
    return data.decode()

def clone(fn,globals):
    source=inspect.getsource(fn);space=dict(fn.__globals__,**globals)
    exec(compile(source,str(Path(__file__))+':strict-fixture-source-equivalent','exec'),space)
    return space[fn.__name__]

@lru_cache(maxsize=1)
def held_factory():
    assert C.digest(Path(Base.__file__).read_bytes())==Returns.PREVIOUS_SHA
    frozen=SimpleNamespace(**dict(Base.Frozen.__dict__,controller=fixture))
    first=clone(Base.controller.__wrapped__,dict(Frozen=frozen))
    base=SimpleNamespace(**dict(Base.__dict__,controller=first))
    second=clone(Returns.controller.__wrapped__,dict(Previous=base))
    returns=SimpleNamespace(**dict(Returns.__dict__,controller=second))
    return clone(Hold.controller.__wrapped__,dict(Previous=returns))

def head_trace(text,raw):
    b=dict(W.Symbols.bundle(),raw=raw);pc=W.address(b,'BlockBufferColli_Head');at=W.location(b,'BlockBufferColli_Head')
    hook=dict(pc=pc,address=at-16,bytes=list(raw[at:at+8]),private=False)
    fields={name:W.address(b,name)for name in('BlockBuffer_X_Adder','BlockBuffer_Y_Adder','Player_Y_Speed','R2','R3')}
    observer=r'''
local stockQueryFields=@FIELDS@
stock.head_queries={}
stockHook(@HOOK@,function(cpu)
 if not stock.active or #stock.head_queries>=24 or math.abs(state().x-STOCK.x)>48 then return end
 local s=stockState();local vy=read(stockQueryFields.Player_Y_Speed)
 if s.pose~=78 and vy<128 then return end
 local y=cpu['cpu.y'];local addx=read(stockQueryFields.BlockBuffer_X_Adder+y);local addy=read(stockQueryFields.BlockBuffer_Y_Adder+y)
 local key=s.x..':'..s.y..':'..s.pose..':'..y..':'..vy
 if stock.last_query==key then return end;stock.last_query=key
 local q={before=s,PC=cpu['cpu.pc'],SP=cpu['cpu.sp'],adder_index=y,adder_x=addx,adder_y=addy,
  native_speed=vy,predicted_world_x=s.x+addx,predicted_y=(s.y+addy)&255,source_actor_y=source(0x611),source_pad=source(0x40a)}
 stock.head_queries[#stock.head_queries+1]=q
 stockReturn(cpu,function(ret)
  q.raw_tile=read(stockQueryFields.R3);q.queried_row=(read(stockQueryFields.R2)+32)&255;q.return_PC=ret.pc;q.return_SP=ret.sp
 end)
end)
'''.replace('@FIELDS@',Base.lua(fields)).replace('@HOOK@',Base.lua(hook))
    old='local function naturalStockTick()\n';assert text.count(old)==1
    return text.replace(old,observer+'\n'+old,1)

@lru_cache(maxsize=3)
def controller(raw,mode='oneup',jump=8):
    assert C.digest(raw)==PIN and jump==8 and mode in('oneup','star')
    text=held_factory()(raw,mode,8)
    if mode=='oneup':assert C.digest(text.encode())=='720d78ec915b3c4a97fcb16442dbc52fb0e169ea117df57e2b328ade2e7c800c','Fixture substitution changed held-Up inputs or observers'
    if mode=='star':
        old='if stock.attempts==0 then target=target-28 end';assert text.count(old)==1
        text=text.replace(old,'if stock.attempts==0 then target=target-20 end',1)
        # Handle the actual native opponent before steering toward the item.
        a=text.index(' if item then\n  if not stock.mature then');b=text.index(' if s.sword==2 then\n',a);z=text.index(" if stock.phase=='left-drop'then",b)
        text=text[:a]+text[b:z]+text[a:b]+text[z:]
        old="s.sword==stock.collected.state.sword and s.power==stock.collected.state.power,'Post-credit source inventory retained'"
        new="(s.sword>0)==(stock.collected.state.sword>0)and s.power==stock.collected.state.power,'Post-credit source sword inventory retained; stance may draw/sheath'"
        assert text.count(old)==1;text=text.replace(old,new,1)
    text=head_trace(text,raw);LuaRuntime().compile(text)
    assert not any(token in text for token in('emu.write','emu.setState','io.open','dofile','saveState','loadState'))
    return text

def metadata(raw,mode='oneup',jump=8):
    return dict(ROM_SHA256=PIN,Lua_SHA256=C.digest(controller(raw,mode,jump).encode()),mode=mode,required_native_variant=3,
        immutable_E161_fixture_SHA256=FIXTURE_SHA,fixture_bytes=92961,old_factories_unchanged=True,
        ordinary_held_Up80=True,actual_native_head_query_trace=True,no_gameplay_seeds=True,native_ready=False,outputs=0,Mesen=False)
