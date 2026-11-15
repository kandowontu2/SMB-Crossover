"""Genuine current Honky existing-helper gap/Star continuation source."""
from pathlib import Path
from unittest.mock import patch
import json
import replay_wwf_honky_star_gap_7a80_1115 as F
import check_smb1_alts_full11_1114 as Runner
import check_shared_world_sprite_images_1114 as Cold
import wwf_stock_source_model_1115 as Model


if __name__=='__main__':
    raw=F.ROM.read_bytes();factory=F.family()
    def forbid(*args,**kwargs):raise AssertionError('Honky source attempted files/Mesen')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Runner.Native,'run',forbid),patch.object(Runner,'Factory',factory),patch.object(Cold,'Factory',factory),patch.object(Runner,'cold',Cold.cold):
        q=Model.run(raw,'honky',4700)
    r=q['receipt'];result=dict(passed=q['passed'],metadata=q['metadata'],receipt_SHA256=q['source_receipt_SHA256'],Main=r.get('Main_returns'),Wf=r.get('WfMovement_calls'),reason=r.get('reason'),
        stock=r.get('natural_stock'),items=r.get('items'),events=r.get('events'),power_changes=r.get('power_changes'),terminal=r.get('terminal'),seconds=q['seconds'],outputs=0,Mesen_run=False)
    print('RESULT '+json.dumps(result,separators=(',',':')),flush=True)
    assert q['passed'],'Honky later-edge/helper stock route remains source-unqualified'
