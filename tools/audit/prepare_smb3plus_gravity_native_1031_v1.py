"""Prepare exact05b1 native reruns with unchanged assertions and no RAM writes."""
from pathlib import Path
import json
import re
import sys

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_functional_roster_visuals58_v1 as B
import prepare_smb2_firstlooks_bg_eye_v6 as V
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location

J=R/'build/smb3plus-peach-gravity-consumer-1031-v1/joint'
O=R/'build/smb3plus-gravity-native-1031-v1'


def main():
    assert not O.exists();b=scoped_load(J/'candidate.nes');out=[]
    stage=J.parent/'source-stage.json';reg=J.parent/'regressions-v1.json';menu=J.parent/'menu-controls-v1.json'
    for p in [stage,reg,menu]:
        d=json.loads(B.read(p));B.bound(d)
        assert d.get('passed',True) and d['candidate']==B.sha(J/'candidate.nes')
    for name,source in [('toad',R/'build/smb3plus-menu-native-1031-v1/toad'),
        ('peach',R/'build/smb3plus-peach-native-braked-1031-v2/peach')]:
        ready=json.loads(B.read(source/'ready.json'));B.bound(ready)
        text=B.read(source/'controller.lua');assert text.count(ready['ROM_sha256'])==1
        text=text.replace(ready['ROM_sha256'],B.sha(J/'candidate.nes'))
        for n,at in re.findall(r'^L\["(\w+)"\]=(\d+)',text,re.M):assert address(b,n)==int(at),n
        for n,bank in re.findall(r'^B\["(\w+)"\]=(\d+)',text,re.M):assert (location(b,n)-16)//8192==int(bank),n
        folder=O/name;folder.mkdir(parents=True)
        script=folder/'controller.lua';runner=folder/'run.py';B.write(script,text);B.write(runner,V.RUN)
        bindings=dict(ready['bindings']);bindings.update({str(p):B.sha(p) for p in [Path(__file__),
            stage,reg,menu,source/'ready.json',source/'capture/result.json',source/'capture/binding.json',
            script,runner,J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl']})
        packet=dict(prepared=True,native=False,ROM=str(J/'candidate.nes'),ROM_sha256=B.sha(J/'candidate.nes'),
            host_timeout_seconds=60,run_cap_bytes=536870912,max_files=64,max_PNGs=4,bindings=bindings,
            controller='Original real Select/lives/walk/jump/land and720 physical ISR checks. Peach uses verified brakes; no RAM/enemy/powerup writes.')
        B.write(folder/'ready.json',json.dumps(packet,indent=2)+'\n');out.append(str(folder/'ready.json'))
    B.write(O/'prepared.json',json.dumps(dict(prepared=out,native=False,source_candidate=B.sha(J/'candidate.nes')),indent=2)+'\n')
    print(json.dumps(dict(prepared=out,native=False)))


if __name__=='__main__':main()
