"""Genuine classic DK current full-route source CPU qualification."""
import argparse
import json
from pathlib import Path
from unittest.mock import patch

import replay_dk_full11_current_1114 as Factory
import check_smb1_alts_full11_1114 as Runner
import check_shared_world_sprite_images_1114 as Cold


def cold(raw,key='donkey_kong'):
    with patch.object(Cold,'Factory',Factory):return Cold.cold(raw,key)


def run(raw,*,metadata=False):
    with patch.object(Runner,'Factory',Factory),patch.object(Runner,'cold',cold):
        return Runner.strict_metadata(raw,'donkey_kong')if metadata else Runner.run(raw,'donkey_kong',9000)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--metadata',action='store_true');a=p.parse_args()
    raw=Factory.ROM.read_bytes()
    def forbid(*args,**kwargs):raise RuntimeError('DK source route attempted files/Mesen')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Runner.Native,'run',forbid):
        q=run(raw,metadata=a.metadata)
    print(json.dumps(q,separators=(',',':')),flush=True)
    if not a.metadata:assert q['passed'],'Classic DK full source route remains unqualified'
