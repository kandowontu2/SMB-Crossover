"""Freeze66b channel stage and direct5373 no-added-source-call proof."""
from pathlib import Path
import argparse
import difflib
import json
import shutil
import zipfile
from check_tmnt_audio_fallback_oc import qualified
from tmnt_native_storage_driver import ROOT,CURRENT,sha

D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
DIGEST='66b911f3a937d3d749b3a88d9e6ba8b1b56b8f2d56c5b16b9317273b13dc20fb'


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    out=a.output;trial=D/'tmnt-parser-channels-v1';parent=D/'tmnt-parser-math-next-v1';native=D/'tmnt-parser-channels-native-ready-v1'
    assert not out.exists()and not out.resolve().is_relative_to(ROOT);assert sha(trial/'candidate.nes')==DIGEST
    proofs={}
    for n in['domain-irq-v1','songs-v1','songs-vs5373-v1','outer-v1','hot404-v1','build-controls-v1']:
        path=trial/n/'proof.json';q=json.loads(path.read_text());assert q['passed']and q['candidate_ROM_sha256']==DIGEST
        proofs[n]=dict(path=str(path),sha256=sha(path))
    gold=json.loads((trial/'songs-vs5373-v1/proof.json').read_text());assert gold['original_calls']==192016 and not gold['regressions']
    assert max(map(int,gold['cycle_delta_histogram']))==0
    assert qualified(parent/'candidate.nes').items()<=qualified(trial/'candidate.nes').items()
    prep=json.loads((native/'readiness.json').read_text());assert prep['candidate_ROM_sha256']==DIGEST
    for n in['baseline','candidate']:
        f=native/(n+'-easy');assert not(f/'host.log').exists()
        assert sha(f/'binding.json')==prep['case_bindings'][n]and json.loads((f/'mock-proof.json').read_text())['passed']
    out.mkdir(parents=True);source=out/'source';shutil.copytree(trial/'source',source,ignore=shutil.ignore_patterns('__pycache__'))
    paths={p.relative_to(source).as_posix():p for p in source.rglob('*')if p.is_file()};hashes={n:sha(p)for n,p in sorted(paths.items())}
    (out/'source-bindings.json').write_text(json.dumps(hashes,indent=2)+'\n');changes={}
    parents={'1346':parent/'source','5373':D/'tmnt-sweep-live-math-v1/source','50b5':D/'tmnt-native-storage-current50b5-v1/current-baseline-v1/source'}
    for n,base in parents.items():
        old={p.relative_to(base).as_posix():sha(p)for p in base.rglob('*')if p.is_file()and'__pycache__'not in p.parts}
        assert not(set(old)-set(hashes));changes[n]={k:dict(before_sha256=old.get(k),after_sha256=h)for k,h in hashes.items()if old.get(k)!=h}
        (out/f'changed-source-versus-{n}.json').write_text(json.dumps(changes[n],indent=2)+'\n')
    assert set(changes['1346'])=={'src/tmnt-native.inc','src/tmnt_audio.s','src/tmnt_parser_channels.s'}
    patch=''
    for n in sorted(changes['1346']):
        old=parent/'source'/n
        patch+=''.join(difflib.unified_diff(old.read_text().splitlines(True)if old.exists()else[],paths[n].read_text().splitlines(True),fromfile='a/'+n,tofile='b/'+n))
    (out/'review.patch').write_text(patch)
    with zipfile.ZipFile(out/'source.zip','w',compression=zipfile.ZIP_DEFLATED)as z:
        for n,p in sorted(paths.items()):z.write(p,n)
    for ext in['.nes','.lbl','.dbg','.map','.build.json','.cv3-mirror.json']:shutil.copyfile(trial/('candidate'+ext),out/('candidate'+ext))
    for name,path in{'source-preparation.json':trial/'channels-preparation.json','native-readiness.json':native/'readiness.json','native-commands.json':native/'commands.json'}.items():shutil.copyfile(path,out/name)
    names=['tmnt_parser_channels_source_v1.py','tmnt_parser_channels_cpu_v1.py','tmnt_parser_channels_build_controls_v1.py',
        'tmnt_parser_channels_native_v1.py','tmnt_parser_channels_finalize_v1.py','tmnt_parser_math_next_cpu_v1.py',
        'tmnt_parser_math_next_outer_v1.py','tmnt_parser_math_next_hot_v1.py']
    tools={};(out/'tools').mkdir()
    for n in names:
        p=ROOT/'tools/audit'/n;shutil.copyfile(p,out/'tools'/n);tools[n]=sha(p)
    report=f'''TMNT66b: PRIVATE CHANNEL CONTROL SOURCE COMPONENT
2026-10-26. No native grant/run, production install or recovered-draw claim.
Accepted production {CURRENT}
Exact candidate {DIGEST}
Parent13463703ea95e769f332acecbcc0d35ef066f4ddd22624fa3fa771d5773fe60d
Only19additional bytes in63; genuine6B readonly offset table atA21B..A220
uses linker-declaredFF TN_DURATION_MEM tail. All old qualified labels, other
banks/CHR/RAM/source stream assets exact; old private helper bodies unchanged.
The original0,4,8,12,0,12channel mapping replaces only repeated arithmetic.
CPX5+TYA reproduce joined A/Y/C/N/Z/V/D/I exactly; original loop guard and all
source init/play/parser calls, counters, events, registers and voices remain.
No malformed private source X outside0..5 claim. No source-state masks added.

FRESH9600fullflags/statejoins,48actualIRQ/maxstack7, complete entry/pointer
closure,12256full37identity interfaces,602fullAudioUpdates with actual188B
native-state binding/disclosed shared cue, canonical/ordinaryflagoffs exact.
Fresh192016original16song calls against1346 preserve549602orderedAPUs and
1099204writerreturns; every192000Play saves31cycles,16Init unchanged.
Fresh DIRECT5373->66b192016original calls ALSO pass; every call is no slower
(range-214..0), all16song means/peaks improve. This clears1346's12positive
individual source calls in the COMBINED candidate without retagging that packet.

Actual complete caller savings versus5373:182at407,214at505,212at533.
The new stage itself saves31there. Model735secondary target still leavesabout
523cycles at533; no native replay is requested merely to rediscover shortfall.
Native Easy600static readiness is preparation only, unchanged5x120inputs,
mode0readback and full hardware guards, pinned actualruntime/settings; NOgrant.
Real vblank/DMC/bank/hardware cadence remains open. Four5373actual missed
secondary transfers and508equal-epoch/image evidence remain immutable.

1346 math domains/7144IRQ/NMI product-owner proof inherit only by exact genuine
compiled helper bytes plus fresh full source-interface/golden checks; this new
stage introduces no math accesses. No nested-NMI/foreign-source relaxation.
No A62/C94 Chip reservation, shared125, Parodius, Git or Downloads changes.
'''
    (out/'report.txt').write_text(report);doc=ROOT/'docs/qa/tmnt-parser-channels-2026-10-26.txt';doc.write_text(report+'\nFrozen packet: '+str(out)+'\n')
    receipt=dict(frozen=True,source_CPU_only=True,native_run=False,accepted=False,ROM_sha256=DIGEST,
        source_files=len(paths),changed_source_1346=3,changed_source_5373=len(changes['5373']),changed_source_50b5=len(changes['50b5']),
        proofs=proofs,tools=tools,source_archive_sha256=sha(out/'source.zip'),source_bindings_sha256=sha(out/'source-bindings.json'),
        native_preparation_only_sha256=sha(native/'readiness.json'),native_grant=False,source_call_regressions_vs5373=0,
        additional_hot533_saving_vs5373=212,residual_model_about523=True,
        report_sha256=sha(doc),checker_sha256=sha(Path(__file__)))
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(dict(frozen=True,receipt_sha256=sha(out/'receipt.json'),source_files=len(paths),report_sha256=sha(doc))))


if __name__=='__main__':main()
