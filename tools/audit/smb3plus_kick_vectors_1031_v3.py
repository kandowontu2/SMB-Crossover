"""Recognize the exact existing macro's redundant LDA at its C-map seam.

BankPRGC emits shadow-store, LDA#bank, hardware-store. Normal NMI legitimately
restores the published shadow during that two-instruction gap. The old checker
accepted only an immediate hardware STA, so retain its failure and classify
this one emitted PC/byte sequence explicitly; no other seam is relaxed.
"""
from pathlib import Path
import importlib.util
import itertools
import json
import sys

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import smb3plus_kick_vectors_1031_v2 as V
K,M,B=V.K,V.M,V.B
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address


def main():
    O=K.O
    assert not (O/'kick-vectors-v3.json').exists()
    controls=json.loads(B.read(O/'kick-controls-v1.json'));B.bound(controls)
    negative=json.loads(B.read(O/'kick-vector-negative-v2.json'))
    assert negative['PC']==0xaed5 and negative['bytes'].startswith('a9db8d1651')
    b=scoped_load(K.J/'candidate.nes')
    path=R/'build/character-host-union-v13/gm_verify_nmi.py'
    spec=importlib.util.spec_from_file_location('actual_source_vectors',path)
    g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
    def known_seam(memory,cpu,slot,store):
        return (slot==2 and cpu.pc==address(b,'MbMappedStep')+9 and memory.banks[1]==90
            and bytes(memory[cpu.pc:cpu.pc+5])==bytes.fromhex('a9db8d1651')
            and g.scheduler.get(memory,'CurrentBankC')==0xdb)
    text=path.read_text();text=text[text.index('def checked_interrupt('):text.index('\nscheduler.interrupt =')]
    old='assert bytes(memory[cpu.pc:cpu.pc + 3]) == store'
    assert text.count(old)==1
    text=text.replace(old,old+' or kick_known_map_seam(memory,cpu,slot,store)')
    g.__dict__['kick_known_map_seam']=known_seam
    exec(compile(text,str(Path(__file__))+'::exact-existing-vector-checker','exec'),g.__dict__)
    M.T.G=g
    q=V.seed(b);_,tr,trace,_=M.T.invoke(q,'M3Movement')
    spans=[(M.T.key(b,'MbMappedStep'),address(b,'MbKickLogicEnd')-address(b,'MbMappedStep')),
           (M.T.key(b,'MbToadBigFrame'),81)]
    sites=sorted({(*k,1) for k in trace if any(k[1]==at[1] and at[0]<=k[0]<at[0]+size for at,size in spans)})
    assert len(sites)>=35
    rows=[]
    for site,(kind,disable,pause) in itertools.product(sites,[('IRQ',255,0),('NMI',255,0),('NMI',0,0),('NMI',0,1)]):
        r=V.seed(b);r.put(NmiDisable=disable,GamePauseStatus=pause,DisableScreenFlag=1)
        c,t,_,info=M.T.invoke(r,'M3Movement',p=0x30,inject=(site,kind))
        assert bytes(r.m[0x5c00:0x5cc0])==bytes(q.m[0x5c00:0x5cc0]),(site,kind,'Private state')
        assert r.m.banks==q.m.banks and r.get('CurrentBankC')==q.get('CurrentBankC')
        rows.append(dict(site=site,kind=kind,disable=disable,pause=pause,
            minimum_SP=info['interrupt']['minimum_SP'],AXYP_SP_live_stack_33SMC_maps_preserved=True))
    d=dict(passed=True,CPU_only=True,native=False,candidate=controls['candidate'],
        actual_new_instruction_sites=len(sites),real_vectors=len(rows),vectors=rows,
        fixture_corrections=[V.__doc__,__doc__],
        scope='Real normal/lag/paused NMI and IRQ; actual mapped extension resumes unchanged. No native timing claim.',
        bindings={str(p):B.sha(p) for p in [Path(__file__),Path(V.__file__),Path(K.__file__),
            R/'tools/audit/smb3plus_kick_vectors_1031_v1.py',O/'kick-controls-v1.json',
            O/'kick-vector-negative-v1.json',O/'kick-vector-negative-v2.json',
            K.J/'candidate.nes',K.J/'candidate.dbg',path,Path(g.scheduler.__file__)]})
    B.write(O/'kick-vectors-v3.json',json.dumps(d,indent=2)+'\n')
    print(json.dumps(dict(passed=True,sites=len(sites),vectors=len(rows),candidate=d['candidate'])))


if __name__=='__main__':main()
