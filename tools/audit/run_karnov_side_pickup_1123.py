"""Run the established Karnov Star route on Downloads or the side trial."""

import argparse
import json
from unittest.mock import patch

import compose_karnov_side_route_1123 as Trial
import run_karnov_stock_1123 as Stock
import run_sparse_sprite_scan_native_1123 as Cadence


def binding(parent, image):
    current = Cadence.Current
    resolve = current.OLD_REFERENCE
    sources = {}

    def reference(raw):
        if Stock.H(raw) == Stock.PIN:
            sources[Stock.PIN] = raw
        return resolve(raw)

    with patch.object(current, 'OLD_REFERENCE', reference):
        current.reference(parent)
    old = sources[Stock.PIN]
    canonical = Stock.Previous.reference(old)
    original = Stock.controller(old, 'star')
    assert Stock.H(original.encode()) == Stock.PINS['star']
    digest = Stock.H(image)

    with patch.multiple(Stock, PIN=digest, PINS={}), patch.object(
        Stock.Previous, 'reference', lambda _: canonical
    ):
        updated = Stock.controller(image, 'star')
    assert original.count(Stock.PIN) == 1
    assert updated == original.replace(Stock.PIN, digest, 1)
    return updated.encode()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--installed', action='store_true')
    args = parser.parse_args()
    downloads = Stock.Stock.check(Stock.ROM)
    parent = Stock.ROM.read_bytes()
    image = parent if args.installed else Trial.compose(parent)
    digest = Stock.H(image)
    work = Cadence.Timing.SHARED
    candidate, script = work / 'candidate.nes', work / 'controller.lua'
    assert set(work.iterdir()) == {candidate, script} and candidate.read_bytes() == parent
    original = script.read_bytes()
    program = binding(parent, image)
    runner = Cadence.Previous
    runner.require_free_workspace(Cadence.Timing.R, Stock.ROM, allow_interactive=True)
    try:
        if not args.installed:
            candidate.write_bytes(image)
        test_rom = Stock.ROM if args.installed else candidate
        guard = Stock.Stock.check(test_rom)
        assert guard['ROM_sha256'] == digest and not guard['matching_patch_files']
        script.write_bytes(program)
        proof = Stock.Stock.run(script, test_rom, work / 'capture', digest, 210)
        assert not proof['images'] and proof['outputs_written'] == 0
        result = proof['receipt']
        fields = ('passed', 'reason', 'physical_frames', 'movement_updates', 'terminal', 'head')
        record = dict(ROM=digest, receipt_SHA256=proof['receipt_SHA256'],
                      script_SHA256=proof['script_SHA256'], result={k: result[k] for k in fields if k in result})
        if proof['passed']:
            record['pickups'] = {
                key: dict(emerged=item['birth']['actor'], collected=item['collect']['after'],
                          music=item['collect'].get('music'))
                for key, item in result['items'].items()
            }
        print('KARNOV SIDE STAR ' + json.dumps(record, separators=(',', ':')), flush=True)
        assert proof['passed']
    finally:
        if not args.installed:
            candidate.write_bytes(parent)
        script.write_bytes(original)
        assert set(work.iterdir()) == {candidate, script} and candidate.read_bytes() == Stock.ROM.read_bytes()
        assert Stock.Stock.check(Stock.ROM) == downloads


if __name__ == '__main__':
    main()
