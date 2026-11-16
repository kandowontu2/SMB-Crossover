"""Measured four-pixel earlier moving catch; exact head controls unchanged."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_excitebike_star_bounce_ready5_91dc_1116 as Previous
import replay_smb1_alts_full11_1114 as Text

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest
BASE_SHA='3cd4f3a45bce587ce2b78400db78bc618ca437961837ec12365d436ce424162c'


@lru_cache(maxsize=1)
def controller(raw,key='star'):
    assert key=='star'and digest(Path(Previous.__file__).read_bytes())==BASE_SHA
    text=Previous.controller(raw,key);prefix,body=text.split('\n',1)
    old='local goal=a.x+(a.vx/16)*lead-8';new='local goal=a.x+(a.vx/16)*lead-4'
    assert body.count(old)==1;body=body.replace(old,new,1)
    b=Current.bundle(raw);pc=W.address(b,'ExAirLaunch');at=Current.START+(pc&8191)
    h=dict(pc=pc,offset=3*8192+(pc&8191),work=True,bytes=list(raw[at:at+8]))
    observer="""hook('BounceAirLaunch',function()
 local q=stock.bounce;if not q then return end
 local e={state=state(),pc=emu.getState()['cpu.pc'],sp=emu.getState()['cpu.sp'],
  sourcePad=ram2(0x5c),previousPad=ram2(0x803),source374=ram2(0x374),
  after_completed_prelean=q.jump and q.takeoff or nil}
 if q.jump then q.admitted_launches=(q.admitted_launches or 0)+1;q.first_admission=q.first_admission or e
 else q.other_launches=(q.other_launches or 0)+1;q.first_other_launch=q.first_other_launch or e end
end)
"""
    marker="hook('GameLoop',function()";assert body.count(marker)==1;body=body.replace(marker,observer+marker,1)
    text=prefix+'\nC.hooks.BounceAirLaunch='+Text.lua(h)+'\n'+body
    Previous.Previous.Previous.Stock.Previous.LuaRuntime().compile(text);return text


def metadata(raw,key='star'):
    q=Previous.metadata(raw,key);q.update(controller_SHA256=digest(controller(raw,key).encode()),lead4_factory_SHA256=digest(Path(__file__).read_bytes()),
        retained_native_near_catch_negative='731e910e682fe9d1a1bacdd4e6d6f1feab2436c5a3d3eb42d9bdd80f75f8a20a',
        ordinary_lead_change='Goal is actual movingStarX+speedMatchLead-4 instead of-8:4px earlier; native near-catch was2px short',
        jump_controls_unchanged='Existing4 completed original prelean updates precede freshA; passive actualAirLaunch observer added, no jumpdefect claim',
        head_controls_unchanged=True)
    return q


def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
