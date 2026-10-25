"""Current CI/CJ dense six-actor diagnostic, not an ordinary playthrough."""
from pathlib import Path
import collections,hashlib,json,statistics
R=Path(__file__).resolve().parents[2];V=R/'build/verification';O=V/'water-current-dense-ct'
P=V/'agent49-water-visible-j-a/adverse_p.py'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    text=P.read_text()
    replacements={"root=H/'adverse-p'":"root=O",
        "g.guard('adverse-p-'+folder.name,2000000)":"dict(global_cap=100000000000,phase_reservation=25000000,retention='all captures and negatives retained')",
        "H/'source-h/build'if candidate else V/'root49-water-enemy-filter-gy/source/build'":"R/'build'if candidate else R/'build/checkpoints/firebar-budget-ci/build'"}
    for a,b in replacements.items():assert text.count(a)==1,a;text=text.replace(a,b)
    assert not O.exists()
    exec(compile(text,str(P),'exec'),dict(__file__=str(P),__name__='water_ct_dense',O=O))
    (O/'adapted-review.py.txt').write_text(text,encoding='utf-8')
    groups=[]
    for mapper in('mmc3','mmc5'):
        for rev in('J','H'):
            folder=O/f'{mapper}-{rev}';path=folder/'native/ordinary-profile.jsonl'
            rows=[json.loads(z)for z in path.read_text().splitlines()]
            bins=collections.defaultdict(list)
            for z in rows:bins[z['name']].append(z)
            scopes={name:dict(samples=len(v),mean=statistics.mean(z['exclusive_cycles']for z in v),maximum=max(z['exclusive_cycles']for z in v),
                native_elapsed_max=max(z['cycles']for z in v),lag_increments=sum(z['lag']for z in v),physical_frame_spills=sum(z['frame_delta']for z in v),
                attained_IRQ=sum(z['irq']for z in v),attained_NMI=sum(z['nmi']for z in v))for name,v in bins.items()}
            groups.append(dict(mapper=mapper,revision='CI'if rev=='J'else'CJ',raw_sha256=sha(path),scopes=scopes))
    (O/'summary.json').write_text(json.dumps(dict(passed=True,groups=groups,original_script_sha256=sha(P),adapted_script_sha256=hashlib.sha256(text.encode()).hexdigest(),
        scope='All6 live enemies and8 source-spaced shield balls are authored before each pass. Native full GameLoop timings subtract actual attained IRQ/NMI. This measures an adverse component and is not natural acquisition or an ordinary route.',goal_complete=False),indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':main()
