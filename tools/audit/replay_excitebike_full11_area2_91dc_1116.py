"""Endpoint-only current underground1-2 successor; v5 inputs unchanged."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import json
import replay_excitebike_full11_91dc_1116 as Previous

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest
BASE_SHA='0274120d2257233649acd5faa0798964c3f204dd7c90ad47fc0bca48aa1a9126'
SCENE=Previous.HISTORIC/'capture/scene.json'
SCENE_SHA='7124a4c33de9c41fb577647f221ec30013b5782cd4fb46530f41dacdb4701e43'

@lru_cache(maxsize=1)
def controller(raw,key='excitebike'):
    assert digest(Path(Previous.__file__).read_bytes())==BASE_SHA and digest(SCENE.read_bytes())==SCENE_SHA
    scenes=json.loads(SCENE.read_text());assert any((r['world'],r['level'],r['old_area'],r['area'])==(0,1,1,2)for r in scenes)
    text=Previous.controller(raw,key)
    text=Previous.once(text,'and s.world==0 and s.level==1 and s.area==0',
        'and route.underground_entrance and s.world==0 and s.level==1 and s.area==2 and s.area_type==0 and s.area_offset==0')
    marker=" if s.level==1 and s.engine==0 then route.entrance=route.entrance or s end"
    text=Previous.once(text,marker,marker+"\n if s.level==1 and s.area==2 and s.area_type==0 and s.area_offset==0 and s.engine==0 then route.underground_entrance=route.underground_entrance or s end")
    Previous.Base.LuaRuntime().compile(text);return text

def metadata(raw,key='excitebike'):
    q=Previous.metadata(raw,key);q.update(controller_SHA256=digest(controller(raw,key).encode()),area_factory_SHA256=digest(Path(__file__).read_bytes()),
        historical_scene_SHA256=SCENE_SHA,controls_identical=True,stage='World0/Level1/Area2/AreaType0/loaded offset0',
        retained_area0_observer_bound=dict(controller='81ae1165da8fc09c665eaf72c40728f1fa242ca2dd393fc2fcc2d656e706480e',
            driver_passes=8000,empty_terminal_receipt_SHA256='44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a'),
        endpoint='Both actual native1-2 entrances plus25 living grounded completed originalMotor/Movement at returnedMain; no exactX constraint')
    return q

def family():return SimpleNamespace(W=W,N=N,controller=controller,metadata=metadata)
