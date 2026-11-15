"""Actual current590 ordinary Gimmick Star, no files/Mesen."""
import json
from pathlib import Path
from unittest.mock import patch
import replay_gimmick_natural_star_current_1115 as Factory
import check_gimmick_flower_board_current_1115 as Source


if __name__=='__main__':
    raw=Factory.ROM.read_bytes()
    def forbid(*args,**kwargs):raise RuntimeError('Gimmick Star attempted files or Mesen')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Source.Runner.Native,'run',forbid),patch.object(Source,'Factory',Factory),patch.object(Source.Runner,'Factory',Factory),patch.object(Source.Runner,'cold',Source.cold):
        q=Source.Runner.run(raw,'mr_gimmick',2800)
    r=q['receipt']
    print('RESULT '+json.dumps(dict(passed=q['passed'],metadata=q['metadata'],receipt_SHA256=q['source_receipt_SHA256'],
        seconds=q['seconds'],completed_Main=r.get('Main_returned'),reason=r.get('reason'),first_mushroom=r.get('first_mushroom_ready'),
        stock_star=r.get('stock_star'),actual_Gm_movement_calls=r.get('Gm_movement_calls'),terminal=r.get('terminal'),outputs=0,Mesen_run=False,gameplay_seeds=0),separators=(',',':')),flush=True)
    assert q['passed'],'Gimmick natural current Star remains source-unqualified'
