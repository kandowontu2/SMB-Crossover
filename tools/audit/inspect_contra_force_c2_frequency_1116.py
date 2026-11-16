"""Read-only real current-parent C2 eligibility; executes no candidate code."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import json
import contra_force_c2_direct_model_1116 as M

C,N,W,Frames=M.C,M.N,M.W,M.Frames


def run(parent):
    assert C.H(parent)==C.PIN
    m=M.cold(parent)
    for _ in range(4):m.controller_pad=0;Frames.frame(m,whole_pass=True);M.empty(m)
    base=N.NesMPU;rows=[]
    for phase,pad in(('idle',0),('Right',1)):
        groups=Counter();actual=Counter();count=0
        class CPU(base):
            def step(self):
                nonlocal count
                tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
                if(tag,self.pc)==(215,0xb08e):
                    assert N.get(m,'SelectedCharacter')==31
                    word=m[0x16c]+256*m[0x16d];offset=word-0xb020
                    assert 0<=offset<=105 and offset%3==0
                    groups[offset//3,N.get(m,'CurrentBankC'),m.rawtags[2]]+=1;count+=1
                return super().step()
        with patch.object(N,'NesMPU',CPU):m.controller_pad=pad;Frames.frame(m,whole_pass=True)
        M.empty(m)
        rows.append(dict(phase=phase,total_queries=count,C2_shadow_and_actual=sum(n for(q,c,t),n in groups.items()if c==t==2),
            groups=[dict(service=q,currentC=c,actualC=t,calls=n)for(q,c,t),n in sorted(groups.items())]))
    q=dict(parent_SHA256=C.PIN,actual_parent_only_no_candidate_CPU=True,genuine_cold_compiled_Burns=True,
        phases=rows,no_actor_health_terrain_position_or_ability_seeds=True,no_physical_cadence_claim=True,outputs=0)
    q['receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q


if __name__=='__main__':
    parent=C.load_current_image();assert C.H(parent)==C.PIN
    def deny(*a,**kw):raise AssertionError('Parent eligibility observer attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(parent)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
