"""Compare the side loop with actual native effects on exact installed code."""
from collections import Counter
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

import profile_sonic_empty_cpu_1110 as Native
from profile_sonic_snapshot_leaf_1110 import PIN, parent_bytes
from sonic_sms_compact_cold_worker_1110 import assemble


W, N = Native.W, Native.N
SOURCE = Path(__file__).resolve().parents[1] / 'reference/sonic_sms_side_batch_1110.s'
BASE, BATCH, EFFECT = 0x9C6E, 0xDA40, 0x9CB6
CHR = 16 + 1024 * 1024
PROBE = 0xE497


def offset(bank, pc):
    return 16 + bank * 8192 + (pc & 8191)


def prepare(raw):
    assert sha256(raw).hexdigest() == PIN
    meta = raw[CHR + 328*1024:CHR + 329*1024]
    scene_side = int.from_bytes(meta[0x100 + 14*3 + 1:0x100 + 15*3], 'little')
    assert meta[0x100 + 14*3] == 0x4c and 0xd2e9 <= scene_side < 0xd31b
    assert meta[scene_side-0xd000:scene_side-0xd000+9] == bytes.fromhex('a50fc908f0034c8b95')
    bundle = W.Symbols.bundle()
    bundle['raw'] = raw
    assert [W.address(bundle, name) for name in ('DoPlayerSideCheck', 'CheckSideMTiles',
        'CrossoverSourceSideProbe', 'MTileAttribute')] == [BASE, EFFECT, PROBE, 0xEF36]
    imports = dict(SideAdder=0x106, PlayerY=0xbd, R0=3, SceneSide=scene_side,
                   MTileAttribute=0xef36, SideEffect=EFFECT)
    code = assemble(''.join(f'{name} = ${at:04x}\n' for name, at in imports.items()) +
                    SOURCE.read_text(encoding='ascii'), {'SONIC_SIDE_BATCH': (BATCH, 96)})
    leaf = code['images']['SONIC_SIDE_BATCH']
    assert raw[CHR+334*1024+BATCH-0xd800:CHR+334*1024+BATCH-0xd800+len(leaf)] == b'\xff'*len(leaf)
    original = raw[offset(126, BASE):offset(126, EFFECT)]
    # Native relative control flow through the lower-miss loop is unchanged.
    assert len(original) == 72 and len(leaf) == 75
    for i in (0x9c85-BASE, 0x9cac-BASE):
        assert original[i:i+3] == bytes.fromhex('2097e4')
        assert leaf[i:i+3] == b'\x20' + scene_side.to_bytes(2, 'little')
    lower_hit = 0x9caf-BASE
    differences = set(i for i in range(len(original)) if original[i] != leaf[i])
    assert differences <= {0x9c86-BASE, 0x9c87-BASE, 0x9cad-BASE, 0x9cae-BASE, lower_hit+1}
    assert leaf[-3:] == b'\x4c' + EFFECT.to_bytes(2, 'little')
    seed = N.fresh(bundle)
    N.put(seed, OperMode=1, OperMode_Task=3, SelectedCharacter=43, NumberofLives=2,
          NmiDisable=255, DisableScreenFlag=0, Player_Y_HighPos=1, CurrentBank=148, CurrentBankC=2)
    seed.raw_page(1, 148)
    seed.raw_page(2, 2)
    seed.ram[2][0x1000:0x1400] = meta
    cookie = raw[offset(126, 0x88d8):offset(126, 0x88d8)+16]
    assert cookie.hex() == 'a72b018c2e04635376b3ef263b330c8f'
    for bank in (2, 3):
        seed.ram[bank][0x1fe0:0x1ff0] = cookie
    return seed, leaf, scene_side


def run(m, pc, a, x, y, p, scene_side):
    cpu = N.NesMPU(memory=m, pc=pc)
    cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp = a, x, y, p, 222
    cpu.stPushWord(0x5aff)
    counts = Counter()
    for _ in range(20000):
        if (cpu.pc, cpu.sp) == (0x5b00, 222):
            return (cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp), cpu.processorCycles, counts
        tag = m.rawtags[(cpu.pc - 0x8000)//8192] if cpu.pc >= 0x8000 else -1
        if (tag, cpu.pc) in ((193, 0xaf27), (254, EFFECT), (254, 0x958b), (2, scene_side)):
            counts[tag, cpu.pc] += 1
        assert m[cpu.pc], ('BRK', tag, hex(cpu.pc))
        cpu.step()
    raise AssertionError(hex(cpu.pc))


def main():
    seed, leaf, scene_side = prepare(parent_bytes())
    outcomes, effects = Counter(), Counter()
    test = list(product((16, 31, 32, 112, 176, 207, 208, 227, 228),
                        (0, 0x1c, 0x23, 0x24, 0x25, 0x6b, 0x6c, 0x1f, 0xc2, 0xc3, 0x54)))
    for i, (height, tile) in enumerate(test):
        old, new = (N.fork(seed) for _ in range(2))
        for m in (old, new):
            N.put(m, Player_X_Position=(24, 244, 253)[i % 3], Player_PageLoc=i & 1,
                  Player_Y_Position=height, PlayerFacingDir=(1, 2)[i & 1], Player_State=0,
                  GameEngineSubroutine=8, AreaType=1)
            m[0x106] = (0, 7, 14)[i % 3]
            for at in range(0x300, 0x4a0):
                m[at] = tile
            W.clear_logs(m)
        at = BATCH - 0xc000
        new.ram[2][at:at+len(leaf)] = leaf
        args = (height, i & 15, (i * 13) & 255, (0x31, 0x34, 0xb1, 0x71)[i % 4], scene_side)
        a, ca, hit_a = run(old, BASE, *args)
        b, cb, hit_b = run(new, BATCH, *args)
        assert a == b, ((height, tile), a, b, hit_a, hit_b)
        assert old.rawtags == new.rawtags
        for lo, hi in ((0, 0x100), (0x100, 0x15a), (0x17b, 0x180), (0x200, 0x800), (0x6000, 0x8000)):
            assert old[lo:hi] == new[lo:hi], ((height, tile), lo,
                [(hex(k), old[k], new[k]) for k in range(lo, hi) if old[k] != new[k]][:10])
        hits = hit_a[193, 0xaf27]
        assert hits == hit_a[2, scene_side] == hit_b[2, scene_side] and not hit_b[193, 0xaf27]
        assert hit_a[254, EFFECT] == hit_b[254, EFFECT]
        effects[tile] += hit_b[254, EFFECT]
        outcomes[hits, ca-cb] += 1
    assert effects[0xc2] and effects[0x6c] and any(hits == 4 for hits, _ in outcomes)
    print(json.dumps(dict(passed=True, SHA256=PIN, cases=len(test), private_batch_bytes=len(leaf),
        batch_body_cycles_saved=[dict(probes=h, cycles=c, cases=n) for (h,c),n in sorted(outcomes.items())],
        effect_entries=sum(effects.values()), output_files=0,
        scope='Already-authenticated direct CPU leaf proof. Host ingress, complete auth/cold/lifecycle and IRQ checks pending.')), flush=True)


if __name__ == '__main__':
    main()
