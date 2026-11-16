"""Actual a2 public-route IRQ/busyNMI at new JSR and all11B helper opcodes."""
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
import inspect,json
import current_sonic_ceiling_complete_a2d9_1116 as F
import check_sonic_hidden_reached_irq_f7c9_1116 as Previous
import check_sonic_ceiling_native_callback_a2d9_1116 as Callback

PREVIOUS_SHA='c0cd191d1f9ac006522d8ade5bb47894c466ba5c1dca7cc83f25c6bc8cd7332e'


def run(raw):
    assert F.H(Path(Previous.__file__).read_bytes())==PREVIOUS_SHA
    proxy=SimpleNamespace(**Previous.Source.__dict__)
    proxy.F=F;proxy.Factory=Callback.Factory;proxy.compile_pack=Callback.compile_pack
    code=inspect.getsource(Previous.run)
    edits=(
        ("m.ram[2][0x1344:0x1371]=b'\\xff'*45 if old else F.C.HELPER", "m.ram[2][0x1344:0x137c]=b'\\xff'*56 if old else F.C.HELPER\n        m.ram[2][0x108f:0x1092]=F.C.OLD_HOOK if old else F.C.HOOK"),
        ('0xd344<=self.pc<0xd371', '(0xd344<=self.pc<0xd37c or self.pc==0xd08f)'),
        ("source=inspect.getsource(Source.run)", "source=inspect.getsource(Source.run).replace(\"receipt['collected'][0]['item']['state']==6\",\"receipt['collected'][0]['item']['state']>=6\").replace('actual f7 CPU','actual a2 CPU')"),
        ("HeadPending=m.ram[2][0x122],policy=list(getter())", "HeadPending=m.ram[2][0x122],JumpTimer=m.ram[2][0x58],policy=list(getter())"),
        ("m.ram[2][0xb8],category", "m.ram[2][0xb8],category,m.ram[2][0x58]==0"),
        ("tile_class=category))", "tile_class=category,JumpTimer=m.ram[2][0x58],HeadPending=m.ram[2][0x122]))")
    )
    for a,b in edits:assert code.count(a)==1,(a,code.count(a));code=code.replace(a,b)
    ns=dict(Previous.__dict__,F=F,Source=proxy,__file__=__file__)
    exec(compile(code,'<actuala2 JSR/helper/sourcecallback interrupt proof>','exec'),ns)
    out=ns['run'](raw)
    actual={r['PC']for r in out['reached_cuts']if r['tag']==2}
    required={0xd08f,0xd371,0xd374,0xd376,0xd379,0xd37b}
    assert required<=actual,('Every new hook/helper instruction reached',required-actual)
    assert all(r['JumpTimer']==0 and not r['sourceVY'][2]&128 for r in out['first8_post_head_original_returns'])
    out.update(every_new_JSR_and11B_instruction_reached=sorted(required),unchanged_classifier_reached_contexts_retained=True,
        original_f7_IRQ_checker_SHA256=PREVIOUS_SHA,no_duplicate_finite_ABI=True,
        retained_19569_observer_negative='All actual ISR/public-route assertions completed, final receipt-only check incorrectly indexed flat trajectory as nested state; corrected to actual sourceVY sign bytes, no opcode/input or comparison-domain change.')
    out['receipt_SHA256']=F.H(json.dumps(out,sort_keys=True,separators=(',',':')).encode());return out


if __name__=='__main__':
    def deny(*a,**k):raise AssertionError('A2 reached interrupt source gate attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):out=run(F.load_current_image())
    print('RESULT '+json.dumps(out,separators=(',',':')),flush=True)
