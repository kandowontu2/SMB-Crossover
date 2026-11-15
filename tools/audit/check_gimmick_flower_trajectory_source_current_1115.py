"""Genuine current590 source trajectory comparison for passive native diagnostic."""
import json
from pathlib import Path
from unittest.mock import patch
import replay_gimmick_flower_trajectory_current_1115 as Factory
import check_gimmick_flower_board_current_1115 as Source


def compact(q):
    return{k:q.get(k)for k in('Main','frame','x','y','GmVX','source_vy','source_ground','hero_x16','hero_y16','star_x16','star_y16','star_vx','star_vy','star_flags','SavedJoypadBits','GmFresh','GmPrevious','GmClock','requested_bits','last_polled_bits','read_serial','poll_serial','PC','SP','power','native_box')}


if __name__=='__main__':
    raw=Factory.ROM.read_bytes()
    def forbid(*args,**kwargs):raise RuntimeError('Flower trajectory source attempted files or Mesen')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Source.Runner.Native,'run',forbid),patch.object(Source,'Factory',Factory),patch.object(Source.Runner,'Factory',Factory),patch.object(Source.Runner,'cold',Source.cold):
        q=Source.Runner.run(raw,'mr_gimmick',2500)
    r=q['receipt'];f=r.get('natural_flower',{});t=f.get('trajectory_diagnostic',{})
    result=dict(passed=q['passed'],receipt_SHA256=q['source_receipt_SHA256'],controller_SHA256=q['metadata']['controller_SHA256'],
        Main=r.get('Main_returned'),reason=r.get('reason'),seconds=q['seconds'],
        returns=[compact(row)for row in t.get('returns',[])],rides=[dict(entry=compact(row['entry']),returned=compact(row['returned']))for row in t.get('rides',[])],
        borrowed=[compact(row)for row in t.get('borrowed',[])],terminal=r.get('terminal'),outputs=0,Mesen_run=False)
    print('RESULT '+json.dumps(result,separators=(',',':')),flush=True)
    assert q['passed'],'Passive Flower source comparison failed its unchanged gameplay gates'
