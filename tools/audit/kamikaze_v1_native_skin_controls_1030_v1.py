"""Compare complete native Mario updates with the corrected visual-only skin."""
from pathlib import Path
import argparse
import itertools
import json
import sys

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R / 'tools/audit'), str(R / 'tools')]
from sunny_integrated_controls_v1 import scoped_load, seed, run, address, sha, registers, app


def setup(b, variant, area, tier, mode, face, keys):
    q = seed(b, 0)
    run(q, 'X5ColdInit')
    q.put(CrossoverMenuIndex=0, MarioVariant=variant, PlayerStatus=tier,
          PlayerSize=int(tier == 0), CurrentPlayer=0, VRAM_Buffer1_Offset=0,
          VRAM_Buffer2_Offset=0, CrossoverBehaviorVersion=mode,
          PlayerFacingDir=face)
    run(q, 'MenuResolveCharacter')
    run(q, 'GetAreaType', a=area << 5)
    run(q, 'QueueSelection')
    q.put(VRAM_Buffer1_Offset=0, VRAM_Buffer2_Offset=0, GameTimerDisplay=4,
          PlayerEntranceCtrl=2, SavedJoypadBits=keys, Left_Right_Buttons=keys & 3,
          A_B_Buttons=keys & 192)
    for k in range(84):
        q.m[address(b, 'VRAM_Buffer1') + k] = 0
    return q


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--rom', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    assert not a.output.exists()
    b = scoped_load(a.rom)
    allowed = {address(b, name) for name in ['MarioVariant', 'X5ChrMode', 'X5WideChrActive']}
    costs, count, objects = [], 0, set()
    for area, tier, mode, face, keys in itertools.product(range(4), range(3), [0, 1], [1, 2], [0, 1, 129]):
        pair = [setup(b, v, area, tier, mode, face, keys) for v in [0, 3]]
        for age in range(2):
            results = []
            for q in pair:
                q.put(VRAM_Buffer1_Offset=0, VRAM_Buffer2_Offset=0)
                c, writes, _ = run(q, 'GameLoop', p=0x71)
                # Compare every application byte (including complete software
                # OAM), genuine returned registers, maps and live short RAM.
                live = bytes(q.m[i] for i in range(0x100, 0x17b))
                results.append((registers(c), app(q, skip=allowed), q.m.banks[:], live,
                                c.processorCycles))
            assert results[0][:4] == results[1][:4], ('native complete Main differs', area, tier, mode, face, keys, age)
            assert pair[1].get('ObjectMetasprite') != 233, 'Skin must use native Mario descriptors'
            objects.add(pair[1].get('ObjectMetasprite'))
            costs.append(results[1][4] - results[0][4])
            count += 1
    palettes = []
    for current, tier in itertools.product([0, 1], range(3)):
        values = []
        for variant in [0, 3]:
            q = seed(b, 0)
            q.put(MarioVariant=variant, CurrentPlayer=current, PlayerStatus=tier,
                  VRAM_Buffer1_Offset=0, VRAM_Buffer2_Offset=0)
            c, _, _ = run(q, 'GetPlayerColors')
            n = q.get('VRAM_Buffer1_Offset')
            values.append(list(q.m[address(b, 'VRAM_Buffer1'):address(b, 'VRAM_Buffer1') + n + 1]))
        assert values[0] == values[1], ('native player palette', current, tier)
        palettes.append(dict(player=current, tier=tier, queue=values[0]))
    # Actual publisher substitutes precisely window0; all world windows and
    # software descriptors/flags remain native, including the real NMI helper.
    published = []
    for page in range(16, 20):
        pair = []
        for variant in [0, 3]:
            q = setup(b, variant, 1, 0, 0, 1, 0)
            q.set('CurrentCHRBank', page)
            c, writes, _ = run(q, 'X5PublishChr')
            upper, pages = 0, {}
            for at, v in writes:
                if at == 0x5130:
                    upper = v & 3
                if 0x5120 <= at <= 0x512b:
                    pages[at - 0x5120] = upper * 256 + v
            pair.append(pages)
        assert pair[1][0] == 696 + page - 16
        assert all(pair[0][i] == pair[1][i] for i in range(1, 12))
        published.append(pair[1][0])
    result = dict(passed=True, ROM_sha256=sha(a.rom), complete_native_Main_pairs=count,
                  native_OAM_descriptors_hitboxes_physics_gameplay_RAM_registers_maps_exact=True,
                  live_short_RAM_and_33SMC_compared=True,
                  allowed_visual_identity_fields=['MarioVariant', 'X5ChrMode[0]', 'X5WideChrActive'],
                  CPU_delta=[min(costs), max(costs)], native_Mario_objects=sorted(objects),
                  palette_pairs=palettes, actual_published_skin_pages=published,
                  world_CHR_windows_unchanged=True, native_playthrough_pending=True,
                  bindings={str(p.resolve()): sha(p) for p in [Path(__file__), a.rom, a.rom.with_suffix('.dbg'),
                            R / 'tools/audit/sunny_integrated_controls_v1.py',
                            R / 'build/kamikaze-v1-skin-art-1030-v1/art.json']})
    a.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ['bindings', 'palette_pairs']}))


if __name__ == '__main__':
    main()
