"""Fund actual original Flower launch speed with a measured safe run-up."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_excitebike_flower_runup_91dc_1116 as Previous

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest
BASE_SHA='c8a836f96fbcaf8d1c990395165a89cda197b05e0c07278cb5440a3ca4c2af7d'

@lru_cache(maxsize=1)
def controller(raw,key='flower'):
    assert key=='flower'and digest(Path(Previous.__file__).read_bytes())==BASE_SHA
    text=Previous.controller(raw,key);old='if s.x>=C.target_x+48 then';assert text.count(old)==1
    text=text.replace(old,'if s.x>=C.target_x+64 then',1)
    Previous.Previous.Previous.Previous.Previous.LuaRuntime().compile(text);return text

def metadata(raw,key='flower'):
    q=Previous.metadata(raw,key);q.update(controller_SHA256=digest(controller(raw,key).encode()),runway_factory_SHA256=digest(Path(__file__).read_bytes()),
        retained_short_runup_negative='4730ec851867197668376231d25d83c9a0e9bee0f21564d2454dbd486abca0ff',
        measured_runup='Prior release1296/speed378 coasted to1317; extend ordinary throttle16px to provide the proved original launch speed, retaining pit guard')
    return q

def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
