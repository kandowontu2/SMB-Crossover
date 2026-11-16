"""Image-only cb95 binding; exact two-PNG54b observer and controls retained."""
from functools import lru_cache
from pathlib import Path
import current_rogue_missile_cb95_1116 as J
import replay_rogue_missile_two_images_54b_1116 as Previous

R,ROM,H,N,W,Frames,PIN=J.R,J.ROM,J.H,J.N,J.W,J.Frames,J.PIN
PREVIOUS_SHA='e7f0e180e03b89d9bd3c9201ff29a67194ef8c58036cdc64fd5db7bada1994a5'


@lru_cache(maxsize=1)
def pack(raw):
    J.bindings(raw);ref=J.reference(raw)
    assert H(Path(Previous.__file__).read_bytes())==PREVIOUS_SHA
    old=Previous.controller(ref);assert H(old.encode())=='42084db449c66fdf4c149d87c7b90ac841f09845a72108b42c48aa5e2910f104'
    assert old.count(J.Previous.PIN)==1 and old.startswith('local visual={pictures={}}\nlocal C=')
    text=old.replace(J.Previous.PIN,PIN,1);assert text.replace(PIN,J.Previous.PIN,1)==old
    start=old.index('local C=');end=old.index('\n',start)
    assert text[:start]==old[:start]and text[end:]==old[end:]
    assert 'bank_SHA256'not in old[start:end]
    return text,dict(owning_SHA256=PIN,controller_SHA256=H(text.encode()),factory_SHA256=H(Path(__file__).read_bytes()),
        reference_only_SHA256=J.Previous.PIN,reference_Lua_SHA256=H(old.encode()),
        second_line_config_only_rebound=True,exact_observer_controls_and_all_assertions=True,
        maximum_RAM_PNGs=2,maximum_PNG_bytes=131072,output_files=0,native_run=False)


def controller(raw):return pack(raw)[0]
def metadata(raw):return pack(raw)[1]


if __name__=='__main__':
    import json
    print('RESULT '+json.dumps(metadata(J.load_current_image()),separators=(',',':')),flush=True)
