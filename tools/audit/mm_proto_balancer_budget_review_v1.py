"""Freeze actual993 owner costs and preserve the identical strictdf failure."""
from pathlib import Path
import argparse
import hashlib
import json

D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
B=D/'robot-balancer-budget-ready-v1';OLD=D/'robot-base-palette-candidate-v2/ready-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:Path(p).write_text(json.dumps(z,indent=2)+'\n')
rows=lambda p:[json.loads(x)for x in Path(p).read_text().splitlines()]


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False)
    for f,h in json.loads((B/'bindings.json').read_text()).items():assert sha(f)==h,f
    n=B/'native';old=OLD/'native'
    assert json.loads((B/'launch-outcome-v1.json').read_text())['returncode']==1
    assert rows(n/'ability-dma-epochs.jsonl')==rows(old/'ability-dma-epochs.jsonl')
    assert rows(n/'events.jsonl')==rows(old/'events.jsonl')
    assert json.loads((n/'first-failure.json').read_text())==json.loads((old/'first-failure.json').read_text())
    assert(n/'actual-ppu.argb').read_bytes()==(old/'actual-ppu.argb').read_bytes()
    assert(n/'actual-ppu-index.csv').read_bytes()==(old/'actual-ppu-index.csv').read_bytes()
    d=rows(n/'bass-diagnostic.jsonl')
    lag=next(x for x in d if x['kind']=='NMI-entry'and x['stamp']['frame']==992)
    entry=next(x for x in d if x['kind']=='NMI-entry'and x['stamp']['frame']==993)
    assert lag['data']['incoming_NmiDisable']==255 and lag['data']['expected_branch']=='lag'
    assert lag['queues']['buffer1_offset']==47 and entry['queues']['buffer1_offset']==54
    assert entry['data']['incoming_NmiDisable']==0 and entry['data']['expected_branch']=='regular'
    packet=entry['queues']['buffer1']
    assert packet[47:55]==[63,12,4,15,23,23,15,0]
    assert packet[28:47]==[63,29,3,15,55,23,63,25,3,22,48,39,63,16,4,34,15,22,16]
    assert entry['state']['X5ChrMode']==[129]+[0]*11
    assert entry['state']['SsChrActive']==0 and entry['state']['InvHudActive']==1 and entry['state']['InvHudPhysical']==243
    heads=[x for x in d if x['kind']=='actual-parser-head'and x['stamp']['frame']==993]
    assert len(heads)==9 and heads[-1]['data']['terminator']
    costs=[heads[i+1]['stamp']['cpu']-heads[i]['stamp']['cpu']for i in range(8)]
    assert costs==[256,136,136,171,152,152,168,168]
    ret={x['data']['name']:x for x in d if x['kind']=='actual-owner-return'and x['stamp']['frame']==993}
    assert ret['SamusFreezeUpdateScreen']['data']['inclusive_cycles']==1417
    assert ret['BankSwitchCHR']['data']['inclusive_cycles']==426
    color_entry=next(x for x in d if x['kind']=='actual-owner-entry'and x['data']['name']=='ColorRotation'and x['stamp']['frame']==991)
    color_write=next(x for x in d if x['kind']=='actual-buffer-or-lease-write'and x['data']['address']==1198 and x['data']['value']==54)
    color_return=next(x for x in d if x['kind']=='actual-owner-return'and x['data']['name']=='ColorRotation'and x['stamp']['frame']==992)
    assert color_entry['stamp']['cpu']<lag['stamp']['cpu']<color_write['stamp']['cpu']<color_return['stamp']['cpu']
    assert color_return['data']['inclusive_cycles']==7499
    assert not any(x['kind']=='actual-parser-head'and x['stamp']['frame']==992 for x in d)
    e=rows(n/'ability-dma-epochs.jsonl')
    fail=next(x for x in e if x['kind']=='actual-PPUMASK-write'and x['scoped']and x['enabling']and not x['safe'])
    assert(fail['stamp']['frame'],fail['stamp']['scanline'],fail['stamp']['cycle'])==(993,1,57)
    disable=[x for x in e if x['kind']=='actual-PPUMASK-write'and not x['enabling']][-1]
    dma=[x for x in e if x['kind']=='completed-DMA-before-render-enable'][-1]
    assert dma['start']['cpu']-disable['stamp']['cpu']==1918
    assert dma['complete']['cpu']-dma['start']['cpu']==517
    assert fail['stamp']['cpu']-dma['complete']['cpu']==4
    selected=[entry,lag,color_entry,color_write,color_return,*heads,*[x for x in d if x['kind']=='actual-owner-return'and x['stamp']['frame']==993],fail]
    put(a.output/'actual993-evidence.json',selected)
    files=[*n.iterdir(),*B.glob('*.json'),B/'launch-host-v1.log',Path(__file__)]
    put(a.output/'external-manifest.json',{str(f):sha(f)for f in files if f.is_file()})
    put(a.output/'proof.json',dict(diagnostic_completed=True,native_profile_pass=False,native_launches=1,retries=0,native_worker_released=True,
        all962_full_DMA_records_semantically_exact=True,all992_completedPPU_and_index_byte_exact=True,
        all_events_and_firstfailure_semantically_exact=True,
        actual993_entry=entry['stamp'],actual993_state=entry['state'],actual993_queues=entry['queues'],
        parser_costs=costs,HUD28_parser_cycles=sum(costs[:4]),GetColors19_parser_cycles=sum(costs[4:7]),ColorRotation7_parser_cycles=168,
        gateway_inclusive_cycles=1417,CHR_inclusive_cycles=426,other_disable_to_DMA_cycles=75,
        disable_to_DMA_cycles=1918,DMA_cycles=517,enable_after_DMA_cycles=4,first_bad_enable=fail,
        redundant_body_3F11_present=False,duplicated_whole_palette_group=False,
        actual_lag992_preserves_inprogress_ColorRotation=True,ColorRotation_inclusive_return7499_includes_actual_lagNMI=True,
        required_uninterrupted_saving_to_original_cutoff_CPU=155,
        cutoff_model='Actualline1dot57 minus precedingprerenderdot274 is465PPUdots/3=155CPU. This is oneepoch distance, not native recovery or futureNMIphase margin.',
        source_cause='ActualHUD28+completeGetColors19 remainpending acrosslag992; ColorRotation source admits initialoffset47 (<49), appends genuine7B3F0C andincrementscycle. Regular993 handles54B and426cycleCHR before517cycleDMA, enablingtoo late.',
        no_product_patch=True,no_deadline_or_outcome_waiver=True,
        evidence_sha256=sha(a.output/'actual993-evidence.json'),manifest_sha256=sha(a.output/'external-manifest.json'),tool_sha256=sha(__file__),
        limits='One read-only exactfailurediagnostic.7499 is inclusiveacrossISR, not exclusiveColorRotationwork. Actual426HDR differs from earlier435inactiveHUD profile; nobackfilled estimates. Source-time stagedcomponent remainsnotnaturalacquisition. No nextfix/nativegrant implied.'))
    print(json.dumps(dict(proof=str(a.output/'proof.json'),sha256=sha(a.output/'proof.json'),strict_pass=False,gateway=1417,CHR=426),indent=2))


if __name__=='__main__':main()
