"""Package immutable Luigi731 FALSE/PASS evidence; no native or game writes."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
OLD = D / 'luigi-flower731-east-ready-v2'
P = D / 'luigi-flower731-rg-owner-v1'
TARGET = ROOT / 'docs/qa/checkpoints/2026-10-26/luigi-physical-flower731-v1'
ROM = '731c918b0f448564587d90fca2979afc9fc0e5eb9b26616f4241801e2e73e16c'


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def get(p):return json.loads(Path(p).read_text())


def main():
    for path, h, flag in [
        (OLD / 'failure-freeze-v1/proof.json', '0b53208063a6eaa8cbe424ea3b7abeea43da48c5a55130275f05a3810e6c9c9d', False),
        (P / 'native-result-freeze-v1/proof.json', '2db2a43bd8a1b87f951f1a1aa6c27e65ac682e1f88585f7e1355711d6369b551', True)]:
        assert sha(path) == h
        q = get(path)
        assert q.get('passed', q.get('native_passed')) is flag
        for f, expected in q['bindings'].items():assert sha(f) == expected, f
    TARGET.mkdir(parents=True, exist_ok=False)
    files = []

    def copy(src, name, role):
        assert src.suffix.lower() in ['.json', '.txt', '.png', '.py', '.lua', '.diff']
        assert src.name.lower() != 'settings.json'
        dst = TARGET / name;dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        files.append(dict(path=name, sha256=sha(dst), bytes=dst.stat().st_size,
                          original_path=str(src), original_sha256=sha(src), role=role))

    for src, name, role in [
        (OLD / 'failure-freeze-v1/proof.json', 'original-FALSE/proof.json', 'Original immutable wrong-owner overall FALSE and 3949 bindings'),
        (OLD / 'native-proof.json', 'original-FALSE/native-proof.json', 'Original failed native endpoint; never relabeled'),
        (OLD / 'failure-freeze-v1/component-evidence.json', 'original-FALSE/component-evidence.json', 'Successful physical subcomponents within original overall FALSE'),
        (P / 'native-result-freeze-v1/proof.json', 'corrected-PASS/proof.json', 'Exact731 one-launch corrected PASS and 4355 bindings'),
        (P / 'native-proof.json', 'corrected-PASS/native-proof.json', 'Actual corrected native exit0 and finite component receipts'),
        (P / 'luigi-easy/native-receipt.json', 'corrected-PASS/native-receipt.json', 'Actual endpoint/zero-retry/CHR receipt'),
        (P / 'native-result-freeze-v1/component-evidence.json', 'corrected-PASS/component-evidence.json', 'Independent saved-data pickups/growth/Rg allocations/contact/drain'),
        (P / 'native-result-freeze-v1/agent-visual-review.json', 'corrected-PASS/agent-visual-review.json', 'Review of 17 selected complete PPU images; explicit limits'),
        (P / 'native-result-freeze-v1/selected-images.json', 'corrected-PASS/selected-images.json', 'Exact original whole-image placements/hashes'),
        (P / 'Rg-owner-only.diff', 'source/Rg-owner-only.diff', 'Controller unchanged; actual owner/source-allocation/fire/contact/drain observer correction'),
        (P / 'luigi-easy/configuration.json', 'source/actual731-configuration.json', 'Genuine compiled bank/PC/opcode/RAM metadata; not callable aliases'),
        (P / 'source-owner-controls-v1/proof.json', 'source/compiled-owner-controls.json', 'Actual dispatcher/pool limit/lifetime/art/damage components'),
        (P / 'observer-owner-controls-v1/proof.json', 'source/observer-owner-controls.json', 'Positive and foreign/empty/wrong-type/no-contact/opcode mock controls'),
        (P / 'controller-source-controls-v1/proof.json', 'source/controller-source-controls.json', '81 source returns, 360 wait bound and five unsafe controls'),
        (P / 'startup-static-v1/proof.json', 'source/startup-static-controls.json', '439 mocked startup/CHR frames and fixed dispatcher controls'),
        (P / 'freeze-v1/receipt.json', 'source/preparation-freeze.json', 'Unmodified pre-native readiness plus derived timestamp evidence binding'),
        (P / 'existing-capture-SFX-art-evidence.json', 'source/original-capture-SFX-art.json', 'Original source queue versus endFrame pose timestamps; no native result transfer'),
        (P / 'offline-SFX-frame-assumption-error.json', 'retained-negative/offline-SFX-frame-assumption-error.json', 'Retained failed offline timestamp assumption; corrected without native retry')]:
        copy(src, name, role)
    for name in ['luigi_flower731_native_v1.lua', 'luigi_flower731_native_v2.lua',
                 'luigi_flower731_prepare_v1.py', 'luigi_flower731_rg_prepare_v1.py',
                 'luigi_flower731_run_v1.py', 'luigi_flower731_failure_v1.py',
                 'luigi_flower731_result_v1.py', 'luigi_flower731_checkpoint_v1.py']:
        copy(ROOT / 'tools/audit' / name, 'frozen-tools/' + name, 'Exact original/corrected observer, preparation, runner or saved-data tool')
    for name in ['luigi-flower731-first-failure-2026-10-26.txt', 'luigi-flower731-Rg-preparation-2026-10-26.txt', 'luigi-flower731-Rg-native-2026-10-26.txt']:
        copy(ROOT / 'docs/qa' / name, 'reports/' + name, 'Immutable original outcome/preparation/corrected native report')
    for name in ['physical-pickups-growth-selected9.png', 'genuine-Rg-contact-drain-selected8.png']:
        copy(P / 'native-result-freeze-v1' / name, 'image-samples/' + name, '17 inspected complete actual731 PPU placements across two sheets')
    readme = '''Luigi Easy731 physical Fire progression: corrected native PASS; original FALSE retained

Exact ROM731c918b0f448564587d90fca2979afc9fc0e5eb9b26616f4241801e2e73e16c.
Original one-shot native FALSE watched Mario's two projectile slots. Actual Luigi8
uses ten Rg slots/type3 with at most two active; source bridge30/ExpandedEnemyHit.
It really emitted shots, so the original broad no-fireballs description is corrected.
That failed receipt stays FALSE, including its original 500-use-limit failure.

A separately granted corrected ONE-shot native PASS retains the identical gameplay
controller and old limits/semantic guards. Actual character8/variant1/Easy0, real
pickups851/1653,60+60 growth updates, eight genuine Rg3 allocations and eight actual
original source sound requests. Live green Koopa slot2/contact2007;46 neutral polls;
all ten slots empty from2017 through2054. Zero deaths, finalFire2. CHR1516/0bad;
motion1535/maxworld-camera3. Sound queue evidence is not audible/waveform parity.

Owner metadata binds genuine compiled instructions/banks/opcodes; no game aliases.
Positive and foreign/empty/no-contact/opcode controls remain. No actor/outcome/game
state injection.17 selected complete actualPPU images reviewed; no obvious corrupt
scenery/blocks/body in those samples. Not every frame, intended-palette/source-art,
fullDMA/stack/fiveSMC, Hard/allitems/fullroute or fullcampaign certification.

Review-files.json maps each copy to its exact original hash and role. Full native
captures remain external. This package includes no ROM/NSF/DMC/settings/raw capture,
launches no emulator and changes no production/default/Git/settings files.
'''
    (TARGET / 'README.txt').write_text(readme, encoding='utf-8')
    files.append(dict(path='README.txt', sha256=sha(TARGET / 'README.txt'), bytes=(TARGET / 'README.txt').stat().st_size, role='Compact review entry point and bounded claims'))
    manifest = dict(passed=True, checkpoint_only=True, ROM_sha256=ROM, historical_FALSE_preserved=True,
                    actual_native_launches_recorded=2, native_launches_by_checkpoint=0,
                    copied_ROM_audio_settings_raw_payload=False, files=files, total_bytes=sum(f['bytes'] for f in files))
    (TARGET / 'review-files.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    for r in files:assert sha(TARGET / r['path']) == r['sha256'] == r.get('original_sha256', r['sha256'])
    print(json.dumps(dict(passed=True, files=len(files), bytes=manifest['total_bytes'], path=str(TARGET), review_map_sha256=sha(TARGET / 'review-files.json')), indent=2))


if __name__ == '__main__':main()
