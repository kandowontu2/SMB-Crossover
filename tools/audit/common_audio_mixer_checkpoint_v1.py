"""Small review checkpoint for independent shared-audio f4efd; no ROM copy."""
from pathlib import Path
import argparse
import json
import shutil
from smb3_host_current3b_cpu_v1 import D, R, sha, put


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output = a.output.resolve()
    a.output.mkdir(parents=True, exist_ok=False)
    src = D/'common-audio-mixer-current3b-v3'
    old = D/'common-audio-mixer-current3b-v2'
    native = D/'common-audio-mixer-f4efd-mega450-ready-v1'
    ready = native/'final-freeze-v1/readiness.json'
    assert sha(ready) == '8ff1e75fe688cac3702b0aaedb1803698db5b6d03d7fbbbfcecc062566d88780'
    q = json.loads(ready.read_text())
    assert q['passed'] and q['worker_released'] and not q['adopted']
    for f, h in q['bindings'].items():
        assert sha(f) == h, f
    payloads = {
        'source-readiness.json': src/'source-freeze-v1/readiness.json',
        'native-final-readiness.json': ready,
        'implementation.patch': src/'implementation.patch',
        'source-overlay/src/guest_audio.s': src/'source/src/guest_audio.s',
        'source-overlay/src/mmc5_sfx.s': src/'source/src/mmc5_sfx.s',
        'source-receipts/proof.json': src/'proof.json',
        'source-receipts/layout.json': src/'layout.json',
        'source-receipts/canonical-and-flagoffs.json': src/'build-controls-v1/proof.json',
        'source-receipts/caller7344.json': old/'controls-v1/proof.json',
        'source-receipts/whole-roster9472.json': old/'roster-v1/proof.json',
        'source-receipts/IRQ1072.json': old/'irq-v1/proof.json',
        'source-receipts/matched768-costs.json': old/'whole-v1/proof.json',
        'negative-drafts/first-assembly.json': D/'common-audio-mixer-current3b-v1/failure.json',
        'negative-drafts/unguarded-ordinary-scope.json': old/'ordinary-scope-v1/scope.json',
        'native-receipts/ROOT-grant.json': native/'ROOT-grant.json',
        'native-receipts/launch.json': native/'launch.json',
        'native-receipts/native-receipt.json': native/'native-receipt.json',
        'native-receipts/result.json': native/'result.json',
        'native-receipts/paired-review.json': native/'review-v1/proof.json',
        'images/paired-selected-wholeframes.png': native/'review-v1/paired-selected-wholeframes.png',
        'reports/source.txt': R/'docs/qa/common-audio-mixer-source-2026-10-26.txt',
        'reports/native.txt': R/'docs/qa/common-audio-mixer-native-2026-10-26.txt',
    }
    rows = []
    for name, f in payloads.items():
        target = a.output/name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(f, target)
        assert sha(target) == sha(f)
        rows.append(dict(path=name, source=str(f), sha256=sha(f), bytes=f.stat().st_size))
    owned = ['tools/audit/'+name for name in [
        'common_audio_mixer_prepare_v1.py', 'common_audio_mixer_prepare_v2.py',
        'common_audio_mixer_prepare_v3.py', 'common_audio_mixer_controls_v1.py',
        'common_audio_mixer_roster_v1.py', 'common_audio_mixer_irq_v1.py',
        'common_audio_mixer_whole_v1.py', 'common_audio_mixer_build_v1.py',
        'common_audio_mixer_freeze_v1.py', 'common_audio_mixer_native_prepare_v1.py',
        'common_audio_mixer_native_review_v1.py', 'common_audio_mixer_native_freeze_v1.py',
        'common_audio_mixer_checkpoint_v1.py', 'smb3_host_mixer_profile_v1.py',
        'smb3_host_sweep_profile_v1.py',
    ]] + ['docs/qa/common-audio-mixer-source-2026-10-26.txt',
          'docs/qa/common-audio-mixer-native-2026-10-26.txt']
    owned_rows = [dict(path=n, sha256=sha(R/n), bytes=(R/n).stat().st_size) for n in owned]
    (a.output/'OWNED-FILES.txt').write_text('\n'.join(owned)+'\n'+
        str(a.output.relative_to(R)).replace('\\', '/')+'/\n', encoding='utf-8')
    (a.output/'README.txt').write_text('''PRIVATE / UNADOPTED SHARED-AUDIO PERFORMANCE COMPONENT
Parent3b -> f4efd; two source files,186 bank29 bytes, no new RAM/assets.
This checkpoint combines SOURCE proof and ONE finite native MegaEasy450
no-regression comparison. It is independent of held authentic SMB3 music.
Source:7344caller/9472all37AudioUpdate/1072IRQ/768cost comparisons pass.
Actual expansion savings31..35cycles; duplicate cleanup up to55depending
identity/state. Ten genuine private labels move; public boundaries fixed.
Initial assembly and ordinary-scope draft failures remain explicit.
Guarded canonicalf4efd and ordinaryd444/f4ffd exact. See source report for
the same-ROM v2/v3 receipt distinction and intermediate predicate read.
Native: one authorised450 launch, zero retries, worker released. Same449
input polls,402DMAs/72safe enables/275PPU frames as genuine3b. No cumulative
visible DMA deficit;275fullRGB pairs identical. FiveSMC/AXY/SP/bank/IRQ and
full256source/destination/render-disabled DMA guards passed. One six-pair
sheet is included; existing hardware8-sprite body contention remains in
BOTH. No waveform, sprite fairness, all-roster gameplay or route claim.
The source-only marker on the original source receipt is intentionally
unchanged; final native receipt separately records the completed scope.
No ROM/NSF/DMC/emulator/settings/lossless capture payload is copied here.
External path/hash bindings are retained; full reproduction needs those
local inputs and original runtime. OWNED-FILES is ROOT's explicit review
list, not an instruction to stage unrelated shared-workspace files.
''', encoding='utf-8')
    review = dict(
        exact_patch_and_source=['implementation.patch', 'source-overlay/src/guest_audio.s', 'source-overlay/src/mmc5_sfx.s'],
        source_contract=['reports/source.txt', 'source-receipts/proof.json', 'source-receipts/layout.json'],
        actual_native=['reports/native.txt', 'native-receipts/native-receipt.json', 'native-receipts/paired-review.json'],
        visual=['images/paired-selected-wholeframes.png'],
        immutable_failures=['negative-drafts/first-assembly.json', 'negative-drafts/unguarded-ordinary-scope.json'])
    put(a.output/'REVIEW-FILES.json', review)
    put(a.output/'manifest.json', dict(passed=True, adopted=False, source_and_native_component=True,
        ROM_sha256=q['ROM_sha256'], parent_ROM_sha256=q['parent_ROM_sha256'],
        source_readiness_sha256=q['source_readiness_sha256'], final_native_readiness_sha256=sha(ready),
        payloads=rows, stable_owned_files=owned_rows, checker_sha256=sha(__file__),
        external_reproduction_limit='All binary/source/runtime/raw-observation paths remain bound externally; no native or game-source installation is performed.'))
    files = [f for f in a.output.rglob('*') if f.is_file()]
    print(json.dumps(dict(passed=True, files=len(files), bytes=sum(f.stat().st_size for f in files),
        owned_files=len(owned), manifest_sha256=sha(a.output/'manifest.json'))))


if __name__ == '__main__':
    main()
