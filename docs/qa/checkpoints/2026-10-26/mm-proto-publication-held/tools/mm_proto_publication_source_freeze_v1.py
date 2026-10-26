"""Freeze the finite a801 private source packet; never launch or install."""
from pathlib import Path
import argparse,ast,hashlib,json,shutil,sys,zipfile
R=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
B=D/'mm-proto-publication-candidate-v3'
P=D/'mm-proto-clean-menu-candidates-v1/clean-menu-irq'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n')

def closure(paths):
    seen=set();todo=list(paths)
    while todo:
        p=todo.pop().resolve()
        if p in seen:continue
        seen.add(p)
        if p.suffix!='.py':continue
        for node in ast.walk(ast.parse(p.read_text())):
            names=[node.module]if isinstance(node,ast.ImportFrom)else[n.name for n in node.names]if isinstance(node,ast.Import)else[]
            for name in names:
                if not name:continue
                q=R/'tools/audit'/(name.split('.')[0]+'.py')
                if q.is_file():todo.append(q)
    return seen

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    assert not a.output.exists()and not a.output.resolve().is_relative_to(R);a.output.mkdir(parents=True)
    assert sha(B/'candidate.nes')=='a801f8e397a416e1b12cb6b78bad25774670c8f9fea0e8334cd0c830cf8a3d56'
    proofs=[B/'proof.json']+[B/x/'proof.json'for x in ['render-cpu-v2','records-cpu-v1','callers-cpu-v1','nmi-cpu-v2','lifecycle-cpu-v1','capacity-body-v1','capacity-shots-v1','build-controls-v2']]
    for p in proofs:assert json.loads(p.read_text())['passed'],p
    manifest=json.loads((B/'source-manifest.json').read_text())
    for rel,h in manifest.items():assert sha(B/'source'/rel)==h
    own=[R/'tools/audit'/n for n in ['mm_proto_publication_candidate_v1.py','mm_proto_publication_candidate_v2.py','mm_proto_publication_candidate_v3.py','mm_proto_publication_render_cpu_v1.py','mm_proto_publication_render_cpu_v2.py','mm_proto_publication_records_cpu_v1.py','mm_proto_publication_callers_cpu_v1.py','mm_proto_publication_nmi_cpu_v1.py','mm_proto_publication_nmi_cpu_v2.py','mm_proto_publication_lifecycle_cpu_v1.py','mm_proto_publication_capacity_cpu_v1.py','mm_proto_publication_build_controls_v1.py','mm_proto_publication_build_controls_v2.py',Path(__file__).name]]
    deps=closure(own)
    deps|={Path(sys.executable),R/'tools/Windows/cc65/bin/cl65.exe'}
    import py65.devices.mpu6502
    deps.add(Path(py65.devices.mpu6502.__file__))
    deps|={B/'source'/rel for rel in manifest}
    deps|={B/x for x in['candidate.nes','candidate.dbg','candidate.map','candidate.lbl','source-manifest.json','source.patch','genuine-symbol-movement.json']}
    deps|={P/x for x in['candidate.nes','candidate.dbg','source-manifest.json']}
    deps|={D/'mm-proto-publication-ownership-v1/native-freeze-v1/receipt.json',D/'mm-proto-publication-ownership-v1/freeze-v1/receipt.json'}
    for folder in ['render-cpu-v1','render-cpu-v2','records-cpu-v1','callers-cpu-v1','nmi-cpu-v1','nmi-cpu-v2','lifecycle-cpu-v1','capacity-body-v1','capacity-shots-v1','build-controls-v1','build-controls-v2']:
        deps|={p for p in(B/folder).iterdir()if p.is_file()and p.suffix in['.py','.json']}
    for folder in ['mm-proto-publication-candidate-v1','mm-proto-publication-candidate-v2']:
        deps|={p for p in(D/folder).iterdir()if p.is_file()and p.suffix in['.py','.json']}
    (a.output/'tools').mkdir()
    for p in own:shutil.copyfile(p,a.output/'tools'/p.name)
    (a.output/'dependencies').mkdir()
    for p in sorted(deps):
        if p.is_relative_to(R/'tools/audit')and p not in own:shutil.copyfile(p,a.output/'dependencies'/p.name)
    (a.output/'proofs').mkdir()
    for i,p in enumerate(proofs):shutil.copyfile(p,a.output/'proofs'/f'{i:02d}-{p.parent.name}.json')
    with zipfile.ZipFile(a.output/'source.zip','x',zipfile.ZIP_DEFLATED)as z:
        for rel in sorted(manifest):z.write(B/'source'/rel,rel)
    with zipfile.ZipFile(a.output/'source.zip')as z:
        assert z.testzip()is None and len(z.namelist())==len(manifest)
        for rel,h in manifest.items():assert hashlib.sha256(z.read(rel)).hexdigest()==h
    changed=json.loads((B/'proof.json').read_text())['changed_source']
    for rel in changed:
        dst=a.output/'overlay'/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(B/'source'/rel,dst)
    for f in['source-manifest.json','source.patch','genuine-symbol-movement.json']:shutil.copyfile(B/f,a.output/f)
    report='''Private publication-aware Mega/Proto priority candidate -- SOURCE ONLY

Parent731c918b0f448564587d90fca2979afc9fc0e5eb9b26616f4241801e2e73e16c
Candidatea801f8e397a416e1b12cb6b78bad25774670c8f9fea0e8334cd0c830cf8a3d56
No production/default/settings/Git changes or native run/adoption.

ONE declared ExRAM lifecycle byte5FF8: bit6 requests body0/shot40 priority;
bit7 tags a completed owned source. Repeated source constructions retain
bit6 until the genuine regular NMI AudioUpdate call returns from a real
DMA/input path. The actual Mega/Proto-only core checks its outer return
word E3FC, then scene1/task3/engine8/death0, before XOR C0. Lag/no pending
and foreign routes do not consume. OperMode0 takes the original vanilla
audio route and never reaches the gate; MoveAll/cold/fresh-game resets
clear the byte. No blind every-NMI or source-clock toggle is used.

Both turns reserve the same logicalR40/44 before every original shot.
Body turn maps native body0, shotsR, then world. Shot turn maps original
special/ordinary shots0, bodyS, worldR+S. The genuine world+19/+-13 order,
phase, emitters, capacities, art and all original live projectiles remain.
No shotmux helper, sprite deletion, source audio clock/store/channel/sample
cut, new hidden RAM or global NMI branch is included.

Changed542bytesbank4 and185bank66 only; CHR/header/allotherbanks exact.
New real declared code: bank4 BF33..BF84(82B), bank66 B9A8..BA25(126B),
both verified oldFF. Pinned menuBB50 and fixed NMI/DMA/AudioUpdate entries
stay exact. Sixteen genuine symbol changes include private body/core
branches and one assembler FARCALL_COUNT constant; no existing RAM symbol
moved and no fake aliases are supplied. Fresh canonical and ordinary MMC3/
MMC5 builds reproduce their exact expected hashes.

Finite fresh source controls:
2456 rendering/reference cases and902 actual IRQ boundaries; independent
unchanged731 emitters define both physical partitions. Original whole
AXYP/SP, ordered OAM values/counts, every other RAM/SMC/bank/hardware result
match.1368 cases cover48 Mega poses,27 Proto poses,6 shot kinds, both faces,
ages, outlines and turns.64 real postdraw Main/release/NMI/next-GameLoop
callers preserve original live ABI/state and consume one completed tag.
2156 complete NMI cases and512 IRQ boundaries retain original full source
audio/APU/orderedstores/input/5SMC/banks/physical flags, with only the new
byte changed by its stated contract.528 actual lifecycle cases include
cold CrossoverInit and KbFreshGameInit. Both priority turns independently
pass56392 generic,1696 water and6848 valid Finish-capacity cases each.
Proto valid cursor44..252 cannot0; the arbitrary manualcur0 counterexample
still gives211 instead of212 and is retained as unreachable by that chain.

MEASURED COSTS: owned DrawAll+189..191; ineligible Mega+85..111; foreign
DrawAll-24..-2. Mega/Proto full NMI+17..88; regular pending+87..88; foreign
full NMI exactly0. Common MoveAllSpritesOffscreen+18; existing cold/fresh
initializers0. These positive costs can worsen actual cadence. They are
not a lag-reduction, pixel fairness, native timing or adoption claim.

LIMITS: Alternating consumed constructions cannot ensure every body/shot/
world opaque pixel survives the hardware first8 rule. Original special
shots still precede ordinary fixed-order bullets; dense special groups
may starve ordinary ones, and priority turns trade body/shot/world display.
Native Vine partial OAM writes before a skipped DrawAll remain a separate
integration limit; a tag is not universal whole-page ownership. Native
BrickChunks call is disabled by ENABLE_CROSSOVER; Vine remains compiled.
Prior unchanged731450 observed no active post-Roster edits. A bounded
compiled Vine/no-draw/regularDMA supplemental chain is still pending.
No death/later-area/Proto natural campaign or physical publication/pixels
have been qualified for this candidate. The proposed450 uses exact same
controller/hardware guards and fresh candidate labels, not old hook PCs.

PRESERVED NEGATIVES: candidatev1 assembler constant-padding failure;
candidatev2 segment-order/auto-PROTO_MENU overflow; renderv1 asserted new
mode/tag on plain unmodified parent; NMIv1 incorrectly expected the
OperMode0 vanilla route to enter the gate; buildcontrolsv1 misclassified
assembler FARCALL_COUNT as RAM. Fresh v2 checkers correct only those
specific source or oracle errors; no substantive behavior/physical guard
is relaxed. All earlier c5/00fb/native negatives remain immutable.
'''
    path=R/'docs/qa/mm-proto-publication-source-2026-10-26.txt';path.write_text(report);shutil.copyfile(path,a.output/'report.txt');deps.add(path)
    put(a.output/'bindings.json',{str(p.resolve()):dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(deps)})
    catalog={p.relative_to(a.output).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(a.output.rglob('*'))if p.is_file()}
    put(a.output/'catalog.json',catalog)
    receipt=dict(passed=True,source_only=True,native_run=False,installed=False,ROM_sha256=sha(B/'candidate.nes'),parent_ROM_sha256=sha(P/'candidate.nes'),source_files=len(manifest),changed_files=changed,proofs={str(p.resolve()):sha(p)for p in proofs},catalog_files=len(catalog),catalog_sha256=sha(a.output/'catalog.json'),bindings=len(deps),bindings_sha256=sha(a.output/'bindings.json'),source_zip_sha256=sha(a.output/'source.zip'),report_sha256=sha(path),tools=len(own),source_costs_and_partial_writer_limits_explicit=True,tool_sha256=sha(__file__))
    put(a.output/'receipt.json',receipt);print(json.dumps(dict(receipt_sha256=sha(a.output/'receipt.json'),**receipt),indent=2))
if __name__=='__main__':main()
