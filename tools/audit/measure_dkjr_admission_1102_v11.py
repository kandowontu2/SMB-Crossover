"""Private DK Jr admission/storage measurement; never writes a cartridge.

No raw ID, page, shared byte or RAM lifetime is granted by this receipt.  The
eight-row copier runs only in an explicitly isolated proposed-overlay fixture.
"""
import collections,hashlib,json,re,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import prepare_dkjr_native_world_1102_v3 as W
import check_hogan_current_bounded_v1 as N
O=R/'build/dkjr-native-source-1102-v2'
BASE=R/'build/sunny-growth-prelude-1102-v9/candidate.nes'
PIN='16a9de64b18370a03885ff503141fc08edd25f3bd026d480854a1754efa1490b'
CODE=[817,833,847,856,867,881,882,883]
ART=[959,960,961]
sha=lambda data:hashlib.sha256(data).hexdigest()


def assemble(stem,source,cfg):
    p=O/stem;p.with_suffix('.s').write_text(source);p.with_suffix('.cfg').write_text(cfg)
    cc=R/'tools/Windows/cc65/bin'
    for command in [[cc/'ca65.exe',p.with_suffix('.s'),'-o',p.with_suffix('.o')],
                    [cc/'ld65.exe','-C',p.with_suffix('.cfg'),p.with_suffix('.o'),'-o',p.with_suffix('.bin'),'-Ln',p.with_suffix('.lbl')]]:
        z=subprocess.run(list(map(str,command)),capture_output=True,text=True);assert z.returncode==0,z.stderr
    symbols={n:int(v,16)for v,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',p.with_suffix('.lbl').read_text(),re.M)}
    return p.with_suffix('.bin').read_bytes(),symbols


BOOT='''.setcpu "6502"
.segment "DK_COLD"
.export DkColdEntry,DkColdStart,DkCopyByte,DkVerifyByte,DkColdEnd,DkCodePages
R0=$03
R1=$04
R2=$05
; The existing common worker copied the two immutable helper rows to C2:D0/D4,
; cleared C000..C8FF and returned to the resident manager. Its typed farcall
; maps RAM3 in A000 before entering this code in the still-mapped RAM2 window.
; Forced blank, SEI, disabled NMI, both invalid headers and saved host context
; belong to that existing manager. R5/R6 (resident cookie pointer) survive.
DkColdEntry:
DkColdStart:
 lda #0
 sta R0
 sta R2
 lda #$a0
 sta R1
DkCopyRow:
 jsr DkMapRow
 ldx #4
DkCopyByte:
 lda $2007
 sta (R0),y
 iny
 bne DkCopyByte
 inc R1
 dex
 bne DkCopyByte
 lda R1
 sec
 sbc #4
 sta R1
 jsr DkMapRow
 ldx #4
DkVerifyByte:
 lda $2007
 cmp (R0),y
 bne DkColdNo
 iny
 bne DkVerifyByte
 inc R1
 dex
 bne DkVerifyByte
 inc R2
 lda R2
 cmp #8
 bne DkCopyRow
 sec
 rts
DkColdNo:
 clc
 rts
DkMapRow:
 lda R2
 asl
 tax
 lda DkCodePages+1,x
 sta $5130
 lda DkCodePages,x
 sta $5123
 ldy #0
 sty $5130
 bit $2002
 lda #$0c
 sta $2006
 sty $2006
 lda $2007
 rts
DkCodePages:
 .word '''+','.join(map(str,CODE))+'''
DkColdEnd:
'''


def main():
    raw=BASE.read_bytes();assert sha(raw)==PIN
    frozen=R/'docs/qa/checkpoints/2026-11-02/dkjr-native-body-v10/manifest.json'
    v10=json.loads(frozen.read_text());assert v10['component_bytes']==7848
    body=(O/'native-body-v10.bin').read_bytes();assert sha(body)==v10['component_SHA256']
    sunny=R/'docs/qa/checkpoints/2026-11-02/sunny-palette-v9/receipt.json'
    s=json.loads(sunny.read_text())
    # The passed Sunny successor has no CHR patches. Bind every actual current
    # byte rather than constructing a stale cumulative ROM.
    sunny_rows=s.get('patches',s.get('all_patches',[]))
    if not sunny_rows:
        for key,value in s.items():
            if isinstance(value,list)and value and isinstance(value[0],dict)and 'offset'in value[0]and 'new'in value[0]:sunny_rows=value;break
    assert len(sunny_rows)==5,list(s)
    for x in sunny_rows:
        at=x['offset'];new=bytes.fromhex(x['new']);assert raw[at:at+len(new)]==new
        assert at+len(new)<=1048592
    worker,L=assemble('admission-cold-v11',BOOT,'MEMORY{P:start=$d25e,size=$1a2,file=%O;}SEGMENTS{DK_COLD:load=P,type=ro;}')
    assert L['DkColdEntry']==0xd25e and L['DkColdEnd']<=0xd400
    # Source-only fourth-owner factor of the granted Prince three-owner
    # proposal. The four removed bytes are executed NOPs from an exact .res15,
    # not discovered padding. Their replacement tables preserve the531B span.
    pool=R/'build/prince-actor-1101-v1'
    source=(pool/'current-owner-v51.s').read_text()
    assert source.count('cmp #3\n bcs CoSelectNo')==1
    source=source.replace('cmp #3\n bcs CoSelectNo','cmp #4\n bcs CoSelectNo')
    assert source.count('.res 15,$ea')==1;source=source.replace('.res 15,$ea','.res 1,$ea')
    old=' jsr CoSelect\n jsr PrTypedWorker'
    new=' jsr CoSelect\n lda SelectedCharacter\n cmp #40\n bne :+\n jsr DkCopyDescriptor\n:\n jsr PrTypedWorker'
    assert source.count(old)==1;source=source.replace(old,new)
    source=source.replace('CoCookieLo:.byte <CoExCookie,<PrCookie,<CoBBCookie','CoCookieLo:.byte <CoExCookie,<PrCookie,<CoBBCookie,<DkCookie')
    source=source.replace('CoCookieHi:.byte >CoExCookie,>PrCookie,>CoBBCookie','CoCookieHi:.byte >CoExCookie,>PrCookie,>CoBBCookie,>DkCookie')
    source=source.replace('CoDescriptorLo:.byte <CoExDescriptor,<PrDescriptor,<CoBBDescriptor','CoDescriptorLo:.byte <CoExDescriptor,<PrDescriptor,<CoBBDescriptor,<DkDescriptor')
    source=source.replace('CoDescriptorHi:.byte >CoExDescriptor,>PrDescriptor,>CoBBDescriptor','CoDescriptorHi:.byte >CoExDescriptor,>PrDescriptor,>CoBBDescriptor,>DkDescriptor')
    old=' lda SelectedCharacter\n cmp #38\n bne PrWorkerDone\n CoFar PrColdBoot,3'
    new=' lda SelectedCharacter\n cmp #40\n beq DkSharedBoot\n cmp #38\n bne PrWorkerDone\nDkSharedBoot:\n CoFar PrColdBoot,3'
    assert source.count(old)==1;source=source.replace(old,new)
    source='DkDescriptor=$dfe0\nDkCookie=$a7cb\nDkCopyDescriptor=$a7e3\n.export CoSelect,CoCookieLo,CoCookieHi,CoDescriptorLo,CoDescriptorHi\n'+source
    cfg='MEMORY{M:start=$ae00,size=$213,file=%O;X:start=$ab72,size=$62,file="'+(O/'admission-owner-extra-v11.bin').as_posix()+'";}SEGMENTS{COMMON_OWNER_PROPOSAL:load=M,type=ro;PR_EXTRA:load=X,type=ro;}'
    manager,ML=assemble('admission-owner-v11',source,cfg)
    extra=(O/'admission-owner-extra-v11.bin').read_bytes();assert len(manager)==531 and len(extra)==96
    selector=(pool/'current-selector-v51.s').read_text()
    reference_selector=selector+'\n.export PrFamily\n'
    ref,RL=assemble('admission-selector-reference-v11',reference_selector,'MEMORY{S:start=$a740,size=$b2,file=%O;}SEGMENTS{EX_SELECT:load=S,type=ro;}')
    selector+='\n.export PrFamily\n'
    selector=re.sub(r'CoCheckCode=\$[0-9a-f]+','CoCheckCode=$%04x'%ML['CoCheckCode'],selector)
    selector=selector.replace('cmp #3\n bcc PrOdd','cmp #4\n bcc PrOdd')
    old=' cmp #39\n beq PrOddBB\n lda #$a5\n jmp PrSharedCall\nPrOddBB:\n lda #$a0'
    new=' cmp #39\n beq PrOddBB\n cmp #40\n beq PrOddBB\n lda #$a5\n jmp PrSharedCall\nPrOddBB:\n lda #$a0'
    assert selector.count(old)==1;selector=selector.replace(old,new)
    # All eight distant rejection branches share an exact local JMP. It adds
    # no flags/register/mapping change and funds21B in the same selector lease.
    hits=re.findall(r' (jcc|jne|jcs) ShDispatchNo',selector);assert len(hits)==8,hits
    selector=re.sub(r' (jcc|jne|jcs) ShDispatchNo',lambda m:' '+{'jcc':'bcc','jne':'bne','jcs':'bcs'}[m[1]]+' DkLocalNo',selector)
    selector=selector.replace('PrSh:\n','DkLocalNo:\n jmp ShDispatchNo\nPrSh:\n')
    # A placeholder cookie has the actual sixteen-byte owner/type shape. Its
    # digest is deliberately NOT an authentication claim for unfinished code.
    desc=bytes([2,0,9,0xd0])+b''.join(p.to_bytes(2,'little')for p in ART[1:]);assert len(desc)==8
    selector+='\n.export DkCookie,DkDescriptorData,DkCopyDescriptor\nDkCookie:\n .byte $a7,$28,$01,0,0,0,0,0,0,0,0,0,0,0,0,0\nDkDescriptorData:\n .byte '+','.join(map(str,desc))+'''\nDkCopyDescriptor:
 ldy #7
:
 lda DkDescriptorData,y
 sta $dfe0,y
 dey
 bpl :-
 rts
'''
    sb,SL=assemble('admission-selector-v11',selector,'MEMORY{S:start=$a740,size=$b2,file=%O;}SEGMENTS{EX_SELECT:load=S,type=ro;}')
    assert len(sb)==175 and SL['DkCookie']==0xa7cb
    source=re.sub(r'DkCopyDescriptor=\$[0-9a-f]+','DkCopyDescriptor=$%04x'%SL['DkCopyDescriptor'],source)
    manager,ML=assemble('admission-owner-v11',source,cfg)
    assert len(manager)==531 and SL['DkCopyDescriptor']==0xa7e3
    # Test only the new table-selector API in a flat isolated CPU fixture.
    # Full public/IRQ/cold binding is expressly deferred, not fabricated.
    select_cases=0;cookie_addresses=[];descriptors=[]
    for owner in range(256):
        m=[0]*65536;m[0xae00:0xae00+len(manager)]=manager;m[0xab72:0xab72+len(extra)]=extra;m[0xa740:0xa740+len(sb)]=sb;m[0x6002]=owner
        c=N.NesMPU(memory=m,pc=ML['CoSelect']);c.sp=224;c.stPushWord(0x5ffe)
        for _ in range(100):
            if c.pc==0x5fff:break
            c.step()
        else:raise AssertionError(('selector bound',owner))
        assert bool(c.p&1)==(37<=owner<=40)
        if c.p&1:
            cookie_addresses.append(m[8]+256*m[9]);descriptors.append(m[6]+256*m[7])
        select_cases+=1
    assert cookie_addresses[-1]==SL['DkCookie'] and descriptors[-1]==0xdfe0
    parity=0
    def selection(data,labels,owner,low,high,authenticated):
        m=[0]*65536;m[0xa740:0xa740+len(data)]=data;m[0x6002]=owner;m[0x16c]=low;m[0x16d]=high
        for at in [0xa800,0xaef3,ML['CoCheckCode']]:m[at:at+2]=[0x38 if authenticated else 0x18,0x60]
        c=N.NesMPU(memory=m,pc=labels['PrFamily']);c.a,c.x,c.y,c.p,c.sp=0x55,7,91,0xb1,224
        for _ in range(100):
            if c.pc in [0xab12,0xab4f,0xb031]:break
            c.step()
        else:raise AssertionError(('selector path bound',owner,low,high))
        return c.pc,c.a,c.x,c.y,c.p,m[0x16c],m[0x16d],m[0xc09e]
    for owner in range(256):
        if owner==40:continue
        for row in range(40):
            for high in [0xaa,0xb0]:
                for authenticated in [False,True]:
                    low=(0x8c+3*row)&255
                    assert selection(ref,RL,owner,low,high,authenticated)==selection(sb,SL,owner,low,high,authenticated),(owner,row,high,authenticated)
                    parity+=1
    # Actual MMC5/PPUDATA model, proposed pages modified only in memory.
    # Body is padded to8192 with invalid/uncommitted FF header bytes.
    b=W.scoped_load(R/'build/excitebike-pose-1101-v3/current4.nes');image=bytearray(raw);payload=body+bytes([0xff])*(8192-len(body))
    for i,page in enumerate(CODE):image[1048592+page*1024:1048592+(page+1)*1024]=payload[i*1024:(i+1)*1024]
    b['raw']=bytes(image);copy_cases=[]
    for fault in [None,*range(8)]:
        m=N.Bus(b);m.raw_page(1,3);m.raw_page(2,2);m.ram[2][0x125e:0x125e+len(worker)]=worker
        m.ram[2][0x1fe0:0x1ff0]=bytes([0x63])*16;m.ram[3][0x1fe0:0x1ff0]=bytes([0x79])*16
        m[0x2000]=0x20;m[8]=0x76;m[9]=0xae
        c=N.NesMPU(memory=m,pc=L['DkColdEntry']);c.sp=224;c.stPushWord(0x5ffe);injected=False
        for _ in range(500000):
            if c.pc==0x5fff:break
            if fault is not None and not injected and c.pc==L['DkVerifyByte']and m[5]==fault:
                # Corrupt the destination just before its actual verifier.
                m.ram[3][fault*1024]^=1;injected=True
            assert m[c.pc]!=0,('bootstrap BRK',hex(c.pc));c.step()
        else:raise AssertionError('bootstrap bound')
        assert bool(c.p&1)==(fault is None)and (fault is None or injected)
        assert (m[8],m[9])==(0x76,0xae)and bytes(m.ram[2][0x1fe0:0x1ff0])==bytes([0x63])*16
        assert bytes(m.ram[2][0x125e:0x125e+len(worker)])==worker
        if fault is None:assert bytes(m.ram[3])==payload
        copy_cases.append(dict(fault_row=fault,accepted=bool(c.p&1),CPU=c.processorCycles,source_worker_preserved=True,state_header_not_published=True))
    # Exercise the actual new resident CoCold chain and unchanged common
    # full-page worker in the same declared peripheral model.  All cartridge
    # modifications below exist in memory only, against still-ungranted pages.
    first_meta=bytearray([0xff])*1024;first_meta[0x25e:0x25e+len(worker)]=worker
    second_meta=bytes((i*29+7)&255 for i in range(1024))
    for page,data in zip(ART[1:],[first_meta,second_meta]):image[1048592+page*1024:1048592+(page+1)*1024]=data
    for pc,data in [(0xae00,manager),(0xab72,extra),(0xa740,sb)]:
        at=16+65*8192+pc-0xa000;image[at:at+len(data)]=data
    b['raw']=bytes(image)
    for name in ['CoCold','CoCheckCode']:
        seg='DK_v11_'+name;b['segs'][seg]=dict(start=str(ML[name]),ooffs=str(16+65*8192+ML[name]-0xa000));b['syms'][name]=dict(val=str(ML[name]),seg=seg)
    m=N.Bus(b);N.put(m,CurrentBank=0xd7,CurrentBankC=2,SelectedCharacter=40,OperMode=1,FamilyMainCommit=1,DisableScreenFlag=1,Mirror_PPUMASK=0,NmiDisable=255,Mirror_PPUCTRL=0xa0,ReloadCHRBank=0)
    m.raw_page(2,2);m.ram[2][:]=bytes([0x5b])*8192;m.ram[3][:]=bytes([0x6c])*8192
    # Starting headers deliberately do not match any existing owner. No
    # foreign actor retirement fixture is implied by this cold-only case.
    m.ram[2][0x1fe0]=m.ram[3][0x1fe0]=0
    z=N.invoke(m,'CoCold');assert z['P']&1,z
    expected_cookie=sb[SL['DkCookie']-0xa740:SL['DkCookie']-0xa740+16]
    assert bytes(m.ram[3][:0x1fe0])==payload[:0x1fe0]
    assert bytes(m.ram[2][:0x900])==bytes(0x900)
    assert bytes(m.ram[2][0x1000:0x1400])==first_meta and bytes(m.ram[2][0x1400:0x1800])==second_meta
    assert bytes(m.ram[2][0x1fe0:0x1ff0])==bytes(m.ram[3][0x1fe0:0x1ff0])==expected_cookie
    commits=[(bank,offset,value)for bank,offset,value in m.ram_writes if bank in [2,3]and offset==0x1fe0]
    assert commits[-2:]==[(3,0x1fe0,0xa7),(2,0x1fe0,0xa7)]and (2,0x1fe0,2)in commits,commits
    reads=m.ppu_reads;warm=N.invoke(m,'CoCold');assert warm['P']&1 and m.ppu_reads==reads
    cold_chain=dict(CPU=z['CPU'],warm_CPU=warm['CPU'],buffered_reads=reads,full_two_headers_commit_last=True,temporary_descriptor_magic=2,state_zero_pages=9,common_plus_private_rows=10,source_helpers_verified=True,all_8192_code_bytes_verified=True,placeholder_cookie_not_a_final_payload_authentication=True)
    # These are exact finite-domain candidate holes. Later upper3 was kept as
    # one conservative reservation in the Prince proposal; do not silently
    # claim this target-specific refinement is already a physical grant.
    evidence=R/'docs/qa/checkpoints/2026-11-02/bubble-bobble-resources-v1/current3-domain-rebind.json'
    finite=json.loads(evidence.read_text())['finite_domains'];collisions={k:sorted(set(v)&set(CODE+ART))for k,v in finite.items()if set(v)&set(CODE+ART)};assert not collisions,collisions
    q=dict(passed=True,proposal_only=True,shared_bytes_written=False,ROM_written=False,native_owner_admitted=False,base_SHA256=PIN,
        original_credits='Nintendo: original NES Donkey Kong Jr. World Rev1 actor, controls, terrain queries, fruit, timing and pixels.',
        frozen_core=dict(bytes=len(body),SHA256=sha(body),header_reserved_spare=312,tentative_public_vector_bytes=114,remaining_before_native_service_glue=198),
        namespace=dict(proposed_raw=40,current_DK=dict(slot=27,raw=28),Prince_raw38_retained=True,Bub_raw39_retained=True,frontend_selector_and_name_funding='Unresolved; no legally free bit promised. No frontend edits.'),
        proposed_physical_pages=dict(code=CODE,body_and_helper_art=ART,bytes=11264,preimages=[dict(page=p,offset=1048592+p*1024,SHA256=sha(raw[1048592+p*1024:1048592+(p+1)*1024]))for p in CODE+ART],existing_finite_domains_exclude_targets=True,current_complete_publisher_closure=False),
        proposed_conditional_RAM=dict(bank3_code=[0xa000,0xbfe0],bank2_mutable_source_and_context=[0xc000,0xc900],bank2_immutable_art_helpers=[0xd000,0xd800],headers=[0xbfe0,0xdfe0],header_bytes_each=16,shared_clock_preserved=[0xdfd0,0xdfd3],lifetime='Only after own exact two-header authentication; retire/invalidate before foreign overlay. No unconditional lease.'),
        cold=dict(common_worker_unchanged=True,compact_descriptor=desc.hex(),resident_descriptor_address=SL['DkDescriptorData'],cold_scratch_descriptor=[0xdfe0,0xdfe8],first_phase='After exact retirement/invalidation C2 is mapped. Copy8B descriptor over the invalid C2 header (byte0=2, never A7), then the unchanged common worker copies2 meta rows D0/D4 and clears9 pages C000..C8FF. Metadata-only rows retain C2 mapping while reading this descriptor.',second_phase='Raw40 typed boot at D25E copies/verifies8 scattered1024B code rows into RAM3 A000 while executing exclusively in RAM2. No header commit in private worker.',bootstrap_bytes=len(worker),bootstrap_end=L['DkColdEnd'],isolated_actual_mapper_PPUDATA_cases=copy_cases,actual_complete_CoCold_fixture=cold_chain,actual_owner_constructor_implemented=False),
        resident_measurement=dict(reference='Granted private Prince v51, not delivered16a9',manager_bytes=len(manager),manager_span=[0xae00,0xb013],old_executed_source_res15_NOPS_removed=14,new_owner_table_bytes=4,new_raw40_descriptor_guard_bytes=10,selector_rejection_factor_saved=21,selector_bytes=len(sb),selector_span=[0xa740,0xa740+len(sb)],cookie_span=[SL['DkCookie'],SL['DkCookie']+16],extra_bytes=len(extra),extra_span=[0xab72,0xabd2],descriptor_bytes=8,descriptor_span=[SL['DkDescriptorData'],SL['DkDescriptorData']+8],remaining_extra_bytes=2,remaining_selector_bytes=3,remaining_common_descriptor_bytes=10,selector_CPU_cases=select_cases,all_other_raw_selector_path_AXYP_target_parity=parity,full_public_foreign_IRQ_closure=False),
        source_hit_freeze=dict(original_duration=60,source_player_clock_and_actor_freeze_qualified=True,current_native_AI_freeze_qualified=False,required_semantics='Suspend native enemy AI/contact/spawn and cannons for source hit epochs while preserving genuine victim art, source hit updates and exact retirement. Do not set global TimerControl across Main: it rejects NativePhase and changes host timer/owner lifetimes.',next_exact_probe='Current EnemiesAndLoopsCore and ProcessCannons ingress; owner-specific source-funded gate needed if existing typed policies cannot express it.'),
        required_actual_routes=['Fresh/cold constructor(originalCA82 including36tick death counter, originalbodyattrs1, sourcepose, nativeanchor, worldenable, fruit reset).','Main plus actual movement/carry/scene/death transport.','Sourcepose FullBox16/Head10/Body11/Side14 and distinct typedcontact; never treat HuBody as enemy contact.','CHR/body fruit/score art and Colors26/native worldbackdrop, Status30/native header, menu17/18.','Actual native pickup/weapon/head/bounce/vine ingress must reject or support raw40 before legacy table indexing; Prince actual NrPickup A2BE bound37 is a known review site.','Current complete finite publisher/table/menu/IRQ closure for all11physicalpages, plus four-owner allraw/header/retirement/NMI/IRQ foreign proof.','DK slot27 Select selector/name/icon funding, root reviewed newraw40 admission, real native smoke and assisted1-1.'],
        scope='Measured storage/typed owner protocol and isolated proposed-overlay copy/verify only. No shared routing/public DK services/menu/rawID/physical/RAM grant or native qualification.',
        bindings={p.relative_to(R).as_posix():sha(p.read_bytes())for p in[Path(__file__),BASE,frozen,sunny,evidence,pool/'current-owner-v51.s',pool/'current-selector-v51.s',R/'docs/qa/allocations/prince-shared-successor-1102-v30.json',O/'admission-cold-v11.s',O/'admission-cold-v11.bin',O/'admission-owner-v11.s',O/'admission-owner-v11.bin',O/'admission-owner-extra-v11.bin',O/'admission-selector-v11.s',O/'admission-selector-v11.bin']})
    (O/'admission-proposal-v11.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:q[k]for k in['passed','proposal_only','ROM_written','base_SHA256','resident_measurement','cold']}))


if __name__=='__main__':main()
