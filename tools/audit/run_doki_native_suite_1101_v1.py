"""Run one bounded Mesen queue for the four Doki and four USA characters."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2]
O=R/'build/doki-final-native-1101-v1';J=R/'build/doki-current-component-1101-v1'
EXPECTED='f6415a64767b9ea1ada79ac5ccab433d7b1f4ae5f8bb13e53f04adeca717a3f1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    O.mkdir(exist_ok=True);assert sha(J/'candidate.nes')==EXPECTED
    rows={}
    for name,v in [('imajin',4),('lina',5),('papa',6),('mama',7),('mario',0),('luigi',1),('toad',2),('peach',3)]:
        output=O/name;assert not output.exists()
        command=[sys.executable,str(R/'tools/audit/prepare_doki_native_1101_v1.py'),'--joint',str(J),'--output',str(output),'--variant',str(v),'--expected',EXPECTED]
        subprocess.run(command,cwd=R,check=True);subprocess.run([sys.executable,str(output/'run.py')],cwd=R,check=True)
        q=json.loads((output/'capture/result.json').read_text());assert q['passed'] and q['ROM_sha256']==EXPECTED and q['variant']==v
        rows[name]={k:q[k]for k in ['variant','frames','Main','ISR_returns','source_movement','jumped','landed','maximum_camera','graphics_checks','APU_writes']}
        print(name+': '+json.dumps(rows[name]),flush=True)
    (O/'suite-results.json').write_text(json.dumps(dict(passed=True,candidate=EXPECTED,rows=rows,bindings={str(p.resolve()):sha(p)for p in[Path(__file__),R/'tools/audit/prepare_doki_native_1101_v1.py',R/'tools/reference/doki_native_bounded_1101_v1.lua']}),indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':main()
