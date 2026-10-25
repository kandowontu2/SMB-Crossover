"""Snapshot current-hash discoveries and strict independent replay coverage."""
from pathlib import Path
import argparse
import hashlib
import json

ARCHIVE = Path('C:/Users/kando/Videos/SMB Crossover Archive')


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    digest = sha(a.rom)
    pairs, sources = {}, []

    def snapshot(path):
        target = a.output / ('source-' + str(len(sources)) + '.json')
        target.write_bytes(path.read_bytes())
        sources.append(dict(path=str(path), frozen=str(target), sha256=sha(target)))
        return json.loads(target.read_text())

    def discovery(folder):
        manifest = folder / 'manifest.json'
        m = json.loads(manifest.read_text())
        assert m['ROM_sha256'] == digest and not m['fixed_replay']
        key = m['config']['name'] + '-' + m['config']['behavior']
        pair = pairs.setdefault(key, dict(discoveries={}, strict_replays={}))
        result = m.get('result') or {}
        pair['discoveries'][str(manifest)] = dict(manifest_sha256=sha(manifest),
            passed=m['exit'] == 0 and result.get('cleared') is True and result.get('deaths') == 0 and m.get('chr_commit', {}).get('passed') is True,
            frames=result.get('frames'), failure=result.get('failure'), exit=m['exit'], result_available=bool(result))

    for relative in ('2026-10-24-roster-pe/matrix-v1/discover-results.json',
                     '2026-10-24-roster-pf/retry-v1/discover-results.json',
                     '2026-10-24-roster-pf/followup-selected-discoveries-v1.json',
                     '2026-10-24-roster-pg/discover-v1/discover-results.json',
                     '2026-10-24-roster-pg/discover-v2/discover-results.json',
                     '2026-10-24-roster-ph/grant-discover-v1/discover-results.json'):
        path = ARCHIVE / relative
        if path.exists():
            index = snapshot(path)
            assert index['ROM_sha256'] == digest
            for run in index['runs']:
                discovery(Path(run['folder']))

    def strict(proof):
        q = json.loads(proof.read_text())
        assert q['passed'] and q['ROM_sha256'] == digest
        key = q['identity'] + '-' + q['mode']
        assert key in pairs and any(d['passed'] for d in pairs[key]['discoveries'].values())
        pairs[key]['strict_replays'][str(proof)] = dict(sha256=sha(proof), result=q['strict_route'])

    pc = ARCHIVE / '2026-10-24-smb3-shrink-pc/probe-v1'
    for name in ('mario3', 'luigi3'):
        for mode in ('easy', 'hard'):
            discovery(pc / 'routes-v1' / ('discover-' + name + '-' + mode + '-v1'))
            strict(pc / ('review-' + name + '-' + mode + '-v1') / 'proof.json')
    for relative in ('2026-10-24-roster-pf/direct-batch-v1/progress.json',
                     '2026-10-24-roster-pf/followup-direct-v1/proof.json',
                     '2026-10-24-roster-pg/zelda-direct-v1/proof.json'):
        index = snapshot(ARCHIVE / relative)
        assert index['ROM_sha256'] == digest
        for run in index['runs']:
            if run['passed']:
                proof = Path(run.get('guarded_review', run['review'])) / 'proof.json'
                assert sha(proof) == run['strict_proof_sha256']
                strict(proof)
    assert len(pairs) == 74
    discovered = [key for key, q in pairs.items() if any(d['passed'] for d in q['discoveries'].values())]
    verified = [key for key, q in pairs.items() if q['strict_replays']]
    report = dict(goal_complete=False, every_item_complete=False, final_mapper_release_complete=False,
        ROM_sha256=digest, required_identity_mode_pairs=74,
        clean_discovery_pairs=len(discovered), strict_independent_direct_pairs=len(verified),
        remaining_discovery_pairs=sorted(set(pairs) - set(discovered)),
        remaining_strict_pairs=sorted(set(pairs) - set(verified)),
        sources=sources, pairs=pairs, driver_sha256=sha(Path(__file__)),
        scope='Snapshot of exact current-hash discovery attempts and validated individual strict direct-replay proofs. Prior failures stay included, null-result harness errors are retained, and mixed aggregates are not relabeled as passes. Complete physical frame retention and automated checks are scoped by each original proof. No exhaustive human visual, every-item, audio/source fidelity, zero-lag or final mapper claim.')
    (a.output / 'proof.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('ROM_sha256', 'clean_discovery_pairs', 'strict_independent_direct_pairs', 'remaining_discovery_pairs')}, indent=2))


if __name__ == '__main__':
    main()
