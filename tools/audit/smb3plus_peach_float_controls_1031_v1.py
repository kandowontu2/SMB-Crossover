"""Compare joined ordinary float producers/consumers to original instructions."""
from pathlib import Path
import itertools
import json
import sys

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import benj_current_menu_controls_1030_v1 as M
import prepare_functional_roster_visuals58_v1 as B
from discover_smb3plus_chr_routes_1030_v1 import ChrRomBus,DONOR
from benj_mario_donor_trace_1030_v1 import MPU
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address

O=R/'build/smb3plus-peach-float-host-1031-v3';J=O/'joint'
N=R/'build/smb3plus-peach-float-donor-native-1031-v1/discovery/capture/ram-float-entry.bin'
FIELDS=['MbFloatExpired','MbFloatTimer','MbFloatAnchor','MbFloatReady',
        'M3Native::Player_Y','M3Native::Player_YHi','M3Native::Player_YVel']


def main():
    assert not (O/'float-controls-v1.json').exists()
    stage=json.loads(B.read(O/'source-stage.json'));B.bound(stage)
    b=scoped_load(J/'candidate.nes');snap=N.read_bytes();bus=ChrRomBus(DONOR.read_bytes())
    cpu=MPU(memory=bus);bus.cpu=cpu;rows=[]

    def check(kind,form,ready,expired,held,timer=0,air=1,water=0,kuribo=0,vy=0,sink=0):
        bus.ram[:0x8000]=snap;bus.select=0x47;bus.reg[6]=0
        bank,entry,label,offset={'velocity':(31,0xb5d0,'MbPeachVelocityEnd',0),
            'after_jump':(30,0xbac0,'MbPeachAfterJump',3),
            'jump_root':(32,0xa003,'MbPeachJumpRoot',0)}[kind]
        bus.reg[7]=bank;bus.remap()
        original={0x119:3,0x11e:3,0x726:0,0xed:form,0x126:form,0x17:held,
            0x7ae4:expired,0x7ae5:timer,0x7ae6:128,0x7ae7:ready,
            0xd8:air,0x575:water,0x577:kuribo,0x58a:sink,0x140:0,0x142:0,0x1cc:0,
            0xa2:100,0x87:1,0xcf:vy,0xe5:128,0xee:14}
        for at,value in original.items():bus.ram[at]=value
        cpu.pc=entry;cpu.sp=0xfd;cpu.p=0x32;cpu.a=0;cpu.x=0;cpu.y=7
        bus.ram[0x1fe:0x200]=bytes.fromhex('ff02')
        for count in range(500):
            if cpu.pc==0x300:break
            assert bus[cpu.pc]!=0,('Original BRK',kind,hex(cpu.pc));cpu.step()
        else:raise AssertionError(('Original bounded float',kind,hex(cpu.pc)))
        expected=tuple(bus.ram[a] for a in [0x7ae4,0x7ae5,0x7ae6,0x7ae7,0xa2,0x87,0xcf])
        q=M.T.make(b,17)
        q.put(M3Variant=3,M3Form=form,MbFloatExpired=expired,MbFloatTimer=timer,
              MbFloatAnchor=128,MbFloatReady=ready)
        for name,value in {'Player_InAir':air,'Player_InWater':water,'Player_Kuribo':kuribo,
            'Player_SandSink':sink,'Pad_Holding':held,'Player_Y':100,'Player_YHi':1,
            'Player_YVel':vy,'Player_Frame':14}.items():q.set('M3Native::'+name,value)
        start=None if not offset else (address(b,label)+offset,91)
        c,tr,path,info=M.T.invoke(q,label,a=0,x=0,y=7,start=start)
        actual=tuple(q.get(n) for n in FIELDS)
        row=dict(kind=kind,form=form,ready=ready,expired=expired,held=held,timer=timer,
            air=air,water=water,kuribo=kuribo,VY=vy,sink=sink,result=actual)
        if actual!=expected:
            B.write(O/'float-negative-v1.json',json.dumps(dict(case=row,source=expected,
                candidate=stage['candidate'],script_sha256=B.sha(__file__)),indent=2)+'\n')
            raise AssertionError((row,expected))
        rows.append(row)

    for form,ready,expired,held,air,water,timer in itertools.product(range(7),range(3),[0,1],
            [0,128],[0,1],[0,1],[0,15,159]):
        check('velocity',form,ready,expired,held,timer,air,water)
    for form,ready,expired,held,vy,sink in itertools.product(range(7),range(3),[0,1],[0,128],[255,0,1],[0,1]):
        check('after_jump',form,ready,expired,held,vy=vy,sink=sink)
    for form,ready in itertools.product(range(7),range(3)):
        check('jump_root',form,ready,0,128)
    d=dict(passed=True,CPU_only=True,native=False,candidate=stage['candidate'],
        source_cases=len(rows),cases=rows,
        source_domain='Original P1, ordinary ground-pound fields0140/0142=0 and native one-tick delay01CC=0; real nonsolid head classification.',
        enum_invariants='All legal Expired0/1 and Ready0/1/2 states, every ordinary form, ground/air/water, held/released, negative/nonnegative velocity, timer boundary and sinking producers.',
        limits=stage['limits'],bindings={str(p):B.sha(p) for p in [Path(__file__),O/'source-stage.json',
            J/'candidate.nes',J/'candidate.dbg',DONOR,N]})
    B.write(O/'float-controls-v1.json',json.dumps(d,indent=2)+'\n')
    print(json.dumps(dict(passed=True,cases=len(rows),candidate=stage['candidate'])))


if __name__=='__main__':main()
