"""One same-control trace, bounded and no output artifacts."""
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import json
import replay_excitebike_head_trace_91dc_1116 as F
import check_smb1_alts_full11_1114 as Runner
import wwf_stock_source_model_1115 as Model

if __name__=='__main__':
    raw=F.ROM.read_bytes();assert F.digest(raw)==F.PIN
    def deny(*args,**kw):raise AssertionError('Readonly head trace attempted output/native')
    family=SimpleNamespace(W=F.W,N=F.N,controller=lambda raw,key:F.controller(raw),metadata=lambda raw,key:F.metadata(raw))
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny),patch.object(Runner.Native,'run',deny),\
        patch.object(Runner,'Factory',family),patch.object(Runner,'cold',F.Current.cold),patch.object(Runner,'strict_metadata',family.metadata):q=Model.run(raw,'excitebike',4900)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    assert not q['passed'],'Diagnostic policy unexpectedly changed outcome'
