"""Strict7a80 two-picture Gimmick/Goomba/Mushroom observer, no game changes."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import compose_gimmick_empty_side_1115 as C
import replay_gimmick_empty_side_current_1115 as Core
import replay_gimmick_private_window7_1114 as Base
import compose_prince_window567_1115 as Window
import compose_battletoads_native_service_1114 as BT
import compose_native_floatey_score_1114 as Score
import compose_battletoads_camera_handoff_1114 as Camera
import replay_smb1_alts_full11_1114 as Text

R,ROM,W,N,PIN=C.R,C.ROM,C.W,C.N,C.CURRENT_CANDIDATE
IDENTITIES=Base.IDENTITIES
Frozen,normalize=Core.Frozen,Core.normalize
PARENT_SOURCE='fe03002ad912ce9957a7fae5f903f45323e9ac43b8a492278a1c47c12228f9d6'
IMAGE_SOURCE='fcd445cc22abbbc7e09450c4ef96d8feb847d85eede0a7805e20f206667f5281'


@lru_cache(maxsize=1)
def reference(raw):
    old590=Core.reference590(raw);ae=Window.inverse(old590);old571=BT.inverse(ae);f11=Score.inverse(old571);cf7=Camera.inverse(f11)
    assert sha256(cf7).hexdigest()==Base.PIN
    assert sha256(Path(Base.__file__).read_bytes()).hexdigest()==PARENT_SOURCE
    assert sha256(Path(Base.Images.__file__).read_bytes()).hexdigest()==IMAGE_SOURCE
    return cf7


@lru_cache(maxsize=1)
def recipe(raw,key='mr_gimmick'):
    old=reference(raw)
    # The old image recipe extends Stage.bindings' RAM dictionary. Supply a
    # private deep copy so it cannot mutate any stage/stock factory cache.
    original=Base.Images.Stage.bindings
    def independent(image,identity='mr_gimmick'):return deepcopy(original(image,identity))
    with patch.object(Base.Images.Stage,'bindings',independent):
        old_config=deepcopy(Base.image_bindings(old,key));text=Base.image_controller(old,key)
    prefix='local C='+Text.lua(old_config)+'\n';assert text.startswith(prefix)
    config=deepcopy(old_config);config['sha']=PIN
    for name,hook in config['hooks'].items():
        at=16+hook['offset'];assert raw[at:at+len(hook['bytes'])]==bytes(hook['bytes']),name
        if'bank'in hook:
            at=16+hook['bank']*8192;hook['bank_SHA256']=sha256(raw[at:at+8192]).hexdigest()
    assert config['maximum_images']==2 and config['maximum_PNG_bytes']==65536
    result='local C='+Text.lua(config)+'\n'+text[len(prefix):];Frozen.LuaRuntime().compile(result)
    assert result.split('\n',1)[1]==text.split('\n',1)[1]
    assert not any(s in result for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState'))
    return config,result,sha256(text.encode()).hexdigest()


def bindings(raw,key='mr_gimmick'):return recipe(raw,key)[0]
def controller(raw,key='mr_gimmick'):return recipe(raw,key)[1]


def metadata(raw,key='mr_gimmick'):
    config,text,parent_lua=recipe(raw,key)
    return dict(ROM_SHA256=PIN,identity=key,controller_SHA256=sha256(text.encode()).hexdigest(),
        navigation=config['navigation'],parent_cf7_SHA256=Base.PIN,parent_factory_SHA256=PARENT_SOURCE,parent_image_source_SHA256=IMAGE_SOURCE,
        parent_image_controller_SHA256=parent_lua,unchanged_control_and_observation_body=True,independent_deep_copied_bindings=True,
        maximum_images=2,maximum_PNG_bytes=65536,actual_current_hook_bytes_and_bank_hashes=True,
        strict_chain='Gm.inverse→16a;PrinceBody.inverse→590;PrinceWindow.inverse→ae66;BTService.inverse→571;Score.inverse→f11;BTCamera.inverse→cf7',
        scope='Private7a80 opening hero/Goomba and hero/mature-Mushroom images only; ends before pickup, no collector/fullstage qualification',
        gameplay_seeds=0,outputs=0,Mesen_run=False)
