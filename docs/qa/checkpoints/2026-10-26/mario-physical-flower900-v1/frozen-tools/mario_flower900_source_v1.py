"""Bind the real later block and document the unchanged Mario/Luigi Hard dispatch gap."""
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
    start = location(b, 'L_GroundArea6')
    data = b['raw'][start:start + 28]
    page, authored = 0, []
    for i in range(13):
        first, second = data[2 + i * 2:4 + i * 2]
        assert first & 15 <= 12, 'This bounded prefix contains no page-set control rows'
        if second & 128:
            page += 1
        if second & 127 == 0:
            authored.append(dict(pair=i, pair_bytes=[first, second],
                                 x=page * 256 + (first >> 4) * 16,
                                 y=32 + (first & 15) * 16))
    assert [r['x'] for r in authored] == [336, 1248]
    assert all(r['y'] == 144 for r in authored)
    source = a.rom.parent / 'source/src'
    rows = []
    for mode, power, kind in [(0, 0, 0), (0, 1, 1), (1, 1, 0), (1, 0, 1)]:
        for char, owner in [(0, 'MarioSourceBeginPowerup'), (8, 'GuestBeginPowerup')]:
            q = Arena(b, char=char)
            q.put(CrossoverBehaviorVersion=mode, PlayerStatus=power,
                  GuestPowerupActive=0, GuestPowerupTarget=0)
            q.set('PowerUpType', kind, 5)
            q.invoke(owner, x=5)
            active = q.get('GuestPowerupActive')
            target = q.get('GuestPowerupTarget') if active else power
            expected = (min(2, power + 1) if char == 8 or mode == 0 else max(power, kind + 1))
            assert target == expected
            rows.append(dict(character=char, mode=mode, before_power=power, authored_type=kind,
                             actual_assembled_begin_owner=owner, actual_active=active,
                             eventual_target=target))
    contacts = []
    for char in [0, 8]:
        q = Arena(b, char=char)
        q.put(CrossoverBehaviorVersion=1)
        c, _ = q.invoke('MarioSourceFireballBrick', a=0x51)
        assert bool(c.p & 1) == (char == 0)
        contacts.append(dict(character=char, Hard_brick51_passthrough=bool(c.p & 1)))
    result = dict(passed=True, source_CPU_only=True, native_executed=False,
                  ROM_sha256=sha(a.rom), real_level_prefix=authored,
                  authored_powerup_delivery='MushFlowerBlock initializes0; UnionPwrUpCore samples actual PlayerStatus, so retainedSuper yields flower1',
                  source_files={n: sha(source / n) for n in ['level_tiles.s', 'union_rare.s',
                               'mario_source.s', 'guest_powerups.s', 'luigi_native.s', 'inventory.s',
                               'object.s', 'collision.s']},
                  begin_component_cases=rows, brick_component_cases=contacts,
                  Hard_compatibility_gap_is_documentation_not_game_patch=True,
                  full_collision_dispatch='MarioSourcePowerupCollision -> unsupported inventory fallback -> SelectedCharacter0 MarioSourceBeginPowerup; SelectedCharacter8 GuestBeginPowerup',
                  tool_sha256=sha(__file__),
                  scope='Actual compiled level bytes and eight isolated begin-owner/two brick helper calls. No physical flower acquisition, transform completion, enemy/brick firing, natural rarity/reachability, IRQ/PPU or native result. Hard mismatch is an unchanged source compatibility question, not an authorized fix.')
    (a.output / 'proof.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(passed=True, authored_blocks=[336, 1248], begin_cases=8,
                          brick_cases=2, proof_sha256=sha(a.output / 'proof.json')), indent=2))


if __name__ == '__main__':
    main()
