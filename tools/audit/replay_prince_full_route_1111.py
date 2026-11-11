"""Continue the exact native Prince replay through the rest of World 1-1."""

import argparse
import json
from pathlib import Path

import replay_prince_question_route_1111 as Question
from nightly_patch_guard_v1 import check
from replay_roster_repair_1111 import NIGHTLY, PIN, R, Source
from run_stdout_mesen_1110 import run


TAIL = R / 'tools/playthroughs/prince_finish_route_1111.lua'


def controller(cookie, support_publication):
    source = Question.controller(cookie, support_publication)

    def change(old, new):
        nonlocal source
        assert source.count(old) == 1, old
        source = source.replace(old, new)

    anchor = 'local function throughSecondBrick(s)'
    change(anchor, TAIL.read_text(encoding='utf-8') + '\n' + anchor)
    change("      finish(true,'Original question-block climb and standing jump pass the Goomba pair')",
           '      startEnding(s)')
    change('local function tick()\n', 'local function tick()\n  if endingFrame() then return end\n')
    change('  local enemy=enemyNear(s.x)', '  if ending then endingTick(s);return end\n  local enemy=enemyNear(s.x)')
    change('assert(#events<100,', 'assert(#events<180,')
    change('assert(frame<=16000,', 'assert(frame<=24000,')
    return source


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--stop-x', type=int, default=0)
    parser.add_argument('--combat-jumps', action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument('--combat-gap', type=int, choices=range(34, 121), default=112)
    parser.add_argument('--wait-on-brick', action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument('--lure-walkers', action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()
    output = args.output.resolve()
    assert output.is_relative_to(R / 'build') and output != R / 'build'
    expected = check(NIGHTLY)['ROM_sha256']
    raw = NIGHTLY.read_bytes()
    if expected != PIN:
        import check_jay_silius_machinegun_1111 as Jay

        assert expected == Jay.CANDIDATE_PIN
        raw = Jay.recover_parent(raw)
    image, layout = Source.proposal(Source.recover_parent(raw))
    assert image == raw
    output.mkdir(exist_ok=True)
    script = output / 'controller.lua'
    script.write_text(controller(layout['cookie'], layout['support_publication']), encoding='utf-8', newline='\n')
    result = run(script, NIGHTLY, output / 'capture', expected, 180, variant=3, extra_env={
        'SMB_PRINCE_KOOPA_BRAKE': '1470', 'SMB_PRINCE_KOOPA_MODE': 'air',
        'SMB_PRINCE_GOOMBA_BRAKE': '1710', 'SMB_PRINCE_GOOMBA_CLIMB': '1',
        'SMB_PRINCE_FINISH_STOP': str(args.stop_x), 'SMB_PRINCE_FINISH_COMBAT': str(int(args.combat_jumps)),
        'SMB_PRINCE_FINISH_BRICK_WAIT': str(int(args.wait_on_brick)),
        'SMB_PRINCE_FINISH_COMBAT_GAP': str(args.combat_gap),
        'SMB_PRINCE_FINISH_LURE': str(int(args.lure_walkers)),
    })
    receipt = result['receipt']
    print(json.dumps(dict(passed=result['passed'], reason=receipt['reason'], phase=receipt['phase'],
                          terminal=receipt['terminal'], route=receipt['later_route'].get('finish', {}),
                          injuries=receipt['injuries'], receipt_SHA256=result['receipt_SHA256'],
                          script_SHA256=result['script_SHA256']), sort_keys=True), flush=True)
    raise SystemExit(0 if result['passed'] else 1)


if __name__ == '__main__':
    main()
