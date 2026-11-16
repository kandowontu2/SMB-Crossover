"""Original-only cold/runtime metadata writer observation, no proposed CPU."""
from pathlib import Path
from unittest.mock import patch
from collections import Counter
import json
import audit_sonic_stock_foundation_1327_1116 as F
import audit_sonic_hidden_selector_consumers_1327_1116 as Static


def run(raw):
    q=F.bindings(raw);static=Static.review(raw);N,W=F.N,F.W
    ctx={'phase':'cold','PC':-1,'tag':-1};writes=Counter();first={};runtime=0
    baseCPU=N.NesMPU;baseBus=W.ControllerBus
    class CPU(baseCPU):
        def step(self):
            ctx.update(PC=self.pc,tag=self.memory.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1)
            return super().step()
    class Bus(baseBus):
        def __setitem__(self,at,value):
            nonlocal runtime
            if isinstance(at,int)and at>=0x8000 and self.rawtags[(at-0x8000)//8192]==2 and 0x1344<=(at&8191)<0x1371:
                valid=tuple(bytes(self.ram[k][0x1fe0:0x1ff0])for k in(2,3))==(q['cookie'],)*2
                key=(ctx['phase'],ctx['tag'],ctx['PC'],valid)
                writes[key]+=1
                first.setdefault(key,dict(address=at,physical_offset=at&8191,value=value&255))
                assert not valid,'No writer to proposed helper while owning headers are valid'
                if ctx['phase']=='runtime':runtime+=1
            return super().__setitem__(at,value)
    with patch.object(W,'ControllerBus',Bus),patch.object(N,'NesMPU',CPU),patch.object(W.UI.F,'NesMPU',CPU):
        m,cold=F.cold(raw,'sonic');ctx['phase']='runtime'
        for _ in range(16):m.controller_pad=0;F.Frames.frame(m,whole_pass=True)
    assert not runtime and writes and bytes(m.ram[2][0x1344:0x1371])==b'\xff'*45
    assert tuple(bytes(m.ram[k][0x1fe0:0x1ff0])for k in(2,3))==(q['cookie'],)*2
    out=dict(passed=True,ROM_SHA256=F.PIN,source_SHA256=F.H(Path(__file__).read_bytes()),
        static_receipt=static['receipt_SHA256'],actual_cold=cold,runtime_Main=16,
        actual_tail_writer_groups=[dict(phase=p,tag=t,PC=pc,own_headers_valid=v,count=n,first=first[(p,t,pc,v)])for(p,t,pc,v),n in writes.items()],
        committed_runtime_tail_writes=runtime,terminal=F.state(m),
        scope='Original1327 only: actual ordinary compiled cold plus16neutral Main; metadata copied only before owning headers valid. Static owning abs/indexed writer census supplements this bounded witness; no arbitrary-pointer or all-foreign-lifecycle claim.',
        new_game_instructions_executed=False,ROM_written=False,Mesen=False,outputs=0)
    out['receipt_SHA256']=F.H(json.dumps(out,sort_keys=True,separators=(',',':')).encode());return out


if __name__=='__main__':
    def deny(*a,**k):raise AssertionError('Read-only Sonic writer audit attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):out=run(F.ROM.read_bytes())
    print('RESULT '+json.dumps(out,separators=(',',':')),flush=True)
