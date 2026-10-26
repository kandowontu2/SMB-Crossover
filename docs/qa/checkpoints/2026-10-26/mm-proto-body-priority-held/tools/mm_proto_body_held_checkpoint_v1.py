"""Publish only the bounded text/source/pixel review of held body-priority00fb."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil

R = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
BASE = D / 'mm-proto-clean-menu-candidates-v1/clean-menu-irq'
GAME = D / 'mm-proto-body-priority-v3'
SRC = GAME / 'ready-v1'
NATIVE = D / 'mm-proto-body-priority-450-ready-v1'
FROZEN = NATIVE / 'native-freeze-v1'
BASE_SHA = '731c918b0f448564587d90fca2979afc9fc0e5eb9b26616f4241801e2e73e16c'
GAME_SHA = '00fb4a72ec9788f7b2878d6201f70a96ae6e47b4935ba186648c7edc04806a62'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read(p):
    return json.loads(Path(p).read_text())


def put(p, value):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(json.dumps(value, indent=2) + '\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    out = args.output.resolve()
    assert out.is_relative_to(R / 'docs/qa/checkpoints')
    out.mkdir(parents=True, exist_ok=False)
    assert sha(BASE / 'candidate.nes') == BASE_SHA
    assert sha(GAME / 'candidate.nes') == GAME_SHA
    assert sha(SRC / 'receipt.json') == '4fc29c37dd31d0cd386bfc87bbdd009252e160b19dba6b757fbb012cc1710e6a'
    assert sha(FROZEN / 'receipt.json') == '7470ef6128141c76bda38eaaabb4257f3bd323bbb600684c7b950153c2bc39c2'
    source_receipt = read(SRC / 'receipt.json')
    native_receipt = read(FROZEN / 'receipt.json')
    assert native_receipt['candidate_held'] and not native_receipt['native_no_harm_cadence_pass']
    assert native_receipt['launches'] == 1 and native_receipt['retries'] == 0
    # Verify the existing frozen inputs; never rerun build, CPU, emulator or decoder.
    source_deps = read(SRC / 'dependency-bindings.json')
    native_deps = read(FROZEN / 'all-actual-artifact-bindings.json')
    for p, h in source_deps.items():
        assert sha(p) == h, p
    for p, data in native_deps.items():
        assert Path(p).stat().st_size == data['bytes'] and sha(p) == data['sha256'], p
    copied = {}

    def copy(p, relative):
        p = Path(p)
        dst = out / relative
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(p, dst)
        assert sha(dst) == sha(p)
        copied[relative] = dict(original=str(p.resolve()), sha256=sha(p), bytes=p.stat().st_size)

    old = read(BASE / 'source-manifest.json')
    new = read(GAME / 'source-manifest.json')
    changed = read(SRC / 'production-delta.json')
    assert set(changed) == {'smb1base-mmc5-expanded.cfg', 'src/megaman_weapons.s', 'src/metasprite_engine.s'}
    for relative, values in changed.items():
        assert old[relative] == values['parent'] and new[relative] == values['candidate']
        assert sha(BASE / 'source' / relative) == values['parent']
        assert sha(GAME / 'source' / relative) == values['candidate']
        copy(GAME / 'source' / relative, 'source-overlay/' + relative)
    copy(SRC / 'production-delta.json', 'source-delta.json')
    copy(SRC / 'source-review.patch', 'source-review.patch')
    copy(SRC / 'genuine-symbol-movement.json', 'genuine-symbol-movement.json')
    copy(SRC / 'qualification.json', 'CPU/qualification.json')
    for p in sorted((SRC / 'proofs').glob('*.json')):
        assert read(p)['passed']
        copy(p, 'CPU/' + p.name)
    copy(GAME / 'capacity-closure-v3/proof.json', 'CPU/capacity-closure-v3.json')
    for name in ['mm-proto-body-priority-2026-10-26.txt', 'mm-proto-body-priority-capacity-2026-10-26.txt', 'mm-proto-body-priority-native-2026-10-26.txt']:
        copy(R / 'docs/qa' / name, 'reports/' + name)
    for folder in [SRC / 'tools', FROZEN / 'tools']:
        for p in sorted(folder.glob('*.py')):
            copy(p, 'tools/' + p.name)
    copy(__file__, 'tools/' + Path(__file__).name)
    for p, dest in [
        (SRC / 'receipt.json', 'external-source-freeze.json'),
        (FROZEN / 'receipt.json', 'external-native-freeze.json'),
        (NATIVE / 'native-receipt.json', 'native/launch-receipt.json'),
        (NATIVE / 'review-v1/proof.json', 'native/mechanical-hardware-positive.json'),
        (NATIVE / 'paired-review-v1/proof.json', 'native/paired-review-held.json'),
        (NATIVE / 'deficit-review-v1/proof.json', 'native/physical-deficits-held.json'),
        (NATIVE / 'ROOT-grant.json', 'native/original-grant.json'),
        (D / 'mm-proto-body-priority-v2/callers-v2/failure.json', 'negatives/92797527-real-caller-V-failure.json'),
        (D / 'mm-proto-body-priority-v1/failure.json', 'negatives/assembler-v1-failure.json'),
    ]:
        copy(p, dest)
    # Already-generated actual native pixels, without decoding/cropping again.
    for relative in ['paired-review-v1/paired-menu-start-wholeframes.png', 'paired-review-v1/paired-early-game-wholeframes.png', 'paired-review-v1/paired-early-game-bottom-actual.png', 'deficit-review-v1/paired-deficit-wholeframes.png']:
        copy(NATIVE / relative, 'actual-pixels/' + Path(relative).name)
    external = [
        BASE / 'candidate.nes', BASE / 'candidate.dbg', BASE / 'source-manifest.json',
        D / 'mm-proto-clean-menu-candidates-v1/freeze-v1/receipt.json',
        GAME / 'candidate.nes', GAME / 'candidate.dbg', GAME / 'source-manifest.json',
        SRC / 'source.zip', SRC / 'catalog.json', SRC / 'source-inputs.json',
        SRC / 'dependency-bindings.json', FROZEN / 'all-actual-artifact-bindings.json',
        FROZEN / 'catalog.json', NATIVE / 'readiness.json',
        NATIVE / 'paired-review-v1/all275-paired-observations.json',
        D / 'root-presentation450-731-v1/readiness.json',
    ]
    external += [Path(p) for p in source_deps if Path(p).suffix == '.py' and Path(p).name not in {Path(k).name for k in copied if k.startswith('tools/')}]
    put(out / 'external-bindings.json', {str(p.resolve()): dict(bytes=p.stat().st_size, sha256=sha(p)) for p in sorted(set(external))})
    put(out / 'copy-origins.json', copied)
    put(out / 'review-files.json', dict(
        source=['source-overlay', 'source-review.patch', 'source-delta.json', 'genuine-symbol-movement.json'],
        source_controls=['CPU', 'external-source-freeze.json', 'tools'],
        actual_native=['native', 'actual-pixels', 'external-native-freeze.json'],
        preserved_failures=['negatives', 'reports'],
        reproducibility=['external-bindings.json', 'copy-origins.json', 'catalog.json', 'proof.json'],
        staging_map=[str(out.relative_to(R)).replace('\\', '/'), 'tools/audit/' + Path(__file__).name],
        excludes=['ROM', 'audio/NSF', 'settings', 'ZIP/source archive', 'raw/lossless capture', 'staging/commit/push', 'new game patch or emulator run'],
    ))
    (out / 'README.txt').write_text('''MEGA/PROTO BODY-FIRST00fb -- HELD REVIEW CHECKPOINT\n\nSource-safe and native performance/visibility acceptance are distinct.\nThe six finite source/CPU controls, capacity closure and canonical/ordinary\nbuilds PASS; the actual same-input450 comparison FAILS cadence and exposes\nbody-versus-bullet visibility tradeoffs. DO NOT ADOPT OR INSTALL00fb.\n\nBASE / EXACT SOURCE RESTORATION\nStart from frozen clean731 source (full external bindings included). Apply\nonly source-overlay's three exact files. Original EOLs are retained; the\npatch is a readable aid. The resulting00fb changes494PRG bytes, onlybank4;\nheader/CHR/RAM/otherbanks are exact. Ordinary MMC3 d444cac8 and MMC5 f4ffd248\nbuilds remain byte-exact. Do not overlay an unrelated newer source tree.\nAll16 versioned source tools and seven native/capacity tools are copied\nfrom their already-frozen packets. Shared imports and full source manifests\nare explicitly hash-bound external prerequisites, not silently regenerated.\n\nQUALIFICATION / GENUINE NEGATIVE\nCPU/ contains six source receipts plus the later capacity closure. The\nindependent partition oracle preserves every emitted record/value/order,\nall original returnedAXYP/SP, genuine label mappings, banks and5SMC.\nOwned active cost+159..160cycles is explicit; foreign costs-23..0.\nThe original92797527 caller failure is included unchanged: savedV leaked\ninto BillNativeReturnP7FF4 as70 instead of30. It was repaired in00fb,\nnot excluded. The source report classifies invalid early fixtures too.\nThe arbitrary impossible Proto cursor0 arithmetic counterexample remains\nexternal; capacity closure proves live prebody aligned44..252 and retains\nreal emitters/carry guards rather than an invented admissibility mask.\n\nACTUAL NATIVE: HARDWARE POSITIVE, CADENCE/VISIBILITY HELD\nExactly one authorized450 launch; no retry. Baseline731 has402physical\nDMAs;00fb has401. Every completed candidate256-byte DMA matches actual\nhardware, all rendering/mask guards pass,442NMI and79IRQ31 checks pass.\n449actual input triples and450prefix bytes are exact. Nonetheless15\nvisible-cutoff frames have a completed-DMA prefix deficit:385 and437..450;\nmax2/final1. First385 carries previous physical image at the same capture\nCPU11463001: baselineDMA366completed385:249:287, candidateDMA365completed\n384:249:283. This is physical publication evidence, not endFrame relabeling.\nNo Main release/stackedPC/source-epoch log was captured, so exact first\ncausal Main instruction is not claimed. No guard was relaxed.\n\nAll275RGBpairs were compared:206exact/69different.267activeOAMmultisets\nmatch. Actual403/404show more complete body/legs alongside fewer complete\nbuster circles, with the same active record multiset. Fixed body priority\ncan permanently starve bullet planes/world. These selected pixels do not\nprove per-live-slot fairness, all poses/abilities, Proto or a full1-1 route.\nStartup184/194/204/371 and early372/373are exact selected whole images.\nThe four copied sheets are actual native pixels, not reconstructions.\n\nThe external raw/capture/settings/ROM/source archives remain immutable.\nOldc5/b0 shot-menu failures remain separate, documented by the source/native\nreports and their public draw-phase checkpoint; no old native result is\nretagged. This checkpoint performs copying/hashing only: no rebuild, CPU\nrerun, native launch, optimization, installation, staging, commit or push.\nParent ROOT controls publication and any subsequent experiments.\n''')
    catalog = {str(p.relative_to(out)).replace('\\', '/'): dict(bytes=p.stat().st_size, sha256=sha(p)) for p in sorted(out.rglob('*')) if p.is_file()}
    put(out / 'catalog.json', catalog)
    proof = dict(passed=True, checkpoint_verified=True, candidate_held=True, adopted=False,
                 source_CPU_qualified=True, native_mechanical_guards_pass=True, native_no_harm_cadence_pass=False,
                 parent_ROM_sha256=BASE_SHA, candidate_ROM_sha256=GAME_SHA,
                 source_freeze_sha256=sha(SRC / 'receipt.json'), native_freeze_sha256=sha(FROZEN / 'receipt.json'),
                 verified_source_dependency_count=len(source_deps), verified_actual_native_artifact_count=len(native_deps),
                 source_overlay_files=3, exact_changed_PRG_bytes=494, only_changed_PRG_bank=4,
                 six_source_receipts=6, capacity_closure_included=True, original_real_caller_V_failure_included=True,
                 original_native_launches=1, new_launches=0, retries=0, worker_released=True,
                 completed_hardware_DMA=[402, 401], physical_prefix_deficit_frames=[385] + list(range(437, 451)),
                 catalog_files=len(catalog), catalog_bytes=sum(v['bytes'] for v in catalog.values()),
                 catalog_sha256=sha(out / 'catalog.json'), external_bindings_sha256=sha(out / 'external-bindings.json'),
                 review_files_sha256=sha(out / 'review-files.json'), checkpoint_tool_sha256=sha(__file__),
                 limits='No source-safe/native performance equivalence claim. No new build/CPU/native, source archive, ROM/audio/settings/raw payload or production/Git mutation.')
    put(out / 'proof.json', proof)
    print(json.dumps(dict(checkpoint=str(out), proof_sha256=sha(out / 'proof.json'), **proof), indent=2))


if __name__ == '__main__':
    main()
