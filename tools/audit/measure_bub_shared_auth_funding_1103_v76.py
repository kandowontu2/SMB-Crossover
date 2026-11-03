"""Source-reproduce then measure shared Sh/Bub full-auth primitive funding.

Only existing source-declared spans are used in the memory proposal. It is
not a permission to replace Shinobi's resident entry or emit a cartridge.
"""
import json
from pathlib import Path
import measure_bub_full_auth_helper_1103_v73 as F
O,R,N,Q,address,sha=F.O,F.R,F.N,F.Q,F.address,F.sha


def build():
    old,base,route,q,head,manifest,ol,bl,_=F.build()
    # Reproduce the complete exact73B installed ShCheckCode before factoring.
    source=(R/'tools/reference/shinobi_resident_loader_1101_v1.inc').read_text()
    source=source[:source.index('ShRetire:\n')]
    source=source.replace('.export ShLoad,ShCheckCode,ShRetire,ShCookie,ShResidentEnd',
        '.export ShCheckCode,ShCheckEnd')
    source='.setcpu "6502"\nCurrentBankC=$7da1\nSelectedCharacter=$6002\nShCookie=$aa78\n'+source+'ShCheckEnd:\n'
    cfg='MEMORY{S:start=$a800,size=$49,file=%O;}SEGMENTS{SHINOBI_RESIDENT:load=S,type=ro;}'
    shlabels=F.L.assemble('shared-auth-v76-Sh-reproduce',source,cfg)
    at=16+65*8192+0x800
    assert (O/'shared-auth-v76-Sh-reproduce.bin').read_bytes()==old['raw'][at:at+73]
    assert shlabels['ShCheckEnd']==0xa849
    source=(O/'full-auth-v73-final.s').read_text()
    def once(a,z):
        nonlocal source
        assert source.count(a)==1,(a,source.count(a));source=source.replace(a,z)
    once(' jsr CoCheckHeaders\n bcc CoColdBegin\n jmp CoYes\n',
        ' jsr CoCheckHeaders\n bcs CoYes\n')
    once('CoGuardNo:\n jmp CoNo\nCoColdBegin:\n','CoColdBegin:\n')
    once('CoColdMode:\n','CoGuardNo:\n jmp CoNo\nCoColdMode:\n')
    once('CoColdMode:\n jsr CoSelect\n jcc CoNo\n',
        'CoColdMode:\n jsr CoSelect\n bcc CoGuardNo\n')
    assert source.count(' ldx CurrentBankC\n dex\n cpx #1\n')==2
    source=source.replace(' ldx CurrentBankC\n dex\n cpx #1\n',' dex\n cpx #1\n')
    # The successful final CPX#1 already setsC; no intervening operation
    # changes it before this unconditional BCS to the shared restore.
    once(' bne CoCheckBank\n sec\n bcs CoHeadersRestore\n',
        ' bne CoCheckBank\n bcs CoHeadersRestore\n')
    once(' ldx #0\n:\n lda R0,x\n pha\n inx\n cpx #8\n bne :-\n',
        ' ldx #$f8\n:\n lda R0+8,x\n pha\n inx\n bne :-\n')
    once(' jsr CoSelectCookie\n bcc :+\n jsr CoCheckHeaders\n',
        ' jsr CoSelectCookie\n bcc :+\nCoAuthKnownCookie:\n jsr CoCheckHeaders\n')
    once(' lda CoDescriptorHi,x\n sta R4\n sec\nCoSelectReturn:',
        ' lda CoDescriptorHi,x\n sta R4\nCoSelectReturn:')
    once(' tax\n lda CoCookieLo,x\n sta R5\n lda CoCookieHi,x\n sta R6\n sec\n rts\nCoSelectNo:',
        ' tax\nCoSelectCookieIndex:\n lda CoCookieLo,x\n sta R5\n lda CoCookieHi,x\n sta R6\n sec\n rts\nCoSelectNo:')
    once('CoRetireLoop:\n txa\n pha\n lda CoCookieLo,x\n sta R5\n lda CoCookieHi,x\n sta R6\n jsr CoCheckHeaders\n',
        'CoRetireLoop:\n txa\n pha\n jsr CoSelectCookieIndex\n jsr CoCheckHeaders\n')
    once(' .res 2,$ea\nCoExCookie:', 'CoExCookie:')
    once('CoSmc:\n', '''; Thirty source-funded bytes: no end/worker pad is leased.
CoCheckShCookie:
 lda R5
 pha
 lda R6
 pha
 lda #<$aa78
 sta R5
 lda #>$aa78
 sta R6
 jmp CoAuthKnownCookie
CoNativeSide:
 pla
 tay
 pla
 tax
 pla
 plp
 jmp $958b
CoShNoPartial:
 pla
 plp
 clc
 rts
CoSmc:
''')
    source+='''
.segment "SH_SHARED_AUTH"
.export ShCheckCode,ShFastEnd,CoNativePrimitive,CoNativeSec,CoNativeNo
ShCheckCode:
 php
 pha
 lda SelectedCharacter
 cmp #36
 jne CoShNoPartial
 txa
 pha
 tya
 pha
 jsr CoCheckShCookie
 bcc CoNativeNo
 jmp CoNativeSec
CoNativePrimitive:
 php
 pha
 lda SelectedCharacter
 cmp #39
 bne CoNativeNormal
 txa
 pha
 tya
 pha
 jsr CoCheckCode
 bcc CoNativeNo
 lda FarcallJmpTarget_SMC+1
 cmp #$b6
 jeq CoNativeSide
CoNativeSec:
 pla
 tay
 pla
 tax
 pla
 plp
 sec
 rts
CoNativeNo:
 pla
 tay
 pla
 tax
 pla
 plp
 clc
 rts
CoNativeNormal:
 pla
 plp
 jmp $a740
ShFastEnd:
.export CoCheckShCookie,CoNativeSide,CoShNoPartial,CoAuthKnownCookie
'''
    cfg='MEMORY{M:start=$ae00,size=$213,file=%O;X:start=$ab72,size=$62,file="'+(O/'shared-auth-v76-extra.bin').as_posix()+'";S:start=$a800,size=$49,file="'+(O/'shared-auth-v76-Sh.bin').as_posix()+'";}SEGMENTS{COMMON_OWNER_PROPOSAL:load=M,type=ro;PR_EXTRA:load=X,type=ro;SH_SHARED_AUTH:load=S,type=ro;}'
    labels=F.L.assemble('shared-auth-v76',source,cfg)
    manager=(O/'shared-auth-v76.bin').read_bytes();extra=(O/'shared-auth-v76-extra.bin').read_bytes();sh=(O/'shared-auth-v76-Sh.bin').read_bytes()
    assert len(manager)==531 and len(extra)==92 and len(sh)==73
    assert labels['CoCold']==0xae00 and labels['CoRetire']==0xae0b and labels['ShCheckCode']==0xa800 and labels['ShFastEnd']==0xa849
    # The old fifteen end pad bytes and both existing cookie addresses/bytes
    # remain exact: pending Prince/DK changes do not lose those resources.
    original=old['raw'][16+65*8192+0xe00:16+65*8192+0x1013]
    assert manager[-47:]==original[-47:]and manager[-15:]==bytes([234])*15
    raw=bytearray(old['raw']);patches=[]
    for pc,data in [(0xae00,manager),(0xab72,extra),(0xa800,sh)]:
        at=16+65*8192+(pc&8191);before=raw[at:at+len(data)]
        raw[at:at+len(data)]=data
        patches.append(dict(CPU=pc,old_hex=before.hex(),new_hex=data.hex()))
    bank=bytearray(raw[16+65*8192:16+66*8192])
    needle=bytes([32])+ol['CoCheckCode'].to_bytes(2,'little')
    refs=[i for i in range(8190)if bank[i:i+3]==needle and not 0xe00<=i<0x1013 and not 0x800<=i<0x849]
    assert refs==[manifest['selector_labels']['PrFamily']-0xa000+33]or len(refs)==1,refs
    for i in refs:bank[i+1:i+3]=labels['CoCheckCode'].to_bytes(2,'little')
    for row in [9,14,34]:
        i=0x108c+3*row;assert bank[i:i+3]==bytes.fromhex('4c40a7')
        bank[i:i+3]=bytes([76])+labels['CoNativePrimitive'].to_bytes(2,'little')
    raw[16+65*8192:16+66*8192]=bank
    return old,dict(old,raw=bytes(raw)),route,q,manifest,ol,labels,patches,refs


def main():
    dst=O/'shared-auth-v76-funding.json';assert not dst.exists()
    old,new,route,q,manifest,ol,nl,patches,refs=build()
    result=dict(passed=True,source_fit_only=True,CPU_qualified=False,candidate_allowed=False,
        ROM_written=False,shared_sources_mutated=False,new_RAM_used=False,cache_used=False,
        canonical_input='DK79 source-only proposal over Prince130/cf7; no positive149 assumption',
        extents=dict(manager=[0xae00,0xb013],extra=[0xab72,0xabce],Sh_auth=[0xa800,0xa849]),
        unchanged_15B_manager_end_padding=[0xb004,0xb013],both_existing_cookie_addresses_and_bytes_unchanged=True,
        source_funding_bytes=dict(full_auth_helper=5,cold_guard_branches=6,live_header_copy_X=6,
            zero_page_wrap_save=2,reused_cookie_index=7,redundant_cold_SEC=1,redundant_header_SEC=1,declared_two_EA_bytes=2),
        helper_primitive_shared_tails_bytes=30,unchanged_public_Sh_retire=0xa849,
        old_labels=ol,new_labels=nl,selector_auth_reference=refs,patches=patches,
        remaining=['Current exact source caller/ABI proofs for ShCheckCode raw36-only, its current cookie and every moved internal symbol.',
            'Four-owner cold/fault/readback/retirement, Sh header and foreign public ABI, genuine IRQ/FF/nested cuts.',
            'Merge pending Prince153/DK89 source payload/cookie changes without assuming additive spare bytes.',
            'No ROM or native packet until root reviews this source-only factor and complete qualifications.'],
        bindings={p.relative_to(R).as_posix():sha(p)for p in [Path(__file__),Path(F.__file__),
            O/'full-auth-v73-measurement.json',F.D.O/'native-owner-proposal-v79.json',
            R/'tools/reference/shinobi_resident_loader_1101_v1.inc',O/'shared-auth-v76-Sh-reproduce.s',
            O/'shared-auth-v76-Sh-reproduce.bin',O/'shared-auth-v76.s',O/'shared-auth-v76.bin',
            O/'shared-auth-v76-extra.bin',O/'shared-auth-v76-Sh.bin',O/'shared-auth-v76.lbl']})
    dst.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k]for k in ['passed','extents','source_funding_bytes','unchanged_15B_manager_end_padding']}))


if __name__=='__main__':main()
