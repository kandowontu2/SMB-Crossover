"""Source-only Mini and Karnov manual vertical platform qualification."""

import argparse
from collections import Counter
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import subprocess
import tempfile

import check_mini_lift_retention_1110_v1 as L
from check_mini_funded_actor_1108_v3 import install, run, slim_fork
from check_mini_lift_admission_async_1108_v1 import clone, final, live, tags
from check_mini_shared_offscreen_irq_1110_v1 import lag_pcs
from check_mini_visibility_dispatch_1110_v1 import memory
from check_native_relative_offscreen_irq_1110 import StackGuard
from measure_mini_kernel_transport_1109 import compile_source, replace_one


R = L.R
BASE = R / 'build/mega-giant-current-native-1110/candidate.nes'
PIN = '94650fbc11ede25b9d08e579bdc6b1d6da81fca8f29c6b0c25dadad2e685ede1'
OUT = R / 'build/manual-vertical-platform-1110'
SOURCE = R / 'tools/reference/manual_vertical_platform_1110.s'
MINI_SOURCE = R / 'tools/reference/mini_manual_vertical_platform_1110.inc'
KARNOV_SOURCE = R / 'tools/reference/karnov_manual_vertical_platform_1110.s'
MINI = R / 'build/mini-native-injury-status-fix-1110/kernel.s'
KARNOV = R / 'build/karnov-native-platform-1101-v1/kr-kernel.bin'
OPTIONS = R / 'build/karnov-host-resource-base-1101-v1/kr-options.bin'
PROTOMAN = R / 'src/protoman_audio_kernel.inc'
MEGAMAN = R / 'build/generated/guest-audio/megaman3.inc'
WORKER = 0xb378
WORKER_BANK = 64
TABLE = 0xb400
KR_SPANS = (('KR_MANUAL_INGRESS', 0xbfcb, 21), ('KR_MANUAL_RESET', 0xddf7, 9),
            ('KR_MANUAL_OPTIONS', WORKER, TABLE - WORKER))
KR_CODE = 1048592 + 399 * 1024
KR_OPTIONS = 1048592 + 1021 * 1024
KR_COOKIE = 0x3bad5
N = L.N
SLOT_FIELDS = ('Enemy_Flag', 'Enemy_ID', 'Enemy_State', 'Enemy_X_Position',
               'Enemy_PageLoc', 'Enemy_Y_Position', 'Enemy_Y_HighPos',
               'Enemy_BoundBoxCtrl', 'FloateyNum_Control', 'EnemyMetasprite')
PLAYER_FIELDS = ('Player_X_Position', 'Player_PageLoc', 'Player_Y_Position', 'Player_State')
INPUT = dict(neutral=0, up=8, select=0x20, chord=0x28, right=1)


def at(bank, cpu):
    return 16 + bank * 8192 + (cpu & 8191)


def link(work, source, spans):
    cfg, obj, binary, labels = (work / f'worker.{ext}' for ext in ('cfg', 'o', 'bin', 'lbl'))
    memories = ''.join(f'M{i}:start=${pc:04x},size=${size:04x},file=%O;'
                       for i, (_, pc, size) in enumerate(spans))
    segments = ''.join(f'{segment}:load=M{i},type=ro;' for i, (segment, _, _) in enumerate(spans))
    cfg.write_text(f'MEMORY {{ {memories} }} SEGMENTS {{ {segments} }}', encoding='utf-8')
    cc = R / 'tools/Windows/cc65/bin'
    subprocess.run([cc / 'ca65.exe', source, '-o', obj], check=True)
    subprocess.run([cc / 'ld65.exe', '-C', cfg, obj, '-o', binary, '-Ln', labels], check=True)
    syms = {}
    for row in labels.read_text().splitlines():
        _, value, name = row.split()
        syms[name.removeprefix('.')] = int(value, 16)
    return binary.read_bytes(), syms


def assert_padding(base, bank, source):
    token = '_fractionOverflowMask: .byte $40\n.endproc\n.align $100\n_fractionTrailingZeros:'
    assert source.read_text().count(token) == 1
    assert base[at(bank, WORKER - 1)] == 0x40
    assert base[at(bank, WORKER):at(bank, TABLE)] == b'\xff' * (TABLE - WORKER)
    counts = bytes(0 if n == 0 else (n & -n).bit_length() - 1 for n in range(256))
    assert base[at(bank, TABLE):at(bank, TABLE) + 256] == counts
    assert base[at(bank, WORKER - 16):at(bank, WORKER)] == bytes.fromhex(
        'a86885c368aa98a0001860a00084c2186040')[-16:]


def mini_source(source):
    edits = [
        ('    .res $8c5-(*-MiniStep),$ea\nMiniWorldEnd:',
         MINI_SOURCE.read_text() + '\n    .res $8c5-(*-MiniStep),$ea\nMiniWorldEnd:'),
        ('    .res $7b-(*-MiniNativeTile),$ea\nMiniNativeTileEnd:', '''MiniManualHigh:
    lda #>$b378
    sta MiniNativeTarget+2
    jmp MiniManualFar
    .res $7b-(*-MiniNativeTile),$ea
MiniNativeTileEnd:'''),
        (' lda SavedJoypadBits\n sta MiniHeld\n jsr MiniStep',
         ' jsr MiniManualInput\n sta MiniAssistState\n jsr MiniStep'),
        ('    .res 6,$ea\n\n; Mini\'s downward source sweep', '''MiniManualFar:
    lda #$c0
    jmp MiniFarCall

; Mini's downward source sweep'''),
        ('MiniPlatformFloor:\n    ldx MiniLiftActor',
         'MiniPlatformFloor:\n    lda MiniAssistState\n    bne @collision\n    ldx MiniLiftActor'),
        ('    lda nocollide\n    bne @miss\n    jsr MiniHostPixelX',
         '@collision:\n    lda nocollide\n    bne @miss\n    jsr MiniHostPixelX'),
        ('    lda $1f,x                ; Only the constructor\'s Mini marker.\n    cmp #$40',
         '    lda $1f,x\n    and #$fe                 ; Authored $40 or manual $41, never native $00.\n    cmp #$40'),
        ('''MiniHostPixelX:
 lda MiniX
 sta MiniCoord
 lda MiniX+1
 jmp MiniToPixel
MiniHostPixelY:
 lda MiniY
 sta MiniCoord
 lda MiniY+1
 jmp MiniToPixel

 .res 1,$ea''', '''MiniHostPixelX:
 ldx #0
 beq MiniHostPixelAxis
MiniHostPixelY:
 ldx #2
MiniHostPixelAxis:
 lda MiniX,x
 sta MiniCoord
 lda MiniX+1,x
 jmp MiniToPixel'''),
    ]
    for before, after in edits:
        source = replace_one(source, before, after)
    return source


def build(base, out):
    assert L.M.sha(base) == PIN
    assert_padding(base, WORKER_BANK, PROTOMAN)
    assert_padding(base, 11, MEGAMAN)
    bank = base[at(11, 0xa000):at(11, 0xa000) + 8192]
    assert sha256(bank).hexdigest() == '44ecf7ce03d13850d75ba8c7bafb9990c5700638c76d4abb81a6ac2ef49a28b7'
    patches = []
    with tempfile.TemporaryDirectory(prefix='link-', dir=out) as name:
        work = Path(name)
        worker, labels = link(work, SOURCE, (('MANUAL', WORKER, TABLE - WORKER),))
        assert labels['ManualPlatformCreated'] == 0xb3f7
        patches.append(L.patch(base, at(WORKER_BANK, WORKER), worker,
                               'One native ID25 constructor in exact ProtoMan alignment padding'))
        old_source = MINI.read_text()
        old, old_labels = compile_source(work, old_source, L.CONFIG)
        mini, mini_labels = compile_source(work, mini_source(old_source), L.CONFIG)
        assert old == MINI.with_suffix('.bin').read_bytes() == base[L.CODE:L.CODE + 5120]
        assert len(mini) == len(old) == 5120
        assert old_labels == {k:v for k,v in mini_labels.items() if k in old_labels}
        patches.append(L.patch(base, L.CODE, mini, 'Existing five Mini source code pages'))
        assert base[L.COOKIE:L.COOKIE + 16] == bytes([167,41,1]) + sha256(
            base[L.CODE:L.CODE + 7168]).digest()[:13]
        patches.append(L.patch(base, L.COOKIE + 3, sha256(mini + base[L.CODE + 5120:L.CODE + 7168]).digest()[:13],
                               'Exact Mini payload cookie'))

        code, kr_labels = link(work, KARNOV_SOURCE, KR_SPANS)
        orig = KARNOV.read_bytes()
        options = OPTIONS.read_bytes()
        assert base[KR_CODE:KR_CODE + 8192] == orig and len(orig) == 8192
        assert base[KR_OPTIONS:KR_OPTIONS + 2048] == options and len(options) == 2048
        pos = 0
        for label, (_, pc, capacity), offset in zip(
                ('KrManualIngress', 'KrManualReset', 'KrManualOptions'), KR_SPANS,
                (KR_CODE + 0x1fcb, KR_OPTIONS + 0x7f7, at(11, WORKER)), strict=True):
            assert kr_labels[label] == pc
            count = kr_labels[label + 'End'] - pc
            assert 0 < count <= capacity and base[offset:offset + count] == b'\xff' * count
            patches.append(L.patch(base, offset, code[pos:pos + count], label))
            pos += count
        assert pos == len(code)
        for pc, pre, entry in ((0xb1fa, '20f8db', 'KrManualIngress'),
                               (0xb0b3, '8d00c8', 'KrManualReset')):
            offset = KR_CODE + pc - 0xa000
            assert base[offset:offset + 3] == bytes.fromhex(pre)
            replacement = b'\x20' + kr_labels[entry].to_bytes(2, 'little')
            patches.append(L.patch(base, offset, replacement, entry + ' call'))
        half = install(base, patches)
        old_cookie = orig[0x1fe0:0x1ff0]
        assert old_cookie[:4] == b'\xa7\x07\x01\x10' and base[KR_COOKIE:KR_COOKIE + 16] == old_cookie
        new_cookie = old_cookie[:4] + sha256(half[KR_CODE:KR_CODE + 0x1fe0]).digest()[:12]
        for offset in (KR_COOKIE, KR_CODE + 0x1fe0):
            patches.append(L.patch(base, offset, new_cookie, 'Matching Karnov kernel cookie'))
    return install(base, patches), patches, labels | mini_labels | kr_labels


def bundles(base, candidate):
    pair = L.bundles(base, candidate)
    for b in pair:
        b['segs']['manual_platform'] = dict(start=str(WORKER), ooffs=str(at(WORKER_BANK, WORKER)))
        b['syms']['ManualPlatform'] = dict(val=str(WORKER), seg='manual_platform')
    return pair


def fields(bus, names, slot=0):
    return tuple(N.get(bus, field, slot) for field in names)


def actors(bus):
    return tuple(fields(bus, SLOT_FIELDS, slot) for slot in range(6))


def owned(bus):
    return [(slot, row) for slot, row in enumerate(actors(bus)) if row[:3] == (1, 0x25, 0x41)]


def world(row, low=0, high=1):
    return row[low] + 256 * row[high]


def frame(bus, held):
    epoch = (N.get(bus, 'FrameCounter') + 1) & 255
    N.put(bus, FrameCounter=epoch, SavedJoypadBits=held, SavedJoypad1Bits=held,
          NmiDisable=255, VRAM_Buffer1_Offset=0, VRAM_Buffer_AddrCtrl=0)
    tick = N.invoke(bus, 'GameCoreRoutine', a=0, x=0, y=0)
    N.consume(bus)
    return tick


def scene(bundle, owner):
    if owner == 41:
        bus = L.fixture(bundle, 0, False, False)
        assert bus.ram[2][0x300] == 2
    else:
        bus = N.fresh(bundle)
        N.put(bus, SelectedCharacter=owner, FmAlts=int(owner == 34), OperMode=1, FamilyMainCommit=1,
              DisableScreenFlag=1, Mirror_PPUMASK=0, NmiDisable=255, NumberofLives=2,
              AreaPointer=0x25, Mirror_PPUCTRL=160)
        N.invoke(bus, 'InitScreen')
        if owner == 34:
            assert bus.ram[2][0x810] == 167
        N.put(bus, DisableScreenFlag=0, Mirror_PPUMASK=30, OperMode_Task=3,
              GameEngineSubroutine=8, PlayerStatus=0, PlayerSize=1, Player_X_Position=40,
              Player_PageLoc=0, Player_Y_Position=176, Player_Y_HighPos=1, PlayerFacingDir=1,
              AreaType=1, AreaParserTaskNum=7, ScreenLeft_X_Pos=0, ScreenLeft_PageLoc=0,
              ScreenRight_X_Pos=255, ScreenRight_PageLoc=0)
        for name in ('Block_Buffer_1', 'Block_Buffer_2'):
            addr = L.M.address(bundle, name)
            bus[addr:addr + 208] = bytes(176) + bytes([0x54]) * 32
        bus[L.M.address(bundle, 'GameTimerDisplay')] = 4
    N.put(bus, NumberofLives=2)
    return bus


def set_slot(bus, slot, **fields):
    for field, value in fields.items():
        bus[L.M.address(bus.bundle, field) + slot] = value


def constructor(seed, offset):
    counts = Counter()
    for mask, mode in product(range(64), ('empty-or-full', 'replace', 'protect-authored')):
        bus = slim_fork(seed)
        px = (1, 10, 255, 256, 521, 731)[mask % 6]
        N.put(bus, Player_X_Position=px & 255, Player_PageLoc=px >> 8,
              Player_Y_Position=176, Player_Y_HighPos=1, ObjectOffset=mask % 6)
        for slot in range(6):
            set_slot(bus, slot, Enemy_Flag=int(bool(mask & (1 << slot))), Enemy_ID=6,
                     Enemy_State=0x41, FloateyNum_Control=0)
        prior = mask % 6
        want = min((slot for slot in range(6) if not mask & (1 << slot)), default=None)
        if mode != 'empty-or-full':
            set_slot(bus, prior, Enemy_Flag=1, Enemy_ID=0x25, Enemy_State=0x41)
            if mode == 'replace':
                want = prior
            else:
                bus[0x73ae + prior] = 1
                want = min((slot for slot in range(6) if slot != prior and not mask & (1 << slot)),
                           default=None)
        before = actors(bus)
        mapping = tuple(bus.rawtags)
        result = N.invoke(bus, 'ManualPlatform', y=(-offset) & 255)
        after = actors(bus)
        assert tuple(bus.rawtags) == mapping and N.get(bus, 'ObjectOffset') == prior
        if want is None:
            assert result['A'] == 0x80 and before == after
        else:
            left = max(0, px - offset)
            assert result['A'] == want + 1 and after[want][:8] == (
                1, 0x25, 0x41, left & 255, left >> 8, 208, 1, 5), (mask, mode, want, result, after)
            assert all(a == b for slot, (a, b) in enumerate(zip(before, after, strict=True)) if slot != want)
        counts[mode] += 1
    for area, world_number, parser_offset in ((1, 1, 23), (1, 6, 23), (3, 5, 14)):
        bus = slim_fork(seed)
        N.put(bus, AreaAddrsLOffset=area, WorldNumber=world_number, EnemyDataOffset=parser_offset,
              AreaType=int(area == 3), Player_Y_Position=173, Player_Y_HighPos=1)
        result = N.invoke(bus, 'ManualPlatform', y=(-offset) & 255)
        assert result['A'] in range(1, 7) and owned(bus)[0][1][5] == 205
        assert N.get(bus, 'EnemyDataOffset') == parser_offset
        counts['parser_scope_exceptions'] += 1
    return dict(counts)


def controls(seed, owner, offset):
    bus = slim_fork(seed)
    births = []
    cpu = N.NesMPU

    class Trace(cpu):
        def step(self):
            if self.pc == 0xb3f7 and self.memory.rawtags[1] == 0xc0:
                mem = self.memory
                slot = self.x
                birth = fields(mem, SLOT_FIELDS, slot)
                player = fields(mem, PLAYER_FIELDS)
                assert birth[:3] == (1, 0x25, 0x41) and birth[7] == 5
                assert world(birth, 3, 4) == max(0, world(player) - offset)
                assert birth[5] == player[2] + 32, (owner, birth, player)
                births.append(dict(slot=slot, left=world(birth, 3, 4), top=birth[5],
                                   player_x=world(player), player_native_y=player[2]))
            return cpu.step(self)

    N.NesMPU = Trace
    try:
        if owner == 34:
            bus.ram[2][0x8f] = 0x89     # All three supported options, no stock mutation.
            bus.ram[2][0x8e] = 0xff
        for held in (INPUT['neutral'], INPUT['select'], INPUT['neutral'], INPUT['up']):
            frame(bus, held)
            assert not births and not owned(bus)
        if owner == 34:
            assert bus.ram[2][0x8e] == 0  # Ordinary Select still changes option.
        initial = fields(bus, PLAYER_FIELDS)
        samples = []
        for _ in range(64):
            frame(bus, INPUT['chord'])  # Up then Select.
            active = owned(bus)
            assert len(active) == len(births) == 1, (owner, active, births)
            player = fields(bus, PLAYER_FIELDS)
            support = bus.ram[2][0x30d] if owner == 41 else N.get(bus, 'PlatformCollisionFlag', active[0][0])
            samples.append((active[0][1][5], player[2], player[3], support))
        assert max(row[0] for row in samples)-min(row[0] for row in samples) >= 4, (owner, samples)
        carries = sum(y < initial[2] - 3 and abs(top - y - 32) <= 1
                      and (support == active[0][0] + 1 if owner == 41 else support < 128)
                      for top, y, _, support in samples)
        assert carries >= 4, (owner, initial, samples)
        if owner == 34:
            assert bus.ram[2][0x8e] == 0  # Chord must not cycle the selected option.
        for age in range(40):
            frame(bus, INPUT['right'] | (0x80 if owner == 34 and age < 8 else 0))
            if world(fields(bus, PLAYER_FIELDS)) >= births[0]['player_x'] + 10:
                break
        frame(bus, INPUT['neutral'])
        frame(bus, INPUT['select'])
        assert len(births) == 1
        for _ in range(9):
            frame(bus, INPUT['chord'])  # Select then Up.
            assert len(owned(bus)) == 1 and len(births) == 2
        assert births[1]['slot'] == births[0]['slot'] and births[1]['left'] > births[0]['left'] + 7, (
            owner, births, fields(bus, PLAYER_FIELDS))
    finally:
        N.NesMPU = cpu
    return dict(births=births, carry_samples=carries, y_range=[min(row[1] for row in samples),
                max(row[1] for row in samples)], platform_range=[min(row[0] for row in samples),
                max(row[0] for row in samples)])


def pressure_and_reset(seed, owner, offset):
    bus = slim_fork(seed)
    pending = 0x30e if owner == 41 else 0x866
    for slot in range(6):
        set_slot(bus, slot, Enemy_Flag=1, Enemy_ID=0x23, Enemy_State=0,
                 Enemy_X_Position=220, Enemy_PageLoc=0, Enemy_Y_Position=160, Enemy_Y_HighPos=1)
    # Deliberately use an existing real authored actor, never a fake copy of
    # the manual marker. Put it far from the player's support position.
    set_slot(bus, 5, Enemy_ID=0x25, Enemy_State=0x40, Enemy_X_Position=210,
             Enemy_BoundBoxCtrl=5)
    frame(bus, INPUT['chord'])
    assert bus.ram[2][pending] == 0x80 and not owned(bus)
    assert fields(bus, SLOT_FIELDS, 5)[:3] == (1,0x25,0x40)
    for _ in range(14):
        frame(bus, INPUT['right'])
        assert bus.ram[2][pending] == 0x80 and not owned(bus)
    current = world(fields(bus, PLAYER_FIELDS))
    assert current > 40, (owner, current)
    N.invoke(bus, 'EraseEnemyObject', x=2)
    frame(bus, INPUT['neutral'])
    [(slot, result)] = owned(bus)
    assert slot == 2 and world(result, 3, 4) == current - offset
    assert fields(bus, SLOT_FIELDS, 5)[:3] == (1,0x25,0x40)
    # Native area initialization clears the slot pool; owner Fresh clears
    # even a pending chord on both new-life and same-life scene paths.
    bus.ram[2][pending] = 0x80
    N.put(bus, AreaPointer=0x26, LevelNumber=1, OperMode_Task=0, GameEngineSubroutine=0,
          FamilyMainCommit=1, DisableScreenFlag=1, Mirror_PPUMASK=0, NmiDisable=255)
    N.invoke(bus, 'InitializeArea')
    assert not owned(bus) and all(not actor[0] for actor in actors(bus))
    N.invoke(bus, 'InitScreen')
    assert bus.ram[2][pending] == 0x00
    return dict(queued_full_pool=True, retry_after_release=True, admitted_at_player_x=current,
                live_authored_slot_preserved=5, next_area_all_slots_cleared=True, next_area_pending_cleared=True)


def regular_parity(seeds, owner, base, candidate):
    changed_mini = [i for i in range(5120) if base[L.CODE + i] != candidate[L.CODE + i]]

    def canonical(bus):
        row = list(memory(bus))
        mapped = list(row[5])
        if owner in (34,41):
            code = bytearray(mapped[3])
            if owner == 41:
                for i in changed_mini:
                    code[i] = 0
            if owner == 34:
                for a,b in ((0x10b3,0x10b6),(0x11fa,0x11fd),(0x1fcb,0x1fdd)):
                    code[a:b] = bytes(b-a)
            code[0x1fe0:0x1ff0] = bytes(16)
            mapped[3] = bytes(code)
            state = bytearray(mapped[2])
            if owner == 34:
                state[0x1df7:0x1dfe] = bytes(7)
            state[0x1fe0:0x1ff0] = bytes(16)
            mapped[2] = bytes(state)
            row[5] = tuple(mapped)
        return row
    cycles = Counter()
    for held in (0,)*12+(1,)*16+(0,)*12+(0x20,0,8,0):
        a,b = [frame(bus, held) for bus in seeds]
        first, second = map(canonical, seeds)
        assert first == second, (owner, held, [i for i, (x,y) in enumerate(zip(first,second)) if x != y])
        assert all(a[key] == b[key] for key in 'AXYP')
        cycles[b['CPU']-a['CPU']] += 1
    return dict(updates=sum(cycles.values()), native_CPU_overhead=dict(cycles))


def vectors(bundle, labels):
    original_bus = N.Bus
    N.Bus = StackGuard
    try:
        seeds = {owner:scene(bundle, owner) for owner in (41,34)}
    finally:
        N.Bus = original_bus
    idle = L.M.address(bundle, 'IdleLoop')
    loop = L.M.address(bundle, 'GameLoop')
    core = L.M.address(bundle, 'GameCoreRoutine')
    stop = lambda c:(c.pc,c.sp) == (idle + 12, 252)
    counts, results = Counter(), {}
    deepest = {}
    min_sp = 255
    windows = {bytes.fromhex('8d45018d1551'):(1, 'CurrentBank'),
               bytes.fromhex('8da17d8d1651'):(2, 'CurrentBankC')}

    def one(c, kind, owner, lag, regular):
        nonlocal min_sp
        z = clone(c)
        m = z.memory
        before, entry = live(z), (z.pc,z.sp)
        original_skip = N.get(m,'NmiSkipped')
        m.vector_floor,m.written_stack = 0x100+z.sp,set()
        if kind == 'lag_FF':
            assert N.get(m,'NmiDisable') == 255
            z.nmi()
        else:
            assert not z.p & 4
            z.irq()
            assert (tags(z),z.pc) == (254,0x8000)
        lag_hits = 0

        def watch(q):
            nonlocal min_sp, lag_hits
            min_sp = min(min_sp,q.sp)
            if kind != 'lag_FF':
                return
            assert q.pc != regular
            lag_hits += int(q.pc == lag)
            key = owner,tags(q),q.pc
            if not q.p & 4 and (key not in deepest or q.sp < deepest[key].sp):
                deepest[key] = clone(q)
                deepest[key].memory.vector_floor = None

        run(z,lambda q:(q.pc,q.sp) == entry,watch)
        m.vector_floor = None
        after = live(z)
        if after[1] != before[1]:
            insn = bytes(m[z.pc - 3:z.pc + 3])
            assert kind == 'lag_FF' and insn in windows, (kind,owner,entry,insn.hex(),before[1],after[1])
            window, field = windows[insn]
            assert after[1][window] == N.get(m,field) == z.a
            assert after[1][:window] + after[1][window+1:] == before[1][:window] + before[1][window+1:]
            after = (after[0], before[1], *after[2:])
        assert after == before, (kind, owner, entry)
        assert lag_hits == int(kind == 'lag_FF')
        assert N.get(m,'NmiSkipped') == (original_skip + int(kind == 'lag_FF')) & 255
        assert not any(address in (0x4014,0x2007) for address,_ in m.writes)
        counts[kind] += 1
        return z

    for owner, seed in seeds.items():
        for scenario in ('birth','full','replacement'):
            m = slim_fork(seed)
            N.put(m, SavedJoypadBits=0x28, SavedJoypad1Bits=0x28, NmiDisable=255)
            for slot in range(6):
                if scenario == 'full':
                    set_slot(m,slot,Enemy_Flag=1,Enemy_ID=0x23,Enemy_State=0)
            if scenario == 'replacement':
                result = N.invoke(m,'ManualPlatform',y=0xf4 if owner==41 else 0xf8)
                assert result['A'] in range(1,7) and len(owned(m))==1
            lag, regular = lag_pcs(m)
            c = N.NesMPU(memory=m, pc=idle)
            c.sp,c.p = 255,0x31
            c.stPushWord(0xe33b)
            reference = clone(c)
            run(reference,stop)
            target = final(reference)
            seen, ingress = set(), {}
            resumed = 0
            inside = False

            def cut(q):
                nonlocal inside, resumed
                tag, pc = tags(q), q.pc
                if tag == 254 and pc in (loop,core):
                    ingress[pc] = q.sp
                if tag == 3 and pc == (labels['MiniManualInput'] if owner == 41 else labels['KrManualIngress']):
                    inside = True
                if (tag,pc) == ((3,labels['MiniStep']) if owner == 41 else (2,0xdbf8)):
                    inside = False
                key = tag,pc,q.sp,q.p&4
                if not inside or key in seen:
                    return
                seen.add(key)
                kinds = ('lag_FF',) if q.p & 4 else ('lag_FF','IRQ')
                for kind in kinds:
                    trial = one(q,kind,owner,lag,regular)
                    run(trial,stop)
                    assert final(trial) == target, (owner,scenario,kind,key)
                    resumed += 1

            run(c,stop,cut)
            assert ingress == {loop:250,core:248} and seen
            assert bool(owned(m)) == (scenario != 'full') and final(c) == target
            results[f'{owner}:{scenario}'] = dict(cuts=len(seen), full_resumes=resumed)
    for (owner,_,_), c in deepest.items():
        lag,regular = lag_pcs(c.memory)
        one(c,'nested_IRQ',owner,lag,regular)
    assert counts['lag_FF'] and counts['IRQ'] and counts['nested_IRQ'] and min_sp > 0x7a
    return dict(cases=results, counts=dict(counts), minimum_handler_SP=min_sp,
                genuine_GameLoop_SP=250, genuine_GameCore_SP=248)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output', type=Path, required=True)
    cli.add_argument('--measure-fit', action='store_true')
    args = cli.parse_args()
    out = args.output.resolve()
    assert out == OUT
    base = BASE.read_bytes()
    assert L.M.sha(base) == PIN
    out.mkdir(exist_ok=True)
    candidate, patches, labels = build(base, out)
    print(dict(in_memory_SHA256=L.M.sha(candidate), patches=len(patches),
               success_PC=hex(labels['ManualPlatformCreated'])), flush=True)
    if args.measure_fit:
        return
    before, after = bundles(base, candidate)
    results = {}
    for owner, offset in ((41,12), (34,8)):
        seed = scene(after, owner)
        results[owner] = dict(constructor=constructor(seed, offset), controls=controls(seed, owner, offset),
                              pressure=pressure_and_reset(seed, owner, offset),
                              no_chord=regular_parity([scene(before,owner),scene(after,owner)],owner,base,candidate))
        print(owner, results[owner], flush=True)
    foreign = {owner:regular_parity([scene(before,owner),scene(after,owner)],owner,base,candidate)
               for owner in (0,5,25)}
    assert all(row['native_CPU_overhead'] == {0:44} for row in foreign.values())
    interrupt = vectors(after, labels)
    print('Actual IRQ/FF lag-NMI', interrupt, flush=True)
    refs = (Path(__file__), SOURCE, MINI_SOURCE, KARNOV_SOURCE, BASE, PROTOMAN, MEGAMAN, MINI,
            MINI.with_suffix('.bin'), L.CONFIG, KARNOV, OPTIONS, R/'src/object.s', R/'src/common.s',
            R/'src/crossover_helpers.s', R/'src/native_platform16_v2.s', R/'src/game.s',
            R/'src/level_tiles.s', R/'src/level_variants.s',
            R/'build/karnov-host-resource-base-1101-v1/kr-terrain.inc',
            R/'build/karnov-host-resource-base-1101-v1/kr-options-host-v8.inc')
    proof = dict(passed=True, source_CPU_only=True, ROM_written=False, Mesen_run=False,
                 parent_SHA256=PIN, expected_memory_only_SHA256=L.M.sha(candidate), patches=patches,
                 labels=labels, success_PC=labels['ManualPlatformCreated'], success_bank=WORKER_BANK,
                 native_config=dict(actor=0x25, marker=0x41, width=32, center={41:4,34:8}, top_offset=32),
                 owner_CPU=results, foreign_CPU=foreign, real_vectors=interrupt,
                 bindings={p.relative_to(R).as_posix():L.M.sha(p.read_bytes()) for p in refs})
    (out/'proof.json').write_text(json.dumps(proof, indent=2)+'\n', encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()
