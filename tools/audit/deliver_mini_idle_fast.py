"""Install, then qualify the exact faster Mini nightly from Downloads."""
import json
import sys

import deliver_mini_nightly_root_1103_v30 as delivery
from build_mini_frame_auth_1103 import PARENT


delivery.O = delivery.R/'build/mini-idle-delivery-1103'
delivery.PREVIOUS = PARENT


def check_native(name, pin):
    packet = delivery.R/'build'/name
    result = json.loads((packet/'capture/result.json').read_text())
    binding = json.loads((packet/'capture/binding.json').read_text())
    assert result['passed'] and result['ROM_sha256'] == binding['ROM_sha256'] == pin
    assert binding['exit_code'] == 0 and binding['ready_sha256'] == delivery.sha(packet/'ready.json')
    return result


def main():
    pin = '4ff069b3474077a1f3f8924b530780dee7a81c2a32d759f8fbe2defcf91e3f4c'
    assert check_native('mini-idle-final-full11-1103', pin)['full_stage']
    assert check_native('mini-idle-final-power-1103', pin)['earned_power']['completed']
    before, after = [json.loads((delivery.R/'build'/f'mini-idle-120-{side}-1103/capture/timing.json').read_text())
                     for side in ['before', 'after']]
    assert [before['ROM_sha256'], after['ROM_sha256']] == [PARENT, pin]
    assert [q['cadence']['idle']['no_controller_read'] for q in (before, after)] == [180, 120]
    delivery.main()
    if sys.argv[1] != 'finalize':
        return
    smoke = delivery.O/'downloads-smoke/capture/timing.json'
    timing = json.loads(smoke.read_text())
    assert timing['ROM_sha256'] == pin and timing['cadence']['idle'] == after['cadence']['idle']
    path = delivery.O/'verified-delivery.json'
    receipt = json.loads(path.read_text())
    receipt['verification_scope'] = '120-update idle trace and real Downloads launch; exact full non-shortcut 1-1 and earned mushroom replays.'
    receipt['idle_before_after'] = [q['cadence']['idle'] for q in [before, after]]
    path.write_text(json.dumps(receipt, indent=2)+'\n')
    notes = delivery.O/'release-notes.txt'
    notes.write_text(
        'Current MMC5 work-in-progress nightly.\n\n'
        'Apply this sole IPS to clean, headered Super Mario Bros. (World).\n'
        f'Base SHA-256: {receipt["base_SHA256"]}\n'
        f'Patched ROM SHA-256: {pin}\n\n'
        'Mini Mario is under Mario: press Select until MINI MARIO. '
        'His idle performance is improved. The same 120 idle updates in Mesen now span '
        '180 video frames instead of 240, with 120 frames without a controller poll instead of 180. '
        'Lag remains. Full 1-1 and the earned mushroom growth replay passed.\n',
        encoding='utf-8')


if __name__ == '__main__':
    main()
