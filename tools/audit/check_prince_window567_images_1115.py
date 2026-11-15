"""Actual new-ROM cold plus ordinary pictures/accepted pickup source route."""
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import argparse,json
import compose_prince_window567_1115 as C
import replay_prince_window567_images_1115 as Factory
import check_shared_world_sprite_images_1114 as Shared


def run(parent):
    raw,composition=C.proposal(parent);receipts=[];loads=json.loads
    def capture(*args,**kwargs):
        q=loads(*args,**kwargs)
        if isinstance(q,dict)and'ROM_SHA256'in q and'physical_frames'in q and'normal_controller_only'in q:receipts.append(q)
        return q
    def strict(image,key):
        q=Factory.metadata(image,key);rejects=[]
        for name,wrong in(('parentAE',parent),('truncated',image[:-1]),('dirty_unowned',image[:100]+bytes([image[100]^1])+image[101:])):
            try:Factory.controller(wrong,key)
            except AssertionError:rejects.append(name)
            else:raise AssertionError('Unknown image accepted')
        q['strict_rejections']=rejects;return q
    with patch.object(Shared,'Factory',Factory),patch.object(Shared,'strict_metadata',strict),patch.object(Shared.json,'loads',capture):
        q=Shared.run(raw,'prince',2200)
    assert len(receipts)==1
    q['actual_accepted_pickup']=receipts[0].get('accepted_pickup');q['composition']=composition
    q['actual_first_publish_readback']=receipts[0].get('first_publish_readback')
    if q['metadata'].get('first_BBC1_fullcookie_and3174plus3plus2_readback'):
        readback=q['actual_first_publish_readback'];assert readback and readback['both16byte_cookies']
        assert sorted(row['bytes']for row in readback['static_graphics_extents'])==[2,3,3174]
    if q['passed']:
        pickup=q['actual_accepted_pickup'];assert pickup['accepted']and pickup['carry']==1 and pickup['erased']and pickup['floatey_control']==6
        assert q['terminal']['Main_returns']-pickup['completed']>=25
        assert q['terminal']['original_commits']-pickup['commit']>=25
        assert q['terminal']['prince_hp']==pickup['after']['prince_hp']and q['terminal']['lives']==2
    q['receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return q


def compact(q):
    keys=('passed','identity','metadata','source_Main_passes','source_receipt_SHA256','receipt_SHA256','reason','terminal',
        'actual_accepted_pickup','actual_first_publish_readback','gameplay_seeds','outputs','Mesen_run','renderer','scope')
    result={key:q.get(key)for key in keys}
    result['source_spots']=[{key:shot[key]for key in('tag','state','target','actual_sprite_banks')}for shot in q.get('shots',[])]
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--verified',action='store_true');args=parser.parse_args()
    if args.verified:import replay_prince_window567_verified_images_1115 as Factory
    def deny(*args,**kwargs):raise AssertionError('Source pictures attempted file output or launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        q=run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
    print(json.dumps(compact(q),separators=(',',':')),flush=True)
    if not q['passed']:raise SystemExit(1)
