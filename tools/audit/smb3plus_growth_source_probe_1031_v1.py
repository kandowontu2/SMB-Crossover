"""Read the actual donor growth consumer; preserve a host mismatch if found."""
from pathlib import Path
import itertools
import json
import sys

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_functional_roster_visuals58_v1 as B
import smb3plus_body_host_controls_1030_v5 as G
from discover_smb3plus_chr_routes_1030_v1 import ChrRomBus,DONOR
from benj_mario_donor_trace_1030_v1 import MPU
from link_pit_rygar_sophia_audit_cpu import scoped_load

O=R/'build/smb3plus-growth-source-probe-1031-v1'
J=R/'build/smb3plus-menu-host-1031-v4/joint'
N=R/'build/smb3plus-peach-float-donor-native-1031-v1/discovery/capture/ram-float-entry.bin'


def main():
    assert not O.exists();O.mkdir()
    b=scoped_load(J/'candidate.nes');raw=DONOR.read_bytes();bus=ChrRomBus(raw)
    cpu=MPU(memory=bus);bus.cpu=cpu;rows=[];bad=[]
    for character,form,grow in itertools.product([2,3],[0,1],range(1,48)):
        bus.ram[:0x8000]=N.read_bytes();bus.select=0x47;bus.reg[6]=29;bus.reg[7]=8;bus.remap()
        for at,value in {0x119:character,0x11e:character,0x726:0,0xed:form,0x126:form,
            0xee:14,0xef:64,0x90:64,0xa2:160,0x87:0,0x543:0,0x544:0,0x545:0,0xfd:0,
            0x517:0,0x140:0,0x142:0,0x144:0,0x145:0,0x551:grow,0x554:0,0x555:0}.items():bus.ram[at]=value
        bus.ram[0x552:0x556]=bytes(4)
        cpu.pc=0xd224;cpu.sp=0xfd;cpu.p=0x30
        bus.ram[0x1fe:0x200]=bytes([255,2])
        for count in range(10000):
            if cpu.pc==0x300:break
            assert bus[cpu.pc]!=0,('Original growth BRK',hex(cpu.pc));cpu.step()
        else:raise AssertionError(('Bounded original growth',hex(cpu.pc)))
        page=bus.ram[0x71b];oam=bytes(bus.ram[0x200:0x218])
        expected=G.pixels([list(oam[a:a+4]) for a in range(0,24,4)],raw[16+524288:],page,(64,160),True)
        q=G.seed(b,character,form,14,1);q.put(M3Growth=grow)
        G.M.T.invoke(q,'M3Graphics')
        target_page=q.get('SmChrBank')+256*q.get('M3SpritePageHi')
        ptr=q.get('SmPosePtr')+256*q.get('SmPosePtr',1);size=q.m[ptr]
        parts=[list(q.m[ptr+1+a:ptr+5+a]) for a in range(0,size,4)]
        actual=G.pixels(parts,b['raw'][16+128*8192:],target_page)
        row=dict(character=character,form=form,grow=grow,source_page=page,source_frame=bus.ram[0xee],
            source_grow=bus.ram[0x551],host_page=target_page,host_frame=q.get('M3RenderFrame'),
            host_grow=q.get('M3Growth'),exact=actual==expected)
        rows.append(row)
        if not row['exact']:bad.append(row)
    d=dict(passed=not bad,source_CPU=True,native=False,cases=rows,failures=bad,
        original_entry='29:D224 with original A8 growth-frame table and real native Peach RAM seed; ordinary ground-pound flags clear.',
        candidate=B.sha(J/'candidate.nes'),bindings={str(p):B.sha(p) for p in [Path(__file__),DONOR,N,J/'candidate.nes',J/'candidate.dbg']})
    B.write(O/'probe.json',json.dumps(d,indent=2)+'\n')
    print(json.dumps(dict(cases=len(rows),failures=len(bad),first=bad[:3])))


if __name__=='__main__':main()
