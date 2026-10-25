"""Rebind the reviewed full-caller and geometry oracles to the current ROMs."""
from pathlib import Path
import argparse, functools, hashlib, importlib.util, json

R=Path(__file__).resolve().parents[2];V=R/'build/verification'
P=V/'agent49-water-visible-j-a'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def main():
    parser=argparse.ArgumentParser();parser.add_argument('kind',choices=['caller','geometry']);kind=parser.parse_args().kind
    out=V/('water-current-caller-cn'if kind=='caller'else'water-current-geometry-co')
    assert not out.exists();out.mkdir()
    source=P/('review_m.py'if kind=='caller'else'compiled_i.py')
    text=source.read_text()
    if kind=='caller':
        replacements={
            "rom=H/'source-h/build'/f'smb-crossover-{mapper}.nes'":"rom=R/'build'/f'smb-crossover-{mapper}.nes'",
            "old=m.q.Image(V/'root49-water-enemy-filter-gy/source/build'/f'smb-crossover-{mapper}.nes')":"old=m.q.Image(R/'build/checkpoints/firebar-budget-ci/build'/f'smb-crossover-{mapper}.nes')",
            "folder=H/'live-k'/f'{mapper}-{char}'":"folder=V/'water-visible-profile-cm'/f'CJ-{mapper}-{char}'",
            "'PASS_NATIVE_FULL_SPECIALWEAPONS_AND_SAME_INPUT_J_DIFFERENTIAL'":"'PASS_CURRENT_NATIVE_FULL_SPECIALWEAPONS_AND_SAME_INPUT_CI_DIFFERENTIAL'"}
        for a,b in replacements.items():assert text.count(a)==1,a;text=text.replace(a,b)
        # Import paths stay anchored to the reviewed module; only its output
        # directory and ROM/evidence bindings change. No oracle is weakened.
        namespace={'__file__':str(source),'__name__':'water_cn_rebound'}
        exec(compile(text,str(source), 'exec'),namespace);namespace['H']=out
    else:
        a="b['banks'][0xa000]==5";assert text.count(a)==1;text=text.replace(a,"b['banks'][0xa000]==36")
        a="((8,5)if mapper=='mmc3'else(136,133))";assert text.count(a)==1;text=text.replace(a,"((8,36)if mapper=='mmc3'else(136,164))")
        namespace={'__file__':str(source),'__name__':'water_co_rebound'}
        exec(compile(text,str(source),'exec'),namespace);namespace['H']=out
        probe=namespace['p']
        @functools.lru_cache(None)
        def context(mapper):
            images=[probe.m.q.Image(R/'build/checkpoints/firebar-budget-ci/build'/f'smb-crossover-{mapper}.nes'),
                probe.m.q.Image(R/'build'/f'smb-crossover-{mapper}.nes')]
            folder=V/'water-visible-profile-cm'/f'CI-{mapper}-1'/'native'
            rows=[json.loads(z)for z in(folder/'caller.jsonl').read_text().splitlines()]
            entry=next(z for z in rows if z['event']=='entry')
            initial=probe.m.snapshot((folder/'caller-ram.bin').read_bytes(),entry)
            assert len(initial)==10240
            return images,initial
        probe.context=context
        replacements={'active_A_bank':dict(old=8,current=36),'geometry_coverage':'Unchanged42760-case oracle per mapper',
            'context':'CI/current ROMs, actual CI full-caller initial RAM from CM'}
    (out/'adapted-review.py.txt').write_text(text,encoding='utf-8')
    (out/'binding.json').write_text(json.dumps(dict(kind=kind,original_source=str(source),original_sha256=sha(source),
        adapted_sha256=hashlib.sha256(text.encode()).hexdigest(),changes=replacements,
        ROMs={m:sha(R/'build'/f'smb-crossover-{m}.nes')for m in('mmc3','mmc5')},script_sha256=sha(__file__)),indent=2)+'\n',encoding='utf-8')
    namespace['main']()

if __name__=='__main__':main()
