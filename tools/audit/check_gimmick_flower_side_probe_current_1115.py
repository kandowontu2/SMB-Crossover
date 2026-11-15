"""Strict API/source reconstruction/compile gates for passive side diagnostics."""
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch
import replay_gimmick_flower_side_probe_current_1115 as Factory
import check_smb1_alts_full11_1114 as Source


if __name__=='__main__':
    raw=Factory.ROM.read_bytes()
    def forbid(*args,**kwargs):raise RuntimeError('Side diagnostic attempted files/Mesen')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Source.Native,'run',forbid),patch.object(Source,'Factory',Factory):
        q=Source.strict_metadata(raw,'mr_gimmick');c=Factory.bindings(raw)
        assert all(raw[16+h['offset']:16+h['offset']+len(h['bytes'])]==bytes(h['bytes'])for h in c['hooks'].values())
    result=dict(passed=True,metadata=q,diagnostic_hooks={k:v for k,v in c['hooks'].items()if k in('GmSideProbeEnter','GmSideProbeReturn','NativeSideStop','SharedWallEnter','SharedLeftClamp')},outputs=0,Mesen_run=False,gameplay_run=False)
    result['receipt_SHA256']=sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    print('RESULT '+json.dumps(result,separators=(',',':')),flush=True)
