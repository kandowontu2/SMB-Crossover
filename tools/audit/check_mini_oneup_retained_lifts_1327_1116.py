"""One current source L run; optional exact single-file input provenance check."""
from pathlib import Path
from unittest.mock import patch
import argparse,json
import replay_mini_oneup_retained_lifts_1327_1116 as F
import check_smb1_alts_full11_1114 as Runner
import wwf_stock_source_model_1115 as Model

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--metadata',action='store_true');p.add_argument('--verify-input-reference',action='store_true');a=p.parse_args();raw=F.ROM.read_bytes();opening=[];reference=False
    if a.verify_input_reference:
        path=F.R/'build/complete-roster-native-1110/packets/regression/mini/controller.lua';data=path.read_bytes();assert F.H(data)==F.RETAINED_SHA
        text=data.decode();fragment=text[text.index('local mini_lift_left ='):text.index('local function route_tick(s)')].rstrip()+'\n'
        assert fragment==F.LIFT_POLICY;reference=True
    def deny(*args,**kw):raise AssertionError('Mini retained-lift L attempted artifacts/native')
    def cold(image,key):m,q=F.Current.cold(image,True);opening.append(q);return m
    family=F.family()
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny),patch.object(Runner.Native,'run',deny),patch.object(Runner,'Factory',family),patch.object(Runner,'cold',cold),patch.object(Runner,'strict_metadata',family.metadata):
        q=family.metadata(raw,'mini')if a.metadata else Model.run(raw,'mini',4300)
    if not a.metadata:q['actual_cold']=opening
    q['single_immutable_input_reference_verified']=reference
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    if not a.metadata:assert q['passed'],'Exact natural Mini hidden1UP remains unqualified'
