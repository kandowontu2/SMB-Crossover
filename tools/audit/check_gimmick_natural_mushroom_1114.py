"""Zero-output source execution of the exactf11 ordinary Gimmick collector."""
import argparse,json
from pathlib import Path
from unittest.mock import patch
import replay_gimmick_natural_mushroom_1114 as Factory
import check_mr_gimmick_full11_current_1114 as Original
import check_smb1_alts_full11_1114 as Runner


def cold(raw,key):
    with patch.object(Original,'Factory',Factory):return Original.cold(raw,key)


def run(raw,metadata=False):
    with patch.object(Runner,'Factory',Factory),patch.object(Runner,'cold',cold):
        return Runner.strict_metadata(raw,'mr_gimmick')if metadata else Runner.run(raw,'mr_gimmick',2400)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--metadata',action='store_true');a=p.parse_args();raw=Factory.ROM.read_bytes()
    def forbid(*args,**kwargs):raise RuntimeError('Gimmick natural source checker attempted file/Mesen output')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Runner.Native,'run',forbid):q=run(raw,a.metadata)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    if not a.metadata:assert q['passed'],'Ordinary Gimmick mushroom route remains unqualified'
