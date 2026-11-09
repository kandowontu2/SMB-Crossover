"""Bind the Getsu controller observer to a composed private cartridge."""

import argparse
import json
from pathlib import Path
import shutil

import check_getsu_fuma_host_render_1110 as Render
from check_tmnt_render_oa import address, location
from prepare_selected_native_packet_v1 import R, prepare, sha


CONTROLLER = R / 'tools/playthroughs/getsu_fuma_host_1110.lua'
RENDER = R / 'build/getsu-host-render-1110/proof.json'
RENDER_V2 = R / 'build/getsu-host-render-1110-v2/proof.json'
SYMBOLS = '''Player_X_Position Player_PageLoc Player_Y_Position Player_Y_HighPos Player_State
ScreenLeft_X_Pos ScreenLeft_PageLoc GameEngineSubroutine NumberofLives SelectedCharacter WorldNumber
LevelNumber OperMode OperMode_Task Enemy_X_Position Enemy_PageLoc Enemy_Y_Position Enemy_Flag Enemy_ID
Enemy_State CrossoverTitleDrawn DisableScreenFlag CrossoverMenuState CrossoverMenuIndex Cv3Variant
CheatStartLevel CheatInvincible'''.split()
PROBE_SYMBOLS = ('CurrentOAMOffset', 'RgOamRotation', 'CurrentBankC')


def stage_packet(out, rom, source_proof, smoke=False, probe=False):
    proof = json.loads(source_proof.read_text())
    render_proof = RENDER_V2 if proof.get('renderer_installed') else RENDER
    rendering = json.loads(render_proof.read_text())
    assert proof['passed'] and rendering['passed']
    digest = sha(rom)
    assert digest == proof['expected_memory_only_SHA256'] and proof['parent_SHA256'] == Render.Owner.PIN
    draw = rendering['draw_address']
    assert draw == 0xa4be and proof['public_vector_rows']['2'] == draw
    raw = rom.read_bytes()
    b = Render.Owner.Page.bundle()
    atlas = Render.ART / 'atlas.chr'
    start = Render.Owner.Page.CHR + 990 * 1024
    art = atlas.read_bytes()
    assert raw[start:start + 1024] == art
    for name, bank, pc in (('GameLoop', 126, 0x82d9), ('FlagpoleCollision', 126, 0x9e47)):
        at = location(b, name)
        assert (at - 16) // 8192 == bank and address(b, name) == pc and raw[at:at + 5] == b['raw'][at:at + 5]
    symbols = (*SYMBOLS, *PROBE_SYMBOLS) if probe else SYMBOLS
    ram = ','.join(f'{n}={address(b,n)}' for n in symbols)
    atlas_bytes = ','.join(map(str, art))
    config = (f'local C={{rom="{digest}",draw={draw},main=0x82d9,flag=0x9e47,'
              f'tileAttribute={address(b,"MTileAttribute")},smoke={str(smoke).lower()},'
              f'probe={str(probe).lower()},ram={{{ram}}},atlas={{{atlas_bytes}}}}}\n')
    source = CONTROLLER.read_text(encoding='utf-8')
    prepare(out, rom, config + source, {Path(__file__), CONTROLLER, source_proof, render_proof, atlas},
            expected=digest, timeout=180, allow_interactive=True,
            scope='Private Getsu normal inputs, actual selector, native OAM/CHR and sword, ' +
                  ('first pipe only.' if smoke else 'full 1-1 into active 1-2.'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--rom', type=Path)
    parser.add_argument('--proof', type=Path, required=True)
    parser.add_argument('--smoke', action='store_true')
    parser.add_argument('--visual-probe', action='store_true')
    args = parser.parse_args()
    out, proof = args.output.resolve(), args.proof.resolve()
    if args.rom:
        stage_packet(out, args.rom.resolve(), proof, args.smoke, args.visual_probe)
        return
    receipt = json.loads(proof.read_text())
    if receipt.get('renderer_installed'):
        import check_getsu_loaded_stage_v2_1110 as Runtime
    else:
        import check_getsu_loaded_stage_1110 as Runtime

    assert out.is_relative_to(R / 'build') and not out.exists()
    out.mkdir()
    _, trial, *_ = Runtime.compose(out)
    expected = receipt['expected_memory_only_SHA256']
    assert Runtime.SHA(trial['raw']) == expected
    rom = out / 'candidate.nes'
    rom.write_bytes(trial['raw'])
    for suffix in ('.lbl', '.dbg'):
        shutil.copyfile(Render.Owner.Page.ROM.with_suffix(suffix), rom.with_suffix(suffix))
    stage_packet(out / 'native', rom, proof, args.smoke, args.visual_probe)


if __name__ == '__main__':
    main()
