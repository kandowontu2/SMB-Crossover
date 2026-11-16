"""Config-only cb95 binding of frozen missile/full/image control bodies."""
from pathlib import Path
from functools import lru_cache
import current_rogue_missile_cb95_1116 as J
import replay_rogue_earned_missile54b_1116 as Attack
import replay_rogue_full11_54b_1116 as Full
import replay_rogue_missile_two_images_54b_1116 as Pictures

R,ROM,H,N,W,Frames,PIN=J.R,J.ROM,J.H,J.N,J.W,J.Frames,J.PIN
PINS={Attack:'a1f9a70d72e839c4393818a271cd7a6f0be7a78b2c3ea2dae0e90d8937dc3cec',
 Full:'045fd3a05cce718c21e84599599abbb0c644d741a7a1756b96bf7a2e1a5692ed',
 Pictures:'e7f0e180e03b89d9bd3c9201ff29a67194ef8c58036cdc64fd5db7bada1994a5'}


@lru_cache(maxsize=3)
def pack(raw,kind='missile'):
    assert kind in('missile','full','pictures');q=J.bindings(raw);ref=J.reference(raw)
    F={'missile':Attack,'full':Full,'pictures':Pictures}[kind]
    assert H(Path(F.__file__).read_bytes())==PINS[F]
    old=F.controller(ref);assert old.count(J.Previous.PIN)==1
    assert 'bank_SHA256'not in old.split('\n',1)[0],'Refresh any new full-bank config explicitly'
    text=old.replace(J.Previous.PIN,PIN,1)
    assert text.replace(PIN,J.Previous.PIN,1)==old
    assert text.split('\n',1)[1]==old.split('\n',1)[1]
    return text,dict(owning_SHA256=PIN,metadata_reference_only_SHA256=J.Previous.PIN,
        factory_SHA256=H(Path(__file__).read_bytes()),frozen_factory_SHA256=PINS[F],kind=kind,
        controller_SHA256=H(text.encode()),reference_controller_SHA256=H(old.encode()),
        frozen_body_and_all_assertions_exact=True,auth_only_rebound=True,protected_Mini20_Sonic94=True,
        facade_banks_refreshed=True,config_has_no_stale_fullbank_pins=True,outputs=0,native=False)


def controller(raw,kind='missile'):return pack(raw,kind)[0]
def metadata(raw,kind='missile'):return pack(raw,kind)[1]
