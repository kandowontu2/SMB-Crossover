"""Reassemble the original Jay motion/contact slices and replay native donor terrain."""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys

import trace_jay_silius_donor_1110 as Donor

ROOT = Donor.ROOT
SOURCE = ROOT / 'tools/reference/jay_silius_original_motion_1110.s'
DONOR_CHECKER_PIN = '20d070792e60aa6fb564adcef2525da705ad2a9f58506067615cbcefd66d3ede'
RECEIPT_PIN = '926a1f5691960335915043009e5f7a2e5c81c63fe5550ae9d2b11ae171bb3ae1'
# Segment, original 16 KiB bank and half-open interval, fixture CPU address.
# Identical low bytes preserve every relative branch's page timing.
RANGES = (
    ('POSITION', 6, 0x81ea, 0x8304, 0x61ea),
    ('PROJECTION', 7, 0xcd88, 0xce18, 0x6388),
    ('INTEGRATE_ENTRY', 7, 0xe1a4, 0xe1aa, 0x64a4),
    ('INTEGRATOR', 7, 0xe20e, 0xe247, 0x650e),
    ('CONTACT', 7, 0xce4d, 0xcf07, 0x664d),
    ('PROBE', 7, 0xcf07, 0xd002, 0x6707),
    ('TILE_READ', 7, 0xd002, 0xd03e, 0x6802),
    ('PROBE_INDEX', 7, 0xd03e, 0xd042, 0x683e),
    ('PLAYER_PROBES', 7, 0xd058, 0xd08f, 0x6858),
)
SCENARIOS = (
    ('idle', [0]*8), ('right', [128]*40), ('left_reverse_release', [128]*12+[64]*18+[0]*8),
    ('jump_tap', [1]+[0]*35), ('jump_hold', [1]*14+[0]*36), ('crouch', [32]*12+[0]*12),
    ('stock_fire', [2]*8+[0]*3+[2]*8+[0]*4), ('jump_fire', [129]*6+[131]*14+[128]*10),
)


def source_images(raw):
    sys.path.insert(0, str(ROOT / 'tools/reference'))
    from sonic_sms_compact_cold_worker_1110 import assemble

    source = SOURCE.read_text()
    original = assemble(source, {name:(lo, hi-lo) for name, _, lo, hi, _ in RANGES})
    fixture = assemble(source, {name:(new, hi-lo) for name, _, lo, hi, new in RANGES})
    code_only = assemble(source, {
        name:(lo if name in ('PROBE_INDEX','PLAYER_PROBES') else new, hi-lo)
        for name, _, lo, hi, new in RANGES})
    moves, exact_moves, regions = [], [], []
    for name, bank, lo, hi, new in RANGES:
        offset = 16 + bank * 0x4000 + (lo & 0x3fff)
        before, after = original['images'][name], fixture['images'][name]
        assert before == raw[offset:offset+hi-lo] and len(after) == hi-lo, name
        assert lo & 255 == new & 255
        moves.append((new, after))
        if name not in ('PROBE_INDEX','PLAYER_PROBES'):
            exact_moves.append((new, code_only['images'][name]))
        regions.append(dict(segment=name, bank=bank, CPU_half_open=[hex(lo), hex(hi)],
            offset=offset, bytes=len(before), donor_SHA256=sha256(before).hexdigest(),
            relocated_operand_bytes=[hex(lo+i) for i,(a,b) in enumerate(zip(before,after,strict=True)) if a!=b]))
    assert sum(row['bytes'] for row in regions) == 1045
    return moves, exact_moves, regions


def return_pc(cpu):
    ram = cpu.memory.ram
    return (ram[0x100+((cpu.sp+1)&255)] | ram[0x100+((cpu.sp+2)&255)] << 8) + 1


def machine_state(cpu):
    bus = cpu.memory
    live_ram = bus.ram[:0x100] + bus.ram[0x101+cpu.sp:]
    ppu = (bus.ppu_ctrl, bus.ppu_mask, bus.ppu_address, bus.ppu_buffer, bus.ppu_latch, bus.oam_address)
    mapper = (bus.ctrl, bus.prg_reg, bus.chr0, bus.chr1, bus.shift, bus.low_bank, bus.high_bank, bus.chr_pages)
    return (cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp, cpu.processorCycles, live_ram,
        bus.sram, bus.vram, bus.oam, ppu, mapper, bus.dma, bus.vblank)


def observe_pointer_retirement(old, new):
    events = []
    class ScratchWatch(Donor.DonorBus):
        def __getitem__(self, address):
            if address == 1:
                events.append(('read', self.scratch_site))
            return super().__getitem__(address)

    origins = []
    for trial in (old, new):
        bus = trial.memory
        bus.__class__ = ScratchWatch
        bus.watch = lambda address, value: events.append(('write', bus.scratch_site)) if address == 1 else None
        events.clear()
        for _ in range(4000):
            bus.scratch_site = bus.code_key(trial.pc)
            trial.step()
            if events:
                assert events[0][0] == 'write', events
                origins.append(events[0][1])
                break
        else:
            raise AssertionError('probe record scratch was not retired by the native caller')
    assert origins[0] == origins[1] and machine_state(old) == machine_state(new)
    bank, pc = origins[0]
    return f'{bank}:{pc:04X}'


def paired_call(cpu, moves, destination, stop_pc, *, data_moved=False):
    assert return_pc(cpu) == stop_pc
    old, new = Donor.fork(cpu), Donor.fork(cpu)
    saved = []
    for start, blob in moves:
        low, high = start - 0x6000, start - 0x6000 + len(blob)
        saved.append((low, high, bytes(new.memory.sram[low:high]), blob))
        new.memory.sram[low:high] = blob
    new.pc = destination
    stop = stop_pc, (cpu.sp + 2) & 255
    traces = []
    for trial in (old, new):
        hardware = []
        trial.memory.watch = lambda address, value: hardware.append((address, value)) if address >= 0x2000 else None
        for _ in range(6000):
            if (trial.pc, trial.sp) == stop:
                break
            assert trial.memory[trial.pc], (hex(trial.pc), trial.sp)
            trial.step()
        else:
            raise AssertionError(('donor movement return bound', hex(trial.pc), trial.sp, stop))
        traces.append(hardware)
    for low, high, before, code in saved:
        assert new.memory.sram[low:high] == code
        new.memory.sram[low:high] = before
    assert traces[0] == traces[1]
    if machine_state(old) == machine_state(new):
        return 'exact_at_return'
    assert data_moved and stop_pc == 0x8058, (hex(cpu.pc), cpu.memory.frame)
    a, b = machine_state(old), machine_state(new)
    assert a[:6] == b[:6] and a[7:] == b[7:]
    assert a[6][0] in (0x62,0x6b,0x74,0x7d,0x86)
    assert a[6][0] == b[6][0] and (a[6][1], b[6][1]) == (0xd0,0x68) and a[6][2:] == b[6][2:]
    return observe_pointer_retirement(old, new)


def opening(raw):
    bus = Donor.DonorBus(raw)
    cpu = Donor.NesMPU(memory=bus, pc=None)
    bus.cpu = cpu
    assert cpu.pc == 0xfff3
    physical_receipt = Donor.RECEIPT.read_bytes()
    assert sha256(physical_receipt).hexdigest() == RECEIPT_PIN
    hardware = json.loads(physical_receipt)
    assert hardware['ROM_sha256'] == Donor.PIN and hardware['controller_only'] and not hardware['script_RAM_writes']
    anchors = {row['frame']: Donor.body_positions(bytes.fromhex(row['oam'])) for row in hardware['records']}
    seed = None
    for index in range(max(anchors)):
        Donor.frame(cpu, bus, Donor.original_pad(index))
        if bus.frame in anchors:
            assert Donor.body_positions(bus.oam) == anchors[bus.frame]
        if bus.frame == 1500:
            seed = Donor.fork(cpu)
    assert seed and Donor.actor(seed.memory)['x_16th'] == 1536
    return seed, anchors


def trace_episode(seed, moves, exact_moves, pads):
    cpu = Donor.fork(seed)
    bus = cpu.memory
    counts = Counter()
    pointer_retirements = Counter()
    scroll_requests = Counter()
    directions, nibbles = Counter(), Counter()
    first_queries, first_effects = {}, {}
    active_contact = False
    probe = None
    tile_reads = []
    contact_pc = {0xce81:'side_blocked', 0xced9:'vertical_blocked', 0xcef7:'landing_snap',
        0xcf02:'ceiling_cancel', 0xcfb0:'special_contact'}

    def record_query():
        assert probe is not None and bus.low_bank == 3
        ram = bus.ram
        table = ram[5] | ram[6] << 8
        raw = bus[table + cpu.y]
        mask = (0xf0, 0x0f)[ram[3] & 1]
        assert cpu.a == raw & mask
        tile = cpu.a if mask == 15 else cpu.a >> 4
        nibbles[probe, tile] += 1
        tile_reads.append((probe, ram[3], ram[2], tile))
        first_queries.setdefault(f'{probe:02X}/{tile:02X}',
            dict(frame=bus.frame, coarse_column=ram[3], coarse_row=ram[2], raw=raw,
                 address=hex(table+cpu.y), packed_mask=mask))

    def step():
        nonlocal active_contact, probe
        bank, pc = bus.code_key(cpu.pc)
        if (bank, pc) == (6, 0x81ea) and return_pc(cpu) == 0x804e:
            assert paired_call(cpu, exact_moves, 0x61ea, 0x804e) == 'exact_at_return'
            counts['position_setup_pairs'] += 1
        elif (bank, pc) == (6, 0x804e):
            scroll_requests[bus.ram[0x34], bus.ram[0x35]] += 1
        elif (bank, pc) == (7, 0xe1a4) and return_pc(cpu) == 0x8058:
            assert cpu.x == 0 and not active_contact
            assert paired_call(cpu, exact_moves, 0x64a4, 0x8058) == 'exact_at_return'
            writer = paired_call(cpu, moves, 0x64a4, 0x8058, data_moved=True)
            pointer_retirements[writer] += 1
            counts['integration_through_original_contact_pairs'] += 1
            active_contact = True
        elif active_contact and (bank, pc) == (6, 0x8058):
            active_contact = False
            probe = None
        elif active_contact and bank == 7:
            if pc == 0xce63:
                assert cpu.x == 0 and bus.low_bank == 3
                counts['real_bank3_terrain_resolutions'] += 1
            elif pc == 0xcf07:
                assert cpu.x == 0 and cpu.y in (0, 2, 4, 6, 8)
                probe = cpu.y
                directions[probe] += 1
            elif pc == 0xd03d:
                record_query()
            if pc in contact_pc:
                name = contact_pc[pc]
                counts[name] += 1
                first_effects.setdefault(name, dict(frame=bus.frame, probe=probe,
                    tentative_y_16th=bus.ram[0x0e]*256+bus.ram[0x0f],
                    prior_y_16th=bus.ram[0x12]*256+bus.ram[0x13],
                    last_tiles=tile_reads[-2:]))
        cpu.step()

    def camera():
        return (bus.ram[0x30]*256+bus.ram[0x31], bus.ram[0x32]*256+bus.ram[0x33])

    initial = Donor.actor(bus)
    initial_camera = camera()
    low_y = initial['y_16th']
    crouch = 0
    for pad in pads:
        tile_reads.clear()
        Donor.frame(cpu, bus, pad, step)
        assert not active_contact
        actor = Donor.actor(bus)
        low_y = min(low_y, actor['y_16th'])
        crouch += int(bool(actor['flags'] & 8))
    assert counts['position_setup_pairs'] == counts['integration_through_original_contact_pairs'] == len(pads)
    assert counts['real_bank3_terrain_resolutions'] == len(pads)
    return dict(frames=len(pads), calls=dict(counts), crouched_frames=crouch,
        initial=initial, terminal=actor, minimum_y_16th=low_y,
        camera_16th=[initial_camera,camera()],
        scroll_requests=[(x,y,count) for (x,y),count in sorted(scroll_requests.items())],
        relocated_data_pointer_retirements=dict(pointer_retirements),
        probe_counts=dict(directions), tile_types=[(p,t,n) for (p,t),n in sorted(nibbles.items())],
        first_queries=first_queries, first_effects=first_effects)


def main():
    assert sha256(Path(Donor.__file__).read_bytes()).hexdigest() == DONOR_CHECKER_PIN
    raw = Donor.DONOR.read_bytes()
    assert sha256(raw).hexdigest() == Donor.PIN
    moves, exact_moves, regions = source_images(raw)
    seed, anchors = opening(raw)
    episodes = {name:trace_episode(seed,moves,exact_moves,pads) for name,pads in SCENARIOS}
    assert episodes['crouch']['crouched_frames'] > 0
    assert episodes['right']['camera_16th'][0][0] < episodes['right']['camera_16th'][1][0]
    assert any(x and count for x,_,count in episodes['right']['scroll_requests'])
    for name, minimum in (('jump_tap',2504), ('jump_hold',1976)):
        trial = episodes[name]
        assert trial['minimum_y_16th'] == minimum
        assert trial['calls']['landing_snap'] == 1 and trial['terminal']['y_16th'] == 2816
        assert trial['first_effects']['landing_snap']['last_tiles'][-1][0::3] == (2, 1)
    assert sum(row['frames'] for row in episodes.values()) == 249
    assert all(row['relocated_data_pointer_retirements'] == {'7:E49D':row['frames']} for row in episodes.values())
    print(json.dumps(dict(passed=True, source_CPU_only=True, output_files=0, donor=Donor.PIN,
        source_SHA256=sha256(SOURCE.read_bytes()).hexdigest(), earlier_hardware_anchors=anchors,
        source_ranges=regions, episodes=episodes)), flush=True)


if __name__ == '__main__':
    main()
