"""Keep Sunny's valid growth palette cache across repeated color callbacks."""
import json,subprocess,shutil
from pathlib import Path
import audit_current_menu_indicators_1102_v1 as A
from check_tmnt_render_oa import address,location
from prepare_selected_native_packet_v1 import sha,R
O=R/'build/sunny-palette-dedup-1102-v5'
ROM=R/'build/menu-family-root-candidate-1102-v1/mr-gimmick-family.nes'

def main():
    O.mkdir(exist_ok=True);b=A.bundle();raw=bytearray(ROM.read_bytes());b['raw']=bytes(raw)
    assert sha(ROM)=='22d09909bf952ef007d1582589dc869073262784bf38b92d2c7b206ce3c45b19'
    entry=address(b,'SunnyColorsIntegrated');tail=address(b,'SunnyIntegrationPalette')+int(b['syms']['SunnyIntegrationPalette']['size'],0)
    assert tail==0xb6d8 and tail+32<=0xb700
    at=location(b,'SunnyColorsIntegrated');end=location(b,'SunnyIntegrationPalette')+int(b['syms']['SunnyIntegrationPalette']['size'],0)
    old=bytes(raw[at:at+5]);assert old==bytes([0xa9,255,0x8d,address(b,'SunnyPalette')&255,address(b,'SunnyPalette')>>8])
    assert bytes(raw[end:end+32])==bytes([255])*32
    source='''.setcpu "6502"
.segment "CODE"
 php
 lda $%04x
 cmp #9
 beq Cached
 plp
 lda #$ff
 sta $%04x
 jmp $%04x
Cached:
 plp
 jmp $%04x
'''%(address(b,'GameEngineSubroutine'),address(b,'SunnyPalette'),entry+5,entry+5)
    (O/'worker.s').write_text(source);(O/'worker.cfg').write_text('MEMORY{ROM:start=$%04x,size=$28,file=%%O;}SEGMENTS{CODE:load=ROM,type=ro;}'%tail)
    cc=R/'tools/Windows/cc65/bin'
    for cmd in [[cc/'ca65.exe',O/'worker.s','-o',O/'worker.o'],[cc/'ld65.exe','-C',O/'worker.cfg','-o',O/'worker.bin',O/'worker.o']]:
        q=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert q.returncode==0,q.stderr
    worker=(O/'worker.bin').read_bytes();assert len(worker)<=32
    patches=[dict(offset=at,old=old.hex(),new=bytes([0x4c,tail&255,tail>>8,0xea,0xea]).hex()),dict(offset=end,old=bytes(raw[end:end+len(worker)]).hex(),new=worker.hex())]
    for p in patches:raw[p['offset']:p['offset']+len(bytes.fromhex(p['new']))]=bytes.fromhex(p['new'])
    candidate=O/'candidate.nes';candidate.write_bytes(raw)
    for ext in ['.dbg','.lbl']:shutil.copyfile(ROM.with_suffix(ext),candidate.with_suffix(ext))
    q=dict(private=True,installed=False,base_ROM_SHA256=sha(ROM),candidate_ROM_SHA256=sha(candidate),patches=patches,worker_PC=tail,worker_bytes=len(worker),scope='During Sunny engine9 transform, retain valid SunnyPalette cache. SunnyIntegrationPalette still compares current visual form and retries declined appends. Other engines retain forced invalidation; star guard and all other identities unchanged. Native negative and CPU/native qualification required.',bindings={str(p):sha(p)for p in [Path(__file__),O/'worker.s',O/'worker.bin']})
    (O/'candidate.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))
if __name__=='__main__':main()
