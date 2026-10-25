"""Freeze an externally qualified Mike music integration packet for review.

This does not adopt sources, overwrite Downloads, commit, or alter any older
receipt. The ready snapshot includes the complete four-file deployable delta.
"""
from pathlib import Path
import argparse, difflib, hashlib, json, shutil

ROOT = Path(__file__).resolve().parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--composition', type=Path, required=True)
    p.add_argument('--qa', type=Path, required=True)
    a = p.parse_args()
    d = a.composition.resolve()
    assert not d.is_relative_to(ROOT)
    comp = json.loads((d / 'composition.json').read_text())
    q = d / 'qualification-v1'
    runs = json.loads((q / 'qualification.json').read_text())
    assert comp['passed'] and runs['passed']
    assert comp['candidate_ROM_sha256'] == runs['candidate_ROM_sha256'] == sha(d / 'candidate.nes')
    assert comp['parent_ROM_sha256'] == runs['parent_ROM_sha256'] == sha(d / 'baseline.nes')
    ready = d / 'ready-v1'
    ready.mkdir(exist_ok=False)
    proofs = {}
    for f in [d / 'composition.json', d / 'frozen-inputs.json', d / 'preparation-fast-source.json', q / 'qualification.json']:
        proofs[str(f)] = sha(f)
    cpu = {}
    for name in ['cpu-full', 'cpu-dispatch', 'cpu-Mike-outer', 'cpu-cost']:
        f = q / name / 'proof.json'
        cpu[name] = json.loads(f.read_text())
        assert cpu[name]['passed']
        proofs[str(f)] = sha(f)
    full, dispatch = cpu['cpu-full'], cpu['cpu-dispatch']
    coverage = dict(CPU_original_calls=sum(v['calls'] for v in full['golden_driver']),
                    CPU_original_ordered_APU_stores=sum(v['ordered_APU_stores'] for v in full['golden_driver']),
                    CPU_adapter_calls=sum(v['source_schedule_calls'] for v in dispatch['actual_dispatch']['roles']),
                    CPU_adapter_ordered_APU_stores=sum(v['source_stores'] for v in dispatch['actual_dispatch']['roles']),
                    CPU_adapter_role_mode_cells=len(dispatch['actual_dispatch']['roles']),
                    CPU_full_other_identity_calls=sum(v['cases'] for v in dispatch['full_outer_non_Mike_identities']),
                    CPU_other_caller_flag_cases=sum(v['cases'] for v in full['non_Mike_full_outer']),
                    CPU_Mike_faithful_outer_ABI_cases=cpu['cpu-Mike-outer']['whole_Mike_AudioUpdate_calls'],
                    CPU_compiled_IRQ_cases=len(dispatch['compiled_interrupts']['actual_IRQ_cases']),
                    CPU_retained_true_nested_NMI_domain_negatives=len(dispatch['compiled_interrupts']['actual_nested_NMI_domain_negatives']))
    assert list(coverage.values()) == [198011, 961696, 78338, 590312, 28, 9216, 6912, 4032, 18, 6], coverage
    native, performance = {}, {}
    for mode, number in [('easy', 0), ('hard', 1)]:
        cells = {}
        for kind in ['parent-performance', 'candidate-performance', 'candidate-music']:
            folder = q / ('native-' + kind + '-' + mode)
            result = json.loads((folder / 'native-result.json').read_text())
            assert result['passed'] and result['mode-readback.json']['actual'] == number
            assert result['config']['hard'] == number
            assert result['ROM_sha256'] == (comp['parent_ROM_sha256'] if kind.startswith('parent') else comp['candidate_ROM_sha256'])
            assert result['nmi-depth.json']['maximum_depth'] == 1
            for name in ['native-result.json', 'binding.json', 'proof.json', 'mode-readback.json',
                         'nmi-depth.json', 'ownership-guards.json', 'chr-commit.json', 'run.lua']:
                f = folder / name
                proofs[str(f)] = sha(f)
            cells[kind] = {k: result[k] for k in ['proof.json', 'mode-readback.json', 'nmi-depth.json']}
        strict = q / ('strict-performance-' + mode + '.json')
        perf = json.loads(strict.read_text())
        assert perf['passed'] and perf['no_extra_skipped_draws_or_lag']
        assert perf['exact_gameplay_work_excluding_wall'] and not perf['regressions']
        performance[mode] = perf
        proofs[str(strict)] = sha(strict)
        native[mode] = cells
    bindings = {}
    diff = []
    for name, hashes in comp['changed_source_files'].items():
        f = d / 'source' / name
        old = d / 'baseline-source' / name
        assert sha(f) == hashes['after_sha256']
        assert (sha(old) if old.exists() else None) == hashes['before_sha256']
        target = ready / 'source' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(f, target)
        bindings['source/' + name] = sha(target)
        diff.extend(difflib.unified_diff(old.read_text().splitlines(True) if old.exists() else [],
                                        f.read_text().splitlines(True),
                                        fromfile='a/' + name if old.exists() else '/dev/null', tofile='b/' + name))
    (ready / 'review.patch').write_text(''.join(diff))
    (ready / 'changed-source-files.json').write_text(json.dumps(comp['changed_source_files'], indent=2) + '\n')
    helpers = ['mike_parodius_music_probe.py', 'check_tmnt_render_oa.py',
               'check_tmnt_audio_fallback_oc.py', 'verify_native_relocation.py',
               'final_item_matrix.py', 'link_pit_rygar_sophia_audit_cpu.py',
               'observe_chip_committed_write.py', 'vehicles_audio_wiring_guards.lua',
               'chr_commit_observer.lua', 'tmnt_performance_observer.lua',
               'run_mesen_isolated.py']
    tool_files = list((ROOT / 'tools/audit').glob('mike_native_music_*')) + [ROOT / 'tools/audit' / n for n in helpers]
    for tool in tool_files:
        if tool.is_file():
            dest = ready / 'tools' / tool.name
            dest.parent.mkdir(exist_ok=True)
            shutil.copyfile(tool, dest)
            bindings['tools/' + tool.name] = sha(dest)
    shutil.copyfile(a.qa, ready / 'qa.txt')
    bindings.update({'qa.txt': sha(ready / 'qa.txt'), 'review.patch': sha(ready / 'review.patch'),
                     'changed-source-files.json': sha(ready / 'changed-source-files.json')})
    (ready / 'source-bindings.json').write_text(json.dumps(bindings, indent=2) + '\n')
    result = dict(passed=True, status='PRIVATE_CURRENT_PARENT_SOURCE_CPU_NATIVE_QUALIFIED_READY_FOR_ROOT_REVIEW',
                  accepted=False, goal_complete=False, parent_ROM_sha256=comp['parent_ROM_sha256'],
                  candidate_ROM_sha256=comp['candidate_ROM_sha256'], composition=comp,
                  coverage=coverage, native=native, strict_performance=performance,
                  receipt_sha256=proofs, source_bindings_sha256=sha(ready / 'source-bindings.json'),
                  whole_driver_APU_channels_stores_and_source_cadence_preserved=True,
                  genuine_source_RAM_pointer_translation_required=True,
                  true_nested_NMI_domain_negative_is_NOT_a_pass=True,
                  full_campaign_or_universal_lag_claim=False, Parodius_native_music_still_open=True,
                  deployment_changes_only=list(comp['changed_source_files']),
                  ROOT_production_Git_and_Downloads_not_modified=True,
                  tool_sha256=sha(Path(__file__)))
    (ready / 'qualification.json').write_text(json.dumps(result, indent=2) + '\n')
    archive = Path(shutil.make_archive(str(d / 'ready-v1'), 'zip', ready))
    summary = dict(passed=True, candidate_ROM_sha256=comp['candidate_ROM_sha256'],
                   qualification_sha256=sha(ready / 'qualification.json'),
                   source_bindings_sha256=sha(ready / 'source-bindings.json'),
                   review_sha256=sha(ready / 'review.patch'), archive_sha256=sha(archive))
    (d / 'ready-v1-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
