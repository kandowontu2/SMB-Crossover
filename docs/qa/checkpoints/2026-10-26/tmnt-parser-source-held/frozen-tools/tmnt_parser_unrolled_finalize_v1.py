"""Freeze5057 exact six-voice component with honest remaining cadence limit."""
from pathlib import Path
import argparse
import difflib
import json
import shutil
import zipfile
from check_tmnt_audio_fallback_oc import qualified
from tmnt_native_storage_driver import ROOT,CURRENT,sha

D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
DIGEST='5057b9e78a54d247914bfc506be4462b4a4d4a1fb9f5f598687bcd8268c17f39'


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    out=a.output;trial=D/'tmnt-parser-unrolled-v1';parent=D/'tmnt-parser-channels-v1';native=D/'tmnt-parser-unrolled-native-ready-v1'
    assert not out.exists()and not out.resolve().is_relative_to(ROOT);assert sha(trial/'candidate.nes')==DIGEST
    proofs={}
    for n in['header-irq-v1','songs-v1','outer-v1','hot404-v1','build-controls-v1']:
        p=trial/n/'proof.json';q=json.loads(p.read_text());assert q['passed']and q['candidate_ROM_sha256']==DIGEST
        proofs[n]=dict(path=str(p),sha256=sha(p))
    songs=json.loads((trial/'songs-v1/proof.json').read_text());assert songs['original_calls']==192016 and not songs['regressions']
    assert songs['cycle_delta_histogram']=={'-45':192000,'0':16}
    prior=D/'tmnt-parser-channels-v1/songs-vs5373-v1/proof.json';q=json.loads(prior.read_text());assert q['passed']and not q['regressions']
    assert max(map(int,q['cycle_delta_histogram']))==0
    assert qualified(parent/'candidate.nes').items()<=qualified(trial/'candidate.nes').items()
    ready=json.loads((native/'readiness.json').read_text());assert ready['candidate_ROM_sha256']==DIGEST
    for n in['baseline','candidate']:
        f=native/(n+'-easy');assert not(f/'host.log').exists()
        assert sha(f/'binding.json')==ready['case_bindings'][n]and json.loads((f/'mock-proof.json').read_text())['passed']
    out.mkdir(parents=True);source=out/'source';shutil.copytree(trial/'source',source,ignore=shutil.ignore_patterns('__pycache__'))
    paths={p.relative_to(source).as_posix():p for p in source.rglob('*')if p.is_file()};hashes={n:sha(p)for n,p in sorted(paths.items())}
    (out/'source-bindings.json').write_text(json.dumps(hashes,indent=2)+'\n');changes={}
    for label,base in{'66b':parent/'source','5373':D/'tmnt-sweep-live-math-v1/source','50b5':D/'tmnt-native-storage-current50b5-v1/current-baseline-v1/source'}.items():
        old={p.relative_to(base).as_posix():sha(p)for p in base.rglob('*')if p.is_file()and'__pycache__'not in p.parts}
        assert not(set(old)-set(hashes));changes[label]={n:dict(before_sha256=old.get(n),after_sha256=h)for n,h in hashes.items()if old.get(n)!=h}
        (out/f'changed-source-versus-{label}.json').write_text(json.dumps(changes[label],indent=2)+'\n')
    assert set(changes['66b'])=={'src/tmnt-native.inc','src/tmnt_audio.s','src/tmnt_parser_unrolled.s'}
    patch=''
    for n in sorted(changes['66b']):
        old=parent/'source'/n
        patch+=''.join(difflib.unified_diff(old.read_text().splitlines(True)if old.exists()else[],paths[n].read_text().splitlines(True),fromfile='a/'+n,tofile='b/'+n))
    (out/'review.patch').write_text(patch)
    with zipfile.ZipFile(out/'source.zip','w',compression=zipfile.ZIP_DEFLATED)as z:
        for n,p in sorted(paths.items()):z.write(p,n)
    for ext in['.nes','.lbl','.dbg','.map','.build.json','.cv3-mirror.json']:shutil.copyfile(trial/('candidate'+ext),out/('candidate'+ext))
    for name,p in{'source-preparation.json':trial/'unrolled-preparation.json','native-readiness.json':native/'readiness.json','native-commands.json':native/'commands.json'}.items():shutil.copyfile(p,out/name)
    names=['tmnt_parser_unrolled_source_v1.py','tmnt_parser_unrolled_cpu_v1.py','tmnt_parser_unrolled_build_controls_v1.py',
        'tmnt_parser_unrolled_native_v1.py','tmnt_parser_unrolled_finalize_v1.py','tmnt_parser_math_next_cpu_v1.py',
        'tmnt_parser_math_next_outer_v1.py','tmnt_parser_math_next_hot_v1.py']
    (out/'tools').mkdir();tools={}
    for n in names:
        p=ROOT/'tools/audit'/n;shutil.copyfile(p,out/'tools'/n);tools[n]=sha(p)
    report=f'''TMNT5057: PRIVATE EXACT SIX-VOICE SOURCE CONTROL COMPONENT
2026-10-26. No native grant/run, installation or recovered-frame claim.
Accepted production {CURRENT}
Exact candidate {DIGEST}
Held donor66b911f3a937d3d749b3a88d9e6ba8b1b56b8f2d56c5b16b9317273b13dc20fb
Only128ROMbytes change, all63:125B genuine TnNativeUnrolled atA221..A29D in
linker-declaredFF duration-helper tail, plus3B originalA644 entryJMP. Public
TnNativePlay still denotes its real executable entry. All old symbols/other
banks/CHR/RAM and all original stream/music/sample bytes remain exact.

The six immutable voice positions are unrolled. EVERY original A612 call,
active-voice A671 call and all six RAM92/RAM93 stores remain in exact order.
Runtime flags still select each active voice. CPX5+TYA preserve each next
voice's fullA/X/Y/P, finalX6/C1/NZ exactly. No note/event/voice/store/tick cut,
no precomputed capture prefix or state substitution. Discarded returnaddress
bytes differ normally because real calls now return into the new helper.

FRESH602complete calls with actual188B native-state binding;3606per-voice full
AXYP/SP/sourceRAM/SMC/bank/orderedAPU/math induction checks; every ordered
nonstack source write exact;105actual compiledIRQ boundaries/maxstack7. IRQ
cases are actualbefore533state and explicitly arranged all-inactive flags;
no masked/nestedNMI/physical hardware claim. OriginalNSF numericPlay root is
still genuine; no external original instruction/pointer enters its operands.

Fresh original16songs192016calls/549602APUs/1099204writerreturns all exact.
Every192000Play saves45cycles INCLUDING new entry routing,16Init unchanged.
All16song means/peaks improve, no per-call regression. Fresh12256full37identity
interfaces and canonical/ordinaryflagoffs pass; all36foreign cases0change.
Old66b DIRECT5373 proof had0positive source calls; this exact subsequent
per-call0/-45 refinement preserves that bound by composition. It is explicitly
inherited composition, not relabeled native/direct5373 execution of5057.

Full caller extra savings vsheld5373 now227at407,259at505,257at533. Model735
first-secondary requirement still leavesabout478cycles at533. Original
provisional62-unroll estimate was superseded by measured45; no native was
launched just to rediscover shortfall. Native Easy600static readiness remains
preparation only, exact5x120workload/mode0/hardwareguards/currentruntime; NOgrant.
Four actual extra5373secondary misses, strict-prefix negative and508equal
hardware epochs remain immutable. New original-ROM golden/source CPU proofs
do not establish real DMC contention/vblank/IRQ timing or release suitability.
Reserved A62/C94, shared125, Parodius, production/Git/Downloads untouched.
'''
    (out/'report.txt').write_text(report);doc=ROOT/'docs/qa/tmnt-parser-unrolled-2026-10-26.txt';doc.write_text(report+'\nFrozen packet: '+str(out)+'\n')
    receipt=dict(frozen=True,source_CPU_only=True,native_run=False,accepted=False,ROM_sha256=DIGEST,source_files=len(paths),
        changed_source_66b=3,changed_source_5373=len(changes['5373']),changed_source_50b5=len(changes['50b5']),proofs=proofs,tools=tools,
        source_archive_sha256=sha(out/'source.zip'),source_bindings_sha256=sha(out/'source-bindings.json'),
        inherited_no_positive5373_calls=dict(path=str(prior),sha256=sha(prior),exact_next_refinement_delta='0/-45 per same original call'),
        native_preparation_only_sha256=sha(native/'readiness.json'),native_grant=False,actual_extra_hot533_saving=257,residual_model_about478=True,
        report_sha256=sha(doc),checker_sha256=sha(Path(__file__)))
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(dict(frozen=True,receipt_sha256=sha(out/'receipt.json'),source_files=len(paths),report_sha256=sha(doc))))


if __name__=='__main__':main()
