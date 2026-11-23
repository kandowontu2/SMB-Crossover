"""Compose and test Shinobi's native block bump after a donor upper contact."""

import argparse
import json
from pathlib import Path
import re
import subprocess
from tempfile import TemporaryDirectory

from mesen_session_guard_v1 import require_free_workspace
import probe_shinobi_current_head_1123 as Current
import probe_shinobi_first_mushroom_1123 as Prior


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'build/shinobi-head-effect-1123'
ASSEMBLY = ROOT / 'tools/reference/shinobi_head_effect_1123.s'
BODY_SOURCE = ROOT / 'tools/reference/shinobi_bbox_design_1101_v29.inc'
H, ROM, W, Stock = Prior.H, Prior.ROM, Prior.W, Prior.Stock
PAGES = Prior.CODE_PAGES
PRG65 = 16 + 65 * 8192
COOKIE = PRG65 + 0xA78
CODE_START = 0xA000
QUERY, QUERY_SIZE = 0xB501, 0x79
BODY, BODY_SIZE = 0xBAF8, 0x100
QUERY_REDIR = (0xB301, 0xB312)
CURRENT = Current.PIN


def compact_box(source):
    old_save = ' .repeat 8,I\n lda R0+I\n pha\n .endrepeat'
    new_save = ''' ldx #0
ShSaveBoxScratch:
 lda R0,x
 pha
 inx
 cpx #8
 bne ShSaveBoxScratch'''
    old_restore = ' .repeat 8,I\n pla\n sta R0+7-I\n .endrepeat'
    new_restore = ''' ldx #7
ShRestoreBoxScratch:
 pla
 sta R0,x
 dex
 bpl ShRestoreBoxScratch'''
    old_right = ''' lda $c00b
 beq ShFullBoxRightByte
 lda #$ff
 bne ShFullBoxRightReady
ShFullBoxRightByte:
 lda $c00a'''
    new_right = ''' lda $c00a
 ldx $c00b
 beq ShFullBoxRightReady
 lda #$ff'''
    source = Prior.once(source, old_save, new_save)
    source = Prior.once(source, old_restore, new_restore)
    return Prior.once(source, old_right, new_right)


def link():
    bundle = W.Symbols.bundle()
    names = ('R0 R1 R2 R3 R6 R7 ScreenLeft_X_Pos ScreenLeft_PageLoc '
             'MTileAttribute AreaType BlockBounceTimer GuestHurtTicks Block_Buffer_1 '
             'PlayerHeadCollision BoundingBox_UL_Corner BoundingBox_LR_Corner').split()
    symbols = {name: W.address(bundle, name) for name in names}
    symbols.update(ShImportPosition=0xB71D, ShSourceBounds=0xB93B)
    preamble = '\n'.join(f'{key} = ${value:04x}' for key, value in symbols.items())
    OUT.mkdir(exist_ok=True)
    with TemporaryDirectory(dir=OUT) as tmp:
        work = Path(tmp)
        asm, cfg, obj, output, names = (work / name for name in ('head.s', 'head.cfg', 'head.o', 'head.bin', 'head.lbl'))
        asm.write_text(preamble + '\n' + compact_box(BODY_SOURCE.read_text()) + '\n' + ASSEMBLY.read_text())
        cfg.write_text('''MEMORY {
 QUERY: start=$B501, size=$79, fill=yes, fillval=$EA;
 KERNEL: start=$BAF8, size=$100, fill=yes, fillval=$EA;
}
SEGMENTS { SHINOBI_QUERY: load=QUERY, type=ro; SHINOBI_KERNEL: load=KERNEL, type=ro; }
''')
        cc65 = ROOT / 'tools/Windows/cc65/bin'
        subprocess.run([cc65 / 'ca65.exe', asm, '-o', obj], check=True)
        subprocess.run([cc65 / 'ld65.exe', obj, '-C', cfg, '-o', output, '-Ln', names], check=True)
        labels = {name: int(pc, 16) for pc, name in re.findall(r'^al ([A-Fa-f0-9]+) \.(\S+)$', names.read_text(), re.M)}
        compiled = output.read_bytes()
    assert len(compiled) == QUERY_SIZE + BODY_SIZE
    assert labels['ShNativeQuery'] == QUERY and labels['ShFullBox'] == BODY
    return compiled, labels


def carrier(raw):
    return b''.join(raw[1048592 + p * 1024:1048592 + (p + 1) * 1024] for p in PAGES)


def compose(raw):
    assert H(raw) == CURRENT
    parent = Current.Goku.recover_parent(raw)
    code, metadata, art = Prior.payload(parent)
    assert carrier(raw) == code and raw[COOKIE:COOKIE + 16] == parent[COOKIE:COOKIE + 16]
    assert code[0x1bba:0x1bf8] == b'\xea' * 62
    new = bytearray(code)
    compiled, labels = link()

    def replace(pc, before, after):
        at = pc - CODE_START
        assert new[at:at + len(before)] == before and len(before) == len(after), hex(pc)
        new[at:at + len(after)] = after

    replace(QUERY, code[QUERY - CODE_START:QUERY - CODE_START + QUERY_SIZE], compiled[:QUERY_SIZE])
    replace(BODY, code[BODY - CODE_START:BODY - CODE_START + BODY_SIZE], compiled[QUERY_SIZE:])
    for pc in QUERY_REDIR:
        replace(pc, bytes.fromhex('2001b5'), b'\x20' + labels['ShUpperProbe'].to_bytes(2, 'little'))
    replace(0xB7B2, bytes.fromhex('8d10c8'), b'\x20' + labels['ShBeginFrame'].to_bytes(2, 'little'))
    replace(0xB809, bytes.fromhex('20bab3'), b'\x20' + labels['ShAfterSource'].to_bytes(2, 'little'))

    result = bytearray(raw)
    for i, page in enumerate(PAGES):
        at = 1048592 + page * 1024
        result[at:at + 1024] = new[i * 1024:(i + 1) * 1024]
    cookie = bytes([167, 36, 1]) + bytes.fromhex(H(new + metadata + art + metadata[1024:]))[:13]
    result[COOKIE:COOKIE + 16] = cookie
    return bytes(result), dict(labels=labels, cookie=list(cookie), code_sha=H(new), ROM_SHA256=H(result))


def mapped_memory(raw):
    memory = bytearray(65536)
    memory[CODE_START:CODE_START + 7168] = carrier(raw)
    for page, address in ((516, 0xD000), (517, 0xD400)):
        start = 1048592 + page * 1024
        memory[address:address + 1024] = raw[start:start + 1024]
    for bank, address in ((126, 0x8000), (127, 0xE000)):
        start = 16 + bank * 8192
        memory[address:address + 8192] = raw[start:start + 8192]
    return memory


def direct(memory, entry, *, a=0, x=0, y=0x5B, p=0x71):
    cpu = Prior.N.NesMPU(memory=memory, pc=entry)
    cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp = a, x, y, p, 0xE0
    cpu.stPushWord(0x5AFF)
    for _ in range(8000):
        if cpu.pc == 0x5B00:
            assert cpu.sp == 0xE0
            return (cpu.a, cpu.x, cpu.y, cpu.p), cpu.processorCycles
        assert memory[cpu.pc] != 0, f'Unexpected BRK at {cpu.pc:04X}'
        cpu.step()
    raise AssertionError(f'Cached Shinobi procedure did not return from {entry:04X}')


def place_tile(memory, camera, x, y, tile):
    memory[0x071D], memory[0x071F] = camera >> 8, camera & 0xFF
    memory[3:7] = bytes([x & 0xFF, x >> 8, y & 0xFF, y >> 8])
    if 32 <= y < 240:
        world = camera + x
        column = 0x03D0 if world & 256 else 0x0300
        memory[column + ((world & 0xFF) >> 4) + (y & 0xF0) - 32] = tile


def verify_controls(raw, image, binding):
    base_memory, new_memory = (mapped_memory(data) for data in (raw, image))
    cycles = []
    queries = 0
    for camera, x in ((0, 23), (218, 119), (504, 24)):
        for y in (8, 32, 156, 239, 240, 260):
            for tile in (range(256) if 32 <= y < 240 else (0,)):
                states = []
                for memory in (base_memory, new_memory):
                    place_tile(memory, camera, x, y, tile)
                    registers, cost = direct(memory, QUERY, x=4)
                    scratch = bytes(memory[3:11] + memory[0xC004:0xC00B] + memory[0xC804:0xC806])
                    states.append((registers, scratch, cost))
                assert states[0][:2] == states[1][:2], (camera, x, y, tile, states)
                cycles.append(states[1][-1] - states[0][-1])
                queries += 1

    boxes = 0
    base_memory, new_memory = (mapped_memory(data) for data in (raw, image))
    for pose in range(96):
        for page, x, y in ((1, 80, 176), (1, 1, 15), (1, 245, 195), (2, 140, 12)):
            for face in (0, 4):
                states = []
                for memory in (base_memory, new_memory):
                    memory[0xC000:0xC800] = bytes(0x800)
                    memory[0xC300], memory[0xC363] = pose, face
                    memory[0x75], memory[0x5C], memory[0xBD], memory[0xA4] = x, 0, y, page
                    memory[3:11] = bytes(range(0xA1, 0xA9))
                    registers, _ = direct(memory, BODY, a=0x47, x=5)
                    states.append((registers, bytes(memory[0x658:0x65C]),
                                   bytes(memory[3:11]), bytes(memory[0xC000:0xC800])))
                assert states[0] == states[1], (pose, page, x, y, face)
                boxes += 1

    new_memory = mapped_memory(image)
    labels = binding['labels']
    captures = 0
    for direction in (0, 4, 8, 12):
        for actor in (0, 1):
            new_memory[0xC3FD] = direction
            direct(new_memory, labels['ShBeginFrame'])
            assert new_memory[0xC811] == 0
            for x, tile in ((91, 0xC1), (83, 0x51)):
                place_tile(new_memory, 248, x, 156, tile)
                regs, _ = direct(new_memory, labels['ShUpperProbe'], x=actor)
                assert regs[0] == 1 and regs[1] == actor
            expected = bytes([0xC1, 0xD5, 0x70]) if direction == 4 and actor == 0 else None
            actual = bytes(new_memory[0xC811:0xC814])
            assert actual == expected if expected else actual[0] == 0
            captures += 1
    return dict(terrain_queries=queries, ordinary_query_cycle_change=[min(cycles), max(cycles)],
                box_abi_cases=boxes, two_cell_head_cases=captures, source_motion_unchanged=True)


def observer(raw, image, binding):
    previous = Current.controller(raw).decode()
    line, body = previous.split('\n', 1)
    # The diagnostic's query return hook refers to the pre-compaction PC.
    # The native head/birth hooks still capture the complete transaction.
    cfg = Prior.once(line, CURRENT, H(image))
    body = "\nC.hooks.QueryReturn=nil\nC.cookie=" + Stock.value(binding['cookie']) + '\n' + body
    return cfg + '\n' + body


def program(raw, image, binding):
    text = Prior.once(observer(raw, image, binding), 'local function policy()', '''local function policy()
 if #births>0 then
  assert(#heads>0 and r('ShReady')==167 and r('NumberofLives')==2,'Live Shinobi native head and item lifecycle')
  assert(births[1].actor.x==336 and births[1].actor.kind==0
   and heads[1].pointer==0x3d5 and heads[1].row==0x70 and heads[1].tile==0xc1,'Actual right-hand question cell')
  if moves>=births[1].player.moves+25 then finish(true,'Shinobi bumped the authored Mushroom block');return {}end
 end''')
    Stock.LuaRuntime().compile(text)
    return text.encode()


def native(raw, image, binding, controller=None):
    out = Stock.OUT
    target, script = out / 'candidate.nes', out / 'controller.lua'
    guard = Stock.check(ROM)
    assert guard['ROM_sha256'] == CURRENT and not guard['matching_patch_files']
    assert set(out.iterdir()) == {target, script} and target.read_bytes() == raw
    previous = script.read_bytes()
    if controller is None:
        controller = program(raw, image, binding)
    require_free_workspace(ROOT, target, allow_interactive=True)
    try:
        target.write_bytes(image)
        script.write_bytes(controller)
        result = Stock.run(script, target, out / 'capture', H(image), 220)
        assert result['script_SHA256'] == H(controller) and result['outputs_written'] == 0 and not result['images']
        return result
    finally:
        target.write_bytes(raw)
        script.write_bytes(previous)
        assert Stock.check(ROM) == guard and set(out.iterdir()) == {target, script}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    raw = ROM.read_bytes()
    image, binding = compose(raw)
    binding['controls'] = verify_controls(raw, image, binding)
    print('SHINOBI HEAD BINDING ' + json.dumps(binding, separators=(',', ':')), flush=True)
    if not args.run:
        return 0
    result = native(raw, image, binding)
    print('SHINOBI HEAD NATIVE ' + json.dumps(result, separators=(',', ':')), flush=True)
    return int(not result['passed'])


if __name__ == '__main__':
    raise SystemExit(main())
