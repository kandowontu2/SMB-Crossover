"""Make a compact review-only checkpoint of four exact900 physical flower attempts."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
OUT = ROOT / 'docs/qa/checkpoints/2026-10-26/mario-physical-flower900-v1'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=False)
    files = []

    def copy(src, name, role):
        assert src.is_file(), src
        assert src.suffix.lower() in ['.py', '.lua', '.json', '.txt', '.png', '.diff']
        assert src.name.lower() != 'settings.json'
        target = OUT / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, target)
        files.append(dict(path=name, sha256=sha(target), bytes=target.stat().st_size,
                          role=role, original_path=str(src), original_sha256=sha(src)))

    packets = [
        ('mario-flower900-first-v1', 'failure-freeze-v1', '592ec9170302df31584ed0f00d66d6a704bda913de830477f5b86159a23aba57', 'v1-FALSE'),
        ('mario-flower900-corrected-v2', 'failure-freeze-v1', '5adad47072a91fcca3133b0bb38e4c3eadc72e175ac2e57759de6b35757bd67a', 'v2-FALSE'),
        ('mario-flower900-right-v3', 'native-result-freeze-v1', '346acb5c51bdf9b716034b899a63a2aff63da4dd95d470918711614f0b24147d', 'v3-FALSE'),
        ('mario-flower900-east-v4-ready-v2', 'native-result-freeze-v1', 'd2524aeb0b7701a1921f175e000db5849bc9e985c1e2ef387d90c9bf7aa60f35', 'v4-PASS')]
    for folder, freeze, expected, prefix in packets:
        p = D / folder
        f = p / freeze
        assert sha(f / 'proof.json') == expected
        for name in ['proof.json', 'selected-images.json']:
            copy(f / name, prefix + '/' + name, 'Immutable exact-attempt evidence metadata; historical FALSE remains FALSE')
        for name in ['native-proof.json', 'mario-easy/native-receipt.json']:
            copy(p / name, prefix + '/' + Path(name).name, 'Actual original native outcome, no retag or retry')
    for p in sorted((ROOT / 'tools/audit').glob('mario_flower900*')):
        if p.suffix in ['.py', '.lua']:
            copy(p, 'frozen-tools/' + p.name, 'Exact source/observer/controller/result/checkpoint tool')
    for name in ['mario-flower900-first-failure-2026-10-26.txt',
                 'mario-flower900-corrected-failure-2026-10-26.txt',
                 'mario-flower900-right-approach-source-2026-10-26.txt',
                 'mario-flower900-right-native-2026-10-26.txt',
                 'mario-flower900-east-preparation-2026-10-26.txt',
                 'mario-flower900-east-native-2026-10-26.txt']:
        copy(ROOT / 'docs/qa' / name, 'reports/' + name, 'Source/native finding and practical scope')
    first = D / 'mario-flower900-first-v1/failure-freeze-v1'
    second = D / 'mario-flower900-corrected-v2/failure-freeze-v1'
    third = D / 'mario-flower900-right-v3/native-result-freeze-v1'
    fourth = D / 'mario-flower900-east-v4-ready-v2'
    extras = [
        (first / 'contact-evidence.json', 'v1-FALSE/contact-evidence.json'),
        (second / 'trajectory.json', 'v2-FALSE/trajectory.json'),
        (third / 'component-evidence.json', 'v3-FALSE/component-evidence.json'),
        (fourth / 'native-result-freeze-v1/component-evidence.json', 'v4-PASS/component-evidence.json'),
        (fourth / 'native-result-freeze-v1/agent-visual-review.json', 'v4-PASS/agent-visual-review.json'),
        (fourth / 'east-source-controls-v1/proof.json', 'v4-PASS/east-source-controls.json'),
        (fourth / 'observer-controller-only.diff', 'controller-revision/v3-to-v4.diff'),
        (fourth / 'preparation-erratum-v1.json', 'retained-preparation-negatives/path-erratum.json'),
        (D / 'mario-flower900-east-v4/preparation-first-error-v1/proof.json', 'retained-preparation-negatives/first-base-mock-error.json'),
        (fourth / 'native-result-freeze-v1/failed-analyzer-v1.py', 'retained-preparation-negatives/failed-input-column-analyzer.py'),
        (fourth / 'native-result-freeze-v1/offline-analysis-first-error.txt', 'retained-preparation-negatives/input-column-error.txt')]
    for src, name in extras:
        copy(src, name, 'Preserved actual source/result/correction/negative metadata; no native rerun')
    for src, name in [
        (first / 'partial-progression-and-contact.png', 'v1-injury.png'),
        (second / 'partial-progression-and-short-jump.png', 'v2-short-jump.png'),
        (third / 'real-pickups-growth-and-fire.png', 'v3-physical-fire-no-contact.png'),
        (fourth / 'native-result-freeze-v1/physical-progression-selected15.png', 'v4-physical-progression.png'),
        (fourth / 'native-result-freeze-v1/real-contact-drain-selected12.png', 'v4-contact-and-drain.png')]:
        copy(src, 'image-samples/' + name, 'Inspected selected complete actual-PPU images; not exhaustive visual certification')
    readme = '''MarioEasy physical flower: four-attempt exact900 review checkpoint

ROM SHA256900b669e212b878041c23e438f2fb26e310ce8f929f904681a9c4b17405b6968.
Review-files.json maps every copied file to its exact original, hash and role.
No ROM/NSF/DMC/settings/audio/video/lossless telemetry payload is shipped.
No native launch, game edit, installation or Git operation occurs in this tool.

v1 FALSE: blind back alignment exposes Mario to a real falling Goomba1395.
v2 FALSE: left retreat with late horizontal launch falls short; injury1472.
v3 FALSE: both real pickups/120growth/Fire succeed, but stationary shots miss
all targets until original500-step use/release bound. No full pass is inferred.
v4 PASS: unchanged physical right mount, then normal East travel/B16/4 pulse,
real live Goomba contact1898, release1899..1944, both slots clear by1911,
endpoint1945,0deaths. Only one launch of each separately granted fixture.

v4 actual pickups839/1457 are mushroom0 then flower1 from authored336/1248.
Each original transformation runs60source updates. Fire2 persists1518..1945.
CHR1396 observed frames/0bad; completed-motion1476checks/maxworld-camera3.
20raw allocation writes form10frame/slot groups, not20distinct shots.
9brick-handler admissions are not nine destroyed bricks. Reveal8/pickup4/
fire20 are source queue stores, not distinct audible cues or waveform proof.

Current success uses exact900/private startup-NMI candidate. It is NOT731 or
currentadoption evidence; separate current-hash native qualification is needed.
No allitems/Hard/Luigi/fullroute/artistic-source-fidelity claim. v4 sheets show
27selected wholePPU images; two originals1544/1904 were separately rechecked.
No obvious displaced block, corrupt scenery or missing body part was seen in
those samples. Not every captured frame was visually reviewed.

The exactv3->v4 diff preserves all earlier item/growth/fire/motion/CHR/injury/
death guards and500-step bound, and strengthens actual live-enemy contact.
All earlier FALSE receipts remain intact. Two saved-data/preparation parser
errors and the additive frozen-report path erratum are retained transparently.
The complete external observations remain preserved under the original paths.
'''
    (OUT / 'README.txt').write_text(readme, encoding='utf-8')
    files.append(dict(path='README.txt', sha256=sha(OUT / 'README.txt'), bytes=(OUT / 'README.txt').stat().st_size,
                      role='Review entry point and explicit outcome/coverage boundaries'))
    manifest = dict(passed=True, review_checkpoint_only=True, native_launches_by_checkpoint=0,
                    production_game_source_settings_Git_changes=False,
                    ROM_sha256='900b669e212b878041c23e438f2fb26e310ce8f929f904681a9c4b17405b6968',
                    all_three_native_FALSE_outcomes_preserved=True,
                    binary_ROM_audio_settings_lossless_payload_copied=False,
                    files=files, total_bytes=sum(z['bytes'] for z in files))
    (OUT / 'review-files.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    for row in files:
        assert sha(OUT / row['path']) == row['sha256'] == row.get('original_sha256', row['sha256'])
    print(json.dumps(dict(passed=True, output=str(OUT), files=len(files), bytes=manifest['total_bytes'],
                          review_map_sha256=sha(OUT / 'review-files.json')), indent=2))


if __name__ == '__main__':
    main()
