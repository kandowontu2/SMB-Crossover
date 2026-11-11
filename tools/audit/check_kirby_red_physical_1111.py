"""Replay the original red-shell encounter against the current Kirby fix."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory

import check_kirby_inhale_vertical_wide_1111 as Inhale
import check_kirby_red_sweep_1111 as Sweep
from run_stdout_mesen_1110 import run


R = Sweep.Control.R
PARENT = Sweep.Control.NIGHTLY
PIN = '852712c9a2afce71c45f9f2c970e1f5c7969c58d878cfa0a250d2bdb7ba93383'
RED_PIN = '7cd19c747dcf32166afaf07d083c91e2d9774c0c08859006976c90944b9b3283'
LEGACY = R / 'build/kirby-red-shell-1110-v3/controller.lua'
LEGACY_PIN = '15d360ea10e46543d869b39363dd2bf2718f4f210a3aff7db5a9987d8fb4a14c'


def proposal(raw):
    seed, _ = Sweep.Control.prepare(raw)
    red, _, red_evidence = Sweep.proposal(raw, seed.bundle)
    wide, _, inhale_evidence = Inhale.proposal(raw, seed.bundle)
    assert sha256(red).hexdigest() == RED_PIN
    start = red_evidence['file_offset']
    stop = start + red_evidence['span_bytes']
    assert wide[start:stop] == raw[start:stop]
    image = wide[:start] + red[start:stop] + wide[stop:]
    assert sha256(image).hexdigest() == PIN
    return image, dict(image_SHA256=PIN, red=red_evidence, inhale=inhale_evidence)


def controller():
    raw = LEGACY.read_bytes()
    assert sha256(raw).hexdigest() == LEGACY_PIN
    header, body = raw.decode('utf-8').replace('\r\n', '\n').split('\n', 1)
    start = body.index(" local f=assert(io.open(OUTPUT..'result.json','w'))")
    end = body.index(' emu.stop(passed and 0 or 1)', start)
    receipt = body[start:end].split(' f:write(json(', 1)[1].split("..'\\n')", 1)[0]
    receipt = receipt.replace('ROM_sha256=C.sha', 'ROM_SHA256=C.sha')
    body = body[:start] + " print('SMB_NATIVE_RECEIPT '..json(" + receipt + ')\n' + body[end:]
    return header + "\nC.sha=assert(os.getenv('SMB_STDOUT_ROM_SHA'))\n" + body


def replay(rom, expected, output):
    output.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=output) as directory:
        script = Path(directory) / 'kirby_red_stdout.lua'
        script.write_text(controller(), encoding='utf-8')
        return run(script, rom, output, expected, 120)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument('--prepare', action='store_true')
    operation.add_argument('--rom', type=Path)
    parser.add_argument('--expected')
    args = parser.parse_args()
    output = args.output.resolve()
    assert output.is_relative_to(R / 'build') and output != R / 'build'
    if args.prepare:
        image, evidence = proposal(PARENT.read_bytes())
        output.mkdir(exist_ok=True)
        candidate = output / 'candidate.nes'
        with candidate.open('xb') as file:
            file.write(image)
        assert candidate.read_bytes() == image
        print(json.dumps(evidence, sort_keys=True), flush=True)
        return
    assert args.expected and len(args.expected) == 64
    result = replay(args.rom, args.expected, output)
    q = result['receipt']
    print(json.dumps(dict(passed=result['passed'], SHA256=result['receipt_SHA256'],
                          script_SHA256=result['script_SHA256'], reason=q['reason'],
                          capture=q.get('capture'), swallow=q.get('actual_down_swallow'),
                          contact=q.get('shell_contact'), defeat=q.get('native_defeat_return'),
                          terminal=q['terminal']), sort_keys=True), flush=True)
    assert result['passed']


if __name__ == '__main__':
    main()
