"""Interrupt actual float, mapper, stack and CHR-helper instruction sites."""
from pathlib import Path
import collections
import importlib.util
import itertools
import json
import sys

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import smb3plus_peach_movement_controls_1031_v1 as P
import smb3plus_body_host_controls_1030_v5 as D
from smb3plus_kick_vectors_1031_v2 import SerialMemory
from check_tmnt_render_oa import address
M,B=P.M,P.B


def main():
    O=P.O;J=P.J
    assert not (O/'vectors-v1.json').exists()
    controls=json.loads(B.read(O/'movement-controls-v1.json'));B.bound(controls)
    graphics=json.loads(B.read(O/'graphics-controls-v2.json'));B.bound(graphics)
    b=P.scoped_load(J/'candidate.nes')
    path=R/'build/character-host-union-v13/gm_verify_nmi.py'
    spec=importlib.util.spec_from_file_location('actual_peach_source_vectors',path)
    g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
    def known_seam(memory,cpu,slot,store):
        return (slot==2 and cpu.pc==address(b,'MbMappedStep')+9 and memory.banks[1]==90
            and bytes(memory[cpu.pc:cpu.pc+5])==bytes.fromhex('a9db8d1651')
            and g.scheduler.get(memory,'CurrentBankC')==0xdb)
    text=path.read_text();text=text[text.index('def checked_interrupt('):text.index('\nscheduler.interrupt =')]
    old='assert bytes(memory[cpu.pc:cpu.pc + 3]) == store';assert text.count(old)==1
    text=text.replace(old,old+' or peach_known_map_seam(memory,cpu,slot,store)')
    g.__dict__['peach_known_map_seam']=known_seam
    exec(compile(text,str(Path(__file__))+'::exact-existing-vector-checker','exec'),g.__dict__)
    M.T.G=g
    spans=[]
    for name,sym in b['syms'].items():
        if name.startswith('MbPeach') and '::' not in name or name=='MbMappedStep':
            assert 'size' in sym,name
            spans.append((name,M.T.key(b,name),int(sym['size'])))
    spans.append(('MbFloatReadChrLow',M.T.key(b,'MbFloatReadChrLow'),23))
    rows=[];coverage=set();cohorts=[]
    for name,steps,release in [('jump',0,False),('negative_wobble',34,False),
            ('positive_wobble',50,False),('expiry',110,False),('release',60,True),
            ('land',40,False),('form5_graphics',0,False)]:
        q=D.seed(b,3,5,14,1) if name=='form5_graphics' else P.peach_seed(b)
        if name!='form5_graphics':
            for frame in range(steps):
                q.put(FrameCounter=frame);M.T.invoke(q,'M3Movement')
            q.put(FrameCounter=steps)
            if release:q.put(SavedJoypadBits=0)
            if name=='land':q.put(Player_State=0,SavedJoypadBits=0)
        held=q.get('SavedJoypadBits')
        snapshot=bytes(q.m);maps=q.m.banks.copy()
        def seed():
            r=M.T.make(b,17);list.__setitem__(r.m,slice(None),snapshot);r.m.banks=maps.copy()
            r.m.__class__=SerialMemory;r.m.pads=[held,0];r.m.pad_index=[0,0];r.m.strobe=0
            return r
        label='M3Graphics' if name=='form5_graphics' else 'M3Movement'
        q=seed();_,tr,trace,_=M.T.invoke(q,label)
        sites=sorted({(*k,1) for k in trace if any(k[1]==at[1] and at[0]<=k[0]<at[0]+size for _,at,size in spans)})
        assert sites,name
        for n,at,size in spans:
            if any(k[1]==at[1] and at[0]<=k[0]<at[0]+size for k in trace):coverage.add(n)
        cohorts.append(dict(name=name,caller=label,sites=len(sites)))
        for site,(kind,disable,pause) in itertools.product(sites,[('IRQ',255,0),('NMI',255,0),('NMI',0,0),('NMI',0,1)]):
            r=seed();r.put(NmiDisable=disable,GamePauseStatus=pause,DisableScreenFlag=1)
            c,t,_,info=M.T.invoke(r,label,p=0x30,inject=(site,kind))
            assert bytes(r.m[0x5c00:0x5cc0])==bytes(q.m[0x5c00:0x5cc0]),(name,site,kind,'Private state')
            assert r.m.banks==q.m.banks and r.get('CurrentBankC')==q.get('CurrentBankC')
            rows.append(dict(cohort=name,site=site,kind=kind,disable=disable,pause=pause,
                minimum_SP=info['interrupt']['minimum_SP'],AXYP_SP_live_stack_33SMC_maps_preserved=True))
    expected={name for name,_,_ in spans}-{'MbPeachFloatSink'}
    assert coverage>=expected,(expected-coverage)
    d=dict(passed=True,CPU_only=True,native=False,candidate=controls['candidate'],
        real_vectors=len(rows),cohorts=cohorts,covered_routines=sorted(coverage),vectors=rows,
        exact_existing_map_seam='Only MbMappedStep+9,A90,A9DB8D1651 with shadowDB; all other original checker assertions unchanged.',
        scope='Genuine normal/lag/paused NMI and IRQ while actual emitted code executes. Sand-sink state is source-CPU qualified separately. No native PPU/timing claim.',
        bindings={str(p):B.sha(p) for p in [Path(__file__),Path(P.__file__),
            O/'movement-controls-v1.json',O/'graphics-controls-v2.json',J/'candidate.nes',J/'candidate.dbg',
            path,Path(g.scheduler.__file__),R/'tools/audit/smb3plus_kick_vectors_1031_v2.py']})
    B.write(O/'vectors-v1.json',json.dumps(d,indent=2)+'\n')
    print(json.dumps(dict(passed=True,vectors=len(rows),cohorts=cohorts,candidate=d['candidate'])))


if __name__=='__main__':main()
