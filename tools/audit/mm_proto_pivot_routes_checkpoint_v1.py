"""Publish bounded route evidence; retain ROMs and lossless recordings externally."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
FINAL = D / 'mega-proto-pivot-routes0a-final-v1'
EXPECTED = '63ed5aeddd50ec8fc455f211e2f647c92d8e0effcf90911cce2c35490bcd5995'


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output.resolve()
    assert out.is_relative_to(ROOT / 'docs/qa/checkpoints') and not out.exists()
    proof = json.loads((FINAL / 'proof.json').read_text())
    assert sha(FINAL / 'proof.json') == EXPECTED
    assert proof['native_route_pass'] and not proof['graphics_complete']
    catalog = json.loads((FINAL / 'catalog.json').read_text())
    assert sha(FINAL / 'catalog.json') == proof['catalog_sha256']
    for name, item in catalog.items():
        source = Path(name)
        assert source.stat().st_size == item['bytes'] and sha(source) == item['sha256'], name
    out.mkdir(parents=True)
    payloads = []

    def copy(source, relative):
        source = Path(source)
        dest = out / relative
        assert dest.is_relative_to(out) and not dest.exists()
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, dest)
        assert sha(source) == sha(dest)
        payloads.append(dict(path=relative, source=str(source),
                             bytes=dest.stat().st_size, sha256=sha(dest)))

    for name in ['proof.json', 'catalog.json', 'review-files.json']:
        copy(FINAL / name, 'final/' + name)
    for name in catalog:
        source = Path(name)
        if not source.is_relative_to(D):
            continue
        if source.suffix not in ['.json', '.png'] and source.name not in ['inputs.csv', 'completed-loop-motion.csv']:
            continue
        copy(source, 'evidence/' + source.relative_to(D).as_posix())
    ready = D / 'mega-proto-pivot-routes0a-static-v1'
    copy(ready / 'observer-only.patch', 'observer-only.patch')
    copy(ready / 'controls-v1/proof.json', 'static-controls.json')
    review = json.loads((FINAL / 'review-files.json').read_text())
    owned = [Path(x) for key in ['owned_tools', 'owned_reports'] for x in review[key]]
    owned.append(Path(__file__).resolve())
    manifest = dict(native_route_pass=True, graphics_complete=False, adopted=False,
                    ROM_sha256=proof['ROM_sha256'], external_catalog_verified=len(catalog),
                    ROOT_selected_whole_frame_placements_viewed=98,
                    residual='Mega head-only frames1941..1943 recover1944; complete flicker fix unproven.',
                    payloads=payloads,
                    owned_files=[dict(path=x.relative_to(ROOT).as_posix(), sha256=sha(x)) for x in owned],
                    scope='Four granted launches; two Easy controller clears and independent replays. No all-weapon, every-frame manual graphics or matched long-route performance claim.')
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    paths = [x.relative_to(ROOT).as_posix() for x in owned] + [out.relative_to(ROOT).as_posix() + '/']
    (out / 'OWNED-FILES.txt').write_text('\n'.join(paths) + '\n')
    print(json.dumps(dict(payloads=len(payloads), external_catalog_verified=len(catalog),
                          manifest_sha256=sha(out / 'manifest.json'))))


if __name__ == '__main__':
    main()
