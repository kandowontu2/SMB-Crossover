"""Root's single native queue for the exact combined private Prince image."""
import argparse
from hashlib import sha256
import json

import compose_prince_entrance_current_1113 as Fix
import check_prince_draw_cache_native_1113 as Prior
import check_player_profile_native_1113 as Motion
import replay_karnov_ladder_stock_1113 as Karnov
from run_stdout_mesen_1110 import run

OUT = Prior.OUT
CASES = ('entry', 'combat', 'megaman', 'luigi', 'karnov')


def inputs():
    parent = Fix.Karnov.Owner.NIGHTLY.read_bytes()
    if Fix.digest(parent) == Fix.PIN:
        parent = Fix.reverse(parent)
    assert Fix.digest(parent) == Fix.PARENT
    candidate, info = Fix.proposal(parent)
    assert Fix.reverse(candidate) == parent
    original = Fix.Karnov.inverse_current(parent)
    cache, _ = Fix.Entry.Cache.proposal(original)
    assert Fix.digest(cache) == Fix.Entry.PARENT
    return candidate, info, parent, cache


def controller(case, candidate, parent, cache):
    assert Fix.digest(candidate) == Fix.PIN and Fix.digest(parent) == Fix.PARENT
    assert Fix.digest(cache) == Fix.Entry.PARENT
    if case == 'entry':
        text = Prior.stage_controller(candidate[Fix.Entry.Cache.Packet.COOKIE:
            Fix.Entry.Cache.Packet.COOKIE+16].hex())
        assert Fix.digest(text.encode()) == Prior.PINS['stage']
    elif case == 'combat':
        # The complete source streams and cookie are unchanged from209.
        # Keep the frozen controller API strict and run its exact text on
        # the independently authenticated composite cartridge.
        text = Prior.Fight.controller(cache)
        assert Fix.digest(text.encode()) == Prior.PINS['combat']
        # The frozen script also has an explicit top-level ROM guard.
        # Rebind that one guard to the authenticated composite, retaining
        # the old factory's strict contract and every gameplay assertion.
        assert text.count(Fix.Entry.PARENT) == 1
        text = text.replace(Fix.Entry.PARENT, Fix.PIN)
    elif case in ('megaman', 'luigi'):
        text = Motion.controller(candidate, case)
        expected = {'megaman': '630ac2f9f991812c519fb05b230d23d2773c1ed17020d96209616e9e18fe884e',
            'luigi': '18fcaaa7575aafd7b10f992989fe4b5a52608a106c8419826cd4079b3281b911'}
        assert Fix.digest(text.encode()) == expected[case]
    else:
        assert case == 'karnov'
        text = Karnov.controller(parent, wait_for_entry=True)
        assert Fix.digest(text.encode()) == '00187419e40f04b1d60f16792a1359ffae1caea4614f6d6ae30d3ff8c20e0f62'
        assert text.count(Fix.PARENT) == 1
        text = text.replace(Fix.PARENT, Fix.PIN)
    return text


def validate(case, result):
    assert result['passed'] and result['ROM_SHA256'] == Fix.PIN
    q = result['receipt']
    assert q['controller_only']
    if case == 'entry':
        final = q['terminal']; stage = q['later_route']['finish']
        assert stage['flag']['native_flag_write'] == 4 and stage['castle'] and stage['gap']
        assert stage['undergroundLanded'] == final
        assert (final['world'], final['level'], final['engine'], final['lives'], final['y']) == (0, 1, 8, 2, 176)
        assert final['hp'] == stage['undergroundStart']['hp'] and final['hp'] > 0
        assert not q['added_helpers']
    elif case == 'combat':
        fight = q['later_route']['swordCombat']
        assert fight['parried'] and fight['actions']['62'] and fight['actions']['58']
        assert fight['loss'] and fight['proxy'] and fight['call'] and fight['kill']
        assert fight['post']['enemy_state'] & 32 and fight['post']['score'] == 1
        assert fight['terminal']['hp'] == 4 and fight['terminal']['lives'] == 2
        assert fight['terminal']['star'] == 0
    elif case in ('megaman', 'luigi'):
        assert q['terminal']['lives'] == 2 and q['terminal']['y'] == 176
        assert q['walk']['x'] > q['first']['x']+8 and q['jump']['apex'] <= q['first']['y']-16
        assert q['profile_calls'] == 0
    else:
        assert case == 'karnov'
        assert q['reason'] == 'naturally-earned-and-used-bomb' and len(q['pickups']) == 4
        assert q['armed'] and q['blast_seen'] and q['terminal']['bomb'] == 0
        assert q['terminal']['health'] == 0 and q['terminal']['lives'] == 2
    return q


def execute(case, rom, candidate, parent, cache):
    assert rom.read_bytes() == candidate
    text = controller(case, candidate, parent, cache)
    script = OUT/'controller.lua'
    script.write_text(text, encoding='utf-8', newline='\n')
    if case == 'entry':
        result, _ = Prior.Stage.replay(script, rom, OUT/'capture', Fix.PIN)
    else:
        result = run(script, rom, OUT/'capture', Fix.PIN, 180, variant=3 if case == 'combat' else 0)
    # Keep aggregate evidence bounded even for the older full-stage trace.
    q = result['receipt']
    evidence = {name:q[name] for name in ('reason', 'physical_frames', 'frames',
        'Main_updates', 'source_updates', 'terminal', 'first', 'walk', 'jump',
        'profile_calls', 'armed', 'blast_seen', 'native_blast_contacts') if name in q}
    if case == 'entry':
        stage = q.get('later_route', {}).get('finish', {})
        evidence['stage'] = {name:stage[name] for name in (
            'flag', 'castle', 'gap', 'undergroundStart', 'undergroundLanded') if name in stage}
    if case == 'combat':
        fight = q.get('later_route', {}).get('swordCombat', {})
        evidence['combat'] = {name:fight[name] for name in ('parried', 'actions',
            'post', 'terminal') if name in fight}
        evidence['causal_commits'] = {name:fight[name]['commit'] for name in (
            'loss', 'proxy', 'call', 'kill') if fight.get(name)}
    if case == 'karnov':
        evidence['pickups'] = [dict(item=item['item'], after=item['after'],
            erased=item['erased']) for item in q.get('pickups', ())]
        evidence['manual_helpers'] = q.get('manual_helpers')
    # Print the actual negative observation too; never lose its hash to a
    # large assertion message before a diagnosis can be recorded.
    print(json.dumps(dict(case=case, passed=result['passed'], ROM_SHA256=Fix.PIN,
        script_SHA256=result['script_SHA256'], receipt_SHA256=result['receipt_SHA256'],
        evidence=evidence, outputs_written=result['outputs_written']),
        separators=(',', ':')), flush=True)
    validate(case, result)
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--case', choices=CASES, action='append')
    p.add_argument('--metadata', action='store_true')
    args = p.parse_args()
    candidate, info, parent, cache = inputs()
    rom = OUT/'candidate.nes'
    if not args.metadata:
        rom.write_bytes(candidate)
    for case in args.case or CASES:
        if args.metadata:
            text = controller(case, candidate, parent, cache)
            print(json.dumps(dict(case=case, script_SHA256=sha256(text.encode()).hexdigest(),
                native_run=False, outputs_written=0)), flush=True)
        else:
            execute(case, rom, candidate, parent, cache)
