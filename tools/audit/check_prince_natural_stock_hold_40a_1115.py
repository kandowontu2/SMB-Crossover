"""Actual40a held-Up80 natural-item source route, no generated files."""
from pathlib import Path
from unittest.mock import patch
import argparse,json
import check_prince_natural_stock_40a_1115 as Previous
import replay_prince_natural_stock_hold_40a_1115 as Factory

def run(raw,mode='oneup'):
    with patch.object(Previous,'Factory',Factory):return Previous.run(raw,mode,8)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--mode',choices=('oneup','star'),default='oneup');a=p.parse_args()
    def deny(*a,**k):raise AssertionError('Held-Up route attempted output or native launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        q=run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes(),a.mode)
    print(json.dumps(q,separators=(',',':')),flush=True)
    if not q['passed']:raise SystemExit(1)
