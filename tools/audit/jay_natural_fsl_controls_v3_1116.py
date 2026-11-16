"""Ordinary controls using the actual native25 import support contract."""
from pathlib import Path
from unittest.mock import patch
import argparse,json
import jay_natural_fsl_controls_v2_1116 as V2

Base,J=V2.Base,V2.J
V2_SHA='e934706d99b0fc6668dc1782b9e285434a987f2b33889a617deea679ec19eeaf'
SYNC_SHA='6c53700f354fd563c7c07a5b8ef4f74b2bcd21a650abce64fce8f62e0dd929d6'


def text():
    assert J.H(Path(V2.__file__).read_bytes())==V2_SHA
    assert J.H((J.R/'tools/reference/jay_silius_native_sync_1111.s').read_bytes())==SYNC_SHA
    s=V2.text()
    def support(p):
        return f's.native_state==0 and s.native_vy==0 and s.native_yhigh==1 and {p}.yhigh==1 and {p}.y<208'
    edits=(
        ('local boarded=lift and lift.contact==lift.slot and y+32==lift.y and g and lift.y<208',
         'local boarded=lift and lift.contact==lift.slot and y+32==lift.y and '+support('lift')),
        ('p3.contact==p3.slot and y+32==p3.y and g','p3.contact==p3.slot and y+32==p3.y and '+support('p3')),
        ('p4.contact==p4.slot and y+32==p4.y and g','p4.contact==p4.slot and y+32==p4.y and '+support('p4')),
    )
    for old,new in edits:assert s.count(old)==1,(old,s.count(old));s=s.replace(old,new)
    return s


def run(raw,kind,limit):
    body=text()
    class Recipe:
        @staticmethod
        def read_text():return body
        @staticmethod
        def read_bytes():return body.encode()
    with patch.object(Base,'POLICY',Recipe):q=Base.run(raw,kind,limit)
    q.update(control_successor='v3 actual native25 support admission',failed_v2_module_SHA256=V2_SHA,
        native_sync_source_SHA256=SYNC_SHA,source_checker_SHA256=J.H(Path(Base.__file__).read_bytes()),
        control_module_SHA256=J.H(Path(__file__).read_bytes()))
    q['receipt_SHA256']=J.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--kind',choices=('flower','star','life'),required=True);p.add_argument('--limit',type=int,default=1800);a=p.parse_args()
    assert 100<=a.limit<=2600
    raw=J.load_current_image()
    def deny(*a,**kw):raise AssertionError('Jay v3 source controller attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(raw,a.kind,a.limit)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
