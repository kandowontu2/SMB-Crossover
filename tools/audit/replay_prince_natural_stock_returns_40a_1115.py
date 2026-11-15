"""Separate40a stock observer: authenticated016E and actual popup credit."""
from functools import lru_cache
from pathlib import Path
import re
import replay_prince_natural_stock_40a_1115 as Previous

C,N,W,PIN,LuaRuntime=Previous.C,Previous.N,Previous.W,Previous.PIN,Previous.LuaRuntime
PREVIOUS_SHA='daa6eb8961dae9986a927d4b8e529eba9b1f2a3264dc2708e539fbe75fc54748'

def authored(raw):
    source=(C.R/'src/level_tiles.s').read_text();data=bytearray()
    for line in source.split('L_GroundArea6:',1)[1].splitlines():
        if'.byte'in line:
            data.extend(int(v,16)for v in re.findall(r'\$([\da-fA-F]{2})',line.split(';')[0]))
            if data[-1]==253:break
    blob=bytes(data);assert raw.count(blob)==1
    return dict(offset=raw.index(blob),bytes=len(blob),SHA256=C.digest(blob))

@lru_cache(maxsize=4)
def controller(raw,mode='oneup',jump=8):
    assert C.digest(Path(Previous.__file__).read_bytes())==PREVIOUS_SHA and C.digest(raw)==PIN
    level=authored(raw);text=Previous.controller(raw,mode,jump);bundle=dict(W.Symbols.bundle(),raw=raw)
    def change(old,new):
        nonlocal text
        assert text.count(old)==1,old[:90];text=text.replace(old,new,1)
    pc=W.address(bundle,'FarcallJmpTarget_SMC')+3;target=W.address(bundle,'SafereturnA_SMC')+1
    assert pc==0x16e
    check=f"assert(pc=={pc} and read(pc)==141 and read(pc+1)=={target&255} and read(pc+2)=={target>>8},'Authenticated native FarCall return instruction')"
    change(" local a=emu.convertAddress(pc);assert(a,'Actual caller return mapping')",
        " local a;if pc<0x8000 then "+check+";a={memType=-1,address=pc}else a=emu.convertAddress(pc);assert(a,'Actual caller return mapping')end")
    change("   local b=emu.convertAddress(pc);if not b or b.memType~=expected.memType or b.address~=expected.address or emu.getState()['cpu.sp']~=expected.sp then return end",
        "   local b;if pc<0x8000 then "+check+";b={memType=-1,address=pc}else b=emu.convertAddress(pc)end;if not b or b.memType~=expected.memType or b.address~=expected.address or emu.getState()['cpu.sp']~=expected.sp then return end")
    fp=W.address(bundle,'FloateyNumbersCore');at=W.location(bundle,'FloateyNumbersCore')
    hook=dict(pc=fp,address=at-16,bytes=list(raw[at:at+8]),private=False)
    timer=W.address(bundle,'FloateyNum_Timer')
    observer=r'''
stock.authored_level=@LEVEL@
stockHook(@HOOK@,function(cpu)
 if not stock.collected or stock.credit or cpu['cpu.x']~=stock.collector.actor.slot then return end
 local i=cpu['cpu.x'];if read(@TIMER@+i)~=43 then return end
 assert(read(STOCK.ram.FloateyNum_Control+i)==(STOCK.kind==3 and 11 or 6),'Actual target popup at native credit time')
 local before={score=stockScore(),lives=read(0x75f),PC=cpu['cpu.pc'],SP=cpu['cpu.sp'],state=stockState()}
 stockReturn(cpu,function(ret)
  local after=stockState();local score=stockScore()
  if STOCK.kind==3 then assert(after.lives==before.lives+1 and read(STOCK.ram.Square2SoundQueue)==64,'Actual delayed1UP life/cue64')
  else assert(after.lives==before.lives and score==before.score+1000,'Actual target Star1000-point award')end
  stock.credit={before=before,state=after,score=score,cue=read(STOCK.ram.Square2SoundQueue),return_PC=ret.pc,return_SP=ret.sp}
 end)
end)
'''.replace('@LEVEL@',Previous.lua(level)).replace('@HOOK@',Previous.lua(hook)).replace('@TIMER@',str(timer))
    change('local function naturalStockTick()\n',observer+'\nlocal function naturalStockTick()\n')
    change("  local credited=STOCK.kind==3 and s.lives==3 or STOCK.kind==2 and stockScore()==stock.collector.score+1000\n  if credited and not stock.credit then stock.credit={state=s,score=stockScore(),cue=read(STOCK.ram.Square2SoundQueue)}end\n",'')
    LuaRuntime().compile(text);return text

def metadata(raw,mode='oneup',jump=8):
    return dict(ROM_SHA256=PIN,Lua_SHA256=C.digest(controller(raw,mode,jump).encode()),mode=mode,jump_mask=jump,
        required_native_variant=3,actual_caller_016E_authenticated=True,actual_popup_timer43_credit=True,
        native_ready=False,no_gameplay_seeds=True,outputs=0,Mesen=False)
