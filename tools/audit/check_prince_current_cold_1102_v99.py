"""Current-image constructor oracle binding, without changing the cold loader."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_current_cold_1102_v98 as V
O=V.O


def main():
 source=Path(V.__file__);text=source.read_text().replace('v98','v99');old='h=C.host(base);assert';assert old in text
 text=text.replace(old,"C.C.H.W.PIN=M.sha(base['raw']);h=C.host(base);assert")
 env=dict(__file__=str(Path(__file__)),__name__='prince_current_cold_v99');exec(compile(text,str(source),'exec'),env);env['main']()
 path=O/'current-shared-cold-CPU-v99.json';q=json.loads(path.read_text());q.update(constructor_oracle_bound_to_actual_memory_image=True,retained_fixture_binding_negative='current-shared-cold-negative-v98.json: oracle retained old16a9 PIN after actual Ex37/Prince38 full cold had returnedC1; no cold-loader code changed.')
 q['bindings'].update({p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),source,O/'current-shared-cold-negative-v98.json']});path.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':main()
