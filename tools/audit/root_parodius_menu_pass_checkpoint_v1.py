"""Freeze the real menu success and its preserved predecessor failures."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
OUT = ROOT / 'docs/qa/checkpoints/2026-10-26/parodius-menu-native-pass'
PACKETS = {
    'parodius-menu-hint-ready-v1': 'dbc8be4be2bb1fd10ef7651ff1bbf3d5719a599c533a3cb7e9c3bb1967f5ea21',
    'parodius-menu-hint-native-negative-v1': '2860f2b6866bf748aaf3ae5b6cb77bd2362271e4c3e493d0c3977a64218f5d8c',
    'parodius-menu-hint-v2-ready-v1': 'de5930556af259b54cdcd5e0c59d976adab6d9c61ab2fbbfc3870508fad06f2e',
    'parodius-menu-hint-v2-native-phase-negative-v1': '043f98012909514dada366e9e6cdae5481f8777e9e74fff6dcc680b9759efb82',
    'parodius-menu-terminal-phase-ready-v1': '5f75ff650d4b02736a49ba01a119915a5b44ec2b2c8103db160170bf558350c1',
    'parodius-menu-terminal-phase-native-v1': 'aa3926978dacebafe7d13724dd703ac16452d0958b77759f7153703b40f0643b',
    'parodius-menu-terminal-phase-final-v1': '524e16b45df2b63b12306635fd80b8366791e5209680e8ceb69e01a2bc07d16c',
}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not OUT.exists()
    verified, inputs = {}, {}
    for name, expected in PACKETS.items():
        directory = D/name
        assert sha(directory/'proof.json') == expected
        proof = json.loads((directory/'proof.json').read_text())
        assert sha(directory/'manifest.json') == proof['manifest_sha256']
        manifest = json.loads((directory/'manifest.json').read_text())
        for path, digest in manifest.items():
            assert sha(path) == digest, path
            if path in inputs:
                assert inputs[path] == digest, path
            inputs[path] = digest
        verified[name] = len(manifest)
    final = json.loads((D/'parodius-menu-terminal-phase-native-v1/proof.json').read_text())
    assert final['passed'] and final['component_results_present'] == 5
    assert final['same_ROM_old_negative_RGB_prefix_matches'] == 1650
    assert final['same_ROM_old_negative_RGB_differences'] == 0
    assert final['original_bus_prefix_equal']
    OUT.mkdir(parents=True)
    catalog = {}

    def copy(p, name):
        p = Path(p)
        target = OUT/name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(p, target)
        assert sha(target) == sha(p)
        catalog[name] = dict(source=str(p), sha256=sha(p))

    for name in PACKETS:
        for p in (D/name).iterdir():
            # Effective conditions are public; raw settings and footage remain external.
            if p.suffix == '.json':
                copy(p, 'packets/'+name+'/'+p.name)
    source = D/'parodius-menu-hint-candidate-v2/source'
    mapping = json.loads((D/'parodius-hud-source-final-map-v1/proof.json').read_text())
    changed = set(mapping['changed_production_sources']) | {'src/character_select.s'}
    for name in sorted(changed):
        copy(source/name, 'changed-source/'+name)
    for path, digest in inputs.items():
        p = Path(path)
        if p.is_relative_to(ROOT/'tools/audit'):
            copy(p, 'frozen-tools/'+p.name)
    for name in ['parodius-menu-hint-proposal-2026-10-25.txt',
                 'parodius-menu-hint-native-hold-2026-10-25.txt',
                 'parodius-menu-initial-hint-proposal-2026-10-25.txt',
                 'parodius-menu-initial-hint-native-hold-2026-10-26.txt',
                 'parodius-menu-terminal-phase-readiness-2026-10-26.txt',
                 'parodius-menu-terminal-phase-native-2026-10-26.txt']:
        copy(ROOT/'docs/qa'/name, 'reports/'+name)
    copy(D/'parodius-menu-terminal-phase-native-v1/selected-actual-full-PPU.png',
         'selected-actual-full-PPU.png')
    review = dict(passed=True, accepted=False, production_adopted=False,
                  root_verified_manifest_counts=verified,
                  root_viewed_actual_full_PPU_frames=final['selected_actual_full_PPU_frames'],
                  review='Four vehicle menus, cancellation/rebuild, first custom HUD and late frames reviewed. Transitional black and partly cleared frames retained. Dense HUD labels and crowded sprite visibility remain open.',
                  remaining=['death/restart', 'actual area catch-up/Buffer2 hold',
                             'worst-case DMC', 'crowded body visibility', 'HUD readability'],
                  raw_settings_and_lossless_captures_retained_external=True,
                  copied_bindings=catalog)
    (OUT/'root-review.json').write_text(json.dumps(review, indent=2)+'\n')
    print(json.dumps(dict(checkpoint=str(OUT), verified=verified, copied=len(catalog))))


if __name__ == '__main__':
    main()
