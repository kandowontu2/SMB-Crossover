"""Compose original SMS Sonic's ordinary frame; no native host admission.

The reference executes donor Z80 instructions. Stage specials, rings, damage,
effects, renderer and sound driver are explicit excluded boundaries. The tile
query and both complete contact dispatchers execute normally, against a private
source-width256 map. All fixture RAM below is unallocated in the NES host.
"""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import random
import re
import subprocess

import port_sonic_post_velocity_1102_v22 as Prior

R = Path(__file__).resolve().parents[2]
OUT = R / 'build/sonic-original-composed-frame-1110'
DONOR = R / 'build/sonic-sms-original-1102-v2/out/s1.sms'
SOURCE = R / 'build/sonic-sms-post-velocity-1102-v22/component.s'
SMS_PIN = '6ad738965ece231427ee046b9905cfee470d5c01220afdd934da4673e4a2458b'
HOST = R / 'build/complete-roster-native-1110/candidate.nes'
HOST_PIN = 'c10b7d87f466bf028096bddd33b7ac2baee242870ee83ccc4eebd529af57bd7f'

EXTRA = r'''
.export OrdinaryFrame,MapController,SourceWorldQuery,LandingFrameBridge
; A8 NES input, A9 flags copy, AA..AB bored timer, AC..AD query offsets,
; AE..AF query pointer. World6000..6FFF; source tile flags7000..70FF.
MapController:
 lda #$ff
 sta $40
 lda $a8
 and #8
 beq :+
 lda $40
 and #$fe
 sta $40
:
 lda $a8
 and #4
 beq :+
 lda $40
 and #$fd
 sta $40
:
 lda $a8
 and #2
 beq :+
 lda $40
 and #$fb
 sta $40
:
 lda $a8
 and #1
 beq :+
 lda $40
 and #$f7
 sta $40
:
 lda $a8
 and #$40
 beq :+
 lda $40
 and #$ef
 sta $40
:
 lda $a8
 and #$80
 beq :+
 lda $40
 and #$df
 sta $40
:
 rts
OrdinaryFrame:
 jsr MapController
 lda #0
 sta $5e
 jsr SelectAndRoll
 ; Source4A3D..4A63 ordinary idle prelude. Water-level detection excluded.
 lda $40
 cmp #$ff
 bne ResetBored
 lda $20
 ora $21
 bne ResetBored
 lda $30
 bpl ResetBored
 inc $aa
 bne IdlePose
 inc $ab
 jmp IdlePose
ResetBored:
 lda #0
 sta $aa
 sta $ab
IdlePose:
 lda #5
 sta $31
 ; Keep ordinary bored counter below360: later bored-script branch excluded.
 lda $40
 cmp #$fe
 bne RestoreLook
 lda $20
 ora $21
 bne RestoreLook
 lda $30
 bpl RestoreLook
 lda #12
 sta $31
 lda $48
 bmi IncrementLook
 lda $47
 cmp #45
 bcs RestoreLook
IncrementLook:
 inc $47
 bne RestoreLook
 inc $48
RestoreLook:
 lda $40
 and #1
 beq AfterLook
 lda $30
 and #1
 bne AfterLook
 lda $47
 ora $48
 beq AfterLook
 lda $48
 bmi IncrementRestore
 lda $47
 bne :+
 dec $48
:
 dec $47
 jmp AfterLook
IncrementRestore:
 inc $47
 bne AfterLook
 inc $48
AfterLook:
 lda $74
 sta $43
 lda $75
 sta $44
 jsr ComposedMotionStep
 lda $43
 sta $74
 lda $44
 sta $75
 jsr PoseAfterVelocity
 jsr AnimationRead
 bcs :+
 brk
:
 jsr HardCapsAndTop
 lda $30
 sta $a9
 jsr AnimationAdvance
 jsr PositionStep
 lda $30
 and #32
 bne FrameDone
 ; The first probe is Xedge,Y+height/2. Recompute Y after X contact.
 lda #0
 sta $ac
 lda $21
 bmi :+
 lda $41
 sta $ac
:
 lda $42
 lsr
 sta $ad
 jsr SourceWorldQuery
 jsr HorizontalTerrain
 lda $41
 lsr
 sta $ac
 lda #0
 sta $ad
 lda $61
 bmi :+
 lda $42
 sta $ad
:
 jsr SourceWorldQuery
 jsr VerticalTerrain
FrameDone:
 rts
ComposedMotionStep:
 lda $30
 and #1
 beq ComposedNormalX
 jsr RollingBody
 jmp ComposedLanding
ComposedNormalX:
 jsr HorizontalBody
ComposedLanding:
 jsr LandingFrameBridge
 jmp MotionY
LandingFrameBridge:
 ; Original4B53/4B57 calls50AF afterX, before choosing rolling/normalY.
 ; Missing this call left the source airborne-roll bit set after landing.
 lda $30
 bpl LandingFrameDone
 lda $43
 sta $b2
 lda $44
 sta $b3
 lda $30
 and #$fb
 sta $30
LandingFrameDone:
 rts
SourceWorldQuery:
 ; Exact width256: base + ((Y+dy)>>5)*256 + ((X+dx)>>5).
 ; Source coordinates in this ordinary fixture remain in16 tile rows.
 clc
 lda $71
 adc $ac
 sta $ae
 lda $72
 adc #0
 sta $af
 ldx #5
:
 lsr $af
 ror $ae
 dex
 bne :-
 clc
 lda $74
 adc $ad
 sta $b0
 lda $75
 adc #0
 sta $b1
 ldx #5
:
 lsr $b1
 ror $b0
 dex
 bne :-
 lda $b0
 clc
 adc #$60
 sta $af
 ldy #0
 lda ($ae),y
 tax
 lda $7000,x
 sta $82
 rts
'''


def digest(raw):
    return sha256(raw).hexdigest()


class Z80:
    """Small instruction executor; unsupported opcodes fail closed.

    Only Z/S/C are consumed by this donor path. INC/DEC and BIT preserve C;
    16-bit ADD preserves Z/S, matching the actual Z80 branches in this path.
    """
    def __init__(self, memory):
        self.m = memory
        self.r = dict.fromkeys('bcdehl', 0)
        self.alt = self.r.copy()
        self.a = 0
        self.ix = 0xd3fc
        self.iy = 0xd200
        self.pc = 0x4928
        self.z = self.s = self.carry = False
        self.stack = [0x32e2]
        self.sound = 0
        self.sprite = 0
        self.physics = None
        self.queries = []
        self.visits = Counter()
        self.excluded = Counter()

    def word(self, at):
        return self.m[at] | self.m[(at + 1) & 65535] << 8

    def putword(self, at, value):
        self.m[at] = value & 255
        self.m[(at + 1) & 65535] = value >> 8 & 255

    def pair(self, name):
        return self.r[name[1]] | self.r[name[0]] << 8

    def setpair(self, name, value):
        self.r[name[1]], self.r[name[0]] = value & 255, value >> 8 & 255

    def byte(self):
        value = self.m[self.pc]
        self.pc = (self.pc + 1) & 65535
        return value

    def immword(self):
        return self.byte() | self.byte() << 8

    def cond(self, n):
        return (not self.z, self.z, not self.carry, self.carry,
                False, True, not self.s, self.s)[n]

    def flags(self, value):
        self.z, self.s = value & 255 == 0, bool(value & 128)

    def getreg(self, n):
        return self.a if n == 7 else self.m[self.pair('hl')] if n == 6 else self.r['bcdehl'[n]]

    def setreg(self, n, value):
        value &= 255
        if n == 7:
            self.a = value
        elif n == 6:
            self.m[self.pair('hl')] = value
        else:
            self.r['bcdehl'[n]] = value

    def alu(self, n, value):
        old = self.a
        if n in (0, 1):
            result = old + value + (int(self.carry) if n == 1 else 0)
            self.carry = result > 255
        elif n in (2, 3, 7):
            result = old - value - (int(self.carry) if n == 3 else 0)
            self.carry = result < 0
        else:
            result = (old & value, old ^ value, old | value)[n - 4]
            self.carry = False
        self.flags(result)
        if n != 7:
            self.a = result & 255

    def step(self):
        at = self.pc
        self.visits[at] += 1
        if at == 0x49d9:
            self.physics = list(self.m[0xd20e:0xd217]) + list(self.m[0xd240:0xd246])
        # Explicit external boundaries; none substitute movement/contact code.
        skips = {0x49e7: (0x4a3d, 'tile_special_and_death_limit'),
                 0x4c28: (0x4c56, 'ring_damage_brake_audio'),
                 0x4c83: (0x4ccb, 'sprite_pointer_and_renderer'),
                 0x4d05: (0x4d21, 'bubbles_sparkles_effects')}
        if at in skips:
            self.pc, name = skips[at]
            self.excluded[name] += 1
            if at == 0x4c83:
                self.sprite = self.a
            return
        if at == 0x36f9:
            self.queries.append(((self.word(0xd3fe) + self.pair('bc')) & 65535,
                                 (self.word(0xd401) + self.pair('de')) & 65535))
        op = self.byte()
        if op in (0xdd, 0xfd):
            base = self.ix if op == 0xdd else self.iy
            sub = self.byte()
            off = self.byte()
            addr = (base + (off if off < 128 else off - 256)) & 65535
            if sub == 0xcb:
                bitop = self.byte()
                group, bit = bitop >> 6, bitop >> 3 & 7
                value = self.m[addr]
                if group == 1:
                    self.z = not value & (1 << bit)
                    self.s = bit == 7 and not self.z
                elif group == 2:
                    self.m[addr] = value & (255 ^ (1 << bit))
                elif group == 3:
                    self.m[addr] = value | (1 << bit)
                else:
                    raise AssertionError(('indexedCB', hex(at), hex(bitop)))
            elif sub == 0x36:
                self.m[addr] = self.byte()
            elif sub in (0x34, 0x35):
                self.m[addr] = (self.m[addr] + (1 if sub == 0x34 else -1)) & 255
                self.flags(self.m[addr])
            elif sub & 0xc7 == 0x46:
                self.setreg(sub >> 3 & 7, self.m[addr])
            elif 0x70 <= sub <= 0x77 and sub != 0x76:
                self.m[addr] = self.getreg(sub & 7)
            elif 0x80 <= sub <= 0xbf and sub & 7 == 6:
                self.alu(sub >> 3 & 7, self.m[addr])
            else:
                raise AssertionError(('indexed', hex(at), hex(sub)))
        elif op == 0xcb:
            sub = self.byte()
            value = self.getreg(sub & 7)
            group, bit = sub >> 6, sub >> 3 & 7
            if group == 1:
                self.z = not value & (1 << bit)
                self.s = bit == 7 and not self.z
            elif group == 0:
                oldcarry = self.carry
                if bit == 2:
                    self.carry = bool(value & 128)
                    result = (value << 1 | int(oldcarry)) & 255
                elif bit == 3:
                    self.carry = bool(value & 1)
                    result = value >> 1 | int(oldcarry) << 7
                elif bit == 7:
                    self.carry = bool(value & 1)
                    result = value >> 1
                else:
                    raise AssertionError(('CBshift', hex(at), hex(sub)))
                self.setreg(sub & 7, result)
                self.flags(result)
            else:
                self.setreg(sub & 7, value & ~(1 << bit) if group == 2 else value | (1 << bit))
        elif op == 0xed:
            sub = self.byte()
            if sub == 0xb0:
                for _ in range(self.pair('bc')):
                    self.m[self.pair('de')] = self.m[self.pair('hl')]
                    self.setpair('de', self.pair('de') + 1)
                    self.setpair('hl', self.pair('hl') + 1)
                self.setpair('bc', 0)
            elif sub in (0x43, 0x53, 0x63, 0x4b, 0x5b, 0x6b):
                addr = self.immword()
                pair = ('bc', 'de', 'hl')[(sub >> 4) - 4]
                if sub & 8:
                    self.setpair(pair, self.word(addr))
                else:
                    self.putword(addr, self.pair(pair))
            elif sub in (0x42, 0x52, 0x62):
                pair = ('bc', 'de', 'hl')[(sub >> 4) - 4]
                result = self.pair('hl') - self.pair(pair) - int(self.carry)
                self.carry = result < 0
                self.setpair('hl', result)
                self.z, self.s = result & 65535 == 0, bool(result & 32768)
            elif sub == 0x44:
                old = self.a
                self.a = -old & 255
                self.flags(self.a)
                self.carry = old != 0
            else:
                raise AssertionError(('ED', hex(at), hex(sub)))
        elif 0x40 <= op <= 0x7f and op != 0x76:
            self.setreg(op >> 3 & 7, self.getreg(op & 7))
        elif 0x80 <= op <= 0xbf:
            self.alu(op >> 3 & 7, self.getreg(op & 7))
        elif op & 0xc7 == 0xc6:
            self.alu(op >> 3 & 7, self.byte())
        elif op & 0xc7 == 0x06:
            self.setreg(op >> 3 & 7, self.byte())
        elif op & 0xc7 in (0x04, 0x05):
            reg = op >> 3 & 7
            value = (self.getreg(reg) + (1 if op & 7 == 4 else -1)) & 255
            self.setreg(reg, value)
            self.flags(value)
        elif op in (0x01, 0x11, 0x21):
            self.setpair(('bc', 'de', 'hl')[op >> 4], self.immword())
        elif op in (0x03, 0x13, 0x23, 0x0b, 0x1b, 0x2b):
            pair = ('bc', 'de', 'hl')[op >> 4]
            self.setpair(pair, self.pair(pair) + (1 if op & 15 == 3 else -1))
        elif op in (0x09, 0x19, 0x29):
            result = self.pair('hl') + self.pair(('bc', 'de', 'hl')[op >> 4])
            self.setpair('hl', result)
            self.carry = result > 65535
        elif op in (0x22, 0x2a):
            addr = self.immword()
            if op == 0x22:
                self.putword(addr, self.pair('hl'))
            else:
                self.setpair('hl', self.word(addr))
        elif op in (0x32, 0x3a):
            addr = self.immword()
            if op == 0x32:
                self.m[addr] = self.a
            else:
                self.a = self.m[addr]
        elif op in (0xc3, 0xc2, 0xca, 0xd2, 0xda, 0xf2, 0xfa):
            dest = self.immword()
            if op == 0xc3 or self.cond(op >> 3 & 7):
                self.pc = dest
        elif op in (0x18, 0x20, 0x28, 0x30, 0x38):
            off = self.byte()
            if op == 0x18 or self.cond((op - 0x20) >> 3):
                self.pc = (self.pc + (off if off < 128 else off - 256)) & 65535
        elif op in (0xcd, 0xc4, 0xcc, 0xd4, 0xdc):
            dest = self.immword()
            if op == 0xcd or self.cond(op >> 3 & 7):
                self.stack.append(self.pc)
                self.pc = dest
        elif op in (0xc9, 0xc0, 0xc8, 0xd0, 0xd8):
            if op == 0xc9 or self.cond(op >> 3 & 7):
                self.pc = self.stack.pop()
        elif op in (0xc5, 0xd5, 0xe5):
            self.stack.append(self.pair(('bc', 'de', 'hl')[(op >> 4) - 12]))
        elif op in (0xc1, 0xd1, 0xe1):
            self.setpair(('bc', 'de', 'hl')[(op >> 4) - 12], self.stack.pop())
        elif op == 0xd9:
            self.r, self.alt = self.alt, self.r
        elif op == 0xeb:
            a, b = self.pair('de'), self.pair('hl')
            self.setpair('de', b)
            self.setpair('hl', a)
        elif op == 0x07:
            self.carry = bool(self.a & 128)
            self.a = (self.a << 1 | int(self.carry)) & 255
        elif op == 0x2f:
            self.a ^= 255
        elif op == 0xef:
            self.sound = self.a if self.a else 1  # existing fixture reserves zero for no event
        else:
            raise AssertionError(('opcode', hex(at), hex(op)))

    def run(self):
        for _ in range(1600):
            if self.pc == 0x34e6:
                assert not self.stack, self.stack
                assert len(self.queries) in (0, 2)
                return self
            self.step()
        raise AssertionError(('Z80 bound', hex(self.pc)))


def sms_input(nes):
    held = ((nes >> 3 & 1) | (nes >> 1 & 2) | (nes << 1 & 4) |
            (nes << 3 & 8) | (nes >> 2 & 16) | (nes >> 2 & 32))
    return 255 ^ held


def labels(path):
    return {line.split()[2].lstrip('.'): int(line.split()[1], 16)
            for line in path.read_text().splitlines()}


def host_constraints(raw):
    # Actual current routing, not inferred from older debug-symbol targets.
    sites = [(1, 0xa5d7, 'ad0260d0128d6a01a9be8d6c01a9bf8d6d01a9c94c5a01'),
             (73, 0xbfbe, '08488d6a01a9b08d6c01a9bf8d6d01a99c205a019015'),
             (62, 0xb902, '0848ad0260d00bad0a73c905f018c906f014'),
             (81, 0xbbf1, 'ad0260d00aad0a73c904d0034c72bc')]
    rows = []
    for bank, pc, expected in sites:
        at = 16 + bank * 8192 + (pc & 8191)
        wanted = bytes.fromhex(expected)
        assert raw[at:at + len(wanted)] == wanted, (bank, hex(pc), raw[at:at+len(wanted)].hex())
        rows.append(dict(physical_PRG=bank, PC=pc, file_offset=at, bytes=wanted.hex()))
    return rows


def main():
    rom = DONOR.read_bytes()
    host = HOST.read_bytes()
    assert digest(rom) == SMS_PIN and digest(host) == HOST_PIN
    constraints = host_constraints(host)
    prior_receipt = json.loads((SOURCE.parent / 'receipt.json').read_text())
    for name, wanted in prior_receipt['bindings'].items():
        assert digest(Path(name).read_bytes()) == wanted, name
    OUT.mkdir(exist_ok=True)
    asm = SOURCE.read_text() + EXTRA
    (OUT / 'component.s').write_text(asm)
    (OUT / 'component.cfg').write_text('MEMORY{ROM:start=$8000,size=$2000,file=%O;}SEGMENTS{CODE:load=ROM,type=ro;}')
    cc = R / 'tools/Windows/cc65/bin'
    for command in ([cc / 'ca65.exe', OUT / 'component.s', '-o', OUT / 'component.o'],
                    [cc / 'ld65.exe', '-C', OUT / 'component.cfg', '-Ln', OUT / 'labels.txt',
                     '-o', OUT / 'component.bin', OUT / 'component.o']):
        result = subprocess.run(list(map(str, command)), capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
    syms = labels(OUT / 'labels.txt')
    code = (OUT / 'component.bin').read_bytes()
    prior_code = (SOURCE.parent / 'component.bin').read_bytes()
    assert code[:len(prior_code)] == prior_code
    template = [0] * 65536
    template[0x8000:0x8000 + len(code)] = code
    # One source-width256 map:32-pixel cells, no copied asset output.
    rng = random.Random(1110)
    count = 0
    visits, excludes = Counter(), Counter()
    cycles = []
    evidence = Counter()
    query_digest = sha256()
    episodes = []
    negative_controls = []

    def one(nes, flags, xv, yv, xpos, ypos, height, camera, frame, prev,
            shoes, zone, tick, terrain, *, previous=None, code_override=None):
        nonlocal count
        m = template.copy()
        m[0x20:0x23] = xv.to_bytes(3, 'little')
        m[0x60:0x63] = yv.to_bytes(3, 'little')
        m[0x70:0x73] = xpos.to_bytes(3, 'little')
        m[0x73:0x76] = ypos.to_bytes(3, 'little')
        m[0x30], m[0x31], m[0x41], m[0x42] = flags, 5, 24, height
        m[0x47:0x49] = camera.to_bytes(2, 'little')
        m[0x58] = 0
        m[0x90:0x97] = [shoes, 0, tick, 255, 0, 73, 1]
        m[0xa0:0xa3] = [prev, frame, 31]
        m[0xa8] = nes
        zoneptr = int.from_bytes(rom[0x3a65+zone*2:0x3a67+zone*2], 'little')
        tileflags = rom[zoneptr:zoneptr+256]
        m[0x7000:0x7100] = tileflags
        m[0x6000:0x7000] = terrain
        original = bytearray(65536)
        original[:0x8000] = rom[:0x8000]
        original[0xc000:0xd000] = bytes(terrain)
        original[0xd3fd:0xd400] = xpos.to_bytes(3, 'little')
        original[0xd400:0xd403] = ypos.to_bytes(3, 'little')
        original[0xd403:0xd406] = xv.to_bytes(3, 'little')
        original[0xd406:0xd409] = yv.to_bytes(3, 'little')
        original[0xd409:0xd40b] = bytes((24, height))
        original[0xd40f] = frame
        original[0xd410] = 5
        original[0xd411] = shoes
        original[0xd414] = flags
        original[0xd203] = sms_input(nes)
        original[0xd206] = 2  # native level-edge clamp disabled in this fixture
        original[0xd223] = tick
        original[0xd238] = 0  # original width256 dispatch
        original[0xd2b7:0xd2b9] = camera.to_bytes(2, 'little')
        original[0xd2df:0xd2e1] = bytes((prev, 31))
        original[0xd2d4] = zone
        original[0xdc0a:0xdc0e] = bytes((73, 1, 255, 0))
        if previous is not None:
            m = previous[0].copy()
            m[0xa8] = nes
            m[0x92] = tick
            original = previous[1].m.copy()
            original[0xd203] = sms_input(nes)
            original[0xd223] = tick
        if code_override is not None:
            m[0x8000:0x8000+len(code_override)] = code_override
        reference = Z80(original).run()
        cpu = Prior.NesMPU(memory=m, pc=syms['OrdinaryFrame'])
        cpu.sp, cpu.p = 224, 0x30
        cpu.stPushWord(0x5aff)
        probes = []
        for _ in range(1600):
            if cpu.pc == 0x5b00:
                break
            if cpu.pc == syms['SourceWorldQuery']:
                probes.append(((m[0x71] | m[0x72] << 8) + m[0xac],
                               (m[0x74] | m[0x75] << 8) + m[0xad]))
            assert m[cpu.pc] != 0, ('6502BRK', hex(cpu.pc), nes, flags)
            cpu.step()
        else:
            raise AssertionError('6502 ordinary frame bound')
        assert cpu.sp == 224
        pairs = [('Xvelocity', m[0x20:0x23], list(original[0xd403:0xd406])),
                 ('Yvelocity', m[0x60:0x63], list(original[0xd406:0xd409])),
                 ('XYposition', m[0x70:0x76], list(original[0xd3fd:0xd403])),
                 ('flags_pose', m[0x30:0x32], [original[0xd414], original[0xd410]]),
                 ('body', m[0x41:0x43], list(original[0xd409:0xd40b])),
                 ('camera', m[0x47:0x49], list(original[0xd2b7:0xd2b9])),
                 ('jump_timer', m[0x58], original[0xd28e]),
                 ('bounce', m[0x63:0x66], list(original[0xd2e6:0xd2e9])),
                 ('animation', m[0xa0:0xa4], [original[0xd2df], original[0xd40f], original[0xd2e0], reference.sprite]),
                 ('shoes', m[0x90], original[0xd411]),
                 ('tempo', m[0x95:0x97], list(original[0xdc0a:0xdc0c])),
                 ('physics_parameters', [m[a] for a in [0x32,0x33,0x34,0x35,0x45,0x46,0x99,
                                                       0x5d,0x38,0x36,0x37,0x59,0x5a,0x5b,0x5c]], reference.physics),
                 ('level_roll_flags', m[0x91], original[0xd207]),
                 ('input_mapping', m[0x40], original[0xd203]),
                 ('sound_event', m[0x5e], reference.sound),
                 ('flags_copy', m[0xa9], original[0xd2b9]),
                 ('bored', m[0xaa:0xac], list(original[0xd299:0xd29b])),
                 ('last_ground_y', m[0xb2:0xb4], list(original[0xd2d9:0xd2db])),
                 ('queries', probes, reference.queries)]
        for name, actual, expected in pairs:
            if actual != expected:
                raise AssertionError((name, count, dict(nes=nes,flags=flags,xv=xv,yv=yv,xpos=xpos,ypos=ypos,
                    height=height,camera=camera,frame=frame,prev=prev,shoes=shoes,zone=zone,tick=tick), actual, expected))
        count += 1
        visits.update(reference.visits)
        excludes.update(reference.excluded)
        cycles.append(cpu.processorCycles)
        query_digest.update(json.dumps(probes, separators=(',', ':')).encode())
        for name, value in [('rolling_input', flags & 1), ('roll_after', m[0x30] & 1),
                            ('ground_after', m[0x30] & 128), ('side_contact', m[0x30] & 64),
                            ('X_velocity_changed_during_frame', m[0x20:0x23] != list(xv.to_bytes(3, 'little'))),
                            ('Y_two_queries', len(probes) == 2), ('jump_event', m[0x5e] == 1)]:
            if value:
                evidence[name] += 1
        return m, reference

    # Each zone's authentic tile index values are used. Every controller value,
    # original roll/ground/air states and both velocity signs enter this frame.
    for nes in range(256):
        for flags in (8, 10, 12, 14, 0x88, 0x8a, 0x89, 0x8b):
            zone = nes & 7
            terrain = [rng.randrange(121) for _ in range(4096)]
            xv = rng.choice([0, 0x10, 0x300, 0xfff800, 0xffff00, 0xffffff])
            yv = rng.choice([0, 0x38, 0x100, 0x800, 0xfffc80, 0xffffff])
            one(nes, flags, xv, yv, (128 << 8) | rng.randrange(256), (96 << 8) | rng.randrange(256),
                24 if flags & 1 else 32, rng.choice([0, 44, 45, 0xffb0, 0xffff]),
                0, 5, rng.choice([0, 1, 2, 255]), zone, nes, terrain)
    # Reference source metadata/source query phase and fractional boundary sweeps.
    for _ in range(2048):
        flags = rng.choice([8, 10, 12, 14, 0x88, 0x8a, 0x89, 0x8b])
        xv = rng.randrange(65536)
        yv = rng.randrange(65536)
        xv |= 0xff0000 if xv & 32768 else 0
        yv |= 0xff0000 if yv & 32768 else 0
        one(rng.randrange(256), flags, xv, yv,
            (rng.randrange(64, 640) << 8) | rng.randrange(256),
            (rng.randrange(48, 192) << 8) | rng.randrange(256),
            rng.choice([24, 32]), rng.randrange(65536), 0, rng.choice([0, 1, 5, 9, 12, 19]),
            rng.randrange(4), rng.randrange(8), rng.randrange(256),
            [rng.randrange(121) for _ in range(4096)])
    # Carry the real jump latch, animation frame, fractions, landing flags,
    # shoes phase and camera across80 consecutive updates on a source floor.
    floor = [0] * 1536 + [2] * 2560  # GHZ tile2, original flat shape16
    for direction in (1, 2):
        for initial_flags in (0x88, 0x89):
            for held in (1, 2, 8, 16, 25):
                for initial_shoes in (0, 16):
                    previous = None
                    apex = 65535
                    jumps = landings = 0
                    for update in range(80):
                        nes = direction | (128 if update < held else 0)
                        if update >= 48:
                            nes = 4 | direction  # source down-to-roll after landing
                        initial_y = 184 if initial_flags & 1 else 176
                        previous = one(nes, initial_flags, 0, 0, 512 << 8, initial_y << 8,
                                       24 if initial_flags & 1 else 32, 0, 0, 5,
                                       initial_shoes, 0, update, floor, previous=previous)
                        state = previous[0]
                        apex = min(apex, state[0x74] | state[0x75] << 8)
                        jumps += state[0x5e] == 1
                        landings += bool(state[0x30] & 128)
                    assert jumps == 1 and landings > 0, (direction, initial_flags, held, initial_shoes, jumps, landings)
                    episodes.append(dict(direction=direction, rolling_start=bool(initial_flags&1),
                                         held=held, shoes=initial_shoes, updates=80,
                                         apex_y=apex, grounded_updates=landings))

    def swap_calls(first, second):
        image = bytearray(code)
        begin = syms['OrdinaryFrame'] - 0x8000
        a = bytes((0x20, syms[first] & 255, syms[first] >> 8))
        b = bytes((0x20, syms[second] & 255, syms[second] >> 8))
        assert image[begin:].count(a) == image[begin:].count(b) == 1
        ai, bi = image.index(a, begin), image.index(b, begin)
        image[ai:ai+3], image[bi:bi+3] = b, a
        return image

    for first, second, fixture in (
            ('HardCapsAndTop', 'AnimationAdvance',
             (0, 8, 0x2000, 0x800, 128 << 8, 96 << 8, 32, 0, 0, 5, 0, 0, 0, [0]*4096)),
            ('HorizontalTerrain', 'VerticalTerrain',
             (1, 0x88, 0x300, 0x100, 128 << 8, 176 << 8, 32, 0, 0, 5, 0, 0, 0, floor))):
        try:
            one(*fixture, code_override=swap_calls(first, second))
        except AssertionError as failure:
            detail = failure.args[0]
            assert isinstance(detail, tuple) and detail[0] in {
                'Xvelocity','Yvelocity','XYposition','flags_pose','body','camera','jump_timer',
                'bounce','animation','shoes','tempo','sound_event','flags_copy','bored','queries'}, detail
            negative_controls.append(dict(swapped_calls=[first, second], first_difference=detail[0]))
        else:
            raise AssertionError(('Undetected wrong source order', first, second))
    # The newly recovered landing callback is independently required: simply
    # joining the previously verified leaves reproduces the episode33 failure.
    landing_fixture = (1, 0x8c, 0x300, 0, 512 << 8, 176 << 8, 32, 0, 0, 5, 0, 0, 0, floor)
    one(*landing_fixture)
    image = bytearray(code)
    call = bytes((0x20, syms['LandingFrameBridge'] & 255, syms['LandingFrameBridge'] >> 8))
    assert image[len(prior_code):].count(call) == 1
    target = image.index(call, len(prior_code))
    image[target:target+3] = bytes((0xea, 0xea, 0xea))
    try:
        one(*landing_fixture, code_override=image)
    except AssertionError as failure:
        detail = failure.args[0]
        assert isinstance(detail, tuple) and detail[0] == 'flags_pose', detail
        negative_controls.append(dict(omitted_call='Original50AF landing callback', first_difference=detail[0]))
    else:
        raise AssertionError('Undetected omitted source landing callback')
    assert all(visits[pc] for pc in (0x4928, 0x49d9, 0x4a82, 0x4bf5, 0x4c56, 0x4ccb,
                                    0x4d81, 0x32e2, 0x331c, 0x3349, 0x3421, 0x36f9, 0x37df))
    report = dict(passed=True, private=True, ROM_written=False, installed=False,
                  host_ROM_SHA256=HOST_PIN, original_ROM_SHA256=SMS_PIN,
                  cases=count, compiled_bytes=len(code), added_bytes=len(code)-len(prior_code),
                  cycles=[min(cycles), max(cycles)], actual_Z80_instructions=sum(visits.values()),
                  visited_source_PCs=len(visits), evidence=dict(evidence),
                  consecutive_episodes=episodes, negative_order_controls=negative_controls,
                  exclusions=dict(excludes), query_trace_SHA256=query_digest.hexdigest(),
                  host_route_preimages=constraints,
                  scope='Actual ordinary donor4928..49E7,4A3D..4C28,4C56..4C83,4CCB..4D05,'
                        '4D21..4DCB then generic32E2..34E6; original36F9..37DF width256 world queries execute. '
                        '6502 joins source physics/roll/input/camera/motor/jump/pose/precap animation/'
                        'caps/postcap animation clock/24bit integration/X contact/Y contact in source order. '
                        'NES A maps SMSbutton2; B maps SMSbutton1; Select/Start have no source action.',
                  limitations=['No native host RAM/code/carrier allocation, lifecycle or ROM mutation.',
                               'No Mesen or in-game Sonic physics improvement is claimed.',
                               'Tile specials/death limit, rings/damage/brake audio, rendering/effects, '
                               'level-edge clamping and bored-script threshold360 are excluded.',
                               'Fixture source-width256 map is not an SMB terrain adapter; source body24x32/24 remains.',
                               'No water-level detection or source upside-down mode in this ordinary-frame proof.'],
                  bindings={str(p.relative_to(R)): digest(p.read_bytes()) for p in
                            [Path(__file__), DONOR, SOURCE, SOURCE.parent/'component.bin',
                             SOURCE.parent/'receipt.json', OUT/'component.s', OUT/'component.bin', OUT/'labels.txt']})
    (OUT / 'proof.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k:report[k] for k in ('passed','cases','compiled_bytes','added_bytes','cycles',
                                           'actual_Z80_instructions','visited_source_PCs','evidence')}))


if __name__ == '__main__':
    main()
