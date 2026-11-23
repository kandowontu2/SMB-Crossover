"""Earn the Spiny copy from Lakitu's live 4-1 spawn and test its needles in Mesen."""

import argparse
from hashlib import sha256
import json
from unittest.mock import patch

import compose_kirby_spiny_sound_1123 as Fix
import replay_kirby_buzzy_guard_native_1122 as Selected
import replay_kirby_stock_native_1122 as Kirby


STAGE_SELECTOR = 12
BODY = Kirby.R / 'tools/playthroughs/kirby_spiny_native_1123.lua'
RETAINED_SCRIPTS = {
    'right_easy': 'd86a4efa7c0da7cded535915348d0cb7eef58eed9ac9b8fad79a1b40c4cb8d0e',
    'right_hard': '248c060b8741a5145d6ce71a982a5886f192fefd9fa4bed4cc09acc1d90fdc30',
    'left_easy': '0574bce440ba5c57d96de32361b1fb8a2ca35905c750bcd9ae0d5b58bac99b49',
    'left_hard': 'ab88ad92e07d73a1b6f9f251f573f760976bf0baea9f451b1e913ed7285cc26d',
    'green_full': '21006897ae2bf02861dd16620a4e7fc7e4bdd6cc19c932d05a192b3f92e35ad5',
    'red_catch': '2e8b0e1ad0edc039a95912e3a7b2786f9705ebcb2e6db30b09efb00f81f5bfa8',
}


def retained_checks(raw):
    """Verify the earlier inhale and shell controllers against the carried code."""
    assert sha256(raw).hexdigest() in (Fix.PARENT, Fix.CANDIDATE)
    start = 16 + 74 * 8192
    bank = Kirby.verified_weapon_bank(raw)
    reference = raw[:start] + bank + raw[start + 8192:]
    with patch.object(Kirby.Kirby, 'PIN', sha256(reference).hexdigest()):
        checks = {case: sha256(Kirby.Kirby.controller(reference, case).encode()).hexdigest()
                  for case in Kirby.Kirby.CASES}
    assert checks == RETAINED_SCRIPTS
    return dict(ROM=sha256(raw).hexdigest(), Kirby_bank_SHA256=sha256(bank).hexdigest(),
                retained_controllers=checks, native_replays_repeated=0, outputs=0)


def controller(raw, *, hard=False, pressure=False):
    assert sha256(raw).hexdigest() in (Fix.PARENT, Fix.CANDIDATE)
    assert sha256(Selected.RED.read_bytes()).hexdigest() == Selected.RED_SHA
    hooks = [('spinyBirth', 'ChpChpEx'), ('weaponUpdate', 'KbWeapons::Update'),
             ('copyAttack', 'KbWeapons::CopyAttack'),
             ('needleAudio', 'GuestSharedSfx::PlayFireballThrow'),
             ('needleContact', 'KbWeapons::Defeat'), ('needleConsumed', 'KbWeapons::Consumed'),
             ('weaponDone', 'KbWeapons::Done')]
    ram = ('CrossoverOptionsFocus', 'KbFloat', 'KbCooldown', 'FrameCounter', 'AreaPointer', 'KbSavedSlot',
           'KbShotType', 'KbShotKind', 'KbShotAge', 'KbShotX', 'KbShotPage', 'KbShotY',
           'KbShotVXHi', 'KbShotVYHi', 'Square1SoundQueue', 'GuestWorldQueues')
    config, base, lua = Kirby.inhale_parts(raw, hooks, ram)
    common = base[base.index('local function r('):base.index('local function finish(')]
    common = Kirby.replace_once(common,
        "r('WorldNumber')==0 and r('LevelNumber')==0 and r('AreaType')==1 and r('AreaAddrsLOffset')==5",
        "r('WorldNumber')==3 and r('LevelNumber')==0 and r('AreaType')==1")
    common = Kirby.replace_once(common, "r('CheatStartLevel')==0 and r('CheatInvincible')==0",
        "r('CheatInvincible')==0")
    common = Kirby.replace_once(common, "r('CrossoverBehaviorVersion')==0 and noCheats()",
        f"r('CrossoverBehaviorVersion')=={int(hard)} and r('CheatStartLevel')==0x2c and noCheats()")
    bindings = base[base.index('local function guarded('):base.index("hook('init'")]
    ref = Selected.RED.read_text(encoding='utf-8')
    frontend = ref[ref.index('local function wait('):ref.index('emu.addEventCallback(')]
    frontend = Kirby.replace_once(frontend, 'for i=1,14 do', f'for i=1,{STAGE_SELECTOR} do')
    if hard:
        frontend = Kirby.replace_once(frontend, " press('down');press('down');press('a')",
            " press('down');press('a')\n assert(r('CrossoverBehaviorVersion')==1,'Actual Hard selected')\n"
            " press('down');press('a')")
        frontend = frontend.replace('Actual Easy Kirby selection', 'Actual Hard Kirby selection')
    source = BODY.read_text(encoding='utf-8').replace('-- COMMON', common)
    source = source.replace('-- BINDINGS', bindings).replace('-- FRONTEND', frontend)
    result = config + f'\nC.pressure={str(pressure).lower()}\n' + source
    lua.compile(result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prior-checks', action='store_true')
    parser.add_argument('--hard', action='store_true')
    parser.add_argument('--pressure', action='store_true')
    parser.add_argument('--candidate', action='store_true')
    parser.add_argument('--install', action='store_true')
    args = parser.parse_args()
    guard = Kirby.check(Kirby.ROM)
    raw = Kirby.ROM.read_bytes()
    assert guard['ROM_sha256'] in (Fix.PARENT, Fix.CANDIDATE) and not guard['matching_patch_files']
    if args.prior_checks:
        print('KIRBY RETAINED ' + json.dumps(retained_checks(raw), separators=(',', ':')), flush=True)
        return
    if args.install:
        assert guard['ROM_sha256'] == Fix.PARENT and not args.hard and not args.pressure
    candidate = Fix.compose(raw) if args.candidate or args.install else raw
    digest = sha256(candidate).hexdigest()
    work = Kirby.OUT
    rom, script = work / 'candidate.nes', work / 'controller.lua'
    assert set(work.iterdir()) == {rom, script} and rom.read_bytes() == raw
    Kirby.require_free_workspace(Kirby.R, Kirby.ROM, allow_interactive=True)
    previous = script.read_bytes()
    replaced = installed = False

    def verify(path, hard, pressure):
        prepared = Kirby.check(path)
        assert prepared['ROM_sha256'] == digest and not prepared['matching_patch_files']
        script.write_bytes(controller(candidate, hard=hard, pressure=pressure).encode())
        result = Kirby.run(script, path, work / 'capture', digest, 130, long_no_capture=True)
        assert result['outputs_written'] == 0 and not result['images'] and Kirby.check(path) == prepared
        summary = dict(receipt=result['receipt'], receipt_SHA256=result['receipt_SHA256'],
                       script_SHA256=result['script_SHA256'], passed=result['passed'], downloads=path == Kirby.ROM)
        print('KIRBY SPINY ' + json.dumps(summary, separators=(',', ':')), flush=True)
        assert result['passed'], result['receipt']['reason']
        return result['receipt_SHA256']

    try:
        path = Kirby.ROM
        if candidate != raw:
            rom.write_bytes(candidate)
            path = rom
        if args.install:
            receipt = verify(path, False, True)
            verify(path, False, False)
            verify(path, True, False)
            assert Kirby.check(Kirby.ROM) == guard
            replaced = True
            Kirby.ROM.write_bytes(candidate)
            assert verify(Kirby.ROM, False, True) == receipt
            assert Kirby.ROM.read_bytes() == candidate
            installed = True
            print(f'Installed {digest} at {Kirby.ROM}; matching Downloads replay {receipt}', flush=True)
        else:
            verify(path, args.hard, args.pressure)
    finally:
        if not installed:
            if candidate != raw:
                rom.write_bytes(raw)
            if replaced:
                Kirby.ROM.write_bytes(raw)
            assert Kirby.check(Kirby.ROM) == guard
        script.write_bytes(previous)
        assert set(work.iterdir()) == {rom, script}
        assert rom.read_bytes() == Kirby.ROM.read_bytes() == (candidate if installed else raw)


if __name__ == '__main__':
    main()
