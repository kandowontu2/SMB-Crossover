"""Actual menu and palette consumers for the private Benj unlock candidate."""
from pathlib import Path
import hashlib
import importlib.util
import itertools
import json
import sys

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R / 'build/smb2-current-cold-init-v6'), str(R / 'tools/audit'), str(R / 'tools')]
O = R / 'build/benj-menu-unlocked-1030-v3'
J = O / 'joint'
spec = importlib.util.spec_from_file_location('benj_real_cold', R / 'build/smb2-current-cold-init-v6/controls.py')
T = importlib.util.module_from_spec(spec)
spec.loader.exec_module(T)
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def regs(c):
    return c.a, c.x, c.y, c.p, c.sp


def main():
    assert not (O / 'menu-palette-controls.json').exists()
    old, new = [scoped_load(p / 'candidate.nes') for p in [R / 'build/coherent62-lives-fixes-v1/joint', J]]
    assert sha(J / 'candidate.nes') == '98048319d382e7a5c4e7186704b6e3b939eda4eec9bdd6e098c402cbd30799b6'
    menu = []
    cycle = [0, 1, 5, 6, 2, 3, 4]
    q = T.make(new, 0)
    q.put(CrossoverMenuIndex=0, MarioVariant=0)
    for expected in cycle[1:] + [0]:
        q.put(CrossoverMenuPressed=32)
        c, tr, path, info = T.invoke(q, 'FmToggle', a=99, x=7, y=5)
        assert q.get('MarioVariant') == expected and c.p & 1
        T.invoke(q, 'MenuResolveCharacter')
        assert q.get('SelectedCharacter') == (8 if expected == 1 else 0)
        menu.append(dict(variant=expected, selected=q.get('SelectedCharacter')))
    palettes = []
    for variant, area, tier, player in itertools.product([5, 6], range(4), range(3), [0, 1]):
        q = T.make(new, 0)
        q.put(MarioVariant=variant, AreaType=area, PlayerStatus=tier, CurrentPlayer=player,
              VRAM_Buffer1_Offset=0, VRAM_Buffer1=0)
        c, tr, path, info = T.invoke(q, 'GetPlayerColors', a=91, x=3, y=5, p=0x71)
        end = q.get('VRAM_Buffer1_Offset')
        start = address(new, 'VRAM_Buffer1') + end - 7
        packet = bytes(q.m[start:start+8])
        colors = bytes.fromhex('163027' if variant == 5 else '0f3617')
        if not (packet[:3] == bytes.fromhex('3f1004') and packet[4:7] == colors):
            failure=dict(variant=variant,area=area,tier=tier,player=player,end=end,packet=packet.hex(),
                         expected_body=colors.hex(),BmColors_calls=path.count(T.key(new,'BmColors')),
                         body_callback=hex(address(new,'BmColors')),native=False)
            negative=O/'palette-consumer-negative.json'
            if not negative.exists():negative.write_text(json.dumps(failure,indent=2)+'\n')
            raise AssertionError(failure)
        assert packet[3] == [34, 34, 15, 15][area] and packet[7] == 0
        assert path.count(T.key(new, 'BmColors')) == 1
        palettes.append(dict(variant=variant, area=area, tier=tier, player=player, packet=packet.hex(), CPU=c.processorCycles))
    foreign = []
    for variant, area, tier, flags in itertools.product(range(5), range(4), range(3), [0x30,0x31,0x71,0xf1]):
        outcomes = []
        for b in [old, new]:
            q = T.make(b, 0)
            q.put(MarioVariant=variant, AreaType=area, PlayerStatus=tier, VRAM_Buffer1_Offset=0, VRAM_Buffer1=0)
            c, tr, path, info = T.invoke(q, 'GetPlayerColors', a=91, x=3, y=5, p=flags)
            outcomes.append((regs(c), T.app(q,tr), q.m.banks[:]))
        assert outcomes[0] == outcomes[1], ('Existing palette consumer', variant, area, tier, flags)
        foreign.append(dict(variant=variant, area=area, tier=tier, flags=flags))
    # Current cache retirement is real mapped WRAM. The older Arena memory
    # model correctly rejects its DFE0 write; use the existing four-bank
    # cartridge model, never suppress the write or substitute a callback.
    import ff_current_ready_cold_controls_v2 as C
    H=C.H
    own = []
    for variant, mode, player in itertools.product([5,6], [0,1], [0,1]):
        m=C.fresh(new,0)
        H.put(m,MarioVariant=variant,CrossoverMenuIndex=0,CrossoverBehaviorVersion=mode,CurrentPlayer=player)
        for label in ['MenuResolveCharacter','QueueSelection','DrawSelectionPreview']:
            C.invoke(m,label)
        H.put(m,SavedJoypad1Bits=16,SavedJoypad2Bits=0)
        C.invoke(m,'CrossoverMenuInput')
        assert H.get(m,'SelectedCharacter')==0 and H.get(m,'MarioVariant')==variant
        assert H.get(m,'BmOwner')==variant and bytes(m[0x5c60:0x5c68])==bytes(8)
        for frame in range(20):
            H.put(m,OperMode=1,OperMode_Task=3,GameEngineSubroutine=8,Player_Y_HighPos=1,
                  SavedJoypadBits=129 if frame<15 else 0,SavedJoypad1Bits=129 if frame<15 else 0,
                  NmiDisable=255,FamilyMainCommit=1,VRAM_Buffer1_Offset=0)
            C.invoke(m,'GameLoop')
            assert H.get(m,'BmOwner')==variant
        own.append(dict(variant=variant, mode=mode, player=player, native_Main_updates=20))
    d = dict(passed=True, CPU_only=True, native=False, candidate=sha(J/'candidate.nes'),
        menu_cycle=menu, actual_palette_packets=palettes, old_palette_comparisons=foreign,
        actual_Fresh_Main=own, limits=['No native PPU or full-level qualification.',
            'Special donor float enemy/ceiling/platform consumers and fire/star palette progression remain partial.'],
        bindings={str(p):sha(p) for p in [Path(__file__),J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',O/'source-stage.json']})
    (O/'menu-palette-controls.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(passed=True,candidate=d['candidate'],cycle=len(menu),palettes=len(palettes),foreign=len(foreign),own_updates=160)))


if __name__=='__main__':
    main()
