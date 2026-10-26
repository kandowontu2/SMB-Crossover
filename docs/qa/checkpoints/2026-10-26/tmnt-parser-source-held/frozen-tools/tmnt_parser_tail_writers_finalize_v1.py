"""Freeze1d741 source STA tails, complete source proofs and retained negatives."""
from pathlib import Path
import argparse
import difflib
import json
import shutil
import zipfile
from check_tmnt_audio_fallback_oc import qualified
from tmnt_native_storage_driver import ROOT,CURRENT,sha

D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
DIGEST='1d741cfa4c502b22906eb8fb74296c12899f34cf03be86e0eb31131fc77e353e'


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    out=a.output;trial=D/'tmnt-parser-tail-writers-v2';parent=D/'tmnt-parser-unrolled-v1'
    assert not out.exists()and not out.resolve().is_relative_to(ROOT);assert sha(trial/'candidate.nes')==DIGEST
    proofs={}
    for n in['domain-irq-v2','songs-v2','outer-v2','hot404-v1','build-controls-v1']:
        p=trial/n/'proof.json';q=json.loads(p.read_text());assert q['passed']and q['candidate_ROM_sha256']==DIGEST
        proofs[n]=dict(path=str(p),sha256=sha(p))
    q=json.loads((trial/'songs-v2/proof.json').read_text());assert q['original_calls']==192016 and not q['regressions']
    assert max(map(int,q['cycle_delta_histogram']))==0
    assert qualified(parent/'candidate.nes').items()<=qualified(trial/'candidate.nes').items()
    out.mkdir(parents=True);source=out/'source';shutil.copytree(trial/'source',source,ignore=shutil.ignore_patterns('__pycache__'))
    paths={p.relative_to(source).as_posix():p for p in source.rglob('*')if p.is_file()};hashes={n:sha(p)for n,p in sorted(paths.items())}
    (out/'source-bindings.json').write_text(json.dumps(hashes,indent=2)+'\n');changes={}
    for label,base in{'5057':parent/'source','5373':D/'tmnt-sweep-live-math-v1/source','50b5':D/'tmnt-native-storage-current50b5-v1/current-baseline-v1/source'}.items():
        old={p.relative_to(base).as_posix():sha(p)for p in base.rglob('*')if p.is_file()and'__pycache__'not in p.parts}
        assert not(set(old)-set(hashes));changes[label]={n:dict(before_sha256=old.get(n),after_sha256=h)for n,h in hashes.items()if old.get(n)!=h}
        (out/f'changed-source-versus-{label}.json').write_text(json.dumps(changes[label],indent=2)+'\n')
    assert set(changes['5057'])=={'src/tmnt-native.inc','src/tmnt_audio.s','src/tmnt_parser_tail_writers.s'}
    patch=''
    for n in sorted(changes['5057']):
        old=parent/'source'/n
        patch+=''.join(difflib.unified_diff(old.read_text().splitlines(True)if old.exists()else[],paths[n].read_text().splitlines(True),fromfile='a/'+n,tofile='b/'+n))
    (out/'review.patch').write_text(patch)
    with zipfile.ZipFile(out/'source.zip','w',compression=zipfile.ZIP_DEFLATED)as z:
        for n,p in sorted(paths.items()):z.write(p,n)
    for ext in['.nes','.lbl','.dbg','.map','.build.json','.cv3-mirror.json']:shutil.copyfile(trial/('candidate'+ext),out/('candidate'+ext))
    shutil.copyfile(trial/'tail-preparation.json',out/'source-preparation.json')
    names=['tmnt_parser_tail_writers_source_v1.py','tmnt_parser_tail_writers_source_v2.py','tmnt_parser_tail_writers_cpu_v1.py',
        'tmnt_parser_tail_writers_cpu_v2.py','tmnt_parser_tail_writers_build_controls_v1.py','tmnt_parser_tail_writers_finalize_v1.py',
        'tmnt_parser_math_next_cpu_v1.py','tmnt_parser_math_next_outer_v1.py','tmnt_parser_math_next_hot_v1.py']
    (out/'tools').mkdir();tools={}
    for n in names:
        p=ROOT/'tools/audit'/n;shutil.copyfile(p,out/'tools'/n);tools[n]=sha(p)
    negatives=dict(source_builder_v1=dict(path=str(D/'tmnt-parser-tail-writers-v1'),
        reason='Preparation exact-text assertion expected uppercase JSR; actual source uses lowercase jsr. No build/run.'),
        songs_v1=dict(path=str(trial/'songs-v1'),reason='Wrong CLI raw-original supplied NSF path instead of standalone compiled directory; no source case executed.'),
        outer_v1=dict(path=str(trial/'outer-v1'),reason='Wrong nonexistent candidate.nes baseline filename; no case executed. Fresh outer-v2 explicitly compares5057 component interfaces.'),
        IRQ_v1=dict(path=str(trial/'domain-irq-v1'),diagnostic_path=str(trial/'domain-irq-diagnostic-v1'),
            reason='Final source store list incorrectly included five real compiled IRQ PPU/mapper stores. v2 explicitly asserts all five exact IRQ stores separately and retains source write equality; no ROM change.'))
    (out/'retained-negative-attempts.json').write_text(json.dumps(negatives,indent=2)+'\n')
    report=f'''TMNT1D741: PRIVATE SIX SOURCE STA TAILS
2026-10-26. Source/CPU only. No native preparation/run/grant or acceptance.
Accepted production {CURRENT}
Exact candidate {DIGEST}
Exact source parent5057b9e78a54d247914bfc506be4462b4a4d4a1fb9f5f598687bcd8268c17f39
84ROMbytes change, all63: six3B original-source endpointJMPs and66B genuine
tails A29E..A2DF in linker-declared98B FF. 32B remain before genuine products
A300 and original moved streamA400. All old qualified labels/RAM/otherbanks/
header/CHR/source music and samples exact. RootA62/C94/shared125 untouched.

Each tail copies the genuine old STA/PHP/INC/PLP bytes exactly and JMPs to
the same original sourcePC+3. Only adapter JSR/RTS overhead is removed: exactly
6cycles per selected request. All original source endpoints, STA/dirtycounter
increment includingFFwrap, voice calls/order, CPU flags and source events stay
genuine. Old leaf labels/bodies remain exact/executable for other callers.
Original1289instruction/369pointer closure proves no operand interior entry.
Raw-APU conditional original STA branch stays unchanged. No newRAM/SMC/math
owner, foreground math, hardware channel, sample, rate, tick or store omission.

203166 exact domain cases:64meaningfulP flags, all256A, legal indexedX0/4/8/12,
directX0/3/255,Y0/47/255, dirty0/1/127/128/254/255 and actual/edge stack depths.
Complete AXYP/SP, exact two stores/values/order and unchanged-ROM copied leaf
structure pass; everycase-6cycles. 528actual compiled IRQ instruction boundaries
pass full ordinary/source/SMC/bank/math state and AXYP/SP. All five actual IRQ
PPU/mapper stores explicitly exact, not silently dropped. Max total stack8.
This is CPU IRQ injection, not physical timing or nested NMI qualification.

Fresh192016 original16song calls,549602 original ordered requests and1099204
writer-return ABI checks pass original executable, full source188B/foreground
ZP/SP/AXYP/SMC/banks. Per-call delta0..-72, no positive call; all16means/peaks
improve. Prior1346's12 tiny regressions remain recorded there; independently
qualified66b DIRECT5373 plus5057 and this exact0-or-less refinement supplies
transitive no-added-call-cost bound, not a fresh direct5373/native run here.

Fresh12256 complete37identity interfaces pass:36foreign exact and0costchange.
Fresh602 actual native188B state stream and every ordered nonstack source write
exact; source endpoints retained. Shared mixer cue404 is explicitly arranged;
that fullAudio fixture is not a literal full native mixer snapshot. Additional
wholeAudio savings30/48/60 at407/505/533; cumulative vs5373 now257/307/317.
At533 original core3174 -> sourceparent5057 2917 -> candidate2857. The735cycle
secondary publication reconstruction still leavesabout418; it is a model, not
a recorded NMI acceptance deadline or native recovery proof. No new native
attempt to rediscover known shortfall. Strict5373 failure and508equal actual
DMA epochs remain immutable. Current production stays50b5.

Canonical exact rebuild and both ordinary flag-off byte hashes pass. All first
preparation/CLI/IRQ-oracle mistakes retained explicitly in accompanying JSON.
No production/Git/Downloads change. Component is reviewable source optimization,
not completed authentic-music release or proof of recovered display cadence.
'''
    (out/'report.txt').write_text(report);doc=ROOT/'docs/qa/tmnt-parser-tail-writers-2026-10-26.txt';doc.write_text(report+'\nFrozen packet: '+str(out)+'\n')
    receipt=dict(frozen=True,source_CPU_only=True,native_run=False,native_preparation=False,accepted=False,ROM_sha256=DIGEST,
        source_files=len(paths),changed_source_5057=3,changed_source_5373=len(changes['5373']),changed_source_50b5=len(changes['50b5']),proofs=proofs,tools=tools,
        source_archive_sha256=sha(out/'source.zip'),source_bindings_sha256=sha(out/'source-bindings.json'),
        retained_negative_attempts_sha256=sha(out/'retained-negative-attempts.json'),native_grant=False,
        actual_extra_hot533_saving_vs5373=317,residual_model_about418=True,report_sha256=sha(doc),checker_sha256=sha(Path(__file__)))
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(dict(frozen=True,receipt_sha256=sha(out/'receipt.json'),source_files=len(paths),report_sha256=sha(doc))))


if __name__=='__main__':main()
