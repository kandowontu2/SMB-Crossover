"""Strict current67 source arena with actual compiled5-1 level selection."""
from pathlib import Path
import inspect
import current_prince_oneup_67e3_1115 as Previous

C,N,W,Game,Frames,PIN=Previous.C,Previous.N,Previous.W,Previous.Game,Previous.Frames,Previous.PIN
prepare=Previous.prepare

def level_menu_unit(m):
    assert N.get(m,'CheatInvincible')==0 and N.get(m,'CheatStartLevel')==0
    rows=[]
    for _ in range(16):
        N.put(m,CrossoverOptionsFocus=1,CrossoverMenuPressed=1,VRAM_Buffer1_Offset=0)
        N.invoke(m,'CheatsMenuInput',a=0,x=0,y=0,p=0x21);rows.append(N.get(m,'CheatStartLevel'))
    assert rows==list(range(33,49))and N.get(m,'CheatInvincible')==0
    return rows

def cold(raw):
    prepare(raw)
    source=inspect.getsource(Game.cold);old='model = W.UI.seed(bundle, 29)';assert source.count(old)==1
    source=source.replace(old,old+'\n        menu_rows=level_menu_unit(model)',1)
    def owning(image):assert image==raw;return raw
    space=dict(Game.__dict__,proof_parent=owning,level_menu_unit=level_menu_unit)
    exec(compile(source,str(Path(__file__))+':actual67-compiled-five1','exec'),space)
    m,opening=space['cold'](raw)
    assert N.get(m,'WorldNumber')==4 and N.get(m,'LevelNumber')==0
    assert N.get(m,'CheatInvincible')==0 and N.get(m,'CheatStartLevel')==48
    assert C.digest(m.bundle['raw'])==PIN
    opening.update(stage='5-1',compiled_start_level_input_rows=list(range(33,49)),actual_CPU_ROM_SHA256=PIN,
        binding_only_reference_SHA256=Previous.REFERENCE,all57_new_Bub_bytes_preserved=True,
        source_frontend='Compiled CheatsMenuInput mailbox unit, then actual Select/Start/parser/constructor',
        source_menu_vblank_limitation=True,gameplay_state_seeds=0)
    return m,opening
