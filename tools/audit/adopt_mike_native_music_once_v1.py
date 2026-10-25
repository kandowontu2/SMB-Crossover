"""Install the reviewed, current-parent StarTropics music integration once.

The qualified source delta is four files. All rollback and fresh compilation
outputs are external; this never reloads or controls an existing emulator.
"""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py/mike-native-current5ec-v1')
PARENT = '5ec81c9250c20aee31af0d3b98c241932c72b3147e05702de70e266f3c854893'
FINAL = '9e0e5ed5d4957aac9baa040ea76616ee4a88233312700b78a8c55250c19f42d3'
QUALIFIED = 'c62a4c1e827d0a460f33cfa22fb47d8fd5becdb771be3c22ab351cfc6a9177ff'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ready = D / 'ready-v1'
    out = D / 'adoption-v1'
    assert not out.exists(), 'One-shot adoption already started; inspect retained state.'
    default = ROOT / 'build/smb-crossover-mmc5-expanded.nes'
    installed = Path('C:/Users/kando/Downloads/SMB-Crossover-Current-MMC5.nes')
    assert sha(default) == sha(installed) == sha(D / 'baseline.nes') == PARENT
    assert sha(D / 'candidate.nes') == FINAL
    qualification = ready / 'qualification.json'
    assert sha(qualification) == QUALIFIED
    q = json.loads(qualification.read_text())
    assert q['passed'] and q['parent_ROM_sha256'] == PARENT and q['candidate_ROM_sha256'] == FINAL
    assert q['coverage'] == dict(CPU_original_calls=198011,
                                CPU_original_ordered_APU_stores=961696,
                                CPU_adapter_calls=78338, CPU_adapter_ordered_APU_stores=590312,
                                CPU_adapter_role_mode_cells=28, CPU_full_other_identity_calls=9216,
                                CPU_other_caller_flag_cases=6912, CPU_Mike_faithful_outer_ABI_cases=4032,
                                CPU_compiled_IRQ_cases=18,
                                CPU_retained_true_nested_NMI_domain_negatives=6)
    for name, expected in q['receipt_sha256'].items():
        assert sha(Path(name)) == expected, name
    bindings = ready / 'source-bindings.json'
    assert sha(bindings) == q['source_bindings_sha256']
    bound = json.loads(bindings.read_text())
    assert len(bound) == 32
    for name, expected in bound.items():
        assert sha(ready / name) == expected, name
        if name.startswith('tools/'):
            assert sha(ROOT / 'tools/audit' / Path(name).name) == expected, name
    frozen = json.loads((D / 'frozen-inputs.json').read_text())
    assert len(frozen['source_files']) == 440 and len(frozen['shared_assets']) == 104
    for name, expected in (frozen['source_files'] | frozen['shared_assets']).items():
        assert sha(ROOT / name) == expected, name
    composition = q['composition']
    files = composition['changed_source_files']
    assert set(files) == {'src/entrypoint.s', 'src/expanded_audio.s',
                          'src/mike_native_music.s', 'smb1base-mmc5-expanded.cfg'}
    for name, row in files.items():
        old = ROOT / name
        assert (sha(old) if old.exists() else None) == row['before_sha256'], name
        assert sha(ready / 'source' / name) == row['after_sha256'], name
    before, after = [(D / n).read_bytes() for n in ['baseline.nes', 'candidate.nes']]
    changes = {str(i): sum(x != y for x, y in zip(before[16+i*8192:16+(i+1)*8192],
                                                after[16+i*8192:16+(i+1)*8192]))
               for i in range(128)}
    assert {i: n for i, n in changes.items() if n} == {'38': 29, '115': 7446, '126': 3}
    assert len(before) == len(after) and before[:16] == after[:16]
    assert before[16+128*8192:] == after[16+128*8192:]
    assert composition['retained_qualified_symbols'] == 54510
    for mapper, expected in composition['ordinary_target_hashes'].items():
        assert sha(D / ('candidate-' + mapper + '.nes')) == expected

    # These were independently rerun by ROOT, rather than inferred from donor
    # evidence. Preserve both strict raw comparisons and six nested-NMI negatives.
    independent = {
        'root-full-cpu-v1/proof.json': '5c2e76a5d97ca8f08e5e04c7358767d82db45ecbcfa7229a080df163a2c13d31',
        'root-dispatch-cpu-v1/proof.json': '9e13885128415c803a18886491295be69ada9abb529c6946696bfa2bfe571fdb',
        'root-native-pilot-hard-v1/native-result.json': 'd80ab676133c08f93db4634544e7d3c07c2a6fd9415a399bca731ff899418575',
    }
    for name, expected in independent.items():
        assert sha(D / name) == expected and json.loads((D / name).read_text())['passed'], name
    root_performance = {}
    for mode in ['easy', 'hard']:
        path = D / ('root-strict-performance-' + mode + '-v1.json')
        strict = json.loads(path.read_text())
        assert strict == q['strict_performance'][mode]
        assert strict['passed'] and not strict['regressions']
        root_performance[mode] = sha(path)
    pilot = json.loads((D / 'root-native-pilot-hard-v1/native-result.json').read_text())
    assert pilot['mode-readback.json']['actual'] == 1 and pilot['nmi-depth.json']['maximum_depth'] == 1

    # Bind the raw native output files, not just their summarized pass fields.
    raw = {}
    native_dirs = [p for p in (D / 'qualification-v1').glob('native-*') if p.is_dir()]
    assert len(native_dirs) == 6
    native_dirs.append(D / 'root-native-pilot-hard-v1')
    for folder in native_dirs:
        assert folder.is_dir()
        for path in folder.rglob('*'):
            if path.is_file():
                raw[str(path)] = sha(path)
    out.mkdir()
    (out / 'raw-native-bindings.json').write_text(json.dumps(raw, indent=2) + '\n')
    shutil.copy2(installed, out / 'previous-MMC5.nes')
    suffixes = ['.nes', '.dbg', '.lbl', '.map', '.build.json', '.build.log', '.cv3-mirror.json']
    backup = out / 'previous-default'
    backup.mkdir()
    for suffix in suffixes:
        old = default.with_suffix(suffix)
        if old.exists():
            shutil.copy2(old, backup / old.name)
    for name, row in files.items():
        if row['before_sha256'] is not None:
            saved = out / 'previous-source' / name
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / name, saved)
    try:
        for name in files:
            shutil.copy2(ready / 'source' / name, ROOT / name)
        with (out / 'fresh-ROOT-build.log').open('w') as log:
            subprocess.run([sys.executable, str(ROOT / 'tools/build_mmc5_expanded.py'),
                            '--output', str(out / 'candidate.nes')],
                           cwd=ROOT, check=True, stdout=log, stderr=subprocess.STDOUT)
        assert sha(out / 'candidate.nes') == FINAL, 'Fresh canonical ROOT build differs'
        for suffix in suffixes:
            assert (out / 'candidate.nes').with_suffix(suffix).is_file(), suffix
    except BaseException:
        for name, row in files.items():
            if row['before_sha256'] is None:
                (ROOT / name).unlink(missing_ok=True)
            else:
                shutil.copy2(out / 'previous-source' / name, ROOT / name)
        raise
    stage = installed.with_name(installed.stem + '.staging-' + FINAL[:8] + '.nes')
    assert not stage.exists()
    shutil.copy2(out / 'candidate.nes', stage)
    assert sha(stage) == FINAL
    stage.replace(installed)
    for suffix in suffixes:
        shutil.copy2((out / 'candidate.nes').with_suffix(suffix), default.with_suffix(suffix))
    assert sha(default) == sha(installed) == FINAL
    proof = dict(adopted=True, goal_complete=False, ROM_sha256=FINAL,
                 parent_ROM_sha256=PARENT, fresh_canonical_ROOT_compile_exact=True,
                 installed=str(installed), changed_source_files=files,
                 changed_PRG_bytes=composition['changed_PRG_bytes'], new_RAM_bytes=0, new_CHR_bytes=0,
                 all_other_banks_fixed_DPCM_and_CHR_exact=True,
                 qualified_symbols_retained=54510,
                 genuine_private_symbol_exception=composition['genuine_private_symbol_exception'],
                 original_NSF_sha256='e67ccc9d3950a62d850d6da27aaecd32fdd50db05c9c341d36dc99b6bfa95845',
                 source_tracks=11, adapted_roles=14, CPU_coverage=q['coverage'],
                 native=q['native'], strict_performance=q['strict_performance'],
                 qualification_sha256=sha(qualification), source_bindings_sha256=sha(bindings),
                 independent_ROOT_receipts=independent, independent_ROOT_performance=root_performance,
                 raw_native_binding_count=len(raw), raw_native_bindings_sha256=sha(out / 'raw-native-bindings.json'),
                 ordinary_target_hashes=composition['ordinary_target_hashes'], rollback=str(out),
                 scope='Authentic original music, mapped SMB contexts and typed hardware mix; current-parent source, CPU, native, interrupt and equal-work cadence checks. Six nested-NMI injections remain explicit non-reentrant-domain negatives. This is not every-item, whole-roster-current-route, full campaign, real hardware, or universal60Hz certification. Roll fade, Parodius music/visibility, remaining CV3 effects and other open roster work remain pending.')
    (out / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')
    dest = ROOT / 'build/verification/mike-native-music'
    dest.mkdir(exist_ok=True)
    shutil.copy2(out / 'proof.json', dest / 'proof.json')
    print(json.dumps(dict(adopted=True, ROM_sha256=FINAL, installed=str(installed),
                          proof=str(out / 'proof.json'), proof_sha256=sha(out / 'proof.json'))))


if __name__ == '__main__':
    main()
