"""Execute strict actualae66 Flower-boarding replay, no files or Mesen."""
import json
from pathlib import Path
from unittest.mock import patch
import replay_gimmick_flower_board_current_1115 as Factory
import check_mr_gimmick_full11_current_1114 as Original
import check_smb1_alts_full11_1114 as Runner


def cold(raw,key):
    with patch.object(Original,'Factory',Factory):return Original.cold(raw,key)


if __name__=='__main__':
    raw=Factory.ROM.read_bytes()
    def forbid(*args,**kwargs):raise RuntimeError('Actualcurrent Gimmick Flower source attempted files/Mesen')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Runner.Native,'run',forbid),patch.object(Runner,'Factory',Factory),patch.object(Runner,'cold',cold):
        q=Runner.run(raw,'mr_gimmick',5000)
    r=q['receipt'];f=r.get('natural_flower',{})
    print('RESULT '+json.dumps(dict(passed=q['passed'],metadata=q['metadata'],receipt_SHA256=q['source_receipt_SHA256'],
        seconds=q['seconds'],completed_Main=r.get('Main_returned',r.get('completed_Main',r.get('Main'))),source_scheduler_passes=q['source_scheduler_passes'],reason=r.get('reason'),
        first_mushroom=r.get('first_mushroom_ready'),flower=f,terminal=r.get('terminal'),
        actual_Gm_movement_calls=r.get('Gm_movement_calls'),outputs=0,Mesen_run=False,gameplay_seeds=0),separators=(',',':')),flush=True)
    assert q['passed'],'Actualae66 ordinary Flower boarding remains unqualified'
