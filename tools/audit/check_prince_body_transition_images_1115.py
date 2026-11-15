"""Actual16a ordinary Goomba/Mushroom/pickup source regression; no renderer."""
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import json
import compose_prince_body_transition_590_1115 as C
import replay_prince_body_transition_images_1115 as Factory
import check_shared_world_sprite_images_1114 as Shared
import check_prince_window567_images_1115 as Previous


def run(parent):
    raw,composition=C.proposal(parent);receipts=[];loads=json.loads
    def capture(*args,**kwargs):
        value=loads(*args,**kwargs)
        if isinstance(value,dict)and'ROM_SHA256'in value and'physical_frames'in value and'normal_controller_only'in value:receipts.append(value)
        return value
    def strict(image,key):
        reader=Path.read_bytes
        def read(path,*args,**kwargs):
            assert path.resolve()!=Factory.ROM.resolve(),'Mutable Downloads reread'
            return reader(path,*args,**kwargs)
        with patch.object(Path,'read_bytes',read):
            q=Factory.metadata(image,key)
        rejects=[]
        for label,wrong in(('parent590',parent),('truncated',image[:-1]),('dirty_unowned',image[:100]+bytes([image[100]^1])+image[101:])):
            try:Factory.controller(wrong,key)
            except AssertionError:rejects.append(label)
            else:raise AssertionError('Unknown image accepted')
        q.update(strict_rejections=rejects,mutable_Downloads_rereads=0)
        print(json.dumps(dict(event='actual16a-images-metadata',**q),separators=(',',':')),flush=True)
        return q
    with patch.object(Shared,'Factory',Factory),patch.object(Shared,'strict_metadata',strict),patch.object(Shared.json,'loads',capture):
        q=Shared.run(raw,'prince',2200)
    assert len(receipts)==1;receipt=receipts[0]
    q.update(actual_accepted_pickup=receipt.get('accepted_pickup'),composition=composition,
        actual_first_publish_readback=receipt.get('first_publish_readback'),actual_CPU_ROM_SHA256=C.CANDIDATE,
        no_source_array_mounts=True,frozen590_controller_body_preserved=True)
    if q['passed']:
        pub=q['actual_first_publish_readback'];assert pub and pub['both16byte_cookies']
        assert sorted(row['bytes']for row in pub['static_graphics_extents'])==[2,3,180,219,449,3174]
        pickup=q['actual_accepted_pickup'];assert pickup['accepted']and pickup['carry']==1 and pickup['erased']and pickup['floatey_control']==6
        assert q['terminal']['Main_returns']-pickup['completed']>=25
        assert q['terminal']['original_commits']-pickup['commit']>=25
        assert q['terminal']['prince_hp']==pickup['after']['prince_hp']and q['terminal']['lives']==2
    q['receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return q


if __name__=='__main__':
    def deny(*args,**kwargs):raise AssertionError('Source graphics/Mushroom regression attempted output or launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        q=run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
    print(json.dumps(Previous.compact(q),separators=(',',':')),flush=True)
    if not q['passed']:raise SystemExit(1)
