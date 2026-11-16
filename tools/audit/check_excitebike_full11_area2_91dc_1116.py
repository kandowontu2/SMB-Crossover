"""Strict current actual underground endpoint, no game or output writes."""
from pathlib import Path
from unittest.mock import patch
import argparse,json
import replay_excitebike_full11_area2_91dc_1116 as F
import check_smb1_alts_full11_1114 as Runner
import wwf_stock_source_model_1115 as Model

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--metadata',action='store_true');a=p.parse_args()
    raw=F.ROM.read_bytes();assert F.digest(raw)==F.PIN;opening=[]
    def deny(*args,**kw):raise AssertionError('Current Ex full source attempted artifacts/native')
    def cold(image,key):
        m,q=F.Current.cold(image,key,True);opening.append(q);return m
    def strict(image,key):
        original=Path.read_bytes
        def read(path):assert path.resolve()!=F.ROM.resolve(),'No mutable nightly reread';return original(path)
        with patch.object(Path,'read_bytes',read):q=F.metadata(image,key)
        for wrong in(image[:-1],F.Current.reference(image),bytes([image[0]^1])+image[1:]):
            try:F.controller(wrong,key)
            except AssertionError:pass
            else:raise AssertionError('Wrong full-route image accepted')
        q['readonly_metadata_wrong_image_rejections']=3;return q
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny),patch.object(Runner.Native,'run',deny),\
        patch.object(Runner,'Factory',F.family()),patch.object(Runner,'cold',cold),patch.object(Runner,'strict_metadata',strict):q=strict(raw,'excitebike')if a.metadata else Model.run(raw,'excitebike',8000)
    if opening:q['actual_cold_readback']=opening
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    if not a.metadata:assert q['passed'],'Current full1-1/25grounded underground1-2 remains unqualified'
