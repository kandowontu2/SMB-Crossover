"""Scoped, in-memory Steve armor carrier packet and cold loader."""

from functools import lru_cache
import json
import re

import check_prince_brick_support_1111 as Host
import check_steve_shatterhand_companion_transport_1111 as Cold
import prince_cold_packet_1111 as Codec
import steve_armor_transport_1112 as Entry
import steve_armor_carriers_1113 as Preimage


PAGES = (371, 375, 379, 336, 338, 167, 304, 306, 307)
SOURCE = Entry.ROOT/'tools/reference/steve_armor_packet_1113.s'
QUALIFICATION_PARENT = 'a3c5fa63872fbb3103ae57d9748fef233e8b2273e26d985aa4006b2492d81b8a'
# Destinations are in the CPU C window, paired with their physical raw bank.
# Complete headers remain transaction-owned. Explicit state blocks reset
# upgrade and token fields when a foreign cache is replaced.
REGIONS = ((2, 0xc100, 239), (2, 0xc1f0, 16), (2, 0xc200, 447),
           (2, 0xc3fb, 5), (2, 0xc400, 128),
           (2, 0xc480, 32), (2, 0xc4a0, 96), (2, 0xc500, 1024),
           (2, 0xc900, 128), (2, 0xc980, 128), (2, 0xca00, 1024),
           (2, 0xce00, 512), (2, 0xd000, 1024), (2, 0xd400, 1024),
           (2, 0xd800, 1024), (2, 0xdc00, 992), (3, 0xcb00, 1024))


def qualification_parent(*, before_quick=False):
    raw = Entry.U.Upgrade.D.HOST.read_bytes()
    if before_quick:
        import compose_quick_climb_material_1113 as Quick
        raw = Quick.inverse(raw)
    assert Entry.digest(raw) == QUALIFICATION_PARENT, (
        'Explicit qualification parent required',Entry.digest(raw))
    return raw


def parent_cookie(raw):
    cookie = raw[Entry.prg(94,0xb2ef):Entry.prg(94,0xb2ef)+16]
    assert cookie[:3] == bytes.fromhex('a81020') and cookie[3] in (10,11,12)
    if cookie[3] == 12:
        assert cookie == bytes.fromhex('a810200c4dbf5b49c59d4e142de148bf')
    assert raw[Entry.prg(65,0xa727):Entry.prg(65,0xa727)+16] == cookie
    return cookie


@lru_cache(maxsize=1)
def original_resident(raw):
    """Execute the installed native cold entry once, retaining only two banks."""
    C = Cold.C
    assert tuple(raw[Entry.CHR+page*1024:Entry.CHR+(page+1)*1024]
                 for page in PAGES) == Preimage.original_rows()
    memory = C.Common.blank(Host.C.Start.W.bundle(raw))
    C.Common.scene(memory, 16)
    memory[0x730b] = 0x40
    cookie = parent_cookie(raw)
    target = Cold.compact_cold(cookie, extended=True,
                               upgrade=Entry.U.descriptor(371))['symbols']['JaySceneOrRetire']
    cpu = C.ColdVector.entry(memory)
    memory[0x16c], memory[0x16d] = target & 255, target >> 8
    C.Vector.finish(memory, cpu, Cold.T.Weapon.Stock.STOP)
    assert C.Common.headers(memory) == (cookie,) * 2
    assert memory.ppu_reads == 32800
    return {bank: bytes(memory.ram[bank]) for bank in (2, 3)}


def blocks(raw, helper=b''):
    resident = original_resident(raw)
    result = [(bank, address, resident[bank][address-0xc000:address-0xc000+size])
              for bank, address, size in REGIONS]
    if helper:
        assert len(helper) <= 2048
        result.append((1, 0xc000, helper))
    return result


def assemble(source, layout):
    """Resolve ca65 local labels and relax only branches outside their range."""
    lines = source.splitlines()
    anonymous = [index for index, line in enumerate(lines) if line.strip() == ':']
    for index, line in enumerate(lines):
        if index in anonymous:
            lines[index] = f'PacketLocal{index}:'
            continue
        for direction, candidates in (('+', [at for at in anonymous if at > index]),
                                      ('-', [at for at in anonymous if at < index])):
            if ':'+direction in line:
                at = candidates[0] if direction == '+' else candidates[-1]
                line = line.replace(':'+direction, f'PacketLocal{at}')
        lines[index] = re.sub(r'\.res (\d+)', lambda m: '.byte '+','.join(['0']*int(m[1])), line)
    inverse = dict(bcc='bcs', bcs='bcc', beq='bne', bne='beq', bmi='bpl', bpl='bmi')
    for iteration in range(64):
        try:
            return Entry.U.H.assemble('\n'.join(lines)+'\n', layout)
        except AssertionError as error:
            detail = error.args[0] if error.args else None
            if not (isinstance(detail, tuple) and isinstance(detail[0], dict)
                    and detail[0].get('op', '').lower() in inverse):
                raise
            item = detail[0]
            index = item['line']-1
            label = f'PacketRelax{iteration}'
            op = inverse[item['op'].lower()]
            lines[index:index+1] = [f'    {op} {label}', f'    jmp {item["operand"]}', label+':']
    raise AssertionError('Packet branch relaxation did not converge')


def link(rows, packet_offset=0, cookie=bytes(16), *, recovery_relocated=False, wave_page=None):
    table = b''.join(address.to_bytes(2, 'little')+bytes((bank,))+len(data).to_bytes(2, 'little')
                     for bank, address, data in rows)
    header = (f'CurrentBankC=$7da1\nPacketOffset={packet_offset}\n'
              f'BlockTableSize={len(table)}\n')
    header += f'SourceDirectBase={9+int(wave_page is not None)}\n'
    if wave_page is not None:
        header += f'STEVE_WAVE_ROW={wave_page}\nWaveArtBytes=192\n'
    if recovery_relocated:
        header += 'STEVE_RECOVERY_RELOCATED=1\n'
    source = SOURCE.read_text().replace('BlockTableBytes', ','.join(map(str, table)))
    source = source.replace('CookieBytes', ','.join(map(str, cookie)))
    return assemble(header+source,
                    {'STEVE_PACKET_BOOT': (0xa000, 64), 'STEVE_PACKET_COLD': (0xb850, 944)})


def proposal(raw, rows=None, *, recovery_relocated=False, marker=0xa8, binding=b'',
             warm_verifier=None, wave_page=None, wave_art=b''):
    previous_cookie = parent_cookie(raw)
    rows = blocks(raw, b'\xa9\x39\x60') if rows is None else rows
    decoded = b''.join(data for _, _, data in rows)
    packed = Codec.encode(decoded)
    assert Codec.decode(packed, len(decoded)) == decoded
    if wave_page is not None:
        assert wave_page == 739 and len(wave_art) == 192 and recovery_relocated
        assert raw[Entry.CHR+wave_page*1024:Entry.CHR+(wave_page+1)*1024] == bytes(1024)
    program = link(rows, recovery_relocated=recovery_relocated, wave_page=wave_page)
    offset = 80+len(program['images']['STEVE_PACKET_COLD'])
    program = link(rows, offset, recovery_relocated=recovery_relocated, wave_page=wave_page)
    prefix = (program['images']['STEVE_PACKET_BOOT'].ljust(64, b'\xea')+
              previous_cookie+program['images']['STEVE_PACKET_COLD'])
    assert len(prefix) == offset and offset < 1024
    payload = prefix+packed
    capacity = 9216 if recovery_relocated else 8960
    capacity += 832 if wave_page is not None else 0
    assert len(payload) <= capacity, (len(prefix), len(packed), capacity)
    # Preserve all recovery cells in physical row307, including their zeros.
    addresses = [Entry.CHR+page*1024+index for page in PAGES for index in range(1024)
                 if recovery_relocated or page != 307 or not 0x200 <= index < 0x300]
    if wave_page is not None:
        addresses += list(range(Entry.CHR+wave_page*1024+192,Entry.CHR+(wave_page+1)*1024))
    old_cold = Cold.compact_cold(previous_cookie, extended=True, upgrade=Entry.U.descriptor(371))
    # Native typed entry D25E is the existing JMP A000 in row331.
    descriptor = bytes((2, 1, 1, 115, 1, 75, 1))
    assert len(descriptor) == 7
    old_descriptor = Cold.companion_descriptors(Entry.U.descriptor(371))[1]
    cookie = bytes((marker,))+previous_cookie[1:4]+bytes.fromhex(
        Entry.digest(previous_cookie+descriptor+payload+binding+wave_art))[:12]
    program = link(rows, offset, cookie, recovery_relocated=recovery_relocated,wave_page=wave_page)
    prefix = (program['images']['STEVE_PACKET_BOOT'].ljust(64, b'\xea')+
              previous_cookie+program['images']['STEVE_PACKET_COLD'])
    payload = prefix+packed
    source = old_cold['source']
    old_line = ' .byte '+','.join(map(str, old_descriptor))
    assert source.count(old_line) == 1
    source = source.replace(old_line, ' .byte '+','.join(map(str, descriptor)))
    source = source.replace(' ldx #24\nPushDescriptor:', ' ldx #6\nPushDescriptor:')
    source = source.replace(' ldx #25\nPullDescriptor:', ' ldx #7\nPullDescriptor:')
    if warm_verifier is None:
        # Standalone transport canaries deliberately have no public hot ABI.
        force_cold = (' lda $7da1\n pha\n lda #2\n jsr $80c2\n'
                      ' lda #0\n sta $dfe0\n pla\n jsr $80c2\n')
        source = source.replace(' ldx #6\nPushDescriptor:',force_cold+' ldx #6\nPushDescriptor:')
    else:
        old_post = (' bcc SceneDone\n lda $7da1\n pha\n lda #2\n jsr $80c2\n'
                    ' stx $c033\n pla\n jsr $80c2\n')
        assert source.count(old_post) == 1
        source = source.replace(old_post,'')
        check = (' bcc SceneWarmDone\n lda $7da1\n pha\n lda #2\n jsr $80c2\n'
                 ' lda #5\n sta $016a\n'+
                 f' lda #<{warm_verifier}\n sta $016c\n lda #>{warm_verifier}\n sta $016d\n'+
                 ' lda #1\n jsr $015a\n pla\n jsr $80c2\n bcc SceneBind\nSceneWarmDone:\n')
        source = source.replace(' jsr $ae00\nSceneReturn:\n',
                                'SceneBind:\n jsr $ae00\nSceneReturn:\n'+check)
    source = source.replace(' .byte '+','.join(map(str, previous_cookie)),
                            ' .byte '+','.join(map(str, cookie)))
    cold = Entry.U.H.assemble(source, {'COLD65': (Cold.T.COLD, Cold.T.COLD_SIZE)})
    output = bytearray(raw)
    if wave_page is not None:
        at = Entry.CHR+wave_page*1024
        output[at:at+192] = wave_art
    for address, value in zip(addresses, payload.ljust(capacity, b'\xff'), strict=True):
        output[address] = value
    at = Entry.prg(65, Cold.T.COLD)
    before = old_cold['images']['COLD65'].ljust(Cold.T.COLD_SIZE, b'\xea')
    assert raw[at:at+len(before)] == before
    output[at:at+len(before)] = cold['images']['COLD65'].ljust(Cold.T.COLD_SIZE, b'\xea')
    at = Entry.prg(65, 0xaf01)
    assert raw[at:at+2] == old_cold['symbols']['JaySelect'].to_bytes(2, 'little')
    output[at:at+2] = cold['symbols']['JaySelect'].to_bytes(2, 'little')
    at = Entry.prg(94, 0xb2ef)
    output[at:at+16] = cookie
    return bytes(output), dict(cookie=cookie, cold=cold, program=program, rows=rows,
                               prefix_bytes=len(prefix), packed_bytes=len(packed), spare=capacity-len(payload),
                               native_warm_auth=warm_verifier is not None, wave_page=wave_page)


def load(candidate, info, memory=None, observe=None, *, allow_failure=False):
    from collections import deque
    C = Cold.C
    if memory is None:
        memory = C.Common.blank(Host.C.Start.W.bundle(candidate))
        C.Common.scene(memory, 16)
        memory[0x730b] = 0x40
    cpu = C.ColdVector.entry(memory)
    target = info['cold']['symbols']['JaySceneOrRetire']
    memory[0x16c], memory[0x16d] = target & 255, target >> 8
    trail = deque(maxlen=12)
    for steps in range(4_000_000):
        if (cpu.pc, cpu.sp) == Cold.T.Weapon.Stock.STOP:
            break
        assert memory[cpu.pc], ('BRK', hex(cpu.pc), memory.rawtags)
        if observe:
            observe(memory, cpu)
        trail.append((hex(cpu.pc), tuple(memory.rawtags), cpu.a, cpu.x, cpu.y, cpu.sp))
        try:
            cpu.step()
        except AssertionError as error:
            labels = info['program']['symbols']
            variables = {name: memory[address] for name, address in labels.items()
                         if name in ('BlockIndex', 'ComparePass', 'InputHigh', 'ColdStack')}
            raise AssertionError((str(error), list(trail), list(memory[3:11]), variables)) from error
    else:
        raise AssertionError(('Packet cold bound', hex(cpu.pc), cpu.sp))
    assert (cpu.a, cpu.x, cpu.y, cpu.p & 0xef, cpu.sp) == (83, 71, 109, 0x21, 224)
    if allow_failure:
        return memory,steps
    assert C.Common.headers(memory) == (info['cookie'],)*2, (C.Common.headers(memory), info['cookie'].hex())
    assert bytes(memory.ram[1][0x1fe0:0x1ff0]) == info['cookie']
    for bank, address, data in info['rows']:
        actual = bytes(memory.ram[bank][address-0xc000:address-0xc000+len(data)])
        assert actual == data, (bank, hex(address), next(((i,a,b) for i,(a,b) in enumerate(zip(actual,data)) if a != b), None))
    return memory, steps


def check_cold(raw):
    candidate, info = proposal(raw)
    memory, steps = load(candidate, info)
    original = original_resident(raw)
    assert bytes(memory.ram[3][:0xb00]) == original[3][:0xb00], [
        (hex(index), before, after) for index, (before, after) in
        enumerate(zip(original[3][:0xb00], memory.ram[3][:0xb00])) if before != after][:20]
    assert bytes(memory.ram[3][0x1000:0x1fe0]) == original[3][0x1000:0x1fe0]
    return dict(parent=Entry.digest(raw), candidate=Entry.digest(candidate), cpu_steps=steps,
                ppu_reads=memory.ppu_reads, prefix_bytes=info['prefix_bytes'],
                packed_bytes=info['packed_bytes'], spare=info['spare'],
                exact_runtime_blocks=len(info['rows']), original_jay_preserved=True,
                cold_mounted=True, executable_canary_bytes=3, output_files=0)


def measure(raw):
    source = b''.join(data for _, _, data in blocks(raw))
    packed = Codec.encode(source)
    assert Codec.decode(packed, len(source)) == source
    program = link(blocks(raw))
    cold_size = 80+len(program['images']['STEVE_PACKET_COLD'])
    return dict(parent=Entry.digest(raw), blocks=len(REGIONS), runtime_bytes=len(source),
                packed_bytes=len(packed), carrier_bytes=9*1024-256,
                cold_loader_bytes=cold_size, total_bytes=cold_size+len(packed),
                remaining_for_new_helper=9*1024-256-len(packed)-cold_size, output_files=0)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cold', action='store_true')
    args = parser.parse_args()
    raw = Entry.U.Upgrade.D.HOST.read_bytes()
    print(json.dumps(check_cold(raw) if args.cold else measure(raw), sort_keys=True), flush=True)
