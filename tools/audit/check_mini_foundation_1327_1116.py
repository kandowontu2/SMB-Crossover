"""One strict typed current metadata/cold16 check; never an item route."""
from pathlib import Path
from unittest.mock import patch
import argparse,json
import current_mini_stock_1327_1116 as C
import run_stdout_mesen_1110 as Native

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--metadata',action='store_true');a=p.parse_args();raw=C.ROM.read_bytes();original_read=Path.read_bytes
    def deny(*args,**kw):raise AssertionError('Current Mini foundation attempted artifacts/native')
    def read(path):
        assert path.resolve()!=C.ROM.resolve(),'Mutable Downloads reread after input capture'
        return original_read(path)
    with patch.object(Path,'read_bytes',read),patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny),patch.object(Native,'run',deny):
        q=C.metadata(raw);rejected=[];wrong=bytearray(raw);wrong[16+8192]^=1
        for name,image in(('00bb_parent',C.reference(raw)),('truncated',raw[:-1]),('unowned_change',bytes(wrong))):
            try:C.bindings(image)
            except AssertionError:rejected.append(name)
            else:raise AssertionError(('Wrong image admitted',name))
        if not a.metadata:_,q['actual_cold']=C.cold(raw,True)
    q.update(passed=True,strict_rejections=rejected,facade_SHA256=C.H(Path(C.__file__).read_bytes()),mutable_Downloads_rereads=0,gameplay_seeds=0,source_item_route=False,Mesen_run=False)
    q['receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode());print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
