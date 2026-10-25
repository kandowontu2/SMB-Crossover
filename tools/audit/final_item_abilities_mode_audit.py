"""Withdraw invalid Hard labels without modifying any historical receipt."""
from pathlib import Path
import argparse
import hashlib
import json
import re

sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--archive',required=True,type=Path)
    p.add_argument('--output',required=True,type=Path)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    rows=[]
    groups=[('current220_progression',a.archive/'final-item-matrix-v1','current220-*-*-native-v3'),
            ('current84_progression',a.archive/'final-item-matrix-v1','current84-*-*-native-v1'),
            ('current84_acquired_abilities',a.archive/'current84-abilities-v1','*-*-native-v2')]
    for group,root,pattern in groups:
        folders=sorted(root.glob(pattern));assert len(folders)==6,(group,len(folders))
        for folder in folders:
            f=folder/'proof.json';z=json.loads(f.read_text());assert z['passed']
            script=(folder/'run.lua').read_text()
            match=re.search(r'\["hard"\]=(True|False)',script);assert match
            assert "r('CrossoverBehaviorVersion')==(C.hard and 1 or 0)" in script
            assert 'hard' not in z['native']
            # Undefined capitalized identifiers are nil. The executed fixture's
            # successful RAM-read assertion therefore required actual mode0.
            rows.append(dict(group=group,path=str(f),proof_sha256=sha(f),
                script_sha256=sha(folder/'run.lua'),ROM_sha256=z['ROM_sha256'],
                family=z['family'],declared_mode=z['mode'],configuration_identifier=match[1],
                actual_mode_from_passed_RAM_read_assertion=0,actual_mode='easy',
                hard_label_withdrawn=z['mode']=='hard',
                evidence="Passed actual RAM read: r('CrossoverBehaviorVersion')==(C.hard and1or0); C.hard nil makes expected0. native.hard absent independently confirms nil. No raw old mode trace or new native rerun is substituted."))
    result=dict(audit_passed=True,native_requalified=False,goal_complete=False,
        affected_receipts=rows,affected_final_runs=len(rows),withdrawn_hard_labels=sum(r['hard_label_withdrawn']for r in rows),
        retained_actual_scope='Each family was exercised twice in Easy. The six84 acquired-ability runs are62 executions of31 distinct Easy plans across3 identities/3mode cells, not six mode cells. The220/84 progression sets each exercise3 actual Easy mode cells twice; direct CPU mode predicates are unaffected.',
        corrections='All original receipts, captures, hashes and source-only matrix views preserved. Prior Hard/native six-mode-cell assertions in the affected summaries/reports are withdrawn. Fresh529 numerical-mode native reruns are separate evidence.',
        artifact_policy='No old JSON/report/screenshot was rewritten or relabeled.',script_sha256=sha(Path(__file__)))
    f=a.output/'proof.json';f.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(audit_passed=True,affected_final_runs=len(rows),withdrawn_hard_labels=result['withdrawn_hard_labels'],proof=str(f),sha256=sha(f))))


if __name__=='__main__':main()
