"""Run the established Mega Giant Mario route with stdout-only receipts."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re

from deliver_steve_move_1111 import NIGHTLY, PIN, R
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run


REFERENCE = R / 'build/mega-giant-current-native-1110/native-end/controller.lua'
REFERENCE_PIN = '61edca1dd04761085c288ec577159fbb5a1297fd2f43698f1c9b7fd61148cc07'


def controller():
    raw = REFERENCE.read_bytes()
    assert sha256(raw).hexdigest() == REFERENCE_PIN
    source = raw.decode('utf-8').replace('\r\n', '\n')
    source, count = re.subn(r'rom=[^,]+,main=', "rom=os.getenv('SMB_STDOUT_ROM_SHA'),main=", source)
    assert count == 1
    source, count = re.subn(r'local function shot\(name\).*?\nend',
                            'local function shot(name) end', source, count=1, flags=re.S)
    assert count == 1
    start = source.index(' local f=assert(io.open(')
    end = source.index(" print('Mega Giant '", start)
    receipt = source[start:end].split(' f:write(json(', 1)[1].split("..'\\n')", 1)[0]
    receipt = receipt.replace('ROM_sha256=C.rom', 'ROM_SHA256=C.rom')
    source = source[:start] + " print('SMB_NATIVE_RECEIPT '..json(" + receipt + ')\n' + source[end:]
    source = source.replace('local function finish(ok,reason)', 'local finished=false\n'
                            'local function finish(ok,reason)\n if finished then return end\n finished=true')
    return source


def replay(script, rom, output, pin):
    result = run(script, rom, output, pin, 140)
    receipt = result['receipt']
    if result['passed']:
        terminal = receipt['terminal']
        assert (terminal['world'], terminal['level'], terminal['engine'], terminal['lives']) == (1, 2, 8, 2)
        assert receipt['body']['sprite_parts'] == 46 and receipt['body']['chr'] == [180, 182]
        assert receipt['flag'] and receipt['controller_only']
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--rom', type=Path, default=NIGHTLY)
    parser.add_argument('--expected', default=PIN)
    args = parser.parse_args()
    output, rom = args.output.resolve(), args.rom.resolve()
    assert output.is_relative_to(R / 'build') and output != R / 'build'
    assert check(rom)['ROM_sha256'] == args.expected
    output.mkdir(exist_ok=True)
    script = output / 'controller.lua'
    script.write_text(controller(), encoding='utf-8', newline='\n')
    result = replay(script, rom, output / 'capture', args.expected)
    receipt = result['receipt']
    print(json.dumps(dict(passed=result['passed'], receipt=result['receipt_SHA256'],
                          script=result['script_SHA256'], reason=receipt['reason'],
                          terminal=receipt['terminal'], body=receipt.get('body'), flag=receipt.get('flag')),
                     sort_keys=True), flush=True)
    raise SystemExit(0 if result['passed'] else 1)


if __name__ == '__main__':
    main()
