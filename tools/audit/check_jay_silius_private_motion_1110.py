"""Run the proposed two-page Jay packet on real donor and native terrain inputs."""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys

import check_jay_silius_host_tile_1110 as Host
import trace_jay_silius_motion_1110 as Motion

sys.path.insert(0, str(Host.ROOT / 'tools/reference'))
import jay_silius_private_motion_1110 as Jay

Donor, W, N = Motion.Donor, Host.W, Host.N
PIN = '49295acff1d70349119b599882a2ec0b4e2f58d21f153c90b2228dc9aceee2a7'
NEXT = '9897c2b85489024be25b4b296d0ea57975a579ba1e3ff37a71f7ac3e0b195b97'
ENTRY = {(6,0x8093):('JayOriginalInput',0x804b), (6,0x81ea):('JayPositionSetup',0x804e),
         (7,0xe1a4):('JayIntegrate',0x8058)}
REAL_SERVICES = {Jay.SERVICES['OriginalWeaponInput']:0x81d2,
                 Jay.SERVICES['OriginalTerrainEvent']:0xea06, 0xd002:0xd002}
STOP = 0x5b00


def digest(raw):
    return sha256(raw).hexdigest()


def exact_parents(installed):
    if digest(installed) == PIN:
        return installed, None
    assert digest(installed) == NEXT
    import check_smb2_menu_tier_isolation_1110 as Tier

    at = 16 + Tier.BANK * 8192 + (Tier.BEGIN & 8191)
    parent = installed[:at] + Tier.OLD + installed[at + len(Tier.OLD):]
    assert digest(parent) == PIN and Tier.proposal(parent)[0] == installed
    return parent, installed


def run(cpu, stop, *, hook=None, bound=6000):
    for _ in range(bound):
        if (cpu.pc, cpu.sp) == stop:
            return
        if hook is not None and hook(cpu):
            continue
        assert cpu.memory[cpu.pc], ('actual CPU BRK', hex(cpu.pc), cpu.sp)
        cpu.step()
    raise AssertionError(('source execution bound', hex(cpu.pc), cpu.sp, stop))


def regs(cpu):
    return cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp


class DonorPacketBus(Donor.DonorBus):
    packet_mode = True

    def __getitem__(self, address):
        if self.packet_mode:
            if Jay.ORIGIN <= address < Jay.ORIGIN + len(self.packet):
                return self.packet[address - Jay.ORIGIN]
            if address in self.physical:
                return self.ram[self.physical[address]]
            if Jay.SCRATCH <= address <= Jay.PROBE_INDEX:
                return self.scratch[address - Jay.SCRATCH]
        return super().__getitem__(address)

    def __setitem__(self, address, value):
        if self.packet_mode:
            assert not Jay.ORIGIN <= address < Jay.ORIGIN + len(self.packet), hex(address)
            if address in self.physical:
                self.ram[self.physical[address]] = value
                return
            if Jay.SCRATCH <= address <= Jay.PROBE_INDEX:
                self.scratch[address - Jay.SCRATCH] = value
                return
        super().__setitem__(address, value)

    def donor_mapper_view(self):
        # Only the parity harness translates the private logical mapper byte
        # into a donor PRG view. The actual packet writes no mapper register.
        bank = self.ram[0xf1]
        assert self.ctrl >> 2 & 3 == 3 and bank < 8 and self.shift == 16
        self.low_bank = self.prg_reg = bank


def packet_fork(cpu, link):
    trial = Donor.fork(cpu)
    bus = trial.memory
    bus.__class__ = DonorPacketBus
    bus.packet = link['images']['PRIVATE']
    bus.physical = {physical:logical for logical,physical in link['ram'].items()}
    bus.scratch = bytearray(Jay.PROBE_INDEX - Jay.SCRATCH + 1)
    return trial


def donor_pair(cpu, link, label, return_pc, counts):
    old, new = Donor.fork(cpu), packet_fork(cpu, link)
    assert Motion.return_pc(cpu) == return_pc
    stop = return_pc, (cpu.sp + 2) & 255
    old_samples, new_samples = [], []

    def trace_old(c):
        if c.pc == 0xd002:
            old_samples.append((c.memory.ram[2], c.memory.ram[3], c.x))
        return False

    def imports(c):
        if c.pc not in REAL_SERVICES:
            return False
        b = c.memory
        target = REAL_SERVICES[c.pc]
        if target == 0xd002:
            new_samples.append((b.ram[2], b.ram[3], c.x))
            direction = b[Jay.SCRATCH + 2]
            counts[f'probe_{direction}'] += 1
        counts[f'genuine_{target:04X}'] += 1
        b.donor_mapper_view()
        native_stop = Motion.return_pc(c), (c.sp + 2) & 255
        b.packet_mode = False
        c.pc = target
        run(c, native_stop)
        b.packet_mode = True
        return True

    new.pc = link['symbols'][label]
    run(old, stop, hook=trace_old)
    run(new, stop, hook=imports)
    new.memory.donor_mapper_view()
    assert regs(old) == regs(new) and old_samples == new_samples, (
        label, cpu.memory.frame, regs(old), regs(new), old_samples, new_samples)
    a, b = old.memory, new.memory
    relevant = lambda m: (bytes(m.ram[:0x100]), bytes(m.ram[0x101 + old.sp:]),
        m.sram, m.vram, m.oam, m.ppu_ctrl, m.ppu_mask, m.ppu_address,
        m.ppu_latch, m.ppu_buffer, m.oam_address, m.low_bank, m.high_bank, m.prg_reg,
        m.ctrl, m.chr0, m.chr1, m.chr_pages, m.shift)
    assert relevant(a) == relevant(b), (label, cpu.memory.frame,
        [(hex(i),x,y) for i,(x,y) in enumerate(zip(a.ram,b.ram)) if x != y and not 0x100 <= i <= 0x1ff])
    counts[label] += 1


def donor_trials(seed, link):
    counts = Counter()
    first = None
    for name, pads in Motion.SCENARIOS:
        cpu = Donor.fork(seed)
        bus = cpu.memory

        def step():
            nonlocal first
            entry = ENTRY.get(bus.code_key(cpu.pc))
            if entry is not None and Motion.return_pc(cpu) == entry[1]:
                if first is None and entry[0] == 'JayOriginalInput':
                    first = Donor.fork(cpu)
                donor_pair(cpu, link, *entry, counts)
            cpu.step()

        for pad in pads:
            Donor.frame(cpu, bus, pad, step)
        print('Paired genuine donor scenario', name, len(pads), flush=True)
    assert all(counts[label] == 249 for label,_ in ENTRY.values())
    assert counts['genuine_81D2'] == 249 and counts['genuine_D002'] == 839
    assert sum(counts[f'probe_{i}'] for i in (0,2,4,6,8)) == 839
    return dict(counts), first


def host_trial(host, link, donor, pads):
    m = N.fork(host)
    m.raw_page(1, 3)
    m.raw_page(2, 2)
    N.put(m, CurrentBank=3, CurrentBankC=2)
    image = link['images']['PRIVATE']
    m.ram[3][:len(image)] = image
    state = link['ram']
    for logical, physical in state.items():
        m[physical] = donor.memory.ram[logical]
    # Fixture constructor uses the unmodified native stage's spawn. Main is
    # never patched. All subsequent motion comes from the proposed packet.
    x = N.get(m,'Player_X_Position') + 256 * N.get(m,'Player_PageLoc')
    native_y = N.get(m,'Player_Y_Position')
    surface_row = next(row for row in range(native_y // 16,15)
                       if Host.expected(m,x // 16,row,2)[:2] == (0,1))
    # The original donor foot list samples actor center +16. The host's
    # recorded spawn is a top anchor; its authored floor is a row lower
    # than the donor opening floor. Derive the center from the actual cell.
    donor_y = (surface_row - 1) * 16
    for hi,lo,pixel in ((0x10,0x11,x),(0x12,0x13,donor_y),(0x30,0x31,0),(0x32,0x33,0)):
        m[state[hi]],m[state[lo]] = pixel >> 4, (pixel << 4) & 255
    counts = Counter()
    timeline = []
    probes = []

    def call(label, a=0, x=0, y=0, p=0x31):
        cpu = N.NesMPU(memory=m, pc=link['symbols'][label])
        cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp = a,x,y,p,224
        cpu.stPushWord(STOP-1)
        prior_header = bytes(m.ram[2][0x1fd0:]) + bytes(m.ram[3][0x1fe0:])
        map_before = tuple(m.rawtags)
        W.clear_logs(m)

        def hook(c):
            if c.pc == link['symbols']['JayHostTile']:
                qy,qx,direction = m[Jay.SCRATCH:Jay.SCRATCH + 3]
                status,tile,reads = Host.expected(m,qx,qy,direction)
                assert status == 0 and len(reads) == 2
                target = (m[0x100+((c.sp+1)&255)] | (m[0x100+((c.sp+2)&255)] << 8)) + 1
                run(c,(target,c.sp+2))
                assert c.a == (tile if qx & 1 else tile << 4)
                assert m[Jay.SCRATCH + 3:Jay.SCRATCH + 6] == [0,m[reads[0]],m[reads[1]]]
                counts[f'host_probe_{direction}_{tile}'] += 1
                probes.append((qx,qy,direction,tile,m[reads[0]]))
                return True
            if c.pc != Jay.SERVICES['OriginalWeaponInput']:
                assert c.pc != Jay.SERVICES['OriginalTerrainEvent'], 'Scripted terrain is outside this fixture'
                return False
            # Call the pinned original weapon routine in its own donor bus.
            # This fixture presses no B and does not publish donor projectiles.
            external = Donor.fork(donor)
            external.pc = 0x81d2
            external.a,external.x,external.y,external.p,external.sp = regs(c)
            for logical,physical in state.items():
                external.memory.ram[logical] = m[physical]
            before = bytes(external.memory.ram)
            external.stPushWord(0x60ff)
            run(external,(0x6100,c.sp))
            unowned = [(hex(i),before[i],v) for i,v in enumerate(external.memory.ram)
                       if i not in state and not 0x100 <= i <= 0x1ff and before[i] != v]
            assert not unowned, unowned
            for logical,physical in state.items():
                m[physical] = external.memory.ram[logical]
            c.a,c.x,c.y,c.p,_ = regs(external)
            c.pc = c.stPopWord()+1
            counts['authentic_weapon_import'] += 1
            return True

        run(cpu,(STOP,224),hook=hook)
        assert map_before == tuple(m.rawtags) and not m.blocked
        assert prior_header == bytes(m.ram[2][0x1fd0:]) + bytes(m.ram[3][0x1fe0:])
        assert all(bank == 2 and (offset < 0x100) for bank,offset,_ in m.ram_writes)
        assert all(0x100 <= address < 0x200 or 0xc000 <= address < 0xc100 for address,_ in m.writes)
        return regs(cpu)[:4]

    previous = 0
    for pad in pads:
        m[state[0x162]],m[state[0x163]] = pad,previous
        a,xr,yr,p = call('JayOriginalInput')
        a,xr,yr,p = call('JayPositionSetup',a,xr,yr,p)
        call('JayIntegrate',a,0,yr,(p & ~0x80) | 2)
        previous = pad
        timeline.append((m[state[0x10]]*256+m[state[0x11]],m[state[0x12]]*256+m[state[0x13]],
                         m[state[0x19]],m[state[0x15]]))
    return timeline, dict(counts), probes, (x,native_y,donor_y,surface_row)


def main():
    raw, successor = exact_parents(Host.ROM.read_bytes())
    donor_raw = Donor.DONOR.read_bytes()
    assert digest(donor_raw) == Donor.PIN
    Donor.input_images(donor_raw)
    Motion.source_images(donor_raw)
    bundle = W.Symbols.bundle()
    bundle['raw'] = raw
    Host.Terrain.source_bindings(raw,bundle)
    Host.carrier(raw)
    host = Host.first_active(bundle)
    if successor is not None:
        latest = dict(bundle, raw=successor)
        assert Host.Terrain.source_bindings(successor,latest) == Host.Terrain.source_bindings(raw,bundle)
        assert Host.carrier(successor) == Host.carrier(raw)
        later = Host.first_active(latest)
        bindings = ('ColumnSets','AreaParserTaskNum','CurrentPageLoc','CurrentColumnPos',
                    'BlockBufferColumnPos','ScreenLeft_PageLoc','ScreenLeft_X_Pos')
        assert all(N.get(host,name) == N.get(later,name) for name in bindings)
        assert host[0x300:0x4a0] == later[0x300:0x4a0]
    old, linked = Jay.build(donor_terrain=True), Jay.build()
    image, donor_image = linked['images']['PRIVATE'], old['images']['PRIVATE']
    assert len(image) == len(donor_image) + 347 and 1024 < len(image) <= 2048
    assert all(op['mode'] not in ('iny','inx') for op in linked['instructions'])
    print('Measured packet', len(image), 'bytes at', hex(Jay.ORIGIN), flush=True)
    seed, anchors = Motion.opening(donor_raw)
    donor_counts, active_donor = donor_trials(seed,old)
    actual = {}
    for name,pads in (('idle',[0]*8),('walk',[1]*40),('tap',[128]+[0]*35),('hold',[128]*14+[0]*36)):
        trail, counts, probes, spawn = host_trial(host,linked,active_donor,pads)
        sx,native_y,donor_y,surface_row = spawn
        assert spawn == (40,176,192,13)
        end = trail[-1]
        assert end[1] == donor_y*16 and not end[2] & 4, (name,end,trail[:8],probes[:12])
        assert any(qy == surface_row and direction == 2 and cls == 1 for _,qy,direction,cls,_ in probes)
        if name == 'walk':
            assert end[0] > 40*16
        apex = donor_y*16 - min(point[1] for point in trail)
        assert apex == {'idle':0,'walk':0,'tap':312,'hold':840}[name], (name,apex)
        actual[name] = dict(updates=len(pads), terminal_XY_16th=end[:2], apex_16th=apex, queries=counts,
                            native_spawn=[sx,native_y], donor_center_Y=donor_y, floor_row=surface_row,
                            floor_raw_tiles=sorted({tile for _,qy,d,cl,tile in probes if qy==surface_row and d==2 and cl==1}))
    print(json.dumps(dict(passed=True, ROM_SHA256=PIN, installed_same_native_bindings=digest(successor) if successor else PIN,
        ROM_written=False, Mesen=False,
        build_files=0, source_SHA256=digest(Path(Jay.__file__).read_bytes()), packet_SHA256=digest(image),
        bytes=len(image), minimum_pages=2, unfilled_bytes_in_two_pages=2048-len(image),
        relative_branches=linked['branch_displacements'], donor_hardware_anchors=sorted(anchors),
        donor_pairs=donor_counts, isolated_live_terrain_routes=actual,
        public_or_RAM_granted=False), sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
