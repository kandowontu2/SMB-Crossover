"""Actual590 source execution of the frozen measured Flower boarding body."""
import json
from pathlib import Path
from unittest.mock import patch

import replay_gimmick_flower_board_prince_current_1115 as Factory
import check_gimmick_flower_board_current_1115 as Source


if __name__=='__main__':
    raw=Factory.ROM.read_bytes()
    def forbid(*args,**kwargs):raise RuntimeError('Actual590 Flower source attempted files/Mesen')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Source.Runner.Native,'run',forbid),patch.object(Source,'Factory',Factory),patch.object(Source.Runner,'Factory',Factory),patch.object(Source.Runner,'cold',Source.cold):
        q=Source.Runner.run(raw,'mr_gimmick',5000)
    r=q['receipt'];f=r.get('natural_flower',{})
    if q['passed']:
        ordered=[f[k]['state']['Main']for k in('opposite_launch','wall_reflection','real_support','support_jump','native')]
        assert ordered==sorted(ordered)and ordered[0]<ordered[-1],'Actual new-support/fresh-jump/collector chronology'
        assert f['support_count']>f['support_baseline']and f['resume']==25
    print('RESULT '+json.dumps(dict(passed=q['passed'],metadata=q['metadata'],receipt_SHA256=q['source_receipt_SHA256'],
        seconds=q['seconds'],completed_Main=r.get('Main_returned'),source_scheduler_passes=q['source_scheduler_passes'],reason=r.get('reason'),
        first_mushroom=r.get('first_mushroom_ready'),flower=f,terminal=r.get('terminal'),
        actual_Gm_movement_calls=r.get('Gm_movement_calls'),outputs=0,Mesen_run=False,gameplay_seeds=0),separators=(',',':')),flush=True)
    assert q['passed'],'Actual590 ordinary Flower boarding remains unqualified'
