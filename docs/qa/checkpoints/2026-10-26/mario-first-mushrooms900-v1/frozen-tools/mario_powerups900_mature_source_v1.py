"""Execute the actual SMB3 mushroom preparation/rise/admission components."""
from pathlib import Path
import argparse
import hashlib
import json

from check_tmnt_render_oa import address, load, location
from robots_weapon_cpu_v1 import Arena


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    assert sha(a.rom) == '900b669e212b878041c23e438f2fb26e310ce8f929f904681a9c4b17405b6968'
    b = load(a.rom)
    n = 'M3RisePickup'
    start, pc = location(b, n), address(b, n)
    code = b['raw'][start:start + int(b['syms'][n]['size'], 0)]
    at = address(b, 'PowerUpType')
    assert at == 0x34
    pattern = bytes([0xa9, 0, 0x95, 0x34])
    off = code.index(pattern)
    assert pc + off == 0xa441 and (start - 16) // 8192 == 90
    rows = []
    for variant in [0, 1]:
        q = Arena(b, char=17)
        q.put(M3Variant=variant, M3Marker=0xb3, M3Form=0, PlayerStatus=0,
              TimerControl=0, CrossoverBehaviorVersion=0)
        for field, value in [('Enemy_ID', 0x2e), ('Enemy_Flag', 1), ('Enemy_State', 1),
                             ('Enemy_Y_Position', 136), ('PowerUpType', 0),
                             ('InvPickup', 0xfc), ('InvPickupOwner', 0xff)]:
            q.set(field, value, 5)
        q.invoke('M3PreparePickup', x=5)
        assert q.get('InvPickup', 5) == 0xd1 and q.get('InvPickupOwner', 5) == 17
        assert q.get('PowerUpType', 5) == 1 and q.get('InvRisePhase', 5) == 0
        history = []
        for tick in range(1, 49):
            before = q.get('Enemy_State', 5)
            c, _ = q.invoke('M3PickupCollision', x=5)
            assert not c.p & 1, ('No early collection', variant, tick, before)
            c, _ = q.invoke('M3RisePickup', x=5)
            expected_state = 0x80 if tick == 48 else 1 + tick // 3
            assert q.get('Enemy_State', 5) == expected_state
            assert q.get('InvRisePhase', 5) == tick % 3
            assert q.get('Enemy_Y_Position', 5) == 136 - tick // 3
            assert q.get('PowerUpType', 5) == (0 if tick == 48 else 1)
            assert q.get('InvPickup', 5) == 0xd1 and q.get('InvPickupOwner', 5) == 17
            history.append(dict(tick=tick, state=expected_state, type=q.get('PowerUpType', 5),
                                y=q.get('Enemy_Y_Position', 5), rise_phase=q.get('InvRisePhase', 5)))
        c, _ = q.invoke('M3PickupCollision', x=5)
        assert c.p & 1, 'Fully emerged walking mushroom admitted'
        assert q.get('Enemy_X_Speed', 5) == 16 and q.get('Enemy_MovingDir', 5) == 1
        rows.append(dict(variant=variant, ticks=history, early_collision_refusals=48,
                         mature_collision_allowed=True, final_type=0, final_stamp=0xd1,
                         original_native_1_type_assertion_rejected=True))
    z = dict(passed=True, source_CPU_only=True, native_executed=False,
             ROM_sha256=sha(a.rom), cases=rows, total_rise_ticks=96,
             actual_bank=90, LDA_PC=0xa441, STA_PC=0xa443,
             actual_instructions=list(pattern), target=0x34,
             genuine_prepare_rise_collision_no_traps=True,
             tool_sha256=sha(__file__),
             scope='Actual assembled components in explicit isolated legal RAM fixtures. Native delivery begins type0; source preparation sets transient1;48 rise updates set mature walking0. No Mesen/real block/control/IRQ/PPU/DMA or growth/ability verdict.')
    (a.output / 'proof.json').write_text(json.dumps(z, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(passed=True, variants=2, rise_ticks=96, STA_PC=0xa443,
                          proof_sha256=sha(a.output / 'proof.json')), indent=2))


if __name__ == '__main__':
    main()
