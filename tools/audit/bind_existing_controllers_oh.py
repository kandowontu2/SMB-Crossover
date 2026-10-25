"""Freeze existing character-specific controller policies for external runs."""
from pathlib import Path
import argparse
import hashlib
import json

ROOT=Path(__file__).resolve().parents[2]


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False)
    names=['mario_luigi_scrooge_nav.lua','mario_luigi_scrooge_policy.lua',
        'scrooge_native_policy.lua','link_simon_ryu_policy.lua','full_roster_policy_og.lua']
    text={n:(ROOT/'tools/playthroughs'/n).read_text() for n in names}
    hashes={n:hashlib.sha256((ROOT/'tools/playthroughs'/n).read_bytes()).hexdigest() for n in names}
    policy=text['mario_luigi_scrooge_policy.lua']
    root="local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))\n"
    include="local travel=assert(dofile(root..'/tools/playthroughs/mario_luigi_scrooge_nav.lua'))"
    assert policy.count(root)==policy.count(include)==1
    policy=policy.replace(root,'').replace(include,"local travel=(function()\n"+text['mario_luigi_scrooge_nav.lua']+'\nend)()')
    scrooge=text['scrooge_native_policy.lua']
    include="local normal=assert(dofile(root..'/tools/playthroughs/mario_luigi_scrooge_policy.lua'))"
    assert scrooge.count(root)==scrooge.count(include)==1
    scrooge=scrooge.replace(root,'').replace(include,'local normal=(function()\n'+policy+'\nend)()')
    final='-- Existing controller-only policies, frozen without workspace-path assumptions.\n'
    for name,source in [('scrooge',scrooge),('simon',text['link_simon_ryu_policy.lua']),('other',text['full_roster_policy_og.lua'])]:
        final+='local '+name+'=(function()\n'+source+'\nend)()\n'
    final+='return function(c)\n if c.char==12 and c.r("DarkwingVariant")==0 then return scrooge(c)end\n if c.char==5 and c.r("Cv3Variant")==0 then return simon(c)end\n return other(c)\nend\n'
    path=a.output/'policy.lua';path.write_text(final)
    q=dict(prepared=True,memory_writes=False,game_changes=False,original_policy_hashes=hashes,
        policy_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        adaptations='Only root/dofile binding is replaced by exact embedded existing policies; Scrooge/Simon use their existing character-specific navigation and combat inputs.')
    (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
