"""Deliver the tested Mini optimization using the existing guarded installer."""
import json
import sys
from pathlib import Path

import deliver_mini_nightly_root_1103_v30 as delivery


def main():
    delivery.O = delivery.R/'build/mini-optimized-delivery-1103'
    delivery.PREVIOUS = '4ff069b3474077a1f3f8924b530780dee7a81c2a32d759f8fbe2defcf91e3f4c'
    rom = Path(sys.argv[sys.argv.index('--rom')+1])
    pin = delivery.sha(rom)
    for name, required in [('mini-final-full11-1103', 'full_stage'),
                           ('mini-final-power-1103', 'earned_power')]:
        result = delivery.proof(delivery.R/'build'/name, pin)
        assert result[required]
    smoke = delivery.R/'build/mini-final-idle-1103'
    delivery.proof(smoke, pin)
    timing = json.loads((smoke/'capture/timing.json').read_text())
    assert timing['ROM_sha256'] == pin
    for phase in ['idle', 'right', 'left', 'brake', 'jump', 'landing']:
        cadence = timing['cadence'][phase]
        assert cadence['physical'] == cadence['updates']
        assert cadence['lag_nmi'] == cadence.get('no_controller_read', 0) == 0
    assert timing['cadence']['idle']['updates'] == 180
    fire_packet = delivery.R/'build/mini-final-fireball-1103'
    fire = json.loads((fire_packet/'capture/result.json').read_text())
    binding = json.loads((fire_packet/'capture/binding.json').read_text())
    assert fire['passed'] and fire['ROM_sha256'] == binding['ROM_sha256'] == pin
    assert binding['exit_code'] == 0
    assert binding['ready_sha256'] == delivery.sha(fire_packet/'ready.json')
    enemy = json.loads((delivery.R/'build/mini-fireball-enemy-cpu-1103/result.json').read_text())
    assert enemy['passed'] and enemy['ROM_SHA256'] == pin
    assert enemy['actual_full_GameCoreRoutine'] and enemy['native_fireball_Goomba_defeat']
    delivery.main()
    if sys.argv[1] != 'finalize':
        return
    receipt_path = delivery.O/'verified-delivery.json'
    receipt = json.loads(receipt_path.read_text())
    receipt.update(idle_cadence=timing['cadence'],
                   fireball_verification=fire, fireball_native_enemy_CPU=enemy,
                   verification_scope='Exact candidate and Downloads launch. '
                   '180 idle updates, walking both ways, braking, jump and landing. '
                   'Full non-shortcut 1-1, earned mushroom and a focused powered '
                   'fireball fixture. Busy-stage lag remains under investigation.')
    receipt_path.write_text(json.dumps(receipt, indent=2)+'\n')
    (delivery.O/'release-notes.txt').write_text(
        'Current MMC5 work-in-progress nightly.\n\n'
        'Apply this sole IPS to clean, headered Super Mario Bros. (World).\n'
        f'Base SHA-256: {receipt["base_SHA256"]}\n'
        f'Patched ROM SHA-256: {pin}\n\n'
        'Mini Mario is a Mario alternate. Press Select until MINI MARIO. '
        'The empty-area idle, walking, turning, jump and landing replay has '
        'zero measured skipped NMIs or missing controller polls. '
        'Busy sections of 1-1 can still lag. '
        'Fire Mini Mario now fires one native bouncing projectile with a 4x4 '
        'graphic. Full 1-1 and earned mushroom collection passed. '
        'Fireball tests use an explicitly powered fixture. '
        'Start a fresh game after reopening the ROM.\n', encoding='utf-8')


if __name__ == '__main__':
    main()
