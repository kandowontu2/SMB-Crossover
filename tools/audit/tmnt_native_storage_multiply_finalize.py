"""Freeze the source/CPU-qualified private ACBD optimization; no native claim."""
from pathlib import Path
import argparse
import difflib
import json
import shutil
import subprocess
import sys
import zipfile
from check_tmnt_audio_fallback_oc import qualified
from tmnt_native_storage_driver import ROOT, CURRENT, sha


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--experiment', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    d, out = a.experiment, a.output
    assert not out.resolve().is_relative_to(ROOT)
    candidate, donor = d / 'multiply-current-a983-v1', d / 'ready-dispatch-v1'
    assert sha(donor / 'receipt.json') == '97a8dd5abe01d8d9217800ed8c1be22ebf050a3dbce04a8ae800d670b754b3a6'
    digest = sha(candidate / 'candidate.nes')
    assert digest == '2f61cd0ce8d1fdef09185bdeaad3d5fcb1072f6a28cc54c05c0c1c39ca792523'
    frozen = json.loads((d / 'current-baseline-v1/frozen-source.json').read_text())
    assert sha(ROOT / 'build/smb-crossover-mmc5-expanded.nes') == CURRENT
    assert all(sha(ROOT / name) == value for name, value in frozen['source_files'].items())
    old, new = (donor / 'candidate.nes').read_bytes(), (candidate / 'candidate.nes').read_bytes()
    bank = lambda raw, n: raw[16 + n * 8192:16 + (n + 1) * 8192]
    changed = {n: [i for i in range(8192) if bank(old, n)[i] != bank(new, n)[i]] for n in range(128)}
    changed = {n: values for n, values in changed.items() if values}
    assert set(changed) == {63} and len(changed[63]) == 79
    assert set(changed[63]).issubset(set(range(0x125, 0x173)) | set(range(0xcbd, 0xcc1)))
    assert old[:16] == new[:16] and old[1048592:] == new[1048592:]
    assert qualified(donor / 'candidate.nes').items() <= qualified(candidate / 'candidate.nes').items()
    proofs = {}
    labels = ['multiply-domain-v1', 'multiply-songs-v2', 'multiply-outer-v1', 'multiply-all-outer-v1',
              'multiply-shared-v1', 'multiply-owners-v1', 'multiply-existing-IRQ-v1',
              'multiply-IRQ-v1', 'multiply-actual-hot-v1', 'multiply-ownership-v2']
    for label in labels:
        path = d / label / 'proof.json';proof = json.loads(path.read_text())
        assert proof['passed']
        key = 'ROM_sha256' if label == 'multiply-shared-v1' else 'candidate_ROM_sha256'
        assert proof[key] == digest
        proofs[label] = dict(path=str(path), sha256=sha(path))
    domain = json.loads((d / 'multiply-domain-v1/proof.json').read_text())
    songs = json.loads((d / 'multiply-songs-v2/proof.json').read_text())
    outer = json.loads((d / 'multiply-all-outer-v1/proof.json').read_text())
    assert domain['cases'] == 1572864
    assert songs['original_calls'] == 192016 and songs['original_ordered_APU_requests'] == 549602
    assert songs['checked_writer_returns'] == 1099204 and songs['every_call_CPU_no_worse']
    assert outer['identities'] == 37 and outer['total_calls'] == 12256
    out.mkdir(parents=True, exist_ok=False)
    source = out / 'source'
    shutil.copytree(candidate / 'source', source, ignore=shutil.ignore_patterns('__pycache__'))
    paths = {path.relative_to(source).as_posix(): path for path in source.rglob('*') if path.is_file()}
    assert len(paths) == 657
    manifest = {name: dict(before_sha256=sha(donor / 'source' / name) if (donor / 'source' / name).exists() else None,
                           after_sha256=sha(path)) for name, path in sorted(paths.items())
                if not (donor / 'source' / name).exists() or sha(donor / 'source' / name) != sha(path)}
    assert set(manifest) == {'src/tmnt-native.inc', 'src/tmnt_audio.s', 'src/tmnt_audio_multiply.s'}
    full = {name: dict(before_sha256=frozen['source_files'].get(name), after_sha256=sha(path))
            for name, path in sorted(paths.items()) if sha(path) != frozen['source_files'].get(name)}
    assert len(full) == 15
    for name, value in [('changed-source-versus-a983.json', manifest), ('changed-source-versus-50b5.json', full)]:
        (out / name).write_text(json.dumps(value, indent=2) + '\n')
    patch = ''
    for name in manifest:
        before = (donor / 'source' / name).read_text() if (donor / 'source' / name).exists() else ''
        patch += ''.join(difflib.unified_diff(before.splitlines(True), paths[name].read_text().splitlines(True), fromfile='a/' + name, tofile='b/' + name))
    (out / 'review-versus-a983.patch').write_text(patch)
    for suffix in ['.nes', '.dbg', '.lbl', '.map', '.build.json', '.cv3-mirror.json']:
        shutil.copyfile(candidate / ('candidate' + suffix), out / ('candidate' + suffix))
    for name, flag, expected in [('roundtrip', None, digest),
                                ('flagoff-mmc3', 'mmc3', 'd444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb'),
                                ('flagoff-mmc5', 'mmc5', 'f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833')]:
        command = [sys.executable, '-B', str(source / 'tools/build_mmc5_expanded.py'), '--workspace', str(source),
                   '--compiler', str(ROOT / 'tools/Windows/cc65/bin/cl65.exe'), '--output', str(out / (name + '.nes'))]
        if flag: command += ['--flag-off', flag]
        run = subprocess.run(command, cwd=source, capture_output=True, text=True)
        (out / (name + '-build.log')).write_text(run.stdout + run.stderr)
        assert run.returncode == 0 and sha(out / (name + '.nes')) == expected
    with zipfile.ZipFile(out / 'source.zip', 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(paths): archive.write(paths[name], name)
    tools = {}; (out / 'tools').mkdir()
    for path in sorted((ROOT / 'tools/audit').glob('tmnt_native_storage_multiply*.py')):
        shutil.copyfile(path, out / 'tools' / path.name);tools[path.name] = sha(path)
    baseline_total = sum(row['parent_cycles'] for row in songs['songs'])
    candidate_total = sum(row['candidate_cycles'] for row in songs['songs'])
    peak_old = max(row['parent_peak'] for row in songs['songs']);peak_new = max(row['candidate_peak'] for row in songs['songs'])
    report = f'''TMNT ACBD multiply: PRIVATE SOURCE/CPU-QUALIFIED, NOT NATIVE-QUALIFIED
2026-10-25. No native grant or launch. No production/Git/Downloads change.

Accepted production parent {CURRENT}
Donor a9838664f94d29d87fbf4742e31d4e20d8b3a96862beabd11224afa4742d9003
New candidate {digest}
Ready source/manifest/review/proofs: {out}

CHANGE AND SPACE
Measured ACBD repeated multiply now tail-jumps to real78-byte TnFastProduct
A125..A172, inside linker-declared unused219-byte writer tail A125..A1FF.
Zero/one use dedicated software paths; nibble2..15 uses MMC5 unsigned product.
Original ACBD four-byte entry span is JMP/NOP; all genuine incoming roots enter
ACBD, none enter displaced ACBF. Original ACD9 shift/return tail stays exact.
Only79 PRGbytes in bank63 change versusa983; every existing qualified symbol,
all other PRG/CHR/header, DPCM, data variants, RAM and shared125 remain exact.
Independently enumerated three changed/new source files versusa983, fifteen
versus original50b5. Full657-file source archive and fresh canonical compile
reproduce the exact new hash. Both ordinary flag-off targets remain byte-exact.

EXCLUSIVE HARDWARE OWNERSHIP
Current genuine compiled prior users are BOTH Mm3::_fraction255_mmc5 and
ProtoMm3::_fraction255_mmc5, not a misleading single-copy claim. Debug source
binds generated MM3 and Proto kernel; audio/megaman3/imported.s is an inactive
reference artifact. Both actual drivers select character1 paths inside
AudioUpdate; TMNT uses character19. Both real AudioUpdate callers are inside
the fixed NMI. Existing and new helpers write both operands before either
product read; zero branches do not read stale products. Caller tails do not
retain pending product reads across returns. Reads return product, so operands
are deliberately NOT supposedly restored by reading them back. Actual inline
68-byte IRQ has no math access;1428 injection cases preserve intermediate
operands, CPU, source RAM/SMC and banks at every helper/tail instruction.
Ownership follows the existing single-depth NMI audio contract. Unsupported
nested-NMI reentry is not newly advertised as safe or used as a fake test pass.
Reference product semantics: https://github.com/SourMesen/Mesen2/blob/master/Core/NES/Mappers/Nintendo/MMC5.h

COMPLETE SOURCE AND CPU CONTRACT
1,572,864 actual linked component cases cover nibble0..15, all256 coefficients,
all64 meaningfulP states, every legal channelX0..5. UpperA bits are discarded
by the identical AND15. A/X/Y/P/SP, original E2=FF/E4=productLow/E5=product>>4
and all ordinary writes match. Preserve original final-ADC V, or incoming V
when nibble0; D/I unchanged; C0 and N/Z exact. Hardware accesses are exclusively
W5205/W5206/R5205/R5206 inside the new helper. Zero/one access no math registers.
EVERY input costs less: zero saves27, one32, nibble2 saves5..12; all larger
operands save more. No fast-path regression is hidden by a favorable average.

Fresh all16 original songs:192016 calls/549602 ordered original APUs/1099204
writer AXYP/SP returns exact. Full188-byte state with only proven ROM-pointer
translation, foregroundRAM/ZP/SMC/PRG banks guarded. Each new product access
has exact helper-PC/operand-order/product checks. Every call <= donor cost.
All song totals improve: aggregate {baseline_total} -> {candidate_total} CPUcycles.
Linked source peak {peak_old} -> {peak_new}; song2 peak5695 ->5685.
No rates, channels, music stores, samples, songs or source data are removed.

Fresh33-identity outer6480/shared6264/owners6040 checks pass on both comparands
with accurate product-read memory, not an operand-return placeholder. Newall37
suite12256 calls adds allfour turtles and4816 consecutive complete AudioUpdate
calls; full ordinary/sourceRAM/SMC/APU/banks/AXYP/SP exact. Only the TWO newly
owned hardware registers5205/5206 sit outside ordinaryRAM comparison; every
foreign identity retains exact math operands/stream and zero cycle change.
Existing IRQ suite424 plus multiply-specific1428 actual vector/IRQ/RTI cases
pass. CPU models do not pretend to simulate DMC DMA or PPU/NMI clocks.

ACTUAL HOT-STATE BINDING AND COST LIMITS
The real frozen native188-byte input/output streams at407/505 match both new
and donor CPU calls. Isolated component407:3834 ->3472 (-362);505:5679 ->5669
(-10). These CPU fixtures have their disclosed software DMC state, so absolute
times are not relabeled as measured native3793/5641. Complete warm AudioUpdate
also saves362/10 at the corresponding source moments; cold peak9166 remains
unchanged. No claim that this recovers the observed eight native lost draws.

RETAINED NEGATIVES/OPEN WORK
First songs invocation chose ready archive lacking preparation.json; no source
fixture ran; corrected invocation uses exact originala983 donor path. Initial
static IRQ audit mistook immediate byte20 for JSR; corrected checker decodes
real instruction boundaries. Both negatives remain without game/assertion
relaxation. Frozen a983/8e2/native-negative/hotlead/Parodius packets remain exact.
Native matched Easy performance previously LOST8 draws and is still open.
This new candidate has NO native timing/DMA/PPU/NMI/preemption/pause/Hard result.
Root must review and grant fresh bounded native qualification before adoption.
'''
    (out / 'report.txt').write_text(report, encoding='utf-8')
    receipt = dict(frozen=True, accepted=False, native_run=False, source_CPU_qualified_only=True,
                   accepted_production_parent_sha256=CURRENT, donor_a983_sha256=sha(donor / 'candidate.nes'), candidate_ROM_sha256=digest,
                   changed_PRG_bytes={63: 79}, source_files=len(paths), changed_source_versus_donor=manifest,
                   existing_symbols_RAM_CHR_other_banks_DPCM_exact=True,
                   original_source_calls=192016, original_ordered_APU_requests=549602, checked_writer_returns=1099204,
                   domain_cases=1572864, every_component_and_song_call_no_worse=True,
                   exclusive_under_existing_single_depth_NMI_audio_contract=True, no_fake_operand_restore=True,
                   source_peak_before=peak_old, source_peak_after=peak_new, source_total_before=baseline_total, source_total_after=candidate_total,
                   canonical_roundtrip_exact=True, ordinary_flagoff_exact=True, proofs=proofs, tools=tools,
                   report_sha256=sha(out / 'report.txt'), source_zip_sha256=sha(out / 'source.zip'), review_patch_sha256=sha(out / 'review-versus-a983.patch'),
                   retained_a983_eight_native_draw_deficit_not_closed=True, production_inputs_650_unchanged=True)
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    assert all(sha(ROOT / name) == value for name, value in frozen['source_files'].items())
    print(json.dumps(dict(frozen=True, candidate=digest, receipt_sha256=sha(out / 'receipt.json'), source_total_saved=baseline_total-candidate_total)))


if __name__ == '__main__':
    main()
