"""Retest both Bubble Bobble identities using the retained native 1-1 route."""

import argparse
from functools import lru_cache
import inspect
import json
from pathlib import Path

import compose_bub_epoch_1123 as Epoch
import profile_bub_empty_native_1113 as Opening
import replay_bub_combined_route_1113 as Route
import run_sparse_sprite_scan_native_1123 as Cadence


Previous, Timing = Cadence.Previous, Cadence.Timing
LABELS = dict(BbNativeUpdate=0xBE61, BbSourceClock=0xA152, BbNativeDraw=0xBD14,
              BbOriginal_D36B=0xA448, BbNativeObserve=0xB89C)


@lru_cache(maxsize=1)
def replay_factory():
    # Rebind only ROM identity and hook locations. Keep the retained full
    # route's controller decisions and read-only native witnesses verbatim.
    assert Epoch.H(Path(Opening.__file__).read_bytes()) == '97eefd9674080cc44271ded124c40434b383ca3dc7e1305872867b1503708620'
    assert Epoch.H(Path(Route.__file__).read_bytes()) == '5d272ff6fb070527707cd8db601c7489a6499434917ce6c03a7dbb090472646f'
    replace = Route.replace_once
    opening = inspect.getsource(Opening.controller)
    opening = replace(opening, '    q, _, binding = B.bindings(raw)\n', '')
    start = opening.index('    # Current typed cookie selector,')
    end = opening.index('    hooks=[]', start)
    opening = opening[:start] + '''    cookie = Epoch.Bub.cookie(raw)
    assert raw[Epoch.Bub.COOKIE:Epoch.Bub.COOKIE+16] == cookie
    image = Epoch.Bub.code(raw)
    q = {'labels': LABELS}
''' + opening[end:]
    opening = replace(opening, '{B.PIN}', '{Epoch.H(raw)}')
    opening = replace(opening, 'sha256(raw).hexdigest() == B.PIN', 'Epoch.H(raw) in (Epoch.PARENT, Epoch.CANDIDATE)')
    common = dict(Epoch=Epoch, LABELS=LABELS)
    scope = dict(Opening.__dict__, **common)
    exec(compile(opening, __file__ + ':opening', 'exec'), scope)

    route = inspect.getsource(Route.controller)
    start = route.index('    parent = U.combined_reverse(raw)')
    end = route.index('    route, old = legacy_route(', start)
    route = route[:start] + '    text = opening(raw, identity)\n' + route[end:]
    route = replace(route, "    labels = B.bindings(parent)[0]['labels']", '    labels = LABELS')
    route = replace(route, '    assert sha256(text.encode()).hexdigest()==LUA_SHA[identity,mode]\n', '')
    factory = dict(Route.__dict__, **common, PIN=Epoch.CANDIDATE, opening=scope['controller'])
    exec(compile(route, __file__ + ':route', 'exec'), factory)
    return factory['controller']


def native(image, rom, script, identity, capture):
    digest = Epoch.H(image)
    guard = Previous.check(rom)
    assert guard['ROM_sha256'] == digest and not guard['matching_patch_files']
    text = replay_factory()(image, identity, 'full11')
    script.write_bytes(text.encode())
    proof = Previous.run(script, rom, capture, digest, 200, long_no_capture=True)
    result = proof['receipt']
    assert proof['outputs_written'] == 0 and not proof['images']
    assert Previous.check(rom) == guard
    keep = ('passed', 'reason', 'name', 'route', 'physical_frames', 'Main_updates',
            'source_updates', 'terminal', 'controller_only', 'runtime_state_writes')
    summary = {key: result[key] for key in keep}
    summary.update(ROM=digest, receipt_SHA256=proof['receipt_SHA256'], script_SHA256=proof['script_SHA256'])
    print('BUB EPOCH FULL STAGE ' + json.dumps(summary, separators=(',', ':')), flush=True)
    assert proof['passed'] and result['controller_only'] and result['runtime_state_writes'] == 0
    assert result['route']['level'] == 1 and result['route']['final_lives'] == 2
    return proof['receipt_SHA256']


def run(install):
    downloads = Timing.ROM
    guard = Previous.check(downloads)
    parent = downloads.read_bytes()
    image = Epoch.compose(parent)
    work = Timing.SHARED
    candidate, script = work / 'candidate.nes', work / 'controller.lua'
    assert not guard['matching_patch_files'] and candidate.read_bytes() == parent
    assert set(work.iterdir()) == {candidate, script}
    script_before = script.read_bytes()
    Previous.require_free_workspace(Timing.R, downloads, allow_interactive=True)
    replaced = delivered = False
    try:
        candidate.write_bytes(image)
        before = [native(image, candidate, script, who, work / 'capture') for who in (0, 1)]
        if install:
            assert downloads.read_bytes() == parent and Previous.check(downloads) == guard
            replaced = True
            downloads.write_bytes(image)
            after = [native(image, downloads, script, who, work / 'capture') for who in (0, 1)]
            assert before == after and downloads.read_bytes() == image
            assert Previous.check(downloads)['ROM_sha256'] == Epoch.CANDIDATE
            delivered = True
            print(f'BUB EPOCH NIGHTLY {Epoch.CANDIDATE} {downloads}', flush=True)
    finally:
        if not delivered:
            if replaced:
                downloads.write_bytes(parent)
            candidate.write_bytes(parent)
        script.write_bytes(script_before)
        assert set(work.iterdir()) == {candidate, script}
        assert candidate.read_bytes() == downloads.read_bytes() == (image if delivered else parent)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--install', action='store_true')
    run(parser.parse_args().install)
