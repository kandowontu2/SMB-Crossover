"""Same controls, original state>=6 collection; retain overstrict bit7 negative."""
from pathlib import Path
from unittest.mock import patch
import argparse,inspect,json,re
import check_sonic_hidden_natural_life_f7c9_1116 as Previous

F=Previous.F
PREVIOUS_SHA='5250ef4b48e39111eeb169ee93c39666f94a876e1fe72239049a47732671b35e'


def run(raw,form='sonic',limit=1200):
    assert F.H(Path(Previous.__file__).read_bytes())==PREVIOUS_SHA
    q=F.bindings(raw);source=(F.R/'src/object.s').read_text()
    admission=source.split('ChkPUSte:  lda Enemy_State,x',1)[1].split('RunPUSubs:',1)[0]
    assert 'cmp #$06' in admission and 'bcc ExitPUp' in admission
    at=q['fields']['Enemy_State'];prefix=(bytes([0xb5,at])if at<256 else b'\xbd'+at.to_bytes(2,'little'))+b'\xc9\x06\x90'
    sites=[m.start()for m in re.finditer(re.escape(prefix),raw[16:1048592])]
    assert sites,'Actual current original state6 admission compare'
    code=inspect.getsource(Previous.run)
    old="assert mature and collect and sounds[64]and not reset,'Mature physical1UP, realcredit/cue and no reset'"
    new="assert collect and collect[0]['actor']['state']>=6 and sounds[64]and not reset,'Original state6 admission, realcredit/cue and no reset'"
    assert code.count(old)==1;code=code.replace(old,new)
    ns=dict(Previous.__dict__,__file__=__file__);exec(compile(code,'<original state6 owning1UP admission>','exec'),ns)
    out=ns['run'](raw,form,limit)
    out.update(retained_overstrict_bit7_fixture_negative='6d5a75065b63569538850ee70d522d1b6f5e5d7a6b4c482b88cb94511ccf3d7c',
        original_policy='Original ChkPUSte admits state>=6 before highbit128. Physical actual collector entry/erase/popup/cue, delayed INC and25returnedworkers stay mandatory.',
        actual_original_admission_sites=[dict(file=16+i,first12=raw[16+i:28+i].hex())for i in sites],
        original_object_source_SHA256=F.H((F.R/'src/object.s').read_bytes()),unmodified_policy_SHA256=F.H(Previous.Policy.text().encode()))
    out['receipt_SHA256']=F.H(json.dumps(out,sort_keys=True,separators=(',',':')).encode());return out


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--form',choices=tuple(F.FORMS),default='sonic');p.add_argument('--limit',type=int,default=1200);a=p.parse_args();assert 500<=a.limit<=1500
    def deny(*a,**k):raise AssertionError('Source life admission attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(F.load_current_image(),a.form,a.limit)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
