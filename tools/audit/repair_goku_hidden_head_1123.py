"""Build and qualify Goku's hidden-block head admission on the MMC5 nightly."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from unittest.mock import patch

from mesen_session_guard_v1 import require_free_workspace
import run_goku_stock_1123 as Replay


ROOT = Path(__file__).resolve().parents[2]
SCRATCH = ROOT / 'build/goku-hidden-head-1123'
ROM = Replay.ROM
BASE = Replay.PIN
CANDIDATE = '93f140baee70d97dd061dae60d549c2ac1ed1920a80b2288fa2b52b9e4be1712'
NATIVE_BANK = 86
QUERY = 0xB236
QUERY_SIZE = 0xC0
HELPER = 0xB83B
HELPER_SIZE = 0x22
ASSEMBLY = ROOT / 'tools/reference/goku_hidden_head_1123.s'
PARENT_QUERY = bytes.fromhex('''
    c9f09003a901608c325c8d335c29f08504984a4a4a4a05048d225c088a48a5038d275ca5
    048d285cad335cc920907829f038e9208d245cad1f07186d325c8d255cad1d0769008d26
    5c29010a0a0a0a8503ad255c4a4a4a4a050320dc95ac245c203bb8eac923f03fc926f03b
    c9c2f037c9c3f033c95ff02fc960f02bc951f023c952d01318a50969d18509a50a696385
    0ab109f00ed008a8b936ef2901f008a975d006a995d002a9008d235cad275c8503ad285c
    850468aa28ac225cad235c60''')
PARENT_HELPER = bytes.fromhex('b109f01bc924f017c925f013c9c0f00cc9c1f008c9559006c95fb002a95160a92360')
NATIVE_RECEIPTS = {
    'life': 'f3f4215f585a22593c447bfed673ea48f46547d9b4ccb10d6124c8a972579476',
    'flower': 'a575c92f7af7d54794f4a61641e9bfc015022cf4552e0a3165ee410292d42729',
    'stage': '2e6595f9157eb10a753ee4909e99357cbf97aa49035b29564215c45cda7aa50b',
}

STAGE_DRIVE = r'''
local function stageDrive()
 local s=F.stage
 if not active() then buttons={};return end
 local c=context()
 c.lastA=r('DpPrevious')&128~=0
 assert(r('SelectedCharacter')==24 and r('DpReady')==68 and r('DpHP')>0
  and r('NumberofLives')==2 and c.world==0,'Living Goku after the Star')
 if c.level==1 then
  buttons={}
  if not s.entered then s.entered=guestReturns end
  if guestReturns>=s.entered+25 and c.grounded then
   assert(s.max_x>=3136 and guestEntries==guestReturns,'Cleared stage through actual Goku movement')
   s.resumed=guestReturns-s.entered
   finish(true,'Goku cleared 1-1 and completed 25 more movement updates in 1-2')
  end
  return
 end
 assert(c.level==0,'Finish only through the 1-1 flagpole')
 if c.x>s.max_x then s.max_x=c.x;s.progress=guestReturns end
 assert(guestReturns-s.progress<720,'Full-level Goku route stopped progressing')
 local b=travel(c)
 if c.x>=2400 and c.x<2488 then
  if s.last_gap then b={right=true,a=true}
  elseif c.x<2434 then b={right=true}
  elseif ready(c) then s.last_gap=state();b={right=true,a=true}
  else b={} end
 end
 buttons=b
end
'''


def digest(data):
    return sha256(data).hexdigest()


def native_offset(pc):
    return 16 + NATIVE_BANK * 8192 + (pc & 8191)


def native_bank(raw, bank):
    start = 16 + bank * 8192
    return raw[start:start + 8192]


def assemble():
    SCRATCH.mkdir(exist_ok=True)
    with TemporaryDirectory(dir=SCRATCH) as temporary:
        work = Path(temporary)
        obj, config, output = (work / name for name in ('query.o', 'query.cfg', 'query.bin'))
        config.write_text('''MEMORY {
  QUERY: start=$B236, size=$C0, fill=yes, fillval=$EA;
  HIDDEN: start=$B83B, size=$22, fill=yes, fillval=$EA;
}
SEGMENTS { QUERY: load=QUERY, type=ro; HIDDEN: load=HIDDEN, type=ro; }
''')
        cc65 = ROOT / 'tools/Windows/cc65/bin'
        subprocess.run([cc65 / 'ca65.exe', ASSEMBLY, '-o', obj], check=True)
        subprocess.run([cc65 / 'ld65.exe', obj, '-C', config, '-o', output], check=True)
        return output.read_bytes()


def compose(parent):
    assert digest(parent) == BASE
    old = native_bank(parent, NATIVE_BANK)
    assert old[QUERY & 8191: (QUERY & 8191) + QUERY_SIZE] == PARENT_QUERY
    assert old[HELPER & 8191: (HELPER & 8191) + HELPER_SIZE] == PARENT_HELPER
    def entries(pc, opcodes):
        target = pc.to_bytes(2, 'little')
        return {0xA000 + i for i in range(len(old) - 2)
                if old[i] in opcodes and old[i + 1:i + 3] == target}

    assert entries(HELPER, (0x20, 0x4C)) == {0xB296}
    assert entries(QUERY, (0x20, 0x4C)) == {0xA880, 0xAE4D, 0xAE5E}
    assert entries(0xAE39, (0x20,)) == {0xB07F, 0xB0A0, 0xB0D7, 0xB0E1,
                                     0xB121, 0xB12B, 0xB144, 0xB14E}
    probe_owners = (0xA864, 0xAE50, 0xB06E, 0xB085, 0xB0BE, 0xB10E, 0xB131)
    signatures = {}
    for owner in probe_owners:
        for call in entries(owner, (0x20, 0x4C)):
            assert old[call & 8191] == 0x20
            stored = call + 2
            key = (stored >> 8) ^ (stored & 255)
            signatures.setdefault(key, set()).add(call + 3)
    assert signatures[0xE8] == {0xAF48} and signatures[0x87] == {0xAA2E}

    code = assemble()
    assert len(code) == QUERY_SIZE + HELPER_SIZE
    image = replace_spans(parent, code[:QUERY_SIZE], code[QUERY_SIZE:])
    assert digest(image) == CANDIDATE and recover_parent(image) == parent
    return image


def replace_spans(image, query, helper):
    result = bytearray(image)
    for pc, block in ((QUERY, query), (HELPER, helper)):
        at = native_offset(pc)
        result[at:at + len(block)] = block
    return bytes(result)


def recover_parent(image):
    assert digest(image) == CANDIDATE
    parent = replace_spans(image, PARENT_QUERY, PARENT_HELPER)
    assert digest(parent) == BASE
    return parent


def memory(raw):
    bus = bytearray(65536)
    for bank, address in ((126, 0x8000), (NATIVE_BANK, 0xA000), (127, 0xE000)):
        bus[address:address + 8192] = native_bank(raw, bank)
    return bus


def run_query(bus, point, screen, tile, foundation, caller, action, vertical):
    y, x = point
    world = screen + x
    block_buffer = 0x03D0 if world & 256 else 0x0300
    cell = block_buffer + ((y & 0xf0) - 32) + ((world & 255) >> 4)
    if 32 <= y < 240:
        bus[cell] = tile
        bus[(cell + 0x63D1) & 65535] = foundation
    bus[0x071D], bus[0x071F] = screen >> 8, screen & 255
    bus[0x5C00], bus[0x5C07] = action, vertical
    bus[3:11] = bytes(range(8))
    cpu = Replay.N.NesMPU(memory=bus, pc=QUERY)
    cpu.a, cpu.x, cpu.y, cpu.sp, cpu.p = y, 0x52, x, 0xE0, 0x71
    inner, outer = caller
    cpu.stPushWord(outer - 1)
    cpu.stPushWord(inner - 1)
    for _ in range(175):
        if cpu.pc == inner:
            break
        assert bus[cpu.pc] != 0, f'Invalid query branch at {cpu.pc:04X}'
        cpu.step()
    else:
        raise AssertionError('Terrain query did not return')
    registers = (cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp)
    scratch = bytes(bus[3:11] + bus[0x5C22:0x5C29] + bus[0x5C32:0x5C34])
    return registers, scratch, cpu.processorCycles


def verify_query(parent, image):
    bundle = Replay.W.Symbols.bundle()
    assert Replay.W.address(bundle, 'Block_Buffer_1') == 0x0300
    assert Replay.W.address(bundle, 'Block_Buffer_2') == 0x03D0
    assert Replay.W.address(bundle, 'GetBlockBufferAddr') == 0x95DC
    assert Replay.W.address(bundle, 'MTileAttribute') == 0xEF36
    buses = memory(parent), memory(image)
    ordinary = (0xAE61, 0xAEFA)
    cycles = []
    cases = 0
    for tile in range(256):
        for screen in (0x0011, 0x00F2, 0x01F2):
            for foundation in (0, 1):
                base, changed = [run_query(bus, (143, 37), screen, tile, foundation,
                                           ordinary, 3, 0xEC) for bus in buses]
                assert base[:2] == changed[:2], (tile, screen, foundation, base, changed)
                cycles.append(changed[-1] - base[-1])
                cases += 1

    head = (0xAE61, 0xAF48)
    producer = (0xB082, 0xAA2E)
    test_points = (
        (head, 2, 0xEC, 0x95), (head, 3, 0xEC, 0x95),
        (producer, 3, 0xED, 0x95), (head, 3, 9, 0),
        (head, 1, 0, 0), (head, 13, 0xEC, 0),
        ((0xAE61, 0xAF3B), 3, 0xEC, 0),  # Side sensor
        ((0xAE61, 0xAF2E), 3, 0xEC, 0),  # Same low return byte as producer
        ((0xB082, 0xAF37), 3, 0xEC, 0),  # Unrelated second caller
        ((0xB0CF, 0xAA4F), 3, 0xEC, 0),  # Ordinary attack probe
        ((0xA883, 0xA81D), 3, 0xEC, 0),  # Direct floor hazard query
    )
    hidden_cases = 0
    for tile in (0x5F, 0x60):
        for caller, action, vertical, expected in test_points:
            old, new = [run_query(bus, (143, 37), 0x00F2, tile, 0,
                                  caller, action, vertical) for bus in buses]
            assert old[0][0] == 0 and new[0][0] == expected, (tile, caller, new)
            assert old[0][1:3] == new[0][1:3] and old[0][4] == new[0][4]
            assert old[0][3] & 0x7D == new[0][3] & 0x7D
            assert new[1][:9] + new[1][10:] == old[1][:9] + old[1][10:]
            assert new[1][9] == expected
            hidden_cases += 1
    for point in ((0, 200), (31, 252), (240, 12), (255, 254)):
        old, new = [run_query(bus, point, 0x01FE, 0, 0, head, 3, 0xED) for bus in buses]
        assert old[:2] == new[:2]
    return dict(native_tile_cases=cases, hidden_context_cases=hidden_cases,
                boundary_cases=4, other_tile_cycle_change=[min(cycles), max(cycles)])


def program(parent, image, route):
    with patch.object(Replay, 'OWNED', SCRATCH):
        if route == 'flower':
            with patch.object(Replay.Flower, 'OWNED', SCRATCH):
                previous = Replay.Flower.controller(parent)
        else:
            previous = Replay.controller(parent, 'star' if route == 'stage' else route)
    # The installed observer's entry windows are outside the rewritten code,
    # apart from the terrain query's unchanged instruction prefix.
    assert parent[native_offset(QUERY):native_offset(QUERY) + 12] == image[
        native_offset(QUERY):native_offset(QUERY) + 12]
    assert previous.count(BASE.encode()) == 1
    controller = previous.replace(BASE.encode(), digest(image).encode(), 1)
    if route != 'stage':
        return controller
    once = Replay.First.once
    text = controller.decode()
    text = once(text, 'local function drive()', STAGE_DRIVE + '\nlocal function drive()\n'
                ' if F.stage then stageDrive();return end')
    text = once(text, " finish(true,'Natural Goku Mushroom then '..C.route..', actual native effect and25 completed original workers')",
                ' F.stage={max_x=0,progress=guestReturns};food.phase=\'after-star\'')
    text = once(text, 'mainReturns>4000', 'mainReturns>6400')
    text = once(text, 'full_stage_claim=false', 'full_stage_claim=ok,level=r(\'LevelNumber\')')
    Replay.Stock.LuaRuntime().compile(text)
    return text.encode()


def native(parent, image, route, *, install=False):
    stock = Replay.Stock
    out = stock.OUT
    target, script = out / 'candidate.nes', out / 'controller.lua'
    previous = script.read_bytes()
    installed = ROM.read_bytes()
    guard = stock.check(ROM)
    assert guard['ROM_sha256'] in (BASE, CANDIDATE) and not guard['matching_patch_files']
    assert set(out.iterdir()) == {target, script} and target.read_bytes() == installed
    controller = program(parent, image, route)
    if install:
        assert 'stage' in NATIVE_RECEIPTS and installed == parent and route == 'life'
    launch = ROM if install else target
    require_free_workspace(ROOT, launch, allow_interactive=True)
    committed = False
    try:
        if installed != image:
            launch.write_bytes(image)
        loaded = stock.check(launch)
        assert loaded['ROM_sha256'] == CANDIDATE and not loaded['matching_patch_files']
        script.write_bytes(controller)
        result = stock.run(script, launch, out / 'capture', CANDIDATE, 230)
        assert result['script_SHA256'] == digest(controller)
        assert result['outputs_written'] == 0 and not result['images']
        assert launch.read_bytes() == image and stock.check(launch) == loaded
        if install:
            assert result['passed'] and result['receipt_SHA256'] == NATIVE_RECEIPTS['life']
            target.write_bytes(image)
            assert target.read_bytes() == ROM.read_bytes() == image and stock.check(ROM) == loaded
            committed = True
        print('GOKU HIDDEN HEAD NATIVE ' + json.dumps(dict(route=route, report=result),
                                                       separators=(',', ':')), flush=True)
        return result
    finally:
        script.write_bytes(previous)
        if not committed:
            if launch.read_bytes() != installed:
                launch.write_bytes(installed)
            if install and target.read_bytes() != installed:
                target.write_bytes(installed)
            assert stock.check(ROM) == guard and target.read_bytes() == installed
        assert set(out.iterdir()) == {target, script}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--run', action='append', choices=('life', 'star', 'flower', 'stage'), default=[])
    mode.add_argument('--install', action='store_true')
    args = parser.parse_args()
    installed = ROM.read_bytes()
    parent = recover_parent(installed) if digest(installed) == CANDIDATE else installed
    image = compose(parent)
    result = verify_query(parent, image)
    print('GOKU HIDDEN HEAD SOURCE ' + json.dumps(dict(result, candidate=digest(image),
        assembly_SHA256=digest(ASSEMBLY.read_bytes())), separators=(',', ':')), flush=True)
    for route in args.run:
        if not native(parent, image, route)['passed']:
            return 1
    if args.install:
        assert native(parent, image, 'life', install=True)['passed']
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
