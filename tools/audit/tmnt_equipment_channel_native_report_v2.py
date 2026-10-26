"""Freeze strict70ba failure and classify the three actual source/DMA epochs."""
from pathlib import Path
from collections import Counter,defaultdict
import argparse
import csv
import gzip
import hashlib
import json
import math
import shutil
import statistics
from tmnt_native_storage_driver import ROOT,CURRENT,OB,sha
from tmnt_native_storage_cpu import Probe

D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
DIGEST='70ba4f682723e62b00ef4278c19e3b898383d2903ce6ad6b35199816748217de'


def read(p):
    with p.open()as f:return list(csv.DictReader(f))


def stats(v):
    v=sorted(v);assert v
    return dict(count=len(v),mean=statistics.mean(v),p95_nearest_rank=v[math.ceil(.95*len(v))-1],maximum=max(v))


def digest(v):return hashlib.sha256(bytes(v)).hexdigest()


def visible(v):return Counter(tuple(v[i:i+4])for i in range(0,256,4)if v[i]<240)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    out=a.output;pair=D/'tmnt-equipment-channel-native-ready-v1';source=D/'tmnt-equipment-channel-ready-v1/receipt.json'
    assert not out.exists()and not out.resolve().is_relative_to(ROOT)
    strict=json.loads((pair/'easy-strict-proof.json').read_text());assert strict['measurement_valid']and not strict['performance_gate_passed']
    assert strict['baseline_ROM_sha256']==CURRENT and strict['candidate_ROM_sha256']==DIGEST and strict['behavior']==0
    assert [r['update']for r in strict['all_completed_update_prefix_deficits']]==[532,560,588]
    assert strict['all_completed_update_prefix_deficits']==strict['all_phase_prefix_deficits']
    folders={k:pair/(k+'-easy')for k in ['baseline','candidate']}
    reports={k:json.loads((v/'native-result.json').read_text())for k,v in folders.items()}
    assert all(v['passed']and v['mode-readback.json']==dict(requested=0,actual=0,selected=19)for v in reports.values())
    assert reports['baseline']['dependencies']==reports['candidate']['dependencies']
    setup={};data={};phase_costs={};exclusive={};native_inputs={}
    for key,folder in folders.items():
        setups=[json.loads(x)for x in(folder/'before-phase-setup.jsonl').read_text().splitlines()];assert len(setups)==10;setup[key]=[]
        for q in setups:
            if q['kind']!='staged':continue
            writes=q['writes']
            if isinstance(writes,dict):writes=[writes[k]for k in sorted(writes,key=int)]
            assert all(0<=r['address']<0x8000 and not 0x2000<=r['address']<0x5c00 and not 0x7400<=r['address']<0x7500 for r in writes)
            setup[key].append(dict(phase=q['data']['phase'],step=q['data']['step'],writes=[{n:r[n]for n in ['address','value','name']}for r in writes]))
        rows=[json.loads(x)for x in(folder/'native-bus.jsonl').read_text().splitlines()];draw=None;dma=[]
        for row in rows:
            if row['kind']=='draw-construction':draw=row
            elif row['kind']=='DMA-complete':
                q=row['data'];assert q['exact']and q['safe']and q['writes']==256 and q['source']==q['hardware']
                assert 241<=q['start']['scanline']<=260 and 241<=q['finish']['scanline']<=260
                assert q['start']['frame']==q['finish']['frame']
                dma.append(dict(ordinal=len(dma)+1,source_draw=draw,data=q))
        assert len(dma)==(572 if key=='baseline'else 575)
        assert dma[0]['source_draw']is None,'Initial committed image predates active600-update ledger'
        completed={r['index']:r for r in rows if r['kind']=='completed-game-update'};assert len(completed)==600
        draws={r['index']:r for r in rows if r['kind']=='draw-construction'}
        game=read(folder/'gameplay.csv');spans=read(folder/'tmnt-performance-calls.csv');audio=read(folder/'audio-components.csv')
        main=[r for r in spans if r['name']=='GameLoop'];assert len(game)==len(main)==600
        cores=[r for r in audio if r['name']in ['TnNativeInit','TnNativePlay']]
        state=read(folder/'source-state.csv');assert len(cores)==len(state)==(602 if key=='candidate'else 0)
        for tick,(core,s)in enumerate(zip(cores,state)):
            assert int(s['sourceTick'])==tick
            core['original_source_tick']=tick;core['native_state_serial']=int(s['serial'])
        data[key]=dict(rows=rows,dma=dma,completed=completed,draws=draws,game=game,spans=spans,main=main,audio=audio,cores=cores,state=state)
        phase_costs[key]={};exclusive[key]={}
        for phase in ['idle','walk','enemies','primary','secondary']:
            top=[r for r in audio if r['name']=='AudioUpdate'and r['phase']==phase]
            foreground=[r for r in main if r['phase']==phase]
            phase_costs[key][phase]=dict(AudioUpdate_inclusive=stats([int(r['inclusiveCycles'])for r in top]),
                AudioUpdate_excluding_IRQ=stats([int(r['CPUcycles'])for r in top]),
                foreground_GameLoop_excluding_ISR=stats([int(r['cpuCycles'])for r in foreground]))
            names=sorted({r['name']for r in audio if r['phase']==phase})
            exclusive[key][phase]={n:stats([int(r['exclusiveCPUcycles'])for r in audio if r['phase']==phase and r['name']==n])for n in names}
        for top in[r for r in audio if r['name']=='AudioUpdate']:
            children=[r for r in audio if int(r['startCPU'])>=int(top['startCPU'])and int(r['endCPU'])<=int(top['endCPU'])]
            assert sum(int(r['exclusiveCPUcycles'])for r in children)==int(top['CPUcycles'])
        native_inputs[key]=dict(mode_readback=reports[key]['mode-readback.json'],hardware=reports[key]['native-source-hardware.json'],
                                ownership=reports[key]['ownership-guards.json'],CHR=reports[key]['chr-commit.json'])
    assert setup['baseline']==setup['candidate']
    gold=json.loads(gzip.decompress((OB/'probe-v2/song-02.json.gz').read_bytes()))
    original=Probe(D/'tmnt-native-storage-current50b5-v1/standalone-original-v1',True)
    apu=read(folders['candidate']/'source-apu.csv');assert len(apu)==2125;grouped=defaultdict(list)
    for row in apu:grouped[int(row['serial'])].append([int(row['register']),int(row['value'])])
    positions=list(range(0xe0,0xee))+list(range(0x7000,0x70ae))
    for tick,row in enumerate(data['candidate']['state']):
        assert int(row['serial'])==tick+1 and int(row['sourceTick'])==tick and int(row['song'])==2
        original.call(gold[tick],2)
        expected=bytes((original.m[at]-(27 if original.origin.get(at)in original.changed_high else 0))&255 for at in positions)
        assert bytes.fromhex(row['ZP14_RAM174_hex'])==expected and grouped[tick+1]==gold[tick]['writes']
    case_maps=[]
    for deficit in strict['all_completed_update_prefix_deficits']:
        index=deficit['update'];maps={}
        for key,q in data.items():
            completed=q['completed'][index];draw=q['draws'][index]
            transfers=[v for v in q['dma']if v['source_draw']and v['source_draw']['index']==index];assert len(transfers)==1
            transfer=transfers[0];main=q['main'][index-1]
            assert int(q['game'][index-1]['update'])==index-1 and main['phase']==deficit['phase']
            assert int(main['endFrame'])+1==completed['stamp']['frame']
            start=completed['stamp']['cpu']-int(main['cycles']);finish=completed['stamp']['cpu']
            top=[r for r in q['audio']if r['name']=='AudioUpdate']
            before=max((r for r in top if int(r['endCPU'])<=start),key=lambda r:int(r['endCPU']))
            inside=[r for r in top if int(r['startCPU'])>=start and int(r['endCPU'])<=finish]
            intervals=[before]+inside
            owners=[dict(AudioUpdate=r,disjoint_components=[s for s in q['audio']if int(s['startCPU'])>=int(r['startCPU'])and int(s['endCPU'])<=int(r['endCPU'])],
                         original_source_calls=[s for s in q['cores']if int(s['startCPU'])>=int(r['startCPU'])and int(s['endCPU'])<=int(r['endCPU'])])for r in intervals]
            frame=draw['stamp']['frame']-1
            drawing=[r for r in q['spans']if int(r['startFrame'])==frame and r['name']in ['DrawAllMetasprites','TnDrawEquipment','TnWorldDraw','TnAmmoHud']]
            maps[key]=dict(index_one_based=index,gameplay_row_zero_based=index-1,phase=deficit['phase'],
                actual_before_movement_geometry=q['game'][index-1],captured_draw_construction=draw,captured_completed_return=completed,
                main_span=main,CPUstart_derived_return_minus_inclusive_cycles=start,CPUend_captured=finish,
                real_associated_DMA=transfer,hardware256_sha256=digest(transfer['data']['hardware']),
                surrounding_completed_audio_intervals=owners,foreground_components_same_profile_frame=drawing)
        assert maps['baseline']['actual_before_movement_geometry']==maps['candidate']['actual_before_movement_geometry']
        b,c=[maps[k]['real_associated_DMA']['data']for k in ['baseline','candidate']]
        delta=c['finish']['frame']-b['finish']['frame'];assert delta==(1 if index==560 else 0)
        bv,cv=visible(b['hardware']),visible(c['hardware'])
        page=dict(full256_bytes_equal=b['hardware']==c['hardware'],different_bytes=sum(x!=y for x,y in zip(b['hardware'],c['hardware'])),
                  visible_parts_baseline=sum(bv.values()),visible_parts_candidate=sum(cv.values()),visible_part_multisets_equal=bv==cv,
                  baseline_only_parts=list((bv-cv).elements()),candidate_only_parts=list((cv-bv).elements()),
                  no_unlogged_actor_owner_or_cause_inference=True)
        case_maps.append(dict(strict_deficit=deficit,maps=maps,associated_DMA_epoch_delta=delta,
            classification='actual_matching_construction_DMA_deferred_one_epoch'if delta else'completion_endFrame_label_drift_without_matching_DMA_deferral',
            OAM_page_comparison=page,actual_NMI_entry_stackedPC_and_NmiDisable_store_not_logged=True))
    # Retain the actual persistent hardware page and latest observed source ID
    # for every epoch, including epochs where the previous page persists.
    first=max(v['dma'][0]['data']['finish']['frame']for v in data.values());last=min(v['dma'][-1]['data']['finish']['frame']for v in data.values())
    epochs=[];counts={k:0 for k in data};images={k:None for k in data};latest={k:None for k in data}
    byframe={k:{v['data']['finish']['frame']:v for v in q['dma']}for k,q in data.items()}
    for frame in range(first,last+1):
        row=dict(physical_epoch=frame,cases={})
        for key in data:
            dma=byframe[key].get(frame)
            if dma:
                counts[key]+=1;images[key]=dma['data']['hardware'];latest[key]=dma['source_draw']['index']if dma['source_draw']else None
            assert images[key]is not None
            row['cases'][key]=dict(DMA_this_epoch=bool(dma),cumulative_DMAs=counts[key],latest_observed_source_construction=latest[key],hardware256_sha256=digest(images[key]))
        row['candidate_minus_baseline_DMA_count']=counts['candidate']-counts['baseline']
        epochs.append(row)
    epoch890=next(r for r in epochs if r['physical_epoch']==890)
    assert epoch890['cases']['baseline']['latest_observed_source_construction']==560
    assert not epoch890['cases']['candidate']['DMA_this_epoch']and epoch890['cases']['candidate']['latest_observed_source_construction']==559
    historical=D/'tmnt-native-storage-current50b5-v1/parser-native-pilot-v1'
    baseline_exact={n:sha(folders['baseline']/n)==sha(historical/'baseline-easy'/n)for n in ['gameplay.csv','tmnt-performance-calls.csv','tmnt-performance-frames.csv']};assert all(baseline_exact.values())
    assert sha(folders['candidate']/'source-state.csv')==sha(historical/'candidate-easy/source-state.csv')
    out.mkdir(parents=True)
    (out/'deficit-cases.json').write_text(json.dumps(case_maps,indent=2)+'\n')
    (out/'physical-DMA-epochs.json').write_text(json.dumps(epochs,indent=2)+'\n')
    details=dict(measurement_valid=True,strict_performance_gate_passed=False,strict_comparator_result_unchanged=True,
        source_original_executable_calls=602,original_ordered_APU_requests=2125,original188byte_state_exact=True,
        same_BEFORE_phase_setup_commands=True,baseline_historical_CSVs_byte_exact=baseline_exact,native_inputs=native_inputs,
        phase_costs=phase_costs,disjoint_exclusive_audio_components=exclusive,
        deficits=[dict(update=r['strict_deficit']['update'],classification=r['classification'],DMA_epoch_delta=r['associated_DMA_epoch_delta'])for r in case_maps],
        actual_epoch890=epoch890,initial_DMA_source_draw_unassociated=True,last_constructed_update600_not_yet_transferred_in_bounded_capture=True,
        minimum_cumulative_DMA_difference=min(r['candidate_minus_baseline_DMA_count']for r in epochs),
        full_OAM_page_equality_not_claimed=True,actual_NMIentry_stackedPC_or_NmiDisable_store_timing_not_recorded=True,
        causal_intersecting_AudioUpdate_is_actual_but_NMIacceptance_time_not_inferred=True,
        no_native_recovery_or_adoption_claim=True)
    (out/'diagnosis.json').write_text(json.dumps(details,indent=2)+'\n')
    shutil.copyfile(pair/'easy-strict-proof.json',out/'easy-strict-proof.json')
    (out/'tools').mkdir();tools={}
    for name in ['tmnt_equipment_channel_native_ready_v1.py','tmnt_equipment_channel_native_report_v1.py','tmnt_equipment_channel_native_report_v2.py','tmnt_native_storage_native_compare.py']:
        path=ROOT/'tools/audit'/name;shutil.copyfile(path,out/'tools'/name);tools[name]=sha(path)
    artifacts={str(path):sha(path)for folder in folders.values()for path in folder.rglob('*')if path.is_file()}
    for path in [pair/'readiness.json',pair/'commands.json',pair/'runtime/settings.json',source]:artifacts[str(path)]=sha(path)
    report=f'''TMNT70BA: ONE MATCHED EASY600 PAIR, STRICT PREFIX GATE FAILED
Baseline {CURRENT}
Candidate {DIGEST}
One baseline and one candidate launch; sequential grant explicitly RELEASED.
No retry, Hard, other campaign, source optimization or adoption.

All source/hardware guards PASS:600equal updates/actualnumeric Easy0, identical
five BEFORE-phase setup lists,602original executable188-byte states and2125
ordered original APUs. Native8400hardware comparisons,54active DMC/540held
DAC44frames,600IRQs/921totalNMIs/maxdepth1; wrong/unsafeDMA0. Both5SMC/PRGbank/
stack/actualCHR/current-player-image guards pass. Candidate minimumSP228 versus
baseline233, safely above stackfloor123. Baseline three historical gameplay/
call/frame CSVs are byte-exact. Candidate source-state equals immutable9a.

StrictFAIL is unchanged:3absolute and3phase prefixes at actual1-based updates
532,560,588; each says+1completed-update frame label, despite candidate draw
construction counts already AHEAD by2/4/3. Overall candidate575DMA versus572;
secondary95versus92draws,25versus28lagNMIs. Otherfourphases120draws/no addedlag.
Longest physical stall stays1. Two0-based gameplay input samples differ528/560;
all other recorded fields match. At the three exact deficient updates, full
BEFORE-movement CSVrows531/559/587 (including input/position/health/gear/ammo/
pose/shot kinds/enemy geometry) are pairwise identical. This is staged same-work
arena scope, not natural gear acquisition or whole captured gameplay RAM.

ACTUAL ASSOCIATED DMA CLASSIFICATION, additive only:
532: baseline return frame861/scan227/dot190; candidate862/240/332. Matching
source532 DMA finishes in SAME epoch862 (baseline CPU25639826, candidate25639830).
This is endFrame completion-label drift, without that construction's DMA delay.
588: baseline return917/219/236; candidate918/240/59. Matching source588 DMA
finishes in SAME epoch918 (baseline27307536,candidate27307538). Same distinction.
560: REAL one-epoch deferral. Baseline source560 DMA finishes epoch890,
CPU26473684. Candidate source560 finishes891,CPU26503462. At actualepoch890
candidate performs NO DMA and retains source559 from epoch889; baseline shows
source560. Candidate561 has no draw, then source562 transfers epoch892. This
matching-construction delay remains a real blocking result, despite more total
DMAs/no addedphase aggregate lag and two other rawlabel-only deficits.

Every mapped transfer has exact complete256B source==hardware destination,
safe start/finishscan241..260 in one physical epoch. Full paired OAM images
are NOT equal:145/145/133bytes differ at532/560/588. Visible Y<240 sprite-part
multisets have two Y-coordinate differences at532 (168versus167) and560
(144versus141);588's visible tuple multiset is equal. The records do not bind
those parts to an actor or explain their cause; no guessed ownership/rotation
or RGB/background/CHR equality claim is made. Full pages, hashes, tuple diffs
and physical persistent-image/source-ID epoch mapping are frozen.

Deficit560 actual preceding AudioUpdate: baseline starts26444195,ends26447141;
candidate26444197..26448238 (inclusive2946versus4041,1095added). Captured Main
return minus capturedinclusivecycles gives starts26447205versus26448299.
Main foreground excludingISR is24942versus24438 (candidate saves504). Actual
candidate AudioUpdate26472584..26475088 lies INSIDE that Main call before
captured return26475490; baseline returns26472267 before its next corresponding
AudioUpdate. Full preceding/intersecting audio, original source tick/call and
disjoint owner spans are frozen. ActualNMIentry/stackedPC and exact NmiDisable
publication-store times were NOT logged; do not turn AudioUpdate entry or
reconstructed CPUstart into an observed NMI acceptance/deadline. No new saving
or optimization target is asserted before ROOT reviews these classifications.

The source740..749/735model and5..14margin remain model facts, not a recovery
proof. Cold renderer+2/+7 and earlier8d602+119/c195+191/source/native negatives
remain immutable. New full result/runtime/scripts/settings/host logs/raw CSV/
JSONL and source checkpoint are hash-bound. No user settings or emulator touched.
Initial DMA precedes first logged construction; final source600 has no nextDMA
within the bounded capture. Those edges remain explicit rather than fabricated.
No production/Git/Downloads mutation or acceptance. StrictFAIL retained.
'''
    (out/'report.txt').write_text(report)
    doc=ROOT/'docs/qa/tmnt-equipment-channel-native-2026-10-26.txt';doc.write_text(report+'\nFrozen native packet: '+str(out)+'\n')
    receipt=dict(frozen=True,accepted=False,performance_gate_passed=False,source_hardware_guard_passed=True,
        baseline_ROM_sha256=CURRENT,candidate_ROM_sha256=DIGEST,grant_released=True,native_scope='one matched Easy600 pair',
        actual_mode=0,source_calls=602,original_APUs=2125,total_baseline_DMA=572,total_candidate_DMA=575,
        added_secondary_skips=-3,absolute_prefix_deficits=3,phase_prefix_deficits=3,
        actual_deferral_updates=[560],completion_label_only_updates=[532,588],
        artifacts=artifacts,tools=tools,source_receipt_sha256=sha(source),diagnosis_sha256=sha(out/'diagnosis.json'),
        deficit_cases_sha256=sha(out/'deficit-cases.json'),physical_DMA_epochs_sha256=sha(out/'physical-DMA-epochs.json'),
        strict_sha256=sha(out/'easy-strict-proof.json'),report_sha256=sha(doc))
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(frozen=True,accepted=False,receipt_sha256=sha(out/'receipt.json'),report_sha256=sha(doc),
        exact_source602_APU2125=True,strict_prefix_deficits=3,label_only=[532,588],actual_one_epoch_deferral=[560],
        minimum_cumulative_DMA_difference=details['minimum_cumulative_DMA_difference'])))


if __name__=='__main__':main()
