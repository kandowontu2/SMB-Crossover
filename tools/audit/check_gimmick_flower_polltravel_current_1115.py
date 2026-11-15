"""Actual590 Flower route with qualified pipe handshakes, no files/Mesen."""
import json
from pathlib import Path
from unittest.mock import patch

import replay_gimmick_flower_polltravel_current_1115 as Factory
import check_gimmick_flower_board_current_1115 as Source


if __name__=='__main__':
    raw=Factory.ROM.read_bytes()
    def forbid(*args,**kwargs):raise RuntimeError('Flower poll-travel source attempted files/Mesen')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Source.Runner.Native,'run',forbid),patch.object(Source,'Factory',Factory),patch.object(Source.Runner,'Factory',Factory),patch.object(Source.Runner,'cold',Source.cold):
        q=Source.Runner.run(raw,'mr_gimmick',3000)
    r=q['receipt'];t=r.get('travel_input_diagnostic',{});f=r.get('natural_flower',{})
    print('RESULT '+json.dumps(dict(passed=q['passed'],metadata=q['metadata'],receipt_SHA256=q['source_receipt_SHA256'],
        seconds=q['seconds'],completed_Main=r.get('Main_returned'),reason=r.get('reason'),first_mushroom=r.get('first_mushroom_ready'),
        Flower=f,travel={k:t.get(k)for k in('polls','reads','A_requests','A_admissions','A_retries','B_retries','support_serial','first_support','last_support','first_admission','last_admission','flower_admissions','trace')},
        terminal=r.get('terminal'),outputs=0,Mesen_run=False),separators=(',',':')),flush=True)
    assert q['passed'],'Actual590 Flower poll-travel route remains source-unqualified'
