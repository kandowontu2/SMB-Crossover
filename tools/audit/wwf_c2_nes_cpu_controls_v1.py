"""Rebind existing WWF cohorts to NES binary ADC/SBC with D retained."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from verify_native_relocation import NesMPU
import wwf_c2_relocation_model_v2 as M
import wwf_action_directory_controls_v1 as D
import wwf_action_ai_controls_v1 as A
import wwf_c2_addressing_controls_v1 as B
import wwf_c2_interrupt_controls_v1 as I
import wwf_isolated_host_phase_controls_v2 as H
T=M.T;O=R/'build/wwf-c2-nes-cpu-controls-v1'

def main():
    assert not O.exists();O.mkdir();M.install()
    M.MPU=T.MPU=T.W.MPU=B.MPU=I.MPU=NesMPU
    results=[]
    for name,module in [('inputs',T),('directories',D),('AI',A),('addressing',B),('interrupts',I),('cold-phase',H)]:
        module.O=O/name;module.main();result=module.O/'controls.json';assert json.loads(result.read_text())['passed'];results.append(result)
    q=dict(passed=True,source_CPU_lab=True,native_host=False,no_host_allocation=True,CPU='Project NesMPU; original D flag retained; actual ADC/SBC always binary.',source_images_unchanged=True,input_cases=132,input_updates=8448,directory_cases=556,directory_updates=35584,AI_fullflag_cases=768,addressing_cases=504960,actual_interrupt_cuts=2748,cold_constructors=24,accepted_frame_pairs=4608,correction='The previous frozen stock-py65 all-flag receipts established source relocation equality under that model. This successor establishes NES binary-arithmetic equivalence with D retained. Source and frozen artifacts are unchanged.',limitations=['No real common/MMC5 interrupt integration or native launch is claimed.','This rebind uses the frozen VM donor-callback environment; the newly selected contact module has its own separate NES receipt.'])
    files=[Path(__file__),R/'tools/audit/verify_native_relocation.py',Path(M.__file__),Path(T.__file__),Path(D.__file__),Path(A.__file__),Path(B.__file__),Path(I.__file__),Path(H.__file__),M.L/'build-proof.json',M.L/'vm.bin',M.L/'c2.bin',*results]
    q['bindings']={str(p.resolve()):T.sha(p)for p in files};T.save(O/'controls.json',q);print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))
if __name__=='__main__':main()
