"""Read root's compact same-cut riser5 receipt without writing decoded files."""
from hashlib import sha256
from pathlib import Path
import base64
import json
import zlib


def main():
    path=Path(__file__).resolve().parents[2]/'docs/qa/dkjr-stair-projection-native-1113.json'
    receipt=json.loads(path.read_text())
    data=zlib.decompress(base64.b64decode(receipt['trace_zlib_base64']))
    assert sha256(data).hexdigest()==receipt['trace_SHA256']=='7bc1b4044d127327f925e2cf38991b24db77c50b7d53089e8b6a8c0d7298c50f'
    assert len(data)==receipt['trace_bytes']==66134
    rows=json.loads(data);assert len(rows)==60
    selected=[r for r in rows if r.get('Main')==8947 or r.get('riser_attempt')==1]
    keys=('Main','frame','event','PC','A','X','Y','SP','x','y','source','prior','riser_attempt',
        'source_x','source_y','facing','direction','jump_age','rect','query','kind2_list',
        'kind3_list','native_box','write_address','write_value','code_map','code_bytes','return_stack')
    for row in selected:
        print('DKJR_NATIVE_STAIR_ROW '+json.dumps({k:row[k]for k in keys if k in row},separators=(',',':')),flush=True)
    print('DKJR_NATIVE_STAIR_SCOPE '+json.dumps(dict(trace_SHA256=sha256(data).hexdigest(),
        rows=60,selected=len(selected),receipt_SHA256=receipt['receipt_SHA256'],
        outputs_written=0,ROM_or_game_writes=False),separators=(',',':')),flush=True)


if __name__=='__main__':main()
