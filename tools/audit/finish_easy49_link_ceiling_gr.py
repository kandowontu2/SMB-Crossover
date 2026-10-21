"""Finish GQ checkpoint packaging after its archive used the wrong relative root."""
from pathlib import Path
import hashlib
import json
import shutil

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'agent-lsr-link-ceiling-c'
C = R / 'build/checkpoints/roster-audit-v49-link-ceiling-gq'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    p = C / 'manifest.json'
    m = json.loads(p.read_text())
    assert m['status'] == 'INSTALLING_WORKING_LINK_CEILING_GQ'
    d = json.loads((H / 'final-review.json').read_text())
    assert sha(H / 'final-review.json') == '3bd67ac13afc0c1f8e7fda7b0d9db447138c67f6831a5121924bb269f0b38e3b'
    assert len(m['builds']) == 2
    assert all(sha(R / n) == h for n, h in d['source_catalog'].items())
    for b in m['builds']:
        assert all(sha(R / a['path']) == a['sha256'] for a in b['artifacts'].values())
    assert sha(R / m['backup']['path']) == m['backup']['sha256']
    assert sha(R / m['admission']['path']) == m['admission']['sha256']
    source = H / d['source_archive']['path']
    assert sha(source) == d['source_archive']['sha256']
    target = C / 'source-v49-link-ceiling-gq.zip'
    assert not target.exists()
    before = sha(p)
    shutil.copyfile(source, target)
    assert sha(target) == d['source_archive']['sha256']
    m.update(status='PASS_WORKING_LINK_CEILING_GQ_BOTH_MAPPERS',
        source_hashes=d['source_catalog'],
        source_archive=dict(path=target.relative_to(R).as_posix(), sha256=sha(target), bytes=target.stat().st_size),
        packaging_completion=dict(script_sha256=sha(__file__), before_manifest_sha256=before,
            retained_publisher_sha256=sha(R / 'tools/audit/publish_easy49_link_ceiling_gq.py'),
            reason='The frozen source archive path is relative to the C packet, not the workspace. Both ROM/build copies and all source changes were already byte-exact. This completion only saves the checked archive/catalog and final checkpoint status.',
            source_or_ROM_changes=False))
    p.write_text(json.dumps(m, indent=2)+'\n')
    print(m['status'], sha(p))


if __name__ == '__main__':
    main()
