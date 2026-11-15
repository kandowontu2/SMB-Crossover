"""Read-only natural-prefix Prince hidden-block head-coordinate diagnostic."""
from pathlib import Path
from unittest.mock import patch
import json
import check_prince_natural_stock_40a_1115 as Previous
import replay_prince_hidden_reach_query_40a_1115 as Factory

if __name__=='__main__':
    def deny(*a,**k):raise AssertionError('Head diagnostic attempted output or native launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny),patch.object(Previous,'Factory',Factory):
        q=Previous.run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes(),'oneup',8)
    assert not q['passed']and q['natural_stock']['query_complete']and len(q['natural_stock']['head_queries'])==1
    q['diagnostic_complete']=True
    print(json.dumps(q,separators=(',',':')),flush=True)
