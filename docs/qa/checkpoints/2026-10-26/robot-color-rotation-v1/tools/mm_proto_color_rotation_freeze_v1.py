"""Bind the finite one-byte source repair without copying another full bundle."""
from pathlib import Path
import argparse
import ast
import hashlib
import json

R = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
C = D / 'robot-color-rotation-candidate-v3'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
put = lambda p, z: Path(p).write_text(json.dumps(z, indent=2) + '\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    assert not a.output.resolve().is_relative_to(R)
    a.output.mkdir(parents=True, exist_ok=False)
    proofs = [C / f for f in ['proof.json', 'cpu-v3/proof.json',
              'caller-v6/proof.json', 'build-controls-v1/proof.json']]
    for f in proofs:
        assert json.loads(f.read_text())['passed']
    source = json.loads((C / 'source-manifest.json').read_text())
    bindings = {}
    for rel, h in source.items():
        f = C / 'source' / rel
        assert sha(f) == h
        bindings[str(f.resolve())] = h
    catalog = {}
    for f in C.rglob('*'):
        if f.is_file() and not f.is_relative_to(C / 'source'):
            catalog[str(f.resolve())] = sha(f)
    for name in ['robot-color-rotation-candidate-v1', 'robot-color-rotation-candidate-v2']:
        for f in (D / name).glob('*.json'):
            catalog[str(f.resolve())] = sha(f)
        f = D / name / 'failed-tool.py'
        assert f.is_file()
        catalog[str(f.resolve())] = sha(f)
    tools = sorted((R / 'tools/audit').glob('mm_proto_color_rotation_*.py'))
    report = R / 'docs/qa/mm-proto-color-rotation-2026-10-26.txt'
    for f in [*tools, report]:
        catalog[str(f.resolve())] = sha(f)
    dependencies, pending = {}, tools[:]
    while pending:
        f = pending.pop()
        if str(f.resolve()) in dependencies:
            continue
        dependencies[str(f.resolve())] = sha(f)
        for node in ast.walk(ast.parse(f.read_text())):
            names = [node.module] if isinstance(node, ast.ImportFrom) else [x.name for x in node.names] if isinstance(node, ast.Import) else []
            for name in names:
                if name:
                    dep = R / 'tools/audit' / (name.split('.')[0] + '.py')
                    if dep.is_file():
                        pending.append(dep)
    for f in [D / 'robot-balancer-budget-review-v1/proof.json',
              D / 'robot-balancer-budget-review-v1/actual993-evidence.json']:
        dependencies[str(f.resolve())] = sha(f)
    bindings.update(catalog)
    bindings.update(dependencies)
    put(a.output / 'catalog.json', dict(sorted(catalog.items())))
    put(a.output / 'bindings.json', dict(sorted(bindings.items())))
    put(a.output / 'review-files.json', dict(
        owned_files=[dict(path=f.relative_to(R).as_posix(), sha256=sha(f)) for f in [*tools, report]],
        final_tools=['mm_proto_color_rotation_candidate_v3.py', 'mm_proto_color_rotation_cpu_v3.py',
                     'mm_proto_color_rotation_caller_v6.py', 'mm_proto_color_rotation_freeze_v1.py'],
        other_versions='Retained qualification negatives/prose predecessors; never mutate or relabel.',
        external_only='ROM/debug/map/source snapshot and all failed proofs stay external. No production/Git/native mutation.'))
    put(a.output / 'proof.json', dict(source_qualified=True, native_run=False, native_granted=False,
        candidate_ROM_sha256=sha(C / 'candidate.nes'), source_manifest_sha256=sha(C / 'source-manifest.json'),
        source_files=len(source), exact_ROM_delta_bytes=1, physical_bank=126, CPU_operand='86EA',
        passed_proofs={str(f): sha(f) for f in proofs}, bindings=len(bindings),
        bindings_sha256=sha(a.output / 'bindings.json'), catalog_sha256=sha(a.output / 'catalog.json'),
        review_files_sha256=sha(a.output / 'review-files.json'), tool_sha256=sha(__file__),
        no_source_or_native_claim_for_separate_ce635_composition=True,
        limits='Finite source and modeledNMI qualification only. Earlier nativeFALSEs immutable; busy-animation deferral/Y-V liveness explicit. No standalone native preparation or launch.'))
    print(json.dumps(dict(proof=str(a.output / 'proof.json'), sha256=sha(a.output / 'proof.json'), bindings=len(bindings)), indent=2))


if __name__ == '__main__':
    main()
