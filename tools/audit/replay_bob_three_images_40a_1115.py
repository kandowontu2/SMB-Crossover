"""Bob's frozen functional route plus the existing three read-only scenes."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import replay_bub_flower_margin_40a_1115 as Functional
import replay_bub_flower_images_40a_1115 as Pictures
import replay_bub_three_images_40a_1115 as Third

R,ROM,W,N,B,PIN=Functional.R,Functional.ROM,Functional.W,Functional.N,Functional.B,Functional.PIN
DEPENDENCIES=((Functional,'88a452e94489dea2749403abc193b7c4a2578b7a2e837183a0cf102af3d85b76'),
    (Pictures,'c1616cddfc30edae8cecdaec3d6e5ac567409c0ed8930fcc8273f91590c0a562'),
    (Third,'59fa9dbff4b9aa9d13759651c0baf30ed3ee9b116244093f84a1148019293526'))
FUNCTIONAL_LUA='27577418b4ecdfe0a5ea0f43a9a31040bbbfcb21611103528aaad5c5169de813'

@lru_cache(maxsize=1)
def controller(raw,identity=1,mode='mushroom'):
    assert identity==1 and sha256(raw).hexdigest()==PIN
    for module,pin in DEPENDENCIES:assert sha256(Path(module.__file__).read_bytes()).hexdigest()==pin
    old=Functional.controller(raw,identity,mode)
    assert sha256(old.encode()).hexdigest()==FUNCTIONAL_LUA
    once=Functional.once
    observer=once(Pictures.OBSERVE,'local function visualBase64(bytes)',Third.GOOMBA+'\nlocal function visualBase64(bytes)')
    observer=once(observer,' visualRows[#visualRows+1]=row',Third.ACK+'\n visualRows[#visualRows+1]=row')
    observer=once(observer,"#visualQueue+#visualRows<2,'Maximum two queued pictures'","#visualQueue+#visualRows<3,'Maximum three queued pictures'")
    observer=once(observer,"#visualRows<2,'Maximum two actual rendered PNGs'","#visualRows<3,'Maximum three actual rendered PNGs'")
    text=once(old,'local function finish(',Pictures.DECL+'local function finish(')
    finish="if done then return end;if ok then assert(#visualRows==3,'Three rendered Goomba and item scenes captured')end;done=true"
    text=once(text,'if done then return end;done=true',finish)
    text=once(text,'natural_flower=flower','natural_flower=flower,visual=visualRows')
    text=once(text,'local routeStarted=false',observer+'\nlocal routeStarted=false')
    text=once(text,'pending=nil;updates=updates+1;tick()','pending=nil;updates=updates+1;tick();visualObserve();visualGoombaObserve()')
    text+=Pictures.END
    restored=text[:-len(Pictures.END)].replace(Pictures.DECL,'',1).replace(observer+'\n','',1)
    restored=restored.replace(finish,'if done then return end;done=true',1)
    restored=restored.replace('natural_flower=flower,visual=visualRows','natural_flower=flower',1)
    restored=restored.replace('tick();visualObserve();visualGoombaObserve()','tick()',1)
    assert restored==old,'Removing only read-only observers restores exact native-qualified Bob controls'
    from check_ff_stdout_controller_source_1110 import LuaRuntime
    LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState'))
    return text

def metadata(raw):
    return dict(ROM_SHA256=PIN,Lua_SHA256=sha256(controller(raw).encode()).hexdigest(),
        functional_Lua_SHA256=FUNCTIONAL_LUA,exact_control_restoration=True,maximum_images=3,
        maximum_total_PNG_bytes=196608,output_files=0,gameplay_seeds=0,Mesen=False)

if __name__=='__main__':
    import json
    print(json.dumps(metadata(ROM.read_bytes()),separators=(',',':')))
