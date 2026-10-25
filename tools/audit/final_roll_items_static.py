"""Parse frozen Roll Lua and check numeric mode/finite plan. No native run."""
from pathlib import Path
import argparse,hashlib,json,re,sys

sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--packet',type=Path,required=True)
    p.add_argument('--parser-root',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();sys.path.insert(0,str(a.parser_root))
    from luaparser import ast
    z=json.loads((a.packet/'preparation.json').read_text(encoding='utf-8'));rows=[]
    for q in z['profiles']:
        path=Path(q['script']);text=path.read_text(encoding='utf-8')
        assert sha(path)==q['script_sha256'];ast.parse(text)
        assert not re.search(r'(?<![A-Za-z0-9_])(True|False)(?![A-Za-z0-9_])',text)
        c=json.loads((path.parent/'config.json').read_text(encoding='utf-8'))
        assert type(c['hard'])is bool and c['mode_value']==int(c['hard'])==q['mode_value']
        assert not set(re.findall(r'\bL\.([A-Za-z_][A-Za-z_0-9]*)',text))-set(c['ram'])
        assert len(c['plan'])==36
        assert sum(p.get('contacts',0)for p in c['plan'])==15
        assert sum(p.get('count',0)for p in c['plan']if p['action']=='charge')==25
        assert sum(p['action']=='capsule'for p in c['plan'])==13
        assert '["hard"]='+('true'if c['hard']else'false')in text.splitlines()[1]
        assert '["mode_value"]='+str(c['mode_value'])in text.splitlines()[1]
        rows.append(dict(mode=q['mode'],numeric_mode=c['mode_value'],script_sha256=sha(path),parsed=True,literal_and_plan_assertions=True,native_passed=False))
    a.output.mkdir(parents=True,exist_ok=False)
    result=dict(passed=True,native_passed=False,goal_complete=False,ROM_sha256=z['ROM_sha256'],preparation_sha256=sha(a.packet/'preparation.json'),script_sha256=sha(Path(__file__)),parser_ast_sha256=sha(Path(ast.__file__)),profiles=rows,scope=__doc__)
    (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(native_passed=False,profiles=2,proof_sha256=sha(a.output/'proof.json'))))


if __name__=='__main__':main()
