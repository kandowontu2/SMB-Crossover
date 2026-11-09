"""Stage both controller-only manual-platform checks from a qualified manifest."""
import argparse
import json
from pathlib import Path

from check_getsu_giant_rebase_1110 import W
from check_tmnt_render_oa import address
from nightly_patch_guard_v1 import check
from prepare_selected_native_packet_v1 import R, prepare, sha

BASE = R / 'build/mega-giant-current-native-1110/candidate.nes'
PIN = '94650fbc11ede25b9d08e579bdc6b1d6da81fca8f29c6b0c25dadad2e685ede1'
SYMBOL_BASE = R / 'build/shared-sparse-draw-native-1110/candidate.nes'
SOURCE = R / 'tools/playthroughs/manual_platform_1110.lua'
NAMES = '''OperMode OperMode_Task GameEngineSubroutine SelectedCharacter
CrossoverTitleDrawn DisableScreenFlag CrossoverMenuState CrossoverMenuIndex
Player_X_Position Player_PageLoc Player_Y_Position Player_State NumberofLives
Enemy_Flag Enemy_ID Enemy_State Enemy_X_Position Enemy_PageLoc Enemy_Y_Position
CheatStartLevel CheatInvincible'''.split()


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output', type=Path, required=True)
    cli.add_argument('--proof', type=Path, required=True)
    args = cli.parse_args()
    out, proof_path = args.output.resolve(), args.proof.resolve()
    assert out.is_relative_to(R / 'build') and out != R / 'build' and not out.exists()
    proof = json.loads(proof_path.read_text())
    assert proof['passed'] and proof['parent_SHA256'] == sha(BASE) == PIN
    refs = {Path(__file__), SOURCE, BASE, proof_path}
    for name, digest in proof['bindings'].items():
        p = R / name
        assert sha(p) == digest, name
        refs.add(p)
    assert check(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes'))['ROM_sha256'] == PIN
    parent = BASE.read_bytes()
    raw = bytearray(parent)
    used = set()
    for patch in proof['patches']:
        start = patch['file_offset']
        before, after = (bytes.fromhex(patch[k]) for k in ('old_hex', 'new_hex'))
        assert before and len(before) == len(after) and start >= 16 and start+len(before) <= len(raw)
        assert raw[start:start+len(before)] == before
        offsets = set(range(start, start+len(before)))
        assert not used & offsets
        used.update(offsets)
        raw[start:start+len(before)] = after
    import hashlib
    digest = hashlib.sha256(raw).hexdigest()
    assert digest == proof['expected_memory_only_SHA256']
    b = W.bundle(parent)
    assert address(b, 'GameLoop') == 0x82d9
    ram = ','.join(f'{n}={address(b,n)}' for n in NAMES)
    # Success hook is bound to the actual published native constructor tail.
    spawn = 0xb3f7
    physical = 64*8192+(spawn & 8191)
    assert raw[16+physical:16+physical+3] == bytes((0xe8, 0x8a, 0x60))
    out.mkdir()
    rom = out / 'candidate.nes'
    rom.write_bytes(raw)
    for owner, name, center, keys in ((41, 'mini', 4, ['select']*8),
                                      (34, 'karnov', 8, ['left', 'select'])):
        menu = ','.join(json.dumps(k) for k in keys)
        config = (f'local C={{rom="{digest}",owner={owner},actor=37,marker=65,width=32,'
                  f'player_center={center},main=0x82d9,main_physical={126*8192+0x2d9},'
                  f'spawn={spawn},spawn_physical={physical},spawn_mem="nesPrgRom",'
                  f'menu_keys={{{menu}}},ram={{{ram}}}}}\n')
        prepare(out / name, rom, config+SOURCE.read_text(), refs, expected=digest,
                timeout=90, allow_interactive=True,
                rom_symbols=(SYMBOL_BASE.with_suffix('.lbl'), SYMBOL_BASE.with_suffix('.dbg')),
                scope='Actual menu and native manual-platform input, movement, carry and replacement; no RAM writes.')
    print('Manual platform candidate staged:', digest)


if __name__ == '__main__':
    main()
