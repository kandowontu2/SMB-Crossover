"""Replace the user's single nightly ROM; deliberately make no backup."""
from pathlib import Path
import hashlib
import json
import os

R = Path(__file__).resolve().parents[2]
J = R / 'build/hogan-adapter'
O = R / 'build/nightly-hogan75'
DEST = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
EXPECTED = '4acfe759b13a9dd7749fb24522f94d2e47267c24a367c294fff361ea6c1f6f2d'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not O.exists()
    assert sha(J / 'candidate.nes') == EXPECTED
    native = R / 'build/hogan-native-route/capture/result.json'
    ready_path = R / 'build/hogan-native-route/ready.json'
    result = json.loads(native.read_text())
    ready = json.loads(ready_path.read_text())
    for path, digest in ready['bindings'].items():
        assert sha(path) == digest, path
    assert result['passed'] and result['ROM_sha256'] == EXPECTED
    assert result['Main'] == 663 if 'Main' in result else result['main_updates'] == 663
    assert result['counters']['defeat'] == 1 and result['maximum_camera'] >= 257
    before = sha(DEST) if DEST.exists() else None
    temporary = DEST.with_name(DEST.name + '.publishing')
    assert not temporary.exists()
    temporary.write_bytes((J / 'candidate.nes').read_bytes())
    assert sha(temporary) == EXPECTED
    os.replace(temporary, DEST)
    assert sha(DEST) == EXPECTED
    O.mkdir()
    receipt = dict(installed=True, backup_created=False, user_requested_no_backups=True,
                   destination=str(DEST), output_sha256=EXPECTED, replaced_sha256=before,
                   playable_identities=75, new_identity='Hulk Hogan',
                   native_evidence=str(native), native_evidence_sha256=sha(native),
                   limitations=['Hogan opening loop verified; full1-1, every upgrade and original audio remain incomplete',
                                'Thomas is not included; native rendering repair pending',
                                'Other roster and campaign work remains active'])
    (O / 'installed.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
