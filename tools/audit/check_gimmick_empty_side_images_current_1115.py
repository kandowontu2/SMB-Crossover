"""Strict graphics observer API and ordinary source path, no real screenshots."""
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import json
import compose_gimmick_empty_side_1115 as C
import replay_gimmick_empty_side_images_current_1115 as F
import check_shared_world_sprite_images_1114 as Source


if __name__=='__main__':
    actual=C.ROM.read_bytes();raw,proposal=C.current_proposal(actual)
    def forbid(*args,**kwargs):raise AssertionError('Gimmick image source attempted files/Mesen')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Source.Native,'run',forbid),patch.object(Source,'Factory',F):
        metadata=Source.strict_metadata(raw,'mr_gimmick');q=Source.run(raw,'mr_gimmick',1800)
    result=dict(passed=q['passed'],factory_SHA256=sha256(Path(F.__file__).read_bytes()).hexdigest(),metadata=metadata,
        source=q,actual_renderer_pngs=False,outputs=0,Mesen_run=False)
    result['receipt_SHA256']=sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    print('RESULT '+json.dumps(result,separators=(',',':')),flush=True)
    assert result['passed'],'Gimmick opening source observations remain unqualified'
