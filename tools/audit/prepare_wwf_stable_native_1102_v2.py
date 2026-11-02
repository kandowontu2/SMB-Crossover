"""Compose the verified helper rewrite over the installed ROM for native testing."""
import json
import re
from pathlib import Path
import propose_wwf_generic_helper_1102_v1 as P
from prepare_selected_native_packet_v1 import prepare,sha

O=P.R/'build/wwf-helper-stable-1102-v2'

def main():
    q=json.loads((O/'proposal.json').read_text());checks=json.loads((O/'caller-load-CPU.json').read_text())
    assert checks['passed'] and checks['actual_IRQ_lagNMI_cuts']==190
    assert sha(P.BASE)==q['base_ROM_SHA256']
    raw=bytearray(P.BASE.read_bytes());begin=16+26*8192+0x800
    old=(O/'original.bin').read_bytes();new=(O/'proposed.bin').read_bytes()
    assert raw[begin:begin+len(old)]==old
    raw[begin:begin+len(new)]=new
    for row in checks['canonical_and_same_bank_routes']:
        at=row['offset'];a=row['old'];b=row['new']
        if row['type']=='farcall26':
            assert raw[at+1]==a&255 and raw[at+6]==a>>8
            raw[at+1]=b&255;raw[at+6]=b>>8
        else:
            assert raw[at:at+3]==bytes([32,a&255,a>>8])
            raw[at+1:at+3]=b.to_bytes(2,'little')
    rom=O/'candidate.nes';assert not rom.exists();rom.write_bytes(raw)
    # Reuse the already Mesen-qualified compact symbol schema, not a second
    # twelve-megabyte debug tree. Explicit current RAM labels serve controller.
    debug=P.R/'build/bub-menu-candidate-1102-v2/combined-visible.dbg'
    assert sha(debug)=='a54fadb57dbd7bb620a6b37a0ba8324cecc698c32a0dc5e0cde5855a347f41b4'
    rom.with_suffix('.dbg').write_bytes(debug.read_bytes())
    source=P.R/'build/hogan-gap-probe-1102-v4/native/controller.lua'
    controller=source.read_text();bundle=P.scoped_load(P.BASE)
    names=set(re.findall(r"\br\('([^']+)'\)",controller))|set(re.findall(r"L\['([^']+)'\]",controller))
    labels={name:P.address(bundle,name) for name in names}
    rom.with_suffix('.lbl').write_text(''.join(f'al {pc:06X} .{n}\n' for n,pc in sorted(labels.items())))
    controller='\n'.join(f'L[{json.dumps(n)}]={pc}' for n,pc in labels.items())+'\n'+controller
    prepare(O/'native-hogan',rom,controller,[Path(__file__),source,O/'proposal.json',O/'caller-load-CPU.json',O/'proposed.bin'],
        expected=sha(rom),timeout=240,allow_interactive=True,
        scope='Controller-only full1-1 Hogan route on native horizontal helper revision. Original no-life-loss and active1-2 assertions retained. No RAM writes. OnePNG; helper contact proof and other five wrestlers remain separate.')
    (O/'candidate.json').write_text(json.dumps(dict(private=True,installed=False,ROM_sha256=sha(rom),base_ROM_sha256=P.PIN,helper=q['helper']),indent=2)+'\n')

if __name__=='__main__':main()
