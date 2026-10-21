"""Freeze the narrow wall-cancel/native-buffer candidate without acceptance."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[2]
OLD = ROOT / 'build/checkpoints/roster-audit-v43'
OUT = ROOT / 'build/checkpoints/roster-audit-v44-provisional-a'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
patches = {
    'build/verification/ryu-wall-cancel44-preparation/wall-cancel-only.patch':
        'a3ad0866aa93087c3a08ec24b867c982a332c3e7355c108da2a527b38ff498ae',
    'build/verification/mm-bass-native-bg-v43-readonly/native-buffer-address-mmc5-only.diff':
        '472bc644f83ce6b903d8dbf637c95fc0660644fe6793fe34ff270cff23b269f9',
}
assert all(sha(ROOT / n) == h for n, h in patches.items())
with zipfile.ZipFile(OLD / 'source-v43.zip') as z:
    previous = json.loads(z.read('archived-file-hashes.json'))
    changed = {n for n, h in previous.items() if sha(ROOT / n) != h}
    assert changed == {'README.md', 'src/collision.s', 'src/remaining_weapons.s'}, changed
    before = z.read('src/remaining_weapons.s').decode().replace('\r\n', '\n')
    marker = '    sta AvFlip\n  :\n  inc AvFlipClock'
    replacement = ('    sta AvFlip\n'
        '    ; attachToWall cancels active Jump Slash; an airborne attack does not.\n'
        '    ldx XgWall\n    beq :+\n    sta AvSlash\n  :\n  inc AvFlipClock')
    assert marker in before
    assert (ROOT / 'src/remaining_weapons.s').read_text(encoding='utf8') == before.replace(marker, replacement, 1)
if OUT.exists():
    assert not (OUT / 'candidate.json').exists(), 'Never overwrite a frozen candidate/checkpoint'
    assert all(p.is_file() and p.suffix in ('.nes', '.dbg', '.lbl', '.map', '.lst')
        and p.name.startswith('smb-crossover-') and sha(p) == sha(ROOT / 'build' / p.name)
        for p in OUT.iterdir()), 'Resume only an identical incomplete preparation copy'
OUT.mkdir(exist_ok=True)
roms = {}
for mapper in ('mmc3', 'mmc5'):
    for ext in ('.nes', '.dbg', '.lbl', '.map', '.lst'):
        p = ROOT / f'build/smb-crossover-{mapper}{ext}'
        shutil.copyfile(p, OUT / p.name)
        assert sha(p) == sha(OUT / p.name)
    rom = OUT / f'smb-crossover-{mapper}.nes'
    a, b = (OLD / rom.name).read_bytes(), rom.read_bytes()
    assert a[:16] == b[:16] and a[16 + 524288:] == b[16 + 524288:]
    changed_banks = [i for i in range(64)
        if a[16 + i * 8192:16 + (i + 1) * 8192] != b[16 + i * 8192:16 + (i + 1) * 8192]]
    # The MMC5 insertion also relinks absolute references to later resident
    # collision routines. This is a placement inventory, not byte/cycle parity.
    assert changed_banks == ([6, 61] if mapper == 'mmc3'
        else [0, 1, 2, 6, 8, 10, 59, 61, 62, 63]), changed_banks
    # Twelve farcall immediate addresses follow bank6 routines moved by eight.
    def bank6_symbols(path):
        segs, scopes, syms = {}, {}, []
        for line in path.read_text().splitlines():
            f = dict(re.findall(r'(\w+)=("[^"]*"|[^,\t]+)', line))
            if line.startswith('seg\t'):
                segs[f['id']] = f
            elif line.startswith('scope\t'):
                scopes[f['id']] = f.get('name')
            elif line.startswith('sym\t') and f.get('type') == 'lab' and 'seg' in f:
                syms.append(f)
        return {(scopes.get(s.get('scope')), s['name']): int(s['val'], 0)
            for s in syms if 'ooffs' in segs[s['seg']]
            and (int(segs[s['seg']]['ooffs']) - 16) // 8192 == 6}
    old_symbols = bank6_symbols((OLD / rom.name).with_suffix('.dbg'))
    new_symbols = bank6_symbols(rom.with_suffix('.dbg'))
    labels = {n: int(v, 16) for v, n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$', rom.with_suffix('.lbl').read_text(), re.M)}
    target_low = (labels['FarcallJmpTarget_SMC'] + 1).to_bytes(2, 'little')
    target_high = (labels['FarcallJmpTarget_SMC'] + 2).to_bytes(2, 'little')
    relocations = [i for i in range(16 + 61 * 8192, 16 + 62 * 8192) if a[i] != b[i]]
    assert len(relocations) == 12
    for i in relocations:
        assert a[i - 1:i] == b[i - 1:i] == b'\xa9'
        assert a[i + 1:i + 4] == b[i + 1:i + 4] == b'\x8d' + target_low
        assert a[i + 3:i + 14] == b[i + 3:i + 14]
        assert a[i + 4] == 0xa9 and a[i + 6:i + 9] == b'\x8d' + target_high
        assert a[i + 9:i + 12] == bytes([0xa9, 6 if mapper == 'mmc3' else 0x86, 0x20])
        old_address, new_address = a[i] + 256 * a[i + 5], b[i] + 256 * b[i + 5]
        assert new_address == old_address + 8
        assert any(old_address == v and new_symbols.get(k) == new_address for k, v in old_symbols.items())
    roms[mapper] = dict(sha256=sha(rom), dbg_sha256=sha(rom.with_suffix('.dbg')),
        lbl_sha256=sha(rom.with_suffix('.lbl')), changed_prg_banks=changed_banks)
report = dict(status='provisional-not-accepted', goal_complete=False,
    created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    checkpoint=OUT.name, parent=OLD.name, patches=patches, roms=roms,
    scope='Ryu active Jump Slash wall cancellation + MMC5 native buffer prefix only; unchanged CHR/header/RAM ABI requires further tests',
    changed_archived_inputs=sorted(changed), tests_complete=False)
(OUT / 'candidate.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2), flush=True)
