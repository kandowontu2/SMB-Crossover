"""Compare the emitted hover wobble against the genuine donor function."""
from pathlib import Path
import argparse
import json
import sys

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import benj_current_menu_controls_1030_v1 as M
import prepare_functional_roster_visuals58_v1 as B
from discover_smb3plus_chr_routes_1030_v1 import ChrRomBus,DONOR
from benj_mario_donor_trace_1030_v1 import MPU
from link_pit_rygar_sophia_audit_cpu import scoped_load
N=R/'build/smb3plus-peach-float-donor-native-1031-v1/discovery/capture/ram-float-entry.bin'


def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--report',type=Path,required=True);a=p.parse_args()
    assert not a.report.exists()
    b=scoped_load(a.rom);bus=ChrRomBus(DONOR.read_bytes());cpu=MPU(memory=bus);bus.cpu=cpu
    snap=N.read_bytes();cases=[];failures=[]
    for timer in range(256):
        for y in [0,128,255]:
            bus.ram[:0x8000]=snap;bus.select=0x47;bus.reg[6]=0;bus.reg[7]=31;bus.remap()
            bus.ram[0x7ae5]=timer;bus.ram[0xe5]=128;bus.ram[0xa2]=y;bus.ram[0x87]=1
            cpu.pc=0xbb50;cpu.sp=0xfd;cpu.p=0x30;cpu.y=7;bus.ram[0x1fe:0x200]=bytes.fromhex('ff02')
            for count in range(150):
                if cpu.pc==0x300:break
                assert bus[cpu.pc]!=0;cpu.step()
            else:raise AssertionError('Bounded donor wobble')
            expected=bus.ram[0xa2],bus.ram[0x87]
            q=M.T.make(b,17)
            q.set('MbFloatTimer',timer);q.set('M3Native::Player_Y',y);q.set('M3Native::Player_YHi',1)
            c,tr,path,info=M.T.invoke(q,'MbPeachFloatWobble',y=7)
            actual=q.get('M3Native::Player_Y'),q.get('M3Native::Player_YHi')
            row=dict(timer=timer,Y=y,actual=actual,source=expected)
            if actual!=expected:failures.append(row)
            cases.append(row)
    d=dict(passed=not failures,CPU_only=True,native=False,candidate=B.sha(a.rom),cases=len(cases),
        failures=failures,results=cases,
        scope='Emitted factorization versus original31:BB50 in actual nonsolid-head domain, all256 table indices and Y carry seams.',
        bindings={str(p):B.sha(p) for p in [Path(__file__),a.rom,a.rom.with_suffix('.dbg'),DONOR,N]})
    B.write(a.report,json.dumps(d,indent=2)+'\n')
    print(json.dumps(dict(passed=d['passed'],cases=len(cases),failures=len(failures),first=failures[:1])))
    if failures:raise SystemExit(1)


if __name__=='__main__':main()
