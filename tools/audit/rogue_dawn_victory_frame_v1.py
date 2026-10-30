"""Extract one checksum-verified castle-walk frame, without a frame tree."""
from pathlib import Path
import csv
import hashlib
import json
import sys

R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from final_inventory_compact_capture_v1 import HEADER,decode,word_fnv
from current_roster_compact_11_v1 import png

O=R/'build/verification/rogue-dawn-victory-native-easy-v1'


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    assert not (O/'actual-victory-walk.json').exists()
    ready=json.loads((O/'ready.json').read_text())
    result=json.loads((O/'result.json').read_text())
    assert result['passed'] and result['ROM_sha256']==ready['ROM_sha256']
    row=next(z for z in csv.DictReader((O/'trace.csv').open())
             if z['engine']=='5' and z['world']=='0' and z['level']=='0' and int(z['x'])>=3210)
    ordinal=int(row['captured'])
    records=[json.loads(z)for z in (O/'captures-index.jsonl').open()]
    record=next(z for z in records if z['type']=='record' and z['kind']==1 and z['full_ordinal']==ordinal)
    assert record['stamp']['ppu_frame']==int(row['ppu_frame'])
    assert record['mode'] in [0,1], 'Direct extraction requires a non-XOR full record'
    with (O/'captures.nesppuv1').open('rb') as f:
        f.seek(record['offset'])
        header=f.read(HEADER.size)
        kind,mode,reserved,sequence,meta_bytes,payload_bytes,checksum=HEADER.unpack(header)
        meta=json.loads(f.read(meta_bytes))
        raw=decode(mode,f.read(payload_bytes),None,meta['decoded_bytes'])
        assert sequence==record['record'] and checksum==word_fnv(raw)==record['word_fnv1a32']
        assert kind==1 and not reserved and meta['stamp']==record['stamp']
    image=O/'actual-victory-walk.png'
    png(image,[raw])
    proof=dict(source='Actual engine5 castle movement whole PPU frame; not an asset render or seeded fixture.',
               native_passed=True,visual_review=False,trace=row,record=record,
               raw_sha256=hashlib.sha256(raw).hexdigest(),PNG_sha256=sha(image),
               ROM_sha256=result['ROM_sha256'],selected_image_count_with_marker_sheet=8,
               bindings={str(p):sha(p)for p in [Path(__file__),O/'ready.json',O/'result.json',
                   O/'trace.csv',O/'captures-index.jsonl',O/'captures.nesppuv1']})
    (O/'actual-victory-walk.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(dict(image=str(image),frame=row['frame'],x=row['x'],y=row['y'],PNG_sha256=sha(image))))


if __name__=='__main__':main()
