"""Strict79fd auth-only rebind of frozen missile/full/Bomb/HUD controls."""
from pathlib import Path
from functools import lru_cache
import current_rogue_hud_scene_dirty79fd_1116 as J
import replay_rogue_missile_cb95_1116 as Core
import replay_rogue_natural_bomb_cb95_1116 as Bomb
import replay_rogue_hud_continuity_cb95_1116 as Hud
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,H,N,W,Frames,PIN=J.R,J.ROM,J.H,J.N,J.W,J.Frames,J.PIN
J_SHA='bcd2f6aea2e6598eeff2ef7aee4a34f195c049e653fcb9b584596af1f9d07868'
PINS={Core:'723f56157c1fa5602ef4a68fc248979109f36bc1adbc48a5468f23af8e0b502a',
 Bomb:'5de4679e9d1726a81cfd08afe1d5fd5c953848832443041849fa5945b6fee1ac',
 Hud:'c229563433813c269dfe63a22e71da2e60bfff32dff10c5207ed2c39f9ef596d'}


@lru_cache(maxsize=5)
def pack(raw,kind='missile',source=False):
    assert kind in('missile','full','bomb','hud')and(not source or kind=='hud')
    assert H(Path(J.__file__).read_bytes())==J_SHA
    ref=J.reference(raw)
    parent=Hud if kind=='hud'else Bomb if kind=='bomb'else Core
    assert H(Path(parent.__file__).read_bytes())==PINS[parent]
    old=(Hud.controller(ref,source)if kind=='hud'else Bomb.controller(ref)if kind=='bomb'else Core.controller(ref,kind))
    assert old.count(J.Previous.PIN)==1
    assert 'bank_SHA256'not in old.split('\n',1)[0]
    text=old.replace(J.Previous.PIN,PIN,1)
    assert text.replace(PIN,J.Previous.PIN,1)==old
    assert text.split('\n',1)[1]==old.split('\n',1)[1]
    LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','saveState','loadState','io.open','takeScreenshot'))
    return text,dict(owning_SHA256=PIN,metadata_reference_only_SHA256=J.Previous.PIN,
        kind=kind,source_only=source,factory_SHA256=H(Path(__file__).read_bytes()),
        frozen_factory_SHA256=PINS[parent],controller_SHA256=H(text.encode()),
        reference_controller_SHA256=H(old.encode()),exact_frozen_functional_body=True,
        exact_original_assertions_and_endpoints=True,auth_only_rebound=True,
        hud_positive_gate_required_in_source_or_native_runner=kind=='hud',
        config_has_no_stale_fullbank_pins=True,outputs=0,native=False)


def controller(raw,kind='missile',source=False):return pack(raw,kind,source)[0]
def metadata(raw,kind='missile',source=False):return pack(raw,kind,source)[1]
