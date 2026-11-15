"""Actual40a full/earned/public-lifecycle/reached-ISR successor source gate."""
from pathlib import Path
from unittest.mock import patch
import inspect,json
import check_prince_sword_tier2_earned_1115 as Previous
import check_prince_sword_tier2_fresh_cold_1115 as Cold
import replay_prince_sword_tier2_fresh_full_1115 as Replay

C=Cold.C

def run(parent):
    assert C.digest(Path(Previous.__file__).read_bytes())=='a46481ebcce75c0088b41452159b10e329f09437265034a5be5fe3f91aebc1cb'
    space=dict(Previous.__dict__,C=C,Replay=Replay,cold=Cold.cold)
    source=inspect.getsource(Previous.actual)
    def change(old,new):
        nonlocal source
        assert source.count(old)==1,old;source=source.replace(old,new,1)
    change("lo=row['live_CPU_half_open'][0]&8191;b.ram[2][lo:lo+len(row['old'])]=row['old']",
        "lo=row['live_CPU_half_open'][0]&8191;bank=3 if row['stream']==0 else 2;b.ram[bank][lo:lo+len(row['old'])]=row['old']")
    change("targets={0xc7b3,0xc7ba,0xc7d3,0xc7d7,0xc7f4,0xc0f6,0xc0fa}",
        "targets={0xc7b3,0xc7ba,0xc7d3,0xc7d7,0xc7f4,0xc0f6,0xc0fa,0xb3f1}")
    change("receipt['new_candidate_readback']['bytes']==4185","receipt['new_candidate_readback']['bytes']==4193")
    change('baseline_restores_only158_owned_bytes=True','baseline_restores_only166_owned_bytes=True')
    exec(compile(source,str(Path(__file__))+':same-earned-full-ISR-on40a','exec'),space)
    # Preserve the authentic cold-budget driver and all ordinary route inputs.
    source=inspect.getsource(Previous.run)
    exec(compile(source,str(Path(__file__))+':same-budget-on40a','exec'),space)
    return space['run'](parent)

if __name__=='__main__':
    def deny(*a,**k):raise AssertionError('Fresh earned source gate attempted output or launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        q=run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
    print(json.dumps(q,separators=(',',':')),flush=True)
