"""Replay the existing 1-1 controller against the original and scoped dispatcher."""

import argparse
from collections import Counter
from copy import deepcopy
from functools import cache
import json
from types import SimpleNamespace
from unittest.mock import patch

import check_contra_force_fast_ingress_1122 as Fast
import check_smb1_alts_full11_1114 as Harness
import replay_contra_force_marker_full11_1116 as Frozen


Layout = Fast.Layout
Current = Layout.Current
N = Layout.N
Frames = Layout.Frames
STATE_FIELDS = ('OperMode', 'OperMode_Task', 'GameEngineSubroutine', 'AreaType',
                'WorldNumber', 'LevelNumber', 'Player_PageLoc', 'Player_X_Position',
                'Player_Y_Position', 'NumberofLives', 'PlayerStatus')
CPU_RAM = ((0, 0x17B), (0x1FE, 0x800), (0x5C00, 0x8000))
PAYLOAD = ((Fast.RETURN & 8191, Fast.RETURN_END & 8191), (Fast.TAIL, Fast.COOKIE + 16))


def state(m):
    return {name: N.get(m, name) for name in STATE_FIELDS}


def death_state(m):
    fields = ('MmDeathAge', 'MmDeathPit', 'TimerControl', 'NmiDisable',
              'EventMusicQueue', 'EventMusicBuffer', 'Player_Y_HighPos')
    return dict(state(m), **{name: N.get(m, name) for name in fields if name in m.bundle['syms']})


def compare(original, candidate, label, repair_death=False):
    for first, last in CPU_RAM:
        old = list.__getitem__(original, slice(first, last))
        new = list.__getitem__(candidate, slice(first, last))
        if old != new:
            diff = [(hex(i), a, b) for i, (a, b) in enumerate(zip(old, new), first) if a != b]
            raise AssertionError((label, 'Native RAM', state(original), state(candidate), diff[:20]))
    for tag, (old, new) in enumerate(zip(original.ram, candidate.ram, strict=True)):
        ranges = []
        first = 0
        if tag == 2:
            omitted = list(PAYLOAD)
            if repair_death:
                omitted.append((0xBECA & 8191, Fast.RETURN & 8191))
                branch_operands = [pc + 1 for pc in Fast.DEATH_BRANCHES]
                for pc in (*branch_operands, *Fast.DEATH_TABLE_BYTES):
                    at = pc & 8191
                    omitted.append((at, at + 1))
            for start, end in sorted(omitted):
                assert start >= first
                ranges.append((first, start))
                first = end
        ranges.append((first, 8192))
        for first, last in ranges:
            if old[first:last] != new[first:last]:
                diff = [(hex(i), a, b) for i, (a, b) in enumerate(
                    zip(old[first:last], new[first:last]), first) if a != b]
                raise AssertionError((label, 'WRAM', tag, state(original), state(candidate), diff[:20]))
    assert original.rawtags == candidate.rawtags, (label, 'PRG mapping')
    assert original.vram == candidate.vram, (label, 'VRAM')
    assert original.chr_latches == candidate.chr_latches, (label, 'CHR pages')
    assert original.ppuctrl == candidate.ppuctrl, (label, 'PPUCTRL')


def run(parent, identity, limit, *, retry=False, repair_death=False):
    assert Harness.N is N and Harness.Frames is Frames
    raw, _, _ = Fast.candidate_image(parent, repair_death=repair_death)
    parent_sha, candidate_sha = map(Fast.Hud.H, (parent, raw))
    cb95 = Fast.Hud.inverse(parent)
    prior = Frozen.previous(identity)
    bundle = Current.bindings(cb95)['bundle']
    assert Current.W.address(bundle, 'MegaManDeathUpdate') == Fast.DEATH_HANDLER
    assert (Current.W.location(bundle, 'MegaManDeathUpdate') - 16) // 8192 | 128 == Fast.DEATH_BANK
    old_bundle = dict(bundle, raw=parent)
    syms = dict(bundle['syms'])
    pause = syms['PauseRoutine']
    assert int(pause['val'], 0) == Layout.PAUSE
    syms['PauseRoutine'] = dict(pause, val=hex(Layout.NEW_PAUSE))
    new_bundle = dict(bundle, raw=raw, syms=syms)
    name, variant = Frozen.IDENTITIES[identity]

    def verify_image(image, key):
        assert image == raw and key == identity, 'Require the exact paired candidate and identity'

    @cache
    def legacy_image():
        a2 = Current.reference(cb95)
        bc5, _ = Current.Previous.reference(a2)
        assert Fast.Hud.H(bc5) == Current.P.C.CANDIDATE
        # The input policy is pinned on the earlier typed build. Its observer
        # addresses, code and cookie will be checked against the real owner.
        legacy = Frozen.Model.P.Model.F.normalize(bc5).original
        assert Fast.Hud.H(legacy) == Frozen.Completed.PIN
        return legacy

    @cache
    def controller():
        legacy = legacy_image()
        q = deepcopy(prior.bindings(legacy, identity))
        assert (q['name'], q['variant'], q['slot']) == (name, variant, 30)
        q['sha'] = candidate_sha
        for label, at in q['ram'].items():
            assert Current.W.address(bundle, label) == at, (label, 'Native RAM moved')
        for label, h in q['hooks'].items():
            at = 16 + h['offset']
            if label in ('GameLoopReturn0', 'GameLoopReturn1'):
                call = b'\x20' + Current.W.address(new_bundle, 'GameLoop').to_bytes(2, 'little')
                assert raw[at - 3:at] == call, (label, 'Main return moved')
            else:
                assert Current.W.address(new_bundle, label) == h['pc'], (label, 'ROM hook moved')
                assert Current.W.location(new_bundle, label) == at
            h['bytes'] = list(raw[at:at + len(h['bytes'])])
            if 'bank' in h:
                begin = 16 + h['bank'] * 8192
                h['bank_SHA256'] = Fast.Hud.H(raw[begin:begin + 8192])
        carrier = raw[Current.P.CHR + 935 * 1024:Current.P.CHR + 959 * 1024]
        for label, h in q['cf']['hooks'].items():
            at = 16384 + (h['pc'] & 8191)
            assert carrier[at:at + len(h['bytes'])] == bytes(h['bytes']), (label, 'Source hook changed')
        cookie = bytearray(raw[573373:573389])
        cookie[2] = variant
        q['cf']['cookie'] = list(cookie)
        q['cf']['carrier_SHA256'] = Fast.Hud.H(carrier)
        frozen = prior.controller(legacy, identity)
        assert Fast.Hud.H(frozen.encode()) == prior.LUA_SHA[identity]
        body = frozen.split('\n', 1)[1]
        lua = 'local C=' + Frozen.Frozen.lua(q) + '\n' + body
        Frozen.Frozen.LuaRuntime().compile(lua)
        return lua, Fast.Hud.H(body.encode())

    def source(image, key):
        verify_image(image, key)
        return controller()[0]

    def metadata(image, key):
        verify_image(image, key)
        lua, body = controller()
        return dict(parent_SHA256=parent_sha, candidate_SHA256=candidate_sha,
                    controller_SHA256=Fast.Hud.H(lua.encode()), controller_body_SHA256=body)

    def normalize(image):
        verify_image(image, identity)
        return Frozen.Completed.normalize(legacy_image())

    factory = SimpleNamespace(ROM=Fast.Hud.ROM, metadata=metadata,
                              controller=source, normalize=normalize)
    base_frame, base_cpu = Frames.frame, N.NesMPU
    original = None
    frames = sums_old = sums_new = 0

    def cold(image, key):
        nonlocal original
        verify_image(image, key)
        pads = [4] * 3 + [1] * 6
        original, candidate = (Fast.cold_menu(b, name, 30, pads, variant)
                               for b in (old_bundle, new_bundle))
        for epoch in range(700):
            s = state(original)
            assert s == state(candidate), ('Boot', epoch, s, state(candidate))
            if (s['OperMode'], s['OperMode_Task'], s['GameEngineSubroutine']) == (1, 3, 8):
                compare(original, candidate, 'Stage entry', repair_death)
                print('ENTRY ' + json.dumps(dict(identity=identity, epoch=epoch, state=s)), flush=True)
                return candidate
            for model in (original, candidate):
                model.controller_pad = 0
                base_frame(model, cold=True)
        raise AssertionError(('Cold stage entry bound', identity))

    def paired(candidate, *, whole_pass, observe=None, expect_parity=True):
        nonlocal frames, sums_old, sums_new
        assert whole_pass and original is not None
        original.controller_pad = candidate.controller_pad
        with patch.object(N, 'NesMPU', base_cpu):
            sums_old += base_frame(original, whole_pass=True)
        cycles = base_frame(candidate, observe=observe, whole_pass=True)
        sums_new += cycles
        frames += 1
        if expect_parity:
            compare(original, candidate, ('Play', frames, candidate.controller_pad), repair_death)
        if frames % 250 == 0:
            progress = dict(identity=identity, frames=frames, state=state(candidate))
            if expect_parity:
                progress['cycles_saved'] = sums_old - sums_new
            print('PAIR ' + json.dumps(progress), flush=True)
        return cycles

    if retry:
        print('BINDING ' + json.dumps(dict(parent_SHA256=parent_sha, candidate_SHA256=candidate_sha,
                                           repair_death=repair_death)), flush=True)
        candidate = cold(raw, identity)
        saw_enemy = False
        for _ in range(600):
            candidate.controller_pad = 1
            paired(candidate, whole_pass=True)
            saw_enemy |= any(N.get(candidate, 'Enemy_Flag', i) for i in range(6))
            if N.get(candidate, 'GameEngineSubroutine') == 11:
                break
        else:
            raise AssertionError(('No natural death on the opening flat', state(candidate)))
        death = death_state(candidate)
        death_frame = frames
        assert saw_enemy and death['NumberofLives'] == 2 and death['PlayerStatus'] == 0, death
        print('DEATH ' + json.dumps(dict(frames=frames, state=death)), flush=True)
        if repair_death:
            outside_scope = N.fork(candidate)
            assert outside_scope[0x1FA] != 0x84 and N.get(outside_scope, 'MmDeathAge') == 0
            mapping = tuple(outside_scope.rawtags)
            N.invoke(outside_scope, 'HuDeath', a=0, x=0, y=0)
            assert N.get(outside_scope, 'MmDeathAge') == 1
            assert tuple(outside_scope.rawtags) == mapping
            print('PUBLIC DEATH ' + json.dumps(dict(identity=identity, age=1, mapping_restored=True)),
                  flush=True)
        watched = {}
        death_labels = {'PlayerDeath', 'RlDeathDispatch', 'LmDeathGate', 'NrDeath', 'HuDeath',
                        'MegaManDeathUpdate', 'ExpandedDeathUpdate', 'PlayerLoseLife'}
        for label, symbol in new_bundle['syms'].items():
            if label not in death_labels or 'seg' not in symbol:
                continue
            pc = Current.W.address(new_bundle, label)
            if not 0x8000 <= pc <= 0xFFFF or 'ooffs' not in new_bundle['segs'][symbol['seg']]:
                continue
            at = Current.W.location(new_bundle, label)
            if 16 <= at < Current.P.CHR:
                watched.setdefault(((at - 16) // 8192 | 128, pc), []).append(label)
        reached = Counter()

        def observe(model, cpu):
            if cpu.pc >= 0x8000:
                tag = model.rawtags[(cpu.pc - 0x8000) // 8192]
                reached.update(watched.get((tag, cpu.pc), ()))
                if (tag, cpu.pc) == (Fast.DEATH_BANK, Fast.DEATH_HANDLER):
                    reached['timed death worker'] += 1
                if (tag, cpu.pc, cpu.x) == (2, Fast.FAST, 24):
                    reached['fast death service'] += 1

        consecutive = 0
        for elapsed in range(900):
            candidate.controller_pad = 0
            paired(candidate, whole_pass=True, observe=observe if elapsed < 12 or repair_death else None,
                   expect_parity=not repair_death)
            if elapsed in (11, 199):
                print('DEATH TRACE ' + json.dumps(dict(elapsed=elapsed + 1,
                                                      state=death_state(candidate), reached=reached)),
                      flush=True)
            s = state(candidate)
            if ((s['OperMode'], s['OperMode_Task'], s['GameEngineSubroutine']) == (1, 3, 8)
                    and s['NumberofLives'] == 1 and N.get(candidate, 'Player_State') == 0):
                assert s['WorldNumber'] == s['LevelNumber'] == s['PlayerStatus'] == 0
                assert N.get(candidate, 'SelectedCharacter') == 31
                assert (N.get(candidate, 'FmGroups') >> 3) & 3 == variant
                assert candidate.ram[2][0x7F + variant] == 0x10
                assert candidate.ram[2][0x2E1] == candidate.ram[2][0x1DB8] == 1
                consecutive += 1
                if consecutive == 25:
                    control = death_state(original)
                    if repair_death:
                        assert control['GameEngineSubroutine'] == 11 and control['NumberofLives'] == 2
                        assert reached['timed death worker'] == 168, reached
                    return dict(passed=True, identity=identity, candidate_SHA256=candidate_sha,
                                matching_updates_before_death=death_frame, replay_updates=frames,
                                death=death, stage_after_retry=s,
                                control=control, reached=reached, grounded_updates=consecutive,
                                gameplay_seeds=0, outputs=0)
            else:
                consecutive = 0
        raise AssertionError(('Natural retry did not reach 25 active grounded updates', death_state(candidate)))

    print('BINDING ' + json.dumps(metadata(raw, identity)), flush=True)
    with patch.object(Harness, 'Factory', factory), patch.object(Harness, 'cold', cold), \
            patch.object(Frames, 'frame', paired):
        result = Harness.run(raw, identity, limit)
    result.update(paired_frames=frames, parent_CPU=sums_old, candidate_CPU=sums_new)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--identity', nargs='+', choices=Frozen.IDENTITIES, default=['burns'])
    parser.add_argument('--limit', type=int, default=6000)
    parser.add_argument('--retry', action='store_true')
    parser.add_argument('--repair-death', action='store_true')
    args = parser.parse_args()
    parent = Fast.Hud.ROM.read_bytes()
    for identity in args.identity:
        result = run(parent, identity, args.limit, retry=args.retry, repair_death=args.repair_death)
        print('RESULT ' + json.dumps(result, separators=(',', ':')), flush=True)
        assert result['passed'], 'The paired route did not reach its finish condition'
