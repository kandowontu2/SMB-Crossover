"""Assemble unused authentic SMB3 core on private b86 asset relocation.

Fixed twelve cold NSF contracts only. Preserve the entire payload; observed
instruction bindings do not constitute universal/static71-song reachability.
"""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler
from link_pit_rygar_sophia_audit_cpu import scoped_load

R=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
BASE=D/'smb3-assets-current3cee-v2'
TRACE=D/'smb3-original-music-closure-v3'
NSF=R/'reference/new-roster-audio/mario3/crossover-named.nsf'
SHA='4f22166e5baf4db867564b57c3d152dacb85b6365f7bf94cf0883d612e7f915c'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

HELPERS=r'''
; Existing exclusive native-music history storage, NOT a new RAM allocation.
; Standalone context only: future host source-state borrow/lifecycle unproved.
B3VirtualMaps=XgLzHistory+$700
B3SavedR0=XgLzHistory+$708
B3SavedR1=XgLzHistory+$709
B3SavedX=XgLzHistory+$70a
B3SavedY=XgLzHistory+$70b
B3Value=XgLzHistory+$70c
B3SavedABank=XgLzHistory+$70d
B3Index=XgLzHistory+$70e
B3AddressLo=XgLzHistory+$70f
B3AddressHi=XgLzHistory+$710
B3Source4012=XgLzHistory+$711
B3Source4015=XgLzHistory+$712
B3PendingClone=XgLzHistory+$713
B3ActiveClone=XgLzHistory+$714
B3WorkEnd=XgLzHistory+$715
.assert B3VirtualMaps=$7b00,error,"Standalone native image work placement"

B3ReadAbsX:
 php
 stx B3SavedX
 sty B3SavedY
 stx B3Index
 jmp B3ReadAbsolute
B3ReadAbsY:
 php
 stx B3SavedX
 sty B3SavedY
 sty B3Index
B3ReadAbsolute:
 jsr B3BorrowPointer
 tsx
 lda $0102,x
 sta R0
 lda $0103,x
 sta R1
 ldy #1
 lda (R0),y
 sta B3AddressLo
 iny
 lda (R0),y
 sta B3AddressHi
 lda R0
 clc
 adc #2
 sta $0102,x
 lda R1
 adc #0
 sta $0103,x
 lda B3AddressLo
 clc
 adc B3Index
 sta R0
 lda B3AddressHi
 adc #0
 sta R1
 jmp B3ReadAddress
B3Read6B:
 php
 stx B3SavedX
 sty B3SavedY
 jsr B3BorrowPointer
 lda $6b
 clc
 adc B3SavedY
 sta R0
 lda $6c
 adc #0
 sta R1
 jmp B3ReadAddress
B3Read71:
 php
 stx B3SavedX
 sty B3SavedY
 jsr B3BorrowPointer
 lda $71
 clc
 adc B3SavedY
 sta R0
 lda $72
 adc #0
 sta R1
B3ReadAddress:
 lda R1
 bpl B3ReadRAM
 lda CurrentBank
 sta B3SavedABank
 lda R1
 sec
 sbc #$80
 lsr
 lsr
 lsr
 lsr
 tay
 lda B3VirtualMaps,y
 tay
 lda B3PayloadBanks,y
 ora #MMC5_PRG_ROM
 BankPRGA a
 lda R1
 and #$0f
 ora #$b0
 sta R1
 ldy #0
 lda (R0),y
 sta B3Value
 lda B3SavedABank
 BankPRGA a
 jmp B3ReadRestore
B3ReadRAM:
 ldy #0
 lda (R0),y
 sta B3Value
B3ReadRestore:
 lda B3SavedR0
 sta R0
 lda B3SavedR1
 sta R1
 ldx B3SavedX
 ldy B3SavedY
 plp
 lda B3Value
 rts
B3BorrowPointer:
 lda R0
 sta B3SavedR0
 lda R1
 sta B3SavedR1
 rts
B3PayloadBanks:
 .byte 78,86,90,93,95,96,98,118,119

; Logical source4012 is retained independently from translated hardware4012.
; Source cadence/4010/4011/4013/4015 and every source event are unchanged.
B3Write4012:
 php
 pha
 sta B3Source4012
 phx
 phy
 lda B3Source4012
 ldx #6
B3SampleFind:
 cmp B3OriginalAddresses,x
 beq B3SampleFound
 dex
 bpl B3SampleFind
 brk ; Outside qualified twelve-role request domain; never silent fallback.
B3SampleFound:
 lda B3TranslatedAddresses,x
 sta $4012
 lda #70|MMC5_PRG_ROM
 cpx #6
 bne B3SampleClone
 lda #97|MMC5_PRG_ROM
B3SampleClone:
 sta B3PendingClone
 lda B3Source4015
 and #16
 bne B3SampleDone
 lda B3PendingClone
 sta B3ActiveClone
 sta $5117
B3SampleDone:
 ply
 plx
 pla
 plp
 rts
B3Write4015:
 php
 pha
 sta B3Source4015
 sta $4015
 and #16
 bne B3StatusDone
 lda B3PendingClone
 beq B3StatusDone
 sta B3ActiveClone
 sta $5117
B3StatusDone:
 pla
 plp
 rts
B3Write4015X:
 php
 pha
 txa
 jsr B3Write4015
 pla
 plp
 rts
B3OriginalAddresses:
 .byte $b8,$a6,$aa,$80,$6d,$82,$60
B3TranslatedAddresses:
 .byte $d7,$c5,$c9,$ea,$f4,$ec,$c5
'''

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    out=p.parse_args().output.resolve();assert not out.is_relative_to(R);out.mkdir(parents=True,exist_ok=False)
    assert sha(BASE/'candidate.nes')=='b86bfa95032a54837fbd1802d60659aaca9dfa8c55a713cc8a58a58ef0a594f6'
    assert sha(NSF)==SHA;raw=NSF.read_bytes();image=raw[128:];assert len(image)==36864
    src=out/'source';src.mkdir();manifest=json.loads((BASE/'source-manifest.json').read_text())
    for n,h in manifest.items():
        assert sha(BASE/'source'/n)==h,n
        dest=src/n;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(BASE/'source'/n,dest)
    instructions={};bindings={};deps={str(NSF):sha(NSF)}
    for f in TRACE.glob('*/footprint.json'):
        deps[str(f)]=sha(f)
        for q in json.loads(f.read_text())['instruction_rows']:
            pc,physical=q['PC'],q['physical_PC']
            assert pc not in bindings or bindings[pc]==physical,(pc,bindings.get(pc),physical)
            bindings[pc]=physical;instructions[pc]=q
    spans=[(0xa000,0xa740,0x1000),(0xe2c0,0xe880,0x32c0),(0x9000,0x901e,0)]
    mem=[0]*65536
    for lo,hi,physical in spans:mem[lo:hi]=image[physical:physical+hi-lo]
    c=MPU(memory=mem);dis=Disassembler(c)
    lines=['; Authenticated original SMB3 NSF, fixed twelve cold role contracts.','.if ::ENABLE_MMC5_EXPANDED','.pushseg','.segment "SMB3_NATIVE_CORE"','B3CoreStart:','.assert B3CoreStart=$cbe8,lderror,"SMB3 core actual freed C38 range"']
    metadata=[];source_labels=set()
    def label(at):
        assert any(lo<=at<hi for lo,hi,_ in spans),('Code target outside retained spans',hex(at))
        return f'::B3Source{at:04X}'
    def emit(lo,hi):
        at=lo
        while at<hi:
            lines.append(f'B3Source{at:04X}:');source_labels.add(at)
            if at not in instructions:
                lines.append(f' .byte ${mem[at]:02x}');at+=1;continue
            q=instructions[at];size=q['bytes'];op,mode=q['mnemonic'],q['mode']
            n,text=dis.instruction_at(at);assert n==size,(at,n,size)
            v=mem[at+1];word=v+256*mem[at+2]
            original=text;classification='original'
            if mode=='rel':
                target=at+size+(v-256 if v>=128 else v);text='j'+op[1:].lower()+' '+label(target);classification='genuine relocated branch'
            elif op in ['JSR','JMP']and mode=='abs':text=op+' '+label(word);classification='genuine relocated call/jump'
            elif mode in ['abs','abx','aby']and word>=0x8000:
                assert op=='LDA'and mode in ['abx','aby'],(at,op,mode,word)
                text='jsr B3ReadAbs'+('X'if mode=='abx'else'Y')+f'\n .word ${word:04x}';classification='original numeric ROM read'
            elif mode=='iny':
                assert op=='LDA'and v in [0x6b,0x71]
                text='jsr B3Read'+f'{v:02X}';classification='original numeric indirect read'
            elif op=='STA'and word in [0x5ffc,0x5ffd]and mode=='abs':
                text=f'sta B3VirtualMaps+{word-0x5ff8}';classification='logical original NSF mapping write'
            elif word==0x4012 and op=='STA'and mode=='abs':text='jsr B3Write4012';classification='faithful source request with translated sample'
            elif word==0x4015 and op in ['STA','STX']and mode=='abs':text='jsr B3Write4015'+('X'if op=='STX'else'');classification='source physical enable/disable retained'
            lines.append(' '+text);metadata.append(dict(source_PC=at,physical_source_PC=bindings[at],source_bytes=size,source_instruction=original,linked_instruction=text,classification=classification));at+=size
    for lo,hi,_ in spans[:2]:emit(lo,hi)
    lines.append(HELPERS);lines+=['B3CoreEnd:','.assert B3CoreEnd<=$dfe8,lderror,"SMB3 native core exceeds actual5120B free C38 span"',
        '.segment "SMB3_NATIVE_COLD"','B3ColdStart:','.assert B3ColdStart=$a800,lderror,"SMB3 cold bridge verified86 gap"',
        'B3StandaloneCold:',' php',' pha',' phx',' phy',' ldx #7','B3ResetMaps:',' lda B3InitialMaps,x',' sta B3VirtualMaps,x',' dex',' bpl B3ResetMaps',
        ' lda #0',' sta B3Source4012',' sta B3Source4015',' sta B3PendingClone',' sta B3ActiveClone',' ply',' plx',' pla',' plp',' jmp B3Source9000',
        'B3InitialMaps:',' .byte '+','.join(str(v)for v in raw[112:120])]
    emit(0x9000,0x901e)
    lines+=['B3ColdEnd:','.assert B3ColdEnd<=$aa00,lderror,"SMB3 cold pool exceeds512B"','.popseg','.endif','']
    native=src/'src/smb3_native_standalone.s';native.write_text('\n'.join(lines))
    assets=src/'audio/smb3-native';assets.mkdir(parents=True);(assets/'source-payload.bin').write_bytes(image)
    fixed=(BASE/'candidate.nes').read_bytes()[16+127*8192:16+128*8192];ca,cb=bytearray(fixed),bytearray(fixed)
    for clone,lo,hi,dest in [(ca,0x3980,0x4281,0x1140),(ca,0x3000,0x3241,0x1a80),(ca,0x6b40,0x6b81,0x1d00),(cb,0x8800,0x8b41,0x1140)]:clone[dest:dest+hi-lo]=image[lo:hi]
    for clone in [ca,cb]:assert all(x==y or 0x1140<=i<0x1fc1 for i,(x,y)in enumerate(zip(clone,fixed)))
    (assets/'clone70.bin').write_bytes(ca);(assets/'clone97.bin').write_bytes(cb)
    more=['.if ::ENABLE_MMC5_EXPANDED','.pushseg']
    for i in range(9):more +=[f'.segment "SMB3_SOURCE_PAGE{i}"',f'B3PayloadPage{i}:',f'.incbin "audio/smb3-native/source-payload.bin",{i*4096},4096']
    more +=['.segment "SMB3_DMC_CLONE70"','B3DmcClone70:','.incbin "audio/smb3-native/clone70.bin"','.segment "SMB3_DMC_CLONE97"','B3DmcClone97:','.incbin "audio/smb3-native/clone97.bin"','.popseg','.endif','']
    (src/'src/smb3_native_payload.s').write_text('\n'.join(more))
    entry=src/'src/entrypoint.s';b=entry.read_bytes();nl=b'\r\n'if b'\r\n'in b else b'\n';entry.write_bytes(b+nl+b'.include "smb3_native_standalone.s"'+nl+b'.include "smb3_native_payload.s"'+nl)
    cfg=src/'smb1base-mmc5-expanded.cfg';b=cfg.read_bytes();nl=b'\r\n'if b'\r\n'in b else b'\n'
    def replace(old,new):
        nonlocal b
        old=old.encode();new=new.replace('\n',nl.decode()).encode();assert b.count(old)==1,(old,b.count(old));b=b.replace(old,new)
    for bank in [78,86,90,93,96,98,118,119]:
        name=f'X5_NEW_{bank:02X}';old=f'{name}: start=$a000, size=$2000, type=ro, file=%O, fill=yes, fillval=$ff, bank=${bank:02x};'
        if bank==86:
            new=f'{name}: start=$a000, size=$0800, type=ro, file=%O, fill=yes, fillval=$ff, bank=${bank:02x};\n    B3_COLD86: start=$a800,size=$0200,type=ro,file=%O,fill=yes,fillval=$ff,bank=$56;\n    B3_GAP86: start=$aa00,size=$0600,type=ro,file=%O,fill=yes,fillval=$ff,bank=$56;'
        else:new=old.replace('size=$2000','size=$1000')
        new+=f'\n    B3_PAYLOAD{bank}: start=$b000,size=$1000,type=ro,file=%O,fill=yes,fillval=$ff,bank=${bank:02x};';replace(old,new)
    old='SMB3_ASSET_MIKE_C95: start=$c6c0, size=$1940, type=ro, file=%O, fill=yes, fillval=$ff, bank=$5f;'
    replace(old,old.replace('$1940','$0940')+'\n    B3_PAYLOAD95: start=$d000,size=$1000,type=ro,file=%O,fill=yes,fillval=$ff,bank=$5f;')
    for bank in [70,97]:replace(f'X5_NEW_{bank:02X}: start=$c000, size=$2000',f'X5_NEW_{bank:02X}: start=$e000, size=$2000')
    replace('VG_AUDIO_DISPATCH:load=XG_AUDIO_MEM,type=ro,start=$dfe8;','SMB3_NATIVE_CORE:load=XG_AUDIO_MEM,type=ro,start=$cbe8;\n    VG_AUDIO_DISPATCH:load=XG_AUDIO_MEM,type=ro,start=$dfe8;')
    extra='\n    SMB3_NATIVE_COLD:load=B3_COLD86,type=ro;\n    SMB3_DMC_CLONE70:load=X5_NEW_46,type=ro;\n    SMB3_DMC_CLONE97:load=X5_NEW_61,type=ro;\n'
    for page,bank in enumerate([78,86,90,93,95,96,98,118,119]):extra+=f'    SMB3_SOURCE_PAGE{page}:load=B3_PAYLOAD{bank},type=ro;\n'
    replace('SEGMENTS {','SEGMENTS {'+extra);cfg.write_bytes(b)
    prep=dict(parent_ROM_sha256=sha(BASE/'candidate.nes'),source_NSF_sha256=SHA,source_trace_proof_sha256=sha(TRACE/'proof.json'),
              distinct_observed_instructions=len(instructions),emitted_original_instruction_rows=metadata,full_original_payload_bytes=len(image),
              source_numeric_pointers_preserved=True,source_RAM_not_relocated=True,standalone_work_range=[0x7b00,0x7b15],borrowed_pointer_restored=[3,4],
              source_state_scope='Exact twelve cold contracts. Original source RAM and register ABI retained; adapter work7B00..7B14 and host CurrentBank shadow are extra owned metadata, not source state.',
              private_source_changes=[n for n in manifest if sha(src/n)!=manifest[n]],source_dependencies=deps,
              limitations='No active host AudioUpdate/owner/lifecycle integration, no native timing, no universal/static71-song reachability proof.')
    (out/'preparation.json').write_text(json.dumps(prep,indent=2)+'\n')
    cmd=[sys.executable,str(R/'tools/build_mmc5_expanded.py'),'--source-overlay',str(src),'--output',str(out/'candidate.nes')]
    run=subprocess.run(cmd,cwd=R,capture_output=True,text=True);(out/'build-command.json').write_text(json.dumps(dict(command=cmd,returncode=run.returncode,stdout=run.stdout,stderr=run.stderr),indent=2)+'\n')
    assert run.returncode==0,run.stdout+run.stderr
    b=scoped_load(out/'candidate.nes');ad=lambda n:int(b['syms'][n]['val'],0)
    proof=dict(passed=True,source_only=True,native_run=False,active_host_music=False,ROM_sha256=sha(out/'candidate.nes'),parent_ROM_sha256=sha(BASE/'candidate.nes'),
               core_bytes=ad('B3CoreEnd')-ad('B3CoreStart'),core_budget=5120,cold_bytes=ad('B3ColdEnd')-ad('B3ColdStart'),cold_budget=512,
               full_payload_bytes=36864,DMC_clone_bytes=16384,tool_sha256=sha(__file__),standalone_CPU_qualified=False)
    (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof,indent=2))
if __name__=='__main__':main()
