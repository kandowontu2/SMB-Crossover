"""Same paired ISR proof; handled calls inherit real Main's busy context."""
from pathlib import Path
from unittest.mock import patch
import inspect,json
import check_mini_weapon_owner_interrupts_1116 as Previous

C,N,W=Previous.C,Previous.N,Previous.W
BASE_SHA='c2f6e53b98d0881558256ac3e57ea5907acb74189725daf41a12bddea0c5f958'

def run(parent):
    assert C.H(Path(Previous.__file__).read_bytes())==BASE_SHA
    source=inspect.getsource(Previous.run)
    def once(old,new):
        nonlocal source
        assert source.count(old)==1,old;source=source.replace(old,new,1)
    once('continuations=0;probe=None','continuations=0;probe=None;busy_seed=None;qualified={}')
    once('        def step(self):\n            m=self.memory','        def step(self):\n            nonlocal busy_seed\n            m=self.memory')
    once('                    seen.add(key);assert len(seen)<96',"                    seen.add(key);assert len(seen)<96\n                    if busy_seed is None and not probe and N.get(m,'NmiDisable')==255:busy_seed=N.fork(m)")
    once("                    if not self.p&4:pair(self,'IRQ',endpoint)","                    if not self.p&4:pair(self,'IRQ',endpoint);qualified.setdefault(self.pc,set()).add('IRQ')")
    once("                    if N.get(m,'NmiDisable')==255:pair(self,'busyNMI',endpoint)","                    if N.get(m,'NmiDisable')==255:pair(self,'busyNMI',endpoint);qualified.setdefault(self.pc,set()).add('busyNMI')")
    once("            seed,_=F.Current.cold(raw,True);probe='actual compiled visible9 caller';Public.public(seed,9,p=0x31);probe=None", "            assert busy_seed is not None;seed=N.fork(busy_seed);seed.__class__=W.ControllerBus;assert N.get(seed,'NmiDisable')==255\n            probe='actual compiled visible9 caller in real Main busy snapshot';Public.public(seed,9,p=0x31);probe=None")
    once("    assert counts['IRQ']and counts['busyNMI']and continuations==sum(counts.values())", "    assert counts['IRQ']and counts['busyNMI']and continuations==sum(counts.values())\n    assert all(qualified.get(pc,set())=={'IRQ','busyNMI'}for pc in PCS),(PCS,qualified)")
    once("paired_interrupt_counts=dict(counts),reached_contexts=cuts", "paired_interrupt_counts=dict(counts),qualified_interrupt_PCs={str(pc):sorted(kinds)for pc,kinds in qualified.items()},handled_busy_context='Unmodified NmiDisableFF captured from actual Main, not seeded',reached_contexts=cuts")
    env=dict(Previous.__dict__);exec(compile(source,str(Path(__file__))+':actual-busy-context','exec'),env);return env['run'](parent)

if __name__=='__main__':
    parent=C.ROM.read_bytes()
    def deny(*a,**kw):raise AssertionError('Mini paired busy proof attempted artifacts/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny),patch.object(Previous.Runner.Native,'run',deny):q=run(parent)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
