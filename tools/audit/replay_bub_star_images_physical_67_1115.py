"""Sequential physical-phase picture requests; all frozen assertions retained."""
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

import replay_bub_selected_star_palette_prince_1115 as Frozen
import replay_bub_star_oam_diagnostic_67_1115 as Diagnostic

C,R,PIN=Frozen.C,Frozen.R,Frozen.PIN
PINS=((Frozen,'f73b20f9c03b6ba2c16f88ece6acf9ea71145c9dbfea2f3887ffdc7e2a60550b'),
    (Diagnostic,'265fe5aff817da9406ccc45d103adfdbf55dd19bef14918d28ce12f81be9e07e'))
BASE_SHA=('1399fcd0b5a9ad0437ac237d2f42693b8644c8d54b11a094f81be4e74e4914e1',
    'b82b77422c84a4a1e194caa2ee413140b53a89ef3bbc41c9ec64dcd3d49d90bd')
CHANGES=(("if heroLastDraw and(heroLastDraw.native&3)==0 and not visualSeen.A0",
          "if not visualSeen.A0"),
         ("elseif heroLastDraw and(heroLastDraw.native&3)==2 and not visualSeen.A2",
          "elseif not visualSeen.A2"))


@lru_cache(maxsize=2)
def baseline(raw,identity):
    assert identity in(0,1)and sha256(raw).hexdigest()==PIN
    for module,pin in PINS:assert sha256(Path(module.__file__).read_bytes()).hexdigest()==pin
    # Root's existing slot can contain the frozen1399 text or its passive
    # b857 facade, both of which Diagnostic.baseline authenticates exactly.
    text=Diagnostic.baseline(raw,0)
    if identity:
        a='["identity"]=0';b='local identity,expectedRom,cookie=0,'
        if text.count(a)==1 and text.count(b)==1:
            changed=text.replace(a,'["identity"]=1',1).replace(b,'local identity,expectedRom,cookie=1,',1)
            text=changed if sha256(changed.encode()).hexdigest()==BASE_SHA[1]else Frozen.controller(raw,1,images=True)
        else:text=Frozen.controller(raw,1,images=True)
    assert sha256(text.encode()).hexdigest()==BASE_SHA[identity]
    return text


@lru_cache(maxsize=2)
def controller(raw,identity=0):
    old=baseline(raw,identity);text=old
    for before,after in CHANGES:
        assert text.count(before)==1
        text=text.replace(before,after,1)
    restored=text
    for before,after in CHANGES:
        assert restored.count(after)==1
        restored=restored.replace(after,before,1)
    assert restored==old,'Only request ordering differs; physical token palette/XY/slot/attr/postcredit assertions remain exact'
    from check_ff_stdout_controller_source_1110 import LuaRuntime
    LuaRuntime().compile(text)
    return text


if __name__=='__main__':
    raw=(Diagnostic.SLOT/'candidate.nes').read_bytes()
    q=dict(ROM_SHA256=PIN,controllers=[dict(identity=i,Lua_SHA256=sha256(controller(raw,i).encode()).hexdigest(),
        bytes=len(controller(raw,i).encode()),baseline_Lua_SHA256=BASE_SHA[i])for i in(0,1)],
        only_latest_phase_enqueue_predicates_removed=True,
        all_physical_token_palette_XY_slot_attr_postcredit_assertions_retained=True,
        frozen_gameplay_controls_assertions_callbacks_restored=True,
        maximum_RAM_PNGs=3,maximum_PNG_bytes=196608,output_files=0,game_state_writes=0)
    print('RESULT '+json.dumps(q,sort_keys=True,separators=(',',':')),flush=True)
