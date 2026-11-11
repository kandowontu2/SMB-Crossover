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


def replay(script, rom, output, expected, *, stop_x=0, combat_jumps=True,
           combat_gap=112, wait_on_brick=True, lure_walkers=True):
    return run(script, rom, output, expected, 180, variant=3, extra_env={
        'SMB_PRINCE_KOOPA_BRAKE': '1470', 'SMB_PRINCE_KOOPA_MODE': 'air',
        'SMB_PRINCE_GOOMBA_BRAKE': '1710', 'SMB_PRINCE_GOOMBA_CLIMB': '1',
        'SMB_PRINCE_FINISH_STOP': str(stop_x), 'SMB_PRINCE_FINISH_COMBAT': str(int(combat_jumps)),
        'SMB_PRINCE_FINISH_BRICK_WAIT': str(int(wait_on_brick)),
        'SMB_PRINCE_FINISH_COMBAT_GAP': str(combat_gap),
        'SMB_PRINCE_FINISH_LURE': str(int(lure_walkers)),
    })


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--rom', type=Path, default=NIGHTLY)
    parser.add_argument('--expected')
    parser.add_argument('--cookie')
    parser.add_argument('--support-publication', type=lambda value: int(value, 0))
    parser.add_argument('--stop-x', type=int, default=0)
    parser.add_argument('--combat-jumps', action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument('--combat-gap', type=int, choices=range(34, 121), default=112)
    parser.add_argument('--wait-on-brick', action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument('--lure-walkers', action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()
    output = args.output.resolve()
    assert output.is_relative_to(R / 'build') and output != R / 'build'
    rom = args.rom.resolve()
    expected = check(rom)['ROM_sha256']
    if args.expected is not None:
        assert expected == args.expected and args.cookie and args.support_publication
        cookie, support_publication = args.cookie, args.support_publication
    else:
        assert rom == NIGHTLY.resolve() and args.cookie is None and args.support_publication is None
        import compose_prince_signed_world_row_1111 as Signed
        source_image = rom.read_bytes()
        if expected == Signed.CANDIDATE:
            image, layout = Signed.proposal(Signed.recover_parent(source_image))
        else:
            if expected != PIN:
                import check_jay_silius_machinegun_1111 as Jay

                assert expected == Jay.CANDIDATE_PIN
                source_image = Jay.recover_parent(source_image)
            image, layout = Source.proposal(Source.recover_parent(source_image))
        assert image == source_image
        cookie, support_publication = layout['cookie'], layout['support_publication']
    output.mkdir(exist_ok=True)
    script = output / 'controller.lua'
    script.write_text(controller(cookie, support_publication), encoding='utf-8', newline='\n')
    result = replay(script, rom, output / 'capture', expected, stop_x=args.stop_x,
                    combat_jumps=args.combat_jumps, combat_gap=args.combat_gap,
                    wait_on_brick=args.wait_on_brick, lure_walkers=args.lure_walkers)
    receipt = result['receipt']
    print(json.dumps(dict(passed=result['passed'], reason=receipt['reason'], phase=receipt['phase'],
                          terminal=receipt['terminal'], route=receipt['later_route'].get('finish', {}),
                          injuries=receipt['injuries'], receipt_SHA256=result['receipt_SHA256'],
                          script_SHA256=result['script_SHA256']), sort_keys=True), flush=True)
    raise SystemExit(0 if result['passed'] else 1)


if __name__ == '__main__':
    main()
