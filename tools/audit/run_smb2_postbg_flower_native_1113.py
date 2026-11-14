"""Root-queue actual Downloads Flower/vegetable runs; metadata never writes."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

import replay_smb2_postbg_flower_native_1113 as Replay
from nightly_patch_guard_v1 import check

R=Path(__file__).resolve().parents[2]
OUT=R/'build/smb2-flag-native-1113'
SCRIPT=OUT/'controller.lua'
NIGHTLY=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
PIN=Replay.C.CANDIDATE
ADAPTER_SHA='04577796b7789175fbf8178ee780f116b82888cfec804d1de16d7a295abce01d'


def prepare(raw,variant,scope):
    assert sha256(raw).hexdigest()==PIN
    assert sha256(Path(Replay.__file__).read_bytes()).hexdigest()==ADAPTER_SHA
    text=Replay.controller(raw,variant,scope)
    parent={'collect':Replay.Flower.COLLECT_SHA,'throw':Replay.Flower.THROW_SHA,'hit':Replay.Flower.HIT_SHA}[scope][variant]
    assert text.count(PIN)==1
    assert sha256(text.replace(PIN,Replay.C.PIN).encode()).hexdigest()==parent
    return text,dict(variant=variant,identity=Replay.Flower.Parent.Root.NAMES[variant],scope=scope,
        controller_SHA256=sha256(text.encode()).hexdigest(),parent_controller_SHA256=parent,
        original_inputs_observers_and_assertions_exact=True)


def table_rows(value):
    if isinstance(value,list):return value
    assert isinstance(value,dict)
    return [value[k]for k in sorted(value,key=lambda k:int(k))]


def source_state(row):
    return {k:row[k]for k in('S2Health','S2MaxHealth','S2Vegetables','S2Holding','S2State','S2Air','S2Fresh')if k in row}


def point(row):
    return {k:row[k]for k in('x','y','updates')if k in row}


def action(row):
    if not row:return None
    return dict(at=point(row.get('s',{})),item=row.get('item'),source=source_state(row.get('source',{})))


def compact_native(result,scope):
    receipt=result['receipt'];natural=receipt.get('natural',{})
    pickups=[]
    for row in table_rows(natural.get('pickups',{})):
        pickups.append(dict(at=point(row.get('s',{})),item=row.get('item'),
            before=source_state(row.get('before',{})),after=source_state(row.get('after',{})),
            erased=row.get('erased'),sound=row.get('sound'),popup=row.get('popup')))
    hit=natural.get('hit')
    evidence=dict(pickups=pickups,pull=action(natural.get('pull_entry')),
        carried=action(natural.get('carried')),thrown=action(natural.get('thrown')),
        projectile_contact=action(natural.get('object_hit')),
        native_defeat=None if not hit else dict(at=point(hit.get('s',{})),before=hit.get('before'),after=hit.get('after')))
    if result['passed']:
        assert receipt['passed']and receipt['ROM_SHA256']==PIN
        assert receipt['capture_files']==receipt['runtime_state_writes']==receipt['new_helpers']==0
        assert result['outputs_written']==0 and not result['images']
        assert len(pickups)==1 and pickups[0]['item']['kind']==1 and pickups[0]['item']['state']>=128
        assert pickups[0]['erased']and pickups[0]['sound']==32 and pickups[0]['popup']==6
        if scope in('throw','hit'):assert evidence['pull']and evidence['carried']and evidence['thrown']
        if scope=='hit':assert evidence['projectile_contact']and evidence['native_defeat']
    return dict(passed=result['passed'],receipt_SHA256=result['receipt_SHA256'],reason=receipt.get('reason'),
        physical_frames=receipt.get('physical_frames'),all_returned_Main=receipt.get('all_returned_Main'),
        endpoint=receipt.get('terminal'),evidence=evidence,outputs_written=result['outputs_written'],
        capture_files=receipt.get('capture_files'),runtime_state_writes=receipt.get('runtime_state_writes'))


def retained_files():
    assert OUT.is_dir()and SCRIPT.is_file(),'Root existing controller slot is required'
    paths=list(OUT.iterdir())
    assert all(p.is_file()and p.name in('candidate.nes','controller.lua')for p in paths)
    return {p.name:sha256(p.read_bytes()).hexdigest()for p in paths if p!=SCRIPT}


def native_case(text,variant,scope,timeout):
    """Root only: one existing controller overwrite and one guarded native run."""
    from capture_budget import preflight,RUN_BYTES
    from run_stdout_mesen_1110 import run
    preserved=retained_files();names={p.name for p in OUT.iterdir()}
    assert check(NIGHTLY)['ROM_sha256']==PIN
    preflight(OUT/'capture',reserved_bytes=RUN_BYTES,reserved_files=0)
    SCRIPT.write_text(text,encoding='utf-8',newline='\n')
    try:
        result=run(SCRIPT,NIGHTLY,OUT/'capture',PIN,timeout,variant=variant)
    finally:
        assert check(NIGHTLY)['ROM_sha256']==PIN
        assert retained_files()==preserved and {p.name for p in OUT.iterdir()}==names
    return compact_native(result,scope)


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--variant',choices=tuple(map(str,range(8)))+('all',),default='4')
    p.add_argument('--scope',choices=Replay.SCOPES,default='collect')
    p.add_argument('--metadata',action='store_true',help='Compile and authenticate only; no files or Mesen.')
    p.add_argument('--timeout',type=int,choices=range(1,241),default=180)
    args=p.parse_args(argv)
    assert check(NIGHTLY)['ROM_sha256']==PIN,'Only exact installed12397 is accepted'
    raw=NIGHTLY.read_bytes();assert sha256(raw).hexdigest()==PIN
    variants=tuple(range(8))if args.variant=='all'else(int(args.variant),)
    aggregate=dict(ROM_SHA256=PIN,launch_context='actual Downloads',scope=args.scope,
        metadata_only=args.metadata,Mesen_run=not args.metadata,results=[],outputs_written=0,
        new_ROM_or_capture_or_receipt_files=0,existing_controller_overwrites=0)
    for variant in variants:
        text,row=prepare(raw,variant,args.scope)
        if not args.metadata:
            row.update(native_case(text,variant,args.scope,args.timeout))
            aggregate['existing_controller_overwrites']+=1
            print(json.dumps(dict(completed_variant=variant,scope=args.scope,passed=row['passed'],
                receipt_SHA256=row['receipt_SHA256'],endpoint=row['endpoint']),separators=(',',':')),flush=True)
        aggregate['results'].append(row)
        if not args.metadata and not row['passed']:
            print(json.dumps(aggregate,separators=(',',':')),flush=True)
            raise AssertionError('Native natural Flower/vegetable qualification failed; original assertion retained')
    assert check(NIGHTLY)['ROM_sha256']==PIN
    aggregate['metadata_compile_passed']=True
    if not args.metadata:aggregate['all_native_cases_passed']=True
    print(json.dumps(aggregate,separators=(',',':')),flush=True)


if __name__=='__main__':main()
