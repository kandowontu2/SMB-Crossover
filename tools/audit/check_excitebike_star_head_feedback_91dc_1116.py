"""Current ordinary responsive head admission; no artifacts or native run."""
from pathlib import Path
from unittest.mock import patch
import argparse,json
import replay_excitebike_star_head_feedback_91dc_1116 as F
import check_smb1_alts_full11_1114 as Runner
import wwf_stock_source_model_1115 as Model

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--metadata',action='store_true');a=p.parse_args()
    raw=F.ROM.read_bytes();assert F.digest(raw)==F.PIN;opening=[]
    def deny(*args,**kw):raise AssertionError('Excitebike source attempted output/native')
    def cold(image,key):
        m,q=F.Current.cold(image,key,True);opening.append(q);return m
    def strict(image,key):
        q=F.metadata(image,'star')
        for wrong in(image[:-1],F.Current.reference(image),bytes([image[0]^1])+image[1:]):
            try:F.controller(wrong)
            except AssertionError:pass
            else:raise AssertionError('Wrong current Star image accepted')
        q['wrong_image_rejections']=3;return q
    family=F.family()
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny),patch.object(Runner.Native,'run',deny),\
        patch.object(Runner,'Factory',family),patch.object(Runner,'cold',cold),patch.object(Runner,'strict_metadata',strict):q=strict(raw,'star')if a.metadata else Model.run(raw,'excitebike',4900)
    if opening:q['actual_cold_readback']=opening
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    if not a.metadata:assert q['passed'],'Actual responsive Star lifecycle/credit/25 remains unqualified'
