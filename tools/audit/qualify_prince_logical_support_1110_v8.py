"""Exact in-memory logical-sole packet qualification; no output files."""
import argparse
import inspect
import json
from unittest.mock import patch

import check_prince_logical_support_1110_v8 as V
import qualify_prince_careful_support_1110_v5 as Legacy
import check_prince_climb_funded_irq_1109_v2 as Async

Q,C,N,I=V.Q,V.C,V.N,V.I


def legacy_matrix(seed):
    old_support,_=V.V.assemble((V.V.R/'tools/reference/prince_careful_support_1110_v5.s').read_text(),0xd6d1)
    count=0
    for action in range(256):
        for mode in (0,1,255):
            for facing in (0,255):
                b=Legacy.fixture(seed,action=action,mode=mode,facing=facing)
                a=Q.Sonic.slim_fork(b);a.ram[2][0x16d1:0x1756]=old_support+b'\0'
                results=[I.invoke(m,3,0xd6d1,(83,71,109,0x61))['regs'] for m in (a,b)]
                assert results[0]==results[1],(action,mode,facing,results)
                assert a.ram[2][:0x16d1]==b.ram[2][:0x16d1] and a.ram[2][0x1756:]==b.ram[2][0x1756:],(action,mode,facing)
                assert a.ram[3]==b.ram[3],(action,mode,facing)
                count+=1
    return dict(exact_frozen132_pairs=count,all256_actions=True,original1_and_original42_results_preserved=True)


def vectors(seed,actual):
    watch=[(2,0xd6d1,0xd756),(3,0xbd4b,0xbda2),(3,0xb310,0xb369)]
    rows=[]
    def run(m,pc):
        regs=I.invoke(m,3,pc,(83,71,109,0x61))['regs']
        # B is not a 6502 processor latch. Real IRQ's stacked copy clears it;
        # py65 retains that virtual value after RTI. Preserve all real flags.
        regs[3]&=0xef
        return regs
    for name,m,pc in (('actual622 logical careful cap',actual,0xd6d1),
        ('legacy42 physical cap',Legacy.fixture(seed),0xd6d1),
        ('actual source pose123 projection',actual,0xbd06)):
        Q.Sonic.O.clear_logs(m)
        rows.append(Async.stress(name,m,lambda q:run(q,pc),watch))
    return rows


def readback(result):
    # The new footer274 crosses SrcLo's256-byte range. The actual loader
    # advances SrcHi through0C..0F; compare the complete PPU page offset.
    text=inspect.getsource(Q.append_readback_faults)
    old="m.ram[2][0x224]==14 and m.ram[2][0x225]==lo"
    new="m.ram[2][0x224]==14 and (m.ram[2][0x225]+256*(m.ram[2][0x226]-0x0c))==lo"
    assert text.count(old)==1
    namespace=dict(Q.__dict__);exec(text.replace(old,new),namespace)
    _,trial,chunks,layout,program,_,_=result
    return namespace['append_readback_faults'](trial,chunks,layout,program)


def cold_vectors(result):
    import check_prince_floor_vectors_1110 as Frozen
    text=inspect.getsource(Frozen.cold_vectors)
    old="edges.index(m.ram[2][0x225]) if m.ram[2][0x225] in edges else 4"
    position="(m.ram[2][0x225]+256*(m.ram[2][0x226]-0x0c))"
    new=f"edges.index({position}) if {position} in edges else 4"
    assert text.count(old)==1
    namespace=dict(Frozen.__dict__);exec(text.replace(old,new),namespace)
    _,trial,chunks,layout,_,_,_=result
    return namespace['cold_vectors'](trial,chunks,layout)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for flag in ('regressions','route','vectors','owners','cold-vectors','readback'):p.add_argument('--'+flag,action='store_true')
    args=p.parse_args();result=V.proposal();parent,trial,chunks,layout,program,packet,rows=result
    seed,cold=Q.actual_cold(trial,chunks,layout,program)
    print('LOGICAL_COLD '+json.dumps(dict(layout=layout,cold=cold),separators=(',',':')),flush=True)
    if args.regressions:
        print('LOGICAL_LEGACY '+json.dumps(legacy_matrix(seed),separators=(',',':')),flush=True)
        print('LOGICAL_POSES '+json.dumps(Q.poses(parent,trial,seed),separators=(',',':')),flush=True)
        print('LOGICAL_LIFECYCLE '+json.dumps(Q.landing_and_lifecycle(trial)[0],separators=(',',':')),flush=True)
    if args.route or args.vectors:
        trace,actual=V.run_trace(result,changed=False)
        route=trace['route']
        assert route['outcome']=='first-gap-clear' and route['actual_fourth_cap']
        assert route['terminal']['hp']==4 and route['terminal']['lives']==2
        assert route['HP_debits']==[dict(tick=312,x=846,before=5,after=4)]
        logical=[r for r in trace['rows'] if r['kind']=='logical']
        assert [r['tick'] for r in logical]==[622,626]
        for r in logical:
            assert (r['previous_sole'],r['previous_high'],r['foot'],r['delta'],r['baseline'])==(147,0,147,5,145)
            assert r['roomrows']==r['row']==r['currentrow']==r['offset']==0 and r['phase_call']==4
            capture,=[v for v in trace['rows'] if v['kind']=='accepted capture' and v['tick']==r['tick']]
            assert capture['foot']==r['previous_sole'] and capture['delta']==r['delta']
        print('LOGICAL_ACTUAL_ROUTE '+json.dumps(dict(
            SHA256=layout['in_memory_SHA256'],outcome=route['outcome'],events=route['events'],
            HP_debits=route['HP_debits'],terminal=route['terminal'],pads=route['pads'],
            logical_support=logical,first_full_cap=next(r for r in route['events'] if r['event'].endswith(' -> fourth-cap')),
            scope='Translated CPU scene, actual native AreaParser/BG/actors/ordinary NMI; no Mesen or fullstage claim',
            helpers_added=0,outputs_written=0),separators=(',',':')),flush=True)
        print('LOGICAL_NEGATIVES '+json.dumps(V.matrix(actual),separators=(',',':')),flush=True)
        if args.vectors:print('LOGICAL_ACTUAL_VECTORS '+json.dumps(vectors(seed,actual),separators=(',',':')),flush=True)
    if args.owners:print('LOGICAL_OWNERS '+json.dumps(Q.owner_regressions(parent,trial,chunks,layout,program,packet,rows),separators=(',',':')),flush=True)
    if args.readback:print('LOGICAL_READBACK '+json.dumps(readback(result),separators=(',',':')),flush=True)
    if args.cold_vectors:print('LOGICAL_COLD_VECTORS '+json.dumps(cold_vectors(result),separators=(',',':')),flush=True)


if __name__=='__main__':main()
