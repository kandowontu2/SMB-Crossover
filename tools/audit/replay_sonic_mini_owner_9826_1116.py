"""Frozen a2 captured-resource1UP body; owning9826 config refresh only."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
import replay_sonic_ceiling_life_resources_a2d9_1116 as Frozen
import current_sonic_mini_owner_9826_1116 as F

J=F
R,ROM,H,PIN=F.R,F.ROM,F.H,F.PIN
FROZEN_SHA='09b1f486b1650847eaf469275e6068be78961cdd0e8ebf530f1baf6930909ff5'

@lru_cache(maxsize=2)
def bindings(raw,form='sonic'):
    # Frozen body and all game assertions are kept; only actual auth changes.
    assert H(Path(Frozen.__file__).read_bytes())==FROZEN_SHA
    q=deepcopy(Frozen.bindings(F.reference(raw),form));q['sha']=PIN;q['facade_SHA256']=H(Path(F.__file__).read_bytes())
    for h in q['hooks'].values():
        if h['tag']>=128:
            at=16+h['offset'];assert raw[at:at+len(bytes.fromhex(h['hex']))]==bytes.fromhex(h['hex'])
            bank=h['tag']&127;h['bank_SHA256']=H(raw[16+bank*8192:16+(bank+1)*8192])
        else:assert F.bindings(raw)['loaded'](h['pc'])[:len(bytes.fromhex(h['hex']))]==bytes.fromhex(h['hex'])
    return q

@lru_cache(maxsize=2)
def controller(raw,form='sonic'):
    q=bindings(raw,form);body=Frozen.controller(F.reference(raw),form).split('\n',1)[1]
    return'local SONIC_CONFIG='+Frozen.Frozen.Frozen.value(q)+'\n'+body
