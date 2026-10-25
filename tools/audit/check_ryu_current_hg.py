"""Review HF captures against GO, including the independently sourced climb fix."""
from pathlib import Path
import contextlib,hashlib,io,json
R=Path(__file__).resolve().parents[2];V=R/'build/verification';N=V/'ryu-native-hf';O=V/'ryu-review-hg'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not O.exists();O.mkdir()
source=R/'reference/crossover2/extracted/scripts/com/smbc/characters/Ryu.as'
assert 'override public function groundOnSide' in source.read_text()
code=(N/'check-bound.py.txt').read_text()
old="if kind!='interior':assert not semantic";assert code.count(old)==1
code=code.replace(old,"if kind not in('interior','climb'):assert not semantic")
old="(A/'strict-native-f.json').write_text";assert code.count(old)==3
code=code.replace(old,"(ROOT_REVIEW/'strict-native-hg.json').write_text")
(O/'check-bound.py.txt').write_text(code)
stream=io.StringIO()
try:
    with contextlib.redirect_stdout(stream):exec(compile(code,str(N/'check-bound.py.txt'),'exec'),{'__name__':'__main__','__file__':str(N/'check-bound.py.txt'),'ROOT_OUTPUT':N,'ROOT_PARENT':R/'build/checkpoints/weapons-source-go','ROOT_CANDIDATE':V/'ryu-current-hd/source','ROOT_REVIEW':O})
finally:(O/'host.log').write_text(stream.getvalue())
result=json.loads((O/'strict-native-hg.json').read_text());assert result['status'].startswith('PASS_')
summary=dict(passed=True,captured_native_groups=2,captured_native_cases=124,actual_compiled_calls=sum(z['actual_native_reexecution_calls']for z in result['groups']),actual_interrupt_gaps=sum(len(z['gaps'])for z in result['groups']),retained_prior_negative_sha256=sha(N/'strict-native-f.json'),source_Ryu_sha256=sha(source),bound_verifier_sha256=sha(O/'check-bound.py.txt'),scope='Source Ryu.groundOnSide rejects native correction while climbing; current GO lacks that earlier B fix. Both climb and prior-interior cases therefore permit only the same explicitly listed native side-response fields. All other RAM/register checks remain intact. Actual in-call IRQs are reported gaps, not masked.',goal_complete=False)
(O/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(summary,flush=True)
