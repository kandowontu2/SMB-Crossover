"""Bounded genuine Star and read-only actual score-writer trace."""
from pathlib import Path
from unittest.mock import patch
import json
import check_prince_natural_stock_40a_1115 as Previous
import replay_prince_star_score_writers_40a_1115 as Factory

if __name__=='__main__':
    def deny(*a,**k):raise AssertionError('Star writer source route attempted output/native launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny),patch.object(Previous,'Factory',Factory):
        q=Previous.run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes(),'star',8)
    print(json.dumps(q,separators=(',',':')),flush=True)
    if not q['passed']:raise SystemExit(1)
