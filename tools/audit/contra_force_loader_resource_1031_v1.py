"""Review exact existing PRG intervals for the measured CF bootstrap."""
from pathlib import Path
import hashlib
import json

R = Path(__file__).resolve().parents[2]
J = R / 'build/peach-palette-fix-1030-v1/joint'
P = R / 'build/contra-force-loader-proposal-v1/proposal.json'
Q = R / 'docs/qa/checkpoints/2026-10-30/arthur-quick-private-allocation/root-review-and-reservations.json'
D = R / 'docs/qa/checkpoints/2026-10-31/contra-force-loader-resources'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not D.exists()
    proposal = json.loads(P.read_text())
    assert sha(P) == 'd54274a31e4f25df1c8d8c412804a0569c1ccd998211d6af9f833725d89c39a9'
    for path, digest in proposal['bindings'].items():
        assert sha(path) == digest, path
    raw = (J / 'candidate.nes').read_bytes()
    assert sha(J / 'candidate.nes') == 'f56e55cd69b93821e66548848305cf9822e2ac0e8a25752d7192332cded53b78'
    segs, syms = {}, []
    for line in (J / 'candidate.dbg').read_text().splitlines():
        if not line.startswith(('seg\t', 'sym\t')):
            continue
        q = dict(x.split('=', 1) for x in line[4:].split(',') if '=' in x)
        if line.startswith('seg\t'):
            segs[q['id']] = q
        elif 'val' in q:
            syms.append(q)
    cfg = (J / 'private.cfg').read_text()
    assert 'BASS_CEILING: load=X5_NEW_4E,type=ro,start=$ac00;' in cfg
    assert 'ROLL_WORLD:load=X5_NEW_4E,type=ro,start=$b000;' in cfg
    byname = {s['name'].strip('"'): s for s in segs.values()}
    bass, roll = byname['BASS_CEILING'], byname['ROLL_WORLD']
    assert (int(bass['start'], 0), int(bass['size'], 0)) == (0xac00, 0x268)
    assert int(roll['start'], 0) == 0xb000
    quick = json.loads(Q.read_text())['Quick_Man']['PRG']
    assert any(q == dict(bank=115, start=0x1f38, end=0x2000) for q in quick)
    rows = []
    for bank, start, end, view, origin in [
        (115, 0x1f38, 0x1fcb, 'A', '147B subset of the prior Quick lease after MIKE_NATIVE_AUDIO.'),
        (78, 0x0e68, 0x0f96, 'C', '302B of the source-bounded gap after BASS_CEILING and before fixed ROLL_WORLD.')]:
        lo, hi = 16 + bank * 8192 + start, 16 + bank * 8192 + end
        assert raw[lo:hi] == bytes([255]) * (hi - lo)
        live = [s for s in segs.values() if 'ooffs' in s and
            int(s['ooffs'], 0) < hi and int(s['ooffs'], 0) + int(s['size'], 0) > lo]
        assert not live
        aliases, labels = [], []
        for s in syms:
            value = int(s['val'], 0)
            if 'seg' not in s:
                if any(base + start <= value < base + end for base in [0xa000, 0xc000]):
                    aliases.append(s)
            elif 'ooffs' in segs[s['seg']]:
                g = segs[s['seg']]
                pos = int(g['ooffs'], 0) + value - int(g['start'], 0)
                if lo <= pos < hi:
                    labels.append(s)
        assert not aliases
        assert not labels or (bank == 115 and all(s['name'] == '"StNativeEnd"' for s in labels))
        rows.append(dict(physical_bank=bank, first_offset=start, end_offset_exclusive=end,
            bytes=end-start, execution_view=view, CPU_start=(0xa000 if view=='A' else 0xc000)+start,
            authority=origin, preimage_sha256=hashlib.sha256(raw[lo:hi]).hexdigest(),
            emitted_segments=live, absolute_aliases=aliases, endpoint_labels=labels))
    assert [q['bytes'] for q in rows] == list(proposal['actual_emitted_bytes'].values())
    files = [Path(__file__), P, Q, J/'candidate.nes', J/'candidate.dbg', J/'private.cfg',
        J/'src/expanded.s', J/'src/roll_dispatch.s',
        R/'tools/reference/contra_force_loader_proposal_v1.s']
    grant = dict(status='PRIVATE_EXACT_CF_BOOTSTRAP_SOURCE_GRANT_NOT_ADMITTED',
        parent_sha256=sha(J/'candidate.nes'), proposal_sha256=sha(P), ROM=rows,
        total_ROM_bytes=449, native=False, installed=False, ready=False,
        constraints=[
            'Only a source-built successor of current f56; no binary overlay of independent candidates.',
            'A115BF38..<BFCB outer preserves origin A; C78CE68..<CF96 copier remains mapped while raw A1/A2/A3 change.',
            'Split actual MEMORY/SEGMENTS at these physical offsets; preserve every prior public PC and adjacent byte.',
            'Retire prior owners and invalidate shared C2/RAM3 cookies before overwrite; full readback and complete fingerprint; validity last.',
            'Use the existing native forced-blank/published-CHR checkpoint and actual busy guard; reject active gameplay.',
            'No new RAM/ZP/common hook/CHR lease. The prior CF raw31 and935..<969 grants remain unchanged.',
            'Prove raw mapper/software shadows, all-register/flags outputs, latch/scroll, real ISR and readback failures before adoption.',
            'Actual menu/InitScreen, native traversal/rendering/combat and palette fairness are still required.'
        ],
        resource_basis='Actual linked source segments and all symbols plus the prior Quick lease establish exact ownership. FF preimages are corroboration, not the authority.',
        bindings={str(p):sha(p) for p in files})
    D.mkdir(parents=True)
    out = D / 'root-review-and-reservations.json'
    out.write_text(json.dumps(grant, indent=2)+'\n', encoding='utf-8', newline='\n')
    (D/'README.md').write_text(
        'Private source integration grant for the measured Contra Force bootstrap:147 bytes at physical115 '
        'offset1F38..<1FCB through A, and302 bytes at physical78 offset0E68..<0F96 through C. The first '
        'is a subset of an existing un-emitted Quick lease; the second is a new precise partition of '
        'the source-bounded gap between BASS_CEILING and the fixed ROLL_WORLD start. All actual symbols '
        'and emitted segments were checked; only the inert StNativeEnd endpoint shares the first start. '
        'The original sources and public entries must remain unchanged.\n\n'
        'This permits a private source build and executable verification. It does not unlock characters, '
        'install a ROM, allocate new global state or certify the measured placeholder cookie. Full loader, '
        'interrupt, owner-retirement and native gameplay checks remain required.\n',
        encoding='utf-8', newline='\n')
    print(json.dumps(dict(grant=str(out), sha256=sha(out), bytes=449, ready=False)))


if __name__ == '__main__':
    main()
