"""Retain119 missing-symbol negative; bind both bracket-form RAM references."""
import json
import re
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare,sha
import prepare_combined_foreign_native_root_1103_v119 as P
import build_storage_guard_v1 as G

O=R/'build/combined-ex-labels-root-1103-v120'


def main():
    G.preflight(private_root=O,reserved_bytes=50000,reserved_files=4,fresh=True)
    old=P.O/'excitebike'; ready=json.loads((old/'ready.json').read_text())
    for p,h in ready['bindings'].items():assert sha(p)==h,p
    result=json.loads((old/'capture/result.json').read_text())
    diag=json.loads((old/'capture/diagnosis.json').read_text())
    assert not result['passed'] and result['reason']=='completed'
    assert diag['hardware_checks']==diag['hardware_failures'] and diag['first_hardware_failure']['banks']
    labels=R/'build/excitebike-pose-1101-v3/current3.lbl'
    symbols=P.symbols(labels); text=(old/'controller.lua').read_text()
    needed=set(re.findall(r'\bL\[[\"\x27]([A-Za-z_0-9]+)[\"\x27]\]',text))
    needed-=set(re.findall(r'\bL\[[\"\x27]([A-Za-z_0-9]+)[\"\x27]\]=\d+',text))
    assert needed=={'ObjectMetasprite','SmPosePtr'}
    current=P.symbols(P.ROM.with_suffix('.lbl'))
    for n in needed:
        assert n not in current and 0<=symbols[n]<0x8000
        assert ('L['+json.dumps(n)+']=') not in text
    prefix='-- Complete bracket-form native RAM symbols omitted by119 extractor.\n'
    prefix+='\n'.join('L['+json.dumps(n)+']='+str(symbols[n]) for n in sorted(needed))+'\n'
    O.mkdir(exist_ok=True)
    prepare(O/'excitebike',P.ROM,prefix+text,[Path(__file__),Path(P.__file__),labels,old/'controller.lua',old/'ready.json',
        old/'capture/result.json',old/'capture/diagnosis.json'],expected=P.PIN,timeout=180,allow_interactive=True,
        scope='Same exact80d3 and119 gameplay inputs/assertions. Complete ObjectMetasprite06E1/SmPosePtr6B06 labels used by existing OAM check.119 omitted bracket-form references and current tiny native symbols omit both, causing false aligned=false; its original negative stays immutable. No ROM/code/physics/observer assertion changes. Original native cold/idle/throttle/coast/reverse/61px leanjump/landing/CHR/palette/HUD/OAM check, no fullstage/install claim.')
    (O/'preparation.json').write_text(json.dumps(dict(prepared=True,native=False,
        ROM_SHA256=P.PIN,missing_symbols={n:symbols[n] for n in needed},
        old_negative_preserved=True,assertions_unchanged=True),indent=2)+'\n')


if __name__=='__main__':main()
