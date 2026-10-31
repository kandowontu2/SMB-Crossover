"""Follow the genuine SMB3+ controller from a captured native B-edge state.

Form/input variations below are explicitly instruction fixtures, not earned
native powerups. The original native stack/return and complete RAM seed remain
bound, and all original mapped instructions execute without callback traps.
"""
from pathlib import Path
import hashlib
import itertools
import json
import sys

R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/audit'))
from discover_smb3plus_chr_routes_1030_v1 import ChrRomBus,DONOR,EXPECTED
from benj_mario_donor_trace_1030_v1 import MPU

O=R/'build/smb3plus-kick-caller-1031-v1'
N=R/'build/smb3plus-kick-donor-native-1031-v3/discovery'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not O.exists() and sha(DONOR)==EXPECTED
    native=json.loads((N/'capture/binding.json').read_text())
    assert native['exit_code']==0 and native['ROM_sha256']==EXPECTED
    for p,digest in native['bindings'].items():assert sha(p)==digest,p
    snap=(N/'capture/ram-B-entry.bin').read_bytes()
    assert len(snap)==32768 and snap[0x17]==snap[0x18]==64
    assert snap[0x119]==2 and snap[0xed]==0
    raw=DONOR.read_bytes();cases=[]
    for character,form,down in itertools.product([0,1,2,3],range(7),[0,4]):
        bus=ChrRomBus(raw);bus.ram[:0x8000]=snap
        bus.select=0x47;bus.reg[6]=0;bus.reg[7]=8;bus.remap()
        bus.ram[0x119]=bus.ram[0x11e]=character
        bus.ram[0xed]=bus.ram[0x126]=form
        bus.ram[0x17]|=down
        cpu=MPU(memory=bus);bus.cpu=cpu
        cpu.pc=0xa6bb;cpu.sp=249;cpu.p=0x22;cpu.x=1;cpu.y=252;cpu.a=0
        ret=1+bus.ram[0x1fa]+256*bus.ram[0x1fb]
        visited=[];kick=[]
        for count in range(20000):
            if cpu.pc==ret and cpu.sp==251:break
            bank=bus.banks[(cpu.pc-0x8000)//8192] if cpu.pc>=0x8000 else -1
            if (bank,cpu.pc) in [(8,0xa9ae),(8,0xa99e),(8,0xb0a0),(38,0xac82),(38,0xac79)]:
                visited.append(dict(bank=bank,PC=cpu.pc,source_offset=16+bank*8192+cpu.pc%8192,
                    SP=cpu.sp,timer=bus.ram[0x517],pose=bus.ram[0xee]))
            if bank==38 and cpu.pc==0xac82:kick.append(count)
            assert bus[cpu.pc]!=0,('BRK',character,form,hex(cpu.pc),bank)
            cpu.step()
        else:raise AssertionError(('Bounded original controller',character,form,hex(cpu.pc)))
        assert bool(kick)==(form==1),('Actual caller form gate',character,form,kick)
        if character==2 and form==1 and not down:
            assert (bus.ram[0x517],bus.ram[0xee],bus.ram[0x4f3])==(12,0x2d,0x10)
        cases.append(dict(character=character,form=form,down=bool(down),
            instructions=count,kick_entries=len(kick),timer=bus.ram[0x517],pose=bus.ram[0xee],
            source_QLevel2=bus.ram[0x4f3],call_boundaries=visited))
    O.mkdir(parents=True)
    report=dict(passed=True,CPU_only=True,native_host=False,donor_sha256=EXPECTED,
        cases=cases,native_seed=str(N/'capture/ram-B-entry.bin'),
        original_return_PC=ret,original_return_SP=251,
        result='Kick hook is big-form dry GndMov_Big only, after genuine SoarJumpFallFrame and before later power/special frames.',
        limits=['Native seed is small Toad. All changed characters/forms/Down are explicit CPU fixtures.',
            'No host gameplay, earned powerup, SFX, menu admission or campaign qualification.'],
        bindings={str(p):sha(p) for p in [Path(__file__),DONOR,N/'ready.json',N/'controller.lua',
            N/'capture/binding.json',N/'capture/ram-B-entry.bin',N/'capture/cpu-B-entry.txt',
            R/'tools/audit/discover_smb3plus_chr_routes_1030_v1.py',
            R/'tools/audit/benj_mario_donor_trace_1030_v1.py']})
    path=O/'caller-controls.json';path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(passed=True,cases=len(cases),sha256=sha(path),scope=report['result'])))


if __name__=='__main__':main()
