"""Rebind proven real transport checks to current64 genuine Benj source."""
from pathlib import Path
import hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import battletoads_transport_controls_v1 as T
import battletoads_only_transport_controls_v1 as F
import battletoads_transport_vectors_v1 as V
H=T.H;L=T.L;address=T.address
O=R/'build/battletoads-current64-only-v1';J=O/'joint'
def vectors():
    out=O/'vector-controls.json';assert not out.exists();q=dict(passed=False,native=False)
    try:
        b=H.C.qualified(J/'candidate.nes');rows=[]
        for raw,rd,alt in[(0,0,0),(2,1,0),(9,0,32),(22,0,0),(25,0,0),(24,0,0),(28,0,0),(32,0,0),(33,0,0),(34,0,0),(255,0,0)]:
            seed=L.make(b);T.reset(seed,raw,rd,alt);cuts=[];seen=set()
            def trace(m,c,step):
                tag=m.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
                pc=c.pc;key=(tag,pc)
                own=(tag==252 and any(address(b,n)<=pc<address(b,n)+97 for n in['NrPortrait','NrWeapons']))or 0x15a<=pc<0x17b
                if own and key not in seen:seen.add(key);cuts.append((step,pc,tag,bool(c.p&4)))
            F.endpoint(L.fork(seed),'GmFreshGate',0x30,trace)
            for step,pc,tag,masked in cuts:
                kinds=[('NMI',0,0),('NMI',255,0),('NMI',0,1)]+([]if masked else[('IRQ',255,0)])
                for kind,lag,pause in kinds:
                    m=L.fork(seed);H.put(m,NmiDisable=lag,GamePauseStatus=pause);proof=[]
                    def inject(mem,c,age):
                        if age!=step:return
                        assert c.pc==pc
                        audio=[];orig=c.step
                        def stepping():
                            if c.pc==address(b,'AudioUpdate'):audio.append(c.pc)
                            return orig()
                        c.step=stepping;r=T.V.interrupt(mem,c,kind);c.step=orig
                        assert len(audio)==int(kind=='NMI')
                        proof.append(dict(raw=raw,rd=rd,alt=alt,PC=pc,rawtag=tag,lag=lag,pause=pause,AudioUpdate_entries=len(audio),**r))
                    F.endpoint(m,'GmFreshGate',0x30,inject);assert len(proof)==1;rows+=proof
        q.update(passed=True,actual_vector_cases=len(rows),normal_lag_pause_and_legal_IRQ=True,
            all33SMC_AXYP_SP_livepage1_raw_banks_shadows_borrowed_pairs_exact=True,AudioUpdate_once_per_NMI=True,rows=rows)
    except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
    q['bindings']={str(p.resolve()):T.sha(p)for p in[Path(__file__),Path(F.__file__),O/'proposal.json',J/'candidate.nes',J/'candidate.dbg']}
    out.write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['rows','bindings','traceback']}));assert q['passed'],q.get('error')
def main():
    T.P=R/'build/battletoads-current64-host-v1/joint';T.O=R/'build/battletoads-current64-transport-v1';T.J=T.O/'joint'
    T.same=F.same # Same actual assertions, observer reads CPU storage without MMIO side effects.
    T.main()
    F.P=T.J;F.O=O;F.J=J;F.main()
    V.O=T.O;V.J=T.J;V.main()
    vectors()
    inputs=[Path(__file__),T.O/'proposal.json',T.O/'endpoint-controls.json',T.O/'vector-controls.json',
        O/'proposal.json',O/'endpoint-controls.json',O/'vector-controls.json']
    q=dict(passed=True,native=False,current64=True,candidate=T.sha(J/'candidate.nes'),
        parent='98048319d382e7a5c4e7186704b6e3b939eda4eec9bdd6e098c402cbd30799b6',
        actual_Benj_targets=['BmFresh','BmColors'],pair_groups=46,shared_readiness_64_exact=True,
        no_gameplay_admission=True,bindings={str(p.resolve()):T.sha(p)for p in inputs})
    (O/'transport-controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))
if __name__=='__main__':main()
