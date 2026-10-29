"""Freeze the Rogue floor/side fixes and the native negatives that exposed them."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
from checkpoint_roster_packets_v1 import ROOT, verify


def bind(path):
    path=Path(path).resolve();data=path.read_bytes()
    return dict(path=str(path),bytes=len(data),sha256=hashlib.sha256(data).hexdigest())


def main():
    hp=ROOT/'build/rogue-dawn-side-v1/handoff.json';h=json.loads(hp.read_text());seen={};verify(h,seen)
    assert bind(hp)['sha256']=='b260f10995fa68f13b6dd2d2f33cfaaab607ab8694139c2da3c7e3c92b238930'
    public={}
    for folder in ['rogue-dawn-floor-v4','rogue-dawn-side-v1']:
        p=ROOT/'build'/folder/'owned-files.json';j=json.loads(p.read_text());verify(j,seen)
        for row in j['public_files']:public[row['path']]=row
    native=[];extra=[]
    for name,count in [('rogue-dawn-floor-native-easy-v1',4),('rogue-dawn-question-target-native-easy-v1',5)]:
        folder=ROOT/'build/verification'/name
        ready,result,review,launch=[json.loads((folder/n).read_text())for n in ['ready.json','result.json','review.json','launch.json']]
        for path,digest in ready['bindings'].items():assert bind(path)['sha256']==digest,path
        assert not result['passed'] and result['zero_deaths'] and result['min_SP']==169
        assert result['full_frames']==review['container']['full_frames']
        assert not launch['changed_inputs']and launch['settings_before']==launch['settings_after']
        native.append(dict(name=name,route_passed=False,reason=result['reason'],PPU_frames=result['frames'],
            completed_Main=result['completed_loops'],zero_deaths=True,min_SP=169,
            selected_whole_frames_visually_viewed=count,strict_guards_passed=True,
            ready=bind(folder/'ready.json'),result=bind(folder/'result.json'),review=bind(folder/'review.json'),
            lossless_stream_reference=bind(folder/'captures.nesppuv1')))
        extra += [folder/n for n in ['ready.json','result.json','review.json','launch.json','run.lua',
            'inputs.csv','trace.csv','events.jsonl','selected-whole-frames.png']]
    report=ROOT/'docs/qa/rogue-dawn-floor-side-native-progress-2026-10-29.json'
    assert not report.exists()
    result=dict(status='Two source collision bugs corrected; native retest of latest side fix still pending',
        handoff=bind(hp),source_report=h['report'],runs=native,
        actual_floor_bug='Original E4A3 samples current bottom before moving downward. Leading-edge host probe stopped one pixel above the floor and repeatedly reset run/jump state. Restored source E4EC distance decrement on every committed downward pixel.',
        actual_side_bug='After corrected floor rest at center193/radius15, inclusive bottom side sample208 entered the floor. Original E89F/E8CE scans the half-open vertical extent and excludes208. Native post-question X337/Y177 stall reproduces in full Main; successor subtracts one pixel from the bottom side sample.',
        coverage_gap='Earlier walking stages asserted posture without asserting actual horizontal progress. New full Main cases require >=48px displacement, real question birth, release, fresh jump and relanding.',
        controller_target='Original first-solid-left head ordering selects brick320 from X330. Input-only target336/338 selects question336 and produces a real typed D8 actor. No wider head box or weaker collision rule.',
        typed_arena_negative='Hard Main26 BRK came from an uninitialized EnemyData pointer in the source arena. Correct genuine GetAreaDataAddrs initializes current ground stream AA3F and six 98-Main cases pass without candidate changes; original negative/trace retained.',
        visual_review='Root viewed all selected wholeframes from both listed native negatives. Overworld blue restored and the correctly targeted question becomes used; typed item remains visible. E075/M000 debug overlays still need final cleanup.',
        scope='No latest-side native clear, all-item, audio-audibility or FPS claim. Downloads remains ac126 WIP; ordinary d444/f4ffd exact in source checks.',
        workspace_cap_bytes=70_000_000_000)
    report.write_text(json.dumps(result,indent=2)+'\n')
    extra += [report,Path(__file__).resolve(),ROOT/'tools/playthroughs/rogue_dawn_11_v4.lua',
        ROOT/'tools/playthroughs/rogue_dawn_opening_route_v1.lua',
        ROOT/'tools/rogue_dawn_opening_head_target_v1.py',ROOT/'tools/rogue_dawn_opening_head_target_v2.py']
    for name in ['rogue-dawn-opening-head-target-source-2026-10-29.json',
                 'rogue-dawn-opening-head-context-negative-2026-10-29.json',
                 'rogue-dawn-opening-head-target-source-v2-2026-10-29.json']:
        extra.append(ROOT/'docs/qa'/name)
    for path in extra:public[str(path.resolve())]=bind(path)
    normalized=dict(h,status=result['status'],source_report=h['report'],report=bind(report),
        original_handoff=bind(hp),owned_files=list(public.values()))
    if not isinstance(normalized.get('actual_ASM_dependencies',{}),dict):normalized['actual_ASM_dependencies']={}
    target=hp.parent/'root-checkpoint.json';assert not target.exists()
    target.write_text(json.dumps(normalized,indent=2)+'\n')
    subprocess.run([sys.executable,'-B',str(ROOT/'tools/audit/checkpoint_roster_component_v5.py'),
        '--handoff',str(target),'--name','rogue-original-floor-and-half-open-side-fixes'],cwd=ROOT,check=True)
    progress=ROOT/'docs/qa/new-character-source-progress-2026-10-28.json';state=json.loads(progress.read_text())
    state['Rogue_floor_side_collision_fixes']=dict(status=result['status'],handoff=bind(hp),report=bind(report),
        checkpoint='checkpoints/2026-10-28/rogue-original-floor-and-half-open-side-fixes')
    progress.write_text(json.dumps(state,indent=2)+'\n')
    print(json.dumps(dict(report=bind(report),public_files=len(public),source_bindings=len(seen))))


if __name__=='__main__':main()
