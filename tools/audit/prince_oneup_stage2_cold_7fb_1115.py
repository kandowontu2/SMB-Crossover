"""Compiled level-selector input unit plus genuine Prince2-1 cold/constructor."""
from pathlib import Path
from unittest.mock import patch
import inspect,json
import current_prince_hidden_point67_ace_1115 as Current

C,N,W,Game,Frames=Current.C,Current.N,Current.W,Current.Game,Current.Frames

def level_menu_unit(m):
    assert N.get(m,'CheatInvincible')==0 and N.get(m,'CheatStartLevel')==0
    rows=[]
    for _ in range(4):
        # UI input/focus and the established queue-consumption mailbox only.
        # No world/level/flag/ability/health/actor state is directly written.
        N.put(m,CrossoverOptionsFocus=1,CrossoverMenuPressed=1,VRAM_Buffer1_Offset=0)
        N.invoke(m,'CheatsMenuInput',a=0,x=0,y=0,p=0x21)
        rows.append(N.get(m,'CheatStartLevel'))
    assert rows==[33,34,35,36]and N.get(m,'CheatInvincible')==0
    return rows

def cold(raw):
    assert C.digest(raw)==C.CANDIDATE
    source=inspect.getsource(Game.cold);old='model = W.UI.seed(bundle, 29)';assert source.count(old)==1
    source=source.replace(old,old+'\n        menu_rows=level_menu_unit(model)',1)
    def owning(image):assert image==raw;return raw
    space=dict(Game.__dict__,proof_parent=owning,level_menu_unit=level_menu_unit)
    exec(compile(source,str(Path(__file__))+':compiled-level-menu-then-unchanged-cold','exec'),space)
    m,opening=space['cold'](raw)
    assert N.get(m,'WorldNumber')==1 and N.get(m,'LevelNumber')==0
    assert N.get(m,'CheatInvincible')==0 and N.get(m,'CheatStartLevel')==36
    opening.update(compiled_start_level_input_rows=[33,34,35,36],selected_world=1,selected_level=0,
        stage='2-1',source_frontend='Compiled CheatsMenuInput mailbox unit, then actual Select/Start/parser/constructor',
        source_menu_vblank_limitation=True,gameplay_state_seeds=0)
    return m,opening

def prepare(image):
    pin=C.digest(image);assert pin in(C.PIN,C.CANDIDATE)
    parent=C.inverse(image)if pin==C.CANDIDATE else image;raw,_=C.proposal(parent)
    assert pin!=C.CANDIDATE or raw==image;return raw

def tile(m,x,y):
    assert 32<=y<240
    return m[0x300+(208 if(x>>8)&1 else 0)+((x&255)>>4)+(y&240)-32]

if __name__=='__main__':
    captured=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
    def deny(*a,**k):raise AssertionError('Stage2 cold source attempted output/native launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        raw=prepare(captured);m,opening=cold(raw)
        for _ in range(8):m.controller_pad=0;Frames.frame(m,whole_pass=True)
        q=dict(passed=True,opening=opening,actual_CPU_ROM_SHA256=C.digest(m.bundle['raw']),
            first_platform144=[dict(x=x,tile=tile(m,x,144))for x in range(224,289,16)],
            current_native_state={name:N.get(m,name)for name in('WorldNumber','LevelNumber','AreaNumber','PlayerStatus','CheatInvincible','CheatStartLevel','NumberofLives')},
            no_natural_item_claim=True,outputs=0,Mesen=False)
    q['receipt_SHA256']=C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode());print(json.dumps(q,separators=(',',':')),flush=True)
