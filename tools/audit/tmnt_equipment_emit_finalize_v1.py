"""Freeze the finite emitter chain, exact state proofs and performance HOLD."""
from pathlib import Path
import argparse
import difflib
import json
import shutil
import zipfile
from check_tmnt_render_oa import load
from check_tmnt_audio_fallback_oc import qualified
from tmnt_native_storage_driver import ROOT,CURRENT,sha

D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
DIGEST='8d60280ccec6cea4a7544cd1745bae03598fee2c05b736877e166dc1d42e1184'


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    out=a.output;trial=D/'tmnt-equipment-cold-kind-v1';base=D/'tmnt-parser-tail-writers-v2'
    assert sha(trial/'candidate.nes')==DIGEST and not out.exists()and not out.resolve().is_relative_to(ROOT)
    proofs={}
    for n in['full-renderer-v1','caller-irq-v2','ownership-v1','audio-outer-v1','build-controls-v2']:
        p=trial/n/'proof.json';q=json.loads(p.read_text());assert q['passed']and q['candidate_ROM_sha256']==DIGEST
        proofs[n]=dict(path=str(p),sha256=sha(p))
    old,new=load(base/'candidate.nes'),load(trial/'candidate.nes');assert qualified(base/'candidate.nes').items()<=qualified(trial/'candidate.nes').items()
    bank=lambda raw,n:raw[16+n*8192:16+(n+1)*8192]
    changes={n:sum(x!=y for x,y in zip(bank(old['raw'],n),bank(new['raw'],n)))for n in range(128)};changes={n:v for n,v in changes.items()if v}
    assert set(changes)=={87}and bank(old['raw'],87)[0x1500:0x1700]==bank(new['raw'],87)[0x1500:0x1700]
    out.mkdir(parents=True);source=out/'source';shutil.copytree(trial/'source',source,ignore=shutil.ignore_patterns('__pycache__'))
    paths={p.relative_to(source).as_posix():p for p in source.rglob('*')if p.is_file()};hashes={n:sha(p)for n,p in sorted(paths.items())}
    (out/'source-bindings.json').write_text(json.dumps(hashes,indent=2)+'\n');deltas={}
    for label,parent in{'1d741':base/'source','5373':D/'tmnt-sweep-live-math-v1/source','50b5':D/'tmnt-native-storage-current50b5-v1/current-baseline-v1/source'}.items():
        oldhash={p.relative_to(parent).as_posix():sha(p)for p in parent.rglob('*')if p.is_file()and'__pycache__'not in p.parts}
        assert not(set(oldhash)-set(hashes));deltas[label]={n:dict(before_sha256=oldhash.get(n),after_sha256=h)for n,h in hashes.items()if oldhash.get(n)!=h}
        (out/f'changed-source-versus-{label}.json').write_text(json.dumps(deltas[label],indent=2)+'\n')
    assert set(deltas['1d741'])=={'src/tmnt.s','src/tmnt_equipment_draw.s','src/tmnt_equipment_icon_fast.s','src/tmnt_equipment_shuriken_fast.s','smb1base-mmc5-expanded.cfg'}
    patch=''
    for n in sorted(deltas['1d741']):
        p=base/'source'/n
        patch+=''.join(difflib.unified_diff(p.read_text().splitlines(True)if p.exists()else[],paths[n].read_text().splitlines(True),fromfile='a/'+n,tofile='b/'+n))
    (out/'review.patch').write_text(patch)
    with zipfile.ZipFile(out/'source.zip','w',compression=zipfile.ZIP_DEFLATED)as z:
        for n,p in sorted(paths.items()):z.write(p,n)
    for ext in['.nes','.lbl','.dbg','.map','.build.json','.cv3-mirror.json']:shutil.copyfile(trial/('candidate'+ext),out/('candidate'+ext))
    names=['tmnt_equipment_fast_emit_source_v1.py','tmnt_equipment_fast_emit_source_v2.py','tmnt_equipment_shuriken_emit_source_v1.py',
        'tmnt_equipment_emit_admission_source_v1.py','tmnt_equipment_emit_admission_source_v2.py','tmnt_equipment_cold_kind_source_v1.py',
        'tmnt_equipment_fast_emit_irq_v1.py','tmnt_equipment_fast_emit_irq_v2.py','tmnt_equipment_emit_ownership_v1.py',
        'tmnt_equipment_fast_emit_build_controls_v1.py','tmnt_equipment_fast_emit_build_controls_v2.py','tmnt_equipment_emit_finalize_v1.py',
        'tmnt_equipment_empty_scans_cpu_v1.py','tmnt_equipment_empty_scans_irq_v1.py','tmnt_parser_math_next_outer_v1.py']
    (out/'tools').mkdir();tools={}
    for n in names:
        p=ROOT/'tools/audit'/n;shutil.copyfile(p,out/'tools'/n);tools[n]=sha(p)
    stages={}
    for label,folder,proof_names in[
        ('admission488',D/'tmnt-equipment-admission-v1',['full-renderer-v1']),
        ('icons4c591',D/'tmnt-equipment-icons-v1',['full-renderer-v1']),
        ('shuriken-c195',D/'tmnt-equipment-shuriken-v1',['full-renderer-v1','caller-irq-v1']),
        ('short5ace',D/'tmnt-equipment-short-admission-v2',['full-renderer-v1','caller-irq-v2','audio-outer-v1','build-controls-v1'])]:
        stages[label]=dict(path=str(folder),ROM_sha256=sha(folder/'candidate.nes'),preparation_sha256=sha(folder/'fast-preparation.json'),
            proofs={n:dict(path=str(folder/n/'proof.json'),sha256=sha(folder/n/'proof.json'))for n in proof_names})
    (out/'prior-stages.json').write_text(json.dumps(stages,indent=2)+'\n')
    failed=D/'tmnt-equipment-short-admission-v1/build.log';assert 'Constant expression expected'in failed.read_text()
    negative=dict(first_assembly_failure=dict(path=str(failed),sha256=sha(failed),reason='Assembler .res could not resolve proc-name expression. v2 uses genuine local EmitterStart at the real function entry; no ROM behavioral issue.'),
        c195_full_positive_costs=dict(path=str(D/'tmnt-equipment-shuriken-v1/full-renderer-v1/cases.json'),sha256=sha(D/'tmnt-equipment-shuriken-v1/full-renderer-v1/cases.json'),maximum_added_cycles=191),
        final_positive_costs=dict(path=str(trial/'ownership-v1/cases.json'),sha256=sha(trial/'ownership-v1/cases.json'),maximum_added_cycles=119))
    (out/'retained-negatives.json').write_text(json.dumps(negative,indent=2)+'\n')
    report=f'''TMNT EXACT EQUIPMENT EMITTERS: SOURCE-QUALIFIED, PERFORMANCE HOLD
2026-10-26. Production remains {CURRENT}
Exact final trial {DIGEST}
Exact frozen source donor1d741cfa4c502b22906eb8fb74296c12899f34cf03be86e0eb31131fc77e353e
Onlybank87 changes ({changes[87]}bytes); all original1d741 labels/RAM/header/CHR
and every otherbank exact. A87 B700..BC8C real helpers, original shared C87
D500..D6FF prefix byte-exact. Source-declared split gives separate A87 tail.
No use of source63remaining32B, shared125 or ROOT A62/C94 storage.

Stages: same54B admission488 saves52selected/0empty/+2pendingnormal; then four
original icon records4c591; then six original two-layer shuriken recordsc195.
All old generic fallback bodies remain literal. No sprite/layer/clip/capacity/
rotation/clock/sample omission. Original per-part X/Y/attribute/tile writes,
CurrentOAMOffset, finalAXYP/SP/R0..R7, all ordinaryRAM/SMC/mapper/CHR publications
and C88 re-publication stores/order match complete actual caller continuations.

Source-derived cold admission5ace moves genuine OWN new private labels only;
entriesB700/B98F and655/766byte footprints stay exact, with real unreachable
FF padding after returns. Every original1d741 label stays exact. Full map of
own private moves is in its preparation; no fake callable aliases. Final8d602
uses EOR-kind classification to retain incomingC/V on earliest legacy paths.
The caller still fixes R3=0/R7=1; iconX is Equipment+79 and Rptr is its exact
readonly right-table entry; shotX is original slot and Rptr follows pose/face.
65534+ checked role entries bind these premises dynamically; compiled source
has exactly one caller per entry and retains all original producer stores.

Fresh final proofs:5262 complete renderer cases/all168 world entries;16384
actual draw caller cases/all64P/fourvariants/icons/capacity/rotation;1682real
compiled IRQ instruction boundaries/maxstack9, all five IRQ stores exact;
1040 extra kind/cold controls. Full state/OAM/VRAM/hardware equality passes.
655 reachable new control instructions prove no A-bank switch, multiplier,
new RAM alias or DMC owner. Original audio core/data/writers/sample code is
inherited by exact unchanged bytes; fresh12256full37identity AudioUpdate
interfaces also pass with ZERO cycle/state/store change for every identity.
Canonical rebuild and both ordinaryflagoff hashes pass. No native grant/run.

PERFORMANCE HOLD: constrained captured-shape equipment1255 ->912..924, saving
331..343 across six shuriken pose/face controls. Actual complete Main RAM was
NOT captured; this is an explicitly arranged same-record component matching
the actual284/443 source spans. Combining frozen source533 saving317 gives
648..660 against the735 reconstruction, stillabout75..87short. Neither the
model nor these source costs prove real native deadline or recovered draws.

Do not hide cold negatives: firstc195 had +191 in dense cases, retained.
Final8d602 standard5262cases max+9, but expanded legal pending-kind controls
expose +119 for three shuriken atHUDY23 with gearoff; three pending boomerang/
Kiai add38; gearoff drop/private-only adds2, empty0. Last-ammo depletion can
clear equipment/selected while shots remain; no unreachability waiver is used.
Full positive examples/counts are retained in ownership proof. No source
correctness failure was repaired by weakening equality. Final candidate stays
HOLD, not a no-harm/cadence restoration. Icons+admission-only4c591 is separately
retained (254saving in constrained fixture), without shuriken guard overhead.

One failed first .res assembly retained. All first native failures from prior
packets, strict5373 negative/508equalDMA and441/735model limits stay unchanged.
Next finite source work should fuse actual caller setup with literal uncommon
paths instead of adding another guard before the unchanged original renderer.
No production, Git, Downloads, native observer/workload or accepted build change.
'''
    (out/'report.txt').write_text(report);doc=ROOT/'docs/qa/tmnt-equipment-emitters-2026-10-26.txt';doc.write_text(report+'\nFrozen packet: '+str(out)+'\n')
    receipt=dict(frozen=True,source_CPU_only=True,native_run=False,accepted=False,performance_status='HOLD',ROM_sha256=DIGEST,
        changed_PRG_bytes=changes,source_files=len(paths),source_changes={n:len(v)for n,v in deltas.items()},proofs=proofs,tools=tools,
        source_archive_sha256=sha(out/'source.zip'),source_bindings_sha256=sha(out/'source-bindings.json'),prior_stages_sha256=sha(out/'prior-stages.json'),
        retained_negatives_sha256=sha(out/'retained-negatives.json'),report_sha256=sha(doc),checker_sha256=sha(Path(__file__)),
        hot_saving_range=[331,343],legal_cold_max_added_cycles=119,residual_model_cycles=[75,87])
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(dict(frozen=True,source_files=len(paths),receipt_sha256=sha(out/'receipt.json'),report_sha256=sha(doc))))


if __name__=='__main__':main()
