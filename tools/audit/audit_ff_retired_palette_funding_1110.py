"""Read-only c10 FF private funding and runtime-cookie audit; stdout only.

Closes all actual ROM62 target-setting RAM3 gateways, their complete direct
6502 flow, both split source-art pointer tables and the36 public veneers.
This is source funding evidence, not an implementation or gameplay verdict.
"""
from hashlib import sha256
import json
from pathlib import Path

from py65.disassembler import Disassembler
import check_ff_white_mushroom_current_1110 as W

IMAGE_PIN = '14f1ac6330109b1e6ab77710c8491b8ba1b706a524b133a7c9542d6b51910b3b'
RETIRED_PIN = 'a76c5f9a9e202f66dcdc7fbcd85b34f9257260a145b63bd85bf720cae9b35cc6'
START, END = 0xb620, 0xb670


def gateways(raw, bundle):
    bank = raw[16+62*8192:16+63*8192]
    lo = W.address(bundle, 'FarcallJmpTarget_SMC')+1
    hi = lo+1
    enter = W.address(bundle, 'FwCallEnter')
    roots = []
    for i in range(len(bank)-12):
        d = bank[i:i+13]
        if (d[0] == 169 and d[2:5] == b'\x8d'+lo.to_bytes(2, 'little') and
                d[5] == 169 and d[7:10] == b'\x8d'+hi.to_bytes(2, 'little') and
                d[10:13] == b'\x4c'+enter.to_bytes(2, 'little')):
            roots.append((0xa000+i, d[1]+256*d[6]))
    return roots


def walk(image, roots):
    memory = [0]*65536
    memory[0xa000:0xc000] = image
    cpu = W.N.NesMPU(memory=memory)
    dis = Disassembler(cpu)
    seen, calls, indirect = {}, [], []
    todo = list(roots)
    while todo:
        pc = todo.pop()
        if not 0xa000 <= pc < 0xc000 or pc in seen:
            continue
        length, text = dis.instruction_at(pc)
        name, mode = cpu.disassemble[memory[pc]]
        seen[pc] = dict(bytes=length, mnemonic=name, mode=mode, text=text)
        nxt = pc+length
        assert name != 'BRK', ('invalid reachable code', hex(pc))
        if name in ('RTS', 'RTI'):
            continue
        if name == 'JMP':
            if mode == 'ind':
                indirect.append((pc, text))
            else:
                todo.append(memory[pc+1]+256*memory[pc+2])
        elif name == 'JSR':
            target = memory[pc+1]+256*memory[pc+2]
            calls.append((pc, target))
            todo += [target, nxt]
        elif mode == 'rel':
            delta = memory[pc+1]
            todo += [nxt, nxt+(delta if delta < 128 else delta-256)]
        else:
            todo.append(nxt)
    return seen, calls, indirect


def main():
    raw = W.ROM.read_bytes()
    assert sha256(raw).hexdigest() == W.PIN
    b = W.Symbols.bundle()
    carrier = 1048592+893*1024
    image = raw[carrier:carrier+8192]
    assert sha256(image).hexdigest() == IMAGE_PIN
    retired = image[START-0xa000:END-0xa000]
    assert len(retired) == 80 and sha256(retired).hexdigest() == RETIRED_PIN
    assert W.address(b, 'FfEffectPalettePointer') == START
    assert W.address(b, 'FfPalettePointer') == END
    assert int(b['syms']['FfEffectPalettePointer']['size'], 0) == 80
    assert image[0xb61d-0xa000:START-0xa000] == bytes.fromhex('4c43b4')
    gates = gateways(raw, b)
    assert len(gates) == 37
    seen, calls, indirect = walk(image, [target for _, target in gates])
    assert len(seen) == 2731 and not indirect
    assert not any(START <= pc < 0xb68b for pc in seen)
    assert not any(START <= target < 0xb68b for _, target in calls)
    assert 0xb613 in seen and seen[0xb61d]['text'] == 'JMP $b443'
    # A deliberately introduced root is caught; no retired-range exclusion
    # is built into the graph traversal.
    bad, _, _ = walk(image, [target for _, target in gates]+[START])
    assert START in bad
    words = []
    for i in range(8191):
        pc = 0xa000+i
        target = image[i]+256*image[i+1]
        if START <= target < END and not START <= pc < END:
            words.append((pc, target))
            assert pc in seen and seen[pc]['text'] == 'JMP $aeb6'
    assert words == [(0xaf4d, 0xb64c), (0xaf55, 0xb64c), (0xaf60, 0xb64c)]
    # These are the only split-address source data tables read by the actual
    # body/FX decoders. Their addresses are data pointers, never hidden code.
    fx_lo, fx_hi = (W.address(b, n)-0xa000 for n in ('FfFxLo', 'FfFxHi'))
    fx = [image[fx_lo+i]+256*image[fx_hi+i] for i in range(44)]
    assert all(not START <= target < END for target in fx)
    art = raw[16+93*8192:16+94*8192]
    rec_lo, rec_hi = (W.address(b, n)-0xc000 for n in ('FfRecordLo', 'FfRecordHi'))
    records = [art[rec_lo+i]+256*art[rec_hi+i] for i in range(80)]
    assert all(0xc000 <= target < 0xe000 for target in records)
    at = W.location(b, 'FwServiceVeneers')
    veneers = []
    for i in range(36):
        d = raw[at+3*i:at+3*i+3]
        assert d[0] == 76
        target = int.from_bytes(d[1:], 'little')
        assert target not in (0xaeda, 0xaef4)
        veneers.append(target)
    loader = (W.R/'build/ff-lives-body-palette-v1/joint/loader.s').read_text()
    assert 'Two obsolete unused exports are explicitly retired' in loader
    assert 'FW_GATE FwEffectPalettePointer,FfEffectPalettePointer' not in loader
    assert 'FW_GATE FwPalettePointer,FfPalettePointer' not in loader
    assert 'lda #<FfPortrait' in loader
    palette = (W.R/'tools/reference/final_fantasy_host_palette_v3.s').read_text()
    assert 'FfEffectPalettePointer' not in palette and 'FfPalettePointer' not in palette
    # Current image keeps a placeholder; loader stamps the external digest
    # only AFTER it copies and verifies all8192 destination bytes.
    assert image[0x1fe0:0x1ff0] == bytes([255])*16
    cookie_at = W.location(b, 'FwCookie')
    cookie = raw[cookie_at:cookie_at+16]
    assert cookie == bytes([167, 22, 0, 9])+sha256(image).digest()[:12]
    assert cookie_at == 511774 and W.address(b, 'FwCookie') == 0xaf0e
    check_at = W.location(b, 'FwCheckByte')
    assert raw[check_at-2:check_at] == bytes.fromhex('a20f')
    assert raw[check_at:check_at+6] == bytes.fromhex('bde0dfdd0eaf')
    assert 'ldx #15' in loader and 'after full8192B verify' in loader
    assert 'valid published LAST' in loader
    assert sha256(W.ROM.read_bytes()).hexdigest() == W.PIN
    print(json.dumps(dict(passed=True, ROM_sha256=W.PIN, image_sha256=IMAGE_PIN,
        ROM_written=False, output_files=0, source_funding_only=True,
        proposed_retirement=dict(name='FfEffectPalettePointer', start=START,
            end_exclusive=END, bytes=80, sha256=RETIRED_PIN,
            source='src/final_fantasy_render.s .proc FfEffectPalettePointer'),
        actual_ROM62_RAM3_gateways=gates, reached_instruction_PCs=len(seen),
        indirect_jumps=indirect, retired_reachable=False,
        negative_new_root_detected=True, outside_word_lookalikes=words,
        split_pointer_tables=dict(FX=44, original_art=80, retired_targets=0),
        public36_ROM_veneer_targets=veneers,
        live_neighbors_preserved=['FfPortrait B613..B620', 'FfVisible B498',
                                 'FfPalettePointer B670..B68B', 'FfMuxPacket B68B..B6FE'],
        cookie=dict(file_offset=cookie_at, address=0xaf0e, bytes=cookie.hex(),
                    scheme='A7,22,0,revision + SHA256(full8192B placeholder image) first12 bytes',
                    placeholder=[0xbfe0,0xbff0], native_check_bytes=16,
                    native_warm_check_rehashes_code=False,
                    cold_rule='Replace carrier and ROM cookie together; genuine forcedblank cold load verifies8192 then stamps cookie validity last. Reuse no old loaded arena as new-ROM proof.'),
        scope='All actual ROM62 RAM3 target-immediate gateways/direct code flow and current source-art pointer/public-service tables. No product edit or helper correctness/gameplay/IRQ/Mesen claim.')), flush=True)


if __name__ == '__main__':
    main()
