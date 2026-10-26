"""Create a small public review packet; never copy game/audio/settings/capture payloads."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
OUT = ROOT / 'docs/qa/checkpoints/2026-10-26/mario-first-mushrooms900-v1'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=False)
    first = D / 'mario-powerups900-first-v2/native-result-freeze-v1'
    final = D / 'mario-powerups900-smb3-corrected-v1/native-result-freeze-v2'
    assert sha(first / 'proof.json') == 'd28e07a9f66648fb1a9c075cd4456ecaf074c36dcb7f0117b7eccefdf9a15968'
    assert sha(final / 'proof.json') == '80e566a642ce6cf986edefc8b4611e8902dbbf4a3dad69b4f09dfc7f3776135f'
    files = []
    def copy(src, name, role):
        assert src.is_file()
        assert src.suffix.lower() in ['.py', '.lua', '.json', '.txt', '.png', '.diff']
        assert src.name.lower() != 'settings.json'
        target = OUT / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, target)
        files.append(dict(path=name, sha256=sha(target), bytes=target.stat().st_size,
                          role=role, original_path=str(src), original_sha256=sha(src)))
    for p in sorted((ROOT / 'tools/audit').glob('mario_powerups*.py')):
        copy(p, 'frozen-tools/' + p.name, 'Exact preparation/observer/source/result/checkpoint tool; historical failed versions retained')
    for p in sorted((ROOT / 'tools/audit').glob('mario_powerups*.lua')):
        copy(p, 'frozen-tools/' + p.name, 'Exact read-only physical-item observer/controller module')
    for name in ['mario-powerups-current3cee-preparation-2026-10-26.txt',
                 'mario-powerups900-first-native-2026-10-26.txt',
                 'mario-powerups900-smb3-corrected-2026-10-26.txt',
                 'mario-powerups900-smb3-native-2026-10-26.txt']:
        copy(ROOT / 'docs/qa' / name, 'reports/' + name, 'Scope and source/native outcome report')
    for src, prefix in [(first, 'first-partial'), (final, 'corrected-SMB3')]:
        for name in ['proof.json', 'final-receipt.json', 'agent-visual-review.json']:
            copy(src / name, prefix + '/' + name, 'Bound native/source/visual metadata only; no ROM or lossless telemetry payload')
    for src, name in [(first / 'mario-selected12.png', 'mario-selected12.png'),
                      (first / 'luigi-selected12.png', 'luigi-selected12.png'),
                      (final / 'mario3-selected16.png', 'mario3-selected16.png'),
                      (final / 'luigi3-selected16.png', 'luigi3-selected16.png')]:
        copy(src, 'image-samples/' + name, 'Inspected concise actual-PPU sample sheet, not every-frame/art certification')
    extra = [
        (first / 'mario3-first-failure.json', 'negatives/original-native-type-failure.json'),
        (D / 'mario-powerups900-first-v1/failed-static-oracle-v1/failure.json', 'negatives/first-static-mock-failure.json'),
        (D / 'mario-powerups900-smb3-corrected-v1/native-result-freeze-v1/failure.json', 'negatives/offline-mature-state-parser-failure.json'),
        (D / 'mario-powerups900-source-mature-v1/proof.json', 'source-mature96/proof.json'),
        (D / 'mario-powerups900-smb3-corrected-v1/freeze-v1/native-oracle-only.diff', 'source-mature96/native-oracle-only.diff')]
    for src, name in extra:
        copy(src, name, 'Exact preserved negative or bounded actual assembled source-oracle correction evidence')
    readme = '''Four first-mushroom outcomes on exact900: public review checkpoint

ROM SHA256900b669e212b878041c23e438f2fb26e310ce8f929f904681a9c4b17405b6968.
Review-files.json maps every shipped file to its role, exact original and SHA256.
No ROM/NSF/DMC/settings/archive/audio/video/lossless telemetry payload is copied.

MarioEasy / LuigiEasy: first batch endpoints1060/1748,0deaths, real mushroom,
60native transform calls each,24crouch/54air frames, finalSuper, CHR/motion pass.
SMB3MarioEasy / SMB3LuigiEasy: corrected batch endpoints924/926,0deaths,
actual$d1/owner17/maturetype0 collection,47growth calls each,24crouch/56air,
finalform1/Super, CHR/motion pass. Both actual numericEasy0 and chosen variants.

Original first batch remains FALSE because its M3 assertion wrongly expected
emergingtype1 at mature walking collection. Source bank90 A441:A9009534 sets
PowerUpType0 at STA A443. Two-variant/96tick actual CPU proof authenticates
transient1, full rise, mature0 and collision admission. Only this test assertion
changed; native source, actor, tier, position and RNG were never injected.
The original failed native and offline parser/mocked-oracle negatives remain.

All four successes are EXACT900 COMPONENTS, not fresh ordinary3cee/Hard/allitem
or final-ROM results. Sample sheets reflect selected actual wholePPU images:
first two12each; SMB3two16placements each (30unique images between lattertwo).
No exhaustive source-pixel/waveform/body/fiveSMC/SP/full-route certification.
Raw reveal/pickup request counts are stores, not distinct audible sounds.

This is a review checkpoint, not an automatic emulator-run/install recipe.
Every historical native grant was consumed; reruns need ROOT review and a
new bounded grant. The complete external captures and proofs remain preserved.
'''
    (OUT / 'README.txt').write_text(readme, encoding='utf-8')
    files.append(dict(path='README.txt', sha256=sha(OUT / 'README.txt'), bytes=(OUT / 'README.txt').stat().st_size,
                      role='Review scope and explicit limits'))
    manifest = dict(passed=True, source_and_review_checkpoint_only=True,
                    game_ROM_audio_settings_lossless_payloads_copied=False,
                    ROM_sha256='900b669e212b878041c23e438f2fb26e310ce8f929f904681a9c4b17405b6968',
                    files=files, total_bytes=sum(z['bytes'] for z in files),
                    first_partial_native_FALSE_preserved=True,
                    independent_native_launches_by_checkpoint=0)
    (OUT / 'review-files.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(passed=True, output=str(OUT), files=len(files), bytes=manifest['total_bytes'],
                          review_map_sha256=sha(OUT / 'review-files.json')), indent=2))


if __name__ == '__main__':
    main()
