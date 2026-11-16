"""Correct native10-byte extent under a separate strict owningbc5 audit."""
from pathlib import Path
from unittest.mock import patch
import inspect,json
import current_prince_oneup_bc5_1115 as Current
import audit_prince_unarmed_contact67_1115 as Previous

def run(raw):
    assert Current.C.digest(Path(Previous.__file__).read_bytes())=='47885ff6e8f5d701f62f02097a1a2e3802d031baef94a79d750695a65743cd0a'
    source=inspect.getsource(Previous.run);old="native('CollisionFound',9)";assert source.count(old)==1
    source=source.replace(old,"native('CollisionFound',10)",1)
    space=dict(Previous.__dict__,Current=Current)
    exec(compile(source,str(Path(__file__))+':correct-native-return-extent','exec'),space)
    q=space['run'](raw);q['all106_HotNew_changes_preserved']=True
    q['old67_audit95006_negative']='Observer requested9bytes from a10byte native return block; no CPU gameplay ran'
    q['receipt_SHA256']=Current.C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q

if __name__=='__main__':
    def deny(*a,**k):raise AssertionError('Current unarmed audit attempted output/native launch')
    raw=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):q=run(raw)
    print(json.dumps(q,separators=(',',':')),flush=True)
