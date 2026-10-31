"""Retain the exact reason the 16-byte isolated lab cannot be a host scope."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).resolve().parent))
import thomas_original_cpu_1031_v1 as T
from check_thomas_c2_component_1031_v2 import C2Bus
from verify_native_relocation import NesMPU
P=R/'build/thomas-c2-component-v4';O=R/'build/thomas-c2-scope-controls-v1/old16-scope-negative.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    assert not O.exists();s=T.labels(P/'component.lbl');b=C2Bus()
    list.__setitem__(b,slice(0x6000,0x8000),(P/'component.bin').read_bytes())
    list.__setitem__(b,slice(0,2048),[(i*73+41)&255 for i in range(2048)])
    c=NesMPU(memory=b);T.run(c,s['ThomasC2ColdInit'],0,0,0xf9,0x30)
    original=b[9];T.run(c,s['ThomasC2Borrow']);borrowed=b[9]
    # Actual RP2A03 host-owned INC09 instruction in a disposable CPU arena.
    list.__setitem__(b,slice(0x5d00,0x5d03),[0xe6,9,0x60]);T.run(c,0x5d00);during=b[9]
    T.run(c,s['ThomasC2Return']);after=b[9]
    assert original==0xba and borrowed==0 and during==1 and after==original
    record=dict(result='RETAINED_HOST_SCOPE_NEGATIVE',source_stage_sha256=sha(P/'source-stage.json'),
        original_host09=original,host09_during16byte_borrow=borrowed,external_actual_INC09=during,host09_after_old_return=after,correct_host_result=(original+1)&255,
        defect='Old16byte owner scope both hides host09 from the interrupt and restores its stale value afterward. It is a lab-onlyprototype, not a hostlease.',
        accepted_successor='build/thomas-c2-eight-melee-v1:08..0F are directC2fields, onlyR0..7borrowed; actuallab132NMI/IRQcontrols preservehost09increment',
        bindings={str(p):sha(p)for p in [Path(__file__),Path(T.__file__),R/'tools/audit/check_thomas_c2_component_1031_v2.py',R/'tools/audit/verify_native_relocation.py',P/'source-stage.json',P/'component.bin',P/'component.lbl']})
    O.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8');print(json.dumps(record))

if __name__=='__main__':main()
