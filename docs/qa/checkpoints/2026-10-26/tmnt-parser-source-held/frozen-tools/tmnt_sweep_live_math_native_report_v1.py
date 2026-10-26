"""Freeze the single matched Easy600 negative; preserve every strict deficit."""
from pathlib import Path
from collections import defaultdict
import argparse
import csv
import gzip
import json
import math
import shutil
import statistics
from tmnt_native_storage_driver import ROOT,CURRENT,OB,sha
from tmnt_native_storage_cpu import Probe

D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
DIGEST='53736e142c6cf568039a3c4927c9356077e3358b7c02fb7b69d3ca72985f2ff6'


def read(p):
    with p.open()as f:return list(csv.DictReader(f))


def stats(v):
    v=sorted(v);assert v
    return dict(count=len(v),mean=statistics.mean(v),p95_nearest_rank=v[math.ceil(.95*len(v))-1],maximum=max(v))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    out=a.output;pair=D/'tmnt-sweep-live-math-native-ready-v1'
    assert not out.exists()and not out.resolve().is_relative_to(ROOT)
    strict=json.loads((pair/'easy-strict-proof.json').read_text())
    assert strict['measurement_valid']and not strict['performance_gate_passed']and strict['behavior']==0
    assert strict['baseline_ROM_sha256']==CURRENT and strict['candidate_ROM_sha256']==DIGEST
    folders={k:pair/(k+'-easy')for k in ['baseline','candidate']}
    reports={k:json.loads((v/'native-result.json').read_text())for k,v in folders.items()}
    assert all(q['passed']and q['mode-readback.json']==dict(requested=0,actual=0,selected=19)for q in reports.values())
    assert reports['baseline']['dependencies']==reports['candidate']['dependencies']
    setup={}
    for k,f in folders.items():
        rows=[json.loads(x)for x in(f/'before-phase-setup.jsonl').read_text().splitlines()]
        assert len(rows)==10
        setup[k]=[]
        for q in rows:
            if q['kind']!='staged':continue
            writes=q['writes']
            if isinstance(writes,dict):writes=[writes[k]for k in sorted(writes,key=int)]
            assert all(0<=x['address']<0x8000 and not 0x2000<=x['address']<0x5c00 and not 0x7400<=x['address']<0x7500 for x in writes)
            setup[k].append(dict(phase=q['data']['phase'],step=q['data']['step'],writes=[{n:x[n]for n in ['address','value','name']}for x in writes]))
        assert len(setup[k])==5
    assert setup['baseline']==setup['candidate']
    gold=json.loads(gzip.decompress((OB/'probe-v2/song-02.json.gz').read_bytes()))
    original=Probe(D/'tmnt-native-storage-current50b5-v1/standalone-original-v1',True)
    source=read(folders['candidate']/'source-state.csv');apu=read(folders['candidate']/'source-apu.csv')
    assert len(source)==602 and len(apu)==2125
    grouped=defaultdict(list)
    for r in apu:grouped[int(r['serial'])].append([int(r['register']),int(r['value'])])
    positions=list(range(0xe0,0xee))+list(range(0x7000,0x70ae))
    for tick,row in enumerate(source):
        assert int(row['serial'])==tick+1 and int(row['sourceTick'])==tick and int(row['song'])==2
        original.call(gold[tick],2)
        expected=bytes((original.m[at]-(27 if original.origin.get(at)in original.changed_high else 0))&255 for at in positions)
        assert bytes.fromhex(row['ZP14_RAM174_hex'])==expected
        assert grouped[tick+1]==gold[tick]['writes']
    ledgers={k:[json.loads(x)for x in(f/'native-bus.jsonl').read_text().splitlines()]for k,f in folders.items()}
    audio={k:read(f/'audio-components.csv')for k,f in folders.items()}
    phase_costs={};components={}
    for k,f in folders.items():
        foreground=read(f/'tmnt-performance-calls.csv');phase_costs[k]={};components[k]={}
        for phase in ['idle','walk','enemies','primary','secondary']:
            top=[r for r in audio[k]if r['name']=='AudioUpdate'and r['phase']==phase]
            loop=[r for r in foreground if r['name']=='GameLoop'and r['phase']==phase]
            phase_costs[k][phase]=dict(AudioUpdate_inclusive=stats([int(r['inclusiveCycles'])for r in top]),
                AudioUpdate_excluding_IRQ=stats([int(r['CPUcycles'])for r in top]),
                foreground_GameLoop_excluding_NMI_IRQ=stats([int(r['cpuCycles'])for r in loop]))
            names=sorted({r['name']for r in audio[k]if r['phase']==phase})
            components[k][phase]={n:stats([int(r['exclusiveCPUcycles'])for r in audio[k]if r['phase']==phase and r['name']==n])for n in names}
        for top in[r for r in audio[k]if r['name']=='AudioUpdate']:
            nested=[r for r in audio[k]if int(r['startCPU'])>=int(top['startCPU'])and int(r['endCPU'])<=int(top['endCPU'])]
            assert sum(int(r['exclusiveCPUcycles'])for r in nested)==int(top['CPUcycles'])
    first=strict['all_completed_update_prefix_deficits'][0]
    first_loss=next(r for r in strict['all_completed_update_prefix_deficits']if r['fewer_draw_constructions']>0)
    assert first['update']==406 and first_loss['update']==533
    windows={}
    for k in folders:
        windows[k]={}
        for index in [406,407,532,533]:
            records=[r for r in ledgers[k]if r.get('index')==index and r['kind']in ['draw-construction','completed-game-update']]
            complete=next(r for r in records if r['kind']=='completed-game-update')
            draw=next((r for r in records if r['kind']=='draw-construction'),None)
            boundary=draw or complete
            top=max((r for r in audio[k]if r['name']=='AudioUpdate'and int(r['endCPU'])<=boundary['stamp']['cpu']),key=lambda r:int(r['endCPU']))
            nested=[r for r in audio[k]if int(r['startCPU'])>=int(top['startCPU'])and int(r['endCPU'])<=int(top['endCPU'])]
            windows[k][index]=dict(records=records,preceding_AudioUpdate=top,disjoint_components=nested)
    completed=windows['candidate'][406]['records'][-1]
    assert completed['stamp']['cpu']==21886273 and completed['stamp']['scanline']==240
    historical=D/'tmnt-native-storage-current50b5-v1/parser-native-pilot-v1'
    baseline_exact={n:sha(folders['baseline']/n)==sha(historical/'baseline-easy'/n)for n in ['gameplay.csv','tmnt-performance-calls.csv','tmnt-performance-frames.csv']}
    assert all(baseline_exact.values())
    assert sha(folders['candidate']/'source-state.csv')==sha(historical/'candidate-easy/source-state.csv')
    details=dict(source_original_executable_calls=602,original_ordered_APU_requests=2125,original188byte_state_exact=True,
        baseline_historical_CSVs_exact=baseline_exact,same_BEFORE_setup_commands=True,phase_costs=phase_costs,
        disjoint_exclusive_components=components,first_prefix=first,first_fewer_draw_prefix=first_loss,
        causal_windows=windows,primary_update406_publication_cpu=21886273,
        previous_source_reconstructed_NMIacceptance_cpu=21886293,recorded_actual_NMIentry_or_stackedPC=False,
        scan240_frameCounter_prefix_diff_is_not_claimed_an_actual_NMI_skip=True,
        no_added_primary_phase_skips=True,secondary_skips_baseline=28,secondary_skips_candidate=32,
        no_native_recovery_or_adoption_claim=True)
    out.mkdir(parents=True);(out/'diagnosis.json').write_text(json.dumps(details,indent=2)+'\n')
    shutil.copyfile(pair/'easy-strict-proof.json',out/'easy-strict-proof.json')
    (out/'tools').mkdir();tools={}
    for name in ['tmnt_sweep_live_math_native_v1.py','tmnt_sweep_live_math_native_report_v1.py','tmnt_native_storage_native_compare.py']:
        path=ROOT/'tools/audit'/name;shutil.copyfile(path,out/'tools'/name);tools[name]=sha(path)
    artifacts={str(path):sha(path)for f in folders.values()for path in f.rglob('*')if path.is_file()}
    readiness=pair/'readiness.json';artifacts[str(readiness)]=sha(readiness)
    source_receipt=D/'tmnt-sweep-composed-live-math-ready-v4/receipt.json'
    report=f'''TMNT5373: ONE MATCHED EASY600 NATIVE PAIR, STRICT GATE FAILED
No adoption/retry/Hard. Sequential worker grant explicitly RELEASED.
Baseline {CURRENT}
Candidate {DIGEST}
Source packet {source_receipt} (sha {sha(source_receipt)})
Raw pair {pair}

Both cold actualnumeric0 runs complete600updates, identical five BEFORE-phase
setup command lists and every original source/hardware/DMC/mixed4015/IRQ/NMI/
stack/bank/5SMC/CHR/full256byteOAMdestination guard. All602actual original
executable states188B and2125ordered requests match. Baseline3historical
gameplay/call/frame CSVs byte-exact; candidate source-state same old9a stream.
Native hardware8400comparisons,54activeDMC/540heldDAC44frames,600IRQs,
921NMIs/maxdepth1; minimumSP candidate223/base233; wrong/unsafeDMA0.
Runtime/settings8a439 and full host files bound by unchanged readiness.

STRICT NEGATIVE:572baseline vs568candidate completedDMA. Secondary28->32skips,
longeststall1unchanged. Other four phases0added skipped draws. All70absolute
and70phase prefix deficits retained. Exactly2input-only rows differ532/560;
all other recordedgamefields identical; same-work measurement remains valid.

PRIMARY DISTINCTION: first strict prefix is still406, fewerconstructions0,
physicalframeCounter+1. Baseline completes735scan218/dot295 CPU21883774;
candidate736scan240/dot290 CPU21886273. This is20cycles BEFORE old reconstructed
NMIacceptance21886293, so the rawframeCounter prefix must not be described as
an observed NMIdeadline miss. ActualNMIentry/stackedPC were not recorded.
The aggregateprimary drawcount120is restored, strictprefix timing notpassed.
First actual fewer-draw prefix issecondary533:509baseline vs508candidate.
Diagnosis binds actual406/407/532/533draw/publication/audio intervals, complete
perphaseAudioUpdate/mainmean/P95/max and disjoint exclusive components.
CPU449save and modeled441target are preserved asCPU/reconstruction facts,
never proof that the overallnative gatepassed. No masks/oracles changed.
All earlier native/source/static-observer negatives stay immutable.
No production/Git/Downloads mutation, extra native launch or adoption.
'''
    (out/'report.txt').write_text(report)
    doc=ROOT/'docs/qa/tmnt-sweep-composed-native-2026-10-25.txt';doc.write_text(report+'\nFrozen negative packet: '+str(out)+'\n')
    receipt=dict(frozen=True,accepted=False,performance_gate_passed=False,source_hardware_guard_passed=True,
        baseline_ROM_sha256=CURRENT,candidate_ROM_sha256=DIGEST,grant_released=True,native_scope='one matched Easy600 pair',
        actual_mode=0,source_calls=602,original_APUs=2125,total_baseline_DMA=572,total_candidate_DMA=568,
        added_secondary_skips=4,absolute_prefix_deficits=70,phase_prefix_deficits=70,strict_primary_prefix_still_fails=True,
        actual_primary_NMI_skip_claim=False,artifacts=artifacts,tools=tools,
        source_receipt_sha256=sha(source_receipt),diagnosis_sha256=sha(out/'diagnosis.json'),
        strict_sha256=sha(out/'easy-strict-proof.json'),report_sha256=sha(doc))
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(frozen=True,accepted=False,receipt_sha256=sha(out/'receipt.json'),
        source602_and2125APU_exact=True,added_secondary_skips=4,first_prefix=406,first_draw_loss=533)))


if __name__=='__main__':main()
