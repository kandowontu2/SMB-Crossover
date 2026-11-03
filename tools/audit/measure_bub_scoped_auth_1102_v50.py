"""Conditional scoped-auth byte/cycle prototype; NOT a qualified cache/candidate."""
import collections,json,re
from pathlib import Path
import measure_bub_landing_1102_v21 as L
import check_bubble_bobble_common_cold_1102_v4 as C

N,Q,P,R,address=L.N,L.Q,L.P,L.R,L.address;O=L.O
PIN='9cf99b438e6f5bc614dc4ccc433707a3796702b7f33a04318a428a1155397f15'


def assemble():
    _,old,layout,route=L.bundle();old['raw']=(O/'combined-current-landing.nes').read_bytes()
    assert P.sha(old['raw'])==PIN
    funding=json.loads((O/'resident-compaction-v49.json').read_text())
    for path,digest in funding['bindings'].items():assert P.sha((R/path).read_bytes())==digest,path
    src=(O/'auth-frame-v49-compact.s').read_text()
    def once(a,z):
        nonlocal src
        assert src.count(a)==1,(a,src.count(a));src=src.replace(a,z)
    # All three targets overwrite incoming A before a functional use:
    # worker LDA#2; X5 publisher LDA X5WideChrActive; retire LDX#0 then
    # validation's LDA token. Public CoCold/CoRetire still save caller A/P.
    once('CoFarIndexed:\n sta SafecallA_SMC+1\n','CoFarIndexed:\n')
    once('CoRetireOwners:\n','''CoRetireOwners:
 ; Proposed bit7 only, never a raw-character value in Rogue count bits.
 ; Do not write ordinary protocol states: NMI may ACK them concurrently.
 lda FamilyMainCommit
 bpl :+
 and #$7f
 sta FamilyMainCommit
:
''')
    once('CoFundingStart:\n .res 20,$ea\n','''; Proposed scope relies on actual Main begin/end, owner stability and
; complete pre-writer invalidation. Those are NOT proved by a flag alone.
CoMarkLease:
 lda FamilyMainCommit
 cmp #1
 bne :+
 lda #$81
 sta FamilyMainCommit
:
 rts
CoFundingStart:
 .res 0,$ea
''')
    once('CoDescriptorHiFunding:.byte $ea,$ea\n','CoDescriptorHiFunding:\nCoForeignLo:.byte $7b,$03\n')
    src+='\n.export CoMarkLease,CoForeignLo\n'
    cfg=(O/'auth-frame-v49-compact.cfg').read_text()
    labels=L.assemble('auth-scope-v50-owner',src,cfg)
    owner=(O/'auth-scope-v50-owner.bin').read_bytes()
    assert len(owner)==531 and labels['CoFundingStart']==0xafe6
    assert labels['CoForeignLo']==0xaff1
    original=P.P.labels(L.B/'native-event-v9-owner.lbl')
    assert [labels[n] for n in ['CoCold','CoRetire','CoSmc','CoOwnerEnd']]==[original[n] for n in ['CoCold','CoRetire','CoSmc','CoOwnerEnd']]
    assert owner[0x1f3:]==old['raw'][16+65*8192+0xff3:16+65*8192+0x1013]
    rs=(L.B/'native-proxy-routes.s').read_text()
    rs=rs.replace('ExCheckCode=$aef3',f'ExCheckCode=${labels["CoCheckCode"]:04x}')
    assert rs.count(' jsr ExCheckCode\n bcc ExDispatchNo\n')==1
    rs=rs.replace(' jsr ExCheckCode\n bcc ExDispatchNo\n',f''' ; Conditional measurement only: genuine Main/writer closure pending.
 lda FamilyMainCommit
 cmp #$81
 beq ExDispatchAuthReady
 jsr ExCheckCode
 bcc ExDispatchNo
 jsr ${labels['CoMarkLease']:04x}
ExDispatchAuthReady:
''')
    rs=rs.replace('ExForeignLo:.byte <ExOriginalStatus,<ExOriginalColors',f'ExForeignLo=${labels["CoForeignLo"]:04x}')
    # The current public reset veneer has an intentional ROM-only target.
    rs=rs.replace('.repeat 37\n jmp ExDispatch\n.endrepeat',
        '.repeat 37,I\n .if I=19\n  jmp $b100\n .else\n  jmp ExDispatch\n .endif\n.endrepeat')
    rcfg=(L.B/'native-proxy-routes.cfg').read_text().replace('size=$ba','size=$c0')
    rcfg=rcfg.replace((L.B/'native-proxy-').as_posix(),(O/'auth-scope-v50-').as_posix())
    rl=L.assemble('auth-scope-v50-routes',rs,rcfg)
    dispatch=(O/'auth-scope-v50-routes.bin').read_bytes();assert len(dispatch)==192
    assert rl['ExDispatch']==route['ExDispatch']==0xa740
    assert rl['BbTypedDispatch']==0xa7fa
    raw=bytearray(old['raw']);parts=[(0xae00,owner),(0xa740,dispatch)]
    for pc,name in [(0xb08c,'route-veneers'),(0xb031,'route-foreign'),(0xb105,'route-foreign-bank'),
                    (0xb013,'route-scene-gate'),(0xb062,'route-scene-own'),(0xb026,'route-retire-stub'),(0xb029,'typed-contact')]:
        blob=(O/f'auth-scope-v50-{name}.bin').read_bytes();parts.append((pc,blob))
    patches=[]
    for pc,blob in parts:
        at=16+65*8192+(pc&8191);before=bytes(raw[at:at+len(blob)])
        if before==blob:continue
        raw[at:at+len(blob)]=blob;patches.append(dict(offset=at,CPU=pc,old=before.hex(),new=blob.hex()))
    new=dict(old);new['raw']=bytes(raw)
    assert len(patches)==4,[(hex(p['CPU']),len(bytes.fromhex(p['new']))) for p in patches]
    # Source-only/in-memory reconstruction; NEVER write raw to a .nes file.
    return old,new,layout,route,labels,rl,patches


def main():
    old,new,layout,route,owner,rl,patches=assemble();baseowner=P.P.labels(L.B/'native-event-v9-owner.lbl')
    native=N.NesMPU;cases=[]
    for identity in [0,1]:
        for phase,keys in [('idle',0),('right',1),('left',2),('jump_right',129),('shot',64)]:
            pair=[Q.fresh(b,route,identity) for b in [old,new]];traces=[];outputs=[];auth=[]
            for index,m in enumerate(pair):
                L.E.main_fields(m);trace=[];count=0;lab=baseowner if index==0 else owner
                class Trace(native):
                    def step(self):
                        nonlocal count
                        mem=self.memory;pc=self.pc;tag=mem.rawtags[(pc-0x8000)//8192] if pc>=0x8000 else -1
                        if tag==193 and pc==lab['CoCheckCode']:count+=1
                        if tag==3 and 0xa000<=pc<0xbfe0 or tag==2 and 0xd320<=pc<0xd400:
                            trace.append((tag,pc,self.a,self.x,self.y,self.p,self.sp))
                        return native.step(self)
                N.NesMPU=Trace
                try:
                    out=[]
                    for epoch in range(8):
                        N.put(m,FrameCounter=epoch,SavedJoypadBits=keys,SavedJoypad1Bits=keys,
                            FamilyMainCommit=0,NmiDisable=255,VRAM_Buffer1_Offset=0)
                        N.invoke(m,'PauseRoutine',a=255,x=7,y=91,p=0x31)
                        assert N.get(m,'FamilyMainCommit')==1
                        out.append(N.invoke(m,'GameCoreRoutine',x=0,y=0))
                        assert N.get(m,'FamilyMainCommit')==(1 if index==0 else 0x81)
                        N.invoke(m,'RdsMainGate',a=0,x=7,y=91,p=0x31)
                        assert N.get(m,'FamilyMainCommit')==0
                    outputs.append(out)
                finally:N.NesMPU=native
                traces.append(trace);auth.append(count)
            assert traces[0]==traces[1],('Actual original/private AXYP/SP instruction trace',identity,phase)
            assert pair[0].ram==pair[1].ram and pair[0].rawtags==pair[1].rawtags
            assert bytes(pair[0][3:11])==bytes(pair[1][3:11])
            for a,z in zip(*outputs):assert [a[k] for k in ['A','X','Y','P']]==[z[k] for k in ['A','X','Y','P']]
            before=sum(q['CPU'] for q in outputs[0]);after=sum(q['CPU'] for q in outputs[1])
            assert auth==[104,8],auth
            cases.append(dict(identity=identity,phase=phase,Main_calls=8,baseline_mean_CPU=before/8,
                conditional_prototype_mean_CPU=after/8,saving_CPU_per_Main=(before-after)/8,
                saving_percent=100*(before-after)/before,full_auth_calls=auth,
                original_private_instruction_AXYP_SP_trace_entries=len(traces[0]),
                original_private_instruction_trace_SHA256=P.sha(json.dumps(traces[0]).encode()),
                native_private_RAM_draw_input_R0_7_maps_final_AXYP_exact=True,
                scope='Actual bracketed Main, no NMI/IRQ or owner/header writers during these empty ground fixtures. Not an invariant proof.'))
    # A direct helper remains FULL even if a forged proposed scope bit is set.
    # Public dispatcher rejection before a lease is similarly preserved.
    direct=0
    for bank in [2,3]:
        for i in range(16):
            for protocol in [0,1,0x81]:
                m=Q.fresh(new,route,0);m.ram[bank][0x1fe0+i]^=1
                N.put(m,FamilyMainCommit=protocol);before=[bytes(q) for q in m.ram]
                z=C.call(m,owner['CoCheckCode'],flags=0x31)
                assert not z['P']&1 and before==[bytes(q) for q in m.ram]
                direct+=1
    # Mandatory adversarial negative: an unannounced header write violates
    # the contemplated lifetime contract. The prototype DOES NOT detect it
    # on a reused dispatch. This is why neither a cache bit nor these timing
    # tests qualify the design; all real writers/ingresses must be closed.
    m=Q.fresh(new,route,0);N.put(m,FamilyMainCommit=1)
    C.call(m,0xb08c+9*3,flags=0x31);assert N.get(m,'FamilyMainCommit')==0x81
    m.ram[3][0x1fe7]^=1
    unsafe=C.call(m,0xb08c+9*3,flags=0x31)
    full=C.call(m,owner['CoCheckCode'],flags=0x31)
    assert unsafe['P']&1 and not full['P']&1
    rejected=dict(case='unannounced_header_write_after_valid_dispatch',
        conditional_dispatch_C_success=True,direct_full_auth_C_success=False,
        demonstrates_missing_lifetime_invariant=True,qualification=False)
    # The source invalidation is before any owner checks or RAM-header
    # writes, and never rewrites ordinary foreign protocol values0..7.
    retire=[]
    for protocol in [0,1,2,3,4,5,6,7,0x81]:
        for raw in [0,2,35,36,37,38,39]:
            m=Q.fresh(new,route,0);N.put(m,SelectedCharacter=raw,FamilyMainCommit=protocol)
            z=C.call(m,owner['CoRetire'],flags=0x31)
            assert N.get(m,'FamilyMainCommit')==(1 if protocol==0x81 else protocol)
            assert (z['A'],z['X'],z['Y'])==(83,71,109)
            assert m.ram[2][0x1fe0]==m.ram[3][0x1fe0]==0
            retire.append(dict(protocol_before=protocol,raw=raw,protocol_after=N.get(m,'FamilyMainCommit')))
    out=dict(passed=True,status='CONDITIONAL_BYTE_AND_CYCLE_MEASUREMENT_ONLY',qualified=False,
        ROM_written=False,native=False,shared_source_mutated=False,lease_bit_granted=False,
        base_ROM_SHA256=PIN,in_memory_prototype_SHA256=P.sha(new['raw']),
        owner_bytes=531,dispatch_bytes=192,public_cold_retire_SMC_cookie_addresses_unchanged=True,
        proposed_state='Existing dedicated FamilyMainCommit5FFF bit7 only; no raw ID stored in Rogue count bits. No allocation is assumed.',
        Main_cases=cases,direct_full_auth_poison_cases=direct,
        rejected_unannounced_writer_control=rejected,retirement_protocol_cases=retire,
        patches=patches,labels=owner,route_labels=rl,
        missing_before_qualification=[
            'Formal permission to use the dedicated common publication high bit.',
            'Complete actual current SelectedCharacter and both-header writer/entry/caller closure, including temporary audio identities and every private-state/code overwrite.',
            'Prove genuine Main entry/exit and direct public-call scope; a manually set busy/lease flag is not trusted evidence.',
            'All changed cold/retire/publisher/import contracts, actual IRQ and lag-NMI cuts, malformed routes, foreign profiles and genuine trapped native-AI retirement.',
            'NMI invalidates bit7 each time, so the no-interrupt one-check measurement is not the final hardware saving. Do not claim60Hz or install this prototype.'
        ],bindings={str(p.relative_to(R)):P.sha(p.read_bytes()) for p in [Path(__file__),O/'combined-current-landing.nes',
            O/'resident-compaction-v49.json',O/'auth-lifetime-v48.json',
            O/'auth-scope-v50-owner.s',O/'auth-scope-v50-owner.bin',O/'auth-scope-v50-owner.lbl',
            O/'auth-scope-v50-routes.s',O/'auth-scope-v50-routes.bin',O/'auth-scope-v50-routes.lbl']})
    dst=O/'scoped-auth-v50-measurement.json';assert not dst.exists();dst.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(passed=True,qualified=False,ROM_written=False,owner_bytes=531,dispatch_bytes=192,
        Main_cases=len(cases),saving_CPU_per_Main=[q['saving_CPU_per_Main'] for q in cases],
        mean_percent=sum(q['saving_percent'] for q in cases)/len(cases),
        direct_full_auth_poison_cases=direct,retirement_protocol_cases=len(retire),
        unannounced_header_writer_control='UNSAFE; lifetime proof mandatory',receipt=str(dst.relative_to(R)))))


if __name__=='__main__':main()
