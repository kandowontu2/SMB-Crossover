"""Unchanged native Shinobi/Excitebike policies on the private auth candidate."""
from pathlib import Path
import json
import re
from prepare_selected_native_packet_v1 import R,prepare,sha
import build_storage_guard_v1 as G

O=R/'build/combined-foreign-native-root-1103-v119'
ROM=R/'build/combined-owner-auth-root-1103-v116/combined-auth-private.nes'
PIN='80d3ae95894f5ddb430c3e753dd95f3fc2eca6a87d8e1afdb4b8ce8376ec795a'


def symbols(path):
    return {m[2]:int(m[1],16) for line in path.read_text().splitlines()
            if (m:=re.fullmatch(r'al ([0-9A-Fa-f]+) \.([\w]+)',line))}


def main():
    G.preflight(private_root=O,reserved_bytes=100000,reserved_files=7,fresh=True)
    assert sha(ROM)==PIN
    grant=R/'docs/qa/allocations/combined-owner-auth-1103-v116.json'
    assert json.loads(grant.read_text())['expected_candidate_SHA256']==PIN
    O.mkdir(exist_ok=False); current=symbols(ROM.with_suffix('.lbl')); rows=[]
    for name,old_packet in [('shinobi','shinobi-smoke'),('excitebike','native4')]:
        root=R/'build/excitebike-pose-1101-v3'/old_packet
        ready=json.loads((root/'ready.json').read_text())
        result=json.loads((root/'capture/result.json').read_text())
        assert result['passed']
        ref_rom=Path(ready['ROM']);labels=ref_rom.with_suffix('.lbl');old=symbols(labels)
        text=(root/'controller.lua').read_text()
        assert not re.search(r'\bemu\.(write|loadSavestate|saveSavestate|reset)\s*\(',text)
        needed=set(re.findall(r'\br\([\"\x27]([A-Za-z_0-9]+)',text))
        needed.update(re.findall(r'\bL\.([A-Za-z_0-9]+)',text))
        if name=='shinobi':
            needed.update(['CurrentCHRBank','X5ChrMode','SsChrActive','X5WideChrActive',
                'ReloadCHRBank','CurrentOAMOffset','Mirror_PPUCTRL','RgOamFirst','RgOamUsed','RgOamRotation'])
        for n in needed:
            assert n in old and old[n]<0x8000,n
            assert n not in current or current[n]==old[n],n
        prefix='-- Explicit native RAM labels; unchanged gameplay policy below.\n'
        prefix+='\n'.join('L['+json.dumps(n)+']='+str(old[n]) for n in sorted(needed))+'\n'
        prepare(O/name,ROM,prefix+text,[Path(__file__),grant,root/'controller.lua',root/'ready.json',
            root/'capture/result.json',labels],expected=PIN,timeout=180,allow_interactive=True,
            scope='Exact80d3 private complete-auth foreign-owner regression. Existing passing controller policy/assertions unchanged; explicit original native RAM labels checked against current available symbols. '+
                ('Shinobi cold Select/Start/entry/walk/OAM alignment smoke only; no fullstage claim.' if name=='shinobi' else
                 'Excitebike cold/idle/throttle/coast/reverse/source leanjump/landing/CHR/palette/HUD/OAM checks. No fullstage claim.')+
                ' No emulated writes, new helpers or installation. Root owns single Mesen queue.')
        rows.append(dict(name=name,source_controller=str(root/'controller.lua'),
                         source_controller_SHA256=sha(root/'controller.lua'),symbols=len(needed)))
    (O/'prepared.json').write_text(json.dumps(dict(prepared=True,native=False,ROM_SHA256=PIN,rows=rows),indent=2)+'\n')
    print(json.dumps(dict(prepared=True,rows=rows)))


if __name__=='__main__':main()
