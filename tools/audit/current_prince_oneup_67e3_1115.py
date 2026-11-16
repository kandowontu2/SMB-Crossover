"""Strict actual67 Prince route boundary; versioned7fb is binding-only."""
from functools import lru_cache
from pathlib import Path
import inspect
import compose_bub_selected_star_palette_prince_1115 as Bub
import prince_oneup_stage2_cold_7fb_1115 as Previous

C,N,W,Game,Frames=Previous.C,Previous.N,Previous.W,Previous.Game,Previous.Frames
PIN='67e3b8e7d4b01ea549fe9dc15c09b5a0b5f7085ee396d672a9c963d24287d0b5'
REFERENCE=C.CANDIDATE
BUB_SHA='79699547d00efeb3e90d2fb321d0a9195f02b7e1e91965759a5f6c888df9aeaa'

@lru_cache(maxsize=1)
def reference(raw):
    assert isinstance(raw,bytes)and C.digest(raw)==PIN,'Exact typed current67e3 required'
    assert C.digest(Path(Bub.__file__).read_bytes())==BUB_SHA
    old=Bub.inverse(raw);assert C.digest(old)==REFERENCE and Bub.proposal(old)[0]==raw
    owned=set(range(Bub.FILE,Bub.FILE+56))|set(range(Bub.COOKIE,Bub.COOKIE+16))
    assert sum(a!=b for a,b in zip(raw,old,strict=True))==57
    assert all(a==b for at,(a,b)in enumerate(zip(raw,old,strict=True))if at not in owned)
    assert C.Packet.extract(raw)==C.Packet.extract(old)
    assert raw[C.Packet.COOKIE:C.Packet.COOKIE+16]==old[C.Packet.COOKIE:C.Packet.COOKIE+16]
    # The other-family change is only its private CHR code and existing
    # cookie. Every native opcode/table used by Prince is byte-identical.
    assert Bub.FILE>=C.Packet.CHR
    assert all(a==b for at,(a,b)in enumerate(zip(raw[:C.Packet.CHR],old[:C.Packet.CHR]))if not Bub.COOKIE<=at<Bub.COOKIE+16)
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
    space=dict(Game.__dict__,proof_parent=owning,level_menu_unit=Previous.level_menu_unit)
    exec(compile(source,str(Path(__file__))+':actual67-compiled-stage2','exec'),space)
    m,opening=space['cold'](raw)
    assert N.get(m,'WorldNumber')==1 and N.get(m,'LevelNumber')==0
    assert N.get(m,'CheatInvincible')==0 and N.get(m,'CheatStartLevel')==36
    assert C.digest(m.bundle['raw'])==PIN
    opening.update(stage='2-1',compiled_start_level_input_rows=[33,34,35,36],
        actual_CPU_ROM_SHA256=PIN,binding_only_reference_SHA256=REFERENCE,all57_new_Bub_bytes_preserved=True,
        every_Prince_packet_cookie_and_native_opcode_exact7fb=True,
        source_frontend='Compiled CheatsMenuInput mailbox unit, then actual Select/Start/parser/constructor',
        source_menu_vblank_limitation=True,gameplay_state_seeds=0)
    return m,opening
