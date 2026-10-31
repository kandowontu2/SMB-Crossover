"""Use an actual serial B input when normal NMI reads the controller.

The retained v1 negative disconnected the physical controller while asserting
that Main's pre-NMI B input must stay held. This fixture implements the NES
strobe and eight serial bits; no native input read/callback is bypassed.
"""
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
from check_tmnt_render_oa import Memory


class SerialMemory(Memory):
    def __getitem__(self,at):
        if isinstance(at,int) and at in (0x4016,0x4017):
            port=at-0x4016;index=self.pad_index[port]
            value=(self.pads[port]>>(7-index))&1 if index<8 else 1
            if not self.strobe:self.pad_index[port]+=1
            return 0x40|value
        return super().__getitem__(at)

    def __setitem__(self,at,value):
        super().__setitem__(at,value)
        if at==0x4016:
            self.strobe=value&1
            self.pad_index=[0,0]


def seed(b):
    q=K.seed(b,2,1,64)
    q.m.__class__=SerialMemory
    q.m.pads=[64,0];q.m.pad_index=[0,0];q.m.strobe=0
    return q


def main():
    O=K.O
    assert not (O/'kick-vectors-v2.json').exists()
    controls=json.loads(B.read(O/'kick-controls-v1.json'));B.bound(controls)
    negative=json.loads(B.read(O/'kick-vector-negative-v1.json'))
    assert [q['address'] for q in negative['differences']]==[0x5c15,0x5c19]
    b=scoped_load(K.J/'candidate.nes')
    spec=importlib.util.spec_from_file_location('actual_source_vectors',R/'build/character-host-union-v13/gm_verify_nmi.py')
    g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g);M.T.G=g
    original_interrupt=g.checked_interrupt
    def diagnostic(memory,cpu,kind):
        try:return original_interrupt(memory,cpu,kind)
        except AssertionError:
            B.write(O/'kick-vector-negative-v2.json',json.dumps(dict(PC=cpu.pc,
                banks=memory.banks,kind=kind,bytes=bytes(memory[cpu.pc:cpu.pc+8]).hex(),
                shadowC=g.scheduler.get(memory,'CurrentBankC'),candidate=controls['candidate'],
                script_sha256=B.sha(__file__)),indent=2)+'\n')
            raise
    g.checked_interrupt=diagnostic
    q=seed(b);_,tr,path,_=M.T.invoke(q,'M3Movement')
    spans=[(M.T.key(b,'MbMappedStep'),44),(M.T.key(b,'MbToadBigFrame'),81)]
    sites=sorted({(*k,1) for k in path if any(k[1]==at[1] and at[0]<=k[0]<at[0]+size for at,size in spans)})
    assert len(sites)>=35
    rows=[]
    for site,(kind,disable,pause) in itertools.product(sites,[('IRQ',255,0),('NMI',255,0),('NMI',0,0),('NMI',0,1)]):
        r=seed(b);r.put(NmiDisable=disable,GamePauseStatus=pause,DisableScreenFlag=1)
        c,t,_,info=M.T.invoke(r,'M3Movement',p=0x30,inject=(site,kind))
        assert bytes(r.m[0x5c00:0x5cc0])==bytes(q.m[0x5c00:0x5cc0]),(site,kind,'Private state')
        assert r.m.banks==q.m.banks and r.get('CurrentBankC')==q.get('CurrentBankC')
        rows.append(dict(site=site,kind=kind,disable=disable,pause=pause,
            minimum_SP=info['interrupt']['minimum_SP'],AXYP_SP_live_stack_33SMC_maps_preserved=True))
    d=dict(passed=True,CPU_only=True,native=False,candidate=controls['candidate'],
        actual_new_instruction_sites=len(sites),real_vectors=len(rows),vectors=rows,
        fixture_correction=__doc__,scope='Real normal/lag/paused NMI and IRQ; actual mapped extension resumes unchanged. No native timing claim.',
        bindings={str(p):B.sha(p) for p in [Path(__file__),Path(K.__file__),O/'kick-controls-v1.json',
            O/'kick-vector-negative-v1.json',R/'tools/audit/smb3plus_kick_vectors_1031_v1.py',
            K.J/'candidate.nes',K.J/'candidate.dbg',R/'build/character-host-union-v13/gm_verify_nmi.py',
            Path(g.scheduler.__file__)]})
    B.write(O/'kick-vectors-v2.json',json.dumps(d,indent=2)+'\n')
    print(json.dumps(dict(passed=True,sites=len(sites),vectors=len(rows),candidate=d['candidate'])))


if __name__=='__main__':main()
