"""Rebase the visible DK Jr candidate and prepare its first natural route probe."""
import argparse
import json
from pathlib import Path

import audit_dkjr_installed_ingress_1108_v1 as I
import prepare_dkjr_oam_slot_1109_v1 as OAM
import prepare_dkjr_visible_current_1109 as V

R = I.R
OUT = R / 'build/dkjr-current-route-1110'
BASE = R / 'build/mini-box-terrain-visible-1110/candidate.nes'
BASE_SHA = '6af068b73709880ee5e2e07c8d9c9df1724bde1774f2dc67f16dff32bb73d018'
PIN = '5f2926ae145059a56cb09e700141459b0a70172d83eb4faf8bb003ce9852bb75'
OAM_MANIFEST = OAM.OUT / 'oam-source.json'
OAM_VECTORS = OAM.OUT / 'oam-IRQ-current.json'
FRONTEND_PROOF = I.O / 'frontend-v2.json'
ROUTE_SOURCE = R / 'tools/audit/dkjr_first_pipe_1110_v1.lua'
PREVIOUS = R / 'build/dkjr-visible-current-1109/dkjr-private.nes'


def pinned_inputs():
    base = BASE.read_bytes()
    assert I.sha(base) == BASE_SHA
    frontend = json.loads(FRONTEND_PROOF.read_text())
    oam = json.loads(OAM_MANIFEST.read_text())
    irq = json.loads(OAM_VECTORS.read_text())
    assert frontend['passed'] and oam['passed'] and irq['passed']
    assert oam['base_SHA256'] == frontend['expected_memory_only_SHA256']
    previous = bytearray(OAM.MINI_PRIVATE.read_bytes())
    previous_claimed = set()
    V.apply(previous, oam['patches'], previous_claimed)
    assert I.sha(previous) == oam['memory_only_hashes'][OAM.sha(OAM.MINI_PRIVATE.read_bytes())]
    V.apply(previous, frontend['patches'], previous_claimed)
    assert I.sha(previous) == I.sha(PREVIOUS.read_bytes()) == irq['memory_only_SHA256']
    raw = bytearray(base)
    claimed = set()
    for group in (frontend, oam):
        V.apply(raw, group['patches'], claimed)
    assert I.sha(raw) == PIN
    patches = frontend['patches'] + oam['patches']
    cookie, = (bytes.fromhex(row['new_hex']) for row in oam['patches'] if row.get('physical_PRG') == 65)
    return bytes(raw), patches, cookie, oam['labels']


def controller(cookie, labels):
    symbols = I.SYMBOLS.bundle()
    block = I.UI.address(symbols, 'Block_Buffer_1')
    native = json.loads(V.LAYOUT.read_text())['labels']
    cfg = dict(pin=PIN, main=native['DkNativeMain'], draw=labels['DkNativeDraw'],
               cookie=list(cookie), block=block)
    source = V.observer(cfg)
    anchor = "emu.addMemoryCallback(function() polled=true end,emu.callbackType.read,0x4016)"
    source = OAM.replace_once(source, anchor, ROUTE_SOURCE.read_text() + '\n' + anchor)
    anchor = " elseif phase=='right' then keys.right=true"
    source = OAM.replace_once(source, anchor, " elseif phase=='first-pipe' then keys=pipeInput()\n" + anchor)
    source = OAM.replace_once(source, "frame=frame+1;assert(frame<3000,'Bounded DK Jr launch and motion')",
        "frame=frame+1;assert(frame<4800,'Bounded DK Jr launch and motion')\n"
        " if phase=='first-pipe' and pipeTick() then return end")
    anchor = """    local f=assert(io.open(OUTPUT..'result.json','w'))
    f:write(json({passed=true,ROM_sha256=C.pin,controller_only=true,frames=frame,
     source_main_calls=updates,source_draw_calls=draws,cadence=cadence,minY=minimumY,body=body,full_stage=false})..'\\n');f:close()
    done=true;emu.stop(0)"""
    return OAM.replace_once(source, anchor, "    smokePassed=true;begin('first-pipe')")


def first_pipe(raw):
    b = I.SYMBOLS.bundle()
    b['raw'] = raw
    m = I.N.fresh(b)
    I.N.put(m, AreaPointer=37, WorldNumber=0, LevelNumber=0, Hidden1UpFlag=1, SelectedCharacter=40)
    I.N.invoke(m, 'GetAreaDataAddrs')
    assert I.N.get(m, 'AreaAddrsLOffset') == 5
    lengths = I.UI.address(b, 'AreaObjectLength')
    m[lengths:lengths + 3] = bytes([255]) * 3
    tile = I.UI.address(b, 'MetatileBuffer')
    columns = []
    for _ in range(30):
        I.N.invoke(m, 'AreaParserCore')
        columns.append(list(m[tile:tile + 13]))
        I.N.invoke(m, 'IncrementColumnPos')
    cap = [columns[x][9] for x in [28, 29]]
    shaft = [columns[x][10] for x in [28, 29]]
    assert cap in ([0x10, 0x11], [0x12, 0x13]) and shaft == [0x14, 0x15], (cap, shaft)
    assert not any(c[9] in (0x10, 0x12) and n[9] in (0x11, 0x13)
                   for c, n in zip(columns[:28], columns[1:29]))
    return dict(left=448, right_exclusive=480, top=176, cap=cap, shaft=shaft,
                vine_cells=0, actual_native_parser=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--rom', type=Path, help='Bind the prepared observer to a root-emitted private ROM.')
    ap.add_argument('--refresh-plan', action='store_true', help='Replace this task’s as yet unbound controller plan.')
    args = ap.parse_args()
    raw, patches, cookie, labels = pinned_inputs()
    lua = controller(cookie, labels)
    receipt = OUT / 'rebase.json'
    plan = OUT / 'controller-plan.lua'
    refs = [Path(__file__), BASE, PREVIOUS, FRONTEND_PROOF, OAM_MANIFEST, OAM_VECTORS, ROUTE_SOURCE, V.SOURCE, V.LAYOUT]
    if args.rom:
        proof = json.loads(receipt.read_text())
        assert proof['passed'] and proof['memory_only_SHA256'] == PIN
        assert lua == plan.read_text()
        for name, digest in proof['bindings'].items():
            assert I.sha((R / name).read_bytes()) == digest, name
        V.prepare(OUT / 'native', args.rom, lua, [*refs, receipt, plan], expected=PIN, timeout=240,
                  allow_interactive=True,
                  scope='Controller-only cold DK Jr, visible OAM DMA, idle cadence, original hop and natural unassisted first pipe. Records bounded contact or obstruction.')
        return

    cpu = I.cpu(raw, cookie)
    geometry = first_pipe(raw)
    OUT.mkdir(exist_ok=True)
    assert not (OUT / 'native').exists()
    assert args.refresh_plan or not receipt.exists() and not plan.exists()
    plan.write_text(lua, encoding='utf-8', newline='\n')
    result = dict(passed=True, ROM_written=False, parent_SHA256=BASE_SHA, memory_only_SHA256=PIN,
                  patches=patches, cookie=cookie.hex(), CPU_cold_controls=cpu, native_parser_geometry=geometry,
                  bindings={p.relative_to(R).as_posix(): I.sha(p.read_bytes()) for p in refs},
                  scope='Exact current preimages, no fresh ownership grants. CPU ingress and controls use a legal flat fixture; native route still needs the root queue.')
    receipt.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print('Current DK Jr rebase', PIN, len(patches), 'exact patches', flush=True)


if __name__ == '__main__':
    main()
