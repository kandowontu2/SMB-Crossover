"""Avoid redundant Sunny growth enemy-palette packets in the owning prelude."""
import json,subprocess,shutil
from pathlib import Path
import audit_current_menu_indicators_1102_v1 as A
import check_hogan_current_bounded_v1 as M
from check_tmnt_render_oa import address,location
from prepare_selected_native_packet_v1 import R,sha
O=R/'build/sunny-face-gate-1102-v8'
BASE=R/'build/sunny-palette-dedup-1102-v5/candidate.nes'

def main():
    O.mkdir(exist_ok=True);b=A.bundle();b['raw']=BASE.read_bytes();raw=bytearray(b['raw'])
    assert sha(BASE)=='e05eb6ea3955e650385527351a70e1efba7f633f26839de99157eb8d1cdda30f'
    gate=address(b,'CrossoverPatchStatusName')+42;hole=location(b,'CrossoverPatchStatusName')+42
    assert gate==0xb206 and raw[hole:hole+24]==bytes([234])*24
    call=location(b,'NrColors::Own')+2;old=bytes(raw[call:call+18]);assert old.hex()=='8d6a01a95f8d6c01a9b18d6d01a983205a01'
    # The original first18B tail-JMP and existing private getter at+18..+40
    # remain exact. The last24B are unreachable NOP padding, with no symbol
    # or original local branch target. The new entry is reached only here.
    source='''.setcpu "6502"
.segment "CODE"
 php
 pha
 lda $%04x
 cmp #23
 bne Original
 lda $%04x
 cmp #9
 bne Original
 pla
 plp
 rts
Original:
 pla
 plp
 jmp $%04x
'''%(address(b,'SelectedCharacter'),address(b,'GameEngineSubroutine'),address(b,'QueueMegaManFacePalette'))
    (O/'gate.s').write_text(source);(O/'gate.cfg').write_text('MEMORY{ROM:start=$%04x,size=24,file=%%O;}SEGMENTS{CODE:load=ROM,type=ro;}'%gate)
    cc=R/'tools/Windows/cc65/bin'
    for cmd in [[cc/'ca65.exe',O/'gate.s','-o',O/'gate.o'],[cc/'ld65.exe','-C',O/'gate.cfg','-o',O/'gate.bin',O/'gate.o']]:
        p=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert p.returncode==0,p.stderr
    code=(O/'gate.bin').read_bytes();assert len(code)==23
    target=bytearray(old);target[4]=gate&255;target[9]=gate>>8
    # Exactly the low/high operands change; native bank3 and JSR stay.
    patches=[dict(offset=call,old=old.hex(),new=target.hex()),dict(offset=hole,old=bytes(raw[hole:hole+len(code)]).hex(),new=code.hex())]
    for p in patches:raw[p['offset']:p['offset']+len(bytes.fromhex(p['new']))]=bytes.fromhex(p['new'])
    candidate=O/'candidate.nes';candidate.write_bytes(raw)
    for ext in ['.dbg','.lbl']:shutil.copyfile(BASE.with_suffix(ext),candidate.with_suffix(ext))
    new=dict(b,raw=bytes(raw));seeds=[M.fresh(x)for x in [b,new]];cases=0
    for rawid in [20,21,23]:
        for engine in [0,8,9,10,12]:
            for star in [0,1]:
                for carry in [0,1]:
                    pair=[]
                    for seed in seeds:
                        m=M.fork(seed);M.put(m,SelectedCharacter=rawid,GameEngineSubroutine=engine,StarInvincibleTimer=star,VRAM_Buffer1_Offset=0,SunnyPalette=255,PlayerStatus=1,GuestPowerupActive=0)
                        z=M.invoke(m,'NrColors',p=0x30|carry);at=address(new,'VRAM_Buffer1');packet=[m[at+i]for i in range(M.get(m,'VRAM_Buffer1_Offset')+1)];pair.append((m,z,packet))
                    if rawid!=23 or engine!=9:
                        assert pair[0][2]==pair[1][2]
                        assert [pair[0][1][k]for k in ['A','X','Y','P']]==[pair[1][1][k]for k in ['A','X','Y','P']]
                    else:
                        assert pair[0][2][:3]==[63,29,3]
                        assert pair[0][2][6:]==pair[1][2],pair
                    cases+=1
    q=dict(passed=True,private=True,installed=False,cases=cases,base_ROM_SHA256=sha(BASE),ROM_sha256=sha(candidate),patches=patches,scope='Only Sunny engine9 omits identical enemy P3 refresh from NrColors. Other owning Ice/City and all other engines retain exact queue/AXYP. P2/backdrop/P0 remain native. Entry uses23of24 verified unreachable padding bytes, no new RAM/pages. Native full-stage proof required.',bindings={str(p):sha(p)for p in [Path(__file__),O/'gate.s',O/'gate.bin',BASE]})
    (O/'candidate.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))
if __name__=='__main__':main()
