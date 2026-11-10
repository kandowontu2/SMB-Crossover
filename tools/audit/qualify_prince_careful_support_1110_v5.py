"""Zero-output cold, predicate, original-actor and vector checks for15f4."""
import argparse
from collections import Counter
import json

import check_prince_careful_support_1110_v5 as V
import check_prince_climb_funded_irq_1109_v2 as Async

Q,C,N,I=V.Q,V.C,V.N,V.I


def fixture(seed,action=42,mode=255,facing=255,kind='cap'):
    m=Q.Sonic.slim_fork(seed)
    def tile(x,y):
        if y>=208:return 0x54
        if 224<=x<256:
            if kind=='covered' and y==128:return 0x54
            if kind=='cap' or kind=='covered':
                if y>=144:return (0x12 if y==144 else 0x14)+int(x>=240)
            if kind=='shaft' and y>=144:return 0x14
            if kind=='wall' and y>=144:return 0x54
        return 0
    C.Seam.terrain(m,tile)
    m.raw_page(1,3);m.raw_page(2,2)
    N.put(m,CurrentBank=3,CurrentBankC=2,GameEngineSubroutine=8,SelectedCharacter=38,
        OperMode=1,GamePauseStatus=0,Player_X_Position=723&255,Player_PageLoc=723>>8,
        Player_Y_Position=112,Player_Y_HighPos=1,Player_State=0,Player_Y_Speed=0,
        NmiDisable=255,DisableScreenFlag=0,Mirror_PPUMASK=30)
    for at,value in ((0x60f,731),(0x84,145),(0x86,145),(0x89,77),(0x78,703)):
        m.ram[2][at:at+2]=value.to_bytes(2,'little')
    for at,value in ((0x611,65),(0x88,3),(0x8b,65),(0x616,action),(0x618,mode),
                     (0x615,facing),(0x617,15),(0x7a,9),(0x4b1,9),(0x4fe,0)):
        m.ram[2][at]=value
    Q.Sonic.O.clear_logs(m)
    return m


def call(m,pc):return I.invoke(m,3,pc,(83,71,109,0x61))['regs']


def matrix(seed):
    base=fixture(seed);counts=Counter();changed=[]
    for action in range(256):
        for mode in (0,1,255):
            for facing in (0,255):
                a,b=(Q.Sonic.slim_fork(base) for _ in range(2))
                for m in (a,b):m.ram[2][0x616]=action;m.ram[2][0x618]=mode;m.ram[2][0x615]=facing
                old,new=call(a,V.OLD),call(b,V.ORIGIN)
                difference=old!=new
                should_change=action==42 and mode in (1,255) and facing==255
                assert difference==should_change,(action,mode,facing,old,new)
                query_reached=action==42 and mode in (1,255)
                if query_reached:
                    assert [i for i,(x,y) in enumerate(zip(a.ram[2],b.ram[2])) if x!=y]==([0x7f] if difference else [])
                    assert all(x==y or i in {0x134d,0x134e,0x1369,0x136a,0x136b,0x136c,0x136d}
                        for i,(x,y) in enumerate(zip(a.ram[3],b.ram[3])))
                    assert bytes(a.ram[2][0x606:0x800])==bytes(b.ram[2][0x606:0x800])
                    assert bytes(a.ram[2][0x84:0x88])==bytes(b.ram[2][0x84:0x88])
                if difference:
                    assert old[0]==0 and new[0]==1,(action,mode,facing,old,new)
                    assert old[1:3]==new[1:3] and old[4:]==new[4:] and (old[3]^new[3])==2,(old,new)
                    assert b.ram[2][0x7f]==144 and a.ram[2][0x7f]==145
                    changed.append(dict(action=action,mode=mode,facing=facing,old=old,new=new))
                elif not query_reached:
                    assert a.ram==b.ram and old==new
                assert bytes(a[3:11])==bytes(b[3:11]) and a.rawtags==b.rawtags
                counts['action_mode_facing_pairs']+=1
    negatives=[]
    def check(name,m):
        a,b=Q.Sonic.slim_fork(m),Q.Sonic.slim_fork(m)
        original_actor=bytes(b.ram[2][0x606:0x800]);oldfoot=bytes(b.ram[2][0x86:0x88])
        old,new=call(a,V.OLD),call(b,V.ORIGIN)
        assert old==new and old[0]==0,(name,old,new)
        assert bytes(a.ram[2])==bytes(b.ram[2])
        assert all(x==y or i in {0x134d,0x134e,0x1369,0x136a,0x136b,0x136c,0x136d}
            for i,(x,y) in enumerate(zip(a.ram[3],b.ram[3]))),name
        assert bytes(b.ram[2][0x606:0x800])==original_actor and bytes(b.ram[2][0x86:0x88])==oldfoot,name
        negatives.append(dict(name=name,old=old,new=new))
    for kind in ('empty','covered','shaft','wall'):check(kind,fixture(seed,kind=kind))
    for state in (1,2,3):
        m=fixture(seed);N.put(m,Player_State=state);check('native-air-state-'+str(state),m)
    for high in (0,2):
        m=fixture(seed);N.put(m,Player_Y_HighPos=high);check('native-Y-page-'+str(high),m)
    for y in (111,113,224):
        m=fixture(seed);N.put(m,Player_Y_Position=y);check('native-Y-mismatch-'+str(y),m)
    m=fixture(seed);m.ram[2][0x86:0x88]=(146).to_bytes(2,'little');check('previous-foot-moved',m)
    m=fixture(seed);m.ram[2][0x611]=66;check('current-foot-moved',m)
    m=fixture(seed);m.ram[2][0x8a]=1;m.ram[2][0x87]=1;check('source-foot-page',m)
    m=fixture(seed,facing=0);check('leading-foot-before-cap',m)
    m=fixture(seed);N.put(m,Player_X_Position=1105&255,Player_PageLoc=1105>>8);check('leading-foot-native-gap',m)
    for mode in (2,3,4,5,6,7,8,15):check('scripted-air-mode-'+str(mode),fixture(seed,mode=mode))
    for area in (0,1,2,3):
        m=fixture(seed,kind='empty');N.put(m,AreaType=area);check('empty-in-area-'+str(area),m)
    return dict(counts=dict(counts),only_new_results=changed,negative_cases=negatives,
        original_motor_actor_OldFoot_unchanged=True)


def vectors(seed):
    rows=[]
    for mode in (1,255):
        m=fixture(seed,mode=mode)
        rows.append(Async.stress('new careful support mode'+str(mode),m,
            lambda q:call(q,V.ORIGIN),[(2,V.ORIGIN,V.ORIGIN+132),(3,0xb310,0xb369)]))
    m=fixture(seed,kind='empty')
    rows.append(Async.stress('new careful empty geometry',m,
        lambda q:call(q,V.ORIGIN),[(2,V.ORIGIN,V.ORIGIN+132),(3,0xb310,0xb369)]))
    return rows


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for option in ('matrix','vectors','poses','lifecycle','owners','readback'):parser.add_argument('--'+option,action='store_true')
    args=parser.parse_args()
    parent,trial,chunks,layout,program,packet,rows=V.proposal()
    seed,cold=Q.actual_cold(trial,chunks,layout,program)
    Q.Sonic.O.clear_logs(seed)
    print('CAREFUL_COLD '+json.dumps(dict(SHA256=layout['in_memory_SHA256'],layout=layout,cold=cold),separators=(',',':')),flush=True)
    if args.matrix:print('CAREFUL_MATRIX '+json.dumps(matrix(seed),separators=(',',':')),flush=True)
    if args.vectors:print('CAREFUL_VECTORS '+json.dumps(vectors(seed),separators=(',',':')),flush=True)
    if args.poses:print('CAREFUL_POSES '+json.dumps(Q.poses(parent,trial,seed),separators=(',',':')),flush=True)
    if args.lifecycle:print('CAREFUL_LIFECYCLE '+json.dumps(Q.landing_and_lifecycle(trial)[0],separators=(',',':')),flush=True)
    if args.owners:print('CAREFUL_OWNERS '+json.dumps(Q.owner_regressions(parent,trial,chunks,layout,program,packet,rows),separators=(',',':')),flush=True)
    if args.readback:print('CAREFUL_READBACK '+json.dumps(Q.append_readback_faults(trial,chunks,layout,program),separators=(',',':')),flush=True)


if __name__=='__main__':main()
