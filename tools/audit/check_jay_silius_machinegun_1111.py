"""Check the installed Jay weapons and compare the first earned donor weapon."""

from collections import Counter
from itertools import product
import argparse
import json

import check_jay_silius_natural_ammo_1111 as Refill
import check_jay_silius_pause_ui_1111 as Pause
import check_steve_shatterhand_motion_carrier_1111 as Steve

T = Pause.T
C, H, N, W = T.C, T.H, T.N, T.W
PIN = '677aad54c55f829d9e7b2aab9e2b1f4eddebcd3c6e6532eeddd9f2ce4e1a26ab'
CANDIDATE_PIN = 'c8d328a27efbc900216985aeb86600a1f626f8cc76e93a91bb30b2c1f8c2e727'
CURRENT_COOKIE = bytes.fromhex('a710200ac5ae56e39c60ac56c337a8c7')
SOURCE = H.ROOT / 'tools/reference/jay_silius_machinegun_1111.s'
TEST_ORIGIN = 0xc100
LIVE_ORIGIN = 0xa785
TEMPLATE = 0xa88d
FLAGPOLE_MARK = 0xc0cb
RECORDS = slice(0x60, 0xb0)
DONOR_RECORDS = slice(0x3b0, 0x400)
# Decoded retired movement from exact 677aad54, A3:A785..A88D. The
# published A000..A8C0 stage repacks from this preimage byte for byte.
RETIRED_MOVEMENT = bytes.fromhex(
    'ad7107c901d06ead7307c903d067a50fc908d061ad77074ab05bad39011056ad'
    'ff5f4a9050ad06070d64070d61070d1d070d1f07055cd03deaeaeaeaeaeaad33'
    'c0d00620fca74cd5a7a50ecd34c0f023a50e8d34c0a5758d35c0ad2ac08d2bc0'
    'a5dc8d2ac02000a02067a1a2002069a3204eb138601860a232bd8da89d00c0ca'
    '10f7a5750a0a0a0a8d0bc0a5754a4a4a4a8d0ac0a5bd186910480a0a0a0a8d0d'
    'c0684a4a4a4a8d0cc0a9018d33c060ad0ac00a0a0a0a8d36c0ad0bc04a4a4a4a'
    '0d36c085758d5a0738ed35c08d0107ad0cc00a0a0a0a8d36c0ad0dc04a4a4a4a'
    '0d36c038e91085bdad0fc0a204c9806acad0fa858ead12c02904f009a901ae0f'
    'c03002a902851e60'
)


def current(raw):
    assert T.digest(raw) == PIN
    hot = C.offset(94, 0xb2ef)
    cookie = raw[hot:hot+16]
    assert cookie == CURRENT_COOKIE
    cold = Steve.cold_program(Steve.DESCRIPTOR, cookie)
    start = C.offset(65, T.COLD)
    assert raw[start:start+T.COLD_SIZE] == cold['images']['COLD65'].ljust(T.COLD_SIZE, b'\xea')
    assert raw[C.offset(65, 0xaf00):C.offset(65, 0xaf03)] == b'\x4c' + T.J.u16(cold['symbols']['JaySelect'])
    trial = dict(W.Symbols.bundle(), raw=raw)
    _, fields, aliases = T.Weapon.assemble(trial)
    constants = ''.join(f'{name}=${address:04x}\n' for name, address in aliases.items())
    alternate = H.assemble(constants + T.Weapon.SOURCE.read_text(), T.ALT_LAYOUT)
    ui = Pause.assemble(aliases, update=0xb800)
    for section in ('UI_DISPATCH', 'UI_LEGACY', 'UI_NATIVE'):
        address, size = Pause.LAYOUT[section]
        start = C.offset(86, address)
        assert raw[start:start+size] == ui['images'][section].ljust(size, b'\xea')
    carrier = T.page(raw, T.CHR_PAGE)
    for section, image in (*alternate['images'].items(), ('PAUSE_SUPPORT', ui['images']['PAUSE_SUPPORT'])):
        address = (T.ALT_LAYOUT | Pause.LAYOUT)[section][0]
        start = address - 0xb400
        assert carrier[start:start+len(image)] == image
    return trial, dict(pause=ui, alternate=alternate, fields=fields, aliases=aliases, cookie=cookie)


def refill(raw, info):
    cookie = info['cookie']
    m, trial, _ = T.Motion.parent(raw=raw, pin=T.digest(raw), cookie=cookie)
    roll, linked = Refill.Ammo.assemble()
    code, aliases = Refill.Hit.assemble(trial, native_defeat=Refill.CAPTURE)
    Refill.Hit.check_loaded(m, code)
    data = roll['images']['AMMODROP']
    assert m.ram[3][0x1700:0x1700+len(data)] == data
    native = {name: W.address(trial, address) for name, address in T.Motion.NATIVE.items()}
    bindings = dict(fields=linked['ram'], motion_fields=native)
    Refill.Hit.select_spread(m, bindings, Pause)
    approach = Refill.approach(m, bindings)
    hit = Refill.fire(m, aliases)
    pickup = Refill.collect(m, bindings, roll['symbols'])
    assert C.Common.headers(m) == (cookie,) * 2
    return dict(approach=approach, hit=hit, pickup=pickup)


def assemble(info, *, origin=TEST_ORIGIN):
    link = C.Jay.build()
    stock, _ = T.Weapon.Stock.bindings(link)
    symbols = stock['symbols'] | info['alternate']['symbols']
    constants = dict(info['aliases'], **{name: symbols[name] for name in ('FreeSlot', 'SpendAmmo', 'AlternateInput')})
    constants.update({name: info['pause']['symbols'][name] for name in ('PauseWeapons', 'ResetWeapons')})
    constants.update(SwimmingFlag=0x0706, WorldNumber=0x0764, LevelNumber=0x0761, OperMode=0x0771,
                     GameEngineSubroutine=0x000f, StageOneFlagpole=FLAGPOLE_MARK, OtherMux=0xb67f)
    text = ''.join(f'{name}=${value:04x}\n' for name, value in constants.items()) + SOURCE.read_text()
    return H.assemble(text, {'MACHINE_GUN': (origin, TEMPLATE-LIVE_ORIGIN)})


def staged(runtime):
    stage, _, sizes = T.Motion.Cold.boot_stage(runtime)
    jump = T.Motion.Cold.BOOT-0xd000
    assert stage[jump:jump+3] == bytes.fromhex('4c00d0')
    return stage[:jump] + bytes.fromhex('4c00a0') + stage[jump+3:], sizes


def proposal(raw):
    """Return the exact-current cartridge candidate and callable verification bindings."""
    trial, info = current(raw)
    seed, _, _ = T.Motion.parent(raw=raw, pin=PIN, cookie=info['cookie'])
    cache = bytes(seed.ram[3])
    start, stop = LIVE_ORIGIN-0xa000, TEMPLATE-0xa000
    assert cache[start:stop] == RETIRED_MOVEMENT
    # The shipped 1-1 movement callback jumps to B800, its projector to B8CC.
    # Preserve the decoder's template and reject any direct old-code caller.
    assert cache[0x168d:0x1690] == bytes.fromhex('4c00b8')
    assert cache[0x1151:0x1154] == bytes.fromhex('4cccb8')
    for lo, hi in ((0, start), (stop, 0x1fe0)):
        assert not [i for i in range(lo, hi-2) if cache[i] in (0x20, 0x4c, 0x6c)
                    and LIVE_ORIGIN <= int.from_bytes(cache[i+1:i+3], 'little') < TEMPLATE]

    old_stage, _ = staged(cache[:0x8c0])
    assert old_stage == T.page(raw, 331) + T.page(raw, 332)
    code = assemble(info, origin=LIVE_ORIGIN)
    symbols = code['symbols']
    payload = code['images']['MACHINE_GUN'].ljust(stop-start, b'\xea')
    stage, sizes = staged(cache[:start] + payload + cache[stop:0x8c0])
    packet = bytearray(T.page(raw, T.PACKET_PAGE))
    carrier = bytearray(T.page(raw, T.CHR_PAGE))
    motion = bytearray(T.page(raw, T.MOTION_PAGE))

    def replace(row, base, address, old, new):
        start = address-base
        assert len(old) == len(new) and row[start:start+len(old)] == old, hex(address)
        row[start:start+len(old)] = new

    def call(name):
        return b'\x20' + T.J.u16(symbols[name])

    def jump(name):
        return b'\x4c' + T.J.u16(symbols[name])

    replace(packet, 0xafc0, 0xb000, bytes.fromhex('4c00b4'), jump('MachineGunDispatch'))
    replace(packet, 0xafc0, 0xb155, b'\xd0', b'\xb0')
    replace(packet, 0xafc0, 0xb338, b'\xd0', b'\xb0')
    stage_guard = bytes.fromhex('ad06070d64070d6107')
    tested_stage = call('StageRejected') + b'\xea'*6
    replace(packet, 0xafc0, 0xb2e8, stage_guard + b'\xd0', tested_stage + b'\xb0')
    replace(motion, 0xb800, 0xb825, stage_guard + b'\xf0', tested_stage + b'\x90')
    replace(carrier, 0xb400, 0xb67b, bytes.fromhex('c0d6f0'), jump('ProgressMux'))
    replace(carrier, 0xb400, 0xb6a8, bytes.fromhex('20e2b6'), call('ResetStageWeapons'))

    cookie = info['cookie'][:4] + bytes.fromhex(T.digest(info['cookie'] + Steve.DESCRIPTOR + stage + packet + carrier + motion))[:12]
    cold = Steve.cold_program(Steve.DESCRIPTOR, cookie)
    at = C.offset(65, T.COLD)
    replacement = cold['images']['COLD65'].ljust(T.COLD_SIZE, b'\xea')
    cookie_at = raw.index(info['cookie'], at, at+T.COLD_SIZE)
    assert replacement == raw[at:cookie_at] + cookie + raw[cookie_at+16:at+T.COLD_SIZE]
    out = bytearray(raw)
    out[cookie_at:cookie_at+16] = cookie
    hot = C.offset(94, 0xb2ef)
    out[hot:hot+16] = cookie
    for page, data in ((T.PACKET_PAGE, packet), (T.CHR_PAGE, carrier), (T.MOTION_PAGE, motion), (331, stage)):
        start = C.CHR + 1024*page
        out[start:start+len(data)] = data
    for page in (167, 216, 220, 234):
        assert T.page(out, page) == T.page(raw, page)
    assert T.page(out, T.CHR_PAGE)[0x186:0x200] == T.page(raw, T.CHR_PAGE)[0x186:0x200]
    assert T.page(out, T.PACKET_PAGE)[0x3ea:] == T.page(raw, T.PACKET_PAGE)[0x3ea:]
    assert T.digest(out) == CANDIDATE_PIN
    return bytes(out), dict(info, cookie=cookie, stage=sizes, machinegun=code)


def recover_parent(image):
    """Reconstruct exact 677aad54 from the installed machine gun candidate."""
    assert T.digest(image) == CANDIDATE_PIN
    assert T.digest(RETIRED_MOVEMENT) == '6c8164d5aaf43010942176c4241da228c2ae3e02a7d0b33d53fddd8534b53ffc'
    hot = C.offset(94, 0xb2ef)
    cookie = image[hot:hot+16]
    seed, _, _ = T.Motion.parent(raw=image, pin=CANDIDATE_PIN, cookie=cookie)
    cache = bytes(seed.ram[3][:0x8c0])
    assert staged(cache)[0] == T.page(image, 331) + T.page(image, 332)
    restored_runtime = cache[:LIVE_ORIGIN-0xa000] + RETIRED_MOVEMENT + cache[TEMPLATE-0xa000:]
    old_stage, _ = staged(restored_runtime)
    raw = bytearray(image)
    raw[hot:hot+16] = CURRENT_COOKIE
    cold = C.offset(65, T.COLD)
    cookie_at = raw.index(cookie, cold, cold+T.COLD_SIZE)
    raw[cookie_at:cookie_at+16] = CURRENT_COOKIE
    at = C.CHR + 331*1024
    raw[at:at+len(old_stage)] = old_stage
    for page, base, address, old in (
        (T.PACKET_PAGE, 0xafc0, 0xb000, '4c00b4'),
        (T.PACKET_PAGE, 0xafc0, 0xb155, 'd0'),
        (T.PACKET_PAGE, 0xafc0, 0xb338, 'd0'),
        (T.PACKET_PAGE, 0xafc0, 0xb2e8, 'ad06070d64070d6107d0'),
        (T.MOTION_PAGE, 0xb800, 0xb825, 'ad06070d64070d6107f0'),
        (T.CHR_PAGE, 0xb400, 0xb67b, 'c0d6f0'),
        (T.CHR_PAGE, 0xb400, 0xb6a8, '20e2b6'),
    ):
        at = C.CHR + 1024*page + address-base
        data = bytes.fromhex(old)
        raw[at:at+len(data)] = data
    assert T.digest(raw) == PIN
    return bytes(raw)


def steve_parity(raw, image, info):
    before, old_epoch = Steve.Live.opening(raw, 2)
    after, new_epoch = Steve.Live.opening(image, 2)
    assert old_epoch == new_epoch == 167
    assert before.ppu_reads == after.ppu_reads == 16400
    assert C.Common.headers(after) == (info['cookie'],) * 2
    assert before.ram[2][0x1800:0x1fe0] == after.ram[2][0x1800:0x1fe0]
    pads = [0]*6 + [64]*12 + [1]*19 + [129]*9 + [2]*15 + [0]*10 + [64]*9
    calls = [Counter(), Counter()]

    def witness(count):
        def observe(m, cpu):
            if (m.rawtags[2], cpu.pc) == (2, Steve.ORIGIN):
                count[cpu.y] += 1
        return observe

    for pad in pads:
        before.controller_pad = after.controller_pad = pad
        for m, count in zip((before, after), calls, strict=True):
            C.Game.frame(m, witness(count))
        old, new = C.Vector.app(before), C.Vector.app(after)
        assert old[:3] + old[4:] == new[:3] + new[4:]
        assert old[3][2][:0x1000] == new[3][2][:0x1000]
        assert before.vram == after.vram and before.chr_latches == after.chr_latches
    assert calls[0] == calls[1] == {0xe0: 80, 0xd6: 80}, calls
    return dict(updates=len(pads), loader_reads=after.ppu_reads, native_move_calls=dict(calls[1]),
                terminal=Steve.Live.player(after), lives=N.get(after, 'NumberofLives'))


def differential(raw, info, program):
    host, _, _ = T.Motion.parent(raw=raw, pin=PIN, cookie=info['cookie'])
    host.raw_page(1, 3)
    host.raw_page(2, 2)
    N.put(host, CurrentBank=3, CurrentBankC=2)
    data = program['images']['MACHINE_GUN']
    start = program['symbols']['MachineGunDispatch'] - 0xc000
    assert not any(host.ram[2][start:start+len(data)])
    host.ram[2][start:start+len(data)] = data
    donor = C.actual_donor()
    fields = info['fields']
    assert set(range(0xc060, 0xc080)).isdisjoint(fields.values())
    tested = Counter()
    for mask, ammo, buttons, flags, cooldown in product(
        range(32), (0, 1, 63), ((0, 0), (64, 0), (64, 64)), (0, 2, 8, 10, 12, 14), (0, 4)
    ):
        now, before = buttons
        old = C.Donor.fork(donor)
        old.memory.low_bank = 6
        new = C.Vector.clone(host)
        params = {0x52: cooldown, 0xb1: ammo, 0xb8: 1, 0x162: now, 0x163: before,
                  0x19: flags, 0x10: 2, 0x11: 0xc7, 0x12: 10, 0x13: 0xf5}
        for address, value in params.items():
            old.memory.ram[address] = value
        old.memory.ram[DONOR_RECORDS] = bytes(range(80))
        for slot in range(5):
            old.memory.ram[0x3b9 + 16*slot] = bool(mask & (1 << slot))
        for logical, physical in fields.items():
            new.ram[2][physical-0xc000] = old.memory.ram[logical]
        new.ram[2][RECORDS] = old.memory.ram[DONOR_RECORDS]
        args = (83, 71, 109, 0x71)
        old_regs = T.Weapon.Stock.direct(old, 0x81d2, args)
        new_regs = T.Weapon.Stock.direct(N.NesMPU(memory=new), program['symbols']['MachineGunDispatch'], args)
        context = (mask, ammo, buttons, flags, cooldown)
        assert old_regs == new_regs, (context, old_regs, new_regs)
        for logical, physical in fields.items():
            assert old.memory.ram[logical] == new.ram[2][physical-0xc000], (context, hex(logical))
        assert old.memory.ram[DONOR_RECORDS] == new.ram[2][RECORDS], context
        tested['fired' if old.memory.ram[0xb1] < ammo else 'blocked'] += 1
    return dict(tested)


def earned_route(image, info):
    import check_jay_silius_helpers_1111 as Helpers

    m, trial, _ = T.Motion.parent(raw=image, pin=T.digest(image), cookie=info['cookie'])
    helper, _ = Helpers.assemble(trial, origin=0xbd20)
    helper = helper['symbols']
    work, fields = T.Motion.assemble_handoff(trial, bytes(m.ram[3][0x88d:0x8c0]), origin=0xb800,
        control_tail=True, native_sync=True, native_helpers=(helper['StepHelpers'], helper['ResetHelpers']),
        pit_boundary=True)
    work.update(tile=C.Jay.build()['symbols']['JayHostTile'], status=0xc0f3)
    early = T.Motion.assisted_route(m, fields, work)
    assert early['terminal'] == (995, 176, 883) and early['lives'] == 2
    late = T.Motion.late_route(m, fields, middle_hold=2)
    assert late['lives'] == 2 and late['scene'][3] == 1 and len(late['gap_landings']) == 3, late
    assert any(row[1] == 'scene' and row[3] == (1, 3, 4, 0) for row in late['events'])
    assert any(row[1] == 'scene' and row[3] == (1, 3, 5, 0) for row in late['events'])
    assert m.ram[2][FLAGPOLE_MARK-0xc000] == 1

    calls = []
    symbols = info['machinegun']['symbols']
    def frame(pad):
        m.controller_pad = pad
        def observe(memory, cpu):
            if memory.rawtags[1] == 3 and cpu.pc == symbols['MachineGunBirth']:
                calls.append((N.get(memory, 'FrameCounter'), cpu.x, memory[0xc0be], memory[0xc01c]))
        C.Game.frame(m, observe)
        assert N.get(m, 'NumberofLives') == 2

    for entrance in range(550):
        frame(0)
        if tuple(N.get(m, name) for name in T.Motion.STATES) == (1, 3, 8) and m.ram[2][0xbf] == 3:
            if N.get(m, 'Player_State') == 0 and N.get(m, 'Player_Y_Position') == 176:
                break
    else:
        raise AssertionError(('Underground entrance did not settle', late['terminal'], T.Motion.position(m, fields),
                              tuple(N.get(m, name) for name in T.Motion.STATES), m.ram[2][0xbf]))
    assert N.get(m, 'AreaType') == 2 and N.get(m, 'LevelNumber') == 1
    assert (m.ram[2][0x20], m.ram[2][0xbe], m.ram[2][0xbf]) == (0, 63, 3)
    m.__class__ = T.Weapon.Draw.DmaBus
    m.dma = None
    frame(16)
    assert N.get(m, 'GamePauseStatus') & 1
    frame(0)
    frame(32)
    assert m.ram[2][0x20] == 1
    for _ in range(60):
        frame(0)
        if not N.get(m, 'GamePauseStatus') & 0x80:
            break
    frame(16)
    assert not N.get(m, 'GamePauseStatus') & 1
    for i in range(32):
        frame(64)
        if len(calls) == 5:
            break
    assert [row[1:] for row in calls] == [(slot, 62-i, 4) for i, slot in enumerate((0xf0, 0xe0, 0xd0, 0xc0, 0xb0))], calls
    assert all((b[0]-a[0])&255 == 5 for a,b in zip(calls, calls[1:])), calls
    active = [(slot, m.ram[2][slot+4], m.ram[2][slot+5]) for slot in range(0x60,0xb0,0x10)
              if m.ram[2][slot+9]]
    assert active == [(slot, 80, 0) for slot in range(0x60,0xb0,0x10)], active
    assert m.ram[2][0xbe] == 58 and m.ram[2][0x20] == 1
    cells = sorted(bytes((m.ram[2][slot+7]-8, 40, 0, m.ram[2][slot+6]-4)) for slot, _, _ in active)
    assert sorted(T.Weapon.Draw.cells(m[0x200:0x300])) == cells
    frame(0)
    assert sorted(T.Weapon.Draw.cells(m.dma)) == cells
    return dict(native_flag_and_castle=True, underground_settle_updates=entrance+1, pause_select_row=1,
                first_five_held_B_births=calls, active=active, dma_cells=len(cells), ammo=58, lives=2)


def controller():
    """Extend the existing physical controller from its native 1-2 checkpoint."""
    from replay_jay_steve_regression_1111 import controller as full_controller

    script = full_controller()
    tail = (H.ROOT / 'tools/playthroughs/jay_machinegun_continue_1111.lua').read_text(encoding='utf-8')
    edits = (
        ('local threeWay=false', 'local threeWay=false\nlocal gunBirths,gunLastClock,gunDma,gunExtendedDma={},nil,0,0'),
        ('"stair_trace":[%s]}', '"stair_trace":[%s],"machine_gun_births":[%s],"machine_gun_dma":%d,"extended_slot_dma":%d}'),
        ("table.concat(jumps,','),table.concat(stairTrace,',')))",
         "table.concat(jumps,','),table.concat(stairTrace,','),table.concat(gunBirths,','),gunDma,gunExtendedDma))"),
        ('local menu=coroutine.create(function()', tail + '\nlocal menu=coroutine.create(function()'),
        (' for slot=0x80,0xa0,0x10 do\n  if ram(2,slot+9)~=0 then',
         ' for slot=0x60,0xa0,0x10 do\n  if ram(2,slot+9)~=0 then'),
        ('expectedCells[y*256+x]=true', 'expectedCells[y*256+x]=slot'),
        ('read(at+2),read(at+3)}', 'read(at+2),read(at+3),expectedCells[read(at)*256+read(at+3)]}'),
        ('  dmaMatches=dmaMatches+1', '  dmaMatches=dmaMatches+1\n  if phase==\'machinegun\' then\n'
         '   gunDma=gunDma+1\n   if cell[6]<0x80 then gunExtendedDma=gunExtendedDma+1 end\n  end'),
        ("  finish(flagReached and castleReached,'Jay cleared 1-1 and entered underground 1-2')",
         "  phase='machinegun';bits=0"),
        (' if not playing then local ok,why=coroutine.resume(menu);assert(ok,why);return end',
         " if not playing then local ok,why=coroutine.resume(menu);assert(ok,why);return end\n"
         " if phase=='machinegun' then local ok,why=coroutine.resume(gun);assert(ok,why);return end"),
    )
    for before, after in edits:
        assert script.count(before) == 1, before
        script = script.replace(before, after)
    return script


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--route', action='store_true')
    args = parser.parse_args()
    raw = H.ROM.read_bytes()
    trial, info = current(raw)
    print('Current controller pause and three-way', Pause.gameplay(trial, info), flush=True)
    print('Current earned refill', refill(raw, info), flush=True)
    program = assemble(info)
    print(json.dumps(dict(passed=True, ROM_SHA256=PIN, machinegun_bytes=program['used']['MACHINE_GUN'],
                          row1_source_pairs=differential(raw, info, program), output_files=0), sort_keys=True),
          flush=True)
    candidate, linked = proposal(raw)
    assert recover_parent(candidate) == raw
    print(json.dumps(dict(candidate_SHA256=T.digest(candidate), cookie=linked['cookie'].hex(),
                          stage=linked['stage'], steve=steve_parity(raw, candidate, linked),
                          controller_SHA256=T.digest(controller().encode())), sort_keys=True), flush=True)
    if args.route:
        print(json.dumps(earned_route(candidate, linked), sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
