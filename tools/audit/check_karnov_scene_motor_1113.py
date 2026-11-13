"""Same-life Karnov constructor reset, retained equipment and real public ABI."""
import argparse
from collections import Counter
import json

import compose_karnov_scene_motor_1113 as Compose
import check_karnov_bomb_1112 as Bomb
import check_karnov_natural_bomb_1113 as Natural

M=Bomb.M


def prepared(seed,selector=8,facing=1):
    m=M.fork(seed)
    M.put(m,AreaAddrsLOffset=0,WorldNumber=0,PlayerFacingDir=facing,
        DisableScreenFlag=1,Mirror_PPUMASK=0,NmiDisable=255,FamilyMainCommit=1)
    for offset,value in {0x62:selector,0x65:2,0x66:0,0x67:19,0x68:0,0x6a:23,0x6b:41,
        0x8e:1,0x8f:3,0xbb:5,0xbd:7,0x300:71,0x400:29,0x7fd:67,0x860:2}.items():m.ram[2][offset]=value
    return m


def kept(m):
    return tuple(m.ram[2][a]for a in (0x65,0x68,0x8e,0x8f,0xbb,0xbd,0x300,0x400,0x7fd,0x860))


def scenes(seed,full=True):
    count=0;returns=set()
    for facing in (1,2):
        for selector in range(256)if full else (8,9):
            m=prepared(seed,selector,facing);before=kept(m)
            result=M.invoke(m,'InitScreen',a=85,x=7,y=91,p=0x21)
            assert m.ram[2][0x62]==(0 if facing==1 else 128),(facing,selector,m.ram[2][0x62])
            assert all(m.ram[2][a]==0 for a in (0x66,0x67,0x6a,0x6b))
            assert kept(m)==before and m.ram[2][0x810]==0xa7
            returns.add(tuple(result[k]for k in ('A','X','Y','P')));count+=1
    return dict(actual_InitScreen_cases=count,all_prior_selectors=full,facings=[1,2],
        expired_original_jump_selectors=[8,9],native_AXYP_returns=[list(r)for r in sorted(returns)],
        shot_health_equipment_stock_cycle_preserved=True)


def foreign(parent,candidate):
    rows=[]
    for owner in (0,7,10,28,32,33,35,36,38,39,42):
        outputs=[]
        for seed in (parent,candidate):
            m=prepared(seed);M.put(m,SelectedCharacter=owner,FmAlts=0)
            before=[bytes(b)for b in m.ram]
            result=M.invoke(m,'HuFresh',a=85,x=7,y=91,p=0x21)
            # Report actual writes, rather than mistaking the intentionally
            # different preloaded Karnov bytes for foreign changes.
            changes=[(bank,i,a,b)for bank,(old,new)in enumerate(zip(before,m.ram))
                for i,(a,b)in enumerate(zip(old,new))if a!=b]
            outputs.append((tuple(result[k]for k in ('A','X','Y','P')),changes,m.rawtags[:]))
        assert outputs[0]==outputs[1],owner
        rows.append(owner)
    return dict(actual_public_HuFresh_foreign_owners=rows,identical_AXYP_write_deltas_and_maps=True)


def interrupts(seed):
    native=M.NesMPU;points=set();counts=Counter();minimum=255
    class Probe(native):
        def step(self):
            nonlocal minimum
            if self.memory.rawtags[1]==3 and 0xafff<=self.pc<0xb128:
                point=(self.pc,self.sp,self.p&4)
                if point not in points:
                    points.add(point)
                    for kind in ('IRQ','lagNMI'):
                        if kind=='IRQ'and self.p&4:continue
                        m=M.fork(self.memory);cpu=native(memory=m,pc=self.pc)
                        for key in ('a','x','y','p','sp'):setattr(cpu,key,getattr(self,key))
                        try:minimum=min(minimum,Bomb.Cpu.inject(cpu,native,kind))
                        except Exception as e:raise AssertionError((kind,hex(self.pc),self.sp))from e
                        counts[kind]+=1
            return native.step(self)
    M.NesMPU=Probe
    try:
        for facing in (1,2):
            m=prepared(seed,8,facing);M.invoke(m,'InitScreen',p=0x21)
        m=prepared(seed,9,1);m.ram[2][0x810]=0;M.invoke(m,'InitScreen',p=0x21)
    finally:M.NesMPU=native
    assert counts['IRQ']>0 and counts['lagNMI']>0 and minimum>=128
    return dict(cuts=dict(counts),instruction_SP_points=len(points),minimum_SP=minimum,
        includes_original_same_life_and_fresh_constructor=True)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--basic',action='store_true')
    parser.add_argument('--route',action='store_true');parser.add_argument('--stop-after',type=int,default=3)
    parser.add_argument('--limit',type=int,default=7500);args=parser.parse_args()
    raw=Compose.Bomb.NIGHTLY.read_bytes()
    at=Compose.ACTOR+Compose.PC-0xa000
    if raw[at:at+len(Compose.OLD)]==Compose.code():raw=Compose.inverse(raw)
    candidate,report=Compose.transform(raw)
    assert Compose.inverse(candidate)==raw
    seed,cold=Bomb.cold(candidate,bytes.fromhex(report['cookie']))
    print('KARNOV_SCENE_MOTOR_BASIC '+json.dumps(dict(layout=report,cold=cold,
        scenes=scenes(seed,not args.basic)),separators=(',',':')),flush=True)
    if not args.basic:
        parent,_=Bomb.cold(raw,Compose.OLD_COOKIE)
        negative=prepared(parent,8,1);M.invoke(negative,'InitScreen',p=0x21)
        assert negative.ram[2][0x62]==8 and negative.ram[2][0x66]==0
        print('KARNOV_SCENE_MOTOR_CONTROLS '+json.dumps(dict(
            parent_reproduces_stale_jump_selector8_with_expired_timer0=True,
            progression=Natural.progression(seed),foreign=foreign(parent,seed)),separators=(',',':')),flush=True)
        print('KARNOV_SCENE_MOTOR_READBACK '+json.dumps(Bomb.cold(candidate,bytes.fromhex(report['cookie']),
            readback=(3,0x10d7,0x29)),separators=(',',':')),flush=True)
        print('KARNOV_SCENE_MOTOR_INTERRUPTS '+json.dumps(interrupts(seed),separators=(',',':')),flush=True)
    if args.route:
        bundle=Natural.W.Symbols.bundle();bundle['raw']=candidate
        opening,model=Natural.C.cold(bundle,dict(name='KARNOV',slot=7,cycle=1,raw=34))
        result=Natural.route(model,candidate,args.limit,args.stop_after)
        print('KARNOV_SCENE_MOTOR_NATURAL '+json.dumps(result,separators=(',',':')),flush=True)
        assert result['passed']


if __name__=='__main__':main()
