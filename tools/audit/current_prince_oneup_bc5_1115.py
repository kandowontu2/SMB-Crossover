"""Explicit owningbc5 Prince route boundary;67 is a binding reference only."""
from functools import lru_cache
from pathlib import Path
import inspect
import compose_hot_draw_bt_67e_1115 as Hot
import current_prince_oneup_67e3_1115 as Previous

C,N,W,Game,Frames=Previous.C,Previous.N,Previous.W,Previous.Game,Previous.Frames
PIN='bc5e275d1dd4dabab4b5b2def66f7643ae46aee17a31ab37887528b791594040'
REFERENCE=Previous.PIN
HOT_SHA='60bf0a62b3b81e56331d035aa32e11f580296f39c1f9d8223de55b02fbfff9e7'

@lru_cache(maxsize=1)
def reference(raw):
    assert isinstance(raw,bytes)and C.digest(raw)==PIN,'Exact typedbc5 required'
    assert C.digest(Path(Hot.__file__).read_bytes())==HOT_SHA
    old=Hot.inverse(raw);assert C.digest(old)==REFERENCE
    assert sum(a!=b for a,b in zip(raw,old,strict=True))==106
    assert raw[:Hot.FILE]==old[:Hot.FILE]and raw[Hot.FILE+Hot.SIZE:]==old[Hot.FILE+Hot.SIZE:]
    assert C.Packet.extract(raw)==C.Packet.extract(old)
    assert raw[C.Packet.COOKIE:C.Packet.COOKIE+16]==old[C.Packet.COOKIE:C.Packet.COOKIE+16]
    return old

def prepare(raw):reference(raw);return raw

def bind(text,raw):
    reference(raw);assert text.count(REFERENCE)==1 and PIN not in text
    out=text.replace(REFERENCE,PIN,1);assert out.replace(PIN,REFERENCE,1)==text
    return out

def cold(raw):
    reference(raw)
    source=inspect.getsource(Game.cold);old='model = W.UI.seed(bundle, 29)';assert source.count(old)==1
    source=source.replace(old,old+'\n        menu_rows=level_menu_unit(model)',1)
    def owning(image):assert image==raw;return raw
    space=dict(Game.__dict__,proof_parent=owning,level_menu_unit=Previous.Previous.level_menu_unit)
    exec(compile(source,str(Path(__file__))+':owningbc5-compiled-stage2','exec'),space)
    m,opening=space['cold'](raw)
    assert N.get(m,'WorldNumber')==1 and N.get(m,'LevelNumber')==0
    assert N.get(m,'CheatInvincible')==0 and N.get(m,'CheatStartLevel')==36
    assert C.digest(m.bundle['raw'])==PIN
    opening.update(stage='2-1',actual_CPU_ROM_SHA256=PIN,binding_only_reference_SHA256=REFERENCE,
        all106_HotNew_changes_preserved=True,complete_Prince_packet_and_cookie_exact67=True,
        source_frontend='Compiled level-menu input unit, then actual Select/Start/parser/constructor',
        source_menu_vblank_limitation=True,gameplay_state_seeds=0)
    return m,opening
