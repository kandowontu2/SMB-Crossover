"""Zero-output actual Bowser packet/menu preservation qualification."""
from pathlib import Path
from unittest.mock import patch
import json
import current_bowser_stock_bc5_1115 as Current
if __name__=='__main__':
    raw=Current.ROM.read_bytes()
    def deny(*a,**kw):raise AssertionError('Bowser source attempted output/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=Current.inspect_inputs(raw)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
