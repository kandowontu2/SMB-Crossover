"""Finite existing private interrupt cohort on selected contact source."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from verify_native_relocation import NesMPU
import wwf_c2_relocation_model_v2 as M
import wwf_c2_interrupt_controls_v1 as I
T=M.T;O=R/'build/wwf-selected-contact-interrupts-v1'

def main():
    assert not O.exists();original=M.L;source=R/'build/wwf-selected-contact-v2'
    q=json.loads((source/'build-proof.json').read_text());M.L=source;M.P={**M.P,'labels':q['labels']};M.MPU=T.MPU=T.W.MPU=I.MPU=NesMPU
    oldprobe=I.compile_probe
    def compile_probe():
        M.L=original
        try:return oldprobe()
        finally:M.L=source
    I.compile_probe=compile_probe;I.O=O;I.main()
    result=json.loads((O/'controls.json').read_text());assert result['passed']
    result['CPU']='NesMPU: D retained, ADC/SBC binary';result['selected_contact_source']=True
    result['bindings'][str(Path(__file__).resolve())]=T.sha(__file__)
    result['bindings'][str(R/'tools/audit/verify_native_relocation.py')]=T.sha(R/'tools/audit/verify_native_relocation.py')
    T.save(O/'controls.json',result)
if __name__=='__main__':main()
