"""Profile exact-nightly Mini using the existing controller-only smoke replay."""
import argparse
from pathlib import Path
import re
import subprocess
import sys

from observe_chip_committed_write import lua
from prepare_selected_native_packet_v1 import R, prepare, sha

BASE = R / 'build/mini-power-regression-root-1103-v60/smoke49/controller.lua'
ROM = R / 'build/mini-power-candidate-root-1103-v56/mini-power.nes'
KERNEL = R / 'build/mini-mario-power-contract-1103-v51/mini-host-v56.lbl'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--rom', type=Path, default=ROM)
    parser.add_argument('--controller', type=Path, default=BASE)
    parser.add_argument('--labels', type=Path, default=KERNEL)
    parser.add_argument('--plain', action='store_true', help='Run the exact regression replay without timing callbacks.')
    parser.add_argument('--idle-updates', type=int, default=20)
    parser.add_argument('--render-details', action='store_true')
    parser.add_argument('--bg-labels', type=Path)
    parser.add_argument('--sample-x', type=int)
    args = parser.parse_args()
    controller = args.controller.read_text()
    digest = sha(args.rom)
    baseline = sha(ROM)
    assert digest in controller or baseline in controller
    controller = controller.replace(baseline, digest)
    assert 20 <= args.idle_updates <= 180
    if args.idle_updates != 20:
        anchor = "if n>=20 then transition('right')end"
        assert controller.count(anchor) == 1
        controller = controller.replace(anchor, f"if n>={args.idle_updates} then transition('right')end")
    labels = dict((name, int(pc, 16)) for pc, name in
                  re.findall(r'^al ([\dA-Fa-f]+) \.(\w+)$', args.labels.read_text(), re.M))
    refs = [args.controller, args.labels, Path(__file__)]
    if args.labels.resolve() != KERNEL.resolve():
        kernel = args.labels.with_suffix('.bin')
        binary = kernel.read_bytes()
        controller = controller.replace(sha(KERNEL.with_suffix('.bin')), sha(kernel))

        def relink(match):
            name = match[1]
            pc = labels[name]
            data = binary[pc-0xa000:pc-0xa000+4]
            return lua(dict(name=name, pc=pc, physical=pc-0x4000, memory='nesWorkRam', bytes=list(data)))

        controller = re.sub(r'\{\["name"\]="(Mini\w+)",\["pc"\]=\d+,\["physical"\]=\d+,'
                            r'\["memory"\]="nesWorkRam",\["bytes"\]=\{[\d,]+\}\}', relink, controller)
        refs.append(kernel)
    if args.plain:
        prepare(args.output, args.rom, controller, refs,
                expected=digest, timeout=240, scope='Existing controller regression on exact Mini candidate.',
                allow_interactive=True)
        return subprocess.call([sys.executable, '-B', args.output / 'run.py'])
    observed = ['MiniHostMain', 'MiniStep', 'MiniNativeTile', 'MiniAnimate',
                'MiniHostDraw', 'MiniHostBox', 'MiniNativeDraw']
    hooks = {name: [labels[name], -1] for name in observed}
    hooks.update(GameLoop=[0x82d9, 126], GameCoreRoutine=[0x839a, 126],
                 GuestGameRoutinesBridge=[0xe02b, 127], PlayerBGCollision=[0x9b5b, 126],
                 PlayerGfxHandler=[0xa2cd, 1], EnemiesAndLoopsCore=[0xa260, 0],
                 DrawAllMetasprites=[0xa000, 4], PlayerOAMReservation=[0xe0d2, 127],
                 CoCheckCode=[0xaee2, 65], CoCheckHeaders=[0xaf27, 65])
    if args.render_details:
        hooks.update(SamusFreezeDrawAll=[0xa2b1, 4], HpGraphicsBankCopy=[0x8369, 126],
                     CrossoverGraphicsBank=[0xe7bd, 127], WorldFirebarAdmission=[0xa261, 4],
                     KbOamPriority=[0xacf7, 72], RlSpecialDrawDispatch=[0xbbc5, 78],
                     KbDrawDispatch=[0xbfcc, 4], DrawBrickDebris=[0xa286, 4],
                     MegaManFullShotBank=[0x90d2, 126], HotPlayerGraphics=[0xb3c2, 66],
                     GuestPlayerVisible=[0x912b, 126], HandlePipeEntry=[0x9d69, 126],
                     X5BounceUiDispatch=[0xa297, 86])
    if args.bg_labels:
        debug_labels = dict((name, int(pc, 16)) for pc, name in
                            re.findall(r'^al ([\dA-Fa-f]+) \.(\w+)$', args.bg_labels.read_text(), re.M))
        for name in ['MiniBackground','BackgroundGuard','BackgroundHeight','ProbeFloor','ProbeSides']:
            hooks[name] = [debug_labels[name], 20]
        refs.append(args.bg_labels)
    observer = Path(__file__).with_suffix('.lua')
    old = 'local function result(ok,why)'
    assert controller.count(old) == 1
    controller = controller.replace(old, 'local profileFinish\n' + old +
                                    '\n if profileFinish then profileFinish() end')
    controller += '\nlocal MiniProfileHooks=' + lua(hooks) + '\n' + observer.read_text()
    if args.sample_x is not None:
        controller = controller.replace('local stack, hooks, stats, cadence = {}, {}, {}, {}',
            f'local sampleX={args.sample_x}\nlocal stack, hooks, stats, cadence = {{}}, {{}}, {{}}, {{}}')
    prepare(args.output, args.rom, controller,
            [*refs, observer], expected=digest,
            timeout=180, scope='Stack and physical-bank matched Mini 1-1 timings, lag NMI count and update cadence.',
            allow_interactive=True)
    return subprocess.call([sys.executable, '-B', args.output / 'run.py'])


if __name__ == '__main__':
    raise SystemExit(main())
