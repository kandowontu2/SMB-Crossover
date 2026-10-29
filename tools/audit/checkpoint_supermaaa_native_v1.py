"""Save SuperMaaa's immutable source host and qualified Easy native traversal."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
from checkpoint_roster_packets_v1 import ROOT,verify


def bind(path):
    path=Path(path).resolve();data=path.read_bytes()
    return dict(path=str(path),bytes=len(data),sha256=hashlib.sha256(data).hexdigest())


def main():
    hp=ROOT/'build/supermaaa-host-v1/handoff.json';h=json.loads(hp.read_text());seen={};verify(h,seen)
    assert bind(hp)['sha256']=='7bd89598fcb7783245a9f75b59afc3f69e57ea539fbe81d0f9226d697429c55a'
    for path,digest in h['bindings'].items():assert bind(path)['sha256']==digest,path
    public=[ROOT/p for p in ['tools/prepare_supermaaa_host_v1.py','tools/reference/supermaaa_host_core_v1.s',
        'tools/audit/supermaaa_host_controls_v1.py','tools/audit/supermaaa_host_freeze_v1.py',
        'tools/audit/supermaaa_host_label_scope_addendum_v1.py','docs/qa/supermaaa-private-host-2026-10-29.txt',
        'tools/audit/supermaaa_native_prepare_v1.py','tools/audit/supermaaa_native_prepare_v2.py']]
    public += [ROOT/'tools/playthroughs'/('supermaaa_11_v'+str(i)+'.lua')for i in range(1,7)]
    public += [Path(__file__).resolve()]
    names=[('supermaaa-native-easy-v1',5),('supermaaa-stomp-native-easy-v2',5),
        ('supermaaa-walk-native-easy-v3',5),('supermaaa-earned-mush-native-easy-v4',6),
        ('supermaaa-pit-landing-native-easy-v5',7),('supermaaa-pit-landing-native-hard-v5',5)]
    runs=[];local=[]
    for name,count in names:
        folder=ROOT/'build/verification'/name
        ready,result,review,launch=[json.loads((folder/n).read_text())for n in ['ready.json','result.json','review.json','launch.json']]
        for path,digest in ready['bindings'].items():assert bind(path)['sha256']==digest,path
        assert ready['ROM_sha256']==h['candidate_ROM']
        assert not launch['changed_inputs']and launch['settings_before']==launch['settings_after']
        assert result['min_SP']==199 and result['full_frames']==review['container']['full_frames']
        runs.append(dict(name=name,passed=result['passed'],reason=result['reason'],mode=result['actual_mode'],
            PPU_frames=result['frames'],completed_Main=result['completed_loops'],zero_deaths=result['zero_deaths'],
            min_SP=result['min_SP'],strict_guards_passed=True,selected_whole_frames_visually_viewed=count,
            result=bind(folder/'result.json'),review=bind(folder/'review.json'),
            stream_reference=bind(folder/'captures.nesppuv1')))
        local += [folder/n for n in ['ready.json','result.json','review.json','launch.json','run.lua',
            'inputs.csv','trace.csv','events.jsonl','selected-whole-frames.png']]
    assert sum(r['passed']for r in runs)==1
    success=runs[4];assert success['PPU_frames']==3485 and success['zero_deaths']and success['mode']==0
    report=ROOT/'docs/qa/supermaaa-native-easy-progress-2026-10-29.json';assert not report.exists()
    result=dict(status='Source host frozen; native Easy1-1 clear with earned mushroom; Hard/full-upgrade tests open',
        handoff=bind(hp),label_scope_addendum=bind(hp.parent/'label-scope-addendum.json'),runs=runs,
        genuine_Easy_endpoint='Actual Select32 selects raw0/MarioVariant2, Start16/lives, physical mushroom pickup atPPU813, natural flagpole at2267, and25controlled updates in1-2. No cheats or emulated writes.',
        actual_global_label_moves=413,raw_name_census_is_not_public_moves=552,
        visual_review='Root viewed every selected wholeframe in all six listed runs. Cold roster/lives, raised source head/body, growing neck, normal overworld, flagpole and underground endpoint are visible. This is selected-frame review, not an all-pixel/native-audio certification.',
        retained_negatives='Early controllers died among enemies or missed the first pit. Walking variant died under the elevated enemy row. Later first-mushroom approach succeeds. Pit-landing controller brakes while falling toward the pit, lands, then makes a fresh jump; no ROM physics changed between pilots.',
        Hard_negative='First Goomba timing lands the controller atop the unopened first question row atX338/Y112, leaving its approach phase waiting for floorY>=160. Input-only recovery v6 is prepared separately; this is not a Hard clear or candidate promotion.',
        source_scope='Original timer growth cap160, stomp halving, raised head/box/fireball origin, real native coins/pickups/life paths, lag-safe CHR/OAM publication and exact foreign paths qualified by finite source controls. Native minimumSP199; normal8-sprite hardware.',
        still_open=['Hard1-1clear','Earned Fire Flower/fireballs, Star,1Up and long-neck dense interactions',
            'All selected-character transitions/physics/performance review and final shared composition'],
        shared_Downloads_unchanged=True,workspace_cap_bytes=70_000_000_000)
    report.write_text(json.dumps(result,indent=2)+'\n');public.append(report)
    root=dict(h,status=result['status'],source_report=bind(h['report']),report=bind(report),
        original_handoff=bind(hp),owned_files=[bind(p)for p in public+local],actual_ASM_dependencies={})
    target=hp.parent/'root-checkpoint.json';assert not target.exists()
    target.write_text(json.dumps(root,indent=2)+'\n')
    subprocess.run([sys.executable,'-B',str(ROOT/'tools/audit/checkpoint_roster_component_v5.py'),
        '--handoff',str(target),'--name','supermaaa-source-host-and-native-easy-clear'],cwd=ROOT,check=True)
    progress=ROOT/'docs/qa/new-character-source-progress-2026-10-28.json';state=json.loads(progress.read_text())
    state['SuperMaaa_private_native_Easy']=dict(status=result['status'],handoff=bind(hp),report=bind(report),
        checkpoint='checkpoints/2026-10-28/supermaaa-source-host-and-native-easy-clear')
    progress.write_text(json.dumps(state,indent=2)+'\n')
    print(json.dumps(dict(report=bind(report),source_bindings=len(h['bindings']),native_runs=len(runs),Easy_clear=True)))


if __name__=='__main__':main()
