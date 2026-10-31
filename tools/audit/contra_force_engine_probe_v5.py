"""Retain v4 evidence-export name collision; bind genuine tool lineage paths."""
from pathlib import Path
import hashlib,json
P=Path(__file__).with_name('contra_force_engine_probe_v4.py')
R=Path(__file__).resolve().parents[2]
negative=R/'build/contra-force-engine-probe-v4/preparation-negative.json'
assert not negative.exists()
negative.write_text(json.dumps(dict(passed=False,failure='v4 finally evidence-export mistook executed source P reproduction directory for outer wrapper P tool path; read_bytes on directory raised PermissionError after CPU checks, no controls receipt/source/native change.',tool=str(P),tool_sha256=hashlib.sha256(P.read_bytes()).hexdigest()),indent=2)+'\n',encoding='utf-8')
s=P.read_text().replace("build/contra-force-engine-probe-v4'", "build/contra-force-engine-probe-v5'")
s=s.replace('files={P,*[P.with_name(', 'files={*[Path(__file__).with_name(').replace('range(1,5)', 'range(1,6)')
exec(compile(s,str(P),'exec'),{'__name__':'__main__','__file__':str(Path(__file__).resolve())})
