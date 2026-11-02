"""Assemble the real cartridge-resident Excitebike loader proposal.

No candidate ROM is written: final CHR reader closure is still a prerequisite.
The components and resident byte budget are concrete and independently testable.
"""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
O=R/'build/excitebike-pose-1101-v3'
BASE=R/'build/shinobi-camera-1101-v20/candidate.nes'


def run(command):
    p=subprocess.run([str(v) for v in command],capture_output=True,text=True)
    assert p.returncode==0,p.stderr


def main():
    b=scoped_load(BASE);raw=b['raw']
    start=16+65*8192+0xe00
    assert raw[start:start+776]==bytes([255])*776
    assert '.res $1108-(*-ProtoArtBegin), $ff' in (R/'src/protoman.s').read_text()
    # Existing exact source actor object is a read-only input, not rebuilt/copied.
    actor=R/'build/excite-prince-component-1101-v2/component.o'
    cfg='MEMORY{C:start=$a000,size=$1800,file=%O,fill=yes;}\nSEGMENTS{EX_CODE:load=C,type=ro;EX_DATA:load=C,type=ro,start=$a900;CODE:load=C,type=ro,start=$b000;}\n'
    (O/'owner-actor.cfg').write_text(cfg)
    cc=R/'tools/Windows/cc65/bin'
    run([cc/'ld65.exe','-C',O/'owner-actor.cfg',actor,O/'pose.o','-o',O/'owner-actor.bin','-Ln',O/'owner-actor.lbl'])
    kernel=(O/'owner-actor.bin').read_bytes();assert len(kernel)==6144
    art=json.loads((O/'body-native.json').read_text())
    offsets=[];packets=bytearray()
    for pose in art['poses']:
        offsets.append(46+len(packets))
        packets.append(len(pose['cells']))
        for cell in pose['cells']:
            packets.extend([cell['tile'],cell['attr'],cell['x']&255,cell['y']&255])
    metadata=b''.join(n.to_bytes(2,'little') for n in offsets)+bytes(packets)
    assert len(metadata)<2048
    metadata+=bytes(2048-len(metadata))
    (O/'owner-metadata.bin').write_bytes(metadata)
    body=(O/'body-native.chr').read_bytes()
    cookie=bytes([0xa7,37,1])+hashlib.sha256(kernel+metadata+body).digest()[:13]
    (O/'excitebike-cookie.bin').write_bytes(cookie)
    # Same reviewed ROM-only dual-header/forcedblank protocol, adapted counts.
    loader=(R/'tools/reference/shinobi_resident_loader_1101_v1.inc').read_text()
    loader=loader.replace('Sh','Ex').replace('SHINOBI_RESIDENT','EXCITEBIKE_RESIDENT')
    start=loader.index('ExCheckCode:\n');end=loader.index('\nExRetire:\n',start)
    # Private C-only helper. Its sole runtime callers save their entire public
    # ABI and consume only carry before overwriting A/X. Identity, both full
    # headers and the caller's C-bank mapping are still checked/restored.
    loader=loader[:start]+'''ExCheckCode:
 lda CurrentBankC
 pha
 lda SelectedCharacter
 cmp #36
 bne ExHeadersNo
 ldx #3
ExHeadersBank:
 stx CurrentBankC
 stx $5116
 ldx #15
ExHeadersByte:
 lda $dfe0,x
 cmp ExCookie,x
 bne ExHeadersNo
 dex
 bpl ExHeadersByte
 ldx CurrentBankC
 dex
 cpx #1
 bne ExHeadersBank
 sec
 bcs ExHeadersRestore
ExHeadersNo:
 clc
ExHeadersRestore:
 pla
 sta CurrentBankC
 sta $5116
 rts
'''+loader[end:]
    loader=loader.replace('cmp #36','cmp #37').replace('cmp #7','cmp #6').replace('sbc #7','sbc #6').replace('cmp #9','cmp #8')
    loader=loader.replace('shinobi-cookie.bin','excitebike-cookie.bin')
    loader=loader.replace('ExCarrierLow:.byte <506,<507,<508,<509,<510,<513,<515,<516,<517','ExCarrierLow:.byte <728,<729,<730,<731,<732,<733,<734,<735')
    loader=loader.replace('ExCarrierUpper:.byte >506,>507,>508,>509,>510,>513,>515,>516,>517','ExCarrierUpper:.byte >728,>729,>730,>731,>732,>733,>734,>735')
    # All six admission tests share one nearby rejection jump. The old long
    # conditional pseudo-ops each emitted an otherwise redundant absolute JMP.
    for old,new in [('jne ExLoadNo','bne ExGuardNo'),('jeq ExLoadNo','beq ExGuardNo'),('jpl ExLoadNo','bpl ExGuardNo')]:
        loader=loader.replace(old,new)
    loader=loader.replace('jcs ExLoadYes\n sei','bcc ExColdBegin\n jmp ExLoadYes\nExGuardNo:\n jmp ExLoadNo\nExColdBegin:\n sei')
    # Both cold and restoration paths publish the same ROM-owned CHR state.
    publisher='ExRomFar X5PublishChr,Bank_X5PublishChr'
    assert loader.count(publisher)==2
    loader=loader.replace(publisher,'jsr ExPublishChr')
    loader=loader.replace('ExSavedSmcOffsets:',f'ExPublishChr:\n {publisher}\n rts\nExSavedSmcOffsets:')
    # The Ex cold pages are contiguous728..735 in one upper quarter. The
    # reviewed Sh source needs two sparse tables; Ex does not. Keep its exact
    # upper-latch reset, dummy buffered read, Y0 and copy/verify protocol.
    oldmap=' ldx R2\n lda ExCarrierUpper,x\n sta $5130\n lda ExCarrierLow,x\n sta $5123'
    newmap=' lda #>728\n sta $5130\n lda R2\n clc\n adc #<728\n sta $5123'
    assert loader.count(oldmap)==1;loader=loader.replace(oldmap,newmap)
    for declaration in ['ExCarrierLow:.byte <728,<729,<730,<731,<732,<733,<734,<735\n',
                        'ExCarrierUpper:.byte >728,>729,>730,>731,>732,>733,>734,>735\n']:
        assert loader.count(declaration)==1;loader=loader.replace(declaration,'')
    # Every payload byte has already passed readback before either header is
    # published. Include byte0 in the existing two-bank loop: RAM3 authenticates
    # first and RAM2's byte0 remains the final commit. Dual-header readers cannot
    # enter while either is incomplete, including any disabled-NMI cut.
    loader=loader.replace('dex\n bne ExPublishByte','dex\n bpl ExPublishByte')
    redundant=''' lda #3
 sta CurrentBankC
 sta $5116
 lda #$a7
 sta $dfe0
 lda #2
 sta CurrentBankC
 sta $5116
 lda #$a7
 sta $dfe0
'''
    assert loader.count(redundant)==1;loader=loader.replace(redundant,'')
    before=''' lda #0
 sta $5130
 bit $2002
 lda #$0c
 sta $2006
 lda #0
 sta $2006
 lda $2007                  ; mandatory buffered-read dummy
 ldy #0
 rts'''
    after=''' ldy #0
 sty $5130
 bit $2002
 lda #$0c
 sta $2006
 sty $2006
 lda $2007                  ; mandatory buffered-read dummy
 rts'''
    assert loader.count(before)==1;loader=loader.replace(before,after)
    # R2 is clamped0..7 and D8's low three bits are zero. ORA therefore
    # selects the identical byte without CLC; map carry is dead until CMP in
    # the copy/verify loop, and public P is restored from the owning frame.
    loader=loader.replace(' lda R2\n clc\n adc #<728\n sta $5123',' lda R2\n ora #<728\n sta $5123')
    loader=loader.replace(' ldx #3\nExPublishBank:',' ldx #3\n ldy #1\nExPublishBank:')
    before=' ldx CurrentBankC\n dex\n cpx #1\n bne ExPublishBank'
    assert loader.count(before)==1;loader=loader.replace(before,' ldx #2\n dey\n bpl ExPublishBank')
    (O/'owner-loader.inc').write_text(loader)
    assert loader.count('jsr ExCheckCode')==1
    dispatch_source=(R/'tools/reference/excitebike_resident_dispatch_1101_v1.inc').read_text()
    assert dispatch_source.count('jsr ExCheckCode')==1
    names=['CurrentBankC','SelectedCharacter','R0','R1','R2','NextBank_SMC','SafecallA_SMC',
           'FarcallJmpTarget_SMC','SafereturnA_SMC','FarCallCommon','ReloadCHRBank','OperMode',
           'FamilyMainCommit','DisableScreenFlag','Mirror_PPUMASK','NmiDisable','X5PublishChr',
           'Mirror_PPUCTRL','HorizontalScroll','VerticalScroll']
    definitions=''.join(f'{name}=${address(b,name):04x}\n' for name in names)
    definitions+=f'Bank_X5PublishChr=${((location(b,"X5PublishChr")-16)//8192)|128:02x}\n'
    (O/'owner-loader.s').write_text('.setcpu "6502"\n.macpack longbranch\n'+definitions+
        '.include "owner-loader.inc"\n.export ExRetireBoth\nExRetireBoth:\n jsr ExRetire\n jmp $a849\n')
    (O/'owner-loader.cfg').write_text('MEMORY{R:start=$ae00,size=$308,file=%O;}SEGMENTS{EXCITEBIKE_RESIDENT:load=R,type=ro;}')
    run([cc/'ca65.exe','-I',O,'--bin-include-dir',O,O/'owner-loader.s','-o',O/'owner-loader.o'])
    run([cc/'ld65.exe','-C',O/'owner-loader.cfg',O/'owner-loader.o','-o',O/'owner-loader.bin','-Ln',O/'owner-loader.lbl'])
    resident=(O/'owner-loader.bin').read_bytes();assert len(resident)<=776
    result=dict(passed=True,baseline_SHA256=hashlib.sha256(raw).hexdigest(),
        resident_bytes=len(resident),resident_budget=776,resident_remaining=776-len(resident),
        kernel_carrier_bytes=len(kernel),metadata_bytes=len(metadata),
        metadata_used_bytes=46+len(packets),body_bytes=len(body),
        proposed_code_pages=list(range(728,734)),proposed_metadata_pages=[734,735],
        proposed_body_pages=[736,737,738],proposed_unused_page=739,
        raw_identity=37,cookie=cookie.hex(),ROM_written=False,installed=False,
        internal_header_helper_ABI='Carry-only private leaf; exactselected37/both16Bheaders/Cmapping. Sole two runtime callers discardA/X/P and preserve their complete publicABI onownframes.',
        exact_header_helper_callers=['ExLoad','ExDispatch'],
        scope='Concrete source actor+pose and resident authenticated forcedblank loader. No host entry, retirement-hook integration or CHR allocation yet.',
        bindings={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in [Path(__file__),actor,O/'pose.o',O/'owner-loader.bin',O/'owner-actor.bin',O/'owner-metadata.bin',O/'body-native.chr']})
    (O/'owner-assembly.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='bindings'}))


if __name__=='__main__':main()
