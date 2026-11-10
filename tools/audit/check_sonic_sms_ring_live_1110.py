"""Exact 9897 source-only Sonic ninth-row, live pickup and lifecycle checks."""
import argparse
from collections import Counter
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json
from pathlib import Path
from unittest.mock import patch

import check_smb2_menu_tier_isolation_1110 as Menu
import check_sonic_injury_prince_rebase_1110 as Prior
import check_sonic_earned_injury_1110 as Native
import check_sonic_eighth_cold_owner_1110 as Eighth
import check_sonic_fairy_funding_1110 as Alias
import check_sonic_public_admission_1110 as Public
import sonic_sms_ring_live_1110 as Ring

R, CHR = Ring.ROOT, Alias.CHR
PIN = '9897c2b85489024be25b4b296d0ea57975a579ba1e3ff37a71f7ac3e0b195b97'
C, O, N, W = Eighth.C, Eighth.O, Native.N, Native.W
META, COOKIE = 1048592 + 328 * 1024, 1034472
RESERVATION = R / 'docs/qa/allocations/sonic-sms-fairy-repack-1110.json'


def digest(data):
    return sha256(data).hexdigest()


def proposal():
    prior, common, p, _ = Prior.reconstruct()
    expected, menu = Menu.proposal(prior)
    raw = Menu.NIGHTLY.read_bytes()
    assert raw == expected and digest(raw) == PIN and menu['changed_bytes'] == 24
    ledger = json.loads(RESERVATION.read_text())
    assert Ring.PAGE in ledger['conditional_physical_CHR_pages'] and Ring.PAGE == 333
    alias = ledger['mandatory_atomic_source_change']
    at = alias['file_offset']
    assert raw[at:at + 27] == bytes.fromhex(alias['new_hex'])
    for compiler in ((69, 0xa4cf, 'e01b9002a203a9c68da17da9c68d1651bdaac28d086b'),
                     (69, 0xa50a, 'ad086ba201a0008d6a01a9758d6c01a9a28d6d01a9be4c5a01')):
        bank, pc, preimage = compiler
        at = 16 + bank * 8192 + (pc & 8191)
        assert raw[at:at + len(preimage)//2].hex() == preimage
    assert raw[:CHR].count(bytes.fromhex('bdaac2')) == 1
    before_page = Alias.page_bytes(raw, Ring.PAGE)
    assert before_page == Alias.page_bytes(raw, 319) == Alias.page_bytes(prior, Ring.PAGE)
    old = p['packet']
    assert raw[META:META + 1024] == old['metadata']
    assert raw[COOKIE:COOKIE + 16] == old['cookie'] and raw[:CHR].count(old['cookie']) == 1
    bundle = C.Current.W.bundle(raw)
    new = Ring.build(p, bundle)
    packet = new['packet']
    image = bytearray(raw)
    for row, page in enumerate(old['code_pages']):
        first = CHR + page * 1024
        block = slice(row * 1024, (row + 1) * 1024)
        assert raw[first:first + 1024] == old['kernel'][block]
        image[first:first + 1024] = packet['kernel'][block]
    image[META:META + 1024] = packet['metadata']
    image[COOKIE:COOKIE + 16] = packet['cookie']
    at = CHR + Ring.PAGE * 1024
    image[at:at + 1024] = packet['ring_extension']
    assert all(Alias.page_bytes(raw, page) == Alias.page_bytes(image, page)
               for page in (319, 320, 329, 331, 332, 334, 335))
    assert image[:COOKIE] == raw[:COOKIE] and image[COOKIE + 16:CHR] == raw[COOKIE + 16:CHR]
    assert packet['kernel'][:5526] == old['kernel'][:5526]
    assert packet['kernel'][0x1fe0:] == old['kernel'][0x1fe0:]
    assert packet['metadata'][0x2e9:0x31f] == old['metadata'][0x2e9:0x31f]
    return raw, bytes(image), common, new, dict(
        current_SHA256=PIN, image_SHA256=digest(image), page=Ring.PAGE, page_file_offset=at,
        page_preimage_SHA256=digest(before_page), extension_SHA256=digest(packet['ring_extension']),
        cookie=packet['cookie'].hex(), metadata=sorted(new['ring_boot']['used'].items()),
        code=new['ring_program']['used'], state_half_open=[Ring.CONTEXT, Ring.CONTEXT + 59],
        site_PCs={label: pc for pc, _, label in new['ring_sites']})


def aliases(raw, image):
    """Compare real bounded fairy publications with the now-different CHR333."""
    assert Alias.page_bytes(raw, Ring.PAGE) != Alias.page_bytes(image, Ring.PAGE)
    bundles = [Alias.C.W.bundle(q) for q in (raw, image)]
    with patch.object(Alias.N, 'Bus', Alias.FundingBus):
        seeds = [Alias.N.fresh(b) for b in bundles]
    for pose in range(27):
        for face in (1, 2):
            results = []
            for seed in seeds:
                m = Alias.slim_fork(seed)
                Alias.N.put(m, SelectedCharacter=5, Z2Variant=1, PlayerFacingDir=face,
                            Player_SprAttrib=0, VRAM_Buffer1_Offset=0, NmiDisable=255, FamilyMainCommit=1)
                a = Alias.invoke(m, 'Z2SetPose', x=pose)
                b = Alias.invoke(m, 'Z2PublishBody')
                Alias.regular_nmi(m)
                assert m.table_reads == [pose] and m.pattern_events
                assert all(page != Ring.PAGE for _, page, _ in m.pattern_events)
                results.append((a, b, Alias.normalize_state(m)))
            assert results[0] == results[1], (pose, face)
    # Restoring only the original pose25 selector exposes the new data as
    # fairy art. This proves the existing alias is a real dependency.
    broken = bytearray(image)
    pose = Ring.PAGE - 308
    assert pose == 25 and broken[574138 + pose] == (319 & 255)
    broken[574138 + pose] = Ring.PAGE & 255
    with patch.object(Alias.N, 'Bus', Alias.FundingBus):
        m = Alias.N.fresh(Alias.C.W.bundle(bytes(broken)))
    Alias.N.put(m, SelectedCharacter=5, Z2Variant=1, PlayerFacingDir=1, NmiDisable=255, FamilyMainCommit=1)
    Alias.invoke(m, 'Z2SetPose', x=pose)
    Alias.invoke(m, 'Z2PublishBody')
    Alias.regular_nmi(m)
    assert any(page == Ring.PAGE and content == digest(Alias.page_bytes(image, Ring.PAGE))
               for _, page, content in m.pattern_events)
    return dict(paired_publications=54, stale_table_negative=1)


def cold(raw, image, common, p):
    q = p['packet']
    old = O.blank(C.Current.W.bundle(raw))
    before = C.cold(old, 43, common['new'])
    seed = O.blank(C.Current.W.bundle(image))
    zero = tuple(bytes(row) for row in seed.ram)
    after = C.cold(seed, 43, common['new'])
    Eighth.owned(seed, q)
    assert after['PPU_reads'] == before['PPU_reads'] + 2050 == 20436
    assert after['descriptor_offsets'] == before['descriptor_offsets'] == list(range(5))
    assert bytes(seed.ram[2][0x1400:0x1800]) == q['ring_extension']
    assert bytes(seed.ram[2][0x1800:0x1fe0]) == zero[2][0x1800:0x1fe0]
    assert bytes(seed.ram[3][0x1ff0:]) == zero[3][0x1ff0:]
    assert [b for b, at, val in seed.ram_writes if at == 0x1fe0 and val == 0xa7][-2:] == [3, 2]
    result = Counter(cold=1)
    m = Eighth.S.slim_fork(seed)
    assert C.cold(m, 43, common['new'])['PPU_reads'] == 0 and m.ram == seed.ram
    result['warm'] += 1
    for bank, address in [(2, 0x1400 + delta) for delta in (0, 393, 394, 767, 1023)] + [(3, 0x1fdf)]:
        m = O.blank(C.Current.W.bundle(image))
        m.corrupt_at = bank, address
        C.cold(m, 43, common['new'], expect_success=False)
        assert O.headers(m) == (bytes(16), bytes(16))
        result['readback_fault_reject'] += 1
    for owner in range(37, 43):
        a, b = (O.blank(C.Current.W.bundle(source)) for source in (raw, image))
        left, right = (C.cold(bus, owner, common['new']) for bus in (a, b))
        C.parity(a, b, left, right)
        result['foreign_cold_exact'] += 1
    return dict(cases=dict(result), reads=[before['PPU_reads'], after['PPU_reads']], minimum_SP=after['minimum_SP'])


def typed_lifecycle(image, common, p):
    """Directed public veneers on actual cold-mapped RAM, separate from natural restart."""
    t = Public.A.T
    seed = t.install(C.Current.W.bundle(image), p, common)
    t.S.scene(seed, 40, 176)
    t.S.set_native(seed, OperMode=1, OperMode_Task=3, WorldNumber=0, LevelNumber=0, AreaAddrsLOffset=5)
    # A genuine constructor owns scene seeding. The directed seed supplies
    # arbitrary already-live values to test each public Fresh path.
    s = p['ring_program']['symbols']
    lo, tile, hi = (s[key] - 0xc000 for key in ('RingContext', 'SceneTiles', 'SceneEnd'))
    poison = bytes(range(1, hi - lo + 1))
    result = Counter()
    for row in (15, 36):
        m = t.clone(seed, p)
        m.ram[2][lo:hi] = poison
        visits = []
        def trace(mem, cpu):
            if cpu.pc in (0xbd69, s['RingFresh'], s['RingClear']):
                visits.append((hex(cpu.pc), tuple(mem.rawtags), cpu.a, cpu.x))
        assert Public.public(m, row, observe=trace).p & 1
        assert not any(m.ram[2][lo:hi]), (row, bytes(m.ram[2][lo:hi]).hex(), visits)
        result['actual_public_fresh_clears'] += 1
        t.S.scene(m, 40, 176)
        assert Public.public(m, 0).p & 1
        assert bytes(m.ram[2][tile:hi]) == b'\x7a\x7b\x7b'
        result['actual_constructor_reseeds'] += 1
    # Public row19 is an outer compatibility leaf. Its installed veneer
    # never dispatches the otherwise present private row19 vector.
    m = t.clone(seed, p)
    m.ram[2][lo:hi] = poison
    at = 16 + 65 * 8192 + (0xb0c5 & 8191)
    assert image[at:at + 3] == bytes.fromhex('4c00b1')
    assert Public.public(m, 19).p & 1 and bytes(m.ram[2][lo:hi]) == poison
    result['compatibility_row19_preserves_state'] += 1
    for bank in (2, 3):
        for i in (0, 1, 15):
            for row in (0, 15, 36):
                m = t.clone(seed, p)
                m.ram[2][lo:hi] = poison
                m.ram[bank][0x1fe0 + i] ^= 1
                before = tuple(bytes(q) for q in m.ram)
                assert not Public.public(m, row).p & 1
                assert tuple(bytes(q) for q in m.ram) == before
                result['corrupt_header_rejects_ring_code'] += 1
    m = t.clone(seed, p)
    m.ram[2][lo:hi] = poison
    t.S.set_native(m, GamePauseStatus=1)
    assert Public.public(m, 0).p & 1
    assert bytes(m.ram[2][lo:hi]) == poison
    result['pause_preserves_live_state'] += 1
    return dict(result)


def live(image, p):
    with redirect_stdout(io.StringIO()) as log:
        try:
            opening, m = Native.Opening.run(image, p, goal_x=190)
        except Exception:
            raise AssertionError(log.getvalue())
    assert opening['passed']
    q = p['packet']
    b = m.bundle
    ring = p['ring_program']['symbols']
    ring_at = Ring.CONTEXT - 0xc000
    ring_end = ring['SceneEnd'] - 0xc000
    tiles_at = ring['SceneTiles'] - 0xc000
    assert bytes(m.ram[2][0x1400:0x1800]) == q['ring_extension']
    assert bytes(m.ram[2][tiles_at:ring_end]) == b'\x7a\x7b\x7b'
    counts, events, picks, enemies = Counter(), [], [], []
    callback = {name: W.address(b, name) for name in ('ForceInjury', 'KillPlayer')}
    points = {(2, ring[name]): name for name in ('RingFresh', 'RingConstruct', 'RingProject', 'RingHurt')}
    points.update({((W.location(b, name) - 16) // 8192 | 128, address): name
                   for name, address in callback.items()})

    def state():
        s = Native.state(m)
        return (s['x'], s['y'], s['engine'], s['lives'], s['source_tick'], m.ram[2][ring_at])

    def observe(mem, cpu):
        if cpu.pc < 0x8000:
            return
        name = points.get((mem.rawtags[(cpu.pc - 0x8000) // 8192], cpu.pc))
        if name is None:
            return
        counts[name] += 1
        if name in ('RingFresh', 'RingConstruct', 'RingProject', 'RingHurt'):
            assert tuple(bytes(mem.ram[bank][0x1fe0:0x1ff0]) for bank in (2, 3)) == (q['cookie'],) * 2
        if name == 'ForceInjury':
            assert mem.ram[2][ring_at] == 5 and bytes(mem.ram[2][tiles_at:ring_end]) == b'\x78' * 3
            enemy = Native.actors(mem)[cpu.x]
            assert enemy['flag'] == 1 and enemy['id'] == 6 and enemy['state'] == 0
            enemies.append(enemy)
        if name != 'RingProject':
            events.append((name, state()))

    for frame in range(1000):
        before = state()
        m.controller_pad = 1 if not counts['KillPlayer'] else 0
        Native.Main.frame(m, observe)
        after = state()
        if before[-1] < after[-1]:
            picks.append(after)
        if counts['KillPlayer'] and after[2:4] == (8, 1) and counts['RingConstruct']:
            assert after[-1] == 0 and after[0] < 100
            assert tuple(N.get(m, name) for name in ('WorldNumber', 'LevelNumber', 'AreaAddrsLOffset')) == (0, 0, 5)
            assert bytes(m.ram[2][tiles_at:ring_end]) == b'\x7a\x7b\x7b'
            assert not any(m.ram[2][ring_at:tiles_at])
            break
    else:
        raise AssertionError(('Natural same-level life restart bound', state(), events, picks))
    assert [s[-1] for s in picks] == list(range(1, 6)), picks
    assert counts['ForceInjury'] == counts['KillPlayer'] == 1 and counts['RingHurt'] == 0
    return dict(frames_after_opening=frame + 1, terminal=after, callbacks=dict(counts),
                pickups=picks, lifecycle_events=events, hit=enemies[0], source_ring_hurt_live_connected=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--part', choices=('build', 'cold', 'typed', 'live', 'all'), default='all')
    args = parser.parse_args()
    assert args.output.resolve().is_relative_to(R / 'build') and not args.output.exists()
    raw, image, common, p, record = proposal()
    print(json.dumps(dict(event='proposal', **record), sort_keys=True), flush=True)
    if args.part in ('typed', 'all'):
        print(json.dumps(dict(event='typed_lifecycle', **typed_lifecycle(image, common, p)),
                         sort_keys=True), flush=True)
    if args.part in ('cold', 'all'):
        print(json.dumps(dict(event='cold', **cold(raw, image, common, p),
                              fairy=aliases(raw, image)), sort_keys=True), flush=True)
    if args.part in ('live', 'all'):
        print(json.dumps(dict(event='live', **live(image, p)), sort_keys=True), flush=True)
    assert not args.output.exists()
    print(json.dumps(dict(passed=True, source_only=True, output_files=0)), flush=True)


if __name__ == '__main__':
    main()
