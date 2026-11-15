"""Strict current571 adapter for the frozen48-Main native idle observation."""
from copy import deepcopy
from hashlib import sha256

import compose_native_floatey_score_1114 as Score
import replay_battletoads_camera_full11_1114 as Stage
import replay_battletoads_idle_native_1114 as Previous

R,ROM,W,N,PIN=Stage.R,Stage.ROM,Stage.W,Stage.N,Score.CANDIDATE
OLD_LUA='f6cc1a294935e7e8a76ba301f8de423b9227880b34059731f9f7b375f89a336e'


def config(raw):
    parent=Score.inverse(raw)
    q=deepcopy(Stage.bindings(parent,'rash'))
    b=dict(W.Symbols.bundle(),raw=raw)
    q['ram']['NmiSkipped']=W.address(b,'NmiSkipped')
    q['sha']=PIN
    for h in q['hooks'].values():
        at=16+h['offset'];assert raw[at:at+len(h['bytes'])]==bytes(h['bytes'])
        if 'bank'in h:
            at=16+h['bank']*8192;h['bank_SHA256']=sha256(raw[at:at+8192]).hexdigest()
    return q


def controller(raw):
    parent=Score.inverse(raw);old=Previous.controller(parent)
    assert sha256(old.encode()).hexdigest()==OLD_LUA
    old_config=config(raw);old_config['sha']=Stage.PIN
    for h in old_config['hooks'].values():
        if 'bank'in h:
            at=16+h['bank']*8192;h['bank_SHA256']=sha256(parent[at:at+8192]).hexdigest()
    lua=Stage.Previous.Parent.Frozen.lua
    prefix='local C='+lua(old_config)+'\n';assert old.startswith(prefix)
    text='local C='+lua(config(raw))+'\n'+old[len(prefix):]
    assert text.split('\n',1)[1]==old.split('\n',1)[1]
    Stage.Frozen.LuaRuntime().compile(text)
    return text
