"""Remove redundant nested JSR depth from owning native callbacks."""
import hashlib,json,subprocess
from pathlib import Path
import prepare_bub_powerup_update_1102_v61 as P
from prepare_selected_native_packet_v1 import R,sha
O=R/'build/bub-upgrades-root-1102-v65';PIN=P.PIN

def main():
    O.mkdir(exist_ok=True);q=json.loads((P.O/'proposal.json').read_text())
    for f,h in q['bindings'].items():assert sha(R/f)==h,f
    image=bytearray((P.O/'private-image.bin').read_bytes());cc=R/'tools/Windows/cc65/bin';labelmap=q['labels']
    inputs=[('pickup',R/'build/bub-upgrades-root-1102-v56',labelmap['BbNativePickup']),('powerup',P.O,labelmap['BbNativePowerupUpdate'])]
    for stem,parent,start in inputs:
        old=(parent/(stem+'.s')).read_text();fragment=' jsr $015a\n sec\n rts\n';assert old.count(fragment)==1
        source=old.replace(fragment,' jmp $015a ; Tail native FarCallCommon: no redundant callback return frame.\n .byte $ea,$ea ; Keep all following data/entries at their exact addresses.\n')
        (O/(stem+'.s')).write_text(source);(O/(stem+'.cfg')).write_text(f'MEMORY{{M:start=${start:04x},size=${0xb53a-start:x},file=%O;}}SEGMENTS{{CODE:load=M,type=ro;}}')
        for command in [[cc/'ca65.exe',O/(stem+'.s'),'-o',O/(stem+'.o')],[cc/'ld65.exe','-C',O/(stem+'.cfg'),O/(stem+'.o'),'-o',O/(stem+'.bin'),'-Ln',O/(stem+'.lbl')]]:
            z=subprocess.run(list(map(str,command)),capture_output=True,text=True);assert z.returncode==0,z.stderr
        part=(O/(stem+'.bin')).read_bytes();before=(parent/(stem+'.bin')).read_bytes();assert len(part)==len(before)
        assert image[start-0xa000:start-0xa000+len(before)]==before
        lab=P.P.labels(O/(stem+'.lbl'));assert all(labelmap[k]==v for k,v in lab.items()),'No entry or mask relocation'
        image[start-0xa000:start-0xa000+len(part)]=part
    base=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes');raw=bytearray(base.read_bytes());assert sha(base)==PIN
    art=raw[1048592+441*1024:1048592+442*1024];cookie=bytes([0xa7,39,1])+hashlib.sha256(image+art).digest()[:13]
    for i,page in enumerate(q['pages']):raw[1048592+page*1024:1048592+(page+1)*1024]=image[i*1024:(i+1)*1024]
    raw[q['cookie_offset']:q['cookie_offset']+16]=cookie
    (O/'private-image.bin').write_bytes(image);(O/'labels.json').write_text(json.dumps(labelmap,indent=2)+'\n')
    out={**q,'expected_memory_only_ROM_SHA256':hashlib.sha256(raw).hexdigest(),'new_cookie':cookie.hex(),'scope':'Private successor retains callback24/33 addresses and masks, replaces redundant JSR FarCallCommon/SEC/RTS with native tail JMP plus2 unreachable NOPs. Native collector/update owns return AXYP/C, as ordinary native callbacks do; immature pickup still claimsSEC untouched. Removes2 live stack bytes at every native gateway. v64 proved actual nestedIRQ in lag audio overwrote SMC at old minSP120. Full latest ISR/lifecycle qualification required. No native image emitted.','bindings':{str(f.relative_to(R)):sha(f) for f in [Path(__file__),P.O/'proposal.json',P.O/'private-image.bin',O/'pickup.s',O/'pickup.bin',O/'powerup.s',O/'powerup.bin',O/'private-image.bin',O/'labels.json']}}
    (O/'proposal.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k not in ['labels','bindings','relocated_source_ingresses']}))

if __name__=='__main__':main()
