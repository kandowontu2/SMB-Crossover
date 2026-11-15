"""Reuse frozen reached-caller ISR driver with carry layout and strict banks."""
from collections import Counter
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import inspect,json
import check_battletoads_dense_isr_1115 as Previous
import plan_battletoads_dense_carry_1115 as D

P,C,N,W=D.P,D.C,D.N,D.W
DRIVER_SHA='dc1397c685e88f7e691831c21939b9d1cd4b36997d828e30e5e34ab996b25f21'


def run(parent,image):
    assert sha256(Path(Previous.__file__).read_bytes()).hexdigest()==DRIVER_SHA
    source=inspect.getsource(Previous.run)
    assert source.count('0x5099<=c.pc<0x50d8')==1
    source=source.replace('0x5099<=c.pc<0x50d8','0x5099<=c.pc<0x50dc')
    scope=dict(Previous.__dict__,D=D,P=P,C=C,N=N,W=W)
    exec(compile(source,str(Path(__file__))+':frozen-reached-caller-driver','exec'),scope)
    base=N.NesMPU;carry=Counter()
    class Observe(base):
        def step(self):
            m=self.memory
            if getattr(m,'carry_successor',False)and self.pc==0x5099:
                owner=N.get(m,'SelectedCharacter')
                assert bool(self.p&1)==(owner==33),'Cohort carry changed across actual SFC/ISR'
                carry[owner,bool(self.p&1)]+=1
            return super().step()
    with patch.object(N,'NesMPU',Observe):q=scope['run'](parent,image)
    q.update(frozen_driver_SHA256=DRIVER_SHA,only_driver_edit='extend helper code capture end50D8→50DC',
        actual_mapped_PRG_ownership_asserted_for_all_unit_reads=True,
        helper_live_carry_observations=[dict(owner=o,C=c,cases=n)for(o,c),n in sorted(carry.items())])
    return q


if __name__=='__main__':
    parent,image,info=D.Input.load()
    def deny(*a,**kw):raise AssertionError('Carry ISR component attempted output/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch.object(C.Packet.Frozen.Cold.Runner.Native,'run',deny):q=run(parent,image)
    q.update(info,outputs=0,Mesen_run=False)
    q['source_receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
