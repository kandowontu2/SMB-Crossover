"""Reuse exact reviewed composition with a separately pinned Mini host fix."""
from pathlib import Path
import argparse,json,hashlib
R=Path(__file__).resolve().parents[2]

def main():
    a=argparse.ArgumentParser();a.add_argument('--host',required=True,type=Path);a.add_argument('--proof',required=True,type=Path);q=a.parse_args()
    host=q.host.resolve();proof=q.proof.resolve();b=host.with_suffix('.bin').read_bytes()
    pin=hashlib.sha256(b).hexdigest();p=json.loads(proof.read_text());assert p['passed']
    recipe=R/'tools/audit/compose_mini_nightly_root_1103_v27.py'
    text=recipe.read_text()
    replacements={"mini-mario-candidate-root-1103-v27":"mini-mario-candidate-root-1103-v28",
        "mini-host-v26.bin":host.with_suffix('.bin').name,
        'eee8d1b557728fff864a0fe7ab38e7655b1308fa272c27df19db07786b1a8bc3':pin}
    for old,new in replacements.items():
        assert text.count(old)==(2 if old=='mini-host-v26.bin'else 1)
        text=text.replace(old,new)
    old="'docs/qa/allocations/mini-mario-private-resources-1103-v24.json']"
    assert text.count(old)==1
    text=text.replace(old,"'docs/qa/allocations/mini-mario-private-resources-1103-v24.json',"+repr(proof.relative_to(R).as_posix())+"]")
    text=text.replace('for name in [*refs,','for name in [*refs,'+repr(recipe.relative_to(R).as_posix())+',')
    env=dict(__file__=__file__,__name__='mini_composer_v28')
    exec(compile(text,str(recipe),'exec'),env);env['main']()

if __name__=='__main__':main()
