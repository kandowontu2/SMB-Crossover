"""Prepare a recoverable GQ backup; never install an unfinished candidate."""
from pathlib import Path
import datetime
import hashlib
import json
import zipfile

R = Path(__file__).resolve().parents[2]
D = R / 'build/verification/root49-combined-adoption-a'
P = R / 'build/verification/agent-lsr-sophia-feet-implementation-a'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not D.exists(), 'Retain the previous preparation; choose a new output.'
    parent = R / 'build/checkpoints/roster-audit-v49-link-ceiling-gq/manifest.json'
    assert sha(parent) == 'b8d20e8cab676894da899801146554f310dc4c339453c7b0897cfe92833c623f'
    old = json.loads(parent.read_text())
    files = dict(old['source_hashes'])
    assert len(files) == 442
    for build in old['builds']:
        for item in build['artifacts'].values():
            files[item['path']] = item['sha256']
    assert len(files) == 450
    generated_parent = R / 'build/verification/agent49-e-sophia-union-a/freeze-final-e.json'
    assert sha(generated_parent) == 'eb873f8e18c7863a67ad342744a871c28b56d259668c3b1cf2eb0851015b9a1f'
    generated = json.loads(generated_parent.read_text())['generated11']
    for name, digest in files.items():
        assert sha(R / name) == digest, ('Main no longer equals the expected predecessor', name)
    generated_differences = {}
    for name, digest in generated.items():
        current = R / 'build/generated' / name
        frozen = P / 'source-c/build/generated' / name
        assert sha(frozen) == digest, name
        assert current.read_bytes().replace(b'\r\n', b'\n') == frozen.read_bytes().replace(b'\r\n', b'\n'), name
        files['build/generated/' + name] = sha(current)
        if sha(current) != digest:
            generated_differences[name] = dict(before=sha(current), candidate=digest, difference='CRLF/LF only; every normalized byte exact')

    revision = P / 'revision-c.json'
    candidate = json.loads(revision.read_text())['source_sha256']
    assert len(candidate) == 455 and not set(old['source_hashes']) - set(candidate)
    changes = {}
    for name, digest in candidate.items():
        assert sha(P / 'source-c' / name) == digest, name
        before = old['source_hashes'].get(name)
        if before != digest:
            assert before is not None or not (R / name).exists(), ('Local new-path conflict', name)
            changes[name] = dict(before=before, candidate=digest)
    for name, digest in generated.items():
        assert sha(P / 'source-c/build/generated' / name) == digest, name

    D.mkdir(parents=True)
    archive = D / 'before-main-gq.zip'
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for name in files:
            z.write(R / name, name)
        z.write(parent, 'checkpoint/manifest.json')
    with zipfile.ZipFile(archive) as z:
        for name, digest in files.items():
            assert hashlib.sha256(z.read(name)).hexdigest() == digest, name
        assert hashlib.sha256(z.read('checkpoint/manifest.json')).hexdigest() == sha(parent)
    report = dict(
        status='PASS_PREPARATION_ONLY_MAIN_GQ_UNCHANGED',
        utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        script_sha256=sha(__file__),
        parent=dict(path=parent.relative_to(R).as_posix(), sha256=sha(parent)),
        before_files=files,
        archive=dict(path=archive.relative_to(R).as_posix(), sha256=sha(archive), bytes=archive.stat().st_size),
        candidate_revision=dict(path=revision.relative_to(R).as_posix(), sha256=sha(revision)),
        candidate_sources=455,
        candidate_changes=changes,
        generated11_normalized_literal=True,
        generated_line_endings=generated_differences,
        prerequisites=[
            'Final scoped feet/cache/foreign/ISR/performance review and immutable freeze.',
            'Independent landing audio and original24 effects review; resolve any confirmed audible regression.',
            'Root review of those final records, then explicit installation and byte checks.',
        ],
        route_guard='Samus specialist confirms all GQ source/artifact guards and native ROM paths already resolve inside immutable agent-lsr-link-ceiling-c/source. Preserve that tree and GQ manifest.',
        main_changed=False, accepted_release=False, goal_complete=False,
    )
    for name, digest in files.items():
        assert sha(R / name) == digest, name
    (D / 'preparation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(status=report['status'], source_changes=len(changes), backed_up_files=len(files), archive_bytes=archive.stat().st_size, report_sha256=sha(D / 'preparation.json'))))


if __name__ == '__main__':
    main()
