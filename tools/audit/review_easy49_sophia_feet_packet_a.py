"""Bind the scoped C collision proof, retaining its audio and performance negatives."""
from pathlib import Path
import hashlib
import json

R = Path(__file__).resolve().parents[2]
D = R / 'build/verification/agent-lsr-sophia-feet-implementation-a'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out = R / 'build/verification/root49-sophia-feet-packet-review-a.json'
    assert not out.exists()
    freeze, review = D / 'implementation-freeze.json', D / 'final-review.json'
    assert sha(freeze) == '405fe73544ffd90e7f2c1b4bfdfd5cbd98283015bab87b94772857b3e370d89e'
    assert sha(review) == 'f97c7d20d1d81306ccfed64128c872f29444d9d373998ea534be643c6f3a2384'
    f, d = [json.loads(p.read_text()) for p in (freeze, review)]
    for name, item in f['files'].items():
        path = D / name
        assert path.stat().st_size == item['bytes'] and sha(path) == item['sha256'], name
    assert len(f['files']) == 2791 and len(f['source_sha256']) == d['source_count'] == 455
    for name, digest in f['source_sha256'].items():
        assert sha(D / 'source-c' / name) == digest, name
    for name, digest in d['reviews'].items():
        assert sha(D / name) == digest, name
    assert not d['accepted_runtime'] and d['no_remaining_owned_jobs']
    assert d['strict_actual']['calls'] == 526
    report = dict(status='PASS_SCOPED_C_PACKET_REHASH_NOT_RUNTIME_ADMISSION', script_sha256=sha(__file__),
        freeze_sha256=sha(freeze), review_sha256=sha(review), rehashed_packet_files=2791,
        source_files=455, strict_actual=d['strict_actual'], native_actual=d['native_actual'],
        profiles=d['profiles'], known_negative=d['known_negative'], qualifications=d['qualifications'],
        successor='Root source-e has a separate append-only landing correction under native review. LSR is optimizing the material flat collision cost in a new phase; neither successor is installed.',
        root_did_not_rerun_specialist_component_matrix=True, main_changed=False,
        accepted_release=False, goal_complete=False)
    out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(status=report['status'], sha256=sha(out), files=2791)))


if __name__ == '__main__':
    main()
