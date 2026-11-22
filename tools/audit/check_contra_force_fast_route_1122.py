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
PICKUP_POLICY = Fast.Hud.R / 'tools/playthroughs/contra_force_11_1031_v2.lua'
PICKUP_POLICY_SHA = '973e3c3704a0917ef899f639c168c550e8e0f274de38796c559a862f2f13a74f'
POWERUP_OBJECT = 0x2E
ITEM_BLOCKS = (336, 1248, 1616, 1024)
COLLECT_ACCEPTED = 0xB876
COLLECT_RTS = 0xB8CF
PICKUP_CONTEXT = '''
 c.item=function()
  for slot=0,5 do
   local flag=r('Enemy_Flag',slot)
   if flag>0 and flag<128 and r('Enemy_ID',slot)==0x2e then
    return {slot=slot,kind=r('PowerUpType',slot),state=r('Enemy_State',slot),
            x=pos('Enemy_X_Position','Enemy_PageLoc',slot),y=r('Enemy_Y_Position',slot)}
   end
  end
 end
'''
PICKUP_TARGETS = '''
 if not target then
  local kind
  if c.status==0 then kind=0
  elseif c.lives==2 then kind=3
  elseif c.status==1 then kind=1
  elseif c.star==0 then kind=2 end
  if kind then
   local nextX=({[0]=336,1248,1616,1024})[kind]
   local y=(kind==3)and 128 or 144
   if c.x>=nextX-50 and c.x<=nextX+20 then
    if not solid(nextX,y) then return{},'upgrade','Expected real upgrade block missing at'..nextX end
    target={x=nextX,y=y,before=c.status,lives=c.lives,kind=kind}
    phase='align';clock=c.update;bumpAttempts=0;pickupAttempts=0
   elseif c.x>nextX+20 then return{},'upgrade','Passed required earned upgrade block at'..nextX end
  end
 end
'''


class PickupCompleted(Exception):
    """The earned item survived the required subsequent gameplay updates."""


def state(m):
    return {name: N.get(m, name) for name in STATE_FIELDS}


def death_state(m):
    fields = ('MmDeathAge', 'MmDeathPit', 'TimerControl', 'NmiDisable',
              'EventMusicQueue', 'EventMusicBuffer', 'Player_Y_HighPos')
    return dict(state(m), **{name: N.get(m, name) for name in fields if name in m.bundle['syms']})


def compare(original, candidate, label, repair_death=False, repair_pickup=False):
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
            if repair_pickup:
                for pc in Fast.MATURITY_TABLE_BYTES:
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


@cache
def legacy_image(parent):
    cb95 = Fast.Hud.inverse(parent)
    a2 = Current.reference(cb95)
    bc5, _ = Current.Previous.reference(a2)
    assert Fast.Hud.H(bc5) == Current.P.C.CANDIDATE
    # The input policy is pinned on the earlier typed build. Its observer
    # addresses, code and cookie will be checked against the real owner.
    legacy = Frozen.Model.P.Model.F.normalize(bc5).original
    assert Fast.Hud.H(legacy) == Frozen.Completed.PIN
    return legacy


@cache
def build_controller(parent, raw, identity, pickup=None, *, native=False):
    legacy = legacy_image(parent)
    prior = Frozen.previous(identity)
    name, variant = Frozen.IDENTITIES[identity]
    bundle = Current.bindings(Fast.Hud.inverse(parent))['bundle']
    q = deepcopy(prior.bindings(legacy, identity))
    assert (q['name'], q['variant'], q['slot']) == (name, variant, 30)
    q['sha'] = Fast.Hud.H(raw)
    if pickup:
        q['ram']['PowerUpType'] = Current.W.address(bundle, 'PowerUpType')
    if native:
        for label in ('FloateyNum_Control', 'Square2SoundQueue', 'AreaMusicQueue', 'Enemy_Y_HighPos'):
            q['ram'][label] = Current.W.address(bundle, label)
    for label, at in q['ram'].items():
        assert Current.W.address(bundle, label) == at, (label, 'Native RAM moved')
    for label, h in q['hooks'].items():
        at = 16 + h['offset']
        if label in ('GameLoopReturn0', 'GameLoopReturn1'):
            call = b'\x20' + Current.W.address(bundle, 'GameLoop').to_bytes(2, 'little')
            assert raw[at - 3:at] == call, (label, 'Main return moved')
        else:
            assert Current.W.address(bundle, label) == h['pc'], (label, 'ROM hook moved')
            assert Current.W.location(bundle, label) == at
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
    if pickup:
        policy = PICKUP_POLICY.read_bytes()
        assert Fast.Hud.H(policy) == PICKUP_POLICY_SHA
        policy_first = 'local choose=(function()\n'
        policy_last = '\nend)()\n'
        assert body.startswith(policy_first)
        keep = body.index(policy_last) + len(policy_last)
        controls = policy.decode().replace('\r\n', '\n').rstrip()
        chase = '''b=aim(item.x+8,4)
      if item.y<c.y-20 and item.x>target.x+64 and c.grounded and not c.heldA then b.a=true end'''
        assert controls.count(chase) == 1
        controls = controls.replace(chase, 'b=aim(target.x+74,2)')
        if pickup == 'all':
            first = controls.index(' if not target and c.status<2 then')
            end = controls.index(' if target then', first)
            controls = controls[:first] + PICKUP_TARGETS + controls[end:]
            controls = controls.replace('if c.status>target.before then',
                'if c.status>target.before or c.lives>target.lives or (target.kind==2 and c.star>0) then')
            stationary = "else phase='item-retreat';jumpStart=nil;releaseUntil=c.update+4 end"
            assert controls.count(stationary) == 1
            controls = controls.replace(stationary, '''elseif item.kind==3 then b=aim(item.x+6,3)
     elseif item.kind==2 then
      b=aim(item.x+4,2)
      if c.grounded and math.abs(item.x-c.x)<24 and item.y<c.y-16 and not c.heldA then b.a=true end
     else phase='item-retreat';jumpStart=nil;releaseUntil=c.update+4 end''')
        body = policy_first + controls + policy_last + body[keep:]
        anchor = '\n c.enemy=function()'
        assert body.count(anchor) == 1
        body = body.replace(anchor, PICKUP_CONTEXT + anchor)
        if pickup == 'all':
            body = body.replace(anchor, "\n c.lives=r('NumberofLives');c.star=r('StarInvincibleTimer')" + anchor)
            life_guard = "if not identity()or r('NumberofLives')~=2 or r('GameEngineSubroutine')==11"
            assert body.count(life_guard) == 1
            body = body.replace(life_guard, "if not identity()or r('NumberofLives')<2 or r('NumberofLives')>3"
                                " or r('GameEngineSubroutine')==11")
    lua = 'local C=' + Frozen.Frozen.lua(q) + '\n' + body
    Frozen.Frozen.LuaRuntime().compile(lua)
    return lua, Fast.Hud.H(body.encode())


def run(parent, identity, limit, *, retry=False, repair_death=False, pickup=None,
        repair_pickup=False, palette=False):
    assert Harness.N is N and Harness.Frames is Frames
    raw, _, _ = Fast.candidate_image(parent, repair_death=repair_death, repair_pickup=repair_pickup)
    control = parent
    if palette:
        from check_contra_force_combined_palette_1122 import compose, compare as compare_palette
        assert repair_death and repair_pickup and not retry
        control, combined, spans, _ = compose(parent, repair_pickup=True)
        assert control == raw
        raw = combined
    parent_sha, candidate_sha = map(Fast.Hud.H, (control, raw))
    cb95 = Fast.Hud.inverse(parent)
    bundle = Current.bindings(cb95)['bundle']
    assert Current.W.address(bundle, 'MegaManDeathUpdate') == Fast.DEATH_HANDLER
    assert (Current.W.location(bundle, 'MegaManDeathUpdate') - 16) // 8192 | 128 == Fast.DEATH_BANK
    syms = dict(bundle['syms'])
    pause = syms['PauseRoutine']
    assert int(pause['val'], 0) == Layout.PAUSE
    syms['PauseRoutine'] = dict(pause, val=hex(Layout.NEW_PAUSE))
    old_bundle = dict(bundle, raw=control, syms=syms if palette else bundle['syms'])
    new_bundle = dict(bundle, raw=raw, syms=syms)
    name, variant = Frozen.IDENTITIES[identity]

    def verify_image(image, key):
        assert image == raw and key == identity, 'Require the exact paired candidate and identity'

    def controller():
        return build_controller(parent, raw, identity, pickup)

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
        return Frozen.Completed.normalize(legacy_image(parent))

    factory = SimpleNamespace(ROM=Fast.Hud.ROM, metadata=metadata,
                              controller=source, normalize=normalize)
    base_frame, base_cpu = Frames.frame, N.NesMPU
    original = None
    frames = sums_old = sums_new = 0
    births = {}
    item_tracks = {}
    collected = []
    pending_item = None
    pickup_result = {}
    maturity_update = None
    pickup_order = {'mushroom': (0,), 'flower': (0, 1), 'all': (0, 3, 1, 2)}.get(pickup, ())

    def compare_play(original, candidate, label):
        if palette:
            compare_palette(original, candidate, spans, label)
        else:
            compare(original, candidate, label, repair_death, repair_pickup)

    def observe_pickup(model, cpu):
        nonlocal pending_item
        if cpu.pc not in (COLLECT_ACCEPTED, COLLECT_RTS) or model.rawtags[1] != 3:
            return
        if cpu.pc == COLLECT_ACCEPTED:
            slot = cpu.x
            kind = N.get(model, 'PowerUpType', slot)
            assert slot < 6 and len(collected) < len(pickup_order) and kind == pickup_order[len(collected)]
            assert N.get(model, 'Enemy_ID', slot) == POWERUP_OBJECT
            assert N.get(model, 'Enemy_State', slot) >= 128
            pending_item = dict(slot=slot, kind=kind, tier=N.get(model, 'PlayerStatus'),
                                area=N.get(model, 'AreaType'),
                                x=N.get(model, 'Enemy_X_Position', slot)
                                + 256 * N.get(model, 'Enemy_PageLoc', slot),
                                y=N.get(model, 'Enemy_Y_Position', slot))
            return
        assert pending_item is not None and cpu.p & 1
        slot, kind = pending_item['slot'], pending_item['kind']
        expected = ITEM_BLOCKS[kind]
        birth = births[slot, kind]
        assert birth['x'] == expected and birth['state'] < 128 and pending_item['area'] == 1, birth
        popup = 11 if kind == 3 else 6
        assert N.get(model, 'Enemy_Flag', slot) == 0 and N.get(model, 'FloateyNum_Control', slot) == popup
        tier = N.get(model, 'PlayerStatus')
        gear = model.ram[2][0x7F + variant]
        sound = N.get(model, 'Square2SoundQueue')
        assert tier == pending_item['tier'] + int(kind < 2) and gear == 0x10 | tier and sound & 0x20
        if kind < 2:
            assert tier == kind + 1 and model.ram[2][0x2E2] == 1
        elif kind == 2:
            assert N.get(model, 'StarInvincibleTimer') == 0x23 and N.get(model, 'AreaMusicQueue') == 0x40
        collected.append(dict(pending_item, update=frames + 1, tier_after=tier,
                              gear=gear, score_popup=popup, sfx=sound, birth=birth))
        pending_item = None

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
                compare_play(original, candidate, 'Stage entry')
                print('ENTRY ' + json.dumps(dict(identity=identity, epoch=epoch, state=s)), flush=True)
                return candidate
            for model in (original, candidate):
                model.controller_pad = 0
                base_frame(model, cold=True)
        raise AssertionError(('Cold stage entry bound', identity))

    def paired(candidate, *, whole_pass, observe=None, expect_parity=True):
        nonlocal frames, sums_old, sums_new, maturity_update
        assert whole_pass and original is not None
        original.controller_pad = candidate.controller_pad
        with patch.object(N, 'NesMPU', base_cpu):
            sums_old += base_frame(original, whole_pass=True)
        cycles = base_frame(candidate, observe=observe_pickup if pickup else observe, whole_pass=True)
        sums_new += cycles
        frames += 1
        if repair_pickup and not palette and maturity_update is None:
            mature = any(N.get(candidate, 'Enemy_ID', slot) == POWERUP_OBJECT
                         and 0 < N.get(candidate, 'Enemy_Flag', slot) < 128
                         and N.get(candidate, 'Enemy_State', slot) >= 128 for slot in range(6))
            if mature or collected:
                maturity_update = frames
        same_behavior = expect_parity and maturity_update is None
        if same_behavior:
            compare_play(original, candidate, ('Play', frames, candidate.controller_pad))
        if pickup:
            for slot in range(6):
                flag = N.get(candidate, 'Enemy_Flag', slot)
                if not 0 < flag < 128 or N.get(candidate, 'Enemy_ID', slot) != POWERUP_OBJECT:
                    if slot in item_tracks:
                        print('ITEM EXIT ' + json.dumps(dict(identity=identity, update=frames,
                                                            last=item_tracks.pop(slot), after_flag=flag,
                                                            player=state(candidate))), flush=True)
                    continue
                kind = N.get(candidate, 'PowerUpType', slot)
                item = dict(update=frames, state=N.get(candidate, 'Enemy_State', slot),
                            x=N.get(candidate, 'Enemy_X_Position', slot)
                            + 256 * N.get(candidate, 'Enemy_PageLoc', slot),
                            y=N.get(candidate, 'Enemy_Y_Position', slot),
                            y_page=N.get(candidate, 'Enemy_Y_HighPos', slot))
                if (slot, kind) not in births:
                    births[slot, kind] = item
                    print('ITEM ' + json.dumps(dict(identity=identity, slot=slot, kind=kind,
                                                    **item)), flush=True)
                    if kind < len(ITEM_BLOCKS):
                        bx = ITEM_BLOCKS[kind]
                        tiles = Current.W.address(candidate.bundle, 'Block_Buffer_1')
                        rows = [[candidate[tiles + (x // 256) % 2 * 208 + (y - 32) // 16 * 16 + (x % 256) // 16]
                                 for x in range(bx - 48, bx + 113, 16)] for y in range(112, 193, 16)]
                        print('ITEM AREA ' + json.dumps(dict(x=bx - 48, y=112, tiles=rows)), flush=True)
                elif frames % 32 == 0 or item_tracks.get(slot, item)['state'] < 128 <= item['state']:
                    print('ITEM POSITION ' + json.dumps(dict(item=item, player=state(candidate))), flush=True)
                item_tracks[slot] = item
            if len(collected) == len(pickup_order):
                s = state(candidate)
                goal_tier = sum(kind < 2 for kind in pickup_order)
                assert s['PlayerStatus'] == goal_tier and candidate.ram[2][0x7F + variant] == 0x10 | goal_tier
                assert s['NumberofLives'] == 2 + int(3 in pickup_order) and s['GameEngineSubroutine'] == 8
                if 2 in pickup_order:
                    assert N.get(candidate, 'StarInvincibleTimer') > 0
                if frames - collected[-1]['update'] == 25:
                    baseline_tier = N.get(original, 'PlayerStatus')
                    if repair_pickup:
                        assert baseline_tier == (goal_tier if palette else 0)
                    pickup_result.update(passed=True, identity=identity, mode=pickup, replay_updates=frames,
                                         comparable_updates=(maturity_update or (frames + 1)) - 1,
                                         baseline_tier=baseline_tier,
                                         pickups=collected, terminal=s, completed_updates_after_pickup=25,
                                         candidate_SHA256=candidate_sha, gameplay_seeds=0, outputs=0)
                    raise PickupCompleted
        if frames % 250 == 0:
            progress = dict(identity=identity, frames=frames, state=state(candidate))
            if same_behavior:
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
    try:
        with patch.object(Harness, 'Factory', factory), patch.object(Harness, 'cold', cold), \
                patch.object(Frames, 'frame', paired):
            result = Harness.run(raw, identity, limit)
    except PickupCompleted:
        return pickup_result
    result.update(paired_frames=frames, parent_CPU=sums_old, candidate_CPU=sums_new)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--identity', nargs='+', choices=Frozen.IDENTITIES, default=['burns'])
    parser.add_argument('--limit', type=int, default=6000)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--retry', action='store_true')
    mode.add_argument('--pickup', choices=('mushroom', 'flower', 'all'))
    parser.add_argument('--repair-death', action='store_true')
    parser.add_argument('--repair-pickup', action='store_true')
    parser.add_argument('--palette', action='store_true')
    args = parser.parse_args()
    from check_contra_force_combined_palette_1122 import comparison_base
    parent = comparison_base(Fast.Hud.ROM.read_bytes())
    for identity in args.identity:
        result = run(parent, identity, args.limit, retry=args.retry, repair_death=args.repair_death,
                     pickup=args.pickup, repair_pickup=args.repair_pickup, palette=args.palette)
        print('RESULT ' + json.dumps(result, separators=(',', ':')), flush=True)
        assert result['passed'], 'The paired route did not reach its finish condition'
