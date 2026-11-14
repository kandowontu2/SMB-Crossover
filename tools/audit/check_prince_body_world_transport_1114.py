"""Actual compiled UI/cold decode, unread-input and code-readback proof."""
from hashlib import sha256
import json,struct
from unittest.mock import patch
import check_prince_body_world_1114 as Game

C,P,N=Game.C,Game.P,Game.N


def run(parent):
    raw,info=C.proposal(parent);assert C.inverse(raw)==parent
    head,chunks,lengths=C.Build.Old.Packet.extract(raw)
    fields=struct.unpack_from('<12H',head,len(head)-54)
    # Current450-byte loader's authenticated wrap fix writes BOTH bytes:
    # C280, not the historical446-byte worker's C300. Derive and pin it.
    wrap=bytes.fromhex('c9dcd008a9808503a9c28504')
    assert head[C.Build.Old.Packet.LOADER:].count(wrap)==1
    input_end,input_wrap=0xdc00,0xc280
    stages=[dict(start=fields[i],dest=fields[i+1],packed=fields[i+2],size=fields[i+3])for i in(0,4,8)]
    assert [s['packed']for s in stages]==list(lengths)
    active=None;results=[];owner=None
    actual_bus=P.W.ControllerBus;actual_cpu=N.NesMPU
    def finish():
        assert active['cursor']==len(active['addresses']),('Unconsumed input',active)
        assert active['written']==active['size'],('Incomplete output',active)
        results.append(dict(stage=active['stage'],packed_bytes=active['cursor'],decoded_bytes=active['written'],
            every_output_write_exact=True,minimum_unread_margin=active['margin']))
    class Bus(actual_bus):
        def __getitem__(self,key):
            if self is owner and active is not None and isinstance(key,int):
                index=active['cursor'];addresses=active['addresses']
                if index<len(addresses)and key==addresses[index]:active['cursor']+=1
            return super().__getitem__(key)
        def __setitem__(self,key,value):
            if self is owner and active is not None and isinstance(key,int):
                lo=active['dest'];i=key-lo
                if 0<=i<active['size']:
                    unread=active['indices'].get(key)
                    if unread is not None:
                        assert unread<active['cursor'],('Unread staging input overwritten',active['stage'],hex(key),unread,active['cursor'])
                        active['margin']=min(active['margin'],active['cursor']-unread)
                    count=active['written']
                    if count<active['size']:
                        assert i==count,('Nonsequential decode output',active['stage'],i,count)
                        assert value==chunks[active['stage']][i],('Decoded write differs',active['stage'],i,value)
                        active['written']+=1
            return super().__setitem__(key,value)
    class CPU(actual_cpu):
        def step(self):
            nonlocal active,owner
            m=self.memory
            if self.pc==0xc000 and m.rawtags[2]==2:
                owner=m
                if active is not None:finish()
                stage=len(results);assert stage<3
                spec=stages[stage];start=spec['start'];count=spec['packed'];end=min(start+count,input_end)
                addresses=list(range(start,end))+list(range(input_wrap,input_wrap+count-(end-start)))
                assert len(addresses)==count and len(set(addresses))==count
                active=dict(spec,stage=stage,addresses=addresses,indices={a:i for i,a in enumerate(addresses)},cursor=0,written=0,margin=65536)
            return super().step()
    with patch.object(P.W,'ControllerBus',Bus),patch.object(N,'NesMPU',CPU):model,opening=Game.cold(raw)
    assert active is not None;finish();assert len(results)==3
    q=dict(passed=True,composition=info,opening=opening,actual_decode_stages=results,
        no_unread_input_overwrite=True,each_decoded_output_byte_exact=True,
        current_loader_wrap={'end':hex(input_end),'restart':hex(input_wrap),'exact_instruction_hex':wrap.hex()},
        actual_granted_live_envelopes_exact=True,all_other_decoded_bytes_transported=True,
        UI_scope='Actual compiled menu/parser/cold; peripheral unit does not model real vblank or native timing',
        outputs=0,Mesen=False)
    q['receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return q


if __name__=='__main__':print(json.dumps(run(Game.Factory.ROM.read_bytes()),separators=(',',':')),flush=True)
