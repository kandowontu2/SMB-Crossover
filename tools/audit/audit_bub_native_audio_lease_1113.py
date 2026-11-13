"""Current Rogue/Bub native-funding study; stdout, no production allocation.

The optional reader comparison uses an in-memory, poisoned audio-view fixture.
The auth timing kernel is explicitly placed in disposable fixture WRAM; that
address is not a proposed runtime allocation. No gameplay proposal is emitted.
"""
from collections import Counter
from hashlib import sha256
import argparse
import json
import re

import check_bub_current_budget_1113 as B
import check_prince_brick_support_1111 as H
import check_hogan_current_bounded_v1 as M
from check_ff_head_lifetime_irq_1110 import clone
from check_tmnt_render_oa import address, location


R = B.R
PAGE_SHA = '3574a5efbb8dd0c3b5708ef977aa329e487ccbf28f3630a2352aadedd8ed429c'
BANK_SHA = '5ad254f292f54fa7147dd7917170b9903933ef27fcd7e1a2fd863b389bacf76b'
READER = bytes.fromhex(
    '2010c4ad517060a5e9c9a0b02ea5230a0a0a0a0a1865e938e980aabd67bc85e9'
    'bda7bb103b8d45018d1551a000b1e88d5170a9be8d45018d155160e9a0aabd5fbe'
    '85e9bd3fbeb0db8a48a52ff0050af0049002491d852f49f0852e688aa52e600980'
    '8d45018d1551a00049dad0062005b74c38c44c00bf')
WORD = lambda n: int(n).to_bytes(2, 'little')
ABS = lambda op, n: bytes((op,)) + WORD(n)


def at(bank, pc):
    return 16 + bank * 8192 + (pc & 8191)


def page_rows(raw, bundle):
    for mode, count, stem in (('lower', 192, 'RdaLower'),
                              ('upper', 32, 'RdaUpperRaw')):
        banks, highs = (location(bundle, stem + suffix)
                        for suffix in ('BankTable', 'HighTable'))
        for row in range(count):
            tag, high = raw[banks + row], raw[highs + row]
            assert 0xa0 <= high <= 0xbf
            yield dict(mode=mode, row=row, tag=tag, high=high,
                       bank_table_file=banks + row)


def bindings(raw):
    assert sha256(raw).hexdigest() == B.PIN
    bundle = H.C.Start.W.bundle(raw)
    assert raw[at(97, 0xc409):at(97, 0xc480)] == READER
    assert address(bundle, 'RdaReadRomValue') == 0xc410
    assert address(bundle, 'RdaPage94') == 0xbf00
    assert location(bundle, 'RdaPage94') == at(87, 0xbf00)
    bank = raw[at(87, 0xa000):at(88, 0xa000)]
    page = bank[-256:]
    assert sha256(bank).hexdigest() == BANK_SHA
    assert sha256(page).hexdigest() == PAGE_SHA
    assert page == bytes.fromhex('adad1e2020') + bytes(251)
    source = (R / 'src/rogue_dawn_audio_pages_v3.s').read_text()
    block = re.search(r'^RdaPage94:\s*(.*?)^\.segment', source, re.M | re.S)[1]
    authored = bytes(int(v, 16) for v in re.findall(r'\$([0-9a-fA-F]{2})\b', block))
    assert authored == page
    rows = list(page_rows(raw, bundle))
    owners = [q for q in rows if q['tag'] & 127 == 87 and q['high'] == 0xbf]
    assert owners == [dict(mode='lower', row=126, tag=0xd7, high=0xbf,
                          bank_table_file=515125)]
    # Source/current symbols bind the complete depot, rather than interpreting
    # a zero run as unused. This does not prove every indirect foreign reader.
    for i in range(15):
        name = 'RdaPage' + str(80 + i)
        assert location(bundle, name) == at(87, 0xb100 + i * 256)
    direct = [(0xa000 + i, int.from_bytes(bank[i+1:i+3], 'little'))
              for i in range(0x1100 - 2) if bank[i] in (0x20, 0x4c)
              and 0xbf00 <= int.from_bytes(bank[i+1:i+3], 'little') < 0xc000]
    return bundle, rows, dict(current_ROM_SHA256=B.PIN,
        bank87_SHA256=BANK_SHA, page_SHA256=PAGE_SHA,
        source_page='src/rogue_dawn_audio_pages_v3.s:RdaPage94',
        exact_source_bytes=256, all_current_Rogue_map_rows=len(rows),
        exact_consuming_rows=owners, local_prefix_literal_call_targets=direct,
        native87_prefix_owner='Tn movement/render/lifecycle plus BT cold router',
        depot_half_open=[0xb100, 0xc000],
        physical_page_file_half_open=[at(87, 0xbf00), at(88, 0xa000)],
        existing_virtual_mux_half_open=[0xc469, 0xc480],
        virtual_mux_semantics='bit7-clear table tag maps tag|80 then JMP BF00; DA uses B705',
        DMC_or_alternate_map_closure=False,
        ownership_scope='Source page, all 224 Rogue map rows and local literal targets only; indirect/DMC/current alternate-map closure remains required.')


def audio_fixture(raw):
    bundle, rows, bound = bindings(raw)
    # AND classifies a padded eight-byte prefix without changing C/V/DI or
    # using PHP/PLP (which normalize model P bit5). Both valid and arbitrary
    # model flags therefore match. Poison the entire proposed residual span.
    leaf = bytes.fromhex('a5e829f8d00aa4e8b915bfa0004c38c4a9004c38c4adad1e2020000000')
    assert len(leaf) == 29
    image = bytearray(raw)
    image[at(87, 0xbf00):at(88, 0xa000)] = leaf + bytes((0xaa,)) * 227
    image[515125] = 0x57
    return bytes(image), dict(bound, fixture_only=True, leaf_bytes=len(leaf),
        leaf_hex=leaf.hex(), potentially_repurposable_bytes=227,
        production_allocation=False, read_cost_qualified=False)


def call_reader(m, row, offset, flags):
    M.put(m, CurrentBank=190, CurrentBankC=225, NmiDisable=255)
    m.raw_page(1, 190)
    m.raw_page(2, 225)
    m[0xe8] = offset
    m[0xe9] = (0x80 + row['row'] % 32 if row['mode'] == 'lower'
                else 0xa0 + row['row'])
    m[0x23] = row['row'] // 32 if row['mode'] == 'lower' else 0
    B.W.clear_logs(m)
    c = M.NesMPU(memory=m, pc=0xc410)
    c.sp, c.p, c.a, c.x, c.y = 224, flags, 0x83, 0x69, 0x77
    c.stPushWord(0x5aff)
    for _ in range(200):
        if c.pc == 0x5b00:
            break
        assert m[c.pc], ('BRK', hex(c.pc), row, offset)
        c.step()
    else:
        raise AssertionError(('reader bound', row, offset, hex(c.pc)))
    assert c.sp == 224 and m.rawtags[1:3] == [190, 225]
    assert M.get(m, 'CurrentBank') == 190
    touched = sorted(set(a for a, value in m.writes
                         if not 0x100 <= a < 0x200 and a < 0x8000))
    return (c.a, c.x, c.y, c.p & 0xef, c.sp, m[0x7051], m[0xe8], m[0xe9],
            tuple(m.rawtags), tuple((a, m[a]) for a in touched)), c.processorCycles


def readers(raw):
    bundle, rows, bound = bindings(raw)
    image, info = audio_fixture(raw)
    pair = [M.fresh(dict(bundle, raw=r)) for r in (raw, image)]
    counts = Counter()
    costs = {}
    for row in rows:
        for offset in range(256):
            flags = (0x20, 0x21, 0x60, 0x65, 0x2c, 0xe9)[(row['row'] + offset) % 6]
            (a, ac), (z, zc) = [call_reader(m, row, offset, flags) for m in pair]
            assert a == z, (row, offset, a, z)
            group = 'virtualized_page' if row['mode'] == 'lower' and row['row'] == 126 else 'all_other_pages'
            counts[group] += 1
            lo, hi = costs.get(group, (zc-ac, zc-ac))
            costs[group] = [min(lo, zc-ac), max(hi, zc-ac)]
    # Input P is arbitrary, including C/V/D/I, not just the six campaign flags.
    row = next(q for q in rows if q['mode'] == 'lower' and q['row'] == 126)
    for flags in range(256):
        for offset in (0, 1, 4, 5, 127, 255):
            a, z = [call_reader(m, row, offset, flags)[0] for m in pair]
            assert a == z, (offset, flags, a, z)
    assert counts == dict(all_other_pages=57088, virtualized_page=256), counts
    assert costs['all_other_pages'] == [0, 0]
    return dict(info, read_cost_qualified=True, comparisons=sum(counts.values()),
        arbitrary_P_boundary_comparisons=1536, counts=counts,
        CPU_cycles_added_per_read=costs, logical_byte_AXYP_SP_maps_touched_RAM_equal=True,
        complete_interrupt_audio_foreign_qualification=False, production_allocation=False,
        output_files=0)


def auth_kernel(cookie, base=0x5800):
    """Unfunded timing kernel preserving exact current header-check outputs."""
    assert len(cookie) == 16
    out = bytearray(ABS(0xad, 0x7da1) + b'\x48\xa2\x03')
    loop = base + len(out)
    out += ABS(0x8e, 0x7da1) + ABS(0x8e, 0x5116)
    branches = []
    for i in range(15, -1, -1):
        out += ABS(0xad, 0xdfe0 + i) + bytes((0xc9, cookie[i], 0xd0, 0))
        branches.append((len(out)-1, i))
    out += b'\xa0\xff\xca\xe0\x01\xf0\x03' + ABS(0x4c, loop)
    out += b'\x38\x4c\x00\x00'
    done_operand = len(out) - 2
    jumps = []
    for branch, i in branches:
        displacement = len(out) - (branch + 1)
        assert -128 <= displacement < 128
        out[branch] = displacement & 255
        out += bytes((0xa0, i, 0x4c, 0, 0))
        jumps.append(len(out)-2)
    failure = base + len(out)
    out += b'\x18'
    done = base + len(out)
    out += b'\x68' + ABS(0x8d, 0x7da1) + ABS(0x8d, 0x5116) + b'\x60'
    for operand in jumps:
        out[operand:operand+2] = WORD(failure)
    out[done_operand:done_operand+2] = WORD(done)
    assert len(out) == 227
    return bytes(out)


def auth_estimate(raw):
    """Declared cold-derived direct CPU fixture; no mounted gameplay edits."""
    seed, opening = B.cold(raw, 0)
    cookie = bytes.fromhex('a72701f3691d419fd9ae7473840ce393')
    kernel = auth_kernel(cookie)
    pair = [clone(seed) for _ in range(2)]
    for m in pair:
        m.raw_page(1, 193)
        M.put(m, CurrentBank=193)
        m[8], m[9] = 0xea, 0xaf
        m[0x7da1] = 2
        m.raw_page(2, 2)
    for i, value in enumerate(kernel):
        pair[1][0x5800+i] = value
    def call(m, pc, flags):
        c = M.NesMPU(memory=m, pc=pc)
        c.sp, c.p, c.a, c.x, c.y = 224, flags, 0xaf, 2, 0x77
        c.stPushWord(0x5aff)
        for _ in range(1000):
            if c.pc == 0x5b00:
                break
            assert m[c.pc]
            c.step()
        else:
            raise AssertionError(('auth bound', hex(c.pc)))
        assert c.sp == 224
        return (c.a, c.x, c.y, c.p & 0xef, c.sp, tuple(m.rawtags),
                m[8], m[9], m[0x7da1]), c.processorCycles
    savings = set()
    for flags in range(256):
        a, z = [call(m, pc, flags) for m, pc in zip(pair, (0xaf27, 0x5800))]
        assert a[0] == z[0], (flags, a, z)
        savings.add(a[1]-z[1])
    assert len(savings) == 1
    poisoned = 0
    for bank in (2, 3):
        for byte in range(16):
            for m in pair:
                m.ram[bank][0x1fe0+byte] ^= 1
            for flags in (0x20, 0x21, 0x60, 0x65, 0x2c, 0xe9):
                a, z = [call(m, pc, flags) for m, pc in zip(pair, (0xaf27, 0x5800))]
                assert a[0] == z[0], (bank, byte, flags, a, z)
                poisoned += 1
            for m in pair:
                m.ram[bank][0x1fe0+byte] ^= 1
    saving = savings.pop()
    return dict(cold_menu=opening, declared_fixture_WRAM=0x5800,
        runtime_allocation_at_that_address=False, kernel_bytes=len(kernel),
        exact_auth_valid_flags=256, invalid_header_cases=poisoned,
        CPU_cycles_saved_per_valid_auth=saving,
        measured_checks_per_native_idle_Main=13.5,
        projected_auth_only_saving_per_Main=saving*13.5,
        gateway_mapping_cost_included=False, Main_or_native_cadence_qualified=False,
        resource_funding_and_gateway_unresolved=True, output_files=0)


def gateway_fixture(raw):
    """Unleased, in-memory native layout for a cost/admission request only."""
    bundle, rows, bound = bindings(raw)
    image, info = audio_fixture(raw)
    image = bytearray(image)
    # Preserve CoCheckHeaders' actual fixed entry. Its incoming Y is dead;
    # the worker saves old C via Y and returns A=oldC, as the old callee does.
    gateway = (ABS(0xac, 0x7da1) + ABS(0x20, 0xafd5) + ABS(0x20, 0xdf1d)
               + ABS(0x8d, 0x7da1) + ABS(0x8d, 0x5116) + b'\x60')
    assert len(gateway) == 16
    single = (ABS(0x8e, 0x7da1) + ABS(0x8e, 0x5116)
              + bytes.fromhex('b9e0dfd108d0058810f6b00118') + ABS(0x4c, 0xafd5))
    assert len(single) == 22
    old_headers = bytes.fromhex(
        'ada17d48a2038ea17d8e1651a00fb9e0dfd108d00a8810f6cae001d0e9b00118688da17d8d165160')
    assert len(old_headers) == 40
    assert raw[at(65, 0xaf27):at(65, 0xaf4f)] == old_headers
    image[at(65, 0xaf27):at(65, 0xaf4f)] = gateway + single + b'\xea\xea'
    # Source-owned duplicate SMC-offset table is rebound to its identical
    # existing generic table. It funds this exact five-byte mapper stub.
    assert raw[at(65, 0xafd5):at(65, 0xafda)] == raw[at(65, 0xaa61):at(65, 0xaa66)] == bytes.fromhex('626a6c6d79')
    assert [0xa000+i for i in range(8190)
            if raw[at(65, 0xa000)+i:at(65, 0xa000)+i+3] == bytes.fromhex('bcd5af')] == [0xae1d, 0xaec8]
    for pc in (0xae1d, 0xaec8):
        image[at(65, pc):at(65, pc)+3] = bytes.fromhex('bc61aa')
    image[at(65, 0xafd5):at(65, 0xafda)] = bytes.fromhex('a9d74c30af')

    base = 0xdf1d
    code = bytearray()
    labels, fixes = {}, []
    def mark(name): labels[name] = base + len(code)
    def emit(data): code.extend(data)
    def branch(op, target):
        emit(bytes((op, 0))); fixes.append((len(code)-1, target, True))
    def jump(target):
        emit(b'\x4c\x00\x00'); fixes.append((len(code)-2, target, False))
    emit(b'\x98\x48\xa5\x08\xc9\xea')
    branch(0xd0, 'GenericJump')
    emit(b'\xa5\x09\xc9\xaf')
    branch(0xf0, 'Fast')
    mark('GenericJump'); jump('Generic')
    mark('Fast')
    emit(ABS(0xad, 0x145) + b'\x48\xa2\x03')
    mark('MapA')
    emit(ABS(0x8e, 0x145) + ABS(0x8e, 0x5115) + b'\xa0\x0f')
    cookie = raw[at(65, 0xafea):at(65, 0xaffa)]
    assert cookie.hex() == 'a72701f3691d419fd9ae7473840ce393'
    for i in range(15, -1, -1):
        if i == 7:
            jump('SecondHalf')
            mark('Failure'); emit(b'\x18'); jump('RestoreA')
            mark('SecondHalf')
        emit(ABS(0xad, 0xbfe0+i) + bytes((0xc9, cookie[i])))
        branch(0xd0, 'Failure')
        emit(b'\x88')
    emit(b'\xca\xe0\x01')
    branch(0xf0, 'RestoreA'); jump('MapA')
    mark('RestoreA')
    emit(b'\x68' + ABS(0x8d, 0x145) + ABS(0x8d, 0x5115) + b'\x68\x60')
    mark('Generic'); emit(b'\xa2\x03')
    mark('GenericLoop'); emit(b'\xa0\x0f' + ABS(0x20, 0xaf37))
    branch(0x90, 'GenericDone')
    emit(b'\xca\xe0\x01'); branch(0xd0, 'GenericLoop')
    mark('GenericDone'); emit(b'\x68\x60')
    for operand, target, relative in fixes:
        if relative:
            delta = labels[target] - (base + operand + 1)
            assert -128 <= delta < 128, (target, delta)
            code[operand] = delta & 255
        else:
            code[operand:operand+2] = WORD(labels[target])
    assert len(code) <= 227
    start = at(87, 0xbf1d)
    image[start:start+len(code)] = code
    return bytes(image), dict(info, native65_old_header_bytes=40,
        native65_new_header_bytes=40, duplicate_SMC_table_bytes_rebound=5,
        native65_SMC_getter_PCs=[0xae1d, 0xaec8], gateway_PC=0xaf27,
        single_header_PC=0xaf37, common_MapC_PC=0xaf30,
        physical87_C_worker_PC=base, worker_bytes=len(code),
        residual_page_bytes=227-len(code), layout_labels=labels,
        code_or_allocation_qualified=False, fixture_only=True)


def gateway_cost(raw):
    """Actual emitted native gateway, direct declared ABI/cost fixtures only."""
    candidate, info = gateway_fixture(raw)
    seed, opening = B.cold(raw, 0)
    pair = [clone(seed), clone(seed)]
    pair[1].bundle = dict(pair[1].bundle, raw=candidate)
    for m in pair:
        m.raw_page(1, 193)
        M.put(m, CurrentBank=193)
        m[0x7da1] = 2
        m.raw_page(2, 2)
        m[0x5115], m[0x5116] = 193, 2
    def call(m, flags):
        c = M.NesMPU(memory=m, pc=0xaf27)
        c.sp, c.p, c.a, c.x, c.y = 224, flags, 0x83, 0x69, 0x77
        c.stPushWord(0x5aff)
        low = c.sp
        for _ in range(2000):
            if c.pc == 0x5b00:
                break
            low = min(low, c.sp)
            assert m[c.pc], ('gateway BRK', hex(c.pc), m.rawtags)
            c.step()
        else:
            raise AssertionError(('gateway bound', hex(c.pc)))
        return (c.a, c.x, c.y, c.p & 0xef, c.sp, tuple(m.rawtags),
                bytes(m[:0x100]), bytes(m[0x200:0x8000]),
                bytes(m[0x15a:0x17b]), bytes(m[0x101+c.sp:0x200])), c.processorCycles, low
    cases = []
    origin = at(65, 0xa000)
    for index in range(7):
        pc = raw[origin+0xbaf+index] + 256*raw[origin+0xbb7+index]
        cookie = raw[at(65, pc):at(65, pc)+16]
        for m in pair:
            m[8], m[9] = pc & 255, pc >> 8
            for bank in (2, 3):
                m.ram[bank][0x1fe0:0x1ff0] = cookie
        valid_costs = set()
        minimum = 255
        for flags in range(256):
            a, z = [call(m, flags) for m in pair]
            assert a[0] == z[0], ('valid', index, flags, a[0][:6], z[0][:6])
            valid_costs.add(z[1]-a[1]); minimum = min(minimum, z[2])
        assert len(valid_costs) == 1
        poison_costs = []
        for bank in (2, 3):
            for byte in range(16):
                for m in pair:
                    m.ram[bank][0x1fe0+byte] ^= 1
                for flags in (0x20, 0x21, 0x60, 0x65, 0x2c, 0xe9):
                    a, z = [call(m, flags) for m in pair]
                    assert a[0] == z[0], ('poison', index, bank, byte, flags, a[0][:6], z[0][:6])
                    poison_costs.append(z[1]-a[1]); minimum = min(minimum, z[2])
                for m in pair:
                    m.ram[bank][0x1fe0+byte] ^= 1
        cases.append(dict(cookie_index=index, cookie_PC=pc, Bub_fast_path=pc==0xafea,
            valid_P_cases=256, invalid_header_cases=len(poison_costs),
            valid_CPU_delta=valid_costs.pop(), invalid_CPU_delta=[min(poison_costs), max(poison_costs)],
            minimum_foreground_SP=minimum))
    return dict(info, direct_ABI_cost_cases=cases, output_files=0,
        actual_cold_prefix=opening, source_health_weapon_ability_fixtures=False,
        scope='Declared header bytes/pointers only after real cold/menu. Exact emitted native maps and all native RAM/SMC/live stack/AXYP/SP, not Main/IRQ/cold or ownership qualification.')


def pair_budget(raw):
    """Actual IdleLoop catch-up, induced by one real busy NMI; no flag seed."""
    import bub_empty_loops_1113 as Empty
    result = []
    for name, image in (('public7ef', raw), ('private_a77', Empty.proposal(raw)[0])):
        m, opening = B.cold(image, 0)
        b = m.bundle
        idle, main = address(b, 'IdleLoop'), address(b, 'GameLoop')
        source = 0xa152
        assert bytes(m.ram[3][source-0xa000:source-0xa000+8]) == bytes.fromhex('ee1fc0a227a02bde')
        rows = []
        def vector(c, kind):
            start = c.processorCycles
            saved = (c.pc, c.sp, c.a, c.x, c.y, c.p & 0xef, tuple(m.rawtags))
            c.nmi() if kind == 'NMI' else c.irq()
            for _ in range(200000):
                if (c.pc, c.sp) == saved[:2]:
                    break
                assert m[c.pc], (kind, hex(c.pc))
                c.step()
            else:
                raise AssertionError((kind, 'return bound'))
            assert (c.pc, c.sp, c.a, c.x, c.y, c.p & 0xef, tuple(m.rawtags)) == saved
            return c.processorCycles-start
        for epoch in range(8):
            m.controller_pad = 0
            # Same real regular-NMI completion used by the current CPU harness.
            M.put(m, NmiDisable=0)
            n = M.NesMPU(memory=m, pc=0x5b00)
            n.sp, n.p = 224, 0x31
            regular = vector(n, 'NMI')
            # A genuine native mapper IRQ cost in the same settled scene.
            m[0x5204] = 0x80
            irq = vector(n, 'IRQ')
            c = M.NesMPU(memory=m, pc=idle)
            c.sp, c.p = 255, 0x31
            c.stPushWord(0xe33b)
            pending = None
            completed = []
            injected = False
            busy = 0
            for _ in range(500000):
                if c.processorCycles and (c.pc, c.sp) == (idle, 253):
                    break
                if c.pc == main:
                    assert pending is None
                    sp = c.sp
                    ret = (m[0x100+sp+1] + 256*m[0x100+sp+2] + 1) & 65535
                    pending = dict(return_PC=ret, start=c.processorCycles,
                                   auth=0, generic_transports=0, clocks=0)
                if pending and (c.pc, c.sp) == (pending['return_PC'], 252):
                    completed.append(dict(pending, CPU=c.processorCycles-pending['start']))
                    pending = None
                bank = m.rawtags[(c.pc-0x8000)//8192] if c.pc >= 0x8000 else -1
                if pending:
                    pending['auth'] += (bank, c.pc) == (193, 0xaee2)
                    pending['generic_transports'] += (bank, c.pc) == (193, 0xaaf7)
                    pending['clocks'] += (bank, c.pc) == (3, source)
                if not injected and (bank, c.pc) == (3, source):
                    assert pending and pending['return_PC'] == 0x82be
                    assert M.get(m, 'NmiDisable') == 255
                    busy = vector(c, 'NMI')
                    injected = True
                assert m[c.pc], ('Main BRK', hex(c.pc), m.rawtags)
                c.step()
            else:
                raise AssertionError(('Idle pair bound', hex(c.pc)))
            assert injected and [q['return_PC'] for q in completed] == [0x82be, 0x82d0]
            assert [q['clocks'] for q in completed] == [1, 1]
            assert not B.state(m)['actors'] and B.state(m)['x'] == 40
            rows.append(dict(normal_CPU_excluding_busy_NMI=completed[0]['CPU']-busy,
                             catchup_CPU=completed[1]['CPU'], regular_NMI_CPU=regular,
                             busy_NMI_CPU=busy, IRQ_CPU=irq,
                             OAM_DMA_stall_not_modeled=513,
                             normal_auth=completed[0]['auth'], catchup_auth=completed[1]['auth'],
                             normal_transports=completed[0]['generic_transports'],
                             catchup_transports=completed[1]['generic_transports']))
        result.append(dict(name=name, opening=opening, actual_pairs=len(rows), rows=rows,
                           no_runtime_gameplay_flag_or_actor_seeds=True))
    return dict(passed=True, source_only=True, campaigns=result,
        NTSC_CPU_cycles_per_frame=1789773/60.0988,
        policy='A real busy NMI changes NmiSkipped; the unmodified IdleLoop calls TerrainCatchupPending, runs one actual non-draw Main, clears its draw skip, then waits for regular NMI.',
        physical_phase_alignment_not_modeled=True, output_files=0)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--readers', action='store_true')
    p.add_argument('--auth-estimate', action='store_true')
    p.add_argument('--pair-budget', action='store_true')
    p.add_argument('--gateway-cost', action='store_true')
    a = p.parse_args()
    raw = B.ROM.read_bytes()
    result = (readers(raw) if a.readers else auth_estimate(raw) if a.auth_estimate
              else pair_budget(raw) if a.pair_budget else gateway_cost(raw)
              if a.gateway_cost else bindings(raw)[2])
    print(json.dumps(result, separators=(',', ':')))
