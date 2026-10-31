"""Read-only concrete Bowser resource request against the installed dfdb source.

This verifies existing ownership and linked/source exclusions. It does not
allocate ranges or claim that the still-unwritten complete host fits them.
"""
from pathlib import Path
import hashlib
import json
import re

R = Path(__file__).resolve().parents[2]
P = R / 'build/coherent62-lives-fixes-v1'
J = P / 'joint'
O = R / 'build/bowser-resource-closure-v1'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
QUICK = R / 'docs/qa/checkpoints/2026-10-30/arthur-quick-private-allocation/root-review-and-reservations.json'
ROGUE = R / 'docs/qa/checkpoints/2026-10-30/rogue-quick-audio-private-allocation/root-review-and-reservations.json'
BT = R / 'build/battletoads-current-host-v1/root-grant-and-partition.json'
WANTED = [(68, 0x1f20, 0x2000), (36, 0x1523, 0x1600),
          (84, 0x1529, 0x1600), (67, 0x122b, 0x1300),
          (83, 0x1534, 0x1600), (88, 0x1334, 0x1400)]


def main():
    assert not O.exists()
    manifest = json.loads((P / 'handoff.json').read_text())
    assert sha(P / 'handoff.json') == 'fae1ec38db9525a645a8907fd92608978de15f0f7cf4b12088cee0e0f0393a1c'
    for path, digest in manifest['bindings'].items():
        assert sha(path) == digest, path
    raw = (J / 'candidate.nes').read_bytes()
    assert sha(J / 'candidate.nes') == 'dfdb194ac73438ae8deb05b5fc93f241b1109d45a84b3ad333d0e632008d7fc7'
    segments, symbols = {}, []
    for line in (J / 'candidate.dbg').read_text().splitlines():
        if not line.startswith(('seg\t', 'sym\t')):
            continue
        q = dict(x.split('=', 1) for x in line[4:].split(',') if '=' in x)
        if line.startswith('seg\t'):
            segments[q['id']] = q
        elif 'val' in q:
            symbols.append(q)
    original = json.loads(QUICK.read_text())['Quick_Man']['PRG']
    excluded = [(q['bank'], q['start'], q['end']) for q in json.loads(ROGUE.read_text())['blocks']]
    excluded += [(q['physical_bank'], q['first_offset'], q['end_offset_exclusive'])
                 for q in json.loads(BT.read_text())['ROM']]
    excluded += [(93, 0xfa7, 0xfe7), (82, 0x1d94, 0x1fc4)]
    rows = []
    for bank, start, end in WANTED:
        assert any(q['bank'] == bank and q['start'] <= start < end <= q['end'] for q in original)
        assert not any(b == bank and start < e and end > s for b, s, e in excluded)
        lo, hi = 16 + bank * 8192 + start, 16 + bank * 8192 + end
        assert set(raw[lo:hi]) == {255}
        live = []
        for q in segments.values():
            if 'ooffs' in q:
                a = int(q['ooffs'], 0)
                z = a + int(q['size'], 0)
                if a < hi and z > lo:
                    live.append(q)
        assert not live
        backed, a_aliases, c_aliases = [], [], []
        for q in symbols:
            value = int(q['val'], 0)
            if 'seg' in q and 'ooffs' in segments[q['seg']]:
                g = segments[q['seg']]
                position = int(g['ooffs'], 0) + value - int(g['start'], 0)
                if lo <= position < hi:
                    backed.append(q)
            elif 'seg' not in q:
                if 0xa000 + start <= value < 0xa000 + end:
                    a_aliases.append(q)
                if 0xc000 + start <= value < 0xc000 + end:
                    c_aliases.append(q)
        assert not backed and not a_aliases
        assert not c_aliases or (bank == 68 and all(q['name'].strip('"') in
            ['AR_CACHE_VALID', 'AR_CACHE_FAMILY', 'AR_CACHE_VERSION'] for q in c_aliases))
        rows.append(dict(physical_bank=bank, first_offset=start, end_offset_exclusive=end,
                         bytes=end-start, A_view=[0xa000+start, 0xa000+end],
                         preimage_sha256=hashlib.sha256(raw[lo:hi]).hexdigest(),
                         live_segments=live, all_segment_backed_symbols=backed,
                         A_view_bankless_aliases=a_aliases,
                         C_view_aliases=c_aliases,
                         restriction='Execute resident code through A only; preserve raw C RAM3.' ))
    # Original legacy CHR lookup is byte-valued, so cannot select these high pages.
    cp = next(q for q in symbols if q['name'] == '"ChrPhysicalMap"' and 'seg' in q)
    g = segments[cp['seg']]
    off = int(g['ooffs'], 0) + int(cp['val'], 0) - int(g['start'], 0)
    legacy_map = list(raw[off:off+256])
    assert max(legacy_map) <= 246
    chr_base = 16 + 128 * 8192
    chr_rows = []
    for start, end in [(824, 827), (927, 935)]:
        lo, hi = chr_base+start*1024, chr_base+end*1024
        assert set(raw[lo:hi]) == {0}
        live = [q for q in segments.values() if 'ooffs' in q and
                int(q['ooffs'], 0) < hi and int(q['ooffs'], 0)+int(q['size'], 0) > lo]
        assert not live
        chr_rows.append(dict(first=start, end_exclusive=end, bytes=(end-start)*1024,
                             preimage_sha256=hashlib.sha256(raw[lo:hi]).hexdigest(),
                             emitted_segments=live))
    values = list(range(824, 827)) + list(range(927, 935))
    token = re.compile(r'(?<![\w$])(?:'+'|'.join(str(v) for v in values)+
        r'|\$0*(?:'+'|'.join(f'{v:x}' for v in values)+
        r')|0x0*(?:'+'|'.join(f'{v:x}' for v in values)+r'))(?![\w])', re.I)
    sources = [Path(p) for p in manifest['bindings'] if Path(p).suffix.lower() in ['.s', '.asm', '.inc']]
    hits = []
    for p in sources:
        for index, line in enumerate(p.read_text(errors='replace').splitlines(), 1):
            if token.search(line.split(';')[0]):
                hits.append(dict(path=str(p), line=index, text=line))
    assert not hits
    files = [P/'handoff.json', J/'candidate.nes', J/'candidate.dbg', J/'candidate.lbl',
             J/'private.cfg', QUICK, ROGUE, BT, Path(__file__).resolve(),
             R/'build/bowser-source-core-v5/handoff.json']
    result = dict(status='CONCRETE_EXISTING_OWNER_REQUEST_ONLY_NO_ALLOCATION',
        source=True, native=False, admitted=False, parent=sha(J/'candidate.nes'),
        parent_bindings_verified=len(manifest['bindings']), ROM=rows, ROM_total=sum(q['bytes'] for q in rows),
        CHR=chr_rows, legacy_ChrPhysicalMap_max=max(legacy_map),
        source_files_scanned=len(sources), direct_wide_page_literal_hits=hits,
        indirect_consumer_closure='Existing source-reviewed Quick leases, every actual DBG symbol/segment (including all refs), no A-view absolute alias, legacy CHR map <=246, no named CHR producer in requested ranges. Direct-wide-literal scan supplements this; it is not a claim to solve arbitrary computed pointers.',
        resource_limits='No whole loader fits the largest224B island. Complete loader/router/portrait fit still requires genuine routine-boundary assembly or a separately qualified BT descriptor-loader successor. No source cache or global RAM is allocated here.',
        suggested_allocation='Conditional1281B source-integration partition only after root review. Preserve adjacent native endpoints; execute new resident workers in A, not C.',
        RAM_request='Temporal raw RAM3 family27 only, state/code/cookie inside its own verified8KB image; invalidate previous owner before loading, full16byte family/version/fingerprint.',
        preserve=['Benj ROM62/B772..<BBA7 and901..<915', 'BT950B/915..<927',
                  'Rogue10pages', 'all Quick current A70/C82/C98 and unionbbox', 'all62 pending/ready states'],
        bindings={str(p.resolve()): sha(p) for p in files})
    O.mkdir()
    (O/'proposal.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(proposal=str(O/'proposal.json'), sha256=sha(O/'proposal.json'),
                          total_ROM=result['ROM_total'], requested_CHR=[824,827,927,935],
                          verified_parent_bindings=len(manifest['bindings']),
                          source_files=len(sources), allocation=False)))


if __name__ == '__main__':
    main()
