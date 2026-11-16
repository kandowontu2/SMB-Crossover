"""Readonly compiled menu and current native Toad stock ownership only."""
from pathlib import Path
from unittest.mock import patch
import json
import current_smb1_toad_stock_91dc_1116 as C

if __name__=='__main__':
    raw=C.ROM.read_bytes();assert C.digest(raw)==C.PIN
    def deny(*args,**kw):raise AssertionError('Toad foundation attempted artifacts/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
        q=C.foundation(raw)
        for wrong in(raw[:-1],C.BT.inverse(raw),bytes([raw[0]^1])+raw[1:]):
            try:C.bindings(wrong)
            except AssertionError:pass
            else:raise AssertionError('Wrong current Toad image accepted')
    q['wrong_image_rejections']=3
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
