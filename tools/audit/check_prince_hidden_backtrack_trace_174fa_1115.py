"""Actual174fa cap-flight first-writer diagnosis; no files or native launch."""
from pathlib import Path
CAPTURED_RAW=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
from unittest.mock import patch
import json
import current_prince_stock_174fa_1115 as Current
import replay_prince_hidden_backtrack_trace_174fa_1115 as Factory

if __name__=='__main__':
    def deny(*a,**k):raise AssertionError('174fa wall diagnostic attempted output/native launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        q=Current.source_run(CAPTURED_RAW,Factory)
    print(json.dumps(q,separators=(',',':')),flush=True)
    if not q['passed']:raise SystemExit(1)
