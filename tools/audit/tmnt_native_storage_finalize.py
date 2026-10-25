"""Freeze the current50b5 native-TMNT storage experiment, without deployment.

The report distinguishes authenticated executable/source CPU checks from the
still-required native DMA, vblank and matched gameplay-cadence qualification.
"""
from pathlib import Path
import argparse
import difflib
import gzip
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile
from check_tmnt_render_oa import load, address
from check_tmnt_audio_fallback_oc import qualified
from tmnt_native_storage_driver import ROOT, CURRENT, OB, MOVED, source_data, sha


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--experiment', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--report', type=Path, required=True)
    a = p.parse_args()
    assert not a.output.resolve().is_relative_to(ROOT)
    assert a.report.resolve() == ROOT / 'docs/qa/tmnt-native-storage-2026-10-25.txt'
    assert not a.output.exists() and not a.report.exists()
    d, out = a.experiment, a.output
    base, candidate, control = d / 'current-baseline-v1', d / 'current-swap-v2', d / 'current-duration-v2'
    frozen = json.loads((base / 'frozen-source.json').read_text())
    assert sha(base / 'baseline.nes') == CURRENT
    assert sha(ROOT / 'build/smb-crossover-mmc5-expanded.nes') == CURRENT
    assert all(sha(ROOT / name) == h for name, h in frozen['source_files'].items())
    assert sha(candidate / 'candidate.nes') == '8e2fa5de95edc5be33bbb20fa9262c2f58e3ebfcb793d82a740275a16409b790'
    assert sha(control / 'candidate.nes') == '6d234b99f5494e1973c075cf39f2a74853bc6707c677b5afa9b6a5a0e8394d5c'
    out.mkdir(parents=True)
    old, new = (base / 'baseline.nes').read_bytes(), (candidate / 'candidate.nes').read_bytes()
    bank = lambda raw, n: raw[16 + n * 8192:16 + (n + 1) * 8192]
    assert old[:16] == new[:16] and old[1048592:] == new[1048592:]
    deltas = {n: sum(x != y for x, y in zip(bank(old, n), bank(new, n))) for n in range(128)}
    deltas = {n: v for n, v in deltas.items() if v}
    assert deltas == {38: 2, 63: 7493, 99: 7862, 125: 1721, 127: 710}
    assert all(bank(old, n) == bank(new, n) for n in [115, 123, 124, 126])
    assert bank(old, 99)[:138] == bank(new, 99)[:138]

    b, c = load(base / 'baseline.nes'), load(candidate / 'candidate.nes')
    qb, qc = qualified(base / 'baseline.nes'), qualified(candidate / 'candidate.nes')
    private = {}
    for key, value in qb.items():
        if qc.get(key) == value:
            continue
        assert len(key) == 2 and key[0] == 'SamusAudioUpdate' and key not in qc
        replacement = ('SamusAudioCold', key[1])
        assert qc[replacement] == value - 0x1174
        private['::'.join(key)] = dict(old_PC=value, new_real_label='::'.join(replacement), new_PC=qc[replacement])
    assert len(private) == 10
    for name in ['SamusAudioUpdate', 'SamusAudioInit', 'AudioUpdate', 'AudioInit',
                 'Cv3DmcOwnerWrite', 'Cv3DmcManagerStart', 'Cv3DmcManagerEnd', 'LmNativeMusicGate']:
        assert address(b, name) == address(c, name)
    original_samus = (base / 'source/src/samus_audio.s').read_text()
    begin = original_samus.index('.proc SamusAudioUpdate\n')
    finish = original_samus.index('.endproc\n', begin) + len('.endproc\n')
    body = original_samus[begin:finish].replace('.proc SamusAudioUpdate', '.proc SamusAudioCold')
    ret = '  jsr CrossoverGraphicsBank\n  pla\n  BankPRGA a\n  rts\n'
    assert body.count(ret) == 1
    body = body.replace(ret, '  jmp SamusAudioFixedReturn\n')
    assert (candidate / 'source/src/tmnt_audio_samus_cold.s').read_text() == '.pushseg\n.segment "TMNT_SAMUS_AUDIO_COLD"\n' + body + '.export SamusAudioCold\n.popseg\n'

    q, memory, cpu, disasm, instructions, words = source_data()
    def normal(at):
        return at + 0x2000 if at < 0xc000 else at - 0x2000
    def move(at):
        return MOVED[2] + at - MOVED[0] if MOVED[0] <= at < MOVED[1] else normal(at)
    def actual(at, size=1):
        native = move(at)
        raw = bank(new, 63 if native < 0xc000 else 99)
        offset = native - (0xa000 if native < 0xc000 else 0xc000)
        return raw[offset:offset + size]
    for word in sorted(words):
        target = memory[word] + 256 * memory[word + 1]
        assert actual(word, 2) == move(target).to_bytes(2, 'little')
    moved = bytearray(memory[MOVED[0]:MOVED[1]])
    for word in sorted(words):
        if MOVED[0] <= word < MOVED[1]:
            moved[word - MOVED[0]:word - MOVED[0] + 2] = move(memory[word] + 256 * memory[word + 1]).to_bytes(2, 'little')
    assert bank(new, 63)[0x429:0x59a] == moved
    indirect = []
    for pc in sorted(instructions):
        width, _ = disasm.instruction_at(pc)
        op, mode = cpu.disassemble[memory[pc]]
        if mode == 'ind' and 0xe0 <= memory[pc + 1] + 256 * memory[pc + 2] <= 0xed:
            at = memory[pc + 1] + 256 * memory[pc + 2]
            native = normal(pc)
            offset = native - (0xa000 if native < 0xc000 else 0xc000)
            raw = bank(new, 63 if native < 0xc000 else 99)[offset:offset + width]
            assert raw == bytes([memory[pc]]) + (address(c, 'TnAudioZp') + at - 0xe0).to_bytes(2, 'little')
            indirect.append(dict(original_PC=pc, native_PC=native, original_ZP=at, actual_operand=address(c, 'TnAudioZp') + at - 0xe0))
    assert [row['native_PC'] for row in indirect] == [0xa6e0, 0xa94e, 0xad8f, 0xaf34]

    mirror = json.loads((candidate / 'candidate.cv3-mirror.json').read_text())
    assert mirror['all_other_fixed_bytes_exact']
    assert sorted(mirror['declared_overlay_offsets']) == [[0x1140, 0x1581], [0x15c0, 0x1681], [0x1700, 0x1af7], [0x1af7, 0x1b8a]]
    for lo, hi in [(0x1140, 0x1581), (0x15c0, 0x1681)]:
        assert bank(old, 125)[lo:hi] == bank(new, 125)[lo:hi]
    assert bank(new, 125)[:0x1140] == bank(new, 127)[:0x1140]
    manager_changes = [i for i in range(0x1af7, 0x1b8a) if bank(old, 125)[i] != bank(new, 125)[i]]
    assert len(manager_changes) == 3 and manager_changes == list(range(manager_changes[0], manager_changes[0] + 3))
    at = manager_changes[0]
    assert bank(old, 125)[at] == 0x8d and bank(new, 125)[at] == 0x20
    assert int.from_bytes(bank(new, 125)[at + 1:at + 3], 'little') == address(c, 'TnDmcOwnerAdmission')
    sample = (candidate / 'source/audio/tmnt/native-drum.dmc').read_bytes()
    assert len(sample) == 129 and digest(sample) == '225add377a86b0499c2c902cf9ba410c2edcdfec7e0d530f2dc719b58f886dfe'
    assert sample == bytes(memory[0xc040:0xc0c1])
    assert bank(new, 125)[0x8c0:0x941] == bank(new, 127)[0x8c0:0x941] == sample
    final_dac = {}
    for initial in range(128):
        dac = initial
        for value in sample:
            for bit in range(8):
                if value & (1 << bit):
                    if dac <= 125: dac += 2
                elif dac >= 2:
                    dac -= 2
        final_dac[initial] = dac
    assert all(final_dac[initial] == 44 for initial in range(0, 128, 2))
    source_dac = set()
    for song in range(1, 17):
        rows = json.loads(gzip.decompress((OB / f'probe-v2/song-{song:02d}.json.gz').read_bytes()))
        for row in rows['calls'] if isinstance(rows, dict) else rows:
            source_dac.update(value for at, value in row['writes'] if at == 0x4011)
    assert source_dac == {0}

    proof_names = ['standalone-full-v1', 'current-linked-full-v2', 'current-shared-CPU-v2',
                   'current-owners-CPU-v3', 'current-outer-CPU-v2', 'current-IRQ-CPU-v2']
    proofs = {}
    for name in proof_names:
        path = d / name / 'proof.json'
        proof = json.loads(path.read_text())
        assert proof['passed']
        if name.startswith('current-'):
            key = {'current-linked-full-v2': 'swapped_ROM_sha256',
                   'current-shared-CPU-v2': 'ROM_sha256'}.get(name, 'candidate_ROM_sha256')
            assert proof[key] == sha(candidate / 'candidate.nes')
        proofs[name] = dict(path=str(path), sha256=sha(path))
    for suffix, expected in [('mmc3', 'd444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb'),
                             ('mmc5', 'f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833')]:
        assert sha(candidate / f'flagoff-{suffix}.nes') == expected

    # Enumerate independently; generated Python bytecode is not deployable input.
    paths = {p.relative_to(candidate / 'source').as_posix(): p for p in (candidate / 'source').rglob('*')
             if p.is_file() and '__pycache__' not in p.parts}
    assert set(frozen['source_files']).issubset(paths)
    manifest = {name: dict(before_sha256=frozen['source_files'].get(name), after_sha256=sha(path))
                for name, path in sorted(paths.items()) if sha(path) != frozen['source_files'].get(name)}
    assert len(manifest) == 14
    shutil.copytree(candidate / 'source', out / 'source', ignore=shutil.ignore_patterns('__pycache__'))
    patch = ''
    for name in manifest:
        if name.endswith('.dmc'):
            continue
        old_text = (base / 'source' / name).read_text() if name in frozen['source_files'] else ''
        patch += ''.join(difflib.unified_diff(old_text.splitlines(True), (out / 'source' / name).read_text().splitlines(True),
                                           fromfile='a/' + name, tofile='b/' + name))
    (out / 'review.patch').write_text(patch)
    (out / 'changed-source.json').write_text(json.dumps(manifest, indent=2) + '\n')
    for suffix in ['.nes', '.dbg', '.lbl', '.map', '.build.json', '.cv3-mirror.json']:
        shutil.copyfile(candidate / ('candidate' + suffix), out / ('candidate' + suffix))
    tools = {}
    (out / 'tools').mkdir()
    for tool in sorted((ROOT / 'tools/audit').glob('tmnt_native_storage_*.py')):
        shutil.copyfile(tool, out / 'tools' / tool.name)
        tools[tool.name] = sha(tool)
    cmd = [sys.executable, '-B', str(out / 'source/tools/build_mmc5_expanded.py'), '--workspace', str(out / 'source'),
           '--compiler', str(ROOT / 'tools/Windows/cc65/bin/cl65.exe'), '--output', str(out / 'roundtrip.nes')]
    r = subprocess.run(cmd, cwd=out / 'source', capture_output=True, text=True)
    (out / 'roundtrip-build.log').write_text(r.stdout + r.stderr)
    assert r.returncode == 0, (r.stdout + r.stderr)[-3000:]
    assert sha(out / 'roundtrip.nes') == sha(out / 'candidate.nes')
    assert all(sha(out / 'source' / name) == sha(path) for name, path in paths.items())
    with zipfile.ZipFile(out / 'source.zip', 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for name in sorted(paths):
            z.write(out / 'source' / name, name)

    receipt = dict(passed=True, accepted=False, private_source_CPU_experiment=True, native_run=False,
                   production_writes=False, parent_ROM_sha256=CURRENT, candidate_ROM_sha256=sha(out / 'candidate.nes'),
                   control_B124_ROM_sha256=sha(control / 'candidate.nes'), frozen_ROOT_inputs=len(frozen['source_files']),
                   canonical_source_roundtrip_exact=True, changed_source_files=manifest, changed_PRG_bytes=deltas,
                   original_public_symbols_retained=len(qb) - 10, authorized_genuine_private_label_relocations=private,
                   moved_connected_original_interval=[0x9f29, 0xa09a], native_destination=[0xa429, 0xa59a],
                   complete_moved_bytes=369, closed_original_instructions=len(instructions), rewritten_original_pointer_words=len(words),
                   full_original_songs=16, original_calls=192016, original_ordered_requests=549602,
                   pointer_high_translation_only_actual_ROM_word_origins=[0x742a, 0x7436, 0x7442],
                   page_aligned_relocation_cycles_equal_B124_control=True,
                   original_ZP_indirect_instruction_regression_guards=indirect,
                   bank99_original_UI_prefix_bytes_exact=138, bank124_115_123_126_CHR_header_exact=True,
                   CV3_owner=3, TMNT_owner=4, CV3_samples_byte_exact=True,
                   CV3_manager_only_changed_instruction_offset=at, TMNT_original_sample_sha256=digest(sample),
                   sample_software_even_initial_DAC_final=44, original_source_4011_values=sorted(source_dac),
                   software_DAC_oracle_not_physical_DMA=True, proofs=proofs, owned_tools=tools,
                   review_patch_sha256=sha(out / 'review.patch'), source_zip_sha256=sha(out / 'source.zip'),
                   held_native_cadence_failure_remains_open=True,
                   limits='Source/assembled-CPU only. No native hardware DMC clock/4015 completion/tail/preemption, physical IRQ/NMI/vblank/OAM/CHR capture, current gameplay or matched completed-update/draw cadence. Extra non-TMNT costs remain explicit and need optimization/native qualification. Does not install TMNT or Parodius music.')
    report = f'''TMNT native audio: current50b5 private storage/source experiment
2026-10-25. Not installed; no native emulator run or release acceptance.

Parent MMC5: {CURRENT}
Private B99 candidate: {receipt['candidate_ROM_sha256']}
Matched B124 control: {receipt['control_B124_ROM_sha256']}
Ready packet: {out}

RESULT
The authentic TMNT driver and all sixteen original songs now assemble privately
on current50b5. Original A code keeps its PCs in bank63. Complete connected source
9F29..A099 (369 bytes, including its crossing loop) moves to A429..A599 without
changing low bytes. Bank99 preserves its real 138-byte UI prefix and stores the
remaining original B data at C08A..DFFF. All 369 connected pointer words are
rewritten. No song, channel, sample, music update, reachable data or SFX is cut.
Bank124 stays byte-identical to parent; this is an enabling storage result, not
approval to consume it. Mac123/Mike115/LOW126, CHR and header are byte-exact.
Changed bank bytes: {deltas}.

REPRODUCTION AND SOURCE
All 650 frozen production inputs still match. The ready packet independently
enumerates all fourteen deployable changed/new files (changed-source.json),
preserves original line endings in source.zip, includes a review patch, and was
freshly rebuilt from that source to the exact candidate hash. Ordinary flag-off
MMC3 d444cac8... and MMC5 f4ffd248... rebuild byte-exact without overflow.
Original NSF SHA256 f220e8d069e321f392526d41e46f5d0f72966d5a22e56d2b269607c678bd58d9.
The original executable, goldens, standalone source and real current linked
writers are bound by the referenced proof hashes in receipt.json.

CPU EVIDENCE
* 192,016 authentic init/play calls and 549,602 ordered original APU requests,
  all sixteen songs at 12,000 updates each. Full original 174-byte RAM and 14-byte
  ZP, public A/X/Y/P/SP exact. B99 pointer-high state translation applies only to
  actual proven ROM-word origins at 742A/7436/7442; no broad RAM masking.
* 24,428 distinct linear/indexed access spans commute with relocation; all369
  actual indirect roots are known complete pointer words, including 9014.
* Actual linked B124 and B99 builds repeat all calls with 1,099,204 source-STA
  writer A/X/Y/P/SP return checks; foreground/ZP/SMC, final banks, PPU/CHR writes
  are guarded. B99 adds exactly zero cycles versus the same linked B124 control.
* Current duration lookup retains original final ADC/DEC flags and all original
  writes. Historical source timing is not native proof: normal601 peak6031 to
  5827; some songs have higher totals. Current linked source-core/writer peak
  reaches7122. No claim that enabling authentic music adds no gameplay lag.
* Fresh existing shared test: 6,264 cases; full outer audio: 6,480 calls across
  all33 unchanged identities, Easy/Hard numeric0/1 and ten caller flag states.
  Whole A/X/Y/P/SP, ordinary RAM/SMC, final banks and ordered APU outcomes exact.
  Discarded CPU stack01A0..01FF is excluded from outer comparisons. Linked
  source allows stack only01D0..01FF, guarding lower SMC. Cold-context cost is
  higher: Mario+29; Samus+83..124; expanded+95..135; foreign direct expanded+26.
* 6,040 DMC ownership/tail/preemption CPU cases preserve existing owners0..3,
  CV3 owner3/sample priority/mirror, assign TMNT4, and guard newer owner claims
  against delayed tail clears. Actual compiled CV3Start uses the common owner
  admission without erasing its freshly set priority. Hardware status/DAC are
  arranged inputs here, not real DMA observations.
* 405 injections execute the real IRQ vector8000, handler and RTI at new gate,
  bank bridge and writer instruction boundaries. Interrupted/final CPU/RAM/SMC,
  PRG banks and source APU exact; isolated maximum total stack depth23 bytes.
  No physical scanline, DMA-stall, nested-NMI or vblank/OAM claim.

FIXED E / SHARED125 CONTRACT
Public SamusAudioUpdate E874 remains fixed and reaches real Cold D700. Its
current body is text-identical except for a fixed-E return bridge. Ten genuinely
private SamusAudioUpdate local labels move to genuine SamusAudioCold locals by
-1174; none remain as false callable aliases. All other60684 qualified symbols
retain addresses; exact exceptions are listed in receipt.json. Existing calls,
all eight512 Samus streams, owner cases, full outer flags and IRQ are checked.
Original TMNT129-byte sample is exact at fixed E8C0..E940 and cloned125. Existing
CV3 primary1140..1580/Sypha15C0..1680 samples are exact. Current mirror producer
declares cold1700..1AF6 and manager1AF7..1B89; manager changes only one real3-byte
STA to JSR TnDmcOwnerAdmission. Other copied fixed bytes retain mirror semantics.
Software decode of authentic sample from every even DAC0..126 ends at44; original
source4011 writes are only0. This binds the softwarehold44 value; physical sample
completion/tail timing remains unproved.

NEGATIVE RESULTS RETAINED
standalone-pilot-v1 first provenance checker incorrectly used a scalar command
as a pointer origin. Corrected to actual complete ROM words; no relaxed source
assertions. current-linked-pilot-v1 then caught a real converter bug: original
JMP($00E2) at A94E had not moved with owned ZP E0..ED to DE..EB, causing BRK and a
bad bank write. Failed gamev1 ROMs/proofs remain intact. Generatorv2 fixes the
three-byte indirect operand and adds a static guard. Standalone v1 and v2 raw
binaries are exact because their standalone ZP remains E0; full original proof
is not relabeled as a current-game proof. Existing historical held-v7 native
combat draw deficit is not erased or closed by these CPU results.

OPEN BEFORE ADOPTION
Optimize added dispatcher/global/owner overhead; qualify real native original
track schedule and merged hardware4015, physical DMC completion/tail/preemption,
pause/events, actual NMI/IRQ/bank/stack/SMC/OAM/CHR, and matched completed updates
and draws on the eventual exact current composition. Root has granted no native
worker for this experiment. Parodius source checkpoint remains frozen and its
music remains unfinished. No ROOT production/Git/Downloads changes were made.
'''
    a.report.write_text(report)
    shutil.copyfile(a.report, out / a.report.name)
    receipt['report_sha256'] = sha(a.report)
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    assert all(sha(ROOT / name) == h for name, h in frozen['source_files'].items())
    print(json.dumps(dict(passed=True, receipt_sha256=sha(out / 'receipt.json'), report_sha256=sha(a.report),
                          changed_files=len(manifest), candidate=receipt['candidate_ROM_sha256'])))


if __name__ == '__main__':
    main()
