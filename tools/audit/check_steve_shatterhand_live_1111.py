"""Run Steve's new punch and the existing Mike and Jay paths through actual Main."""

import json

import check_jay_silius_scene_lifecycle_1110 as Scene
from check_jay_silius_stock_draw_dispatch_1111 import DmaBus
import compose_steve_shatterhand_1111 as S


C, N, W = S.C, S.N, S.W


def field(m, name):
    return m[S.FIELDS[name]]


def mode(m):
    return tuple(N.get(m, name) for name in ('OperMode', 'OperMode_Task', 'GameEngineSubroutine'))


def player(m):
    return (N.get(m, 'Player_PageLoc') * 256 + N.get(m, 'Player_X_Position'),
            N.get(m, 'Player_Y_Position'))


def goombas(m):
    return [(slot, N.get(m, 'Enemy_PageLoc', slot) * 256 + N.get(m, 'Enemy_X_Position', slot),
             N.get(m, 'Enemy_Y_Position', slot))
            for slot in range(6) if N.get(m, 'Enemy_ID', slot) == 6
            and N.get(m, 'Enemy_Flag', slot) == 1 and not N.get(m, 'Enemy_State', slot) & 0x20]


def opening(raw, variant):
    m = Scene.menu(dict(W.Symbols.bundle(), raw=raw), variant)
    for update in range(480):
        if mode(m) == S.PLAY:
            return m, update
        C.Game.frame(m)
    raise AssertionError(('Native character did not enter 1-1', variant))


def punch_trace(m, linked):
    symbols = linked['symbols']
    calls = []
    births = []
    edges = []
    m.__class__ = DmaBus
    matched, expected, drawn = 0, set(), []
    for update, pad in enumerate([0] * 6 + [64] * 12 + [0] * 6):
        m.controller_pad = pad
        m.dma = None
        draw = []

        def visit(memory, cpu):
            if (memory.rawtags[2], cpu.pc) == (2, symbols['StevePunchControl']):
                calls.append((update, cpu.a))
                if N.get(m, 'JnPressed') & 64:
                    edges.append(update)
            if (memory.rawtags[1], cpu.pc) == (3, symbols['StevePunchBirth']):
                births.append((update, cpu.x, player(m)))
            if (memory.rawtags[2], cpu.pc) == (2, symbols['SteveDrawEmit']):
                x, y = player(m)
                screen = N.get(m, 'ScreenLeft_PageLoc') * 256 + N.get(m, 'ScreenLeft_X_Pos')
                left = N.get(m, 'PlayerFacingDir') == 2
                offsets = (-8, -16) if left else (16, 24)
                draw.extend(bytes((y, tile, 64 if left else 0, x - screen + dx))
                            for tile, dx in zip((32, 34), offsets, strict=True)
                            if 0 <= x - screen + dx <= 255)

        C.Game.frame(m, visit)
        if expected:
            assert m.dma is not None and expected == punch_cells(m.dma), (update, expected, punch_cells(m.dma))
            assert m.chr_latches[0] == 220 and m.ppuctrl & 0x20
            matched += 1
        expected = set(draw)
        assert expected == punch_cells(m[0x200:0x300]), (update, expected, punch_cells(m[0x200:0x300]))
        if expected:
            drawn.append((update, sorted(cell.hex() for cell in expected)))
    assert len(calls) == 24 and edges == [6] and [b[:2] for b in births] == [(8, 0)], (calls, edges, births)
    assert len(drawn) == matched == 6, (drawn, matched)
    assert not any(N.get(m, 'JnShotKind', i) for i in range(6))
    return dict(updates=len(calls), edges=edges, births=births, first_draw=drawn[0], matched_DMA=matched)


def punch_cells(oam):
    return {bytes(oam[at:at + 4]) for at in range(0, 256, 4)
            if oam[at] < 240 and oam[at + 1] in (32, 34)}


def assets(seed, parent, candidate):
    before = S.page(parent, 220)
    after = S.page(candidate, 220)
    assert before[:512] == after[:512] and after[512:576] == S.punch_art()
    poses = set()
    for facing in (1, 2):
        for state in range(4):
            for value in range(8):
                N.put(seed, PlayerFacingDir=facing, Player_State=state)
                C.Vector.call(seed, 'JnSetPose', x=value)
                assert N.get(seed, 'SmChrBank') == 220 and N.get(seed, 'PlayerChrBank') == 220
                at = C.offset(97, N.get(seed, 'SmPosePtr') + 256 * N.get(seed, 'SmPosePtr', 1))
                pose = candidate[at:at + 17]
                assert pose[0] == 16 and all(tile % 2 == 0 and tile < 32 for tile in pose[1::4]), pose.hex()
                poses.add(at)
    assert len(poses) == 8
    return dict(body_descriptors=len(poses), selector_cases=64, body_tiles=[0, 31],
                punch_tile_pairs=[32, 34], original_arm_SHA256=C.digest(after[512:576]))


def natural_goomba(m, linked):
    symbols = linked['symbols']
    for update in range(300):
        x, y = player(m)
        targets = goombas(m)
        if x >= 216 and targets and min(enemy[1] for enemy in targets) <= x + 32:
            break
        m.controller_pad = int(x < 216)
        C.Game.frame(m)
    else:
        raise AssertionError(('The first native Goomba did not approach Steve', player(m), goombas(m)))

    before = player(m), goombas(m)
    births, native_hits = [], []
    for age in range(15):
        m.controller_pad = 64 if age == 0 else 0

        def visit(memory, cpu):
            bank, pc = memory.rawtags[1], cpu.pc
            if (bank, pc) == (3, symbols['StevePunchBirth']):
                births.append((age, cpu.x, player(m)))
            if (bank, pc) == (226, 0xa563):
                punch = (field(m, 'SteveHitPage') * 256 + field(m, 'SteveHitX'),
                         field(m, 'SteveHitY'), field(m, 'SteveHitHigh'))
                native_hits.append((age, cpu.x, player(m), goombas(m), punch))

        C.Game.frame(m, visit)
        if native_hits:
            assert len(native_hits) == 1 and [b[:2] for b in births] == [(2, 0)], (births, native_hits)
            slot = native_hits[0][1]
            assert N.get(m, 'Enemy_State', slot) & 0x20 and N.get(m, 'FloateyNum_Control', slot) == 1
            assert N.get(m, 'NumberofLives') == 2
            assert field(m, 'SteveHitLife') == 0
            return dict(approach_updates=update, before=before, births=births, native_hits=native_hits,
                        score=N.get(m, 'FloateyNum_Control', slot), lives=N.get(m, 'NumberofLives'))
    raise AssertionError(('Steve missed the first native Goomba', before, births, native_hits, player(m),
                          goombas(m), {n: field(m, n) for n in S.FIELDS}))


def capacity(seed):
    cases = 0
    for offset in (0, 224, 228, 232, 252, 253):
        for rotation in (0, 28):
            m = C.Vector.clone(seed)
            m[0x200:0x300] = bytes((248, 0, 0, 0)) * 64
            m[S.FIELDS['StevePunchSelector']] = 1
            m[S.FIELDS['StevePunchPhase']] = 2
            N.put(m, CurrentOAMOffset=offset, GuestOamRotationActive=int(bool(rotation)),
                  RgOamRotation=rotation, PlayerFacingDir=1, Player_PageLoc=1,
                  Player_X_Position=0, ScreenLeft_PageLoc=0, ScreenLeft_X_Pos=248)
            C.Vector.call(m, 'JnDraw')
            wanted = {bytes((176, 32, 0, 24)), bytes((176, 34, 0, 32))} if offset <= 228 else set()
            assert punch_cells(m[0x200:0x300]) == wanted, (offset, rotation)
            assert N.get(m, 'CurrentOAMOffset') == offset + (8 if wanted else 0)
            cases += 1
    return dict(capacity_and_cross_page_draw_cases=cases)


def bad_headers(seed, linked):
    count = 0
    points = {linked['symbols'][name] for name in ('StevePunchControl', 'SteveDrawEmit')}
    for bank in (2, 3):
        for index in range(16):
            m = C.Vector.clone(seed)
            m.ram[bank][0x1fe0 + index] ^= 1
            m.controller_pad = 64

            def visit(memory, cpu):
                assert cpu.pc not in points or memory.rawtags[2] != 2, (bank, index, hex(cpu.pc))

            C.Game.frame(m, visit)
            assert not any(N.get(m, 'JnShotKind', i) for i in range(6))
            assert not punch_cells(m[0x200:0x300])
            assert N.get(m, 'NumberofLives') == 2
            count += 1
    return count


def vectors(seed, linked):
    symbols = linked['symbols']
    points = {(1, 226, symbols['SteveWeaponsGate']), (1, 222, S.HOT),
              (1, 3, symbols['SteveSharedMux']), (1, 3, symbols['SteveCombat']),
              (1, 3, symbols['StevePunchBirth']), (1, 3, symbols['SteveDraw']),
              (2, 2, symbols['StevePunchControl']), (2, 2, symbols['SteveDrawEmit'])}
    found = set()

    def state(m, cpu):
        return (tuple(bytes(ram) for ram in m.ram), tuple(m.rawtags), bytes(m[3:11]),
                bytes(m[0x15a:0x17b]), bytes(m[0x101 + cpu.sp:0x200]), bytes(m[0x200:0x300]),
                bytes(m[min(S.FIELDS.values()):max(S.FIELDS.values()) + 1]))

    def visit(m, cpu):
        match = {point for point in points if cpu.pc == point[2] and m.rawtags[point[0]] == point[1]}
        for point in match - found:
            for kind in ('NMI', 'IRQ'):
                q, d = C.Vector.clone(m, cpu)
                before = state(q, d)
                assert C.Vector.isr(q, d, kind) == 'returned', (point, kind)
                assert state(q, d) == before, (point, kind)
            found.add(point)

    for i in range(8):
        seed.controller_pad = 64 if i == 2 else 0
        C.Game.frame(seed, visit)
    assert found == points, points - found
    return dict(NMI_cuts=len(found), IRQ_cuts=len(found))


def parity(parent, candidate, linked):
    pads = [0] * 6 + [64] * 12 + [1] * 19 + [129] * 9 + [2] * 15 + [0] * 10 + [64] * 9
    result = {}
    for variant, name in enumerate(('Mike', 'Jay')):
        before, old_open = opening(parent, variant)
        after, new_open = opening(candidate, variant)
        assert new_open == old_open == 167
        if variant:
            assert C.Common.headers(after) == (linked['cookie'],) * 2
            assert before.ppu_reads == 12300 and after.ppu_reads == 14350
        else:
            assert before.ppu_reads == after.ppu_reads == 0
        for update, pad in enumerate(pads):
            for m in (before, after):
                m.controller_pad = pad
                C.Game.frame(m)
            old, new = C.Vector.app(before), C.Vector.app(after)
            assert (old if variant == 0 else old[:3] + old[4:]) == (
                    new if variant == 0 else new[:3] + new[4:]), (name, update)
            assert before.vram == after.vram and before.chr_latches == after.chr_latches, (name, update)
            if variant:
                assert before.ram[2][:256] == after.ram[2][:256], (name, update)
        result[name] = dict(updates=len(pads), player=player(after),
                            lives=N.get(after, 'NumberofLives'), cold_ppu_reads=after.ppu_reads)
    return result


def rebase(current, candidate):
    if C.digest(current) == S.PIN:
        return {}
    import compose_prince_brick_1111 as Prince

    old, new, _ = Prince.support_workers()
    parent, _ = Prince.replace_worker(current, new, old)
    assert C.digest(parent) == S.PIN
    old_candidate, linked = S.proposal(parent)
    assert all(parent[start:start + length] == current[start:start + length]
               for start, length in linked['spans'])
    restored, _ = Prince.replace_worker(old_candidate, old, new)
    assert restored == candidate
    return dict(recovered_parent=S.PIN, old_candidate=C.digest(old_candidate), exact=True)


def main():
    raw = S.Donor.HOST.read_bytes()
    installed = raw if C.digest(raw) == S.LIVE_PIN else None
    if installed is not None:
        raw = S.recover_parent(installed)
    candidate, linked = S.proposal(raw)
    if installed is not None:
        assert candidate == installed
    print('Steve candidate', C.digest(candidate), linked['cookie'].hex(), flush=True)
    m, scene_updates = opening(candidate, 2)
    assert C.Common.headers(m) == (linked['cookie'],) * 2
    assert m.ppu_reads == 14350
    assert bytes(m.ram[2][0x1800:0x1c00]) == S.page(candidate, 220)
    start = C.Vector.clone(m)
    print('Steve native opening', scene_updates, player(m), 'PPU reads', m.ppu_reads, flush=True)
    right = punch_trace(m, linked)
    left = C.Vector.clone(start)
    left.controller_pad = 2
    C.Game.frame(left)
    assert N.get(left, 'PlayerFacingDir') == 2
    flipped = punch_trace(left, linked)
    print('Steve held B and native DMA', right, flipped, flush=True)
    hit = natural_goomba(C.Vector.clone(start), linked)
    art = assets(C.Vector.clone(start), raw, candidate)
    interrupts = vectors(C.Vector.clone(start), linked)
    rejected = bad_headers(start, linked)
    limits = capacity(start)
    foreign = parity(raw, candidate, linked)
    print(json.dumps(dict(passed=True, sha256=C.digest(candidate), natural_goomba=hit,
                          foreign=foreign, right=right, left=flipped, assets=art,
                          headers_rejected=rejected, limits=limits, interrupts=interrupts,
                          rebase=rebase(raw, candidate), output_files=0), sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
