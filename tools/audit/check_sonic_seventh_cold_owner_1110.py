"""Qualify Sonic's actual seventh common cold owner, in memory only.

This deliberately leaves the public selector and scene router at six owners.
The proposed cookie commits only after the original Sonic code has been copied
and read back. No menu entry, gameplay hook, cartridge or artifact is produced.
"""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys

R = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R / 'tools/reference'))
import check_sonic_compact_cold_worker_1110 as C
import check_sonic_resident_funding_1110 as Funding
import sonic_sms_cold_payload_1110 as Payload
from check_mini_funded_actor_1108_v3 import slim_fork

O, N = C.O, C.N
CHR = 1048592


def digest(data):
    return sha256(data).hexdigest()


def proposal(raw):
    program = C.B.build()
    compact, compact_patches, old_rows = C.proposal(raw, program)
    base = C.Current.W.bundle(raw)
    shifted, sh_layout = Funding.proposal(base)
    _, demo_layout = Funding.retired_demo(base)
    packet = Payload.build()
    image, patches = bytearray(compact), list(compact_patches)

    def put(bank, pc, old, new, role):
        at = C.off(bank, pc)
        assert len(old) == len(new) and image[at:at + len(old)] == old, (role, bank, hex(pc))
        image[at:at + len(new)] = new
        patches.append(dict(bank=bank, pc=pc, bytes=len(new), old_hex=old.hex(),
                            new_hex=new.hex(), role=role))

    # Apply the independently qualified Sh factor and its two imports. Its
    # front byte is then explicitly granted to the common owner's DK copier.
    for start, size in ((0xabd4, 65), (0xaa8b, 3), (0xac47, 3)):
        at = C.off(65, start)
        put(65, start, raw[at:at + size], shifted[at:at + size], 'Qualified Sh carry-result factor')
    cookie_pc = demo_layout['fixed']['start']
    at = C.off(126, cookie_pc)
    put(126, cookie_pc, raw[at:at + 18], packet['cookie'] + b'\xea\xea',
        'Immutable Sonic cookie in retired, unreferenced demo entry')

    # The complete 99-byte shared allocation includes every live original
    # table, cookie and instruction. No presumed free byte is borrowed.
    extra_pc, extra_end = 0xab72, 0xabd5
    at = C.off(65, extra_pc)
    old_extra = bytes(image[at:at + extra_end - extra_pc])
    old_cookie = raw[C.off(65, 0xab9d):C.off(65, 0xabad)]
    assert old_cookie[:3] == bytes((0xa7, 38, 2))
    desc = (program['new']['symbols']['BbColdExDescriptor'], 0xbf93,
            program['new']['symbols']['BbColdBBDescriptor'], 0xdfe0, 0xb9f9,
            program['new']['symbols']['GfColdDescriptor'], 0xaffa)
    cookies = (0xafda, 0xab9f, 0xafea, 0xa7c5, 0xb003, 0xab81, cookie_pc, 0xaa78)

    def planes(values):
        return bytes(v & 255 for v in values) + bytes(v >> 8 for v in values)

    far_tail = raw[C.off(65, extra_pc):C.off(65, extra_pc) + 15]
    getsu_cookie = raw[C.off(65, 0xab81):C.off(65, 0xab91)]
    retire_low = bytes((0, 0x8f, 0x7a, 0x0c, 0, 0, 0))
    retire_high_nonzero = bytes((0xd9, 0xbb, 0xd6))
    dk_copy = bytes.fromhex('a006b9dca799e0df8810f760')
    extra = (far_tail + getsu_cookie + planes(desc) + old_cookie + planes(cookies)
             + retire_low + retire_high_nonzero + dk_copy)
    assert len(extra) == 99
    assert extra[0xabc9 - extra_pc:] == dk_copy
    assert extra[0xabc5 - extra_pc] == 0  # high[0] aliases retireLow[6]; never read.
    put(65, extra_pc, old_extra, extra, 'Seven complete owner tables, bounded retire high plane and relocated DK copier')
    for pc, old, new in ((0xaf0f, 0xab91, 0xab91), (0xaf14, 0xab97, 0xab98),
                         (0xaf1a, 0xabad, 0xabaf), (0xaf1f, 0xabb4, 0xabb7),
                         (0xaf5f, 0xabbb, 0xabbf), (0xaf67, 0xabc1, 0xabc5),
                         (0xae83, 0xabc7, 0xabc9)):
        put(65, pc, old.to_bytes(2, 'little'), new.to_bytes(2, 'little'), 'Seven-owner table/copy linkage')
    for pc, old, new in ((0xaee9, 6, 7), (0xaf07, 6, 7), (0xaf50, 5, 6), (0xa80e, 6, 7)):
        put(65, pc, bytes((old,)), bytes((new,)), 'Cold/authentication registry only; Sh remains separate')
    # Actual low-byte zero branch dominates every retire high-plane read.
    assert raw[C.off(65, 0xaf5e):C.off(65, 0xaf6c)] == bytes.fromhex('bdbbabf0168d6c01bdc1ab8d6d01')
    assert all(not lo or i in (1, 2, 3) for i, lo in enumerate(retire_low))
    # These remain intentionally SIX. A valid cold cookie is not permission
    # to execute Sonic through the foreign Mini/Getsu dispatch registry.
    for pc in (0xa750, 0xb01b):
        assert image[C.off(65, pc):C.off(65, pc) + 2] == bytes((0xc9, 6))
    assert image[C.off(65, 0xabd5):C.off(65, 0xac10)] == shifted[C.off(65, 0xabd5):C.off(65, 0xac10)]

    alias = json.loads((R / 'docs/qa/allocations/sonic-sms-fairy-repack-1110.json').read_text())['mandatory_atomic_source_change']
    a = alias['file_offset']
    assert image[a:a + 27] == bytes.fromhex(alias['old_hex'])
    image[a:a + 27] = bytes.fromhex(alias['new_hex'])
    for index, page in enumerate(packet['code_pages']):
        a = CHR + page * 1024
        image[a:a + 1024] = packet['kernel'][index * 1024:(index + 1) * 1024]
    a = CHR + packet['metadata_page'] * 1024
    image[a:a + 1024] = packet['metadata']
    return bytes(image), program, packet, patches, old_rows, sh_layout


def six_regressions(base, trial, program, rows):
    counts, seeds = Counter(), {}
    for owner in range(37, 43):
        print('Existing owner regression', owner, flush=True)
        old, new = O.blank(base), O.blank(trial)
        a, b = C.cold(old, owner, program['old']), C.cold(new, owner, program['new'])
        C.parity(old, new, a, b)
        assert 3 not in a['descriptor_offsets']
        assert set(b['descriptor_offsets']) == {0, 1, 2} | set(range(3, 3 + rows[owner]['rows'] * 2))
        O.clear_logs(old); O.clear_logs(new)
        seeds[owner] = old, new
        a, b = slim_fork(old), slim_fork(new)
        x, y = C.cold(a, owner, program['old']), C.cold(b, owner, program['new'])
        C.parity(a, b, x, y)
        assert x['PPU_reads'] == y['PPU_reads'] == 0
        counts['existing_cold_pairs'] += 1; counts['existing_warm_pairs'] += 1
        for bank in (2, 3):
            for index in range(16):
                a, b = slim_fork(old), slim_fork(new)
                a.ram[bank][0x1fe0 + index] ^= 1; b.ram[bank][0x1fe0 + index] ^= 1
                assert not C.invoke(a, O.AUTH)['P'] & 1 and not C.invoke(b, O.AUTH)['P'] & 1
                assert not a.ram_writes and not b.ram_writes
                counts['existing_header_poison_pairs'] += 1
        for fault in ('write-protection', (2, 0), (3, 0) if rows[owner]['code_rows'] else (2, 0x1000)):
            a, b = O.blank(base), O.blank(trial)
            if fault == 'write-protection': a.protection = b.protection = [0, 0]
            else: a.corrupt_at = b.corrupt_at = fault
            x = C.cold(a, owner, program['old'], expect_success=False)
            y = C.cold(b, owner, program['new'], expect_success=False)
            C.parity(a, b, x, y, fault=True,
                     dk_failed_descriptor=owner == 40 and O.headers(a) != (bytes(16), bytes(16)))
            counts['existing_fault_pairs'] += 1
        for fields in (dict(SelectedCharacter=44), dict(OperMode=0), dict(FamilyMainCommit=0),
                       dict(DisableScreenFlag=0), dict(Mirror_PPUMASK=24), dict(NmiDisable=0)):
            a, b = O.blank(base), O.blank(trial)
            for m in (a, b): O.scene(m, owner); N.put(m, **fields); O.clear_logs(m)
            before = [bytes(row) for m in (a, b) for row in m.ram]
            assert not C.invoke(a)['P'] & 1 and not C.invoke(b)['P'] & 1
            assert before == [bytes(row) for m in (a, b) for row in m.ram]
            assert not a.ram_writes and not b.ram_writes
            counts['existing_guard_pairs'] += 1
    for source in range(37, 43):
        dest = 37 + (source - 36) % 6
        a, b = (slim_fork(m) for m in seeds[source])
        x, y = C.cold(a, dest, program['old']), C.cold(b, dest, program['new'])
        C.parity(a, b, x, y)
        counts['existing_retire_pairs'] += 1
    return counts, seeds


def sonic_owned(m, packet):
    assert O.headers(m) == (packet['cookie'], packet['cookie'])
    assert bytes(m.ram[2][:0x900]) == bytes(0x900)
    assert bytes(m.ram[2][0x1000:0x1400]) == packet['metadata']
    assert bytes(m.ram[3][:7168]) == packet['kernel']


def seventh(trial, program, packet, seeds):
    counts = Counter()
    own = O.blank(trial)
    before = tuple(bytes(row) for row in own.ram)
    result = C.cold(own, 43, program['new'])
    sonic_owned(own, packet)
    assert result['PPU_reads'] == 8 * (2048 + 2), result
    assert result['descriptor_offsets'] == [0, 1, 2, 3, 4]
    assert bytes(own.ram[3][7168:0x1fe0]) == before[3][7168:0x1fe0]
    assert bytes(own.ram[2][0x900:0x1000]) == before[2][0x900:0x1000]
    assert bytes(own.ram[2][0x1400:0x1fd0]) == before[2][0x1400:0x1fd0]
    commits = [(b, v) for b, a, v in own.ram_writes if a == 0x1fe0]
    assert commits[-2:] == [(3, 0xa7), (2, 0xa7)] and all(v == 0 for _, v in commits[:-2])
    assert C.invoke(own, O.AUTH)['P'] & 1
    O.clear_logs(own)
    warm = slim_fork(own)
    assert C.cold(warm, 43, program['new'])['PPU_reads'] == 0
    assert warm.ram == own.ram
    counts['Sonic_cold'] = counts['Sonic_warm'] = 1
    for bank in (2, 3):
        for index in range(16):
            m = slim_fork(own); m.ram[bank][0x1fe0 + index] ^= 1
            assert not C.invoke(m, O.AUTH)['P'] & 1 and not m.ram_writes
            counts['Sonic_header_poisons'] += 1
    for fault in ('write-protection', (2, 0x1000), (3, 0), (3, 1023), (3, 1024), (3, 4095), (3, 6144), (3, 7167)):
        m = O.blank(trial)
        if fault == 'write-protection': m.protection = [0, 0]
        else: m.corrupt_at = fault
        C.cold(m, 43, program['new'], expect_success=False)
        assert O.headers(m) == (bytes(16), bytes(16)) and not C.invoke(m, O.AUTH)['P'] & 1
        counts['Sonic_readback_faults'] += 1
    for fields in (dict(SelectedCharacter=44), dict(OperMode=0), dict(FamilyMainCommit=0),
                   dict(DisableScreenFlag=0), dict(Mirror_PPUMASK=24), dict(NmiDisable=0)):
        m = O.blank(trial); O.scene(m, 43); N.put(m, **fields); O.clear_logs(m)
        saved = [bytes(row) for row in m.ram]
        assert not C.invoke(m)['P'] & 1 and saved == [bytes(row) for row in m.ram] and not m.ram_writes
        counts['Sonic_guard_cases'] += 1
    # A copied/authenticated raw43 is still denied by the public selector.
    m = slim_fork(own)
    assert not C.invoke(m, 0xb08c)['P'] & 1 and not m.ram_writes
    counts['Sonic_public_selector_still_rejects'] = 1
    for source, (_, seeded) in seeds.items():
        print('Existing -> Sonic -> existing transition', source, flush=True)
        m = slim_fork(seeded)
        C.cold(m, 43, program['new']); sonic_owned(m, packet)
        C.cold(m, source, program['new'])
        assert O.headers(m) == O.headers(seeded)
        # Compare all bytes actually redefined by the existing owner's cold
        # load. Opaque unowned private tails need not match a fresh seed.
        for bank in (2, 3):
            writes = {at for b, at, _ in m.ram_writes if b == bank}
            # This log includes only the destination call (cold clears it).
            assert all(m.ram[bank][at] == seeded.ram[bank][at] for at in writes)
        assert C.invoke(m, O.AUTH)['P'] & 1
        counts['Sonic_roundtrip_owner_transitions'] += 1
    m = slim_fork(own)
    N.put(m, SelectedCharacter=0)
    C.invoke(m, O.RETIRE)
    assert m.ram[2][0x1fe0] == m.ram[3][0x1fe0] == 0
    assert not C.invoke(m, O.AUTH)['P'] & 1
    counts['Sonic_foreign_retire'] = 1
    return counts, result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--static-only', action='store_true')
    args = p.parse_args()
    output = args.output.resolve()
    assert output.is_relative_to(R / 'build') and not output.exists()
    raw = C.ROM.read_bytes()
    image, program, packet, patches, rows, sh = proposal(raw)
    result = dict(passed=True, source_only=True, outputs_written=0, ROM_written=False,
                  parent_SHA256=C.PIN, in_memory_SHA256=digest(image), proposed_cookie=packet['cookie'].hex(),
                  no_public_raw43_admission=True, no_gameplay_or_interrupt_qualification=True,
                  source_payload_bytes=len(packet['core']['image']), stored_payload_bytes=len(packet['kernel']),
                  descriptor=0xaffa, metadata_page=328, code_pages=list(packet['code_pages']),
                  CoExtra_half_open=[0xab72, 0xabd5], Sh_entry=sh['entry'], patches=patches)
    if not args.static_only:
        base, trial = C.Current.W.bundle(raw), C.Current.W.bundle(image)
        counts, seeds = six_regressions(base, trial, program, rows)
        extra, cold_result = seventh(trial, program, packet, seeds)
        counts.update(extra)
        result.update(actual_CPU=dict(counts), Sonic_cold_result=cold_result)
        assert C.Current.inventory(raw) == C.Current.inventory(image)
        result['all_100_current_menu_entries_unchanged'] = True
    assert not output.exists()
    print(json.dumps(result, sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
