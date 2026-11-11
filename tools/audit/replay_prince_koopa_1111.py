"""Replay Prince's second-gap retreat and Koopa approach on the installed nightly."""

import argparse
import json
from pathlib import Path
import re

from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import R, digest, run


NIGHTLY = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
PIN = '4df817587ea5b0aff3f278a4201976745bad4d9dd1b2a99d6cb5fd3b9c74dadc'
PUBLISHED = R / 'tools/playthroughs/prince_original_first_pipe_stdout_1110.lua'
PUBLISHED_PIN = 'e9b45ae96c00ee55b456200f346ab2e4f22c78013a0820e98910ecddcc6dc65e'
TAIL = R / 'tools/playthroughs/prince_late_1111.lua'


def replace_once(source, expression, replacement):
    updated, count = re.subn(expression, lambda _: replacement, source, count=1)
    assert count == 1, expression
    return updated


def published_controller():
    assert digest(PUBLISHED) == PUBLISHED_PIN
    source = PUBLISHED.read_text(encoding='utf-8')
    source = replace_once(source, r'local function fourthAndGap\(s\)',
                          TAIL.read_text(encoding='utf-8') + '\nlocal function fourthAndGap(s)')
    source = replace_once(source, "      switch\\('second-gap-approach',1\\)",
                          "      switch('late-second-approach',1)")
    source = replace_once(source, r'  if firstPipe then\n    if #caps==2 then fourthAndGap\(s\) else laterTick\(s\) end',
                          "  if firstPipe then\n    if progress:sub(1,5)=='late-' then\n      afterSecondGap(s)\n"
                          '    elseif #caps==2 then fourthAndGap(s) else laterTick(s) end')
    source = replace_once(source, r'emu\.setInput\(\{right=pad&1~=0,',
                          'emu.setInput({right=pad&1~=0,left=pad&2~=0,')
    return source.replace('#events<52', '#events<100').replace('frame<=8000', 'frame<=16000')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--koopa-brake', type=int, action='append', choices=range(1450,1561))
    parser.add_argument('--koopa-mode', choices=('standing','climb','ledge','step'), default='climb')
    parser.add_argument('--koopa-jump-x', type=int, default=1501, choices=range(1491,1519))
    args = parser.parse_args()
    output = args.output.resolve()
    assert output.is_relative_to(R / 'build') and output != R / 'build'
    assert check(NIGHTLY)['ROM_sha256'] == PIN
    output.mkdir(exist_ok=True)
    script = output / 'controller.lua'
    script.write_text(published_controller(), encoding='utf-8', newline='\n')
    default_brake = 1540 if args.koopa_mode == 'standing' else 1470
    for brake in args.koopa_brake or (default_brake,):
        result = run(script, NIGHTLY, output, PIN, 120, variant=3,
                     extra_env={'SMB_PRINCE_KOOPA_BRAKE': str(brake),
                                'SMB_PRINCE_KOOPA_MODE': args.koopa_mode,
                                'SMB_PRINCE_KOOPA_JUMP_X': str(args.koopa_jump_x)})
        receipt = result['receipt']
        later = receipt.get('later_route', {})
        koopa = later.get('koopa')
        reverse = later.get('reverse', {})
        if result['passed'] and args.koopa_mode == 'climb' and brake == 1470:
            assert receipt['controller_only'] and not receipt['added_helpers']
            assert tuple(receipt['terminal'][key] for key in ('x', 'y', 'hp', 'lives')) == (1491, 112, 4, 2)
            assert koopa['top'] == receipt['terminal']
            assert {(a['x'], a['y']) for a in reverse['falls'].values()} == {(1408, 206)}
            assert set(reverse['falls']) == {'0', '1'}
        if koopa and 'writes' in koopa:
            koopa = dict(koopa, writes=[write for write in koopa['writes'] if write['pc'] == 0xc42a])
        print(json.dumps(dict(brake=brake, mode=args.koopa_mode, passed=result['passed'],
            receipt_SHA256=result['receipt_SHA256'], script_SHA256=result['script_SHA256'],
            reason=receipt['reason'], phase=receipt.get('phase'),
            terminal=receipt.get('terminal', receipt.get('state')), koopa=koopa,
            second_gap=later.get('second_gap'),
            goomba_falls=reverse.get('falls'), post_pair=reverse.get('return_landing'),
            next_group=later.get('enemies')), sort_keys=True), flush=True)
        if result['passed']:
            break
    raise SystemExit(0 if result['passed'] else 1)


if __name__ == '__main__':
    main()
