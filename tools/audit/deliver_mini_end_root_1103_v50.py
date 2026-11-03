"""Reuse the verified installer for the minimal Mini ending repair."""
import json
import sys
import deliver_mini_nightly_root_1103_v30 as D

D.O = D.R / 'build/mini-mario-end-delivery-root-1103-v50'
D.PREVIOUS = '8daf59cc958e2a3a645882ea53c6bd75e9a7c641793054f8ce534358f369a7d7'

if __name__ == '__main__':
    D.main()
    if sys.argv[1] == 'finalize':
        pin = json.loads((D.O / 'verified-delivery.json').read_text())['ROM_SHA256']
        (D.O / 'release-notes.txt').write_text(
            'Current MMC5 work-in-progress nightly.\n\n'
            'Apply this sole IPS to clean, headered Super Mario Bros. (World).\n'
            'Base SHA-256: 0b3d9e1f01ed1668205bab34d6c82b0e281456e137352e4f36a9b2cfa3b66dea\n'
            'Patched ROM SHA-256: ' + pin + '\n\n'
            'Mini Mario is unlocked: highlight Mario and press Select until MINI MARIO. '
            'A jumps; B runs. Hold against a wall and press A again for the adapted wall jump. '
            'Native ending collisions and lives-screen coordinates are repaired. '
            'A full non-shortcut 1-1 run reaches active 1-2 without life loss or helper platforms; '
            'the actual Downloads launch passes selection and movement checks. '
            'Powerups, original audio and other stages remain unfinished. '
            'Prince of Persia remains locked; Donkey Kong Jr. is not in the public menu.\n'
        )
