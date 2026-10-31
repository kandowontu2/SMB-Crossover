"""Real CF menu resolve/Start -> native cold parser/lives/Main, source CPU only."""
from pathlib import Path
import collections
import hashlib
import json
import re
import sys
import traceback

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R / 'tools/audit'), str(R / 'tools')]
import cf_cold_warm_palette_parser_controls_v1 as P
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address

C, H = P.C, P.H
O = R / 'build/contra-force-menu-cold-parser-1031-v1'
J = R / 'build/contra-force-menu-admission-1031-v2/joint'
K = R / 'build/contra-force-p1-kernel-v1'
P.J = H.O = J
P.L = {n: int(v, 16) for v, n in re.findall(r'al ([0-9A-Fa-f]+) \.(\w+)', (K / 'runtime.lbl').read_text())}
P.CF += ['CfP1EarlyTag', 'CfP1LateEntry']
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def visible_body(m):
    # Real completed hardware sprite window0, never the CPU BG pattern view.
    pages = m.chr_latches
    records = [list(m[512 + i:516 + i]) for i in range(0, 256, 4) if m[512 + i] < 240]
    body = []
    for row in records:
        y, tile, attr, x = row
        start = (tile & 1) * 4096 + (tile & 254) * 16
        if start // 1024 != 0 or not 959 <= pages[0] < 968:
            continue
        lo = 16 + 128 * 8192 + pages[0] * 1024 + start % 1024
        pattern = m.bundle['raw'][lo:lo + 32]
        if any(pattern):
            body.append(row)
    return dict(body_window0_page=pages[0], visible_source_body_parts=body,
                P0=list(m.vram[0x3f11:0x3f14]), P1=list(m.vram[0x3f15:0x3f18]))


def main():
    assert not O.exists()
    O.mkdir()
    result = dict(passed=False, source_CPU=True, native=False, admitted=False,
                  actual_ready_menu_Start=True, explicit_future_block_bypass=False,
                  no_CF_RAM_or_Ready_preload=True, cohorts=[])
    try:
        stage = json.loads((J.parent / 'source-stage.json').read_text())
        for path, digest in stage['bindings'].items():
            assert sha(path) == digest, path
        b = qualified(J / 'candidate.nes')
        for variant in range(4):
            m = C.fresh(b, 0)
            H.put(m, CrossoverMenuIndex=30, FmGroups=variant << 3, FmAlts=0,
                  CrossoverMenuState=2, SelectedCharacter=0)
            front = [P.invoke(m, name) for name in ['MenuResolveCharacter', 'QueueSelection', 'DrawSelectionPreview']]
            assert H.get(m, 'SelectedCharacter') == 31 and H.get(m, 'FmGroups') & 24 == variant << 3
            pending = P.invoke(m, 'FmPending')
            assert pending['AXYP'][0] == 26 + variant and not pending['AXYP'][3] & 1
            assert m.ppu_reads == 0 and m.ram[2][0x1fe0] != 167
            H.put(m, CrossoverMenuButtons=0, SavedJoypad1Bits=16, SavedJoypad2Bits=0)
            start = P.invoke(m, 'CrossoverMenuInput')
            assert H.get(m, 'FmGroups') == variant << 3 and H.get(m, 'CrossoverMenuState') == 0
            assert start['counts'].get('IcGlobalInit') == 1 and start['counts'].get('QwBoot') == 1
            assert start['counts'].get('CmHostFresh') == 1 and start['A2_instructions'] == 0
            cont = P.invoke(m, 'NativeRareGameMenuRoutineCore::ChkContinue', a=start['AXYP'][0],
                            x=start['AXYP'][1], y=start['AXYP'][2], p=start['AXYP'][3])
            assert H.get(m, 'OperMode') == 1 and H.get(m, 'OperMode_Task') == 0
            P.invoke(m, 'PauseRoutine', a=0)
            setup, frames, lives = [], [], []
            cohort = dict(variant=variant, real_frontend=front, pending=pending, real_Start=start,
                          native_continue=cont, parser=setup, visible_lives=lives, frames=frames)
            result['cohorts'].append(cohort)
            for age in range(600):
                if H.get(m, 'OperMode_Task') == 3 and H.get(m, 'GameEngineSubroutine') == 8:
                    break
                H.put(m, SavedJoypadBits=0, SavedJoypad1Bits=0, SavedJoypad2Bits=0,
                      A_B_Buttons=0, Left_Right_Buttons=0, Up_Down_Buttons=0, NmiDisable=255)
                z = P.invoke(m, 'GameLoop')
                nmi = C.A.consume(m)
                witness = visible_body(m)
                setup.append(dict(age=age, task=H.get(m, 'OperMode_Task'), screen=H.get(m, 'ScreenRoutineTask'),
                                  engine=H.get(m, 'GameEngineSubroutine'), Main=z, NMI=nmi, body=witness))
                if witness['visible_source_body_parts'] and H.get(m, 'OperMode_Task') != 3:
                    assert witness['P0'] == [55, 18, 15], ('Actual visible lives sourceP0', variant, age, witness)
                    lives.append(dict(age=age, **witness))
            else:
                raise AssertionError(('Native cold parser bound', variant, setup[-3:]))
            total = collections.Counter()
            for row in setup:
                total.update(row['Main']['counts'])
            assert total['CfLoaderProposal'] == 1 and total['CfHostConstruct'] == 1 and total['CfHostSceneEnsure'] == 1, total
            assert total['JnResetDispatch'] == 1 and total['native_BW_ctor_setup'] == 0, total
            assert m.ppu_reads == 24 * 1025 * 2 and m.ram[2][0x2e1] == 1
            assert any(m[address(b, 'Block_Buffer_1'):address(b, 'Block_Buffer_1') + 416])
            assert lives, ('No actual native lives source body', variant)
            for age in range(32):
                keys = 1 | (128 if 4 <= age < 12 else 0) | (64 if 16 <= age < 24 else 0)
                H.put(m, SavedJoypadBits=keys, SavedJoypad1Bits=keys, SavedJoypad2Bits=0,
                      A_B_Buttons=keys & 192, Left_Right_Buttons=keys & 3, Up_Down_Buttons=0, NmiDisable=255)
                z = P.invoke(m, 'GameLoop')
                nmi = C.A.consume(m)
                witness = visible_body(m)
                assert z['counts'].get('CfHostMovement') == 1 and z['counts'].get('CfHostDraw') == 1, ('Real gameplay source route', variant, age, z['counts'])
                assert z['counts'].get('CfP1LateEntry') == 1 and z['counts'].get('CfHostConstruct', 0) == 0
                assert not H.get(m, 'MmDeathFlag') and witness['visible_source_body_parts'], ('Actual game body missing/death', variant, age, witness)
                assert witness['P0'] == [55, 18, 15]
                frames.append(dict(age=age, input=keys, Main=z, NMI=nmi, body=witness))
            assert max(row['Main']['X'] for row in frames) > min(row['Main']['X'] for row in frames)
        result.update(passed=True, actual_classes=4, actual_gameplay_Main_updates=128,
                      real_menu_Start_no_bypass=True, actual_forcedblank_copy_verify_once_each=True,
                      full_ROM_guard_before_every_A2=True, actual_lives_and_game_body_physical_patterns_present=True)
    except Exception as error:
        result.update(error=repr(error), traceback=traceback.format_exc())
        raise
    finally:
        files = [Path(__file__), Path(P.__file__), Path(C.__file__), J.parent / 'source-stage.json',
                 J / 'candidate.nes', J / 'candidate.dbg', K / 'runtime.lbl']
        result['bindings'] = {str(p.resolve()): sha(p) for p in files}
        path = O / 'controls.json'
        path.write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps(dict(path=str(path), sha256=sha(path), passed=result['passed'], error=result.get('error'))), flush=True)


if __name__ == '__main__':
    main()
