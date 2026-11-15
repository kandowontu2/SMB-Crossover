"""Normal-input full current7a80 Flower successor source, no files/Mesen."""
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import argparse,json
import compose_gimmick_empty_side_1115 as C
import replay_gimmick_empty_side_flower_current_1115 as F
import check_gimmick_flower_board_current_1115 as Source


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--metadata',action='store_true');args=p.parse_args()
    actual=C.ROM.read_bytes();raw=C.current_proposal(actual)[0]if sha256(actual).hexdigest()!=C.CURRENT_CANDIDATE else actual
    assert sha256(raw).hexdigest()==C.CURRENT_CANDIDATE
    def forbid(*args,**kwargs):raise AssertionError('Gimmick Flower successor attempted files/Mesen')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Source.Runner.Native,'run',forbid),patch.object(Source,'Factory',F),patch.object(Source.Runner,'Factory',F),patch.object(Source.Runner,'cold',Source.cold):
        if args.metadata:
            metadata=Source.Runner.strict_metadata(raw,'mr_gimmick')
            print('API '+json.dumps(dict(passed=True,metadata=metadata,factory_SHA256=sha256(Path(F.__file__).read_bytes()).hexdigest(),outputs=0,Mesen_run=False),separators=(',',':')),flush=True)
            raise SystemExit(0)
        q=Source.Runner.run(raw,'mr_gimmick',3000)
    r=q['receipt'];result=dict(passed=q['passed'],metadata=q['metadata'],receipt_SHA256=q['source_receipt_SHA256'],Main=r.get('Main_returned'),
        Gm=r.get('Gm_movement_calls'),reason=r.get('reason'),Flower=r.get('natural_flower'),terminal=r.get('terminal'),seconds=q['seconds'],outputs=0,Mesen_run=False,gameplay_seeds=0)
    print('RESULT '+json.dumps(result,separators=(',',':')),flush=True)
    assert q['passed'],'New braking navigation remains unqualified'
