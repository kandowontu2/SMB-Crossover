"""Freeze existing source-specific controls for the remaining OG route matrix."""
from pathlib import Path
import argparse
import hashlib
import json

ROOT=Path(__file__).resolve().parents[2]


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    names=['full_roster_policy_og.lua','mike_policy_nx.lua','vic_audio_policy_nv.lua','meta_grounded_policy_nu.lua']
    files={n:ROOT/'tools/playthroughs'/n for n in names}
    text={n:p.read_text() for n,p in files.items()}
    assert all('dofile('not in s and 'emu.write('not in s and 'setState('not in s for s in text.values())
    final='-- Frozen existing controllers only. No game state grants or writes.\n'
    for var,name in [('base',names[0]),('mike',names[1]),('vic',names[2]),('meta',names[3])]:
        final+='local '+var+'=(function()\n'+text[name]+'\nend)()\n'
    final+='''return function(c)
 if ROSTER_CONFIG.name=='mike' then return mike(c)end
 if ROSTER_CONFIG.name=='vic' then return vic(c)end
 if ROSTER_CONFIG.name=='meta' then return meta(c)end
 return base(c)
end
'''
    policy=out/'policy.lua';policy.write_text(final)
    q=dict(prepared=True,game_changes=False,memory_writes=False,
        source_hashes={n:hashlib.sha256(p.read_bytes()).hexdigest() for n,p in files.items()},
        policy_sha256=hashlib.sha256(policy.read_bytes()).hexdigest(),
        scope='Existing self-contained Mike/Vic/grounded-Meta controls, otherwise the existing OG controller. Frozen embedded sources; no workspace-path dependency or emulated writes. Every candidate still requires native discovery plus exact independent replay and graphics/scroll review.')
    (out/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
