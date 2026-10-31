"""Allocate only the measured external CF/BT authentication guard in ROM."""
from pathlib import Path
import hashlib
import json

R = Path(__file__).resolve().parents[2]
J = R / 'build/peach-palette-fix-1030-v1/joint'
P = R / 'build/contra-force-rom-guard-proposal-v1/proposal.json'
Q = R / 'docs/qa/checkpoints/2026-10-30/arthur-quick-private-allocation/root-review-and-reservations.json'
D = R / 'docs/qa/checkpoints/2026-10-31/contra-force-rom-guard-resources'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def inspect(joint):
    raw = (joint/'candidate.nes').read_bytes()
    lo, hi = (16 + 69*8192 + q for q in (0x1f47, 0x1fbd))
    assert raw[lo:hi] == b'\xff'*118
    segs, syms = {}, []
    for line in (joint/'candidate.dbg').read_text().splitlines():
        if line.startswith(('seg\t', 'sym\t')):
            q = dict(x.split('=', 1) for x in line[4:].split(',') if '=' in x)
            if line.startswith('seg\t'):
                segs[q['id']] = q
            elif 'val' in q:
                syms.append(q)
    assert not [s for s in segs.values() if 'ooffs' in s and
        int(s['ooffs'], 0) < hi and int(s['ooffs'], 0)+int(s['size'], 0) > lo]
    temporal_aliases = []
    for s in syms:
        value = int(s['val'], 0)
        if 'seg' in s and 'ooffs' in segs[s['seg']]:
            g = segs[s['seg']]
            pos = int(g['ooffs'], 0)+value-int(g['start'], 0)
            assert not lo <= pos < hi, s
        elif 'seg' not in s:
            if any(b+0x1f47 <= value < b+0x1fbd for b in (0xa000, 0xc000)):
                # This rawRAM3 data lease is never ROM69. Its actual declarations
                # are bound below; do not permit an unclassified absolute alias.
                assert s['name'] == '"BwPersistent"' and value == 0xbf80, s
                temporal_aliases.append(dict(name='BwPersistent', value=value,
                    owner='Bowser rawRAM3 data, not ROM69'))
    byname = {s['name'].strip('"'): s for s in segs.values()}
    z = byname['Z2_LOGIC']
    assert (int(z['start'], 0), int(z['size'], 0)) == (0xa000, 0x1f47)
    return dict(ROM_sha256=sha(joint/'candidate.nes'), emitted_conflicts=0,
        symbol_conflicts=0, classified_temporal_aliases=temporal_aliases,
        preimage_sha256=hashlib.sha256(raw[lo:hi]).hexdigest())


def main():
    assert not D.exists()
    assert sha(P) == '4ecb248d79775d93fdc77075b68e85df95c1caec630823559d0e456a97884f0b'
    proposal = json.loads(P.read_text())
    for p, digest in proposal['bindings'].items():
        assert sha(p) == digest, p
    assert proposal['actual_bytes'] == 118 and not proposal['ROM_granted']
    quick = json.loads(Q.read_text())['Quick_Man']['PRG']
    assert dict(bank=69, start=0x1f47, end=0x2000) in quick
    reviewed = [inspect(j) for j in (J, R/'build/bowser-current64-v3/joint')]
    files = [Path(__file__), P, Q, R/'tools/reference/contra_force_rom_guard_v1.s']
    for j in (J, R/'build/bowser-current64-v3/joint'):
        files += [j/'candidate.nes', j/'candidate.dbg', j/'private.cfg']
    for pattern in ('*.s', '*.inc'):
        files += list((R/'build/bowser-current64-v3/joint/bowser').glob(pattern))
    out = dict(status='PRIVATE_MEASURED_EXTERNAL_CF_BT_GUARD_SOURCE_GRANT',
        native=False, installed=False, shared_hook_granted=False,
        ROM=dict(physical_bank=69, first_offset=0x1f47, end_offset_exclusive=0x1fbd,
            bytes=118, execution_view='A', CPU_start=0xbf47,
            authority='118B subset of prior Quick lease after actual Z2_LOGIC'),
        reviewed=reviewed,
        constraints=[
            'Source-built successors only; split actual MEMORY/SEGMENTS; preserve all existing public PCs and neighboring bytes.',
            'Only the measured ROM guard and full expected cookie. Remaining67 bytes of the older lease are not granted here.',
            'Authenticate full cookie/class in ROM before any rawA2 opcode; restore rawC and AXYP except resultC.',
            'BT branch uses the actual imported BtCheck address and bank. Preserve its real ingress ABI.',
            'Root/Bowser owner retains shared resolver edits; this grant alone adds no common hook.',
            'No new global/ZP/RAM/CHR grant; run emitted guard, wrong-cookie, all-flags, mapper/ISR and first-opcode failure controls.',
            'This is source allocation, not functional admission, native verification or permission to install an untested ROM.'
        ], bindings={str(p):sha(p) for p in files})
    D.mkdir(parents=True)
    path = D/'root-review-and-reservations.json'
    path.write_text(json.dumps(out, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps(dict(grant=str(path), sha256=sha(path), bytes=118)))


if __name__ == '__main__':
    main()
