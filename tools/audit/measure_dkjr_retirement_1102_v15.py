"""Four-owner retire factor in existing source-owned PRG65 spans only.

Builds and tests private memory images. No shared file, cartridge, menu or
allocation changes are made by this measurement.
"""
import copy,json,re
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A
import check_hogan_current_bounded_v1 as N
R=A.R;O=A.O;W=A.W


def main():
    p=json.loads((O/'admission-proposal-v11.json').read_text());assert p['passed']
    hp=O/'hit-freeze-v12-CPU.json';h=json.loads(hp.read_text());assert h['passed']
    H={n:int(v,16)for v,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',(O/'hit-freeze-v12.lbl').read_text(),re.M)}
    source=(O/'admission-owner-v11.s').read_text()
    # CoWorker's success carry must survive the typed-owner discriminator.
    # The inherited CMP#38/BNE accidentally cleared it for successfulEx37.
    old=' cmp #38\n bne PrWorkerDone\nDkSharedBoot:'
    new=' cmp #38\n beq DkSharedBoot\n sec\n rts\nDkSharedBoot:'
    assert source.count(old)==1;source=source.replace(old,new)
    arrays=[]
    for name in ['CoCookieLo','CoCookieHi','CoDescriptorLo','CoDescriptorHi']:
        match=re.search('^'+name+r':\.byte [^\n]+\n',source,re.M);assert match
        arrays.append(match[0]);source=source[:match.start()]+source[match.end():]
    start=source.index('CoRetireOwners:\n');end=source.index('CoInvalidate:\n',start)
    old_body=source[start:end]
    source=source[:start]+'''CoRetireOwners:
 ldx #3
CoRetireLoop:
 txa
 pha
 lda CoCookieLo,x
 sta R5
 lda CoCookieHi,x
 sta R6
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
'''+source[end:]
    start=source.index('PrRetire:\n');end=source.index('PrCookie:\n',start);old_private=source[start:end]
    source=source[:start]+'PrRetire=CoRetireOwners\n'+source[end:]
    source=source.replace('CoOwnerEnd:\n',' .res $213-(*-CoCold), $ea\nCoOwnerEnd:\n')
    assert source.count('PrExtraEnd:\n')==1
    data=''.join(arrays)+'CoRetireLo:.byte 0,<PrNativeRetire,<BbNativeRetire,<$%04x\nCoRetireHi:.byte 0,>PrNativeRetire,>BbNativeRetire,>$%04x\n'%(H['DkHitThaw'],H['DkHitThaw'])
    source=source.replace('PrExtraEnd:\n',data+'PrExtraEnd:\n')
    source=' .export CoRetireOwners,CoRetireLoop,CoRetireLo,CoRetireHi\n'+source
    cfg='MEMORY{M:start=$ae00,size=$213,file=%O;X:start=$ab72,size=$62,file="'+(O/'retire-extra-v15.bin').as_posix()+'";}SEGMENTS{COMMON_OWNER_PROPOSAL:load=M,type=ro;PR_EXTRA:load=X,type=ro;}'
    manager,L=A.assemble('retire-owner-v15',source,cfg);extra=(O/'retire-extra-v15.bin').read_bytes()
    assert len(manager)==531 and len(extra)<=98
    selector=(O/'admission-selector-v11.s').read_text();selector=re.sub(r'CoCheckCode=\$[0-9a-f]+','CoCheckCode=$%04x'%L['CoCheckCode'],selector)
    sb,SL=A.assemble('retire-selector-v15',selector,'MEMORY{S:start=$a740,size=$b2,file=%O;}SEGMENTS{EX_SELECT:load=S,type=ro;}')
    assert len(sb)==175
    # All full real actor payloads come from the already granted Prince v54
    # memory-only proposal over exact16a9. No proposed new Prince successor is
    # silently substituted, and no cartridge is emitted.
    pp=R/'build/prince-actor-1101-v1/sunny-rebase-manifest-v54.json';prior=json.loads(pp.read_text());raw=bytearray(A.BASE.read_bytes());assert A.sha(raw)==A.PIN
    patches=prior['patches']
    for x in patches:
        at=x['file_offset'];old=bytes.fromhex(x['old_hex']);new=bytes.fromhex(x['new_hex']);assert bytes(raw[at:at+len(old)])==old
        raw[at:at+len(new)]=new
    assert A.sha(raw)==prior['expected_memory_only_SHA256']
    b=W.scoped_load(R/'build/excitebike-pose-1101-v3/current4.nes')
    def bundle(parts):
        out=bytearray(raw)
        for pc,data in parts:
            at=16+65*8192+pc-0xa000;out[at:at+len(data)]=data
        result=copy.deepcopy(b);result['raw']=bytes(out)
        return result
    before=bundle([(0xae00,(O/'admission-owner-v11.bin').read_bytes()),(0xab72,(O/'admission-owner-extra-v11.bin').read_bytes()),(0xa740,(O/'admission-selector-v11.bin').read_bytes())])
    after=bundle([(0xae00,manager),(0xab72,extra),(0xa740,sb)])
    oldlabels={n:int(v,16)for v,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',(O/'admission-owner-v11.lbl').read_text(),re.M)}
    def symbols(bb,labels):
        for name in ['CoCold','CoRetire','CoCheckCode']:
            seg='DK_retire_'+name;bb['segs'][seg]=dict(start=str(labels[name]),ooffs=str(16+65*8192+labels[name]-0xa000));bb['syms'][name]=dict(val=str(labels[name]),seg=seg)
    symbols(before,oldlabels);symbols(after,L)
    def cold(bb,owner):
        m=N.Bus(bb);m.raw_page(2,2)
        N.put(m,CurrentBank=0xd7,CurrentBankC=2,SelectedCharacter=owner,OperMode=1,FamilyMainCommit=1,DisableScreenFlag=1,Mirror_PPUMASK=0,NmiDisable=255,Mirror_PPUCTRL=0xa0,ReloadCHRBank=0)
        target=W.address(bb,'CoCold')
        m[W.address(bb,'SafecallA_SMC')+1]=0x55;m[W.address(bb,'FarcallJmpTarget_SMC')+1]=target&255;m[W.address(bb,'FarcallJmpTarget_SMC')+2]=target>>8
        c=N.NesMPU(memory=m,pc=W.address(bb,'FarCallCommon'));c.a,c.x,c.y,c.p,c.sp=0xc1,7,91,0x31,224;c.stPushWord(0x5aff);low=224
        for _ in range(2000000):
            if c.pc==0x5b00:break
            low=min(low,c.sp);assert m[c.pc]!=0,('cold BRK',owner,hex(c.pc));c.step()
        else:raise AssertionError(('full cold instruction bound',owner,hex(c.pc)))
        z=dict(A=c.a,X=c.x,Y=c.y,P=c.p,CPU=c.processorCycles,minimum_SP=low);assert c.sp==224 and z['P']&1,(owner,z)
        return m,z
    negative=N.Bus(before);negative.raw_page(2,2)
    N.put(negative,CurrentBank=0xd7,CurrentBankC=2,SelectedCharacter=37,OperMode=1,FamilyMainCommit=1,DisableScreenFlag=1,Mirror_PPUMASK=0,NmiDisable=255,Mirror_PPUCTRL=0xa0,ReloadCHRBank=0)
    rejected=N.invoke(negative,'CoCold');assert not rejected['P']&1
    inherited_negative=dict(owner=37,CPU=rejected['CPU'],P=rejected['P'],cause='Successful commonworker carry is cleared by inherited CMP#38 on raw37 before BNE/RTS. Installed16a9 does not contain this private Prince wrapper.',exact_original_source='CoFar CoWorker,$fb / BCC PrWorkerDone / LDA SelectedCharacter / CMP#38 / BNE PrWorkerDone')
    cases=[];flags_preserved=0;cold_cases=[]
    for owner in [37,38,39]:
        m,z=cold(after,owner);cold_cases.append(dict(owner=owner,CPU=z['CPU'],P=z['P']))
        # Once truly loaded, old/new retire execute genuine owner code.
        # Save real source bytes and compare complete native/overlay state.
        for foreign in [0,28,36,37,38,39,40,255]:
            for cbank in [0,2]:
                a=N.fork(m);n=N.fork(m);a.bundle=before;n.bundle=after
                # Rebind all active mapped ROM windows to the new resident.
                for mm in [a,n]:
                    for win,tag in enumerate(list(mm.rawtags)):
                        if tag&128:mm.raw_page(win,tag)
                for mm in [a,n]:N.put(mm,SelectedCharacter=foreign,CurrentBankC=cbank);mm.raw_page(2,cbank)
                za=N.invoke(a,'CoRetire',a=0x51,x=4,y=0x73,p=0xf1);zn=N.invoke(n,'CoRetire',a=0x51,x=4,y=0x73,p=0xf1)
                assert (za['A'],za['X'],za['Y'],za['P'])==(zn['A'],zn['X'],zn['Y'],zn['P'])and (za['A'],za['X'],za['Y'])==(0x51,4,0x73),(owner,foreign,cbank,za,zn)
                assert a.rawtags==n.rawtags and bytes(a[:0x100])+bytes(a[0x1e0:0x800])==bytes(n[:0x100])+bytes(n[0x1e0:0x800])
                assert all(bytes(a.ram[i])==bytes(n.ram[i])for i in range(4)),(owner,foreign,cbank,'owner state')
                assert bytes(a[0x15a:0x17b])==bytes(n[0x15a:0x17b])
                assert a.ram[2][0x1fe0]==a.ram[3][0x1fe0]==n.ram[2][0x1fe0]==n.ram[3][0x1fe0]==0
                cases.append(dict(owner=owner,foreign=foreign,entry_C=cbank,old_CPU=za['CPU'],new_CPU=zn['CPU'],AXYP_maps_all_RAM_SMC_exact=True))
    # NewDK headers authenticate the171B true native-field thaw leaf. This
    # fixture invokes the common before-overwrite retire, even after selecting
    # a foreign owner, with all six exact positive boundary flags retained.
    helper=(O/'hit-freeze-v12.bin').read_bytes();cookie=sb[SL['DkCookie']-0xa740:SL['DkCookie']-0xa740+16]
    dk=[]
    for foreign,cbank in [(0,0),(28,2),(36,0),(37,2),(38,0),(39,2),(40,0),(255,2)]:
        mm=N.Bus(after);N.put(mm,CurrentBank=0xd7,CurrentBankC=cbank,SelectedCharacter=foreign)
        mm.raw_page(2,cbank);mm.ram[2][0x1540:0x1540+len(helper)]=helper
        for bank in [2,3]:mm.ram[bank][0x1fe0:0x1ff0]=cookie
        for i,flag in enumerate([1,2,7,16,64,127]):
            for at,value in [(0x440,1),(0x446,flag),(0x44c,9 if i%2 else 6),(0x452,20+i)]:mm.ram[2][at+i]=value
            mm[W.address(after,'Enemy_Flag')+i]=0x80|i;mm[W.address(after,'Enemy_ID')+i]=0 if i%2 else 6
        z=N.invoke(mm,'CoRetire',a=0x51,x=4,y=0x73,p=0xf1)
        for i,flag in enumerate([1,2,7,16,64,127]):
            assert mm[W.address(after,'Enemy_Flag')+i]==flag and mm[W.address(after,'Enemy_ID')+i]==(9 if i%2 else 6)
            flags_preserved+=1
        assert not any(mm.ram[2][0x440:0x446])and mm.ram[2][0x1fe0]==mm.ram[3][0x1fe0]==0
        start=len(mm.writes);N.invoke(mm,'CoRetire');assert not any(W.address(after,'Enemy_Flag')<=at<W.address(after,'Enemy_Flag')+6 for at,_ in mm.writes[start:])
        dk.append(dict(foreign=foreign,entry_C=cbank,CPU=z['CPU'],all_six_fields_once=True,second_retire_no_native_flag_writes=True))
    out=dict(passed=True,proposal_only=True,ROM_written=False,shared_source_written=False,base_SHA256=A.PIN,reference_private_Prince_SHA256=prior['expected_memory_only_SHA256'],
        manager_bytes=len(manager),manager_span=[0xae00,0xb013],extra_bytes=len(extra),extra_span=[0xab72,0xab72+len(extra)],selector_bytes=len(sb),selector_span=[0xa740,0xa740+len(sb)],source_funding='Replace three repeated owner-specific header/retire bodies by one authenticated four-entry loop. Move existing16B cookie/descriptor address tables into the freed30B privatePrinceRetire body. Public CoRetire/CoCold/CoCheckCode and all veneers remain source-bound; old privatePrRetire has no surviving call and aliases the common before-overwrite seam.',
        old_main_retire_source_bytes=old_body,old_private_retire_source_bytes=old_private,inherited_Ex37_private_cold_negative=inherited_negative,new_successful_actual_cold_owners=cold_cases,legacy_real_owner_retirement_cases=cases,new_DK_real_private_thaw_cases=dk,new_DK_exact_flags_restored=flags_preserved,
        expected_allocations='Existing granted privatePrince65 spans only; no new area or shared RAM grant inferred. Current16a9, pendingBub9cf370B and privatePrincev64 ingress must compose disjointly only after root review.',
        remaining=['Full real IRQ/lagNMI cuts of changed four-owner auth/retire/control frames.','Final payload-derivedDKcookie, complete public service vectors/native actor constructor and sourceAI freeze inclmisc/firebars.','Exact frontend Select-state/name/portrait/pending/Start funding and actual menu admission.'],
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in[Path(__file__),A.BASE,pp,O/'admission-proposal-v11.json',O/'admission-owner-v11.s',hp,O/'hit-freeze-v12.bin',O/'retire-owner-v15.s',O/'retire-owner-v15.bin',O/'retire-extra-v15.bin',O/'retire-selector-v15.s',O/'retire-selector-v15.bin']})
    (O/'retirement-proposal-v15.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k]for k in ['passed','manager_bytes','extra_bytes','selector_bytes','new_DK_exact_flags_restored']}))


if __name__=='__main__':main()
