"""Zero-output current Jay controller checks and actual motor-return pairing."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import argparse,json
import current_jay_natural_stock_91dc_1116 as J

N,W,Frames=J.N,J.W,J.Frames


def bind(raw):
    q=J.bindings(raw);m=J.cold(raw);base=N.NesMPU;instances=[];counts=Counter();witnesses=[];points={}
    for name in('GameLoop','JayPrivateUpdate','JayIntegrate'):
        row=q['hooks'][name];points[row['tag'],row['PC']]=name
    def tag(pc):return m.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else-1
    class CPU(base):
        def __init__(self,*a,**kw):super().__init__(*a,**kw);self.pending=[];instances.append(self)
        def settle(self):
            while self.pending and(self.pc,self.sp,tag(self.pc))==self.pending[-1]['return']:
                p=self.pending.pop();counts[p['name']+'_returns']+=1
                if p['name']=='JayIntegrate':
                    assert(p['return'][0],p['return'][2])==(q['motion_callsite_PC']+11,3)
                    if len(witnesses)<8:witnesses.append(dict(entry=p['entry'],return_PC=self.pc,return_SP=self.sp,
                        return_tag=tag(self.pc),native=J.Foundation.fields(m)))
        def step(self):
            self.settle();name=points.get((tag(self.pc),self.pc))
            if name:
                pc=(m[0x100+((self.sp+1)&255)]+256*m[0x100+((self.sp+2)&255)]+1)&65535
                self.pending.append(dict(name=name,return_=(pc,(self.sp+2)&255,tag(pc)),entry=dict(PC=self.pc,SP=self.sp,tag=tag(self.pc))))
                self.pending[-1]['return']=self.pending[-1].pop('return_');counts[name+'_entries']+=1
            return super().step()
    for phase,pad in(('idle',0),('Right',1)):
        for _ in range(8):
            with patch.object(N,'NesMPU',CPU):m.controller_pad=pad;Frames.frame(m,whole_pass=True)
            for c in instances:c.settle();assert not c.pending
            assert tuple(bytes(m.ram[k][0x1fe0:0x1ff0])for k in(2,3))==(J.COOKIE,J.COOKIE)
            assert N.get(m,'NumberofLives')==2 and N.get(m,'JnHealth')==6
    for name in('GameLoop','JayPrivateUpdate','JayIntegrate'):
        assert counts[name+'_entries']==counts[name+'_returns']>0,(name,counts)
    assert counts['GameLoop_returns']==16
    return dict(parent_SHA256=J.PIN,facade_SHA256=J.H(Path(J.__file__).read_bytes()),grant_SHA256=J.GRANT_SHA,
        actual_compiled_Jay_cold=True,ordinary_idle8_Right8=True,counts=dict(counts),original_Integrate_return_witnesses=witnesses,
        terminal=J.Foundation.fields(m),source_fields=q['source'],current_primary_and_motion_exact=True,
        no_item_or_gameplay_seeds=True,no_natural_pickup_or_native_or_cadence_claim=True,outputs=0)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bind',action='store_true',required=True);p.parse_args()
    raw=J.load_current_image()
    def deny(*a,**kw):raise AssertionError('Jay source checker attempted output/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=bind(raw)
    q['receipt_SHA256']=J.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
