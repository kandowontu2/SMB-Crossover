"""Bind actual Downloads verification and rebuild its sole public IPS."""
from pathlib import Path
import hashlib
import json
from prepare_selected_native_packet_v1 import R, sha
from nightly_patch_guard_v1 import check

O = R / 'build/bub-delivery-1102-v9'
D = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
PIN = '613b3300b09e530ec920835b95df53f3115d865ed854e273809d4cafa52407ce'


def main():
    p = O / 'downloads-bub-controls'
    binding = json.loads((p / 'capture/binding.json').read_text())
    ready = json.loads((p / 'ready.json').read_text())
    assert binding['exit_code'] == 0 and binding['ROM_sha256'] == PIN
    assert binding['ready_sha256'] == sha(p / 'ready.json')
    assert Path(ready['ROM']) == D and json.loads((p / 'capture/result.json').read_text())['passed']
    for source, h in ready['bindings'].items():
        assert sha(source) == h, source
    guard = check(D)
    assert sha(D) == PIN
    base = Path('C:/NES/Super Mario Bros. (World).nes')
    a, b = base.read_bytes(), D.read_bytes()
    assert sha(base) == '0b3d9e1f01ed1668205bab34d6c82b0e281456e137352e4f36a9b2cfa3b66dea'
    patch, i = bytearray(b'PATCH'), 0
    while i < len(b):
        if i < len(a) and a[i] == b[i]:
            i += 1
            continue
        start = i if i != 0x454f46 else i - 1
        i = max(i, start + 1)
        while i < len(b) and i - start < 65535 and (i >= len(a) or a[i] != b[i]):
            i += 1
        patch += start.to_bytes(3, 'big') + (i - start).to_bytes(2, 'big') + b[start:i]
    patch += b'EOF' + len(b).to_bytes(3, 'big')
    restored, pos = bytearray(a), 5
    while patch[pos:pos + 3] != b'EOF':
        offset, size = int.from_bytes(patch[pos:pos + 3], 'big'), int.from_bytes(patch[pos + 3:pos + 5], 'big')
        pos += 5
        assert size > 0
        restored.extend(bytes(max(0, offset + size - len(restored))))
        restored[offset:offset + size] = patch[pos:pos + size]
        pos += size
    restored = restored[:int.from_bytes(patch[pos + 3:pos + 6], 'big')]
    assert restored == b
    ips = O / 'SMB-Crossover-Latest-WIP-MMC5.ips'
    ips.write_bytes(patch)
    q = json.loads((O / 'delivery.json').read_text())
    q.update(downloads_launch_verified=True, downloads_verification_scope='Actual Downloads Bub cold selection, idle/walk/jump/bubble controls pass. Bob candidate ride passed; extra Downloads Bob replay hit host runtime bound during connection interruption, not qualified.',
             latest_patch_guard=guard, IPS_SHA256=hashlib.sha256(patch).hexdigest(), IPS_bytes=len(patch), IPS_roundtrip=True, base_SHA256=sha(base))
    (O / 'published-receipt.json').write_text(json.dumps(q, indent=2) + '\n')
    (O / 'release-notes.txt').write_text('Current MMC5 work-in-progress nightly.\n\nApply the IPS to clean headered Super Mario Bros. (World).\nBase SHA-256: '+sha(base)+'\nPatched ROM SHA-256: '+PIN+'\n\nNovember 2: playable Bub and Bob, with original bubble trapping/popping and bubble rides. Both pass cold selection, controls and earned rides; Bub passes Easy stomp and ceiling regression. Actual Downloads launch/control test passes. Full 1-1 and all powerup testing remain incomplete; idle/walk currently runs about half rate. Prior WWF/Karnov and other playable updates retained.\n')
    print(json.dumps(dict(ROM_SHA256=PIN, IPS_SHA256=q['IPS_SHA256'], IPS_roundtrip=True, actual_Downloads=True)))


if __name__ == '__main__':
    main()
