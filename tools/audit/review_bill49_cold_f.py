"""Freeze the completed cold-helper comparisons without broad body claims."""
from pathlib import Path
import hashlib
import json

R = Path(__file__).resolve().parents[2]
H = R/'build/verification/root49-bill-cold-f'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    output = H/'actual-review.json'
    assert not output.exists()
    prep = json.loads((H/'preparation.json').read_text())
    assert sha(R/prep['corrected_core']['path']) == prep['corrected_core']['sha256']
    assert prep['runtime_changed'] is False and prep['masks_added'] == []
    rows = []
    refs = [H/'preparation.json', H/'verify_cpu.py', R/prep['original_cpu']['path'],
            R/prep['original_negative']['path']]
    negative = json.loads((R/prep['original_negative']['path']).read_text())
    assert negative['status']=='FAIL_COMPONENT_UNWAIVED' and negative['case']==0
    for mapper in ['mmc3','mmc5']:
        p = H/(mapper+'-a.json')
        data = json.loads(p.read_text())
        assert data['status']=='PASS_EXECUTED_COMPILED_COMPONENTS' and data['group']=='cold'
        assert data['cases']==29952 and data['all256_inputP_values']==list(range(256))
        assert data['script']['sha256']==prep['corrected_core']['sha256']
        assert data['groups']['cold61B-pure-full-ABI']['cases']==9984
        assert data['groups']['cold-both-real-callers-through-TYA-allP']['cases']==19968
        for side in ['before','after']:
            for kind in ['rom','debug','labels','map']:
                q = data[side][kind]
                assert sha(q['path'])==q['sha256']
        rows.append(dict(mapper=mapper,cases=data['cases'],groups=data['groups'],digest=data['digest']))
        refs.append(p)
    report = dict(status='PASS_COLD_HELPER_ONLY_59904_EXECUTED_COMPARISONS',
        script_sha256=sha(__file__),references={str(p.relative_to(R)):sha(p) for p in refs},
        results=rows, executed_comparisons=59904,
        complete_initial_RAM_equality_asserted=True, all_input_P_bytes=True,
        final_registers_status_stack_RAM_and_ordered_writes_exact=True, exclusions_added=[],
        original_different_entry_bank_negative_retained=True,
        qualifications=['Only the cold helper relocation and its two actual callers were executed in group cold.',
            'This is not a pass for the full Bill body proposal or its incomplete46-scenario native coverage.',
            'Other CPU groups, native hardware interrupts, ordinary traversal and full source geometry remain separate gates.'],
        main_runtime_changed=False, goal_complete=False, accepted_release=False)
    output.write_text(json.dumps(report,indent=2)+'\n')
    print(report['status'],sha(output),flush=True)


if __name__=='__main__':
    main()
