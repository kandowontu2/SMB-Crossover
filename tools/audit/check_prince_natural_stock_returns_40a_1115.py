"""Actual40a natural item route, strict native return/credit observers."""
from pathlib import Path
from unittest.mock import patch
import argparse,json
import check_prince_natural_stock_40a_1115 as Previous
import replay_prince_natural_stock_returns_40a_1115 as Factory

def run(raw,mode='oneup',jump=8):
    with patch.object(Previous,'Factory',Factory):return Previous.run(raw,mode,jump)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--mode',choices=('oneup','star'),default='oneup');p.add_argument('--jump',type=int,choices=(8,128),default=8);a=p.parse_args()
    def deny(*a,**k):raise AssertionError('Stock successor attempted output or native launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        q=run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes(),a.mode,a.jump)
    print(json.dumps(q,separators=(',',':')),flush=True)
    if not q['passed']:raise SystemExit(1)
