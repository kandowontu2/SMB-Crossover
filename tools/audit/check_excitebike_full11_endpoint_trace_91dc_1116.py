"""One full-route observer diagnostic, bounded and source only."""
from pathlib import Path
from unittest.mock import patch
import json
import replay_excitebike_full11_endpoint_trace_91dc_1116 as F
import check_smb1_alts_full11_1114 as Runner
import wwf_stock_source_model_1115 as Model

if __name__=='__main__':
    raw=F.ROM.read_bytes();assert F.digest(raw)==F.PIN
    def deny(*args,**kw):raise AssertionError('Current Ex diagnostic attempted artifacts/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny),patch.object(Runner.Native,'run',deny),\
        patch.object(Runner,'Factory',F.family()),patch.object(Runner,'cold',F.Current.cold),patch.object(Runner,'strict_metadata',F.metadata):q=Model.run(raw,'excitebike',4600)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    assert not q['passed']and q['receipt'].get('route',{}).get('endpoint_gate'),'Expected one explicit observer diagnostic, not stage qualification'
