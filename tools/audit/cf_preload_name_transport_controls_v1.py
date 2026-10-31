"""Finite exact8f0a B020 gate/resolver ABI proof, no BT gameplay admission."""
from pathlib import Path
import collections,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import battletoads_current_loader_controls_v1 as L
H=L.H;address=L.address
O=R/'build/cf-preload-name-transport-controls-v1'
J=R/'build/cf-preload-name-source-v1/joint';P=R/'build/cf-cold-warm-palette-source-v1/joint'


def startrow(m,slot,p):
    c=H.start(m,'BtServiceVeneers',p=p)
    pc=address(m.bundle,'BtServiceVeneers')+slot*3
    m[address(m.bundle,'FarcallJmpTarget_SMC')+1]=pc&255
    m[address(m.bundle,'FarcallJmpTarget_SMC')+2]=pc>>8
    return c


def finish(m,c,watch=None):
    c,low=H.finish(m,c,watch)
    assert c.sp==224
    assert m.rawtags[1]==H.get(m,'CurrentBank') and m.rawtags[2]==H.get(m,'CurrentBankC')
    app=[(a,v)for a,v in m.writes if a<256 or 0x200<=a<0x5100 or 0x5200<=a<0x8000]
    return c,low,((c.a,c.x,c.y,c.p,c.sp),[bytes(x)for x in m.ram],m.ram_writes,app)


def main():
    O.mkdir(exist_ok=False);q=dict(passed=False,native=False,checks={},vectors=[])
    try:
        assert L.sha(J/'candidate.nes')=='38a6259ca3abacccc10b8adb3b256f94a72f90307d44fb5ed5afe15114c372cd'
        assert (P/'bt/cache.bin').read_bytes()==(J/'bt/cache.bin').read_bytes()
        bundles=[H.C.qualified(x/'candidate.nes')for x in[P,J]]
        seeds=[]
        for b in bundles:
            m=L.make(b);c,_=L.call(m,'BtLoad');assert c.p&1;seeds.append(m)
        for n in ['BtServiceVeneers','BtServiceUnavailable','BtRouter']:
            assert address(bundles[0],n)==address(bundles[1],n)
        counts=collections.Counter();deltas=[];mins=[]
        for valid,slot in itertools.product([0,1],range(37)):
            changed=not valid and slot==18
            pair=[L.fork(seeds[1]),L.fork(seeds[1])]if changed else[L.fork(s)for s in seeds]
            if not valid:
                for m in pair:m.ram[3][0x1fe0]=0
            for flag in range(64):
                results=[];cycles=[]
                for side,m in enumerate(pair):
                    m.writes.clear();m.ram_writes.clear()
                    c=H.start(m,{18:'FmQueueName'}[slot],p=L.flags(flag))if changed and side==0 else startrow(m,slot,L.flags(flag))
                    c,lo,result=finish(m,c);results.append(result);cycles.append(c.processorCycles);mins.append(lo)
                if changed:
                    # Exact full-cookie authentication maps C3 and restores it
                    # before executing the native callback. These two named
                    # bank-shadow writes are transport, not callback data.
                    shadow=address(pair[1].bundle,'CurrentBankC')
                    assert results[1][3][:2]==[(shadow,3),(shadow,seeds[1].rawtags[2])],results[1][3]
                    observed=list(results[1]);observed[3]=results[1][3][2:]
                    assert results[0]==tuple(observed),('native callback after exact transport prefix',slot,flag,results[0][0],results[1][0])
                else:
                    assert results[0]==results[1],('actual old/new BT output/writes',valid,slot,flag,results[0][0],results[1][0])
                counts['all_BT_rows']+=1
                counts['intentional_native_fallback_pairs'if changed else'unchanged_old_new_BT_pairs']+=1
                if not changed:deltas.append(cycles[1]-cycles[0])
        q['inherited_review_negative']='Invalid15 observer included exact CurrentBankC3->prior shadow writes as native application writes. V2 requires that exact two-write transport prefix, then compares every native write without reordering; allRAM and returnedAXYP/SP remain exact. No source change.'
        q['checks']['BT_allflags_rows']=dict(counts,all37rows_all64flags_valid_and_invalid=True,
            unchanged_cache_bytes=True,actual_AXYP_SP_allRAM_ordered_application_writes_exact=True,
            actual_genuine_FmQueueName_for_invalid18=True,
            unchanged_BT_CPU_delta=[min(deltas),max(deltas)],minimum_SP=min(mins))
        print('BT rows PASS',dict(counts),flush=True)
        poison=0
        for byte in range(16):
            m=L.fork(seeds[1]);m.ram[3][0x1fe0+byte]^=1;before=[bytes(x)for x in m.ram]
            for flag in range(64):
                c,_=L.call(m,'BwBtResolve',a=0,p=L.flags(flag))
                assert not c.p&1
                assert [bytes(x)for x in m.ram]==before;poison+=1
        q['checks']['cookie_poison']=dict(pairs=poison,full16bytes_all64flags_reject=True)
        foreign=0
        b=bundles[1];resolver=(address(b,'BwBtResolve'),((L.location(b,'BwBtResolve')-16)//8192)|128)
        for raw in range(256):
            if raw in[27,31,33]:continue
            m=L.fork(seeds[1]);H.put(m,SelectedCharacter=raw);before=[bytes(x)for x in m.ram]
            for slot,flag in itertools.product([15,18,19],range(64)):
                m.writes.clear();m.ram_writes.clear();seen=[]
                def watch(mem,c,i):
                    if c.pc==resolver[0] and mem.rawtags[(c.pc-0x8000)//8192]==resolver[1]:seen.append(i)
                c,lo,result=finish(m,startrow(m,slot,L.flags(flag)),watch)
                assert not seen,('foreign entered resolver',raw,slot,flag)
                assert (c.a,c.x,c.y,c.p,c.sp)==(85,7,91,L.flags(flag)&0x7c,224)
                assert not m.ram_writes and not result[3] and [bytes(x)for x in m.ram]==before
                assert not any(a==0x5116 for a,v in m.writes)
                foreign+=1
        q['checks']['foreign_direct_table']=dict(pairs=foreign,raw_values=253,all64flags_15_18_19=True,
            never_enters_resolver_or_native_fallback=True,AXYP_SP_exact_Cclear=True,
            application_and_allRAM_unchanged=True,no_C_mapping=True)
        print('foreign gate PASS',foreign,flush=True)
        admitted=0
        for raw,slot in itertools.product([27,31,33],[0,15,18,19]):
            m=L.fork(seeds[1]);H.put(m,SelectedCharacter=raw);m.ram[3][0x1fe0]=0
            for flag in range(64):
                seen=[]
                def watch(mem,c,i):
                    if c.pc==resolver[0] and mem.rawtags[(c.pc-0x8000)//8192]==resolver[1]:seen.append(i)
                finish(m,startrow(m,slot,L.flags(flag)),watch)
                assert len(seen)==1,(raw,slot,flag,seen);admitted+=1
        q['checks']['admitted_gate']=dict(pairs=admitted,owners=[27,31,33],resolver_once=True)
        # Finite real-vector closure of the new gate, moved reject and native
        # fallback branch. Stable title audio contexts for ordinary/paused NMI;
        # actual source updates/cold copies are outside this transport proof.
        vectorpaths=[]
        for raw,valid,slot in[(33,1,0),(33,0,15),(33,0,18),(33,0,19),(31,0,18),(0,0,18)]:
            seed=L.fork(seeds[1]);H.put(seed,SelectedCharacter=raw,OperMode=0)
            if not valid:seed.ram[3][0x1fe0]=0
            cuts=[];seen=set()
            router=address(b,'BtRouter');fallback=address(b,'BwResolveColdNative')
            def trace(mem,c,i):
                tag=mem.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
                own=(tag==215 and router<=c.pc<0xb100)or(tag==195 and fallback<=c.pc<fallback+19)
                key=(tag,c.pc)
                if own and key not in seen:seen.add(key);cuts.append((i,c.pc,bool(c.p&4)))
            m=L.fork(seed);finish(m,startrow(m,slot,0x30),trace)
            for step,pc,masked in cuts:
                for kind,lag,pause in[('NMI',0,0),('NMI',255,0),('NMI',0,1)]+([]if masked else[('IRQ',255,0)]):
                    m=L.fork(seed);H.put(m,NmiDisable=lag,GamePauseStatus=pause);proof=[]
                    def inject(mm,c,i):
                        if i==step:
                            assert c.pc==pc
                            proof.append(L.V.interrupt(mm,c,kind))
                    finish(m,startrow(m,slot,0x30),inject);assert len(proof)==1
                    q['vectors'].append(dict(owner=raw,valid=valid,slot=slot,PC=pc,lag=lag,pause=pause,**proof[0]))
            vectorpaths.append(dict(owner=raw,valid=valid,slot=slot,instruction_cuts=len(cuts)))
        q['checks']['real_vectors']=dict(cases=len(q['vectors']),paths=vectorpaths,
            normal_lag_paused_NMI_and_legal_IRQ=True,all33SMC_livepage1_AXYP_SP_rawmaps_exact=True)
        q.update(passed=True,scope='Actual emitted19B fallback/name and unchanged B020 gate:4736allflagBTrows; changedinvalid18compares genuineFmQueueName after exactC3authprefix; original15/19unchanged. All253foreignraw/fullflags15/18/19reject before resolver. NoBTv7orCFreadiness/native.')
    except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
    files=[Path(__file__),R/'tools/audit/battletoads_linked_owner_gate_controls_v2.py',R/'build/battletoads-linked-owner-gate-controls-v2/controls.json',R/'tools/audit/battletoads_linked_owner_gate_controls_v1.py',R/'build/battletoads-linked-owner-gate-controls-v1/controls.json',Path(L.__file__),Path(H.__file__),Path(L.V.__file__),
        J/'candidate.nes',J/'candidate.dbg',J/'bt/router.s',J/'bowser/router.s',J/'bt/cache.bin',J/'bt/cookie.bin',
        P/'candidate.nes',P/'candidate.dbg',P/'bt/router.s',P/'bt/cache.bin',
        R/'build/battletoads-shared-owner-gate-review-v1/review.json']
    q['bindings']={str(p.resolve()):L.sha(p)for p in files}
    (O/'controls.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:v for k,v in q.items()if k not in['vectors','bindings','traceback']}),flush=True)
    assert q['passed'],q.get('error')


if __name__=='__main__':main()
