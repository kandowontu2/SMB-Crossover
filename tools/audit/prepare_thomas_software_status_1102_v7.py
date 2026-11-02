"""Compare all six real6502 flags against Mesen's actual status representation."""
import json
from pathlib import Path
from prepare_selected_native_packet_v1 import R, prepare, sha

O=R/'build/bub-menu-candidate-1102-v2'
PIN='f5c30ceaa36894f3e814ef277081ecd9cf434a934c0f7b3f514c2291be0e1cfc'


def main():
    source=O/'native-thomas-software-rti/controller.lua'
    failure=O/'native-thomas-software-rti/capture/vector-classification.json'
    old=source.read_text();q=json.loads(failure.read_text())
    saved=q['post_pending'][0]['status'];actual=q['cpu']['p']
    assert(saved,actual,q['post_pending'][0]['p'])==(0xb0,0x80,6)
    assert saved&0xcf==actual&0xcf and(saved^actual)==0x30
    text=old
    marker=" requireVector((s['cpu.ps']&0xef)==(q.status&0xef),'Software RTI restores its original P (B is not a CPU latch)')"
    assert text.count(marker)==1
    text=text.replace(marker,""" -- Mesen's actual cpu.ps omits both non-latched stack bits B/constant5.
 -- Compare C/Z/I/D/V/N individually; no real flag is omitted.
 for _,flag in ipairs({1,2,4,8,64,128})do
  requireVector((s['cpu.ps']&flag)==(q.status&flag),'Software RTI restores each real C/Z/I/D/V/N flag')
 end
 requireVector(s['cpu.ps']&0x30==0,'Actual Mesen status excludes non-latched stack bits4/5')""")
    marker="   setup_sp=q.sp,status=q.status,return_pc=q.return_pc,old_C=q.old_C,"
    assert text.count(marker)==1
    text=text.replace(marker,marker+"\n   actual_reported_P=emu.getState()['cpu.ps'],expected_real_flags=q.status&0xcf,")
    for a in ["assert(q.kind==kind and q.sp==s['cpu.sp'],'Real vector stack balance')",
              "assert(q.smc==image()and q.a==s['cpu.a']and q.x==s['cpu.x']and q.y==s['cpu.y'],'Vector restores live registers/SMC')",
              "requireVector(stackbyte(soft.sp,1)==soft.status and stackbyte(soft.sp,2)+256*stackbyte(soft.sp,3)==soft.return_pc,'Exact software RTI P/PC frame retained')",
              "requireVector(q.status==stackbyte(q.sp,1)and q.return_lo==stackbyte(q.sp,2)and q.return_hi==stackbyte(q.sp,3),'Hardware RTI original P/PC stack frame retained')"]:
        assert old.count(a)==text.count(a)==1
    controls="emu.addEventCallback(function()\n if done then return end;local b={}"
    assert old.split(controls,1)[1]==text.split(controls,1)[1]
    receipt=O/'thomas-software-status-v7.json'
    assert not receipt.exists()
    receipt.write_text(json.dumps(dict(prepared=True,native=False,ROM_changed=False,
        ROM_SHA256=PIN,actual_negative_SHA256=sha(failure),
        actual_saved_stack_P=saved,actual_Mesen_cpu_ps=actual,
        actual_pre_setup_Mesen_cpu_ps=q['post_pending'][0]['p'],
        six_latched_flag_mask=0xcf,stack_only_bits=0x30,
        real_flag_XOR=(saved^actual)&0xcf,
        all_C_Z_I_D_V_N_compared_individually=True,
        original_hardware_parity_and_software_frame_assertions_retained=True,
        scope='Actual native negative establishes only stack bits4/5 differ. The successor compares every real status flag individually and asserts Mesen omits bits4/5; no ROM or input changes.'),indent=2)+'\n')
    rom=R/'build/wwf-helper-stable-1102-v2/candidate2.nes';assert sha(rom)==PIN
    prepare(O/'native-thomas-software-status',rom,text,
        [Path(__file__),source,failure,receipt,O/'thomas-software-rti-CPU-v6.json'],
        expected=PIN,timeout=240,allow_interactive=True,
        scope='Unchanged Thomas full1-1 replay and strict physically qualified software/hardware RTI contracts. Observer corrects actual Mesen cpu.ps representation: all six C/Z/I/D/V/N flags compare individually, stack-onlyB/constant5 explicitly absent. Positive actual software/hardware counts required; no ROM/gameplay/install change.')


if __name__=='__main__':main()
