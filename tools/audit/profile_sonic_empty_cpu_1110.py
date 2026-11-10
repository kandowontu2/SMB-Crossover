"""Trace exact rebased Sonic's genuine, empty 1-1 controller updates in memory."""
from collections import Counter, defaultdict
from hashlib import sha256
import json

import profile_ff_empty_cpu_v2_1110 as Profile
import stage_sonic_original_1110 as Stage

W, N, UI = Stage.Controller.W, Stage.Controller.N, Stage.Controller.UI
PIN = 'e7a30825f992d9a28c813ee7eb2571e6836b8f75c6579234f7f7a66106a6d896'
AUTH_CHECK = (193, 0xaf27)
AUTH_PC = (0xaf27, 0xaf35, 0xaf38, 0xaf3a, 0xaf3c, 0xaf3d, 0xaf46, 0xaf4e)


def position(m):
    return N.get(m, 'Player_X_Position') + 256 * N.get(m, 'Player_PageLoc')


def flags(m):
    return tuple(N.get(m, 'Enemy_Flag', i) for i in range(6))


def enter(image):
    bundle = W.Symbols.bundle()
    bundle['raw'] = image
    original_bus = N.Bus
    N.Bus = W.ControllerBus
    try:
        m = UI.seed(bundle, 25)
    finally:
        N.Bus = original_bus
    for _ in range(3):
        UI.key(m, 32)
    assert UI.menu_name(m)[0] == 'SONIC' and N.get(m, 'SelectedCharacter') == 43
    start = UI.key(m, 16)
    assert N.get(m, 'CrossoverMenuState') == 0
    N.invoke(m, 'NativeRareGameMenuRoutineCore::ChkContinue', a=start['A'], x=start['X'], y=start['Y'], p=start['P'])
    N.invoke(m, 'PauseRoutine', a=0)
    return m


def cpu_main(m):
    idle = W.address(m.bundle, 'IdleLoop')
    cpu = N.NesMPU(memory=m, pc=idle)
    cpu.sp, cpu.p = 255, 0x31
    cpu.stPushWord(0xe33b)
    return cpu, (idle + 12, 252)


def main_step(m, pad, trace=None):
    m.controller_pad = pad
    W.clear_logs(m)
    nmi_cycles = Profile.normal_nmi(m)
    cpu, stop = cpu_main(m)
    if trace:
        trace.run(cpu, stop)
    else:
        for _ in range(500000):
            if (cpu.pc, cpu.sp) == stop:
                break
            assert m[cpu.pc], hex(cpu.pc)
            cpu.step()
        else:
            raise AssertionError(('cold Main bound', hex(cpu.pc)))
    assert not m.blocked
    return cpu.processorCycles, nmi_cycles


class Trace:
    def __init__(self, m, packet):
        self.m = m
        self.cycles = Counter()
        self.instructions = Counter()
        self.call_count = Counter()
        self.call_cycles = Counter()
        self.ancestors = defaultdict(Counter)
        self.names = defaultdict(lambda: defaultdict(list))
        self.entry_cycles = Counter()
        self.entry_count = Counter()
        self.auth_origins = Counter()
        self.auth_targets = Counter()
        self.private_names = {}
        for name, sym in m.bundle['syms'].items():
            if sym.get('type') != 'lab' or 'seg' not in sym:
                continue
            try:
                at, loc = W.address(m.bundle, name), W.location(m.bundle, name)
            except (KeyError, ValueError):
                continue
            if loc < 16:
                continue
            tag = -1 if at < 0x8000 else (loc - 16) // 8192 | 128
            self.names[tag][at].append(name)
        for group, symbols in ((3, packet['service']['symbols']), (2, packet['metadata']['symbols']),
                               (3, packet['packet']['frame']['symbols'])):
            for name, pc in symbols.items():
                if group == 3 and not 0xa000 <= pc < 0xc000:
                    continue
                if group == 2 and not 0xd000 <= pc < 0xdfe0:
                    continue
                self.names[group][pc].append(name)
                if name in ('SonicHostMain', 'SonicNativeOrdinaryFrame', 'MetaFeet', 'MetaHead', 'MetaSide',
                            'MetaBounds', 'MetaDraw', 'MetaGraphics'):
                    self.private_names[group, pc] = name
        self.names[2][0xd100].insert(0, 'SonicServices')
        self.names[193][0xaf27].insert(0, 'CoCheckHeaders')

    def label(self, point):
        tag, pc = point
        nearby = [at for at in self.names[tag] if at <= pc]
        if not nearby:
            return f'{tag}:{pc:04X}'
        at = max(nearby)
        names = '/'.join(self.names[tag][at][:2])
        return f'{tag}:{pc:04X} {names}+{pc-at:X}'

    def run(self, c, stop):
        m = self.m
        common = W.address(m.bundle, 'FarCallCommon')
        jump = W.address(m.bundle, 'FarcallJmpTarget_SMC')
        calls, scopes, frames = [], [], []
        last = None
        for _ in range(300000):
            state = c.pc, c.sp
            for pending, totals, counts in ((calls, self.call_cycles, self.call_count),
                                           (scopes, self.entry_cycles, self.entry_count)):
                for index in range(len(pending) - 1, -1, -1):
                    goal, name, start = pending[index]
                    if state == goal:
                        totals[name] += c.processorCycles - start
                        counts[name] += 1
                        del pending[index]
            while frames and c.sp >= frames[-1][0][1]:
                frames.pop()
            if state == stop:
                assert not calls and not scopes and not frames
                return
            point = Profile.point(m, c.pc)
            name = self.private_names.get(point)
            if point == AUTH_CHECK:
                # Common authentication has exactly one nested caller here.
                # AEF6 is the JSR from the register-preserving public checker.
                low = m[0x100 + ((c.sp + 1) & 255)]
                high = m[0x100 + ((c.sp + 2) & 255)]
                outer = m[0x100 + ((c.sp + 5) & 255)] | m[0x100 + ((c.sp + 6) & 255)] << 8
                self.auth_origins[(low | high << 8) - 2, outer - 2] += 1
                self.auth_targets[m[jump + 1] | m[jump + 2] << 8] += 1
                name = 'CoCheckHeaders'
            if c.pc == common or name:
                ret = m[0x100+((c.sp+1)&255)] + 256*m[0x100+((c.sp+2)&255)] + 1
                goal = ret, (c.sp+2)&255
                if c.pc == common:
                    destination = m[jump+1] + 256*m[jump+2]
                    tag = c.a if 0xa000 <= destination < 0xc000 else Profile.point(m, destination)[0]
                    key = last, (tag, destination)
                    calls.append((goal, key, c.processorCycles))
                    self.ancestors[key][tuple(edge[1] for edge in frames[-5:])] += 1
                if name:
                    scopes.append((goal, name, c.processorCycles))
            opcode = m[c.pc]
            assert opcode, point
            if opcode == 0x20:
                frames.append(((c.pc + 3, c.sp), point))
            begin = c.processorCycles
            c.step()
            self.cycles[point] += c.processorCycles - begin
            self.instructions[point] += 1
            last = point
        raise AssertionError(('profiled Main bound', hex(c.pc)))

    def summary(self, frames):
        banks, ranges = Counter(), Counter()
        for (tag, pc), cycles in self.cycles.items():
            banks[tag] += cycles
            ranges[tag, pc & 0xffc0] += cycles
        count = len(frames)
        return dict(updates=count, start_x=frames[0]['before_x'], end_x=frames[-1]['after_x'],
            Main=dict(mean=sum(self.cycles.values())/count, minimum=min(x['Main'] for x in frames),
                      maximum=max(x['Main'] for x in frames)),
            normal_NMI=dict(mean=sum(x['NMI'] for x in frames)/count, minimum=min(x['NMI'] for x in frames),
                            maximum=max(x['NMI'] for x in frames)),
            FarCallCommon_per_Main=sum(self.call_count.values())/count,
            FarCallCommon_hot=[dict(caller=self.label(site), target=self.label(target),
                calls_per_Main=self.call_count[site, target]/count, inclusive_cycles_per_Main=cycles/count,
                ancestry=[self.label(p) for p in self.ancestors[site, target].most_common(1)[0][0]])
                for (site, target), cycles in self.call_cycles.most_common(18)],
            private_entries={name: dict(calls_per_Main=self.entry_count[name]/count, inclusive_cycles_per_Main=cycles/count)
                             for name, cycles in self.entry_cycles.items()},
            shared_header_checks=dict(origins=[(f'{inner:04X}', f'{outer:04X}', calls/count)
                    for (inner, outer), calls in self.auth_origins.most_common()],
                targets=[(f'{target:04X}', calls/count) for target, calls in sorted(self.auth_targets.items())],
                instructions=[dict(pc=f'{pc:04X}', per_Main=self.instructions[193, pc]/count,
                    cycles_per_Main=self.cycles[193, pc]/count) for pc in AUTH_PC]),
            hot_banks=[(tag, cycles/count) for tag, cycles in banks.most_common(8)],
            hot64=[(self.label(point), cycles/count) for point, cycles in ranges.most_common(12)])


def main():
    image, _, packet, record = Stage.reconstruct()
    digest = sha256(image).hexdigest()
    assert digest == record['ROM_SHA256'] == PIN, digest
    offset = 16 + 65 * 8192 + (0xaf27 & 8191)
    assert image[offset:offset + 40] == bytes.fromhex(
        'ada17d48a2038ea17d8e1651a00fb9e0dfd108d00a8810f6cae001d0e9b00118688da17d8d165160')
    m = enter(image)
    for cold in range(300):
        if (N.get(m, 'OperMode'), N.get(m, 'OperMode_Task'), N.get(m, 'GameEngineSubroutine')) == (1, 3, 8):
            break
        main_step(m, 0)
    else:
        raise AssertionError('native 1-1 cold bound')
    assert position(m) == 40 and N.get(m, 'NumberofLives') == 2
    for _ in range(4):
        main_step(m, 0)
    out = {}
    for phase, pad, length in (('idle', 0, 32), ('walk', 1, 32)):
        trace = Trace(m, packet)
        frames = []
        for _ in range(length):
            before_x = position(m)
            assert not any(flags(m)), (phase, before_x, flags(m))
            assert N.get(m, 'GameEngineSubroutine') == 8 and N.get(m, 'NumberofLives') == 2
            cycles, nmi_cycles = main_step(m, pad, trace)
            assert not any(flags(m)), (phase, position(m), flags(m))
            frames.append(dict(before_x=before_x, after_x=position(m), Main=cycles, NMI=nmi_cycles))
        out[phase] = trace.summary(frames)
        assert sum(x['Main'] for x in frames) == sum(trace.cycles.values())
    assert out['idle']['start_x'] == out['idle']['end_x'] == 40
    assert out['walk']['end_x'] > out['walk']['start_x']
    assert bytes(m.ram[2][0x1fe0:0x1ff0]) == bytes(m.ram[3][0x1fe0:0x1ff0]) == packet['packet']['cookie']
    print(json.dumps(dict(passed=True, ROM_SHA256=digest, source_CPU_only=True, output_files=0,
        native_cold_Main=cold, profiles=out, scope='Controller-only empty 1-1. Instruction cycles exclude DMA stall and scanline IRQ. Inclusive call spans overlap.')), flush=True)


if __name__ == '__main__':
    main()
