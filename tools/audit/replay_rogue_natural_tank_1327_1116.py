"""Native-ready strict1327 ordinary first Rogue energy tank; stdout only."""
from functools import lru_cache
from pathlib import Path
import json,re
import current_rogue_grounded_stock_1327_1116 as J
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,H,N,W,Frames,PIN=J.R,J.ROM,J.H,J.N,J.W,J.Frames,J.PIN
FACADE_SHA='e8682a76ce89431a925e152f360c93e59d9dfce6d2276d15a561bb0b31caa812'
TEMPLATE=R/'tools/playthroughs/rogue_natural_tank_1327_1116.lua'


@lru_cache(maxsize=1)
def bindings(raw):
    assert H(Path(J.__file__).read_bytes())==FACADE_SHA
    q=J.bindings(raw);b=q['bundle'];body=J.policy_text(raw);text=TEMPLATE.read_text()
    names=set(q['fields'])|set(re.findall(r"\br\('([^']+)'",body+text))|{'CrossoverTitleDrawn','DisableScreenFlag','CrossoverMenuState','CrossoverBehaviorVersion'}
    hooks={}
    for n,h in q['hooks'].items():
        if 'PC'not in h:continue
        hooks[n]=dict(PC=h['PC'],offset=h['file']-16,bytes=list(raw[h['file']:h['file']+16]))
    return dict(sha=PIN,ram={n:W.address(b,n)for n in sorted(names)},hooks=hooks)


def lua(v):
    if isinstance(v,str):return json.dumps(v)
    if isinstance(v,(int,float)):return str(v)
    if isinstance(v,list):return'{'+','.join(lua(x)for x in v)+'}'
    if isinstance(v,dict):return'{'+','.join('['+lua(k)+']='+lua(x)for k,x in sorted(v.items()))+'}'
    raise TypeError(type(v))


@lru_cache(maxsize=1)
def controller(raw):
    q=bindings(raw);body=J.policy_text(raw)
    text='local C='+lua(q)+'\nlocal choose=(function()\n'+body+'\nend)()\n'+TEMPLATE.read_text()
    LuaRuntime().compile(text)
    assert all(t not in text for t in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return text


def metadata(raw):
    text=controller(raw)
    return dict(ROM_SHA256=PIN,controller_SHA256=H(text.encode()),factory_SHA256=H(Path(__file__).read_bytes()),
        template_SHA256=H(TEMPLATE.read_bytes()),facade_SHA256=FACADE_SHA,policy_SHA256=H(J.policy_text(raw).encode()),
        ordinary_inputs_only=True,mature_typedD8_C1_scorewriter_plus25_original_returns=True,
        public_Main_writer_inclusive_return_count_explicit=True,images=0,generated_files=0,Mesen=False)


if __name__=='__main__':print(json.dumps(metadata(J.load_current_image()),separators=(',',':')),flush=True)
