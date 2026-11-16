"""Actual current Toad first Mushroom, original engine and ordinary controls."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import current_smb1_toad_stock_91dc_1116 as Current
import replay_smb1_alts_full11_1114 as Text
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,digest=Current.R,Current.ROM,Current.PIN,Current.W,Current.N,Current.digest
TEMPLATE=R/'tools/playthroughs/smb1_toad_mushroom_91dc_1116.lua'
PINS={Text.NAV:'d51c479da4e6bb0256fec5411a6e61cd4174977cfa76447655bdb18d88d3c3f4',
    Text.POLICY:'feca813dc2d28328a2c75c746fe838ec52159abfc8a415e3ec7a6d44dda65574'}


@lru_cache(maxsize=1)
def controller(raw,key='toad'):
    assert key=='toad';c=dict(Current.bindings(raw));h=c['hooks']['MarioSourceMovement']
    c['movement_hex']=raw[16+h['offset']:16+h['offset']+64].hex()
    for p,sha in PINS.items():assert digest(p.read_bytes())==sha
    route=Text.POLICY.read_text();prefix="local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))\n"
    assert route.count(prefix)==1;route=route.replace(prefix,'',1)
    old="local travel=assert(dofile(root..'/tools/playthroughs/mario_luigi_scrooge_nav.lua'))"
    assert route.count(old)==1;route=route.replace(old,'local travel=(function()\n'+Text.NAV.read_text()+'\nend)()',1)
    text='local C='+Text.lua(c)+'\nlocal travel=(function()\n'+route+'\nend)()\n'+TEMPLATE.read_text()
    LuaRuntime().compile(text)
    assert'\r'not in text and not any(s in text for s in('emu.write','emu.setState','io.open','dofile','takeScreenshot','loadState','saveState'))
    return text


def metadata(raw,key='toad'):
    return dict(ROM_SHA256=PIN,controller_SHA256=digest(controller(raw,key).encode()),
        factory_SHA256=digest(Path(__file__).read_bytes()),template_SHA256=digest(TEMPLATE.read_bytes()),
        foundation=Current.foundation(raw),pure_control_sources={p.name:digest(p.read_bytes())for p in PINS},
        scope='Actual compiled Toad, genuine firstM birth/mature/collector/erase/cue/1000/60tick tier1 then25 returned Mario movements at actualMainreturn',
        gameplay_seeds=0,game_bytes_changed=0,outputs=0,Mesen=False)


def family():return SimpleNamespace(W=W,N=N,controller=controller,metadata=metadata)
