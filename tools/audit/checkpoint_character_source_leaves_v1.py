"""Root-verify and preserve Arthur, Quick Man and the first four-host union."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT/'docs/qa/checkpoints/2026-10-30'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def archive(name, relative, expected, scope, upstream_archive=None):
    handoff = ROOT/relative
    assert sha(handoff) == expected
    record = json.loads(handoff.read_text())
    # Quick Man declares its builders separately from generated outputs.
    # The first checkpoint preserves those in an explicit tools addendum.
    bindings = {**record['bindings'], **record.get('tools', {})}
    assert isinstance(bindings, dict)
    for path, digest in bindings.items():
        assert sha(path) == digest, path
    target = DEST/name
    assert not target.exists(), 'Preserve frozen checkpoint'
    target.mkdir(parents=True)
    archive_path = target/'frozen-source-packet.zip'
    if upstream_archive:
        source = Path(record['source_archive'])
        assert sha(source) == record['source_archive_sha256'] == upstream_archive
        shutil.copyfile(source, archive_path)
        assert sha(archive_path) == upstream_archive
        shutil.copyfile(handoff, target/'handoff-baseline.json')
    else:
        files = {**bindings, str(handoff):expected, str(Path(__file__)):sha(__file__)}
        with zipfile.ZipFile(archive_path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            for path_string, digest in files.items():
                path = Path(path_string).resolve()
                if not path.is_relative_to(ROOT) or path.suffix in {'.nes', '.dbg', '.lbl', '.map', '.exe', '.dll'}:
                    continue
                assert sha(path) == digest
                item = zipfile.ZipInfo(path.relative_to(ROOT).as_posix(), (2026,10,30,0,0,0))
                item.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(item, path.read_bytes())
    with zipfile.ZipFile(archive_path) as z:
        members = {name:hashlib.sha256(z.read(name)).hexdigest() for name in z.namelist()}
        assert len(members) == len(z.namelist())
        if upstream_archive:
            for member, digest in members.items():
                original = ROOT/member
                if str(original) in bindings:
                    assert bindings[str(original)] == digest, member
    proof = dict(status='Root-verified frozen component; not shared gameplay admission', scope=scope,
                 handoff=str(handoff), handoff_sha256=expected, verified_bindings=len(bindings),
                 archive_sha256=sha(archive_path), archive_bytes=archive_path.stat().st_size,
                 archive_members=members, runtime_references=bindings)
    (target/'root-review.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(dict(checkpoint=str(target.relative_to(ROOT)), bindings=len(bindings),
                         archive_bytes=proof['archive_bytes'], members=len(members))))


def main():
    archive('arthur-source-leaf', 'build/arthur-source-v1/handoff.json',
            '5560c1f290209d63ed36475b1557c8bdc79d21ee8de0423acbe1fcbb8e4ba3ac',
            dict(verified='1920 native instruction cases, requested second jump, five source weapon handlers, authentic84 poses and420 lossless8x16 checks; root viewed source art and all six arena images.',
                 native='Private1000-frame NROM controller arena only; pickups are controller-selected test fixtures.',
                 open='Actual SMB terrain, progression, lifecycle, audio and host leases; Arthur stays pending.'))
    archive('quick-man-source-leaf', 'build/quickman-source-v1/handoff.json',
            'e5715042b777d6d6f4f0756218294789d3fd40b9ad95abc8b17ad920675f1ca1',
            dict(verified='44 source CPU cases, two full fan trajectories, eight exact instruction roundtrips and30 native pose geometries; root viewed pose sheet.',
                 native=False, palette='Decoded palette roles/display RGB do not prove live Quick Man palette installation.',
                 open='Complete motion/contact/progression, host8x16 packing and leases; Quick Man stays pending.'))
    archive('four-host-union-baseline', 'build/character-host-union-v2/handoff-baseline.json',
            sha(ROOT/'build/character-host-union-v2/handoff-baseline.json'),
            dict(verified='Four source-backed components linked; source CPU, family NMI, foreign application and ordered-write comparisons; all bindings independently rehashed.',
                 native=False, frontier='31-slot77-profile frontend ancestor979cff78; latest shared32-slot80-profile frontend untouched and must be composed before admission.',
                 performance='Measured1451..2458 extra legacy Main CPU cycles; optimization pending; no60Hz claim.',
                 open='Fast path, current frontend composition, real native gameplay and final admission.'),
            upstream_archive='157d198766a7f960d65669e93a635a5d98e1dc825052d1f4dd21fdb9288cd028')


if __name__ == '__main__':
    main()
