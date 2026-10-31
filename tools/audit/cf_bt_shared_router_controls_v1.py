"""Independent exact4aacf shared resolver/BT-row ABI, no Bowser graphics claim."""
from pathlib import Path
import itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import battletoads_current_loader_controls_v1 as L
H=L.H;address=L.address
O=R/'build/cf-bt-shared-router-controls-v1'
J=R/'build/cf-bt-shared-transport-v3/joint';P=R/'build/bowser-playable-jump-v1/joint'

def startrow(m,slot,p):
    c=H.start(m,'BtServiceVeneers',p=p);pc=address(m.bundle,'BtServiceVeneers')+slot*3
    m[address(m.bundle,'FarcallJmpTarget_SMC')+1]=pc&255;m[address(m.bundle,'FarcallJmpTarget_SMC')+2]=pc>>8
    return c

def main():
    O.mkdir(exist_ok=False);q=dict(passed=False,native=False,rows=[],vectors=[])
    try:
        assert L.sha(J/'candidate.nes')=='a7da1094265701d69fc52588f495eddb09e3c1ff7d76e55e62f5bdfdf45d501d'
        assert (J/'bt/cache.bin').read_bytes()==(P/'bt/cache.bin').read_bytes()
        bundles=[H.C.qualified(x/'candidate.nes')for x in[P,J]];seeds=[]
        for b in bundles:
            m=L.make(b);c,_=L.call(m,'BtLoad');assert c.p&1;seeds.append(m)
        for valid,slot,flags in itertools.product([0,1],range(37),range(64)):
            pair=[]
            for seed in seeds:
                m=L.fork(seed)
                if not valid:m.ram[3][0x1fe0]=0
                m.writes.clear();m.ram_writes.clear()
                c=startrow(m,slot,L.flags(flags));c,low=H.finish(m,c)
                assert c.sp==224 and m.rawtags==seed.rawtags
                assert H.get(m,'CurrentBank')==seed.rawtags[1]and H.get(m,'CurrentBankC')==seed.rawtags[2]
                # The complete source cache is byte-identical on both inputs.
                # SFC internals are intentional transport state; application
                # writes and their order, cache state and returned flags are not normalized.
                app=[(a,v)for a,v in m.writes if a<256 or 0x200<=a<0x5100 or 0x5200<=a<0x8000]
                pair.append(((c.a,c.x,c.y,c.p,c.sp),[bytes(x)for x in m.ram],m.ram_writes,app,c.processorCycles,low,
                    sum(a in[0x5115,0x5116]for a,v in m.writes)))
            assert pair[0][:4]==pair[1][:4],('actual old/new BT row output/writes',valid,slot,flags,pair[0][0],pair[1][0])
            q['rows'].append(dict(valid=valid,slot=slot,flags=flags,oldCPU=pair[0][4],newCPU=pair[1][4],
                old_mapper_writes=pair[0][6],new_mapper_writes=pair[1][6],minimum_SP=pair[1][5]))
        # Every fingerprint byte is actually consulted, with all flags through
        # the resolver; no callback is executed by this pure-target helper.
        poisons=0
        for bad,flags in itertools.product(range(16),range(64)):
            m=L.fork(seeds[1]);m.ram[3][0x1fe0+bad]^=1
            before=[bytes(x)for x in m.ram]
            c,_=L.call(m,'BwBtResolve',a=0,p=L.flags(flags))
            assert not c.p&1 and[bytes(x)for x in m.ram]==before;poisons+=1
        rom={3:'BwColdPrepare',15:'CmHostFresh',17:'BwColdDraw',18:'FmQueueName',19:'JnResetDispatch',
             26:'BwColors',30:'BwStatusName',32:'HuNativeWorldPalette'}
        pure=0
        for raw,valid,slot,flags,active in itertools.product([27,33],[0,1],range(36),range(64),[0,1]):
            m=L.fork(seeds[1]);H.put(m,SelectedCharacter=raw,OperMode=1 if active else 0,OperMode_Task=3 if active else 0)
            if raw==27:
                m.ram[3][0x1fe0:0x1ff0]=(J/'bowser/cookie.bin').read_bytes()
            if not valid:m.ram[3][0x1fe0]=0
            before=[bytes(x)for x in m.ram];c,_=L.call(m,'BwBtResolve',a=3*slot,p=L.flags(flags))
            target=rom.get(slot)if raw==27 else None
            if raw==27 and slot==2 and not active:target='BwColdDraw'
            allowed=bool(target or valid)
            assert bool(c.p&1)==allowed,(raw,valid,slot,flags,active,c.p,target)
            if allowed:
                want=address(m.bundle,target)if target else 0xa000+slot*3
                bank=((L.location(m.bundle,target)-16)//8192)|128 if target else 3
                assert c.a==bank and m[address(m.bundle,'FarcallJmpTarget_SMC')+1]+256*m[address(m.bundle,'FarcallJmpTarget_SMC')+2]==want
            assert[bytes(x)for x in m.ram]==before;pure+=1
        # Real vector cuts at every reached shared transport instruction.
        seed=seeds[1];cuts=[];seen=set()
        def trace(m,c,step):
            tag=m.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else -1
            owned=(tag==215 and address(m.bundle,'BtRouter')<=c.pc<0xb100)or(tag==195 and(address(m.bundle,'BwBtResolve')<=c.pc<address(m.bundle,'BwStartFlags')or address(m.bundle,'BwResolveFamilyTail')<=c.pc<0xb300))or(tag==197 and address(m.bundle,'CfOrBtCheck')<=c.pc<address(m.bundle,'CfExternalGuardEnd'))or 0x15a<=c.pc<0x17b
            key=(tag,c.pc)
            if owned and key not in seen:seen.add(key);cuts.append((step,c.pc,bool(c.p&4)))
        H.finish(L.fork(seed),startrow(L.fork(seed),0,0x30)) if False else None
        m=L.fork(seed);H.finish(m,startrow(m,0,0x30),trace)
        for step,pc,masked in cuts:
            for kind,lag,pause in [('NMI',0,0),('NMI',255,0),('NMI',0,1)]+([]if masked else[('IRQ',255,0)]):
                m=L.fork(seed);H.put(m,NmiDisable=lag,GamePauseStatus=pause);proof=[]
                def inject(mm,c,age):
                    if age==step:
                        assert c.pc==pc
                        proof.append(L.V.interrupt(mm,c,kind))
                c,_=H.finish(m,startrow(m,0,0x30),inject);assert len(proof)==1
                q['vectors'].append(dict(PC=pc,lag=lag,pause=pause,**proof[0]))
        delta=[r['newCPU']-r['oldCPU']for r in q['rows']]
        q.update(passed=True,actual_BT_old_new_allflag_rows=len(q['rows']),all16cookie_poison_allflag_pairs=poisons,
            pure_two_family_allflag_targets=pure,actual_vectors=len(q['vectors']),old_new_BT_CPU_delta=[min(delta),max(delta)],
            source_cache_byte_identical=True,actual_AXYP_SP_ordered_application_writes_RAM0_3_raw_maps_exact=True,
            scope='Shared resolver/BT transport only. 4aacf Bowser graphics negative excluded; no natural BT lifecycle/host/cold/menu or native qualification.')
    except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
    q['bindings']={str(p.resolve()):L.sha(p)for p in[Path(__file__),Path(L.__file__),J/'candidate.nes',J/'candidate.dbg',
        J/'bt/router.s',J/'bowser/router.s',J/'bt/cache.bin',J/'bt/cookie.bin',J/'bowser/cookie.bin',P/'candidate.nes',P/'candidate.dbg']}
    (O/'controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['rows','vectors','bindings','traceback']}));assert q['passed'],q.get('error')
if __name__=='__main__':main()
