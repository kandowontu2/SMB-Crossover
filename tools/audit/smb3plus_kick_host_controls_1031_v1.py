"""Source kick equivalence and actual mapped M3Movement regressions."""
from pathlib import Path
import itertools
import json
import sys

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import benj_current_menu_controls_1030_v1 as M
import prepare_functional_roster_visuals58_v1 as B
from discover_smb3plus_chr_routes_1030_v1 import ChrRomBus,DONOR
from benj_mario_donor_trace_1030_v1 import MPU
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address

P=R/'build/smb3plus-body-host-1030-v3/joint'
O=R/'build/smb3plus-kick-host-1031-v1';J=O/'joint'
N=R/'build/smb3plus-kick-donor-native-1031-v3/discovery/capture/ram-B-entry.bin'


def seed(b,variant,form,held=0,water=0,air=0):
    q=M.T.make(b,17)
    q.put(M3Variant=variant,M3Form=form,AreaType=0 if water else 1)
    M.T.invoke(q,'M3Reset')
    q.put(M3Marker=0xb3,M3Previous=0,SavedJoypadBits=held,Player_State=air)
    return q


def app(q,trace):
    protocol=set(range(0x100,0x200))|{0x5115,0x5116,address(q.b,'CurrentBank'),address(q.b,'CurrentBankC')}
    return [(w['address'],w['value']) for w in trace if w['address'] not in protocol]


def main():
    assert not (O/'kick-controls-v1.json').exists()
    stage=json.loads(B.read(O/'source-stage.json'));B.bound(stage)
    old,new=[scoped_load(p/'candidate.nes') for p in [P,J]]
    snap=N.read_bytes();raw=DONOR.read_bytes();own=[]
    for player,timer,held,fresh in itertools.product([0,1],list(range(17))+[255],[0,4,64,68],[0,64,128]):
        bus=ChrRomBus(raw);bus.ram[:0x8000]=snap
        bus.select=0x47;bus.reg[6]=0;bus.reg[7]=38;bus.remap()
        for at,value in {0x119:2,0x11e:2,0x726:player,0x17:held,0x18:fresh,0x517:timer,
                         0xee:14,0x4f3:0}.items():bus.ram[at]=value
        cpu=MPU(memory=bus);bus.cpu=cpu;cpu.pc=0xac82;cpu.p=0x22 if not player else 0x20;cpu.y=7
        for _ in range(100):
            if cpu.pc==0xac79:break
            assert bus[cpu.pc]!=0
            cpu.step()
        else:raise AssertionError('Bounded original kick')
        expected=bus.ram[0x517],bus.ram[0xee],bus.ram[0x4f3],cpu.y
        q=seed(new,2,1)
        for n,v in {'M3Native::Pad_Holding':held,'M3Native::Pad_Input':fresh,
                    'M3Native::Player_TailAttack':timer,'M3Native::Player_Frame':14,
                    'M3Native::Sound_QLevel2':0}.items():q.set(n,v)
        # Start immediately after the already-qualified genuine Soar call.
        c,trace,path,info=M.T.invoke(q,None,y=7,start=(address(new,'MbToadBigFrame')+3,91))
        actual=tuple(q.get(n) for n in ['M3Native::Player_TailAttack','M3Native::Player_Frame',
            'M3Native::Sound_QLevel2'])+(c.y,)
        assert actual==expected,(player,timer,held,fresh,actual,expected)
        own.append(dict(player=player,timer=timer,held=held,fresh=fresh,result=actual))
    foreign=[]
    for variant,form,held,water,air,flags in itertools.product([0,1,3],range(7),[0,64,128,68],
                                                            [0,1],[0,2],[0x30,0x31,0x71,0xf1]):
        results=[]
        for b in [old,new]:
            q=seed(b,variant,form,held,water,air)
            c,tr,path,info=M.T.invoke(q,'M3Movement',a=91,x=3,y=7,p=flags)
            results.append((M.regs(c),app(q,tr),q.m.banks[:],c.processorCycles))
        assert results[0][:3]==results[1][:3],('Foreign movement',variant,form,held,water,air,flags,results)
        foreign.append(dict(variant=variant,form=form,held=held,water=water,air=air,flags=flags,
                            CPU_delta=results[1][3]-results[0][3]))
    calls=[]
    for form,water,air in itertools.product(range(7),[0,1],[0,2]):
        q=seed(new,2,form,64,water,air)
        c,tr,path,info=M.T.invoke(q,'M3Movement')
        called=path.count(M.T.key(new,'MbToadBigFrame'))
        assert bool(called)==(form==1 and not water),(form,water,air,called)
        if called:
            assert q.get('M3Native::Player_TailAttack')==12
            assert q.get('M3Native::Player_Frame')==0x2d
        calls.append(dict(form=form,water=water,air=air,kick_calls=called))
    q=seed(new,2,1,64);sequence=[]
    for frame in range(16):
        M.T.invoke(q,'M3Movement')
        sequence.append(q.get('M3Native::Player_TailAttack'))
    assert sequence==[12,11,10,9,8,7,6]+[0]*9,sequence
    report=dict(passed=True,CPU_only=True,native=False,installed=False,menu_unlocked=False,
        candidate=stage['candidate'],source_kick_cases=len(own),foreign_movement_pairs=len(foreign),
        native_controller_call_cases=calls,held_B_timer_sequence=sequence,
        original_timer_frame_sound_Y=own,foreign=foreign,
        limits=stage['limits'],bindings={str(p):B.sha(p) for p in [Path(__file__),O/'source-stage.json',
            P/'candidate.nes',J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',N,DONOR,
            R/'tools/audit/benj_current_menu_controls_1030_v1.py',
            R/'tools/audit/discover_smb3plus_chr_routes_1030_v1.py',
            R/'tools/audit/benj_mario_donor_trace_1030_v1.py']})
    B.write(O/'kick-controls-v1.json',json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(passed=True,source_kick_cases=len(own),foreign_pairs=len(foreign),
        original_timer_sequence=sequence,candidate=stage['candidate'])))


if __name__=='__main__':main()
