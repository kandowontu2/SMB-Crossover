"""Distinct combined canonicalPrince159/DK90 resident storage measurement.

No shared writes, cartridge, menu admission or new allocation is performed.
"""
import json
import re
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A
import prepare_prince_backdrop_manifest_1103_v159 as PR

R,O=A.R,A.O


def main():
    base,parent=PR.image();assert A.sha(base['raw'])=='b303e4451694cf5c8555eb53b268adfe17bed37fc9bd6207bc8b5c9f56b5b82d'
    frozen=json.loads((O/'native-owner-proposal-v90.json').read_text())
    cookie=(O/'native-cookie-v90.bin').read_bytes();payload=(O/'native-payload-v90.bin').read_bytes()
    selector=(PR.O/'post-selector-v153.s').read_text()
    copy_at=selector.index('\nPrCopyLive:\n');old_live=selector[copy_at:];selector=selector[:copy_at]
    selector=selector.replace('cmp #3\n bcc PrOdd','cmp #4\n bcc PrOdd')
    assert selector.count('cmp #39\n beq PrOddBB')==1
    selector=selector.replace('cmp #39\n beq PrOddBB','cmp #37\n bne PrOddBB')
    for before,after in [('jcc ShDispatchNo','bcc DkLocalNo'),('jne ShDispatchNo','bne DkLocalNo'),('jcs ShDispatchNo','bcs DkLocalNo')]:selector=selector.replace(before,after)
    selector=selector.replace('PrSh:\n','DkLocalNo:\n jmp ShDispatchNo\nPrSh:\n')
    selector=selector.replace('ExForeignLo:\n','''.export PrFamily,DkCookie,DkDescriptorData,DkCopyDescriptor
DkCookie:
 .incbin "'''+(O/'native-cookie-v90.bin').as_posix()+'''"
 .res $9a-(*-ExDispatch),$ea
ExForeignLo:
''')
    selector+='''
DkDescriptorData:
 .byte 2,0,9,$d0,$c0,3,$c1,3
DkCopyDescriptor:
 ldy #7
:
 lda DkDescriptorData,y
 sta $dfe0,y
 dey
 bpl :-
 rts
'''
    scfg='MEMORY{S:start=$a740,size=$b2,file=%O;}SEGMENTS{EX_SELECT:load=S,type=ro;}'
    sb,SL=A.assemble('native-combined-selector-v101',selector,scfg)
    assert len(sb)==176 and SL['ExForeignLo']==0xa7da
    owner=(PR.O/'post-owner-v159.s').read_text()
    owner=re.sub(r'^PrCopyLive=\$[0-9a-f]+\n','',owner,count=1)
    owner=f'DkDescriptor=$dfe0\nDkCookie=${SL["DkCookie"]:04x}\nDkCopyDescriptor=${SL["DkCopyDescriptor"]:04x}\n'+owner
    def once(before,after):
        nonlocal owner
        assert owner.count(before)==1,(before,owner.count(before));owner=owner.replace(before,after)
    once('cmp #3\n bcs CoSelectNo','cmp #4\n bcs CoSelectNo')
    once(' jsr CoSelect\n jsr PrTypedWorker\n .res 15,$ea',''' jsr CoSelect
 lda SelectedCharacter
 eor #40
 bne :+
 jsr DkCopyDescriptor
:
 jsr PrTypedWorker''')
    tables=[]
    for name,value in [('CoCookieLo','<DkCookie'),('CoCookieHi','>DkCookie'),('CoDescriptorLo','<DkDescriptor'),('CoDescriptorHi','>DkDescriptor')]:
        match=re.search('^'+name+r':\.byte [^\n]+\n',owner,re.M);assert match,name
        tables.append(match[0].rstrip()+','+value+'\n');owner=owner[:match.start()]+owner[match.end():]
    start,end=owner.index('CoRetireOwners:\n'),owner.index('CoInvalidate:\n')
    original_retire=owner[start:end]
    owner=owner[:start]+'''CoRetireOwners:
 ldx #3
CoRetireLoop:
 txa
 pha
 jsr CoSelectIndex
 jsr CoCheckHeaders
 bcc CoRetireNext
 pla
 tax
 pha
 lda CoRetireLo,x
 beq CoRetireInvalidate
 sta FarcallJmpTarget_SMC+1
 lda CoRetireHi,x
 sta FarcallJmpTarget_SMC+2
 lda #2
 sta CurrentBankC
 sta $5116
 sta SafecallA_SMC+1
 lda #3
 jsr FarCallCommon
CoRetireInvalidate:
 jsr CoInvalidate
CoRetireNext:
 pla
 tax
 dex
 bpl CoRetireLoop
 jmp ShRetire
'''+owner[end:]
    start,end=owner.index('PrRetire:\n'),owner.index('PrCookie:\n')
    original_private_retire=owner[start:end];owner=owner[:start]+'PrRetire=CoRetireOwners\n'+owner[end:]
    once(' beq PrWorkerPrince\n rts\nPrWorkerPrince:', ' beq PrWorkerPrince\n eor #14 ;38xor40, retains successful common carry\n bne PrWorkerDone\nPrWorkerPrince:')
    # Both typed boots shareD25E. OnlyPrince then runs its realC2 installer;
    # DK returns sourceboot's success without executing unrelated C766.
    installer=(PR.O/'native-installer-v153.s').read_text()
    assert 'PpInstallLive:\n ldy #52\nCopy:\n lda $c200,y\n sta $bfa3,y' in installer
    assert old_live.startswith('\nPrCopyLive:\n sta $016a\n lda #<$c766\n')
    live='''PrCopyLive:
 lda SelectedCharacter
 eor #38
 bne PrCopyLiveDone
 ; C766 firstLDY52/thenLDA packet: incomingA is dead. Native cold frame
 ; retains original publicAXYP and savedSMC; no redundant STA016A here.
 lda #<$c766
 sta $016c
 lda #>$c766
 sta $016d
 lda #3
 jsr $015a
PrCopyLiveDone:
 rts
'''
    once('CoSmc:\n',live+'CoSmc:\n')
    once('PrExtraEnd:\n',''.join(tables)+'CoRetireLo:.byte 0,<PrNativeRetire,<BbNativeRetire,<$d60c\nCoRetireHi:.byte 0,>PrNativeRetire,>BbNativeRetire,>$d60c\nPrExtraEnd:\n')
    # Source-backed structural cold/header factors from v76. Full auth helper
    # still savesR3..6, every complete header is compared on every call. The
    # generic retirement owns allR0..7, so shared full descriptor selection
    # may clobberR3/R4 before the existing outer frame restores them.
    once(' jsr CoCheckHeaders\n bcc CoColdBegin\n jmp CoYes\n',' jsr CoCheckHeaders\n bcs CoYes\n')
    once('CoGuardNo:\n jmp CoNo\nCoColdBegin:\n','CoColdBegin:\n')
    once('CoColdMode:\n','CoGuardNo:\n jmp CoNo\nCoColdMode:\n')
    once('CoColdMode:\n jsr CoSelect\n jcc CoNo\n','CoColdMode:\n jsr CoSelect\n bcc CoGuardNo\n')
    assert owner.count(' ldx CurrentBankC\n dex\n cpx #1\n')==2
    owner=owner.replace(' ldx CurrentBankC\n dex\n cpx #1\n',' dex\n cpx #1\n')
    once(' bne CoCheckBank\n sec\n bcs CoHeadersRestore\n',' bne CoCheckBank\n bcs CoHeadersRestore\n')
    once(' ldx #0\n:\n lda R0,x\n pha\n inx\n cpx #8\n bne :-\n',' ldx #$f8\n:\n lda R0+8,x\n pha\n inx\n bne :-\n')
    once(' tax\n lda CoCookieLo,x\n',' tax\nCoSelectIndex:\n lda CoCookieLo,x\n')
    once(' .res 2,$ea\nCoExCookie:','CoExCookie:')
    once('CoOwnerEnd:\n',' .if (*-CoCold)<$213\n .res $213-(*-CoCold),$ea\n .endif\nCoOwnerEnd:\n')
    owner='.export CoRetireOwners,CoSelectIndex,PrCopyLive,PrCopyLiveDone,CoRetireLo,CoRetireHi\n'+owner
    cfg='MEMORY{M:start=$ae00,size=$400,file=%O;X:start=$ab72,size=$100,file="'+(O/'native-combined-extra-v101.bin').as_posix()+'";}SEGMENTS{COMMON_OWNER_PROPOSAL:load=M,type=ro;PR_EXTRA:load=X,type=ro;}'
    ob,OL=A.assemble('native-combined-owner-v101',owner,cfg)
    extra=(O/'native-combined-extra-v101.bin').read_bytes()
    selector=re.sub(r'CoCheckCode=\$[0-9a-f]+','CoCheckCode=$%04x'%OL['CoCheckCode'],selector)
    sb,SL2=A.assemble('native-combined-selector-v101',selector,scfg);assert SL==SL2
    fits=len(ob)<=531 and len(extra)<=98 and len(sb)<=178
    raw=bytearray(base['raw']);patches=[]
    if fits:
        for pc,data,role in [(0xae00,ob,'CombinedPrince159+DK90 source-funded cold/header/retire and guarded liveinstaller'),(0xab72,extra,'Shared two typed boot/copy outcomes and four-owner address tables'),(0xa740,sb,'Pinned foreignUI/local-reject selector;DKcookie andscratchdescriptor')]:
            at=16+65*8192+pc-0xa000;before=raw[at:at+len(data)];raw[at:at+len(data)]=data
            patches.append(dict(physical_PRG=65,CPU_half_open=[pc,pc+len(data)],file_offset=at,old_hex=before.hex(),new_hex=data.hex(),role=role))
        for index,page in enumerate(A.CODE+A.ART):
            at=1048592+page*1024;data=payload[index*1024:(index+1)*1024];before=raw[at:at+1024];raw[at:at+1024]=data
            patches.append(dict(physical_CHR=page,file_offset=at,old_hex=before.hex(),new_hex=data.hex(),role='Unchangedfrozen90DK private11carrier payload'))
        # Keep the two explicitly granted DK native gates, rebound against
        # identical cf7/Prince159 preimages, but leave scene/menu blocked.
        for row in frozen['patches']:
            if row.get('grant')!='docs/qa/allocations/dkjr-shared-gates-1103-v104.json':continue
            at=row['file_offset'];before,after=bytes.fromhex(row['old_hex']),bytes.fromhex(row['new_hex'])
            assert raw[at:at+len(before)]==before;raw[at:at+len(after)]=after;patches.append(row)
    out=dict(passed=fits,measured=True,qualified=False,ROM_written=False,shared_source_written=False,native_owner_admitted=False,
        canonical_in_progress_Prince='build/prince-actor-1101-v1/backdrop-manifest-v159.json',parent_memory_SHA256=A.sha(base['raw']),
        expected_memory_only_SHA256=A.sha(raw)if fits else None,Prince_cookie=parent['Prince_cookie'],Bub_cookie=parent['Bub_cookie'],DK_cookie=cookie.hex(),
        manager_bytes=len(ob),manager_spare=531-len(ob),extra_bytes=len(extra),extra_spare=98-len(extra),selector_bytes=len(sb),selector_spare=178-len(sb),
        manager_labels=OL,selector_labels=SL,patches=patches,
        source_funding=dict(retirement='Genericfour-entry loop/PrRetirealias and movefour oldtables into reclaimed privatePrRetire body; previous79 pattern, independently rebased159.',
            liveinstaller='Move19B selectorcopy leaf into manager, guard exact38 vs40, remove3B dead incomingA store; C766firstLDY52 thenLDA sourcepacket provesAdeaddeadbeforeuse.',
            cold_header='Existing v76 structural branch/R0push/headerloop/redundantSEC factors; retirement reuses full CoSelectIndex under outerR0..7save. No fullauth elision/cache/Sh A800 rewrite.',
            source_extents=['Existing531B AE00..B013','Existing98B AB72..ABD4','Existing178B A740..A7F2, ExForeignLo fixedA7DA']),
        original_retire_source=original_retire,original_private_retire_source=original_private_retire,original_copy_source=old_live,
        required=['In-progress159 may still change:freeze/rebind finalPrince/currentBub before approval','Completeall4cold/16transitions/headers/readback/failure/retire/stateABI on this exact memory model','Everyforeignpublic/nativeingress/SMC/maps/IRQ/FF/nested and liveinstallerpacketlifetime','Rootexactsharedspan grant plus native scene40/menu proof before any cartridge'],
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in [Path(__file__),Path(PR.__file__),PR.O/'backdrop-manifest-v159.json',PR.O/'post-owner-v159.s',PR.O/'post-owner-v159.bin',PR.O/'post-owner-extra-v159.bin',PR.O/'post-selector-v153.s',PR.O/'post-selector-v153.bin',PR.O/'native-installer-v153.s',O/'native-owner-proposal-v90.json',O/'native-payload-v90.bin',O/'native-cookie-v90.bin',O/'native-combined-owner-v101.s',O/'native-combined-owner-v101.bin',O/'native-combined-extra-v101.bin',O/'native-combined-selector-v101.s',O/'native-combined-selector-v101.bin']})
    (O/'native-combined-owner-v101-measurement.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k]for k in ['passed','manager_bytes','manager_spare','extra_bytes','extra_spare','selector_bytes','selector_spare','expected_memory_only_SHA256']}))


def image():
    q=json.loads((O/'native-combined-owner-v101-measurement.json').read_text());assert q['passed']
    for rel,digest in q['bindings'].items():assert A.sha((R/rel).read_bytes())==digest,rel
    base,_=PR.image();raw=bytearray(base['raw']);assert A.sha(raw)==q['parent_memory_SHA256']
    for row in q['patches']:
        at=row['file_offset'];before,after=bytes.fromhex(row['old_hex']),bytes.fromhex(row['new_hex'])
        assert raw[at:at+len(before)]==before;raw[at:at+len(after)]=after
    assert A.sha(raw)==q['expected_memory_only_SHA256'];return dict(base,raw=bytes(raw)),q


if __name__=='__main__':main()
