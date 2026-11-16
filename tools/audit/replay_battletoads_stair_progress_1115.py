"""New ordinary BT stair-progress policy; frozen C/F/cadence remain intact."""
from functools import lru_cache
from pathlib import Path
import compose_hot_draw_bt_67e_1115 as C
import replay_hot_draw_bt_67e_1115 as Base

R,ROM,W,N=C.R,C.ROM,Base.W,Base.N
IDENTITIES=Base.IDENTITIES
BASE_SHA='e3c497579769eb2599651f78f8c788da892f3f540794f0a06624defbdf3cdc0a'
MONITOR=r'''
local btStairAnchorX,btStairAnchorY,btStairSamples=nil,nil,0
local function btStairNoProgress(c)
 if c.char~=33 or c.world~=0 or c.level~=0 or c.areaType~=1 or c.engine~=8
  or c.x<2160 or c.x>=2208 or c.y<112 or c.y>144 or not c.grounded then
  btStairAnchorX=nil;btStairAnchorY=nil;btStairSamples=0;return false
 end
 if btStairAnchorX==nil or math.abs(c.x-btStairAnchorX)>2 or math.abs(c.y-btStairAnchorY)>2 then
  btStairAnchorX=c.x;btStairAnchorY=c.y;btStairSamples=0;return false
 end
 btStairSamples=btStairSamples+1
 return btStairSamples>=16
end
'''


def sources(raw):
    assert C.H(Path(Base.__file__).read_bytes())==BASE_SHA
    Base.parent(raw)


def bindings(raw,key):
    sources(raw);return Base.bindings(raw,key)


normalize=Base.normalize


@lru_cache(maxsize=4)
def controller(raw,key='zitz'):
    sources(raw);assert key in IDENTITIES
    text=Base.controller(raw,key)
    marker="local rollGap='approach'";assert text.count(marker)==1
    text=text.replace(marker,MONITOR+'\n'+marker,1)
    marker=' local danger=e and e.dx>0 and e.dx<32 and math.abs(e.y-c.y)<45';assert text.count(marker)==1
    text=text.replace(marker,' local btStairStalled=btStairNoProgress(c)\n'+marker,1)
    marker='(obstacle or not support or danger or still>16)';assert text.count(marker)==1
    text=text.replace(marker,'(obstacle or not support or danger or still>16 or btStairStalled)',1)
    Base.Original.LuaRuntime().compile(text)
    assert '\r'not in text and not any(s in text for s in('emu.write','emu.setState','io.open','saveState','loadState','takeScreenshot'))
    return text


def metadata(raw,key=None):
    sources(raw)
    if key is not None:
        return dict(ROM_SHA256=C.H(raw),identity=key,controller_SHA256=C.H(controller(raw,key).encode()),
            base_controller_SHA256=C.H(Base.controller(raw,key).encode()),normal_controls_only=True,
            game_bytes_changed=False,gameplay_seeds=0,outputs=0)
    return dict(ROM_SHA256=C.H(raw),controllers={k:C.H(controller(raw,k).encode())for k in IDENTITIES},
        policy='Grounded stair progress window, normal existing jump condition only',
        domain=dict(world=0,level=0,areaType=1,engine=8,X_half_open=[2160,2208],Y_inclusive=[112,144]),
        anchor_tolerance_pixels=2,stationary_samples_before_trigger=17,
        original_lastA_release_and_jumpAge_logic_unchanged=True,original_clear_endpoint_unchanged=True,
        fixed80_cadence_body_untouched=True,game_bytes_changed=False,outputs=0,Mesen_run=False)
