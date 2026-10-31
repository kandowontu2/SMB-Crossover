"""Rebind every frozen original input/action/AI cohort to true C2 source."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import wwf_c2_relocation_model_v2 as M
import wwf_action_directory_controls_v1 as D
import wwf_action_ai_controls_v1 as A
T=M.T;O=R/'build/wwf-c2-relocation-controls-v2'

def main():
    assert not O.exists();O.mkdir();M.install()
    for p,h in M.P['bindings'].items():assert T.sha(p)==h,p
    for name,module in [('inputs',T),('directories',D),('AI',A)]:
        module.O=O/name;module.main()
    q=dict(passed=True,source=True,isolated_lab=True,native=False,no_host_allocation=True,source_build=T.sha(M.L/'build-proof.json'),controller_cases=132,controller_ticks=8448,directory_cases=556,directory_ticks=35584,AI_fullflag_cases=768)
    q['indexed_X_witnesses']={str(k):sorted(v)for k,v in M.INDEX_WITNESS.items()}
    q['actual_environment_scratch_clobbers']=sorted(M.HOST_CLOBBERS)
    q['bindings']={str(p.resolve()):T.sha(p)for p in [Path(__file__),Path(M.__file__),M.L/'build-proof.json',M.L/'vm.bin',M.L/'c2.bin',M.L/'environment.bin',M.L/'irq.bin',O/'inputs/controls.json',O/'directories/controls.json',O/'AI/controls.json']}
    T.save(O/'controls.json',q);print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))
if __name__=='__main__':main()
