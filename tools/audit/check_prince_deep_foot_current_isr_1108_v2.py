"""Current relocated Prince landing: same actual IRQ/lag-NMI cut harness."""
from pathlib import Path
import inspect,json,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
import rebase_prince_deep_foot_1108_v1 as Q
P=Q.P


def main():
    text=inspect.getsource(P.main)
    a=text.index("    receipt=O/'deep-branch-measurement.json'")
    z=text.index('    _,m,lab=A.first8(new)',a)
    text=text[:a]+'''    receipt=O/'landing-contract.json';q=json.loads(receipt.read_text())
    base,new,changes,_=CURRENT.image()
    assert changes==q['patches'] and hashlib.sha256(new['raw']).hexdigest()==q['body_frontend_and_landing_memory_SHA256']
'''+text[z:]
    old="    fr=foreign(base,new,m);print(fr,flush=True)"
    assert text.count(old)==1;text=text.replace(old,"    fr=q['comparison'];assert fr['foreign_cases']==61422")
    text=text.replace('parent_SHA256=B.SHA','parent_SHA256=CURRENT.PIN').replace("q['combined_memory_SHA256']","q['body_frontend_and_landing_memory_SHA256']")
    text=text.replace("'deep-branch-ABI-ISR.json'","'landing-current-ISR.json'")
    env=dict(P.__dict__,CURRENT=Q,O=Q.O,__file__=str(Path(__file__)))
    exec(compile(text,str(Path(__file__)),'exec'),env);env['main']()


if __name__=='__main__':main()
