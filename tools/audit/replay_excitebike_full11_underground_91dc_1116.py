"""Parser-authenticated type2 underground endpoint; no input/game changes."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_excitebike_full11_area2_91dc_1116 as Previous

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest
BASE_SHA='9c8a6a6f286d464f6154f0e02aa855fadc30db503e60fc70d7fef7c0a331abd4'

@lru_cache(maxsize=1)
def parser(raw):
    b=Current.bundle(raw);at=W.location(b,'GetAreaType');area=W.address(b,'AreaType')
    prefix=bytes.fromhex('29600a2a2a2a8d')+area.to_bytes(2,'little')
    assert raw[at:at+len(prefix)]==prefix,'Actual AND60/ASL/ROLx3/STA area type'
    world_at=W.location(b,'WorldAddrOffsets');table_at=W.location(b,'AreaAddrOffsets')
    pointer=raw[table_at+raw[world_at]+2];assert pointer==0xc0
    assert((pointer&96)>>5,pointer&31)==(2,0)
    return dict(GetAreaType_file=at,GetAreaType_PC=W.address(b,'GetAreaType'),exact_prefix=prefix.hex(),
        World0_Area2_pointer=pointer,loaded_type=2,loaded_offset=0)

@lru_cache(maxsize=1)
def controller(raw,key='excitebike'):
    assert digest(Path(Previous.__file__).read_bytes())==BASE_SHA;parser(raw)
    text=Previous.controller(raw,key);assert text.count('s.area_type==0')==2
    text=text.replace('s.area_type==0','s.area_type==2')
    Previous.Previous.Base.LuaRuntime().compile(text);return text

def metadata(raw,key='excitebike'):
    q=Previous.metadata(raw,key);q.update(controller_SHA256=digest(controller(raw,key).encode()),underground_factory_SHA256=digest(Path(__file__).read_bytes()),
        stage='World0/Level1/Area2/AreaType2/loaded offset0',actual_owning_parser=parser(raw),controls_identical=True,
        retained_type0_observer_bound=dict(controller='1a9b4cc785437ee7a3b5b23789631b284b36f9904cf5045184226269059d9223',driver_passes=8000),
        causal_endpoint_diagnostic='b443b0ed8926b9adb5e35962e7a625e88f758be134e0a2a6b51b5f7a24a70d05')
    return q

def family():return SimpleNamespace(W=W,N=N,controller=controller,metadata=metadata)
