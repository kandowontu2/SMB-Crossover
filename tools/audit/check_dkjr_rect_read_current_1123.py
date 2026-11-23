"""Bounded memory-only current DK rectangle equivalence and CPU costs.

Normal opening inputs qualify movement separately from isolated ABI mounts.
IRQ and busy-NMI tests compare matched interrupted ordinary continuations.
"""
import argparse
from collections import Counter
import json
from pathlib import Path

import compose_dkjr_rect_read_current_1123 as C
import check_dkjr_sonic_dispatch_1123 as Q
from check_mini_funded_actor_1108_v3 import registers, live_stack, slim_fork

P, N, W, B = C.Profile, Q.N, Q.W, Q.B


def point(cpu):
    return P.point(cpu.memory, cpu.pc)


def finish(c, stop, watch=None):
    for _ in range(300000):
        if (c.pc, c.sp) == stop:
            return
        if watch:
            watch(c)
        assert c.memory[c.pc], ('Real instruction BRK', point(c))
        c.step()
    raise AssertionError(('Bounded instruction call', point(c), stop))


def state(m):
    return dict(x=B.position(m), y=N.get(m, 'Player_Y_Position'), source=m.ram[2][0x6b],
        prior=m.ram[2][0x6c], facing=m.ram[2][0x6d], direction=m.ram[2][0x54],
        held=m.ram[2][0x14], sampled=m.ram[2][0x15], lives=N.get(m, 'NumberofLives'),
        native=N.get(m, 'Player_State'), age=m.ram[2][0x7e], fraction=m.ram[2][0x7f])


def compare(a, b, raw, image, old, new, normalize_carrier=None):
    for lo, hi in ((0, 0x15a), (0x1fd, 0x800), (0x5c00, 0x8000)):
        assert bytes(a[lo:hi]) == bytes(b[lo:hi]), ('Full native gameplay', hex(lo),
            [hex(i) for i in range(lo, hi) if a[i] != b[i]][:12])
    assert a.rawtags == b.rawtags and a.chr_latches == b.chr_latches
    assert bytes(a[0x15a:0x17b]) == bytes(b[0x15a:0x17b]), 'All live mutable farcall operands'
    hardware = lambda m: [(at,value) for at,value in m.writes if 0x2000 <= at < 0x6000]
    assert hardware(a) == hardware(b), 'Ordered hardware/extended-state writes'
    assert a.vram == b.vram and a.ppuctrl == b.ppuctrl
    assert (a.ppu_addr, a.toggle, a.buffer, a.upper, a.lastset, a.protection) == (
        b.ppu_addr, b.toggle, b.buffer, b.upper, b.lastset, b.protection)
    rows = [list(map(bytearray, m.ram)) for m in (a, b)]
    cells = [p['symbols']['RectReadCell']&8191 for p in (old, new)]
    assert bytes(a.ram[3][cells[0]+1:cells[0]+3]) == bytes(b.ram[3][cells[1]+1:cells[1]+3]), 'Same latest descriptor pointer'
    for index, (m, program, rom) in enumerate(zip((a, b), (old, new), (raw, image), strict=True)):
        begin = C.Head.RECT_START&8191
        expected = program['images']['RECT']
        for i, value in enumerate(expected):
            if begin+i not in (cells[index]+1, cells[index]+2):
                assert m.ram[3][begin+i] == value, ('Immutable private code', index, hex(begin+i))
        rows[index][3][begin:begin+len(expected)] = bytes(len(expected))
        cookie = rom[C.Head.Base.COOKIE_AT:C.Head.Base.COOKIE_AT+16]
        for bank in (2, 3):
            assert bytes(m.ram[bank][0x1fe0:0x1ff0]) == cookie
            rows[index][bank][0x1fe0:0x1ff0] = bytes(16)
    if normalize_carrier:
        normalize_carrier(rows)
    assert rows[0] == rows[1], ('All remaining WRAM gameplay',
        [(bank, hex(i)) for bank in range(4) for i,(a,b) in enumerate(zip(rows[0][bank],rows[1][bank])) if a != b][:16])


class Trace:
    def __init__(self, program, capture=False):
        self.program = program
        self.calls = Counter()
        self.captures = []
        self.entry = None
        self.end = None
        self.capture = capture

    def run(self, c, stop):
        names = {pc:name for name,pc in self.program['symbols'].items()
                 if name in ('DkRectCommon', 'RectRead', 'RectReadCell')}
        seen = {}
        def observe(q):
            tag, pc = point(q)
            if tag == 3 and pc in names:
                self.calls[names[pc]] += 1
                if self.entry is None and pc == C.Head.RECT_START:
                    self.entry = Q.clone(q)
                    self.entry.memory.combined_terminal = stop
            if self.capture and tag == 3 and C.Head.RECT_START <= pc < self.program['symbols']['DkAcceptHead']:
                key = pc, q.p&5
                if key not in seen:
                    seen[key] = len(self.captures)
                    assert len(self.captures) < 160
                    z = Q.clone(q)
                    z.memory.combined_terminal = stop
                    self.captures.append(z)
                elif q.sp < self.captures[seen[key]].sp:
                    # Keep the deepest actually reached stack for this PC/C/I
                    # contract rather than a clone per repeated list byte.
                    z = Q.clone(q)
                    z.memory.combined_terminal = stop
                    self.captures[seen[key]] = z
        finish(c, stop, observe)
        self.end = Q.clone(c)


def rebound(original, image):
    c = Q.clone(original)
    old = c.memory.bundle['raw']
    c.memory.bundle = dict(c.memory.bundle, raw=image)
    # This fixture starts at the same immutable external RECT entry. Replace
    # only the physically already-loaded source program and its real cookie.
    # The ordinary route test above instead lets the cold loader copy them.
    for at,data in C.chunks(C.Head.RECT_START, C.program(P.Old.ROM.read_bytes())[1]['images']['RECT']):
        offset = C.Head.RECT_START&8191
        c.memory.ram[3][offset:offset+len(data)] = data
    cookie = image[C.Head.Base.COOKIE_AT:C.Head.Base.COOKIE_AT+16]
    for bank in (2,3):
        c.memory.ram[bank][0x1fe0:0x1ff0] = cookie
    for window, tag in enumerate(tuple(c.memory.rawtags)):
        if tag&128:
            c.memory.raw_page(window, tag)
    W.clear_logs(c.memory)
    return c


def interrupts(control, cuts, raw, image, old, new, maximum):
    total = Counter()
    def interrupted(c, kind):
        before = registers(c), live_stack(c), tuple(c.memory.rawtags)
        end = c.pc, c.sp
        if kind == 'IRQ':
            c.p &= ~4
            before = registers(c), live_stack(c), tuple(c.memory.rawtags)
            c.irq()
        else:
            c.nmi()
        finish(c, end)
        assert (registers(c), live_stack(c), tuple(c.memory.rawtags)) == before, ('ISR transparent CPU/stack/maps', kind)
        return c
    selected = cuts if maximum is None else cuts[:maximum]
    for index, cut in enumerate(selected):
        for kind in ('IRQ', 'busy-NMI'):
            a, b = Q.clone(control), Q.clone(cut)
            # Both sides get the same actual native ISR and its legitimate
            # audio/zero-page side effects before their ordinary continuation.
            if kind == 'busy-NMI':
                N.put(a.memory, NmiDisable=1)
                N.put(b.memory, NmiDisable=1)
            interrupted(a, kind)
            interrupted(b, kind)
            finish(a, a.memory.combined_terminal)
            finish(b, b.memory.combined_terminal)
            assert registers(a,0xef) == registers(b,0xef) and live_stack(a) == live_stack(b)
            compare(a.memory, b.memory, raw, image, old, new)
            total[kind] += 1
    return dict(total)


def units(entry, raw, image, old, new):
    count, savings = 0, Counter()
    # Explicit component mounts, not normal-play acquisitions. RAM uses the
    # actual bounded C800 geometry-list domain; ROM uses immutable body data.
    for mode, pointer in ((0,0xc800),(1,0xc800),(2,0xc800),(0,0xb019),(1,0xb019)):
        for status in range(0x20,0x100):
            if not status&0x20:
                continue
            for x,y in ((0,0),(255,255)):
                a = Q.clone(entry)
                b = rebound(entry,image)
                for c in (a,b):
                    c.a,c.x,c.y,c.p = mode,x,y,status
                    c.memory.ram[2][2:4] = pointer.to_bytes(2,'little')
                    c.memory.ram[2][0x800:0x809] = bytes((0,176,255,208,255,0,0,0,0))
                    W.clear_logs(c.memory)
                stop = ((a.memory[0x101+a.sp]+256*a.memory[0x102+a.sp]+1)&65535,a.sp+2)
                finish(a,stop)
                finish(b,stop)
                assert registers(a,0xef) == registers(b,0xef) and live_stack(a) == live_stack(b)
                compare(a.memory,b.memory,raw,image,old,new)
                savings[a.processorCycles-b.processorCycles] += 1
                count += 1
    return dict(cases=count, all_valid_statuses=True, A_modes=[0,1,2], XY_extremes=True,
        descriptor_domains=['C800 geometry list','immutable B019 body'], saved_cycles=dict(savings))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--interrupt-limit', type=int)
    args = ap.parse_args()
    raw = P.Old.ROM.read_bytes()
    image, proof = C.compose(raw)
    old, new, _ = C.program(raw)
    pair = [P.Old.boot(r) for r in (raw, image)]
    compare(*pair, raw, image, old, new)
    phases, entry, cuts = {}, None, []
    schedule = (('standing',0,16), ('Right',1,24), ('Left',2,16), ('release',0,4),
                ('neutral-A',128,1), ('steer-Right-in-air',1,16), ('landing',0,32),
                ('fresh-Right-A',129,1), ('fresh-landing',1,56))
    for phase, pad, count in schedule:
        costs = [0,0]
        starts = [state(m) for m in pair]
        calls = [Counter(),Counter()]
        for tick in range(count):
            traces = [Trace(old), Trace(new, capture=(phase=='Right' and tick==10))]
            for index,(m,tr) in enumerate(zip(pair,traces,strict=True)):
                assert not any(B.flags(m)) and N.get(m,'NumberofLives')==2
                costs[index] += B.main_step(m,pad,tr)[0]
                calls[index].update(tr.calls)
            assert registers(traces[0].end,0xef) == registers(traces[1].end,0xef)
            assert live_stack(traces[0].end) == live_stack(traces[1].end)
            compare(*pair, raw, image, old, new)
            if traces[1].captures:
                assert entry is None
                entry, cuts = traces[0].entry, traces[1].captures
        phases[phase] = dict(returns=count, cycles=costs, saved_per_Main=(costs[0]-costs[1])/count,
            before=starts[0], after=state(pair[0]), calls=list(map(dict,calls)))
        print('DK RECT PHASE '+json.dumps(dict(phase=phase, **phases[phase]),separators=(',',':')), flush=True)
    assert entry and cuts
    assert phases['neutral-A']['after']['source'] == 3
    assert phases['steer-Right-in-air']['after']['x'] == phases['neutral-A']['after']['x']
    assert phases['steer-Right-in-air']['after']['direction'] == 0
    assert phases['fresh-Right-A']['after']['direction'] == 4
    assert phases['fresh-landing']['after']['source'] == 1 and phases['fresh-landing']['after']['native'] == 0
    result = dict(passed=True, composition=proof, phases=phases,
        component_ABI=units(entry,raw,image,old,new),
        matched_interrupts=interrupts(entry,cuts,raw,image,old,new,args.interrupt_limit),
        captured_reached_cuts=len(cuts), source_CPU_only=True, Mesen_run=False, outputs=0,
        exact_native_WRAM_and_mapper_PPU_comparisons=True, physical_cadence_qualified=False,
        checker_SHA256=C.H(Path(__file__).read_bytes()))
    canonical = json.dumps(result,sort_keys=True,separators=(',',':'))
    print('DK RECT RECEIPT '+json.dumps(dict(result=result,receipt_SHA256=C.H(canonical.encode())),separators=(',',':')),flush=True)


if __name__ == '__main__':
    main()
