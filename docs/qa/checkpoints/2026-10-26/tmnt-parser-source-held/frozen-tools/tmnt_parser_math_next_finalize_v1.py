"""Freeze1346 source/CPU component; no native grant or recovery claim."""
from pathlib import Path
import argparse
import difflib
import json
import shutil
import zipfile
from check_tmnt_audio_fallback_oc import qualified
from tmnt_native_storage_driver import ROOT,CURRENT,sha

D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
DIGEST='13463703ea95e769f332acecbcc0d35ef066f4ddd22624fa3fa771d5773fe60d'


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    out=a.output;trial=D/'tmnt-parser-math-next-v1';parent=D/'tmnt-sweep-live-math-v1';native=D/'tmnt-parser-math-next-native-ready-v1'
    assert not out.exists()and not out.resolve().is_relative_to(ROOT)
    assert sha(trial/'candidate.nes')==DIGEST
    fresh={}
    for n in ['domain-v1','songs-v1','outer-v1','hot404-v1','irq-v1','ownership-v1','build-controls-v1']:
        p=trial/n/'proof.json';q=json.loads(p.read_text());assert q['passed']and q['candidate_ROM_sha256']==DIGEST
        fresh[n]=dict(path=str(p),sha256=sha(p))
    assert json.loads((trial/'songs-v1/proof.json').read_text())['original_calls']==192016
    assert qualified(parent/'candidate.nes').items()<=qualified(trial/'candidate.nes').items()
    readiness=json.loads((native/'readiness.json').read_text());assert readiness['candidate_ROM_sha256']==DIGEST
    for name in ['baseline','candidate']:
        f=native/(name+'-easy');assert sha(f/'binding.json')==readiness['case_bindings'][name]
        assert not(f/'host.log').exists()and json.loads((f/'mock-proof.json').read_text())['passed']
    out.mkdir(parents=True);source=out/'source';shutil.copytree(trial/'source',source,ignore=shutil.ignore_patterns('__pycache__'))
    paths={p.relative_to(source).as_posix():p for p in source.rglob('*')if p.is_file()}
    hashes={n:sha(p)for n,p in sorted(paths.items())};(out/'source-bindings.json').write_text(json.dumps(hashes,indent=2)+'\n')
    changes={};patch=''
    for label,base in [('5373',parent/'source'),('50b5',D/'tmnt-native-storage-current50b5-v1/current-baseline-v1/source')]:
        old={p.relative_to(base).as_posix():sha(p)for p in base.rglob('*')if p.is_file()and'__pycache__'not in p.parts}
        assert not(set(old)-set(hashes));changes[label]={n:dict(before_sha256=old.get(n),after_sha256=h)for n,h in hashes.items()if old.get(n)!=h}
        (out/f'changed-source-versus-{label}.json').write_text(json.dumps(changes[label],indent=2)+'\n')
    assert set(changes['5373'])=={'src/tmnt-native.inc','src/tmnt_audio.s','src/tmnt_parser_math_next.s'}
    for name in sorted(changes['5373']):
        old=parent/'source'/name
        patch+=''.join(difflib.unified_diff(old.read_text().splitlines(True)if old.exists()else[],paths[name].read_text().splitlines(True),fromfile='a/'+name,tofile='b/'+name))
    (out/'review.patch').write_text(patch)
    with zipfile.ZipFile(out/'source.zip','w',compression=zipfile.ZIP_DEFLATED)as z:
        for n,p in sorted(paths.items()):z.write(p,n)
    for ext in ['.nes','.lbl','.dbg','.map','.build.json','.cv3-mirror.json']:shutil.copyfile(trial/('candidate'+ext),out/('candidate'+ext))
    for name,p in {'source-preparation.json':trial/'preparation-next.json','native-readiness.json':native/'readiness.json','native-commands.json':native/'commands.json'}.items():shutil.copyfile(p,out/name)
    tools=['tmnt_parser_math_next_'+n+'_v1.py'for n in ['source','cpu','outer','hot','irq','ownership','build_controls','native','finalize']]
    (out/'tools').mkdir();toolbindings={}
    for n in tools:
        p=ROOT/'tools/audit'/n;shutil.copyfile(p,out/'tools'/n);toolbindings[n]=sha(p)
    report=f'''TMNT1346: PRIVATE SOURCE/CPU MATH AND PARSER COMPONENT
2026-10-26. NO native grant/run, installation or recovered-draw claim.
Accepted production {CURRENT}
Held exact donor53736e142c6cf568039a3c4927c9356077e3358b7c02fb7b69d3ca72985f2ff6
New exact candidate {DIGEST}
Only72ROM bytes change, all in63:68B new real helpers inside originalFF
A1B2..A1FF plus two genuine3B numeric-source entry hooks. Every old qualified
label, otherbank, CHR/header and sourceRAM address is exact. Source archive
{len(paths)}files,3source changes versus5373/{len(changes['50b5'])}versus50b5.
Reserved62/94 Chip tails, shared125 and currentParodius remain untouched.

AAD0 repeated sums use hardware product only when its highbyte iszero.
Early-carry inputs retain the original literal CLC/ADC/carry/DEX loop and X.
Fast route reconstructs the real last-ADC V and reaches genuine CMP80/writer.
Count0/1, overflow and abstract outside-source byte edges preserve fullflags.
The source variable is TnAudioZp+2 =physicalE0; helper comment/fixture E2 is
relative-offset terminology, not a physical E2 address or changed alias.
A671 inlines EVERY original AF96 pointer instruction, then exact duration
DEC/branch joins. Original numericAF96 remains genuine for its other callers.
No init/play/tick, source register/state, sample, voice, handler/event, APUstore,
note or music-rate removal. This is instruction/call-overhead optimization.

FRESH qualification:132096 bounded source-loop cases (0..128 x1..16 x64flags),
4224outside-count/byte edges;110592actual pointer/duration join cases;
192016original16song calls,549602orderedAPUs,1099204writerreturns, exact source
AXYP/SP/188Bstate/foregroundZP/SMC/banks;12256full37identity outer calls;
602fullAudioUpdates bound to actual native188Bstates with disclosed shared
cue/status inputs;7144real compiled IRQ boundaries/maxstack7; source/compiled
multiplier owner/entry closure proof; canonical and ordinaryflagoffs exact.
All36foreign identities preserve fullstate/APU/math and0cyclechange.

Extra actual complete-source caller savings vs5373:151at407,183at505,181at533.
602call stream improves0..183. All16song means/peaks improve, BUT12individual
calls regress:4x+1,7x+3,1x+6. These are retained in songs proof, not masked.
Raw early-carry helper component can add28, source pointer path saves7/8.
Model735remaining-secondary target is NOT met; about554still remains at533
under the same reconstruction. No native launch requested just to repeat it.
Unchanged matchedEasy600 static readiness is preparation ONLY, pinned actual
runtime/settings and mode0readback, no worker held or permission inferred.

Ownership premise is explicit: product reads return products, not operands;
both operands are written before each read. TMNT19 runs serial inside existing
single-depthNMI, exclusive ofchar1 MM3/Proto owners. Real IRQ has no product
access and every reached helper boundary preserves products/source/ABI.
No foreground math, fake operandrestore or unsupported nested-NMI claim.
Previous5373 strict negative and508actualDMA epoch evidence are immutable.
Actual hardware, source clock evolution, vblank/DMC contention and remaining
four lost draws are OPEN. Source/CPU equivalence does not close performance.
'''
    (out/'report.txt').write_text(report);doc=ROOT/'docs/qa/tmnt-parser-math-next-2026-10-26.txt';doc.write_text(report+'\nFrozen packet: '+str(out)+'\n')
    receipt=dict(frozen=True,source_CPU_only=True,native_run=False,accepted=False,candidate_ROM_sha256=DIGEST,
        parent_ROM_sha256=sha(parent/'candidate.nes'),accepted_ROM_sha256=CURRENT,source_files=len(paths),
        changed_source_5373=3,changed_source_50b5=len(changes['50b5']),fresh_proofs=fresh,tools=toolbindings,
        source_archive_sha256=sha(out/'source.zip'),source_bindings_sha256=sha(out/'source-bindings.json'),
        native_preparation_only_sha256=sha(native/'readiness.json'),native_grant=False,
        individual_source_call_regressions=12,maximum_regression_cycles=6,
        additional_actual_hot533_saving=181,residual_model_about554=True,native_recovery_claim=False,
        report_sha256=sha(doc),checker_sha256=sha(Path(__file__)))
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(dict(frozen=True,receipt_sha256=sha(out/'receipt.json'),report_sha256=sha(doc),source_files=len(paths))))


if __name__=='__main__':main()
