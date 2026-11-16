"""Two passive RAM pictures over the native-qualified natural Bomb route."""
from functools import lru_cache
from pathlib import Path
import replay_rogue_natural_bomb_cb95_1116 as F
import run_rogue_tank_images_root_1116 as Pictures
from check_ff_stdout_controller_source_1110 import LuaRuntime

R, ROM, H, PIN = F.R, F.ROM, F.H, F.PIN
BASE_SHA = '5de4679e9d1726a81cfd08afe1d5fd5c953848832443041849fa5945b6fee1ac'
BASE_LUA = '3395fd00a8ffae0e8448850be7b5d299d2f3e67876da6de71625acf1bf15665b'
PICTURES_SHA = '7823bb1bc64c7f8c31ef9afa286cbc66f44ccb05587c833dd40a068d9118b694'


def once(text, old, new):
    assert text.count(old) == 1, (old, text.count(old))
    return text.replace(old, new, 1)


@lru_cache(maxsize=1)
def controller(raw):
    assert H(Path(F.__file__).read_bytes()) == BASE_SHA
    assert H(Path(Pictures.__file__).read_bytes()) == PICTURES_SHA
    base = F.controller(raw)
    assert H(base.encode()) == BASE_LUA
    edits = (
        ('if finished then return end;finished=true',
         "if finished then return end;if reason=='natural-Bomb-and-lifecycle25'then assert(#visual.pictures==2,'Both actual Bomb pictures')end;finished=true"),
        ('Mesen_images=0}', 'Mesen_images=2,visual=visual}'),
    )
    text = base
    for old, new in edits:
        text = once(text, old, new)
    restored = text
    for old, new in reversed(edits):
        restored = once(restored, new, old)
    assert restored == base
    observer = Pictures.OBSERVER
    for old, new in (
        ('#visual.pictures==0 and mature and not collector',
         "#visual.pictures==0 and gear.started and stock=='bomb'and mature and mature.actor.private==208 and not collector"),
        ('#visual.pictures==1 and credit',
         "#visual.pictures==1 and gear.bomb and not gear.expiry and(r('RdWAction',gear.slot)==9 or r('RdWAction',gear.slot)==10)"),
        ('Mature Rogue energy tank', 'Mature earned Bomb upgrade'),
        ('Earned tank and resumed Rogue', 'Original Bomb explosion'),
        ('state=state(),PNG_bytes=#png',
         'state=state(),item=actor(5),shot=gear.bomb and bombShot(gear.slot)or nil,PNG_bytes=#png'),
    ):
        observer = once(observer, old, new)
    text = 'local visual={pictures={}}\n'+text+'\n'+observer
    assert text.count('emu.takeScreenshot()') == 1
    assert not any(v in text for v in ('emu.write', 'emu.setState', 'io.open', 'dofile', 'saveState', 'loadState'))
    LuaRuntime().compile(text)
    return text


def metadata(raw):
    return dict(ROM_SHA256=PIN, factory_SHA256=H(Path(__file__).read_bytes()),
        Lua_SHA256=H(controller(raw).encode()), base_Lua_SHA256=BASE_LUA,
        functional_body_and_controls_exact_after_observer_removal=True,
        maximum_RAM_PNGs=2, maximum_PNG_bytes_each=65536,
        maximum_visible_OAM_records_each=32, output_files=0, gameplay_writes=False,
        compile_only=True, native=False)


if __name__ == '__main__':
    import json
    print('RESULT '+json.dumps(metadata(ROM.read_bytes()), separators=(',', ':')), flush=True)
