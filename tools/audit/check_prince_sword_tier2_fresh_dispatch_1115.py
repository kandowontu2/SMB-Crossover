"""Exact40a actual native callback regressions; frozen5cfa negative retained."""
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import inspect,json
import check_prince_sword_tier2_dispatch_1115 as Previous
import check_prince_sword_tier2_fresh_cold_1115 as Cold

C=Cold.C

def invoke(m,target,slot=5):
    # The actual resident private-callback bridge establishes RAM2 before
    # entering C7xx. A completed Main may have returned with another C bank.
    Cold.N.put(m,CurrentBankC=2);m.raw_page(2,2)
    return Previous.invoke(m,target,slot)

def run(parent):
    source=inspect.getsource(Previous.run)
    old="assert bytes(trials[0][0][:0x800])==bytes(trials[1][0][:0x800]),'Native callback effects differ'"
    new="diff=[(at,a,b)for at,(a,b)in enumerate(zip(bytes(trials[0][0][:0x800]),bytes(trials[1][0][:0x800])))if a!=b];assert not diff,(kind,tier,diff[:40])"
    assert source.count(old)==1;source=source.replace(old,new,1)
    space=dict(Previous.__dict__,C=C,Earned=SimpleNamespace(cold=Cold.cold,Game=Cold.Game),invoke=invoke)
    exec(compile(source,str(Path(__file__))+':exact40a-callback-components','exec'),space)
    return space['run'](parent)

if __name__=='__main__':
    def deny(*a,**k):raise AssertionError('Fresh callback source proof attempted output or launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        q=run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
    print(json.dumps(q,separators=(',',':')),flush=True)
