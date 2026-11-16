"""Versioned e32f guard/lifecycle checks via explicitly typed currenta2 read."""
from pathlib import Path
from unittest.mock import patch
import json
import current_mini_owner_research_a2_1116 as Reader
import check_mini_weapon_owner_lifecycle_1116 as Previous

if __name__=='__main__':
    raw=Previous.C.ROM.read_bytes();parent=Reader.reference(raw)
    def deny(*a,**kw):raise AssertionError('Typed Mini lifecycle attempted artifacts/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=Previous.run(parent)
    q['typed_current_read']=Reader.metadata(raw);print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
