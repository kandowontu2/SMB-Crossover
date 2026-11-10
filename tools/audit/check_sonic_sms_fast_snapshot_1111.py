"""Build and verify the exact raw43 rollback optimization in memory."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import check_sonic_native_effects_vectors_1110 as Vectors
import check_sonic_ring_draw_cadence_1110 as Release
import deliver_dkjr_second_gap_1111 as DK
import profile_sonic_snapshot_leaf_1110 as Leaf
from sonic_sms_compact_cold_worker_1110 import assemble


RING, SOURCE = Release.RING, Path(__file__).resolve().parents[1] / 'reference/sonic_sms_fast_snapshot_1111.s'
LIVE, N = RING.Live, RING.N
PIN = '8c1ebb1bfbe21499461c5fd65ea75b784460ac2cb81a712a9db9941aa7cec711'
STOP = (0x5b00, 224)


def changed(a, b):
    return {i for i, (x, y) in enumerate(zip(a, b, strict=True)) if x != y}


def proposal(raw, previous):
    """Apply the two private code edits and the authenticated cookie."""
    assert sha256(raw).hexdigest() == DK.PIN == Leaf.SUCCESSOR
    old = previous['packet']
    assert old['cookie'].hex() == 'a72b018c2e04635376b3ef263b330c8f'
    assert LIVE.COOKIE == 16 + 126*8192 + 0x8d8 and raw[:LIVE.CHR].count(old['cookie']) == 1
    assert old['code_pages'][-1] == 330 and old['ring_feedback_page'] == 334
    assert old['frame']['symbols']['SaveFrame'] == Leaf.ENTRY
    assert old['frame']['symbols']['SaveSMC'] - 2 == Leaf.CONTINUE
    body = assemble(SOURCE.read_text(encoding='ascii'), {'SNAPSHOT': (Leaf.PROBE, 33)})['images']['SNAPSHOT']
    assert body == Leaf.four_lanes()
    kernel, feedback = (bytearray(old[k]) for k in ('kernel', 'ring_feedback'))
    entry = Leaf.ENTRY - 0xa000
    origin = Leaf.PROBE - 0xd800
    assert kernel[entry:entry+len(Leaf.PREIMAGE)] == Leaf.PREIMAGE
    assert feedback[origin:origin+len(body)] == b'\xff'*len(body)
    kernel[entry:entry+3] = b'\x4c' + Leaf.PROBE.to_bytes(2, 'little')
    feedback[origin:origin+len(body)] = body
    payload = lambda k, f: k + old['metadata'] + old['ring_extension'] + f + old['ring_art']
    assert old['cookie'][3:] == sha256(payload(old['kernel'], old['ring_feedback'])).digest()[:13]
    cookie = old['cookie'][:3] + sha256(payload(kernel, feedback)).digest()[:13]

    image = bytearray(raw)
    patch_spans = ((LIVE.CHR + 330*1024 + Leaf.ENTRY - 0xbc00,
                    old['kernel'][entry:entry+3], kernel[entry:entry+3]),
                   (LIVE.CHR + 334*1024 + origin,
                    old['ring_feedback'][origin:origin+len(body)], body),
                   (LIVE.COOKIE, old['cookie'], cookie))
    allowed = set()
    for at, before, after in patch_spans:
        assert len(before) == len(after) and raw[at:at+len(before)] == before
        image[at:at+len(after)] = after
        allowed.update(range(at, at+len(before)))
    differences = changed(raw, image)
    assert differences <= allowed
    assert len(differences) == 49 and sha256(image).hexdigest() == PIN
    # The latest Jay stock-flight draft owns physical 218, 331 and resident
    # PRG 65/94 spans. Existing separate Jay transport 332 stays exact too.
    assert all(raw[LIVE.CHR+n*1024:LIVE.CHR+(n+1)*1024] == image[LIVE.CHR+n*1024:LIVE.CHR+(n+1)*1024]
               for n in (218, 224, 328, 329, 331, 332, 333, 881, 883, 960, 961))
    assert all(raw[16+n*8192:16+(n+1)*8192] == image[16+n*8192:16+(n+1)*8192]
               for n in (65, 94))
    q = dict(old, kernel=bytes(kernel), ring_feedback=bytes(feedback), cookie=cookie)
    p = dict(previous, packet=q)
    return bytes(image), p, dict(parent_SHA256=DK.PIN, image_SHA256=sha256(image).hexdigest(), cookie=cookie.hex(),
        changes=len(differences), spans=[dict(offset=at, length=len(data)) for at, _, data in patch_spans],
        source_SHA256=sha256(SOURCE.read_bytes()).hexdigest())


def from_installed(raw):
    """Rebuild the same patch directly from the pinned cartridge pages."""
    def page(number):
        at = LIVE.CHR+number*1024
        return raw[at:at+1024]

    pages = (*range(321,328),330)
    old = dict(cookie=raw[LIVE.COOKIE:LIVE.COOKIE+16], code_pages=pages, ring_feedback_page=334,
        frame=dict(symbols=dict(SaveFrame=Leaf.ENTRY, SaveSMC=Leaf.CONTINUE+2)),
        kernel=b''.join(map(page,pages)), metadata=page(328), ring_extension=page(333),
        ring_feedback=page(334), ring_art=page(224))
    image, _, receipt = proposal(raw, dict(packet=old))
    return image, receipt


def reconstruct():
    installed = Leaf.NIGHTLY.read_bytes()
    assert sha256(installed).hexdigest() == DK.PIN
    before = Release.Rebase.parent_bytes()
    sonic, common, old, summary = Release.proposal(before)
    assert summary['image_SHA256'] == Leaf.PIN
    raw = DK.merge(before, sonic)
    assert installed == raw
    image, new, receipt = proposal(raw, old)
    assert (image, receipt) == from_installed(raw)
    dk_changes = changed(sonic, raw)
    assert len(dk_changes) == 248 and dk_changes.isdisjoint(changed(raw, image))
    receipt['retained_DK_changes'] = len(dk_changes)
    return raw, image, common, old, new, receipt


def new_bus(image):
    return LIVE.O.blank(LIVE.C.Current.W.bundle(image))


def cold_and_headers(raw, image, common, old, new):
    result = RING.cold(raw, image, common, new)
    program = common['new']
    faults = [(3, Leaf.ENTRY-0xa000+i) for i in range(3)]
    faults += [(2, Leaf.PROBE-0xc000+i) for i in (0, 1, 2, 5, 16, 25, 28, 32)]
    for bank, at in faults:
        m = new_bus(image)
        m.corrupt_at = (bank, at)
        LIVE.C.cold(m, 43, program, expect_success=False)
        assert LIVE.O.headers(m) == (bytes(16),)*2
    m = new_bus(image)
    LIVE.C.cold(m, 43, program)
    assert LIVE.O.headers(m) == (new['packet']['cookie'],)*2
    assert [(b,v) for b,a,v in m.ram_writes if a==0x1fe0][-2:] == [(3,0xa7),(2,0xa7)]
    poison = [(bank, i) for bank in (2,3) for i in range(16)] + [(2,None),(3,None)]
    for bank, i in poison:
        bad = LIVE.Eighth.S.slim_fork(m)
        if i is None:
            bad.ram[bank][0x1fe0:0x1ff0] = old['packet']['cookie']
        else:
            bad.ram[bank][0x1fe0+i] ^= 1
        calls = []
        before = bytes(bad.ram[2][0x200:0x2b8])

        def observe(mem,cpu):
            if cpu.pc in (Leaf.ENTRY, Leaf.PROBE) and mem.rawtags[2] == 2:
                calls.append(cpu.pc)

        assert not LIVE.Public.public(bad, 0, observe=observe).p & 1
        assert not calls and bytes(bad.ram[2][0x200:0x2b8]) == before
    return dict(result, targeted_write_readback_faults=len(faults), header_rejections=len(poison),
                headers_published_in_bank_order=True)


def scene(image, p, common):
    t = LIVE.Public.A.T
    m = t.install(LIVE.C.Current.W.bundle(image), p, common)
    t.S.scene(m, 40, 176)
    t.S.set_native(m, OperMode=1, OperMode_Task=3, WorldNumber=0, LevelNumber=0, AreaAddrsLOffset=5,
                   DisableScreenFlag=0, Mirror_PPUMASK=30, NmiDisable=255)
    return m


def normalize(m):
    ram = [bytearray(bank) for bank in m.ram]
    ram[2][Leaf.PROBE-0xc000:Leaf.PROBE-0xc000+33] = bytes(33)
    ram[3][Leaf.ENTRY-0xa000:Leaf.ENTRY-0xa000+3] = bytes(3)
    for bank in (2,3):
        ram[bank][0x1fe0:0x1ff0] = bytes(16)
    return (tuple(bytes(bank) for bank in ram), tuple(m.rawtags), bytes(m[0:0x100]),
            bytes(m[0x15a:0x17b]), bytes(m[0x200:0x800]), m.ppu_log)


def runtime(raw, image, common, old, new):
    left, right = scene(raw, old, common), scene(image, new, common)
    t = LIVE.Public.A.T
    ages, counts = Counter(), Counter()
    for epoch in range(52):
        for m in (left,right):
            t.S.set_native(m, FrameCounter=epoch, SavedJoypadBits=0 if epoch < 16 else 129 if epoch == 18 else 1)
            if epoch in (27,28):
                N.put(m, ColumnSets=0)
            if epoch == 29:
                N.put(m, ColumnSets=255)
        seen = []

        def observe(m,c):
            if c.pc == Leaf.PROBE and m.rawtags[2] == 2:
                seen.append(c.pc)

        a, b = LIVE.Public.public(left, 0), LIVE.Public.public(right, 0, observe=observe)
        assert (a.a,a.x,a.y,a.p,a.sp) == (b.a,b.x,b.y,b.p,b.sp) and a.p & 1
        assert normalize(left) == normalize(right), epoch
        assert a.processorCycles-b.processorCycles == 1027 and len(seen) == 1, (epoch, a.processorCycles,b.processorCycles,seen)
        assert bytes(right.ram[2][0x200:0x2b8]) == bytes(left.ram[2][0x200:0x2b8])
        status = right.ram[2][0x116]
        counts['failed_and_restored' if status else 'committed'] += 1
        ages[status] += 1
    assert counts['failed_and_restored'] and counts['committed']
    return dict(epochs=52, cycles_saved_per_epoch=1027, outcomes=dict(counts), statuses=dict(ages))


def vectors(image, common, new):
    irq = LIVE.Public.L
    seed = scene(image, new, common)
    trace, stats = set(), Counter()
    irq.DEEPEST = None
    irq.PATHS.clear()

    def foreground(m,c):
        return (irq.regs(c), bytes(m[3:11]), bytes(m[0x15a:0x17b]), bytes(m[0x101+c.sp:0x200]),
                bytes(m[0x200:0x800]), tuple(bytes(b) for b in m.ram), tuple(m.rawtags))

    def observe(mem,cpu):
        pc = cpu.pc
        if mem.rawtags[1] != 3 or mem.rawtags[2] != 2:
            return
        if Leaf.PROBE <= pc < Leaf.PROBE+33:
            if pc != Leaf.PROBE and cpu.x not in (44,22,0,255):
                return
        elif pc not in (Leaf.ENTRY, Leaf.CONTINUE, Leaf.CONTINUE+2, Leaf.CONTINUE+5):
            return
        key = pc,cpu.x
        if key in trace:
            return
        trace.add(key)
        uninterrupted, initial = Vectors.clone(mem,cpu)
        irq.finish(uninterrupted, initial, STOP)
        for kind in ('NMI','IRQ'):
            q,d = Vectors.clone(mem,cpu)
            expected = foreground(q,d)
            assert irq.isr(q,d,kind,STOP) == 'returned'
            assert foreground(q,d) == expected, (kind, key, 'foreground changed')
            irq.finish(q,d,STOP)
            assert foreground(q,d) == foreground(uninterrupted,initial), (kind,key,'continuation changed')
            stats[kind] += 1

    with patch.object(irq,'regs',side_effect=lambda c:(c.pc,c.a,c.x,c.y,c.p&0xef,c.sp)), \
            patch.object(irq,'clone',side_effect=Vectors.clone):
        assert LIVE.Public.public(seed, 0, observe=observe).p & 1
        assert irq.DEEPEST is not None
        mem,cpu,entry,stop = irq.DEEPEST
        q,d = Vectors.clone(mem,cpu)
        expected = foreground(q,d)
        assert irq.isr(q,d,'IRQ') == 'returned' and foreground(q,d) == expected
        control,c = Vectors.clone(mem,cpu)
        for target in ((entry[0],entry[-1]),stop):
            irq.finish(control,c,target)
            irq.finish(q,d,target)
            assert foreground(control,c) == foreground(q,d)
    assert stats['NMI'] == stats['IRQ'] >= 35
    return dict(cuts=dict(stats), actual_handlers=dict(irq.PATHS), nested_IRQ=1, deepest_parent_SP=cpu.sp,
                selected_X_iterations=[44,22,0])


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--part', choices=('all','packet','cold','runtime','vectors','natural'), default='all')
    args = cli.parse_args()
    raw, image, common, old, new, receipt = reconstruct()
    print(json.dumps(dict(event='packet', **receipt), sort_keys=True), flush=True)
    if args.part in ('all','cold'):
        print(json.dumps(dict(event='cold', **cold_and_headers(raw,image,common,old,new)), sort_keys=True), flush=True)
    if args.part in ('all','runtime'):
        print(json.dumps(dict(event='runtime', **runtime(raw,image,common,old,new)), sort_keys=True), flush=True)
    if args.part in ('all','vectors'):
        print(json.dumps(dict(event='vectors', **vectors(image,common,new)), sort_keys=True), flush=True)
    if args.part in ('all','natural'):
        print(json.dumps(dict(event='natural', **RING.natural(image,new)), sort_keys=True), flush=True)
    print(json.dumps(dict(passed=True, part=args.part, source_only=True, output_files=0)), flush=True)


if __name__ == '__main__':
    main()
