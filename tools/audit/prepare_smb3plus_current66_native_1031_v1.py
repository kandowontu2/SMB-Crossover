"""Prepare only: exact frozen current66+SMB3 child, unchanged native policies."""
from pathlib import Path
import json,re,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_functional_roster_visuals58_v1 as B
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
J=R/'build/smb3plus-current66-source-1031-v2/joint'
O=R/'build/smb3plus-current66-native-1031-v1'
H=R/'docs/qa/checkpoints/2026-10-31/smb3plus-current66-source-v1/handoff.json'
P=R/'build/smb3plus-gravity-native-1031-v1'


def main():
    assert not O.exists()
    assert B.sha(H)=='8c5c861f81ac849f8f4f28aa76f9f5db0be70a2d866b26994e2fbb2c3ca198b0'
    h=json.loads(B.read(H));B.bound(h)
    assert B.sha(J/'candidate.nes')==h['candidate']=='01a40d4019ae00220c7279c9ab8d4f6f25afb44af1612a6a1483a257448f0fa9'
    b=scoped_load(J/'candidate.nes');packets=[]
    receipts=[J.parent/n for n in['source-stage.json','regressions-v1.json','menu-controls-v1.json','vectors-v1.json']]
    receipts +=[R/'build/smb3plus-current66-whole-controller-1031-v1/probe.json',R/'build/smb3plus-current66-foreign-main-1031-v1/controls.json']
    for n in['toad','peach']:
        parent=P/n;old=json.loads(B.read(parent/'ready.json'));B.bound(old)
        original=B.read(parent/'controller.lua');assert original.count(old['ROM_sha256'])==1
        text=original.replace(old['ROM_sha256'],h['candidate'])
        assert text.replace(h['candidate'],old['ROM_sha256'])==original
        for name,at in re.findall(r'^L\["(\w+)"\]=(\d+)',text,re.M):assert address(b,name)==int(at),name
        for name,bank in re.findall(r'^B\["(\w+)"\]=(\d+)',text,re.M):assert(location(b,name)-16)//8192==int(bank),name
        folder=O/n;folder.mkdir(parents=True)
        B.write(folder/'controller.lua',text);B.write(folder/'run.py',B.read(parent/'run.py'))
        paths=[Path(__file__),H,parent/'ready.json',parent/'controller.lua',parent/'run.py',
            folder/'controller.lua',folder/'run.py',J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',*receipts]
        q=dict(prepared=True,native=False,launched=False,ROM=str(J/'candidate.nes'),ROM_sha256=h['candidate'],
            host_timeout_seconds=60,run_cap_bytes=536870912,max_files=64,max_PNGs=4,
            controller='Identical frozen gravity-native policy/observer except ROM hash; real Select/lives/walk/jump/land and720 physical ISR checks. Peach uses verified brakes; no RAM/enemy/powerup writes.',
            original_policy_ready=str(parent/'ready.json'),original_policy_sha256=B.sha(parent/'controller.lua'),
            only_controller_change='Exact ROM SHA literal rebound; all consumed L/B labels verified at final linked addresses/banks.',
            source_control_handoff=str(H),source_control_handoff_sha256=B.sha(H),
            bindings={str(p.resolve()):B.sha(p)for p in paths})
        B.write(folder/'ready.json',json.dumps(q,indent=2)+'\n');B.bound(q)
        packets.append(dict(name=n,ready=str(folder/'ready.json'),ready_sha256=B.sha(folder/'ready.json')))
    out=dict(prepared=True,native=False,launched=False,ROM_sha256=h['candidate'],packets=packets,
        limitations=['Source ground pound/custom stomp delay/special art/kick SFX unfinished','No native success claimed for the composed child; root owns launch/review/installation'],
        bindings={str(p.resolve()):B.sha(p)for p in[Path(__file__),H,*[Path(v['ready'])for v in packets]]})
    B.write(O/'prepared.json',json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(prepared=True,native=False,launched=False,packets=packets,prepared_sha256=B.sha(O/'prepared.json'))))


if __name__=='__main__':main()
