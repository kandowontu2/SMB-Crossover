"""Bind missing owner row33 to the genuine native powerup animation update."""
import hashlib,json,subprocess
from pathlib import Path
import prepare_bub_collecting_upgrades_1102_v56 as P
import check_bub_original_upgrades_1102_v49 as Q
from check_tmnt_render_oa import address,location
from prepare_selected_native_packet_v1 import R,sha
O=R/'build/bub-upgrades-root-1102-v61';PIN=P.PIN

def main():
    O.mkdir(exist_ok=True);q=json.loads((P.O/'proposal.json').read_text())
    for f,h in q['bindings'].items():assert sha(R/f)==h,f
    previous=Q.U;Q.U=P
    try:_,b,_,_=Q.bundles()
    finally:Q.U=previous
    image=bytearray((P.O/'private-image.bin').read_bytes());start=q['labels']['BbPickupEnd']
    pc=address(b,'GuestPowerupUpdate');bank=((location(b,'GuestPowerupUpdate')-16)//8192)|128
    source=f'''.setcpu "6502"
.export BbNativePowerupUpdate,BbPowerupEnd
.segment "CODE"
BbNativePowerupUpdate:
 sta $016a
 lda #${pc&255:02x}
 sta $016c
 lda #${pc>>8:02x}
 sta $016d
 lda #${bank:02x}
 jsr $015a
 sec
 rts
BbPowerupEnd:
'''
    (O/'powerup.s').write_text(source);(O/'powerup.cfg').write_text(f'MEMORY{{M:start=${start:04x},size=${0xb53a-start:x},file=%O;}}SEGMENTS{{CODE:load=M,type=ro;}}')
    cc=R/'tools/Windows/cc65/bin'
    for command in [[cc/'ca65.exe',O/'powerup.s','-o',O/'powerup.o'],[cc/'ld65.exe','-C',O/'powerup.cfg',O/'powerup.o','-o',O/'powerup.bin','-Ln',O/'powerup.lbl']]:
        z=subprocess.run(list(map(str,command)),capture_output=True,text=True);assert z.returncode==0,z.stderr
    worker=(O/'powerup.bin').read_bytes();labels=P.labels(O/'powerup.lbl')
    assert image[start-0xa000:start-0xa000+len(worker)]==bytes([255])*len(worker)
    prior_row=image[99:102].hex();image[99:102]=bytes([76,start&255,start>>8]);image[start-0xa000:start-0xa000+len(worker)]=worker
    raw=bytearray(b['raw']);art=raw[1048592+441*1024:1048592+442*1024]
    cookie=bytes([0xa7,39,1])+hashlib.sha256(image+art).digest()[:13]
    for i,page in enumerate(q['pages']):raw[1048592+page*1024:1048592+(page+1)*1024]=image[i*1024:(i+1)*1024]
    raw[q['cookie_offset']:q['cookie_offset']+16]=cookie
    (O/'private-image.bin').write_bytes(image);all_labels={**q['labels'],**labels};(O/'labels.json').write_text(json.dumps(all_labels,indent=2)+'\n')
    out={**q,'expected_memory_only_ROM_SHA256':hashlib.sha256(raw).hexdigest(),'new_cookie':cookie.hex(),'labels':all_labels,'native_update_row':33,'native_update_bytes':len(worker),'native_update_PC':pc,'native_update_bank':bank,'prior_row33':prior_row,'remaining_source_gap':0xb53a-labels['BbPowerupEnd'],'scope':'Private body successor. Preserve original branch-relaxed component and native entry addresses. Pickup24 invokes native collector; previously unimplemented33 now invokes genuine GuestPowerupUpdate through actual bank gateway, then SEC. Resolves engine9 not advancing; transformation/ISR/emulator proof required. No ROM emission or install.','bindings':{str(f.relative_to(R)):sha(f) for f in [Path(__file__),P.O/'proposal.json',P.O/'private-image.bin',O/'powerup.s',O/'powerup.cfg',O/'powerup.bin',O/'private-image.bin',O/'labels.json']}}
    # Composition always rebases directly on current installed9cf, not v56.
    (O/'proposal.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k not in ['labels','bindings','relocated_source_ingresses']}))

if __name__=='__main__':main()
