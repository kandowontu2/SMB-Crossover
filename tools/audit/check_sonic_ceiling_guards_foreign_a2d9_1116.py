"""Newa2 owning public/lifecycle/shared-family wrapper; frozenf7 source retained."""
from pathlib import Path
from unittest.mock import patch
import argparse,inspect,json
import current_sonic_ceiling_complete_a2d9_1116 as F
import check_sonic_hidden_guards_foreign_f7c9_1116 as Previous

PREVIOUS_SHA='78215aa36a87d8a723dfa2201950cf2f542f230638d452d4a3b4f6f2ff85be6a'


def run(raw,kind='guards'):
    assert F.H(Path(Previous.__file__).read_bytes())==PREVIOUS_SHA
    ns=dict(Previous.__dict__,F=F,__file__=__file__)
    for name in('private','parentize','same','guards','foreign'):
        code=inspect.getsource(getattr(Previous,name)).replace('0x1344:0x1371','0x1344:0x137c').replace("b'\\xff'*45","b'\\xff'*56")
        if name=='private':
            a="rows[3][0x1b26:0x1b39]=F.C.OLD;rows[2][0x1344:0x137c]=b'\\xff'*56"
            b=a+"\n        assert rows[2][0x108f:0x1092]==F.C.HOOK;rows[2][0x108f:0x1092]=F.C.OLD_HOOK"
            assert code.count(a)==1;code=code.replace(a,b)
        if name=='parentize':
            a="m.ram[3][0x1b26:0x1b39]=F.C.OLD;m.ram[2][0x1344:0x137c]=b'\\xff'*56"
            b=a+"\n    m.ram[2][0x108f:0x1092]=F.C.OLD_HOOK"
            assert code.count(a)==1;code=code.replace(a,b)
        if name=='guards':code=code.replace('Only declared selector19/helper45','Only declared selector19/hook3/helper56')
        if name=='foreign':code=code.replace('bytes(m[self.pc:self.pc+45])','bytes(m[self.pc:self.pc+56])')
        exec(compile(code,'<new owninga2 exact94-byte public-family wrapper>','exec'),ns)
    out=ns[kind](raw);out['frozen_f7_checker_SHA256']=PREVIOUS_SHA
    out['receipt_SHA256']=F.H(json.dumps(out,sort_keys=True,separators=(',',':')).encode());return out


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--foreign',action='store_true');a=p.parse_args()
    def deny(*a,**k):raise AssertionError('Newa2 public/family source wrapper attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):out=run(F.load_current_image(),'foreign'if a.foreign else'guards')
    print('RESULT '+json.dumps(out,separators=(',',':')),flush=True)
