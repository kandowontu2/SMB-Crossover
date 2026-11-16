"""Bounded source callback proof of the read-only ACE attribution observer."""
from pathlib import Path
from unittest.mock import patch
import argparse,inspect,json
import replay_battletoads_carry_attribution_1115 as P
import check_battletoads_carry_native_profile_1115 as Previous

C,F,Model=P.C,P.F,P.Model
DRIVER_SHA='19b9a88827e1ca1c6209a40644f253cfffc122cde38973ffdff7cc9aa183889f'


def strict(raw):
    original=Path.read_bytes
    def read(path):
        assert path.resolve()!=C.ROM.resolve(),'Attribution reread mutable Downloads'
        return original(path)
    rejects=[]
    with patch.object(Path,'read_bytes',read):
        q=P.metadata(raw)
        for label,bad in(('parent174fa',C.inverse(raw)),('old_a90',P.Prior.reference(raw)),('unknown',bytes(len(raw))),('truncated',raw[:-1])):
            try:P.controller(bad)
            except AssertionError:rejects.append(label)
            else:raise AssertionError(('Wrong attribution input accepted',label))
        for at in(90000,653512,716848,792489,765868,1989648,1501131):
            bad=bytearray(raw);bad[at]^=1
            try:P.controller(bytes(bad))
            except AssertionError:rejects.append('dirty@'+str(at))
            else:raise AssertionError(('Dirty attribution input accepted',at))
    q.update(strict_rejections=rejects,mutable_Downloads_rereads=0,LF_Lua_compiled=True)
    return q


def callbacks(raw):
    assert C.digest(Path(Previous.__file__).read_bytes())==DRIVER_SHA
    scope=dict(Previous.__dict__,P=P)
    exec(compile(inspect.getsource(Previous.callbacks),str(Path(__file__))+':qualified-callback-chain','exec'),scope)
    q=scope['callbacks'](raw);profile=q['profile'];a=profile['attribution']
    assert not a['unacknowledged']and a['entries']==a['returns'],a
    for name in('BtMovement','BtPhysicsStep_actual','BtGraphics','BtDraw','DrawAllMetasprites','MetaspriteRenderLoop','BlockBufferColli_Head','BlockBufferColli_Side'):
        assert a['entries'].get('Main:'+name,0)>0,('Mapped function not reached',name,a['entries'])
    assert a['entries'].get('NMI_regular:AudioUpdate')==80,a['entries']
    assert len(profile['rows'])<=32 and len(a['groups'])<=32
    for phase,count in(('idle',48),('walk',32)):
        main=[g for k,g in a['groups'].items()if k.startswith(phase+':Main/checks')]
        assert sum(g['calls']for g in main)==count
    q.update(source_callback_chain_SHA256=DRIVER_SHA,all_measured_source_entries_returned=True,
        source_scheduler_regular_NMI_only=True,native_fast_catchup_busy_IRQ_scope_pending=True)
    return q


def interrupts(raw):
    # Exercise the new Audio child-IRQ subtraction using real vector code.
    # Returning immediately after injection lets the frozen callback driver
    # observe the freshly vectored first instruction before it executes.
    import check_battletoads_idle_native_profile_1115 as Driver
    base=Model.N.NesMPU;points=P.config(raw)['attribution']['points'];main=P.Prior.config(raw)['hooks']['GameLoop']['pc']
    injected=dict(Main=0,IRQ=0,NMI=0)
    class Vector(base):
        def step(self):
            m=self.memory;tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
            if type(m).__name__=='ReadBus':
                if self.pc==main and tag==254:injected['Main']+=1
                if injected['Main']>=2 and not injected['IRQ']and self.pc==points['AudioUpdate']['pc']+3 and tag==255 and not self.p&4:
                    self.irq();injected['IRQ']+=1;return
                if injected['Main']>=3 and not injected['NMI']and self.pc==points['BtPhysicsStep_actual']['pc']+2 and tag==3:
                    self.nmi();injected['NMI']+=1;return
            return super().step()
    scope=dict(Driver.__dict__,P=P,Base=Model,W=Model.W,N=Model.N,Frames=Model.Frames)
    exec(compile(inspect.getsource(Driver.run),str(Path(__file__))+':actual-vector-callback-fixture','exec'),scope)
    with patch.object(Model.N,'NesMPU',Vector):q=scope['run'](raw)
    a=q['profile']['attribution'];assert injected['IRQ']==injected['NMI']==1,injected
    assert a['entries']==a['returns']and not a['unacknowledged']
    assert a['entries'].get('NMI_busy:AudioUpdate')==1,a['entries']
    assert a['groups']['idle:NMI_regular/AudioUpdate']['interrupt']==120,a['groups']
    assert a['groups']['idle:Main/BtPhysicsStep_actual']['interrupt']>0
    q.update(explicit_actual_vector_injection=injected,no_gameplay_flags_or_state_seeded=True,
        freshly_vectored_first_instruction_callback_observed=True,actual_nested_IRQ_subtraction_cycles=120,
        source_fixture_not_natural_physical_schedule=True,native_fast_classification_pending=True)
    return q


def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=('strict','callbacks','interrupts'));a=ap.parse_args()
    raw=P.load_current_image()
    def deny(*args,**kw):raise AssertionError('Attribution attempted output/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch.object(C.Prior.Packet.Frozen.Cold.Runner.Native,'run',deny):q={'strict':strict,'callbacks':callbacks,'interrupts':interrupts}[a.mode](raw)
    q.update(mode=a.mode,outputs=0,Mesen_run=False)
    q['source_receipt_SHA256']=C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)


if __name__=='__main__':main()
