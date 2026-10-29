"""Retain bounded native diagnostics, rejected hypotheses and input-only fixes."""
from pathlib import Path
import hashlib,json,subprocess,sys
from checkpoint_roster_packets_v1 import ROOT,verify


def binding(path):
    p=Path(path).resolve();data=p.read_bytes()
    return dict(path=str(p),bytes=len(data),sha256=hashlib.sha256(data).hexdigest())


def main():
    report=ROOT/'docs/qa/rogue-native-pickup-and-route-diagnostics-2026-10-29.json'
    assert not report.exists(),'Keep prior observations immutable'
    hp=ROOT/'build/rogue-dawn-side-v1/handoff.json'
    h=json.loads(hp.read_text());seen={};verify(h,seen)
    assert binding(hp)['sha256']=='b260f10995fa68f13b6dd2d2f33cfaaab607ab8694139c2da3c7e3c92b238930'
    source_reports=[ROOT/p for p in [
        'docs/qa/rogue-dawn-jump-hold-source-2026-10-29.json',
        'docs/qa/rogue-dawn-item-birth-page-counterexample-2026-10-29.json',
        'docs/qa/rogue-dawn-native-item-absence-attribution-2026-10-29.json',
        'build/rogue-nmi-profile-v1/profile.json','build/rogue-nmi-profile-v2/profile.json']]
    for p in source_reports:verify(json.loads(p.read_text()),seen)
    names=[('rogue-dawn-side-native-easy-v1',5),
        ('rogue-dawn-source-ascent-hold-native-easy-v2',5),
        ('rogue-dawn-item-contact-diagnostic-native-v1',0),
        ('rogue-dawn-item-contact-diagnostic-native-v3',5),
        ('rogue-dawn-actor-birth-chronology-native-v1',0),
        ('rogue-dawn-grounded-opening-native-v1',6),
        ('supermaaa-opening-recovery-native-hard-v6',6),
        ('supermaaa-earned-memory-native-hard-v7',6)]
    native=[];local=[]
    for name,viewed in names:
        d=ROOT/'build/verification'/name
        ready,result,launch=[json.loads((d/n).read_text())for n in ['ready.json','result.json','launch.json']]
        for path,digest in ready['bindings'].items():
            if path not in seen:
                assert binding(path)['sha256']==digest,path;seen[path]=digest
            else:assert seen[path]==digest,path
        assert launch['settings_before']==launch['settings_after']and not launch['changed_inputs']
        assert result['adapter']['full_closed']and result['adapter']['per_frame_files']==0
        assert result['passed']is False,'These retained route endpoints are bounded negatives'
        row=dict(name=name,passed=False,reason=result['reason'],mode=result['actual_mode'],
            PPU_frames=result['frames'],completed_Main=result['completed_loops'],
            zero_deaths=result['zero_deaths'],min_SP=result['min_SP'],
            selected_whole_frames_visually_viewed=viewed,result=binding(d/'result.json'),
            lossless_stream_reference=binding(d/'captures.nesppuv1'))
        local += [d/n for n in ['ready.json','result.json','launch.json','run.lua','inputs.csv','trace.csv','events.jsonl']]
        if viewed:
            review=json.loads((d/'review.json').read_text())
            assert review['container']['full_frames']==result['full_frames']
            row['review']=binding(d/'review.json')
            local += [d/'review.json',d/'selected-whole-frames.png']
        native.append(row)
    d=ROOT/'build/verification/rogue-dawn-grounded-opening-native-v1'
    events=[json.loads(x)for x in(d/'events.jsonl').read_text().splitlines()]
    writes=[x for x in events if x['kind']=='native-actor-field-write'and x['data']['slot']==5]
    assert any(x['data']['symbol']=='InvPickup'and x['data']['value']==0xd8 for x in writes)
    assert any(x['data']['symbol']=='Enemy_Flag'and x['data']['before']==1 and x['data']['value']==0 for x in writes)
    packets=[x for x in events if x['kind']=='policy-read-only-diagnostic']
    earned=next(x for x in packets if x['data']['tanks']==1 and x['data']['power']==1)
    profile=json.loads(source_reports[-1].read_text())
    heavy=max(profile['cases'],key=lambda x:x['host_NMI_CPU'])
    result=dict(status='Real first physical Rogue Dawn upgrade earned; full1-1 and all-item qualification open',
        handoff=binding(hp),candidate=h['candidate'],native_runs=native,
        source_reports=[binding(p)for p in source_reports],
        actual_pickup=dict(birth_PPU=1229,contact_retirement_PPU=1425,typed_item=hex(0xd8),
            watched_actor_changes=writes,first_observed_earned_packet=earned,
            result='The same unmodified490a candidate creates a native slot5 actor at world336; it rises, survives, and retires through physical contact. Native power1 and RdTanks1 are observed. No direct grants/cheats/state writes.'),
        route_attribution='The prior input policy jumped from the lone opening block and approached the question row from above. Actor write chronology proves that run never created an item. V6 first lands at world286..288, walks beneath the question, bumps it and pursues the physical item.',
        source_hold='Six original/completeMain standing/running/aim cases prove84px sustained ascent, including original in-air action1. Fixed32-poll holds were shortened by native lag; preserving A through actual negative-VY ascent corrects the controller, with no jump/world edits.',
        rejected_origin_hypothesis='Native InitBlock initially sees stale SmHead, but actual SophiaHeadBlockOrigin corrects blockX/page before SetupPowerUp. Four legal Easy/Hard camera225/257 source scenes keep the correct world336 actor for85 completeMains. Camera0/player337 is outside loaded-page admission. No game fix was justified.',
        visual_scope='Root viewed only the recorded selected wholeframes, including real cold menu/lives, floor approach and earned first item. This is not a frame-by-frame review of every retained stream or an all-pixel/audio certification. Earlier blue-piece interpretations do not prove actor ownership; the new write chronology and tank count do.',
        Maaa_Hard='V6 earns Mushroom but reenters the initial route after damage. V7 remembers earned pickup and continues, then dies near world1510. These remain input-route negatives; no Hard clear or ROM physics change is claimed.',
        NMI_cost_profile=dict(heaviest_initialized_case=heavy,
            correction='V1 totals/APU comparisons remain valid; its absolute reader cutoff was wrong. V2 uses actual linked prefix bounds.',
            limits='Eight finite original/host NMI observations, ordered APU/state exact. Excludes DMA stalls, DMC steals and PPU timing. No native FPS or optimization claim.'),
        unlaunched_negative='Read-only telemetry policyv2 attempted a new io.open output and was rejected by preparation. No emulator launch or bypass. V3/v4 use the existing bounded event log instead.',
        shared_Downloads_unchanged=True,workspace_cap_bytes=70_000_000_000,
        still_open=['Rogue native1-1clear and earned remaining nine original items/abilities',
            'Source audio overhead/performance improvement and native listening',
            'Maaa Hard/remaining native abilities','DK/Gimmick/SMB2 actual integration and final shared composition'])
    report.write_text(json.dumps(result,indent=2)+'\n')
    public=[ROOT/p for p in [
        'tools/rogue_dawn_jump_hold_v1.py','tools/rogue_dawn_item_birth_page_v1.py','tools/rogue_dawn_item_birth_review_v1.py',
        'tools/audit/profile_rogue_nmi_costs_v1.py','tools/audit/profile_rogue_nmi_costs_v2.py',
        'tools/audit/rogue_dawn_contact_prepare_v1.py','tools/audit/rogue_dawn_actor_trace_prepare_v1.py',
        'tools/audit/roster_expansion_cold_capture_v4_diagnostic.lua','tools/audit/roster_expansion_cold_capture_v5_actor_writes.lua',
        'tools/playthroughs/supermaaa_11_v7.lua']]
    public += [ROOT/'tools/playthroughs'/f'rogue_dawn_11_v{i}.lua'for i in range(5,8)]
    public += [ROOT/'tools/playthroughs'/f'rogue_dawn_item_contact_trace_v{i}.lua'for i in range(1,5)]
    public += [Path(__file__).resolve(),report]
    checkpoint=dict(status=result['status'],candidate=h['candidate'],report=binding(report),
        bindings=seen,actual_ASM_dependencies={},
        owned_files=[binding(p)for p in public+local+source_reports])
    target=hp.parent/'native-diagnostics-checkpoint-v1.json';assert not target.exists()
    target.write_text(json.dumps(checkpoint,indent=2)+'\n')
    subprocess.run([sys.executable,'-B',str(ROOT/'tools/audit/checkpoint_roster_component_v5.py'),
        '--handoff',str(target),'--name','rogue-native-first-pickup-and-route-diagnostics'],cwd=ROOT,check=True)
    p=ROOT/'docs/qa/new-character-source-progress-2026-10-28.json';state=json.loads(p.read_text())
    state['Rogue_native_first_physical_upgrade']=dict(status=result['status'],report=binding(report),
        checkpoint='checkpoints/2026-10-28/rogue-native-first-pickup-and-route-diagnostics')
    p.write_text(json.dumps(state,indent=2)+'\n')
    print(json.dumps(dict(report=binding(report),runs=len(native),first_physical_upgrade_earned=True)))


if __name__=='__main__':main()
