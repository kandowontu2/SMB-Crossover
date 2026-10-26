"""Checkpoint the unchanged menu failure and its diagnostic, without adoption."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
OUT = ROOT / 'docs/qa/checkpoints/2026-10-26/parodius-menu-native-held'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    assert not OUT.exists()
    OUT.mkdir(parents=True)
    catalog = {}

    def copy(source, name, expected=None):
        source = Path(source)
        actual = sha(source)
        if expected:
            assert actual == expected, source
        dest = OUT / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, dest)
        assert sha(dest) == actual
        catalog[dest.relative_to(OUT).as_posix()] = dict(source=str(source), sha256=actual)

    packets = {
        'parodius-hud-df515-lifecycle-ready-v2': 'd3fb136764d197281fb2d3638ef4a27ede5f6dd268ab91a93a006083ff5211b6',
        'parodius-hud-df515-menu-negative-v1': '3295e15654f6d07b8d414862cb2c3d553349dceaf05fc085fb95def64cd2a44a',
        'parodius-hud-df515-menu-diagnostic-ready-v1': 'ff3643f5522c228d9fd1effac7c95b12c24f3295ff206edfd002281ca9f03c00',
        'parodius-hud-df515-menu-diagnostic-outcome-v1': 'ed10c7e9aa75f66bfd551fd750ded06ae5d311038cc06b0b890b29376e8ae9d4',
    }
    verified = {}
    for name, expected in packets.items():
        p = D / name
        assert sha(p / 'proof.json') == expected
        proof = json.loads((p / 'proof.json').read_text())
        manifest = json.loads((p / 'manifest.json').read_text())
        assert sha(p / 'manifest.json') == proof['manifest_sha256']
        for file, digest in manifest.items():
            assert sha(file) == digest, file
        verified[name] = len(manifest)
        for f in p.iterdir():
            if f.is_file():
                assert f.suffix in ['.json', '.png']
                copy(f, 'packets/' + name + '/' + f.name)
    mp = D / 'parodius-hud-source-final-map-v1/proof.json'
    assert sha(mp) == '9512a468203de8bbf8daa77fd90b1bb6b94570ba03410dad0fc2fb901dc319c9'
    m = json.loads(mp.read_text())
    copy(mp, 'source-final-map.json')
    for name, record in m['changed_production_sources'].items():
        copy(Path(m['source_final']) / name, 'changed-source/' + name, record['candidate_sha256'])
        if record['installed_source_sha256']:
            assert sha(ROOT / name) == record['installed_source_sha256'], name
    for name, digest in m['tools'].items():
        copy(ROOT / name, 'frozen-tools/' + Path(name).name, digest)
    raw = D / 'parodius-hud-df515-menu-diagnostic-preparation-v1/menu/baseline-early'
    for name in ['first-init-start-mismatch.json', 'lifecycle-proof.json']:
        copy(raw / name, 'actual-diagnostic/' + name)
    for name in ['parodius-hud-lifecycle-readiness-2026-10-25.txt',
                 'parodius-hud-menu-native-hold-2026-10-25.txt',
                 'parodius-hud-menu-diagnostic-readiness-2026-10-25.txt',
                 'parodius-hud-menu-diagnostic-native-2026-10-25.txt']:
        copy(ROOT / 'docs/qa' / name, 'reports/' + name)
    result = dict(accepted=False, production_adopted=False,
                  root_verified_manifest_counts=verified,
                  actual_failure='Pre-render start:173 of256 DMA writes; pending transfer; all current/source/hardware bytes already equal.',
                  visible_pixel_corruption_proven=False,
                  actual_diagnostic_prefix_exact='128 actual ARGB frames plus every original parsed bus row.',
                  raw_settings_and_lossless_captures_retained_external=True,
                  copied_bindings=catalog)
    (OUT / 'root-review.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(checkpoint=str(OUT), verified=verified, copied=len(catalog), accepted=False)))


if __name__ == '__main__':
    main()
