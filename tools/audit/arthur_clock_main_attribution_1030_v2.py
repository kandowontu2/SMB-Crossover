"""Attribute genuine current Arthur Main cost without changing source clocks.

Flat source-control scene, six complete Main updates, actual serial-input NMI
mailbox acquisition. This is diagnostic instruction accounting, not native
timing or proof of a performance improvement.
"""
from pathlib import Path
import collections,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import arthur_physical_clock_context_v2 as V
from arthur_physical_clock_controls_v2 import fresh,electrical_nmi,static
A=V.A;B=V.B;O=V.O;N=V.N


def run(b):
    q=fresh(b);payload=static(q);g=V.C.L.L.load_nmi(b)
    ranges=[]
    for s in b['segs'].values():
        if 'ooffs'not in s or not int(s['size'],0):continue
        ranges.append(((int(s['ooffs'],0)-16)//8192,int(s['start'],0),
                       int(s['start'],0)+int(s['size'],0),s['name'].strip('"')))
    names=['ArDispatch','ArHostMovement','ArHostGraphics','ArHostDraw','ArHostEnsure',
           'ArHostAfterTerrain','ArHostShotContacts','ArStep','ArHostPoint',
           'SamusFreezeDrawAll','DrawAllMetasprites','PlayerBGCollision',
           'AudioUpdate','NrBody','ArHostDrawAll','ArClockPollC70','CrossoverGraphicsBank',
           'MetaspriteRenderLoop','NativeGoombaRender','X5BounceUiDispatch',
           'NrFreshGameInit','ArHostNmiClock','ArHostRenderChunk','FarCallCommon']
    watch={A.point(b,n):n for n in names if n in b['syms']}
    cls=A.M.NesMPU;original=cls.step
    segments=collections.Counter();costs=collections.defaultdict(list);active=[];updates=[]
    enabled=False
    def step(c):
        if not enabled or c.memory is not q.m:return original(c)
        for e in active[:]:
            if c.sp==((e['sp']+2)&255)and c.pc==e['return_PC']:
                costs[e['name']].append(c.processorCycles-e['CPU']);active.remove(e)
        pc=c.pc;bank=q.m.banks[(pc-0x8000)//8192]if pc>=0x8000 else -1
        name=watch.get((bank,pc))
        if name:
            ret=q.m[0x100+((c.sp+1)&255)]|q.m[0x100+((c.sp+2)&255)]<<8
            key=(name,c.sp,(ret+1)&65535)
            if not any((e['name'],e['sp'],e['return_PC'])==key for e in active):
                active.append(dict(name=name,sp=c.sp,CPU=c.processorCycles,return_PC=(ret+1)&65535))
        owner=next((n for bk,lo,hi,n in ranges if bk==bank and lo<=pc<hi),
                   'SMC/RAM'if pc<0x8000 else 'UNATTRIBUTED')
        before=c.processorCycles;value=original(c);segments[owner]+=c.processorCycles-before
        return value
    cls.step=step
    try:
        for age in range(1,19):
            normal=(age-1)%3==0
            keys=1|(128 if 7<=age<10 or 16<=age<19 else 0)
            q.put(NmiDisable=0 if normal else 255,FamilyMainCommit=0 if normal else 1,
                  VRAM_Buffer_AddrCtrl=0,VRAM_Buffer1_Offset=0)
            electrical_nmi(q,g,keys)
            if not normal:continue
            q.put(NmiDisable=255,FamilyMainCommit=1,VRAM_Buffer_AddrCtrl=0,VRAM_Buffer1_Offset=0)
            enabled=True
            c,tr,mn,ann,events=A.M.run_linked(q,'GameLoop')
            enabled=False
            # The top-level trampoline returns outside its final RTS step;
            # finish any named leaf that ends exactly at that real return.
            for e in active[:]:
                if c.sp==((e['sp']+2)&255)and c.pc==e['return_PC']:
                    costs[e['name']].append(c.processorCycles-e['CPU']);active.remove(e)
            assert not active,('Unfinished profiling frame',[(e['name'],e['sp'])for e in active])
            assert static(q)==payload
            assert tr.count(A.point(b,'ArStep'))==1
            updates.append(dict(age=age,CPU=c.processorCycles,minimum_SP=mn))
    finally:cls.step=original
    assert len(updates)==6
    total=sum(r['CPU']for r in updates)
    assert sum(segments.values())==total,(sum(segments.values()),total)
    return dict(passed=True,updates=updates,complete_Main_CPU=dict(min=min(r['CPU']for r in updates),
        max=max(r['CPU']for r in updates),mean=total/len(updates)),
        exclusive_instruction_segments=dict(segments.most_common()),
        inclusive_routine_costs={n:dict(calls=len(v),total=sum(v),min=min(v),max=max(v),mean=sum(v)/len(v))
            for n,v in sorted(costs.items(),key=lambda x:-sum(x[1]))},
        source_due_pad_and_physics_not_supplied_by_profiler=True,
        exclusive_costs_sum_exactly_to_complete_Main=True,
        limits=['Six flat-scene linked CPU updates, not the earlier native controller route.',
                'Named routine costs are inclusive and overlap; segment totals are exclusive.',
                'No optimization or60Hz/native performance qualification claimed.'])


def main():
    out=O/'Main-cost-attribution-1030-v2.json';assert not out.exists()
    proof=dict(passed=False,native=False,admitted=False)
    try:
        h=json.loads((O/'handoff.json').read_text())
        for p,v in h['bindings'].items():assert B.sha(p)==v,p
        proof['checks']=run(A.scoped_load(N/'candidate.nes'));proof['passed']=True
    except Exception as e:proof.update(error=repr(e),traceback=traceback.format_exc())
    proof['bindings']={str(p.resolve()):B.sha(p)for p in[Path(__file__),Path(V.__file__),
        R/'tools/audit/arthur_physical_clock_controls_v2.py',O/'handoff.json',N/'candidate.nes',N/'candidate.dbg']}
    proof['predecessor_negative']=str(O/'Main-cost-attribution-negative-1030-v1.json')
    proof['profiler_correction']='HuCommon is not a standalone JSR-entry contract; remove its invalid inclusive call-frame guess. Its instructions remain in exact exclusive segment accounting.'
    target=out if proof['passed']else O/'Main-cost-attribution-negative-1030-v2.json'
    assert not target.exists();target.write_text(json.dumps(proof,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(passed=proof['passed'],error=proof.get('error'),path=str(target),
        costs=proof.get('checks',{}).get('complete_Main_CPU'))),flush=True)
    assert proof['passed']


if __name__=='__main__':main()
