"""Zero-output Sunny live-input/current owning-code/menu foundation check."""
from pathlib import Path
from unittest.mock import patch
import json
import current_sunny_stock_bc5_1115 as Current

if __name__=='__main__':
    raw=Current.ROM.read_bytes()
    def deny(*a,**k):raise AssertionError('Sunny foundation attempted files/native launch')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=Current.inspect_inputs(raw)
    print(json.dumps(q,separators=(',',':')),flush=True)
