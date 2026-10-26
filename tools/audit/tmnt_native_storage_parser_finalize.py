"""Freeze a separate source/CPU-only parser candidate, retaining all negatives."""
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
from tmnt_native_storage_parser import PARENT, RECEIPT


DIGEST = '9a791d0e13015ff362ffc9e460aaac8c8a0a5b6f73e990959dee4e074da473fd'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--experiment', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    d, out = a.experiment, a.output
    assert not out.resolve().is_relative_to(ROOT)
    donor, candidate = d / 'multiply-ready-v1', d / 'parser-current-2f61-v3'
    assert sha(donor / 'receipt.json') == RECEIPT
    assert sha(donor / 'candidate.nes') == PARENT and sha(candidate / 'candidate.nes') == DIGEST
    frozen = json.loads((d / 'current-baseline-v1/frozen-source.json').read_text())
    assert sha(ROOT / 'build/smb-crossover-mmc5-expanded.nes') == CURRENT
    assert all(sha(ROOT / name) == value for name, value in frozen['source_files'].items())
    old, new = (donor / 'candidate.nes').read_bytes(), (candidate / 'candidate.nes').read_bytes()
    banks = lambda raw, n: raw[16 + n * 8192:16 + (n + 1) * 8192]
    changed = {n: [i for i in range(8192) if banks(old, n)[i] != banks(new, n)[i]] for n in range(128)}
    changed = {n: positions for n, positions in changed.items() if positions}
    assert set(changed) == {63} and len(changed[63]) == 36
    allowed = set(range(0x180, 0x1b2)) | {0x6a6} | set(range(0x937, 0x951)) | set(range(0xad4, 0xad7))
    assert set(changed[63]) <= allowed
    assert old[:16] == new[:16] and old[1048592:] == new[1048592:]
    assert banks(old, 63)[0x125:0x173] == banks(new, 63)[0x125:0x173]
    assert qualified(donor / 'candidate.nes').items() <= qualified(candidate / 'candidate.nes').items()
    names = ['parser-domains-v2', 'parser-songs-v2', 'parser-all-outer-v2', 'parser-shared-v1',
             'parser-owners-v1', 'parser-existing-IRQ-v1', 'parser-multiply-IRQ-v1', 'parser-IRQ-v1', 'parser-actual-hot-v2']
    proofs = {}
    for label in names:
        path = d / label / 'proof.json';j = json.loads(path.read_text())
        assert j['passed'] and j['ROM_sha256' if label == 'parser-shared-v1' else 'candidate_ROM_sha256'] == DIGEST
        proofs[label] = dict(path=str(path), sha256=sha(path))
    domains = json.loads((d / 'parser-domains-v2/proof.json').read_text())
    songs = json.loads((d / 'parser-songs-v2/proof.json').read_text())
    outer = json.loads((d / 'parser-all-outer-v2/proof.json').read_text())
    hot = json.loads((d / 'parser-actual-hot-v2/proof.json').read_text())
    assert domains['cases'] == 771776
    assert songs['original_calls'] == 192016 and songs['original_ordered_APU_requests'] == 549602
    assert songs['checked_writer_returns'] == 1099204 and songs['every_call_CPU_no_worse']
    assert outer['identities'] == 37 and outer['total_calls'] == 12256
    assert [row['saved_CPUcycles'] for row in hot['rows']] == [36, 72]
    out.mkdir(parents=True, exist_ok=False)
    source = out / 'source'
    shutil.copytree(candidate / 'source', source, ignore=shutil.ignore_patterns('__pycache__'))
    paths = {path.relative_to(source).as_posix(): path for path in source.rglob('*') if path.is_file()}
    assert len(paths) == 658
    manifest = {name: dict(before_sha256=sha(donor / 'source' / name) if (donor / 'source' / name).exists() else None, after_sha256=sha(path))
                for name, path in sorted(paths.items()) if not (donor / 'source' / name).exists() or sha(donor / 'source' / name) != sha(path)}
    assert set(manifest) == {'src/tmnt-native.inc', 'src/tmnt_audio.s', 'src/tmnt_audio_parser.s'}
    full = {name: dict(before_sha256=frozen['source_files'].get(name), after_sha256=sha(path))
            for name, path in sorted(paths.items()) if sha(path) != frozen['source_files'].get(name)}
    assert len(full) == 16
    for name, value in [('changed-source-versus-2f61.json', manifest), ('changed-source-versus-50b5.json', full)]:
        (out / name).write_text(json.dumps(value, indent=2) + '\n')
    patch = ''
    for name in manifest:
        prior = donor / 'source' / name
        patch += ''.join(difflib.unified_diff(prior.read_text().splitlines(True) if prior.exists() else [], paths[name].read_text().splitlines(True), fromfile='a/' + name, tofile='b/' + name))
    (out / 'review-versus-2f61.patch').write_text(patch)
    for suffix in ['.nes', '.dbg', '.lbl', '.map', '.build.json', '.cv3-mirror.json']:
        shutil.copyfile(candidate / ('candidate' + suffix), out / ('candidate' + suffix))
    for name in ['preparation.json', 'parser-preparation.json']: shutil.copyfile(candidate / name, out / name)
    for name, flag, expected in [('roundtrip', None, DIGEST), ('flagoff-mmc3', 'mmc3', 'd444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb'),
                                ('flagoff-mmc5', 'mmc5', 'f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833')]:
        command = [sys.executable, '-B', str(source / 'tools/build_mmc5_expanded.py'), '--workspace', str(source),
                   '--compiler', str(ROOT / 'tools/Windows/cc65/bin/cl65.exe'), '--output', str(out / (name + '.nes'))]
        if flag: command += ['--flag-off', flag]
        result = subprocess.run(command, cwd=source, capture_output=True, text=True)
        (out / (name + '-build.log')).write_text(result.stdout + result.stderr)
        assert result.returncode == 0 and sha(out / (name + '.nes')) == expected
    with zipfile.ZipFile(out / 'source.zip', 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(paths): archive.write(paths[name], name)
    tools = {}; (out / 'tools').mkdir()
    for path in sorted((ROOT / 'tools/audit').glob('tmnt_native_storage_parser*.py')):
        shutil.copyfile(path, out / 'tools' / path.name);tools[path.name] = sha(path)
    reused = {name: sha(ROOT / 'tools/audit' / name) for name in ['tmnt_native_storage_multiply.py', 'tmnt_native_storage_multiply_cpu.py',
              'tmnt_native_storage_multiply_outer.py', 'tmnt_native_storage_multiply_compat.py', 'tmnt_native_storage_multiply_irq.py',
              'tmnt_native_storage_driver.py', 'tmnt_native_storage_cpu.py', 'tmnt_native_storage_linked_cpu.py',
              'tmnt_native_storage_owners_cpu.py', 'tmnt_native_storage_irq_cpu.py', 'vehicles_audio_wiring_cpu.py',
              'check_tmnt_render_oa.py', 'check_tmnt_audio_fallback_oc.py', 'verify_native_relocation.py', 'final_item_matrix.py']}
    (out / 'reused-checkers.json').write_text(json.dumps(reused, indent=2) + '\n')
    before, after = sum(row['parent_cycles'] for row in songs['songs']), sum(row['candidate_cycles'] for row in songs['songs'])
    peak_before, peak_after = max(row['parent_peak'] for row in songs['songs']), max(row['candidate_peak'] for row in songs['songs'])
    report = f'''TMNT parser: PRIVATE SOURCE/CPU-QUALIFIED; NO NATIVE QUALIFICATION
2026-10-25. No production, Git or Downloads edits. No Mesen grant or launch.

Accepted production parent {CURRENT}
Immutable multiply donor {PARENT}
Separate parser candidate {DIGEST}

Minimal source and storage
Only36 additional PRG bytes in bank63 differ from multiply2f61. Three source
deltas are src/tmnt-native.inc, src/tmnt_audio.s and new src/tmnt_audio_parser.s.
All retained qualified symbols/RAM/header/CHR, other127banks, shared125,
existing multiplier helper and complete original songs/samples stay exact.
The 50-byte interleaved table A180..A1B1 uses verified linker-declared FF fill.
Only eight table bytes contain data, the literal four original handler words.
Full658-file archive, independently enumerated3/16source deltas versus2f61/
production50b5, review patch and fresh byte-exact canonical build are included.
Ordinary flag-off MMC3/MMC5 builds retain their exact original hashes.

Actual changes and flags
A6A5's taken BCS re-enters A6A1 rather than A6A0: that edge already proves C1,
so skip only the repeated SEC. Every actual SBC and its final flags remain.
AACC's repeated triangle add moves DEX to the back edge. It removes repeated
JMP/BEQ work, retaining literal ADC, first-carry exit X and final-ADC V.
A937's command dispatcher uses an interleaved table indexed by AND30 directly.
It preserves original E2/E3 handler pointers and restores the same X/A/Y/P.
Explicit CLC reproduces the removed LSRs' C0; no incoming-carry assumption.
Original1289-instruction/369-pointer closure has no external entry into the
rewritten instruction interiors. Padding follows the unconditional JMP.
No new RAM or hardware consumer, channel/rate/store/data removal or alias.

Domain/source/interrupt checks
771776 strict component cases pass: triangle all256coefficients x16notes x64P,
remainder every terminating byte operand pair with all D/I combinations and
full64P controls, dispatcher all256A x5stream controls x3channels x64P.
Initial SEC/SBC kills incoming remainder C/N/Z/V; original A>0/divisor0
nontermination is explicitly not advertised as a terminating test domain.
Every tested terminating component costs no more; dispatcher saves4cycles.
Fresh16songs192016calls/549602ordered original APUs/1099204writer returns:
full188byte source state/proven-pointer translation, foregroundRAM/ZP/SMC,
banks and public AXYP/SP match. Every call <=2f61; all16song totals improve.
Total source cycles {before}->{after}, saves{before-after}; peak{peak_before}->{peak_after}.
All37 full outer12256 calls (4816consecutive turtle calls), shared6264 and
owner6040 cases pass; all foreign identities retain exact outcomes and cycles.
Real vector/IRQ/RTI injection3506parser+424existing+1428multiply cases pass.
No physical IRQ/DMA/PPU/OAM or nested-NMI safety claim follows from CPU tests.

Bound actual hot states and limits
Captured a983188byte before/after states at407/505 bind both full source calls.
Isolated CPU407:3472->3436(-36);505:5669->5597(-72). Adapted parser exclusive
1486->1450 and3093->3021; raw original1472/3078 attribution excluded original
STA-to-JSR writer conversion, so those distinct absolute values are retained.
Actual ADC and SBC counts match, preserving original sound operations.
Complete602 warm AudioUpdates per turtle/mode:1830063->1828403(-1660).
Cold peak9166 stays unchanged. These software CPU fixtures do not model actual
DMC DMA cycles. No recovered-draw/60Hz/native-performance claim is made.

Retained negatives
parser-current-2f61-v1 keeps the first assembly failure: relocatable .res
expression was invalid. Numeric13padding now has an explicit A173 assertion.
Draft b424 in parser-current-2f61-v2 failed strict handler carry: originalP02
versus draftP03 at A937 inputP21. checker-v2.py, parser-domains-v1/checker-v1.py,
failure.txt, partial6song progress and complete b424outer/hot results remain.
The CLC correction reran all domains/songs/outer/hot/IRQ from fresh folders;
no comparison was weakened. A983's actual Easy8lost-draw negative and frozen
multiply/hotlead/Parodius packets remain unchanged. New9a791 has no native
result, cannot be adopted on this source-only packet, and requires a fresh
bounded native grant and matched performance/visual/guard qualification.
'''
    (out / 'report.txt').write_text(report)
    receipt = dict(frozen=True, accepted=False, source_CPU_qualified_only=True, native_run=False,
                   production_parent_ROM_sha256=CURRENT, donor_ROM_sha256=PARENT, candidate_ROM_sha256=DIGEST,
                   changed_PRG_bytes={str(n): len(values) for n, values in changed.items()}, source_files=len(paths),
                   changed_source_versus_donor=manifest, existing_symbols_RAM_CHR_other_banks_samples_exact=True,
                   no_new_RAM_hardware_ownership=True, domain_cases=domains['cases'], original_calls=192016,
                   original_ordered_APU=549602, writer_returns=1099204, every_call_CPU_no_worse=True,
                   source_total_before=before, source_total_after=after, source_peak_before=peak_before, source_peak_after=peak_after,
                   actual_hot_CPU_saved=[36, 72], warm602_total_saved=1660, cold_peak_unchanged=9166,
                   canonical_build_exact=True, ordinary_flagoff_exact=True, proofs=proofs, tools=tools,
                   reused_checkers_sha256=sha(out / 'reused-checkers.json'), report_sha256=sha(out / 'report.txt'),
                   source_zip_sha256=sha(out / 'source.zip'), review_patch_sha256=sha(out / 'review-versus-2f61.patch'),
                   a983_eight_native_lost_draws_remain_open=True, production650inputs_unchanged=True)
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    assert all(sha(ROOT / name) == value for name, value in frozen['source_files'].items())
    print(json.dumps(dict(frozen=True, candidate=DIGEST, receipt_sha256=sha(out / 'receipt.json'), saved_source_CPUcycles=before-after)))


if __name__ == '__main__':
    main()
