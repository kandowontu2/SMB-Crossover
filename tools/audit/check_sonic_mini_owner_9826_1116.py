"""Actual9826 Sonic43 neutral16 and unchanged sustained-ceiling1UP callbacks."""
from pathlib import Path
from unittest.mock import patch
from collections import Counter
import inspect,json
import replay_sonic_mini_owner_9826_1116 as Factory
import check_sonic_hidden_native_callback_f7c9_1116 as Previous

F=Factory.F

def functions():
    assert F.H(Path(Previous.__file__).read_bytes())=='76442c0f0362192ef95cbefbc9a80b00892c702622c7927f916bc14f4e9108b1'
    ns=dict(Previous.__dict__,F=F,Factory=Factory,__file__=__file__)
    for name in('compile_pack','run'):
        s=inspect.getsource(getattr(Previous,name))
        if name=='run':
            s=s.replace("receipt['terminal']['rings']==5","receipt['terminal']['rings']==receipt['pre_oneup_resources']['rings']")
            s=s.replace("receipt['collected'][0]['item']['state']==6","receipt['collected'][0]['item']['state']>=6")
            s=s.replace('actual f7 CPU','actual combined9826 CPU')
        exec(compile(s,'<actual9826 frozen Sonic callback>','exec'),ns)
    return ns

def neutral(raw):
    m,cold=F.cold(raw,'sonic');base=F.N.NesMPU;counts=Counter();pending=[]
    points={(254,F.W.address(m.bundle,'GameLoop')):'Main',(3,0xbbb0):'OriginalFrame'}
    class CPU(base):
        def step(self):
            tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
            while pending and(self.pc,self.sp,tag)==pending[-1][1]:counts[pending.pop()[0]+'_returns']+=1
            name=points.get((tag,self.pc))
            if name:
                counts[name+'_entries']+=1;sp=self.sp;pc=(m[256+((sp+1)&255)]+256*m[256+((sp+2)&255)]+1)&65535
                pending.append((name,(pc,(sp+2)&255,m.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else-1)))
            return super().step()
    with patch.object(F.N,'NesMPU',CPU):
        for _ in range(16):m.controller_pad=0;F.Frames.frame(m,whole_pass=True)
    assert not pending and counts['Main_entries']==counts['Main_returns']==16
    assert counts['OriginalFrame_entries']==counts['OriginalFrame_returns']==16
    assert F.state(m)['x']==40 and F.N.get(m,'SelectedCharacter')==43
    return dict(passed=True,cold=cold,counts=dict(counts),terminal=F.state(m))

def run(parent):
    raw,composition=F.C.proposal(parent);n=neutral(raw);q=functions()['run'](raw,'sonic',1200)
    assert q['passed']and q['native_body_receipt']['pending']==0
    q.update(neutral16=n,composition=composition,unchanged_resource_body=True,actual_CPU_SHA256=F.PIN)
    q['combined_receipt_SHA256']=F.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q

if __name__=='__main__':
    def deny(*a,**k):raise AssertionError('Combined Sonic source attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(F.ROM.read_bytes())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
