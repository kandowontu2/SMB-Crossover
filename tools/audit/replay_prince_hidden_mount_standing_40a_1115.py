"""Queue the original standing A jump during the real Up-mount release."""
from functools import lru_cache
import replay_prince_hidden_partial_up_40a_1115 as Previous

C,N,W,PIN=Previous.C,Previous.N,Previous.W,Previous.PIN

@lru_cache(maxsize=1)
def controller(raw,mode='oneup',jump=8):
    text=Previous.controller(raw,mode,jump)
    def change(a,b):
        nonlocal text
        assert text.count(a)==1,a[:100];text=text.replace(a,b,1)
    old="""  if idle(s)and s.action==0 then
   local left,right=capFeet(s,912,144)
   if left and right then stock.actual_mount=s;stockPhase('cap-run',1)end
  end
  assert(age<240,'Bounded original partial-cap Up continuation')"""
    new=r'''  local left,right=capFeet(s,912,144)
  if left and right and s.action==8 then stock.actual_mount=s;stockPhase('cap-standing-A',128)end
  assert(age<240,'Bounded original partial-cap Up continuation')
 elseif stock.phase=='cap-standing-A'then
  pad=128
  if s.action==3 then
   stock.standing_admission=s;stock.minimum_y=s.y
   stock.standing_support={left_x=s.x+2,right_x=s.x+13,row=s.y+32,left_tile=tile(s.x+2,s.y+32),right_tile=tile(s.x+13,s.y+32),native_ground=s.ground,source_foot=s.foot}
   stockPhase('standing-flight',1)
  end
  assert(age<200,'Original standing-A handler must admit actual action3')
 elseif stock.phase=='standing-flight'then
  stock.minimum_y=math.min(stock.minimum_y,s.y);pad=s.x<1040 and 1 or 0
  if age>100 and floor(s)and idle(s)and s.action==0 then
   stock.standing_landing=s;final=s;finish(false,'Original cap standing jump landed without hidden1UP birth')
  end
  assert(age<360,'Bounded original cap standing jump and landing')'''
    change(old,new)
    b=dict(W.Symbols.bundle(),raw=raw);index=W.address(b,'BlockBufferAdderData')+6
    old=f" if stock.phase~='running-reach'or cpu['cpu.y']~=read({index})or(s.pose~=78 and vy<128)then return end"
    change(old,f" if stock.phase~='standing-flight'or cpu['cpu.y']~=read({index})then return end")
    Previous.Previous.Previous.LuaRuntime().compile(text)
    assert not any(token in text for token in('emu.write','emu.setState','io.open','dofile','saveState','loadState'))
    return text

def metadata(raw,mode='oneup',jump=8):
    return dict(ROM_SHA256=PIN,Lua_SHA256=C.digest(controller(raw,mode,jump).encode()),required_native_variant=3,
        genuine_Up_mount_then_original_A_queued=True,actual_action3_and_cap_foot_tiles_recorded=True,
        actual_delayed_life_cue64_and_25_Prince_returns_required=True,endpoint_at_actual_Main_return=True,
        no_gameplay_seeds=True,native_ready=False,outputs=0,Mesen=False)
