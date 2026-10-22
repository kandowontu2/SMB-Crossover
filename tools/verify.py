"""Build and verify both NES ports in Mesen 2, with a Mario regression replay."""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jobs', type=int, default=4, help='Independent emulator processes (default 4)')
    parser.add_argument('--mmc5', action='store_true', help='Also run the guest checks on MMC5')
    parser.add_argument('--emulator', help='Mesen 2 path; otherwise uses MESEN or local discovery')
    parser.add_argument('--checkpoint', type=Path, help='Verify copied immutable ROMs without rebuilding; use the existing baseline ROM')
    args = parser.parse_args()
    cases = []
    verification = ROOT / 'build/verification'
    verification.mkdir(parents=True, exist_ok=True)

    def fixture_manifest() -> dict[str, str]:
        paths = sorted(path for path in (ROOT/'tests').rglob('*') if path.is_file())
        paths.append(ROOT/'tools/run_mesen.py')
        return {path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in paths}

    fixtures_before = fixture_manifest()

    def save_summary(report: dict) -> None:
        data = json.dumps(report, indent=2)+'\n'
        (verification/'summary.json').write_text(data)
        label = args.checkpoint.name if args.checkpoint else 'working-build'
        (verification/f'summary-{label}.json').write_text(data)

    save_summary({'result': 'running', 'checkpoint': str(args.checkpoint.resolve()) if args.checkpoint else None,
                  'fixture_hashes_before': fixtures_before})

    def rom_path(target: str) -> Path:
        directory = args.checkpoint.resolve() if args.checkpoint and not target.endswith('-baseline') else ROOT/'build'
        return directory/f'{target}.nes'

    def command(*arguments: str) -> None:
        subprocess.run([sys.executable, *arguments], cwd=ROOT, check=True)

    def test(name: str, target: str) -> None:
        arguments = [sys.executable, 'tools/run_mesen.py', f'tests/{name}.lua', str(rom_path(target)), '--timeout', '90']
        if name in ('water-motion-differential', 'water-expansion-differential',
                    'water-corner-differential', 'water-oam-differential'):
            arguments += ['--timeout', '80']
        if name == 'sophia-native-products':
            arguments += ['--timeout', '150']
        if name == 'scrooge-ceiling-separation':
            arguments += ['--timeout', '180']
        if args.emulator:
            arguments += ['--emulator', args.emulator]
        result = subprocess.run(arguments, cwd=ROOT, capture_output=True, text=True)
        print(result.stdout, end='')
        if result.stderr:
            print(result.stderr, end='')
        if result.returncode or 'PASS ' not in result.stdout:
            raise RuntimeError(f'{name} failed for {target}')
        cases.append({'test': name, 'rom': target, 'result': 'passed'})

    if not args.checkpoint:
        command('tools/build.py', '--baseline')
        command('tools/build.py')
    test('baseline', 'smb-crossover-mmc3-baseline')
    test('baseline', 'smb-crossover-mmc3')
    test('mario-trace', 'smb-crossover-mmc3-baseline')
    test('mario-trace', 'smb-crossover-mmc3')
    test('mmc3-bank-interrupt', 'smb-crossover-mmc3')
    verification = ROOT / 'build/verification'
    # Mario runs the source (2.02/original) profile, not stock SMB physics, so
    # the crossover replay is pinned to its frozen source-Mario reference; the
    # baseline replay above remains a stock boot/control smoke test.
    before = (ROOT/'tests/mario-trace-reference.csv').read_bytes()
    after = (verification/'smb-crossover-mmc3-mario-trace.csv').read_bytes()
    failures = []
    if before != after:
        failures.append('Mario state diverged from the frozen source-Mario replay.')
    else:
        print('PASS Mario: all 19 state fields match the source-Mario reference for 521 frames')
    mappers = ['mmc3']
    if args.mmc5:
        if not args.checkpoint:
            command('tools/build.py', '--mapper', 'mmc5')
        mappers.append('mmc5')
    names = ('character-select', 'player-outlines', 'player-outlines-render', 'title-character-switch', 'crossover', 'native-castle-source-pixels', 'guest-camera-anchor', 'pit-crouch-clearance', 'scrooge-ledge-corner', 'megaman-controls',
                     'megaman-interactions', 'megaman-physics', 'megaman-step-collision-202', 'megaman-buster',
                     'megaman-music', 'megaman-audio-effects', 'megaman-death',
                     'megaman-powerups', 'megaman-environment', 'megaman-oam',
                     'megaman-block-alignment', 'megaman-powerup-animation',
                     'mario-lives-screen', 'megaman-lives-screen', 'samus-lives-screen',
                     'samus-controls', 'samus-audio-effects', 'samus-pickup-sfx', 'samus-combat', 'samus-solid-blocks',
                     'samus-pipes', 'samus-powerups', 'samus-oam',
                     'megaman-scrolling','megaman-charged-scrolling','samus-scrolling',
                     'bill-controls','bill-collision-equivalence','link-controls','simon-controls',
                     'bill-lives-screen','link-lives-screen','simon-lives-screen',
                     'bill-powerup-animation','link-powerup-animation','simon-powerup-animation',
                     'bill-scrolling','link-scrolling','simon-scrolling',
                     'bill-projectiles-oam','link-projectiles-oam','simon-projectiles-oam',
                     'bill-combat','link-combat','simon-combat',
                     'bill-music','link-music','simon-music',
                     'megaman-lag-stress','megaman-projectiles-overload','bill-lag-stress','bill-stomp',
                     'bill-sprite-overload','link-block-rendering','link-block-alignment',
                     'simon-block-rendering','simon-adjacent-blocks','simon-pipes','samus-head-bricks',
                     'guest-fast-landings','bill-audio-isolation','link-audio-isolation','simon-audio-isolation',
                     'megaman-world-sfx','samus-world-sfx','bill-world-sfx','link-world-sfx','simon-world-sfx',
                     'mario-water','megaman-water','samus-water','bill-water','link-water','simon-water')
    added = ('pit','rygar','luigi','bass','ryu','sophia')
    names += tuple(f'{character}-{check}' for character in added
                   for check in ('controls','environment','systems','lives-screen','powerup-animation'))
    names += tuple(f'{character}-world-sfx' for character in added if character!='luigi')
    names += ('bass-weapons','bass-reference','ryu-weapons','pit-attacks','rygar-attacks','rygar-native-return','empty-metasprites')
    names += tuple(f'{character}-normal-death' for character in ('bill','link','simon','luigi','bass','ryu','sophia'))
    names += tuple(f'{character}-playlist' for character in ('bass','ryu','sophia'))
    names += ('link-beam-impact','link-sword-timing','ryu-source-weapons','bass-native-sfx','megaman-landing-sfx')
    names += ('pit-fresh-fire','luigi-fresh-fire','sophia-fresh-fire')
    names += ('guest-lag-chr','guest-loading-vram')
    names += ('bass-walk','rygar-walk','pit-flight','underground-bricks','rygar-playlist','rygar-music-loop')
    names += ('bass-inventory','bass-special-weapons','bass-special-enemies','bass-arm-question','bass-arm-question-stress')
    names += ('bass-energy-drops','bass-pickup-art','bass-pickup-rise','bass-pharaoh-follow',
              'bass-pharaoh-stock','bass-flame-contact','bass-armor','bass-source-sfx',
              'bass-water-audio','samus-weapon-families')
    names += tuple(f'{c}-flame-source-{theme}' for c in ('megaman','bass') for theme in range(4))
    names += ('bass-upgrade-random','bass-pickup-contact','bass-palette-stability',
              'bass-knuckle-blocks','bass-knuckle-vram','bass-knuckle-scroll')
    names += ('bass-head-upgrades','bass-pickup-exposed','bass-knuckle-native-capture')
    names += ('lance-select','lance-controls','lance-lives-screen','lance-powerup-animation',
              'world-springs','world-firebars','bill-world-objects')
    names += tuple(f'{character}-flagpole-full' for character in
                   ('mario','megaman','samus','bill','link','simon','pit','rygar',
                    'luigi','bass','ryu','sophia','lance'))
    names += ('mario-alternate-scrooge','scrooge-facing-portrait','scrooge-ability-arena','scrooge-cane-enemies','scrooge-pogo-enemies','remaining-source-sfx','megaman-inventory-202','megaman-rush-202','samus-passives-202','scrooge-lives-screen','scrooge-powerup-animation','scrooge-flagpole-full','simon-big-drops-202','ryu-big-drops-202')
    names += tuple(f'{c}-inventory-202' for c in ('samus','bill','link','simon','ryu','sophia'))
    names += tuple(f'{c}-energy-drops-202' for c in ('samus','link','simon','ryu','sophia'))
    names += ('samus-crouch-202', 'samus-crouch-power-forms', 'samus-head-displacement', 'samus-zero-wall-contact', 'samus-beam-rendering', 'bill-flare-limit-202',
              'bill-hud-split', 'bill-av-collision-equivalence',
              'sophia-collision-equivalence', 'sophia-homing-targets',
              'sophia-independent-weapons', 'megaman-special-armor-202',
              'guest-injury-scripted-state')
    names += tuple(f'{c}-melee-upgrades-202' for c in ('link', 'simon', 'ryu'))
    names += ('ryu-projectile-source-pixels', 'ryu-fire-source-pixels', 'ryu-projectile-origins')
    names += ('sophia-cannon-art', 'samus-bomb-block-equivalence', 'samus-bomb-initial-performance')
    names += ('sophia-attached-fire', 'sophia-cannon-upgrade-snapshot')
    names += ('sophia-missile-impact-art', 'sophia-impact-sequence',
              'sophia-homing-vector', 'sophia-homing-nearest',
              'sophia-homing-terrain', 'sophia-homing-lifetime')
    names += ('sophia-poweron-audio', 'sophia-native-products')
    names += ('sophia-missile-collision-equivalence',)
    names += ('guest-audio-flush-differential', 'scrooge-native-movement', 'scrooge-underhang',
              'scrooge-body-hitbox', 'scrooge-pogo-hitbox', 'scrooge-pogo-contact', 'scrooge-pogo-bowser', 'scrooge-ceiling-separation', 'scrooge-pogo-bump-support', 'guest-foot-corner-matrix',
              # Mario now runs his source profile; Luigi keeps the native
              # engine and its native-reference physics/water-pit comparisons.
              'luigi-native-physics', 'mario-native-death-control', 'mario-native-pipe-control',
              'luigi-native-water-pit',
              'mario-powerup-fire-arena')
    names += tuple(f'expanded-poweron-{c}' for c in (6,7,9,10,11,12))
    names += tuple(f'expanded-water-entry-{c}' for c in (6,7,9,10,11,12))
    names += ('guest-head-upper-extent', 'link-roof-jump', 'roster-stomp-audit',
              'guest-ordinary-contact', 'spin-body-contact-202',
              'megaman-body-contact-202', 'bass-body-contact-202')
    names += ('megaman-injury-202', 'bass-injury-202',
              'megaman-injury-input-202', 'bass-injury-input-202',
              'megaman-bass-hurt-profiles')
    names += ('samus-injury-202', 'samus-injury-morph-202', 'player-outline-cache')
    names += ('link-injury-source', 'simon-injury-source', 'ryu-injury-source',
              'link-injury-202', 'simon-injury-202', 'ryu-injury-202',
              'lsr-injury-endpoints', 'lsr-injury-hurt-profiles',
              'lsr-injury-body-pixels', 'lsr-injury-dpcm',
              'native-wall-corner', 'ryu-ground-wall-launch', 'firebar-draw-admission')
    names += ('link-source-movement', 'simon-source-movement',
              'link-source-kinematics', 'simon-source-jump-states',
              'link-source-body-contact', 'link-source-thrust-phase',
              'link-source-thrust-contact', 'link-source-thrust-blocks',
              'link-source-thrust-order', 'link-weapon-profile-202',
              'simon-weapon-profile-202')
    names += ('link-source-enemy-effects', 'simon-source-enemy-effects',
              'ryu-source-enemy-effects', 'link-boomerang-source-effects',
              'lsr-bowser-source-flash', 'link-source-enemy-effect-properties',
              'simon-source-enemy-effect-properties', 'ryu-source-enemy-effect-properties')
    names += ('native-freeze-admission', 'offscreen-helper-caller', 'enemy-bbox-caller', 'samus-empty-candidates',
              'bill-empty-candidates', 'sophia-empty-candidates',
              'sophia-late-input-candidates', 'link-effects-empty-gate',
              'simon-effects-empty-gate', 'ryu-effects-empty-gate',
              'bass-ordinary-body-layout', 'bill-ordinary-body-layout')
    names += tuple(f'{character}-injury-pixels-{theme}'
                   for character in ('megaman', 'bass') for theme in range(4))
    names += ('sophia-enemy-explosion-art', 'sophia-enemy-explosion')
    names += tuple(f'guest-water-upper-{c}' for c in (0,1,2,8,12))
    names += tuple(f'expanded-decoder-{c}' for c in (6,7,9,10,11))
    names += ('water-motion-differential', 'water-expansion-differential', 'water-left-source',
              'water-oam-differential', 'water-corner-differential',
              'megaman-bass-lone-boss', 'megaman-water-performance',
              'bass-water-performance')
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1,args.jobs)) as pool:
        pending = {pool.submit(test,name,f'smb-crossover-{mapper}'): (name,mapper)
                   for mapper in mappers for name in names}
        for future in concurrent.futures.as_completed(pending):
            try:
                future.result()
            except Exception as error:
                failures.append(str(error))
    cases.sort(key=lambda item:(item['rom'],item['test']))
    fixtures_after = fixture_manifest()
    changed_fixtures = sorted(path for path in fixtures_before.keys() | fixtures_after.keys()
                              if fixtures_before.get(path) != fixtures_after.get(path))
    if changed_fixtures:
        failures.append('Verification fixtures changed during the run: '+', '.join(changed_fixtures))
    summary = {
        'result': 'failed' if failures else 'passed', 'emulator': 'Mesen 2', 'hardware_tested': False,
        'mario_replay': {'frames': 521, 'fields': 19, 'identical': before == after},
        'cases': cases,
        'roms': {mapper: hashlib.sha256(rom_path(f'smb-crossover-{mapper}').read_bytes()).hexdigest()
                 for mapper in mappers},
        'checkpoint': str(args.checkpoint.resolve()) if args.checkpoint else None,
        'failures': failures,
        'fixture_hashes_before': fixtures_before,
        'fixture_hashes_after': fixtures_after,
        'changed_fixtures': changed_fixtures,
    }
    save_summary(summary)
    if failures:
        raise RuntimeError('\n'.join(failures))
    print(f'PASS all {len(cases)} emulator cases; evidence: {verification}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
