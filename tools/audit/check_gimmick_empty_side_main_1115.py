"""Combined actual16a+Gimmick normal-controls source regressions, no outputs."""
from hashlib import sha256
import argparse,json
from pathlib import Path
from unittest.mock import patch
import compose_gimmick_empty_side_1115 as C
import replay_gimmick_empty_side_current_1115 as Factory
import check_gimmick_flower_board_current_1115 as Source


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--case',choices=tuple(Factory.SOURCES)+('all',),default='flower');args=p.parse_args()
    actual=C.ROM.read_bytes();raw,proposal=C.current_proposal(actual);assert C.current_inverse(raw)==actual
    rows=[]
    def forbid(*args,**kwargs):raise RuntimeError('Combined Gimmick source attempted files/Mesen')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Source.Runner.Native,'run',forbid),patch.object(Source,'Factory',Factory),patch.object(Source.Runner,'Factory',Factory),patch.object(Source.Runner,'cold',Source.cold):
        for key in Factory.SOURCES if args.case=='all'else(args.case,):
            q=Source.Runner.run(raw,key,3000);r=q['receipt']
            rows.append(dict(key=key,passed=q['passed'],receipt_SHA256=q['source_receipt_SHA256'],metadata=q['metadata'],Main=r.get('Main_returned'),actual_Gm_movement_calls=r.get('Gm_movement_calls'),
                reason=r.get('reason'),seconds=q['seconds'],terminal=r.get('terminal'),Flower=r.get('natural_flower')if key=='flower'else None,stock=r.get('stock_oneup'if key=='oneup'else'stock_star')if key!='flower'else None))
            print('CASE '+json.dumps(rows[-1],separators=(',',':')),flush=True)
    result=dict(passed=all(q['passed']for q in rows),actual_input16a_SHA256=sha256(actual).hexdigest(),runtime_SHA256=sha256(raw).hexdigest(),proposal=proposal,rows=rows,outputs=0,Mesen_run=False,gameplay_seeds=0)
    result['receipt_SHA256']=sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    print('RESULT '+json.dumps(result,separators=(',',':')),flush=True)
    assert result['passed'],'Combined current Gimmick source regression remains unqualified'
