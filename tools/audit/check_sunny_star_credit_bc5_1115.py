"""Actual bc5 original CPU Star and25 returned Sunny updates, no files."""
from pathlib import Path
from unittest.mock import patch
import json
import replay_sunny_star_credit_bc5_1115 as F
import check_smb1_alts_full11_1114 as Runner
import wwf_stock_source_model_1115 as Model
if __name__=='__main__':
    raw=F.ROM.read_bytes()
    def deny(*a,**kw):raise AssertionError('Sunny stock source attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny),patch.object(Runner.Native,'run',deny),\
        patch.object(Runner,'Factory',F),patch.object(Runner,'cold',F.Current.cold),patch.object(Runner,'strict_metadata',F.metadata):q=Model.run(raw,'star',1800)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    assert q['passed'],'Sunny actual delayed Star credit/25 returns did not qualify'
