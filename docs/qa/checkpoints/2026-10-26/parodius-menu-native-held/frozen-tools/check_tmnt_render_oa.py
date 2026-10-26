"""Execute original and optimized TnWorldDraw, including real edge fallbacks."""
from pathlib import Path
import argparse
import gzip
import hashlib
import itertools
import json
from py65.devices.mpu6502 import MPU


def load(path):
    debug = path.with_suffix('.dbg')
    text = debug.read_text() if debug.exists() else gzip.decompress(path.with_suffix('.dbg.gz').read_bytes()).decode()
    syms = {}; segs = {}
    for line in text.splitlines():
        if not line.startswith(('sym\t', 'seg\t')): continue
        z = dict(x.split('=', 1) for x in line[4:].split(',') if '=' in x)
        if line.startswith('seg\t'): segs[z['id']] = z
        elif 'val' in z: syms[z['name'].strip('"')] = z
    return dict(raw=path.read_bytes(), syms=syms, segs=segs)


def address(bundle, name):
    return int(bundle['syms'][name]['val'], 0)


def location(bundle, name):
    s = bundle['syms'][name]; g = bundle['segs'][s['seg']]
    return int(g['ooffs'], 0) + int(s['val'], 0) - int(g['start'], 0)


class Memory(list):
    def __init__(self, bundle):
        super().__init__([0] * 65536); self.bundle = bundle; self.writes = []; self.banks = [126, 87, 88, 127]
        for i, b in enumerate(self.banks): self.page(i, b)
        for g in bundle['segs'].values():
            if g.get('name') == '"SMCCODE"':
                start, size, pos = (int(g[k], 0) for k in ('start', 'size', 'ooffs'))
                self[start:start+size] = bundle['raw'][pos:pos+size]
        for name, slot in [('CurrentBank', 1), ('CurrentBankC', 2)]: self[address(bundle, name)] = self.banks[slot] | 128

    def page(self, window, bank):
        self.banks[window] = bank
        list.__setitem__(self, slice(0x8000+window*8192, 0xa000+window*8192), self.bundle['raw'][16+bank*8192:16+(bank+1)*8192])

    def __setitem__(self, at, value):
        if isinstance(at, int):
            assert at < 0x8000, ('unexpected ROM write', hex(at), value)
            self.writes.append((at, value)); list.__setitem__(self, at, value)
            if 0x5114 <= at <= 0x5117: self.page(at-0x5114, value & 127)
        else: list.__setitem__(self, at, value)


def execute(bundle, record, state, offset, rotation, flags, attr, header=None):
    m = Memory(bundle)
    for i in range(256): m[0x200+i] = (73*i+29) & 255
    x, y, xp, yp = state
    values = dict(R0=record & 255, R1=record >> 8, R3=attr, R4=x, R5=xp, R6=y, R7=yp,
                  CurrentOAMOffset=offset, GuestOamRotationActive=rotation[0], RgOamRotation=rotation[1])
    if header is not None:
        values.update(R0=0xa0, R1=0x5c)
        m[0x5ca0] = header
        for i in range(1, 257): m[0x5ca0+i] = [1, 0xa2, 0xf8, 0xfc][(i-1) % 4]
    for n, v in values.items(): m[address(bundle, n)] = v
    m[0x1fe] = 0xef; m[0x1ff] = 0xff; m.writes = []
    c = MPU(memory=m, pc=address(bundle, 'TnWorldDraw')); c.sp = 0xfd
    c.a = 0x55; c.x = 3; c.y = 7; c.p = flags
    generic = 0
    for _ in range(5000):
        if c.pc == 0xfff0: break
        if c.pc == address(bundle, 'MetaspriteRenderLoop'): generic += 1
        c.step()
    else: raise AssertionError(('CPU timeout', hex(c.pc), m.banks))
    excluded = set(range(0x100, 0x200)) | set(range(0x5114, 0x5118))
    for g in bundle['segs'].values():
        if g.get('name') == '"SMCCODE"': excluded.update(range(int(g['start'], 0), int(g['start'], 0)+int(g['size'], 0)))
    for n in ('safecall_a', 'SafecallA'):
        if n in bundle['syms']: excluded.add(address(bundle, n))
    memory = {at: m[at] for at, _ in m.writes if at not in excluded}
    oam_writes = [(at, v) for at, v in m.writes if 0x200 <= at < 0x300]
    return (c.a, c.x, c.y, c.p & 0xcf), memory, oam_writes, c.processorCycles, generic


def main():
    p = argparse.ArgumentParser(); p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--baseline', type=Path, required=True); p.add_argument('--output', type=Path, required=True)
    a = p.parse_args(); a.output.mkdir(parents=True, exist_ok=False)
    old, new = load(a.baseline), load(a.rom)
    old_labels = {q[2]: q[1] for line in a.baseline.with_suffix('.lbl').read_text().splitlines() if len(q := line.split()) == 3}
    new_labels = {q[2]: q[1] for line in a.rom.with_suffix('.lbl').read_text().splitlines() if len(q := line.split()) == 3}
    assert all(new_labels[n] == v for n, v in old_labels.items()), 'A pre-existing label moved'
    records = {}; bounds = []
    for face in ('R', 'L'):
        lo = location(new, 'TnWorld'+face+'Lo'); hi = location(new, 'TnWorld'+face+'Hi')
        s = new['syms']['TnWorld'+face+'Lo']; g = new['segs'][s['seg']]
        base = int(g['ooffs'], 0)-int(g['start'], 0)
        for pose in range(84):
            ptr = new['raw'][lo+pose]+256*new['raw'][hi+pose]
            off = base+ptr; length = new['raw'][off]
            assert length % 4 == 0 and length < 128
            for i in range(1, length+1, 4):
                part = new['raw'][off+i:off+i+4]
                dx, dy = (v-256 if v >= 128 else v for v in (part[3], part[2]))
                assert -8 <= dx <= 0 and -24 <= dy <= 0, (face, pose, dx, dy)
                bounds.append((dx, dy))
            records.setdefault(ptr, dict(face=face, pose=pose, length=length))
    states = [(8,24,0,1), (128,128,0,1), (255,255,0,1), (0,24,0,1), (7,24,0,1),
              (8,23,0,1), (8,0,0,1), (128,23,0,1), (255,24,255,1), (0,24,1,1),
              (128,255,0,0), (128,0,0,2)]
    offsets = [0,16,128,232,240,248,252]
    rotations = [(0,0),(1,4),(1,128),(1,252)]
    rows = []; fast = 0; fallback = 0

    def check(ptr, state, offset, rotation, flags, attr, header=None):
        nonlocal fast, fallback
        before = execute(old, ptr, state, offset, rotation, flags, attr, header)
        after = execute(new, ptr, state, offset, rotation, flags, attr, header)
        assert before[:3] == after[:3], (hex(ptr), state, offset, rotation, hex(flags), hex(attr), header,
            before[0], after[0], [(hex(k), before[1].get(k), after[1].get(k)) for k in set(before[1])|set(after[1]) if before[1].get(k)!=after[1].get(k)][:16])
        assert before[4] == 1 and after[4] in (0,1)
        fast += after[4] == 0; fallback += after[4] == 1
        rows.append(dict(pointer=ptr, state=state, offset=offset, rotation=rotation, flags=flags,
                         attr=attr, header=header, baseline_cycles=before[3], candidate_cycles=after[3], fallback=bool(after[4])))

    for i, (ptr, state, off, rot, flags) in enumerate(itertools.product(records, states, offsets, rotations, [0x30,0x71])):
        check(ptr, state, off, rot, flags, [0,0x20,3,0xff][i % 4])
    for header, off, rot, flags in itertools.product([0,1,3,4,8,16,124,128,252,255], offsets, rotations, [0x30,0x71]):
        check(0x5ca0, (128,128,0,1), off, rot, flags, 0, header)
    proof = dict(passed=True, ROM_sha256=hashlib.sha256(new['raw']).hexdigest(),
        baseline_ROM_sha256=hashlib.sha256(old['raw']).hexdigest(), cases=len(rows), fast_cases=fast,
        fallback_cases=fallback, world_table_entries=168, unique_records=len(records),
        signed_bounds=dict(dx=[min(p[0] for p in bounds),max(p[0] for p in bounds)],dy=[min(p[1] for p in bounds),max(p[1] for p in bounds)]),
        all_preexisting_labels_unchanged=True, registers='Exact A/X/Y and NV-DIZC',
        memory='Exact written application RAM and ordered OAM writes; only stack, SMC operands, mapper bank registers and safecall bookkeeping excluded.',
        scope='Actual assembled TnWorldDraw differential; no interrupts/native frame timing in this CPU layer.')
    (a.output/'proof.json').write_text(json.dumps(proof, indent=2)+'\n')
    (a.output/'cases.json').write_text(json.dumps(rows, separators=(',',':'))+'\n')
    print(json.dumps(proof, indent=2))


if __name__ == '__main__': main()
