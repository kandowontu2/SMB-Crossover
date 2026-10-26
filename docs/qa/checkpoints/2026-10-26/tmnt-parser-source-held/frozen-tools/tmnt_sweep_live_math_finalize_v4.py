"""Freeze the exact composed C87 candidate and finite native-pair readiness."""
from pathlib import Path
import argparse
import difflib
import json
import shutil
import zipfile
from tmnt_native_storage_driver import ROOT,CURRENT,sha

D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
DIGEST='53736e142c6cf568039a3c4927c9356077e3358b7c02fb7b69d3ca72985f2ff6'


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    out=a.output;trial=D/'tmnt-sweep-live-math-v1';union=D/'tmnt-sweep-cv3-render-combined-v2'
    original=D/'tmnt-native-storage-current50b5-v1/current-baseline-v1'
    fast=D/'tmnt-sweep-fast-ready-v1';render=D/'root-tmnt-render-combined-v1'
    native=D/'tmnt-sweep-live-math-native-ready-v1'
    assert not out.exists()and not out.resolve().is_relative_to(ROOT)
    assert sha(trial/'candidate.nes')==DIGEST and sha(original/'baseline.nes')==CURRENT
    fresh={}
    for name in ['full-math-composed-v2','hot-cue404-v1','audio-irq-v1','owners-v1','outer-v1','mixer-v1','cues-v1','build-controls-v1']:
        path=trial/name/'proof.json';q=json.loads(path.read_text())
        assert q['passed']and q['candidate_ROM_sha256']==DIGEST
        fresh[name]=dict(path=str(path),sha256=sha(path))
    assert json.loads((trial/'full-math-composed-v2/proof.json').read_text())['math_cases']==129920
    assert json.loads((trial/'outer-v1/proof.json').read_text())['total_calls']==12256
    assert json.loads((trial/'mixer-v1/proof.json').read_text())['complete_mixer_calls']==9216
    candidate=(trial/'candidate.nes').read_bytes();previous=(union/'candidate.nes').read_bytes()
    bank=lambda raw,n:raw[16+n*8192:16+(n+1)*8192]
    assert [n for n in range(128)if bank(candidate,n)!=bank(previous,n)]==[87]
    assert bank(candidate,87)[:0x1500]==bank(previous,87)[:0x1500]==bank((render/'candidate.nes').read_bytes(),87)[:0x1500]
    core=(fast/'candidate.nes').read_bytes();inherited_banks=[63,99,125,126,127]
    assert all(bank(candidate,n)==bank(core,n)for n in inherited_banks)
    # The frozen ready catalog is authoritative for the exact earlier proof path.
    contracts=json.loads((fast/'qualification.json').read_text());song=Path(contracts['proofs']['songs']['path'])
    source_gold=json.loads(song.read_text());assert source_gold['passed']and source_gold['original_calls']==192016
    inherited=dict(original16song_driver_gold=dict(path=str(song),sha256=sha(song),
        actual_qualified_ROM_sha256=source_gold['candidate_ROM_sha256'],
        whole_compiled_banks_identical=inherited_banks,explicitly_inherited_not_fresh_or_native=True),
        renderer={name:dict(path=str(union/name/'proof.json'),sha256=sha(union/name/'proof.json'))
                  for name in ['renderer-v1','render-caller-irq-v1']},
        renderer_bank87_prefix_bytes=0x1500,renderer_tail_not_executed_by_draw_callers=True)
    for row in inherited['renderer'].values():assert json.loads(Path(row['path']).read_text())['passed']
    ready=json.loads((native/'readiness.json').read_text());assert ready['candidate_ROM_sha256']==DIGEST
    for label in ['baseline','candidate']:
        case=native/(label+'-easy');assert sha(case/'binding.json')==ready['case_bindings'][label]
        binding=json.loads((case/'binding.json').read_text());assert all(sha(Path(n))==h for n,h in binding['dependencies'].items())
        assert json.loads((case/'mock-proof.json').read_text())['passed']
        assert not(case/'host.log').exists(),'This packet must be frozen before native launch'
    out.mkdir(parents=True);source=out/'source';shutil.copytree(trial/'source',source,ignore=shutil.ignore_patterns('__pycache__'))
    paths={p.relative_to(source).as_posix():p for p in source.rglob('*')if p.is_file()}
    bindings={n:sha(path)for n,path in sorted(paths.items())}
    (out/'source-bindings.json').write_text(json.dumps(bindings,indent=2)+'\n')
    source_parents={'50b5':original/'source','e595':union/'source'}
    manifests={}
    for name,parent in source_parents.items():
        old={p.relative_to(parent).as_posix():sha(p)for p in parent.rglob('*')if p.is_file() and '__pycache__' not in p.parts}
        assert not(set(old)-set(bindings)),('Removed source input',name)
        manifests[name]={n:dict(before_sha256=old.get(n),after_sha256=h)for n,h in bindings.items()if old.get(n)!=h}
        (out/f'changed-source-versus-{name}.json').write_text(json.dumps(manifests[name],indent=2)+'\n')
    assert set(manifests['e595'])=={'src/tmnt_sweep_fast.s'}
    patch=''
    for name in sorted(manifests['50b5']):
        old=source_parents['50b5']/name
        try:
            left=old.read_text(encoding='utf-8').splitlines(True)if old.exists()else[]
            right=paths[name].read_text(encoding='utf-8').splitlines(True)
        except UnicodeDecodeError:
            patch+='Binary files a/'+name+' and b/'+name+' differ; exact bytes bound in source manifest/archive.\n'
        else:
            patch+=''.join(difflib.unified_diff(left,right,fromfile='a/'+name,tofile='b/'+name))
    (out/'review.patch').write_text(patch)
    with zipfile.ZipFile(out/'source.zip','w',compression=zipfile.ZIP_DEFLATED)as z:
        for name,path in sorted(paths.items()):z.write(path,name)
    for ext in ['.nes','.lbl','.dbg','.map','.build.json','.cv3-mirror.json']:shutil.copyfile(trial/('candidate'+ext),out/('candidate'+ext))
    for name,path in {'composition-proof.json':union/'composition-proof.json',
                     'live-math-source-proof.json':trial/'preparation-live-math.json',
                     'deadline-erratum.json':D/'tmnt-deadline-acceptance-erratum-v1/proof.json',
                     'native-readiness.json':native/'readiness.json','native-commands.json':native/'commands.json'}.items():shutil.copyfile(path,out/name)
    tools=['tmnt_sweep_live_math_source_v1.py','tmnt_sweep_live_math_irq_v1.py',
           'tmnt_sweep_live_math_build_controls_v1.py','tmnt_sweep_live_math_native_v1.py',
           'tmnt_sweep_live_math_finalize_v4.py','tmnt_sweep_cv3_render_compose_v2.py',
           'tmnt_sweep_inline_gate_source_v1.py','tmnt_sweep_composed_outer_v1.py','tmnt_sweep_composed_mixer_v1.py']
    (out/'tools').mkdir();toolbindings={}
    for name in tools:
        path=ROOT/'tools/audit'/name;shutil.copyfile(path,out/'tools'/name);toolbindings[name]=sha(path)
    report=f'''TMNT COMPOSED SOURCE CANDIDATE: PRIVATE, NOT INSTALLED
Accepted production: {CURRENT}
Exact candidate: {DIGEST}
Full source files: {len(paths)}; changed inputs versus50b5: {len(manifests['50b5'])}.
Literal source0c45 CV3 effects, root a8e0 renderer/ammo union, inline pulse
specialization and faithful C87 math are composed without overwriting owners.
Cv3FxOwnerInit BFDA38 and whole Cv3DmcResetOwner remain byte-exact0c45.
The genuine sweep gate is A845, the full28B wrapper remains, C87 entry D500.
Only420ROM bytes within87 change versus e595, solely new private C87 code.
Four genuine private helper labels move; full mapping is in source proof.
The earlier3deleted CV3 private labels and10real Samus cold relocations remain
the explicit composition exceptions; public callable addresses stay genuine.

FRESH:129920 bounded period18..2047 x64physical flags,5740fallback,
17920physical-status,1280complete mixer,9216dirty/held/two-effect mixer,
12256full37identity outer calls,6040shared owner controls and853actualIRQ
boundaries/read-liveness. Full final state/ordered original sound outputs pass.
Canonical rebuild exact; ordinary flagoffs d444cac8 and f4ffd248 exact.
Inherited driver-only192016original calls on64504, not relabeled: entire
banks63/99/125/126/127 exact. Renderer5262+4608caller/48IRQ inherited by exact
unchanged87prefix and original callable dependencies. No native result implied.

Actual complete hot407 CPU path5736->5287 saves449 including all routing;
505saves66. These have real original188B source-state bindings and disclosed
arranged before-call Fireball/status inputs, not a full historical mixer dump.
Old410 target was wrong. Additive erratum reconstructs strict-before actual
NMIacceptance441; raw old trace did not capture entry/stackedPC/last MainPC.
449 is only8cycles above that model, NOT proof of recovered native frames.
Current math leaves literal fallback/output ordering. It omits only dead
adapter-derived initial2/3copies, redundant carry/zero stores and final flags
overwritten by the real wrapper. Actual IRQ reads none of these intermediates.
No source tick, APU event, voice, DMCsample, song, sprite, pickup or input cut.

Costs are not uniformly lower. Isolated guarded/fallback component includes
up110cycles routing; fresh37identity cold entries disclose up124 versus0c45,
expanded fallback+12. TMNT cold0c45 owner init adds43/86 versus inline donor;
all26cold cue calls+43 are retained; other2054cue calls improve0..24 there.
Whole hot449 is measured against parser9a, not the generic component baseline.
Other-owner and unsupported externalAPU frameIRQ domain limitations remain.
Actual cold source inhibits frameIRQ; original16songs have no4017requests.

One mistakenly chosen0c45 whole-mixer comparison failed pausedchar0owner4
(0c45 does not own the added TMNT4 lifecycle). Its original failure is retained;
same complete assertions pass on genuine composed e595. No masks were loosened.
First Lua mock launch used a Python lacking lupa; bundled runtime then passed.
No native launched. Both static pair bodies reverse to literal historical
five120update workloads with identical BEFORE-phase setup; actual numeric0
readback, source/APU/DMC/OAMdestination/CHR/NMI/IRQ/bank/stack/5SMC guards stay.
Static old9a601rows/566draw negative and all old negatives remain unchanged.
Current runtime/settings are bound in native-readiness.json; user files untouched.
Fresh matched50b5/5373Easy600 pair requires explicit grant, no retry/Hard.
No Parodius integration, production/Git/Downloads mutation or adoption claim.
'''
    (out/'report.txt').write_text(report)
    doc=ROOT/'docs/qa/tmnt-sweep-composed-live-math-2026-10-25.txt';doc.write_text(report+'\nFrozen external packet: '+str(out)+'\n')
    receipt=dict(frozen=True,accepted=False,source_CPU_only=True,native_run=False,
        accepted_ROM_sha256=CURRENT,candidate_ROM_sha256=DIGEST,source_files=len(paths),
        changed_source_files_vs50b5=len(manifests['50b5']),fresh_proofs=fresh,inherited=inherited,
        source_archive_sha256=sha(out/'source.zip'),source_bindings_sha256=sha(out/'source-bindings.json'),
        review_patch_sha256=sha(out/'review.patch'),tools=toolbindings,report_sha256=sha(doc),
        native_readiness_sha256=sha(native/'readiness.json'),native_pair_path=str(native),
        CPU_hot407_saving=449,reconstructed_acceptance_target=441,native_recovery_claim=False,
        checker_sha256=sha(Path(__file__)))
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(frozen=True,receipt_sha256=sha(out/'receipt.json'),ROM_sha256=DIGEST,
        source_files=len(paths),changed_files=len(manifests['50b5']),report_sha256=sha(doc))))


if __name__=='__main__':main()
