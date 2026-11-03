"""Measure combined101 full-auth Sh/Bub primitives; no cartridge permission."""
import itertools,json,re
from pathlib import Path
import measure_dkjr_prince_owner_1103_v101 as D
import check_bub_complete_auth_ingress_1103_v82 as P

R,O,N,Q,address,sha=P.R,P.O,P.N,P.Q,P.address,P.sha
L=P.P.P.F.L


def build():
    old,manifest=D.image()
    root=D.O
    src=(root/'native-combined-owner-v101.s').read_text()
    cfg='MEMORY{M:start=$ae00,size=$213,file=%O;X:start=$ab72,size=$62,file="'+(O/'combined-auth-v83-extra.bin').as_posix()+'";S:start=$a800,size=$49,file="'+(O/'combined-auth-v83-Sh.bin').as_posix()+'";}SEGMENTS{COMMON_OWNER_PROPOSAL:load=M,type=ro;PR_EXTRA:load=X,type=ro;SH_SHARED_AUTH:load=S,type=ro;}'
    begin,end=src.index('CoCheckCode:\n'),src.index('CoCheckHeaders:\n')
    assert src[begin:end].count(' jsr CoSelect\n')==1
    assert src[begin:end].count(' sta R3,x\n')==1
    src=src[:begin]+'''CoCheckCode:
 lda SelectedCharacter
 sec
 sbc #37
 cmp #4
 bcs CoSelectNo
 tax
CoCheckIndex:
 lda R5
 pha
 lda R6
 pha
 jsr CoSelectCookieIndex
 jsr CoCheckHeaders
 pla
 sta R6
 pla
 sta R5
 rts

CoSelect:
 lda SelectedCharacter
 sec
 sbc #37
 cmp #4
 bcs CoSelectNo
 tax
CoSelectIndex:
 jsr CoSelectCookieIndex
 lda CoDescriptorLo,x
 sta R3
 lda CoDescriptorHi,x
 sta R4
 rts
CoSelectCookieIndex:
 lda CoCookieLo,x
 sta R5
 lda CoCookieHi,x
 sta R6
 sec
 rts
CoSelectNo:
 clc
 rts

'''+src[end:]
    before='CoPublishChr:\n CoFar X5PublishChr,Bank_X5PublishChr\n rts\n'
    assert src.count(before)==1
    src=src.replace(before,'''CoPublishChr:
 sta SafecallA_SMC+1
 lda #<X5PublishChr
 sta FarcallJmpTarget_SMC+1
 lda #>X5PublishChr
 sta FarcallJmpTarget_SMC+2
 lda #Bank_X5PublishChr
 jmp FarCallCommon
''')
    for name,suffix in [('CoCookieLo','<$aa78'),('CoCookieHi','>$aa78')]:
        match=re.search('^'+name+r':\.byte [^\n]+\n',src,re.M);assert match
        src=src[:match.start()]+match[0].rstrip()+','+suffix+'\n'+src[match.end():]
    mark=' .if (*-CoCold)<$213\n'
    assert src.count(mark)==1
    src=src.replace(mark,'''CoExistingDataEnd:
CoNativeSide:
 pla
 tay
 pla
 tax
 pla
 plp
 jmp $958b
CoDataEnd:
'''+mark)
    sh=(O/'shared-auth-v76.s').read_text().split('.segment "SH_SHARED_AUTH"',1)[1]
    sh='.segment "SH_SHARED_AUTH"'+sh
    before='''ShCheckCode:
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
'''
    after='''ShCheckCode:
 php
 pha
 txa
 pha
 tya
 pha
 lda SelectedCharacter
 cmp #36
 bne CoNativeNo
 ldx #4
 jsr CoCheckIndex
'''
    assert sh.count(before)==1
    sh=sh.replace(before,after).replace('.export CoCheckShCookie,CoNativeSide,CoShNoPartial,CoAuthKnownCookie',
        '.export CoCheckIndex,CoSelectCookieIndex,CoNativeSide,CoExistingDataEnd,CoDataEnd,CoExCookie,CoBBCookie')
    sh=sh.replace('ShFastEnd:\n',' .res $49-(*-ShCheckCode),$ea\nShFastEnd:\n')
    labels=L.assemble('combined-auth-v83',src+sh,cfg)
    manager=(O/'combined-auth-v83.bin').read_bytes();extra=(O/'combined-auth-v83-extra.bin').read_bytes();shcode=(O/'combined-auth-v83-Sh.bin').read_bytes()
    assert (len(manager),len(extra),len(shcode))==(531,97,73)
    oldlabels=manifest['manager_labels']
    bound=json.loads((root/'native-combined-padding-v108.json').read_text())
    assert bound['passed']and bound['compiled_code_data_end']==0xb002
    assert labels['CoExistingDataEnd']==0xb002 and labels['CoDataEnd']==0xb00b
    assert labels['CoSmc']==oldlabels['CoSmc']==0xafdd
    assert labels['CoExCookie']==0xafe2 and labels['CoBBCookie']==0xaff2
    assert manager[0x1e2:0x202]==(root/'native-combined-owner-v101.bin').read_bytes()[0x1e2:0x202]
    assert manager[0x20b:]==bytes([234])*8
    assert labels['CoCold']==0xae00 and labels['CoRetire']==0xae0b
    assert labels['ShFastEnd']==0xa849
    selector=(root/'native-combined-selector-v101.s').read_text()
    selector,count=re.subn(r'CoCheckCode=\$[0-9a-f]+','CoCheckCode=$%04x'%labels['CoCheckCode'],selector)
    assert count==1
    scfg='MEMORY{S:start=$a740,size=$b2,file=%O;}SEGMENTS{EX_SELECT:load=S,type=ro;}'
    sl=L.assemble('combined-auth-v83-selector',selector,scfg)
    selected=(O/'combined-auth-v83-selector.bin').read_bytes()
    assert len(selected)==176 and sl['ExForeignLo']==0xa7da
    raw=bytearray(old['raw']);patches=[]
    for pc,blob in [(0xae00,manager),(0xab72,extra),(0xa740,selected),(0xa800,shcode)]:
        at=16+65*8192+pc-0xa000;before=bytes(raw[at:at+len(blob)]);raw[at:at+len(blob)]=blob
        patches.append(dict(CPU=pc,old_hex=before.hex(),new_hex=blob.hex()))
    for row in [9,14,34]:
        at=16+65*8192+0x108c+row*3
        assert raw[at:at+3]==bytes.fromhex('4c40a7')
        raw[at:at+3]=bytes([76])+labels['CoNativePrimitive'].to_bytes(2,'little')
    return old,dict(old,raw=bytes(raw)),manifest,labels,patches


def main():
    destination=O/'combined-auth-v83-measurement.json';assert not destination.exists()
    old,new,parent,labels,patches=build()
    route=P.P.P.F.C.bundle()[1]
    cases=[]
    for identity in [0,1]:
        for phase,keys in [('idle',0),('walk',1),('left',2),('jump',129),('bubble',64)]:
            pair=[Q.Q.fresh(bb,route,identity)for bb in [old,new]];outputs=[]
            for m in pair:
                Q.L.E.main_fields(m);out=[]
                for epoch in range(12):
                    held=keys&127|(128 if keys&128 and epoch==1 else 0)
                    N.put(m,FrameCounter=epoch,SavedJoypadBits=held,SavedJoypad1Bits=held,VRAM_Buffer1_Offset=0)
                    out.append(N.invoke(m,'GameCoreRoutine',a=85,x=0,y=0,p=0x31))
                outputs.append(out)
            P.P.parity(*pair,[x[-1]for x in outputs])
            for a,z in zip(*outputs):assert [a[k]for k in ['A','X','Y','P']]==[z[k]for k in ['A','X','Y','P']]
            before=sum(z['CPU']for z in outputs[0])/12;after=sum(z['CPU']for z in outputs[1])/12
            row=dict(identity=identity,phase=phase,baseline_CPU=before,proposal_CPU=after,saving_CPU=before-after)
            cases.append(row);print(json.dumps(row),flush=True)
    result=dict(passed=True,source_fit_only=True,CPU_qualified=False,candidate_allowed=False,ROM_written=False,
        cache_used=False,new_RAM_used=False,canonical_input='Exact combined101 Prince159/DK90 over current cf7',
        manager_bytes=531,extra_bytes=97,selector_bytes=176,Sh_auth_bytes=73,
        unchanged_cookie_addresses=[0xafe2,0xaff2],unchanged_cookie_bytes=True,
        source_funding=dict(generated101_footer=17,used_footer=9,footer_remaining=8,
            generic_auth_growth=1,cold_publisher_tail_JMP_saving=1,
            additional_Sh_cookie_table_bytes=2,Sh_early_AXYP_reject_saving=3,Sh_index_argument_bytes=2,
            Sh_new_footer_padding=1),
        Main_cases=cases,labels=labels,patches=patches,
        scope='Complete authentication on each call; Sh index4 is admitted only after exact Selected36 guard. Cold and retire descriptor table remains4records. Fixed Sh/public entries, current cookie locations/values and selector foreign table remain unchanged. CoPublishChr uses a genuine tail JMP through unchanged FarCallCommon, removing only its redundant JSR/RTS level. Footer placement is a source-only proposal, not a lease.',
        remaining=['Full combined101 cold/Fresh/retire/all-positive-and-reject/foreign/scratch/SMC/API/IRQ/FF/nested requalification, including wrong-owner deeper Sh reject frame and publisher tail unwind.',
            'Complete external reference closure and root exact private candidate permission before ROM/native.'],
        bindings={p.relative_to(R).as_posix():sha(p)for p in [Path(__file__),Path(P.__file__),
            D.O/'native-combined-owner-v101-measurement.json',D.O/'native-combined-padding-v108.json',
            D.O/'native-combined-owner-v101.s',D.O/'native-combined-owner-v101.bin',
            O/'combined-auth-v83.s',O/'combined-auth-v83.bin',O/'combined-auth-v83-extra.bin',
            O/'combined-auth-v83-Sh.bin',O/'combined-auth-v83-selector.s',O/'combined-auth-v83-selector.bin']})
    destination.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True,extents=[531,97,176,73],cookie_locations_unchanged=True)))


if __name__=='__main__':main()
