"""Trace all actual new encoded cold input/output; no decoded array mounts."""
from pathlib import Path
from unittest.mock import patch
import json,struct
import current_prince_hidden_point67_ace_1115 as Current

C,N,W,Frames=Current.C,Current.N,Current.W,Current.Frames

def run(parent):
    raw,composition=C.proposal(parent);head,chunks,sizes=C.Packet.extract(raw)
    fields=struct.unpack_from('<12H',head,len(head)-54)
    stages=[dict(start=fields[i],dest=fields[i+1],packed=fields[i+2],size=fields[i+3])for i in(0,4,8)]
    active=None;owner=None;pending=None;results=[];first=[];published=[]
    oldbus=W.ControllerBus;oldcpu=N.NesMPU
    def finish():
        nonlocal active
        assert active['cursor']==active['packed']and active['written']==active['size']
        results.append(dict(stage=active['stage'],packed_bytes=active['cursor'],decoded_bytes=active['written'],
            every_output_byte_exact=True,minimum_unread_margin=active['margin']))
        active=None
    class Bus(oldbus):
        def __getitem__(self,key):
            if self is owner and active is not None and isinstance(key,int):
                i=active['cursor'];addresses=active['addresses']
                if i<len(addresses)and key==addresses[i]:active['cursor']+=1
            return super().__getitem__(key)
        def __setitem__(self,key,value):
            if self is owner and active is not None and isinstance(key,int)and 0<=key-active['dest']<active['size']:
                unread=active['indices'].get(key)
                if unread is not None:
                    assert unread<active['cursor'],'Unread new compressed input overwritten'
                    active['margin']=min(active['margin'],active['cursor']-unread)
                i=key-active['dest'];count=active['written']
                if count<active['size']:
                    assert i==count and value==chunks[active['stage']][i],('Actual new decoder output differs',active['stage'],i)
                    active['written']+=1
            return super().__setitem__(key,value)
    class CPU(oldcpu):
        def step(self):
            nonlocal active,owner,pending
            m=self.memory
            if m is owner and pending==(self.pc,self.sp):finish();pending=None
            if self.pc==0xc000 and m.rawtags[2]==2:
                owner=m;assert active is None and pending is None
                stage=len(results);assert stage<3;spec=stages[stage];start=spec['start'];count=spec['packed'];end=min(start+count,0xdc00)
                addresses=list(range(start,end))+list(range(0xc280,0xc280+count-(end-start)))
                assert len(addresses)==len(set(addresses))==count
                active=dict(spec,stage=stage,addresses=addresses,indices={a:i for i,a in enumerate(addresses)},cursor=0,written=0,margin=65536)
                ret=(m[0x100+((self.sp+1)&255)]+256*m[0x100+((self.sp+2)&255)]+1)&65535
                pending=(ret,(self.sp+2)&255)
            if m is owner and self.pc==0xb310 and m.rawtags[1]==3 and not first:
                assert bytes(m[0xb310:0xb353])==C.NEW
                first.append(dict(PC=self.pc,SP=self.sp,all67_exact_before_SMC=True))
            if m is owner and self.pc==0xbbc1 and m.rawtags[1]==3 and not published:
                assert active is None and pending is None and len(results)==3
                cookie=raw[C.Packet.COOKIE:C.Packet.COOKIE+16]
                assert all(bytes(m.ram[b][0x1fe0:0x1ff0])==cookie for b in(2,3))
                published.append(dict(PC=self.pc,SP=self.sp,all_three_streams_exact=True,both_cookies=True))
            return super().step()
    with patch.object(W,'ControllerBus',Bus),patch.object(N,'NesMPU',CPU):
        m,opening=Current.cold(raw)
        for _ in range(8):m.controller_pad=0;Frames.frame(m,whole_pass=True)
    assert len(results)==3 and first and published
    q=dict(passed=True,candidate_SHA256=C.CANDIDATE,actual_decoder_stages=results,
        first_actual_PointRead=first[0],first_BBC1=published[0],source_array_mounts=0,
        actual_CPU_ROM_SHA256=C.digest(m.bundle['raw']),outputs=0,Mesen=False)
    q['receipt_SHA256']=C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q

if __name__=='__main__':
    def deny(*a,**k):raise AssertionError('Point transport source attempted output/native launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        q=run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
    print(json.dumps(q,separators=(',',':')),flush=True)
