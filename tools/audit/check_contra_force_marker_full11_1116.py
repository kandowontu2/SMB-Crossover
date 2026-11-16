"""Zero-output current CF full routes using preserved completed-return policy."""
from pathlib import Path
from unittest.mock import patch
import argparse,json
import replay_contra_force_marker_full11_1116 as F
import check_smb1_alts_full11_1114 as Harness

C=F.C


def run(raw,key,metadata=False):
    if metadata:return F.metadata(raw,key)
    with patch.object(Harness,'Factory',F),patch.object(Harness,'cold',F.Model.cold):
        result=Harness.run(raw,key,10000)
    assert result['passed'],('Current CF full route negative',key,result)
    return result


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--identity',choices=F.IDENTITIES,required=True);ap.add_argument('--metadata',action='store_true');args=ap.parse_args()
    parent=C.load_current_image();raw,_=C.proposal(parent)
    def deny(*a,**kw):raise AssertionError('Current CF full route attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(raw,args.identity,args.metadata)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
