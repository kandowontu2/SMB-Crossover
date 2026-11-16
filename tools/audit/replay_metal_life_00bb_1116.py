"""Only exact new owning metadata and readonly growth fields; controls frozen."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import current_metal_life_00bb_1116 as Current
import replay_metal_native_caps_7c0f_1116 as Life
import replay_metal_star_cell_7c0f_1116 as Star
import replay_metal_stock_7c0f_1116 as Config
import replay_smb1_alts_full11_1114 as Text
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,digest,C=Current.R,Current.ROM,Current.PIN,Current.W,Current.N,Current.digest,Current.Compose
KINDS=('oneup','star')
PINS={'oneup':('b801807675bd16beafcbc2e217839615fc77396ced9494e533e285b9df74ccc5','0411e2c3197664ad5657efc4de0e4762fe3a5b8b5221b8792baea10f4047ea6e'),
      'star':('8200726d1653f84158f62c7164790d8da0848ce5dbe7f03566d18c0ee7e8c439','70622af40c9afb210733b7160ce13c264436ca3fd15af299b4094046bf20c9a4')}


@lru_cache(maxsize=2)
def bindings(raw,key='oneup'):
    old=Current.reference(raw);actor,renderer,extra,_=Current.payload(raw);q=deepcopy(Config.bindings(old,key));b=Current.bundle(raw)
    q.update(sha=PIN,cookie=Current.COOKIE.hex(),actor_hex=actor.hex(),renderer_hex=renderer.hex(),extra_hex=extra.hex())
    for name in('GuestPowerupActive','GuestPowerupAge'):q['ram'][name]=W.address(b,name)
    for name,h in q['hooks'].items():
        if h['space']=='prg':
            at=h['offset']+16;assert raw[at:at+len(h['bytes'])]==bytes(h['bytes']),name
            lo=16+h['bank']*8192;h['bank_SHA256']=digest(raw[lo:lo+8192])
        elif name=='MsLifeCompare':
            h['bytes']=list(renderer[h['pc']-0xcd00:h['pc']-0xcd00+8]);assert h['bytes']==list(bytes.fromhex('ad5f07cd3ec81036'))
    return q


@lru_cache(maxsize=2)
def controller(raw,key='oneup'):
    assert key in KINDS;module=Life if key=='oneup'else Star
    assert digest(Path(module.__file__).read_bytes())==PINS[key][0]
    old=module.controller(Current.reference(raw),key);assert digest(old.encode())==PINS[key][1]
    _,body=old.split('\n',1);anchor="power=r('PlayerStatus'),lives=";extra="growthActive=r('GuestPowerupActive'),growthAge=r('GuestPowerupAge'),"
    assert body.count(anchor)==1;observed=body.replace(anchor,extra+anchor,1);assert observed.replace(extra,'',1)==body
    text='local C='+Text.lua(bindings(raw,key))+'\n'+observed;LuaRuntime().compile(text);return text


def metadata(raw,key='oneup'):
    old=Current.reference(raw);text=controller(raw,key)
    return dict(ROM_SHA256=PIN,parent7c0f_SHA256=digest(old),factory_SHA256=digest(Path(__file__).read_bytes()),
        facade_SHA256=digest(Path(Current.__file__).read_bytes()),composer_SHA256=Current.COMPOSER_SHA,
        controller_SHA256=digest(text.encode()),frozen_parent_factory_SHA256=PINS[key][0],frozen_parent_Lua_SHA256=PINS[key][1],
        control_body_exact_after_removing_readonly_growth_fields=True,kind=key,hook_registration='Frozen actual exec/return registrations retained, including MsFrameB461 and dynamic PC/SP witnesses',
        scope='Actual00bb genuine M then '+key+'; exact prior controls and strict inventory/25 returned-original-work gates; no hosted60 growth claim',
        outputs=0,Mesen=False,gameplay_seeds=0,game_state_writes=False)


def family(kind='oneup'):return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw,kind),metadata=lambda raw,key:metadata(raw,kind))
