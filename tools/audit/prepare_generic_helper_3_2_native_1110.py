"""Stage a controller-only Scrooge 3-2 helper witness."""

import argparse
import json
from pathlib import Path
import re

from current_roster_compact_11_v1 import linked, policy_dependencies
from nightly_patch_guard_v1 import check
from prepare_selected_native_packet_v1 import R, prepare, sha


ROM = R / 'build/generic-helper-wwf-native-1110/candidate.nes'
PIN = 'dad683110311fa7925dcc4c2ce0aff3bb645d5c51b1a68b2d5c0731052850e73'
NIGHTLY = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
RELEASED_PIN = 'f33c7b19d27309ab4e4771125a74360f978dba08bd807d25bc6307026e568734'
GLOBALS = R / 'build/roster-combined-1101-v3/candidate.lbl'
CONTROLLER = Path(__file__).with_name('generic_helper_3_2_native_1110.lua')
POLICY = R / 'tools/playthroughs/scrooge_native_policy.lua'
SYMBOLS = '''AreaAddrsLOffset AreaPointer AreaType Block_Buffer_1 CheatInvincible CheatStartLevel
    CrossoverBehaviorVersion CrossoverMenuIndex CrossoverMenuState CrossoverOptionsFocus
    CrossoverTitleDrawn DarkwingVariant DisableScreenFlag Enemy_Flag Enemy_ID Enemy_PageLoc
    Enemy_State Enemy_X_Position Enemy_Y_HighPos Enemy_Y_Position GameEngineSubroutine HpActorOwner
    HpRecord HpSlot LevelNumber NumberofLives OperMode OperMode_Task PlatformCollisionFlag
    Player_PageLoc Player_State PlayerStatus Player_X_Position Player_X_Speed Player_Y_HighPos
    Player_Y_Position Player_Y_Speed ScreenLeft_PageLoc ScreenLeft_X_Pos ScreenRight_PageLoc
    ScreenRight_X_Pos SelectedCharacter TimerControl WorldNumber ScPogo MmVY R0'''.split()


def hook(bank, pc, raw, prefix):
    at = 16 + bank * 8192 + (pc & 8191)
    data = raw[at:at + 3]
    assert data.startswith(bytes.fromhex(prefix)), (bank, hex(pc), data.hex())
    return dict(bank=bank, pc=pc, bytes=list(data))


def lua(value):
    if isinstance(value, dict):
        return '{' + ','.join(f'[{lua(key)}]={lua(item)}' for key, item in value.items()) + '}'
    if isinstance(value, list):
        return '{' + ','.join(map(lua, value)) + '}'
    return json.dumps(value)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output', type=Path, required=True)
    cli.add_argument('--released', action='store_true')
    args = cli.parse_args()
    out = args.output.resolve()
    assert out.is_relative_to(R / 'build') and out != R / 'build'
    proof = None
    if args.released:
        rom, pin = NIGHTLY, RELEASED_PIN
        guard = check(rom)
        assert guard['passed'] and guard['ROM_sha256'] == pin
    else:
        rom, pin = ROM, PIN
        proof = ROM.with_name('proof.json')
        receipt = json.loads(proof.read_text())
        assert receipt['passed'] and receipt['candidate_SHA256'] == pin
    current = rom.read_bytes()
    if proof:
        for patch in receipt['patches']:
            at, data = patch['file_offset'], bytes.fromhex(patch['new_hex'])
            assert current[at:at + len(data)] == data

    _, _, address, location, _ = linked(GLOBALS.with_suffix('.nes'))
    # Current 32-slot layout uses a computed vertical transition. The old
    # X5MenuDown and X5MenuCharacters label addresses were reused as code.
    at = location('NrMenuNavigate')
    assert current[at + 26:at + 33] == bytes.fromhex('ad08732904f004')
    assert current[at + 33:at + 37] == bytes.fromhex('2086a060')
    menu_bank = 16 + 124 * 8192
    assert current[menu_bank + 0x86:menu_bank + 0x91] == bytes.fromhex('088a186908291f28090060')
    slot = 8
    at = location('NrMenuCharacter')
    assert current[at:at + 3] == bytes.fromhex('4ceead')
    assert current[menu_bank + 0xdee:menu_bank + 0xdf1] == bytes.fromhex('4ca1a0')
    assert current[menu_bank + 0xa1:menu_bank + 0xa4] == bytes.fromhex('bd40a0')
    assert current[menu_bank + 0x40 + slot] == 12
    known_helper_ram = {'HpActorOwner': 0x73ae, 'HpRecord': 0x738a, 'HpSlot': 0x73d4}
    addresses = {name: known_helper_ram[name] if name in known_helper_ram else address(name)
                 for name in SYMBOLS}
    carry_pc = address('PositionPlayerOnHPlat')
    assert (location('PositionPlayerOnHPlat') - 16) // 8192 == 0 and carry_pc == 0xb683
    hooks = {
        'scan': hook(26, 0xad0b, current, 'ad8273'),
        'free': hook(26, 0xad56 if args.released else 0xad55, current, 'a005'),
        'construct': hook(2, 0xa74f, current, 'a90095'),
        'carry': hook(0, carry_pc, current, 'a57518'),
    }
    config = dict(rom=pin, root=R.as_posix(), policy=POLICY.as_posix(), slot=slot,
                  hooks=hooks, symbols=addresses, released=int(args.released))
    script = CONTROLLER.read_text(encoding='utf-8')
    assert not re.search(r'\bemu\.(?:write\w*|setState|loadSavestate|reset)\s*\(', script)
    policies = policy_dependencies(POLICY)
    reads = re.compile(r"\br\('([A-Za-z_0-9]+)'")
    referenced = set(reads.findall(script))
    for policy in policies:
        referenced.update(reads.findall(policy.read_text()))
    # Stage-specific branches in the shared policy also resolve correctly.
    for name in referenced - addresses.keys():
        addresses[name] = address(name)
    refs = {Path(__file__), CONTROLLER, GLOBALS.with_suffix('.dbg'),
            R / 'tools/audit/current_roster_compact_11_v1.py',
            R / 'tools/audit/sound_cheats_menu_native_v1.lua',
            R / 'tools/reference/generic_helper_camera_1110.s',
            R / 'src/crossover_helpers.s', R / 'src/crossover_helper_data.inc',
            R / 'src/cheats.s', R / 'src/level_tiles.s', R / 'src/common.s',
            R / 'docs/qa/generic-helper-capacity-1110.md', *policies}
    if proof:
        refs.add(proof)
    prepare(out, rom, 'local witness = ' + lua(config) + '\n' + script, refs,
            expected=pin, timeout=240, allow_interactive=True,
            rom_symbols=(GLOBALS, GLOBALS.with_suffix('.dbg')) if args.released else None,
            scope='Easy Scrooge 3-2 via real Start Level menu; native slot occupancy, '
                  'offscreen construction and edge visibility through a no-loss stage exit.'
                  if args.released else 'Private Easy Scrooge 3-2, including native platform carry.')


if __name__ == '__main__':
    main()
