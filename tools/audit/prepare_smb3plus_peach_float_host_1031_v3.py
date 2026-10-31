"""Correct the v2 preparation hook's first, unchanged-source write phase."""
from pathlib import Path
import json

R=Path(__file__).resolve().parents[2]


def main():
    prior=R/'tools/audit/prepare_smb3plus_peach_float_host_1031_v2.py'
    text=prior.read_text()
    assert text.count('    assert not source2.exists()')==1
    text=text.replace('    assert not source2.exists()','')
    old="    source2.write_text(code,encoding='utf-8',newline='\\n')"
    assert text.count(old)==1
    text=text.replace(old,"    if source2.exists():assert source2.read_text()==code\n    else:source2.write_text(code,encoding='utf-8',newline='\\n')")
    text=text.replace("P.O=R/'build/smb3plus-peach-float-host-1031-v2'","P.O=R/'build/smb3plus-peach-float-host-1031-v3'")
    old="        if path==P.J/'src/smb3_mario_art.inc':"
    assert text.count(old)==1
    text=text.replace(old,old[:-1]+" and 'MbFloatForm5ChrLo' in text:")
    ns={'__file__':str(Path(__file__).resolve()),'__name__':'private_peach_float_v3'}
    exec(compile(text,str(prior),'exec'),ns)
    ns['main']()
    P=ns['P'];p=P.O/'source-stage.json';d=json.loads(p.read_text())
    d['bindings'][str(prior)]=P.B.sha(prior)
    d['retained_preparation_negative']='v2 preparation hook asserted the form5 relocation during the initial unchanged-source copy; no v2 compilation or ROM was produced.'
    p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8',newline='\n')


if __name__=='__main__':main()
