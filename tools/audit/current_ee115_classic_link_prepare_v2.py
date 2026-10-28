"""Link-only legal mature-flower height correction, original source FALSE retained."""
from pathlib import Path
import inspect,json,sys
from types import SimpleNamespace
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
import current_ee115_classic_tiers_prepare_v1 as old


def main():
    negative=R/'build/current-ee115-classic-tiers-v1/link-source-negative.json'
    assert json.loads(negative.read_text())['error']=="AssertionError(('link', 1, 0))"
    ns=dict(old.__dict__)
    ns.update(__file__=__file__,IDS=('link',),FIXTURE=R/'tests/current-ee115-classic-link-v2.lua',OUT=R/'build/current-ee115-classic-link-v2')
    # A stationary flower placed at Y168 is above Easy Link's actual collision
    # band. Existing item profiles use Y184; unlike Star/Mushroom it will not
    # fall into the band. Correct only this staged actor, never player/outcomes.
    source=inspect.getsource(old.fixture)
    anchor="prefix=prefix.replace('CURRENT_SHARED_STAR_LIFE','CURRENT_CLASSIC_TIERS').replace(\"OUTPUT..'star-life.csv'\",\"OUTPUT..'classic-tiers.csv'\")"
    assert source.count(anchor)==1
    source=source.replace(anchor,anchor+"\n    assert prefix.count(\"local y=r('Player_Y_Position')-8\")==1\n    prefix=prefix.replace(\"local y=r('Player_Y_Position')-8\",\"local y=r('Player_Y_Position')+8\")")
    exec(compile(source,__file__,'exec'),ns)
    original_namespace=old.shared.namespace
    def namespace():
        m,cfgs=original_namespace();actor=m['actor']
        def place(q,kind,slot,pickup,character):
            actor(q,kind,slot,pickup,character)
            assert character==4 and kind==46 and pickup in [0,1]
            q.set('Enemy_Y_Position',q.get('Player_Y_Position')+8,slot)
        m['actor']=place;return m,cfgs
    # Isolated globals for this preparation, no mutation of old tool/module.
    ns['shared']=SimpleNamespace(namespace=namespace,EXPECTED=old.shared.EXPECTED,MATRIX=old.shared.MATRIX,__file__=old.shared.__file__)
    exec(compile(inspect.getsource(old.main),__file__,'exec'),ns)
    ns['main']()
    out=ns['OUT'];ready=out/'link/prepared-not-run.json';z=json.loads(ready.read_text())
    paths={Path(x['path'])for x in z['bindings']}|{Path(old.__file__),negative}
    z.update(original_source_negative=dict(path=str(negative),sha256=old.sha(negative)),
             correction='Only staged mature pickup Y176+8=184; stationary flower at oldY168 never enters actual Easy Link contact band. All growth, inventory, primary, hardware/cap predicates unchanged.',
             source_setup_scope='Corrected legal staged mature actor height; no natural reveal/rise claim.')
    z['bindings']=[dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=old.sha(p))for p in sorted(paths)]
    old.put(ready,z)
    batch=out/'prepared-batch.json';v=json.loads(batch.read_text());v['readies'][0]['sha256']=old.sha(ready);old.put(batch,v)
    print(json.dumps(dict(ready=str(ready),sha256=old.sha(ready),batch_sha256=old.sha(batch),native_run=False)))


if __name__=='__main__':main()
