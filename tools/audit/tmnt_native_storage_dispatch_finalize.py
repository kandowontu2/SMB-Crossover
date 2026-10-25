"""Freeze the separately qualified dispatch optimization after the8e2 packet."""
from pathlib import Path
import argparse
import difflib
import json
import shutil
import subprocess
import sys
import zipfile
from tmnt_native_storage_driver import ROOT, CURRENT, sha
from check_tmnt_audio_fallback_oc import qualified


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--experiment', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    d, out = a.experiment, a.output
    assert not out.resolve().is_relative_to(ROOT)
    base, ready, candidate = d / 'current-baseline-v1', d / 'ready-v1', d / 'current-dispatch-v1'
    parent = json.loads((ready / 'receipt.json').read_text())
    assert sha(ready / 'receipt.json') == 'db0b2c00a82d4459ae8349dd84220a2421c74bd82b2b8263ace1c5aed903b47d'
    assert sha(candidate / 'candidate.nes') == 'a9838664f94d29d87fbf4742e31d4e20d8b3a96862beabd11224afa4742d9003'
    frozen = json.loads((base / 'frozen-source.json').read_text())
    assert sha(ROOT / 'build/smb-crossover-mmc5-expanded.nes') == CURRENT
    assert all(sha(ROOT / name) == digest for name, digest in frozen['source_files'].items())
    out.mkdir(parents=True, exist_ok=False)
    source = out / 'source'
    shutil.copytree(candidate / 'source', source, ignore=shutil.ignore_patterns('__pycache__'))
    files = {p.relative_to(source).as_posix(): p for p in source.rglob('*') if p.is_file()}
    assert len(files) == 656 and set(frozen['source_files']).issubset(files)
    manifest = {name: dict(before_sha256=frozen['source_files'].get(name), after_sha256=sha(path))
                for name, path in sorted(files.items()) if sha(path) != frozen['source_files'].get(name)}
    assert len(manifest) == 14
    assert all(sha(path) == sha(ready / 'source' / name) for name, path in files.items() if name != 'src/tmnt_audio_resident.s')
    old, donor, new = (base / 'baseline.nes').read_bytes(), (ready / 'candidate.nes').read_bytes(), (candidate / 'candidate.nes').read_bytes()
    bank = lambda raw, n: raw[16 + n * 8192:16 + (n + 1) * 8192]
    changed_vs_donor = {n: [i for i in range(8192) if bank(donor, n)[i] != bank(new, n)[i]] for n in range(128)}
    changed_vs_donor = {n: v for n, v in changed_vs_donor.items() if v}
    assert changed_vs_donor == {125: list(range(0x941, 0x961)), 127: list(range(0x941, 0x961))}
    assert qualified(ready / 'candidate.nes') == qualified(candidate / 'candidate.nes')
    deltas = {n: sum(x != y for x, y in zip(bank(old, n), bank(new, n))) for n in range(128)}
    deltas = {n: count for n, count in deltas.items() if count}
    assert old[:16] == new[:16] and old[1048592:] == new[1048592:]
    assert all(bank(old, n) == bank(new, n) for n in [115, 123, 124, 126])
    assert bank(old, 99)[:138] == bank(new, 99)[:138]
    for suffix in ['.nes', '.dbg', '.lbl', '.map', '.build.json', '.cv3-mirror.json']:
        shutil.copyfile(candidate / ('candidate' + suffix), out / ('candidate' + suffix))
    patch = ''
    for name in manifest:
        if name.endswith('.dmc'): continue
        before = (base / 'source' / name).read_text() if name in frozen['source_files'] else ''
        patch += ''.join(difflib.unified_diff(before.splitlines(True), files[name].read_text().splitlines(True),
                                           fromfile='a/' + name, tofile='b/' + name))
    (out / 'review.patch').write_text(patch)
    (out / 'changed-source.json').write_text(json.dumps(manifest, indent=2) + '\n')
    for label, flag, expected in [('roundtrip', None, sha(candidate / 'candidate.nes')),
                                  ('flagoff-mmc3', 'mmc3', 'd444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb'),
                                  ('flagoff-mmc5', 'mmc5', 'f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833')]:
        command = [sys.executable, '-B', str(source / 'tools/build_mmc5_expanded.py'), '--workspace', str(source),
                   '--compiler', str(ROOT / 'tools/Windows/cc65/bin/cl65.exe'), '--output', str(out / (label + '.nes'))]
        if flag: command += ['--flag-off', flag]
        run = subprocess.run(command, cwd=source, capture_output=True, text=True)
        (out / (label + '-build.log')).write_text(run.stdout + run.stderr)
        assert run.returncode == 0 and sha(out / (label + '.nes')) == expected, (label, run.stdout[-1000:], run.stderr[-1000:])
    proofs = {}
    for label, key in [('dispatch-CPU-v1', 'candidate_ROM_sha256'),
                       ('dispatch-outer-CPU-v1', 'candidate_ROM_sha256'),
                       ('dispatch-current-outer-CPU-v1', 'candidate_ROM_sha256'),
                       ('dispatch-cost-CPU-v1', 'candidate_ROM_sha256'),
                       ('dispatch-owners-CPU-v1', 'candidate_ROM_sha256'),
                       ('dispatch-shared-CPU-v1', 'ROM_sha256'),
                       ('dispatch-IRQ-CPU-v1', 'candidate_ROM_sha256'),
                       ('dispatch-linked-full-v2', 'swapped_ROM_sha256')]:
        path = d / label / 'proof.json'
        proof = json.loads(path.read_text())
        assert proof['passed'] and proof[key] == sha(candidate / 'candidate.nes')
        proofs[label] = dict(path=str(path), sha256=sha(path))
    linked = json.loads((d / 'dispatch-linked-full-v2/proof.json').read_text())
    assert linked['original_calls'] == 192016 and linked['ordered_original_source_APU_requests'] == 549602
    assert linked['checked_writer_returns'] == 1099204 and linked['storage_cycles_exactly_duration']
    cost = json.loads((d / 'dispatch-cost-CPU-v1/proof.json').read_text())
    outer = json.loads((d / 'dispatch-current-outer-CPU-v1/proof.json').read_text())
    # Preserve complete per-identity/mode/owner rows, not only a favorable mean.
    summary = dict(cold_outer=outer['rows'], warm_outer=cost['rows'],
                   owner_status=cost['owner_status_rows'], owner_admission=cost['owner_admission_rows'])
    (out / 'costs-versus-current50b5.json').write_text(json.dumps(summary, indent=2) + '\n')
    tools = {}
    (out / 'tools').mkdir()
    for tool in sorted((ROOT / 'tools/audit').glob('tmnt_native_storage_*.py')):
        shutil.copyfile(tool, out / 'tools' / tool.name)
        tools[tool.name] = sha(tool)
    with zipfile.ZipFile(out / 'source.zip', 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(files): archive.write(files[name], name)
    report = f'''TMNT current50b5 storage: separate dispatcher optimization
2026-10-25. PRIVATE SOURCE/CPU ONLY; no native run or installation.

Accepted parent {CURRENT}
Immutable enabling donor {parent['candidate_ROM_sha256']}
New candidate {sha(candidate / 'candidate.nes')}
Source/review/manifest/proofs: {out}

CHANGE
Remove PHP/PHA/PLA/PLP from TnAudioDispatch. Real LmNativeMusicGate begins
LDA SelectedCharacter/CMP15 and real TnAudioUpdate begins LDA0/STA Request/
LDA Character/CMP253; both overwrite A/N/Z/C before any incoming use. V/D/I
are preserved. Unreachable padding keeps every existing and new qualified
label at its genuine entry, including TnAudioLegacy and following helpers.
Only32 bytes at E941..E960 in fixed127 and its125 mirror differ from8e2.
All other files/module bytes remain exact. Fourteen changed/new source files
versus parent are independently enumerated, including both CV3 owner files.

CHECKS ON THIS EXACT NEW CANDIDATE
49,152 real prefix cases: all256 incomingA and all64 meaningfulP combinations
on foreign/Mac/native paths, each saving14 CPU cycles without input-A shortcuts.
6,480 full outer calls/all33 unchanged identities versus8e2 AND separately
versus parent50b5; 2,880 full outer calls across allfour turtles, numeric Easy/
Hard0/1, ten flags, six cold contexts and three incomingA values. Exact output
AXYP/SP, RAM/SMC, banks and ordered APU. Existing ignored discarded-stack scope
remains01A0..01FF; lowerSMC is guarded. Full shared6,264 and DMC owner6,040
controls repeated against parent. Actual IRQ vector/handler/RTI405 helper
injections plus25 dispatcher/downstream injections pass. Neither IRQ suite
claims real PPU/DMA clocks or nested-NMI behavior.

The original linked16-song corpus was freshly rerun, rather than relabeling
the8e2 receipt:192,016 calls/549,602 original ordered requests/1,099,204 writer
AXYP/SP returns, complete sourceRAM/ZP provenance and foreground/SMC/bank guard.
B99 still adds zero cycles over corrected B124 control6d234b99. Native drivers,
all songs/369pointer words/369-byte complete relocated interval/sample and
existing Mac/Mike/CV3 samples remain source-exact under documented relocation.
Fresh roundtrip and ordinary flag-off builds reproduce exact expected hashes.
All650 frozen ROOT production inputs remain unchanged.

REMAINING EXACT COSTS VERSUS PARENT50B5
The dispatcher saves14 where used; foreign direct ExpandedAudioUpdate now+12
(Vic direct remains0). After real CPU music initialization,120 consecutive
updates in each mode/all33 identities produce7,920 exact warm comparisons:
Mario/Luigi/early guests/Vic+29 per update; Samus+43; expanded other thanVic+41.
These warm fixtures observe softwareowner0 only, so do not pretend to cover
naturally active DMC. Initial area cold calls: Mario/Luigi+29; earlyguests/Vic
+69; Samus+83; laterexpanded+81. Full six cold event/pause contexts include
early+69..109, Samus+83..124, laterexpanded+81..121. Exact per-identity/mode
rows are costs-versus-current50b5.json.

760 separate arranged owner controls preserve exact outcomes. GuestDmcStatus:
owner0 or hardware4015bit4 active adds0; completed foreignowner1/2/3 adds59,
or67 if selectedcharacter19. Cv3DmcOwnerWrite old/newowners0..3 adds40. These
are explicit remaining regressions, not waived by dispatch savings. DMCowner4
has new semantics and is not equated to an unsupported oldowner4 state.
Software-status inputs do not prove real DAC/DMA completion or tail timing.
Current source-core+writer music peak still reaches7122; duration lookup has
some historical per-song total regressions despite lowering its worst spike.

LIMITS/NEXT
Not accepted. Historical TMNTv7 native combat draw deficit remains open. Need
native authentic track/APU/mixed4015 schedule, physical DMC/tail/preemption,
pause/events, NMI/IRQ/banks/SMC/stack/OAM/CHR and strict matched completed
updates/draws on eventual exact current composition. Root grants no native
worker here. No source channels/rates/stores or samples were suppressed.
Bank124 remains parent-exact; this enables a storage proposal, not a Parodius
installation or a whole-roster music completion claim. Ready8e2 and Parodius
checkpoints stay immutable; ROOT production/Git/Downloads stay untouched.
'''
    (out / 'report.txt').write_text(report)
    receipt = dict(passed=True, accepted=False, private_source_CPU_only=True, native_run=False,
                   production_changes=False, parent_ROM_sha256=CURRENT,
                   enabling_donor_ROM_sha256=parent['candidate_ROM_sha256'],
                   enabling_receipt_sha256=sha(ready / 'receipt.json'),
                   candidate_ROM_sha256=sha(candidate / 'candidate.nes'),
                   changed_PRG_bytes_vs_50b5=deltas, changed_offsets_vs_8e2=changed_vs_donor,
                   all_qualified_symbols_exact_vs_8e2=True, changed_source_files=manifest,
                   all_650_ROOT_inputs_unchanged=True, canonical_roundtrip_exact=True,
                   ordinary_flagoff_builds_exact=True, proofs=proofs,
                   original_calls_freshly_rerun=linked['original_calls'], original_requests=linked['ordered_original_source_APU_requests'],
                   checked_writer_returns=linked['checked_writer_returns'], original_storage_cycles_equal_control=True,
                   cost_detail_sha256=sha(out / 'costs-versus-current50b5.json'),
                   report_sha256=sha(out / 'report.txt'), source_zip_sha256=sha(out / 'source.zip'),
                   review_patch_sha256=sha(out / 'review.patch'), owned_tools=tools,
                   no_native_cadence_or_physical_DMC_claim=True)
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    assert sha(ready / 'receipt.json') == receipt['enabling_receipt_sha256']
    assert all(sha(ROOT / name) == digest for name, digest in frozen['source_files'].items())
    print(json.dumps(dict(passed=True, candidate=receipt['candidate_ROM_sha256'],
                          receipt_sha256=sha(out / 'receipt.json'), source_files=len(files), changed_files=len(manifest))))


if __name__ == '__main__':
    main()
