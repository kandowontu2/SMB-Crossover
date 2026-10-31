"""Defer the exact status span check until its imported farcall is linked."""
from pathlib import Path
import json

R=Path(__file__).resolve().parents[2]


def main():
    prior=R/'tools/audit/prepare_smb3plus_menu_host_1031_v1.py'
    text=prior.read_text()
    old="f'.assert *-M3StatusNameDispatch<={old_size},error,\"Existing status span\"\\n.res {old_size}-(*-M3StatusNameDispatch),$ea\\n'"
    assert text.count(old)==1
    text=text.replace(old,"f'.assert *-M3StatusNameDispatch={old_size},lderror,\"Existing status span\"\\n'")
    text=text.replace("O=R/'build/smb3plus-menu-host-1031-v1'","O=R/'build/smb3plus-menu-host-1031-v2'")
    namespace={'__file__':str(Path(__file__).resolve()),'__name__':'private_smb3_menu_v2'}
    exec(compile(text,str(prior),'exec'),namespace);namespace['main']()
    P=namespace['P'];p=namespace['O']/'source-stage.json';d=json.loads(p.read_text())
    negative=R/'build/smb3plus-menu-host-1031-v1/main-build.json'
    d['bindings'].update({str(x):P.B.sha(x) for x in [prior,negative]})
    d['retained_preparation_negative']='The v1 RES expression includes an imported farcall with relocatable bank. V2 uses an exact final-link82-byte assertion; no padding or size bound is relaxed.'
    P.B.write(p,json.dumps(d,indent=2)+'\n')


if __name__=='__main__':main()
