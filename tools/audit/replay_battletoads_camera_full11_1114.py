"""Strict BT camera candidate stage controls; frozen1daca factory remains strict."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256

import compose_battletoads_camera_handoff_1114 as C
import replay_battletoads_full11_current_1114 as Previous

R,ROM,W,N,PIN=Previous.R,Previous.ROM,Previous.W,Previous.N,C.CANDIDATE
IDENTITIES=Previous.IDENTITIES
SOURCE_PIN='f67790c886332aa7073fef9895f4db055e34185740c3e8a47df7b68fca7c1856'


def legacy(raw):
    assert sha256((R/'tools/audit/replay_battletoads_full11_current_1114.py').read_bytes()).hexdigest()==SOURCE_PIN
    return C.Parent.inverse(C.inverse(raw))


class Frozen:
    LuaRuntime=Previous.Parent.Frozen.LuaRuntime
    @staticmethod
    def normalize(raw):return Previous.normalize(legacy(raw))


normalize=Frozen.normalize


@lru_cache(maxsize=2)
def bindings(raw,key):
    old=legacy(raw);q=deepcopy(Previous.bindings(old,key));q['sha']=PIN
    for h in q['hooks'].values():
        if'bank'in h:
            at=16+h['bank']*8192;h['bank_SHA256']=sha256(raw[at:at+8192]).hexdigest()
    return q


@lru_cache(maxsize=2)
def controller(raw,key):
    old=legacy(raw);text=Previous.controller(old,key)
    prefix='local C='+Previous.Parent.Frozen.lua(Previous.bindings(old,key))+'\n';assert text.startswith(prefix)
    text='local C='+Previous.Parent.Frozen.lua(bindings(raw,key))+'\n'+text[len(prefix):]
    marker='if c.x>3120 then b.right=true end';assert text.count(marker)==1
    text=text.replace(marker,'if c.x>3120 then b.right=true;b.b=false;if c.grounded and not c.lastA then b.a=true end end',1)
    Frozen.LuaRuntime().compile(text)
    assert not any(v in text for v in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return text


def metadata(raw,key):
    q=bindings(raw,key)
    return dict(ROM_SHA256=PIN,identity=key,compiled_menu={k:q[k]for k in('name','owner','slot','variant','cycle')},
        controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),physical_private_RAM3_reads=True,
        original_factory_source_SHA256=SOURCE_PIN,ordinary_final_flag_hop=True,
        full_nonshortcut1_1_then25grounded1_2=True,normal_controls_only=True,gameplay_seeds=0,outputs=0,Mesen_run=False)
