"""Execute real late lift renderer, native row control and firebar admission."""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
from check_tmnt_render_oa import load, address, location, Memory
from verify_native_relocation import NesMPU


class Machine:
    def __init__(self, bundle):
        self.b = bundle
        self.m = Memory(bundle)
        self.cpu = NesMPU(memory=self.m)

    def put(self, n, value, i=0):
        self.m[address(self.b, n)+i] = value&255

    def get(self, n, i=0):
        return self.m[address(self.b, n)+i]

    def call(self, n, x=0, y=0, a=0x55, p=0x75):
        at = location(self.b, n)
        bank = (at-16)//8192
        if address(self.b, n) >= 0xa000 and address(self.b, n) < 0xc000:
            self.m.page(1, bank)
            self.put('CurrentBank', bank|128)
        c = self.cpu
        c.a, c.x, c.y, c.p, c.sp = a, x, y, p, 0xfd
        c.stPushWord(0x7eff)
        c.pc = address(self.b, n)
        self.m.writes = []
        for _ in range(20000):
            if c.pc == 0x7f00:
                break
            c.step()
        else:
            raise AssertionError((n, hex(c.pc), self.m.banks))
        assert c.sp == 0xfd, (n, c.sp)
        if address(self.b, n) >= 0xa000 and address(self.b, n) < 0xc000:
            assert self.m.banks[1] == bank
        return c.a, c.x, c.y, c.p

    def setup(self, slot=0, rel=100, first=112, second=176, world=1, area=0x62,
              ident=0x2b, active=1, rotation=0, offset=0, rotating=1):
        fields = dict(GuestOamRotationActive=rotating, RgOamRotation=rotation,
                      CurrentOAMOffset=offset, ScreenLeft_X_Pos=226, ScreenLeft_PageLoc=4,
                      ScreenRight_X_Pos=225, ScreenRight_PageLoc=5, AreaPointer=area,
                      WorldNumber=world, ObjectOffset=slot, Enemy_Rel_XPos=rel&255,
                      Enemy_Rel_YPos=first, FirebarSlot=0xa5, FirebarPart=0xb6,
                      FirebarTemp=0xc7, Enemy_OffscreenBits=0xd8)
        for n, v in fields.items():
            self.put(n, v)
        for i in range(6):
            self.put('Enemy_Flag', 0, i)
            self.put('Enemy_ID', 0, i)
        self.put('Enemy_Flag', active, slot)
        self.put('Enemy_ID', ident, slot)
        self.put('Enemy_Y_Position', first, slot)
        self.put('Enemy_Y_HighPos', 1, slot)
        self.put('Enemy_State', second, slot)
        x = 4*256+226+rel
        self.put('Enemy_X_Position', x&255, slot)
        self.put('Enemy_PageLoc', x>>8, slot)
        for i in range(64):
            self.m[0x200+i*4:0x204+i*4] = [248, 0xa3, 0x5c, 0x71]


def sprites(m):
    return sorted(tuple(m.m[0x200+i*4:0x204+i*4]) for i in range(64) if m.m[0x200+i*4] < 240)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--parent', type=Path, required=True)
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    old, new = load(a.parent), load(a.rom)
    counts = dict(mask_records=0, source_geometry=0, all_rotations=0, capacity=0,
                  vertical_limits=0, negative_admission=0, native_firebars=0)
    for mask in range(8):
        at = location(new, f'Z2LateSmallRow{mask}')
        n = new['raw'][at]
        data = new['raw'][at+1:at+1+n]
        parts = [tuple(data[i:i+4]) for i in range(0, n, 4)]
        wanted = [(90, 2, 0, col*8) for col in range(3) if not (mask & (4>>col))]
        assert parts[::-1] == wanted
        counts['mask_records'] += 1

    controls = {}

    def control(slot, rel, first, second, mode, ident):
        key = slot, rel, first, second, mode, ident
        if key not in controls:
            area, world = mode
            m = Machine(old)
            m.setup(slot=slot, rel=rel, first=first, second=second, area=area, world=world,
                    ident=ident, rotating=0)
            m.call('GetEnemyOffscreenBits', x=slot)
            mask = (m.get('Enemy_OffscreenBits')&14)>>1
            m.call('CrossoverDrawSmallPlatform', x=slot)
            controls[key] = sprites(m), mask
        return controls[key]

    def check(slot=0, rel=100, first=112, second=176, mode=(0x62, 1), ident=0x2b,
              rot=0, offset=0):
        area, world = mode
        expected, mask = control(slot, rel, first, second, mode, ident)
        count = sum(not (mask & (4>>col)) for col in range(3))
        ys = [first, second if area == 0x62 and world in [1, 4] else (first+128)&255]
        cursor = offset
        wanted = []
        for yy in ys:
            if 32 <= yy < 240 and count and cursor+count*4 < 256:
                wanted += [s for s in expected if s[0] == yy]
                cursor += count*4
        m = Machine(new)
        m.setup(slot=slot, rel=rel, first=first, second=second, area=area, world=world,
                ident=ident, rotation=rot, offset=offset)
        owner = {n:m.get(n) for n in ['ObjectOffset', 'Enemy_OffscreenBits', 'FirebarSlot', 'FirebarPart', 'FirebarTemp', 'CurrentBankC']}
        regs = m.call('Z2DrawLateSmallLifts', x=3, y=7, a=0x55, p=0x75)
        assert regs == (0x55, 3, 7, 0x75), regs
        assert all(m.get(n) == v for n, v in owner.items()), owner
        assert sprites(m) == sorted(wanted), (slot, rel, first, second, mode, ident, rot, offset, mask, sprites(m), sorted(wanted))
        assert m.get('CurrentOAMOffset') == cursor
        assert m.m.banks[2] == 88
        assert all(0x200 <= at < 0x300 for at, v in m.m.writes if 0x200 <= at < 0x400)
        return m

    modes = [(0x62, 1), (0x62, 4), (0x40, 0)]
    for slot, mode, ident, rot in itertools.product(range(6), modes, [0x2b, 0x2c], range(0, 256, 4)):
        check(slot=slot, mode=mode, ident=ident, rot=rot)
        counts['all_rotations'] += 1
    for slot, mode, rel, rot, off in itertools.product([0, 3], modes,
             [-16, -8, -1, 0, 7, 239, 248, 255], [0, 4, 128, 252], [0, 16, 224, 232, 240, 248, 252]):
        check(slot=slot, mode=mode, rel=rel, rot=rot, offset=off)
        counts['capacity'] += 1
    for mode, first, rot, off in itertools.product(modes, [31, 32, 64, 112, 239, 240], [0, 4, 128, 252], [0, 240]):
        check(mode=mode, first=first, rot=rot, offset=off)
        counts['vertical_limits'] += 1

    # The composite owner executes the actual native firebar path first.
    # Foreign cases retain exact OAM/application owner fields and C/V/D/I;
    # farcall return reload A can change transient N/Z before caller LDA #0.
    for ident, active, rotating, flags in itertools.product(range(0x37), [0, 0x80, 1], [0, 1], [0x35, 0x75]):
        if ident in [0x2b, 0x2c] and active == 1 and rotating:
            continue
        pair = []
        for b in [old, new]:
            m = Machine(b)
            m.setup(ident=ident, active=active, rotating=rotating)
            regs = m.call('WorldFirebarDrawAdmission', x=3, y=7, p=flags)
            pair.append((regs[:3], regs[3]&0x7d, sprites(m), m.get('CurrentOAMOffset'),
                         m.get('CurrentBankC'), m.get('FirebarSlot'), m.m.banks.copy()))
        assert pair[0] == pair[1], (ident, active, rotating, flags, pair)
        counts['negative_admission'] += 1
    for ident, slot, rot, offset in itertools.product(range(0x1b, 0x23), [0, 3], range(0, 256, 4), [0, 240]):
        pair = []
        for b in [old, new]:
            m = Machine(b)
            m.setup(slot=slot, ident=ident, rotation=rot, offset=offset)
            m.put('FirebarPartCount', 2, slot)
            for i in range(2):
                m.put('FirebarPartX', 100+i*8, slot*12+i)
                m.put('FirebarPartY', 112, slot*12+i)
            regs = m.call('WorldFirebarDrawAdmission')
            pair.append((regs[:3], regs[3]&0x7d, sprites(m), m.get('CurrentOAMOffset'),
                         m.get('CurrentBankC'), m.get('FirebarSlot'), m.m.banks.copy()))
        assert pair[0] == pair[1], (ident, slot, rot, offset, pair)
        counts['native_firebars'] += 1
    counts['source_geometry'] = len(controls)
    proof = dict(passed=True, adopted=False, goal_complete=False,
                 ROM_sha256=hashlib.sha256(new['raw']).hexdigest(),
                 parent_ROM_sha256=hashlib.sha256(old['raw']).hexdigest(), cases=counts,
                 scope='Actual late renderer and original direct native small-lift row control; all64 rotations, slots0..5, both lift IDs, source worlds2/5 and vanilla +128 second rows, native horizontal column masks, vertical clipping and capacity rejection. Exact helper A/X/Y/P, restored shared scratch/Cbank. Actual native world-firebar OAM and owner outputs remain exact for tested foreign cases; outer farcall transient N/Z excluded because the caller immediately loads0. No interrupts, native PPU or frame-timing claim.')
    a.output.write_text(json.dumps(proof, indent=2))
    print(json.dumps(proof), flush=True)


if __name__ == '__main__':
    main()
