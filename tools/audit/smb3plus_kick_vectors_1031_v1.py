"""Interrupt the actual new C mapping and big-Toad source routine."""
from pathlib import Path
import importlib.util
import itertools
import json
import sys

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import smb3plus_kick_host_controls_1031_v1 as K
import benj_current_menu_controls_1030_v1 as M
import prepare_functional_roster_visuals58_v1 as B
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address


def main():
    O=K.O
    assert not (O/'kick-vectors-v1.json').exists()
    controls=json.loads(B.read(O/'kick-controls-v1.json'));B.bound(controls)
    b=scoped_load(K.J/'candidate.nes')
    spec=importlib.util.spec_from_file_location('actual_source_vectors',R/'build/character-host-union-v13/gm_verify_nmi.py')
    g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g);M.T.G=g
    q=K.seed(b,2,1,64)
    _,tr,path,_=M.T.invoke(q,'M3Movement')
    spans=[(M.T.key(b,'MbMappedStep'),44),(M.T.key(b,'MbToadBigFrame'),81)]
    sites=sorted({(*k,1) for k in path if any(k[1]==at[1] and at[0]<=k[0]<at[0]+size for at,size in spans)})
    assert len(sites)>=35
    rows=[]
    for site,(kind,disable,pause) in itertools.product(sites,[('IRQ',255,0),('NMI',255,0),('NMI',0,0),('NMI',0,1)]):
        r=K.seed(b,2,1,64)
        r.put(NmiDisable=disable,GamePauseStatus=pause,DisableScreenFlag=1)
        c,t,_,info=M.T.invoke(r,'M3Movement',p=0x30,inject=(site,kind))
        differences=[dict(address=a,baseline=q.m[a],interrupted=r.m[a])
            for a in range(0x5c00,0x5cc0) if q.m[a]!=r.m[a]]
        if differences:
            B.write(O/'kick-vector-negative-v1.json',json.dumps(dict(site=site,kind=kind,
                disable=disable,pause=pause,differences=differences,
                candidate=controls['candidate'],script_sha256=B.sha(__file__)),indent=2)+'\n')
        assert not differences,(site,kind,'Private state',differences)
        assert r.m.banks==q.m.banks and r.get('CurrentBankC')==q.get('CurrentBankC')
        rows.append(dict(site=site,kind=kind,disable=disable,pause=pause,
            minimum_SP=info['interrupt']['minimum_SP'],AXYP_SP_live_stack_33SMC_maps_preserved=True))
    d=dict(passed=True,CPU_only=True,native=False,candidate=controls['candidate'],
        actual_new_instruction_sites=len(sites),real_vectors=len(rows),vectors=rows,
        scope='Real normal/lag/paused NMI and IRQ; actual mapped extension resumes unchanged. No native timing claim.',
        bindings={str(p):B.sha(p) for p in [Path(__file__),Path(K.__file__),O/'kick-controls-v1.json',
            K.J/'candidate.nes',K.J/'candidate.dbg',R/'build/character-host-union-v13/gm_verify_nmi.py',
            R/'tools/audit/rogue_dawn_scheduler_controls_v1.py']})
    B.write(O/'kick-vectors-v1.json',json.dumps(d,indent=2)+'\n')
    print(json.dumps(dict(passed=True,sites=len(sites),vectors=len(rows),candidate=d['candidate'])))


if __name__=='__main__':main()
