"""Foreign movement equivalence and genuine joined Peach jump/hover sequence."""
from pathlib import Path
import csv
import itertools
import json
import sys

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import smb3plus_kick_host_controls_1031_v1 as K
M,B=K.M,K.B
from link_pit_rygar_sophia_audit_cpu import scoped_load

O=R/'build/smb3plus-peach-float-host-1031-v4';J=O/'joint'
P=R/'build/smb3plus-kick-host-1031-v1/joint'
N=R/'build/smb3plus-peach-float-donor-native-1031-v1/discovery/capture/float-boundaries.csv'


def peach_seed(b,form=0):return K.seed(b,3,form,128)


def jump_sequence(b,form,release=None):
    q=peach_seed(b,form);rows=[];ticks=[]
    for frame in range(130):
        q.put(FrameCounter=frame,SavedJoypadBits=128 if release is None or frame<release else 0)
        c,tr,path,info=M.T.invoke(q,'M3Movement')
        ticks.extend(w['value'] for w in tr if w['address']==M.T.address(b,'MbFloatTimer') and w['opcode']==0xee)
        rows.append(dict(frame=frame,expired=q.get('MbFloatExpired'),timer=q.get('MbFloatTimer'),
            ready=q.get('MbFloatReady'),Y=q.get('Player_Y_Position'),Yhi=q.get('Player_Y_HighPos'),
            VY=q.get('Player_Y_Speed'),air=q.get('Player_State'),
            velocity_callbacks=path.count(M.T.key(b,'MbPeachVelocityEnd'))))
    return q,rows,ticks


def main():
    assert not (O/'movement-controls-v1.json').exists()
    stage=json.loads(B.read(O/'source-stage.json'));B.bound(stage)
    old,new=[scoped_load(p/'candidate.nes') for p in [P,J]]
    foreign=[]
    for variant,form,held,water,air,flags in itertools.product([0,1,2],range(7),[0,64,128,68],
            [0,1],[0,2],[0x30,0x31,0x71,0xf1]):
        results=[]
        for b in [old,new]:
            q=K.seed(b,variant,form,held,water,air)
            c,tr,path,info=M.T.invoke(q,'M3Movement',a=91,x=3,y=7,p=flags)
            results.append((M.regs(c),K.app(q,tr),q.m.banks[:],c.processorCycles))
        assert results[0][:3]==results[1][:3],('Foreign movement',variant,form,held,water,air,flags)
        foreign.append(dict(variant=variant,form=form,held=held,water=water,air=air,flags=flags,
            CPU_delta=results[1][3]-results[0][3]))
    donor=[r for r in csv.DictReader(N.open()) if int(r['bank'])==31 and int(r['pc'])==0xbc4d]
    assert len(donor)==160 and [int(r['E5']) for r in donor]==list(range(160))
    assert len({r['frame'] for r in donor})==80
    sequences=[]
    for form in range(7):
        q,rows,ticks=jump_sequence(new,form)
        if form<4:
            assert ticks==list(range(1,161)),(form,ticks)
            active=[r for r in rows if r['timer']]
            assert len(active)==80 and active[-1]['expired']==1
            assert all(r['velocity_callbacks']==2 for r in active)
            # Landing is an explicit host contact fixture, not a level-clear claim.
            q.put(Player_State=0,SavedJoypadBits=0)
            M.T.invoke(q,'M3Movement')
            assert [q.get(n) for n in ['MbFloatExpired','MbFloatTimer','MbFloatAnchor','MbFloatReady']]==[0,0,0,0]
        else:assert not ticks,(form,ticks)
        sequences.append(dict(form=form,source_timer_ticks=ticks,controller_updates=rows,
            explicit_ground_reset_checked=form<4))
    releases=[]
    for form in range(4):
        q,rows,ticks=jump_sequence(new,form,60)
        at=rows[60];assert at['expired']==1 and at['ready']==1
        assert all(r['timer']==0 for r in rows[61:])
        releases.append(dict(form=form,release_update=60,expired_at_release=at,ticks=ticks))
    d=dict(passed=True,CPU_only=True,native=False,candidate=stage['candidate'],
        foreign_movement_pairs=len(foreign),foreign=foreign,jump_sequences=sequences,
        release_sequences=releases,original_hover_callbacks=160,original_hover_updates=80,
        scope='Actual M3Reset and M3Movement without intercepted callbacks. Terrain landing is an explicit host-state fixture; no natural collision or full-level claim.',
        limits=stage['limits'],bindings={str(p):B.sha(p) for p in [Path(__file__),Path(K.__file__),
            O/'source-stage.json',N,J/'candidate.nes',J/'candidate.dbg',P/'candidate.nes',P/'candidate.dbg']})
    B.write(O/'movement-controls-v1.json',json.dumps(d,indent=2)+'\n')
    print(json.dumps(dict(passed=True,foreign_pairs=len(foreign),jump_forms=len(sequences),
        original_hover_updates=80,candidate=stage['candidate'])))


if __name__=='__main__':main()
