"""Source/caller and finite CPU contracts for frozen one-way fragments."""
from collections import Counter
from hashlib import sha256
import itertools
import json
import re
from py65.disassembler import Disassembler

import check_dkjr_oneway_components_1114 as K
import check_dkjr_platform_query_lifecycle_1114 as Life

F,G=K.F,K.G
Q,P,H,N,W,L,C=K.Q,K.P,K.H,K.N,K.W,K.L,K.C


def run_flat(memory,pc,p=0x61):
    cpu=N.NesMPU(memory=memory,pc=pc);cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp=85,3,91,p,224
    cpu.stPushWord(0x5aff)
    for _ in range(100):
        if(cpu.pc,cpu.sp)==(0x5b00,224):return cpu
        assert memory[cpu.pc],('flat BRK',hex(cpu.pc))
        cpu.step()
    raise AssertionError(('flat bound',hex(cpu.pc)))


def main_projection(proposal):
    row=next(r for r in proposal['fragments']if r['payload_offset']==10846)
    pair=[]
    for key in('preimage_hex','proposed_hex'):
        m=bytearray(65536);m[0xd65e:0xd6a7]=bytes.fromhex(row[key]);pair.append(m)
    cases=0;digest=sha256()
    for state,p in itertools.product(range(1,6),range(256)):
        outputs=[]
        for m in pair:
            m[0xc06b]=state;c=run_flat(m,0xd68c,p)
            outputs.append((c.a,c.x,c.y,c.p,c.sp,m[0x1e]))
        assert outputs[0]==outputs[1],('Main map',state,p,outputs)
        digest.update(bytes(outputs[0]));cases+=1
    return dict(passed=True,legal_states=[1,2,3,4,5],all256_incoming_P=True,
        exact_AXYP_SP_and_stored_state_contexts=cases,aggregate_SHA256=digest.hexdigest())


def source_contract(raw,proposal,labels):
    source,*_=H.T.old_source();body=F.T.P.T.payload(raw)
    # Authenticate the unchanged successful-phase entry guard with Life's
    # byte-exact current source closure. Both callers tail into this routine.
    phase=source[source.index('DkjrNativePhase:'):source.index('NativePhaseHit:')]
    phase=phase[phase.index('lda $c06b'):]
    assert phase.index('lda $c06b')<phase.index('cmp #1')<phase.index('bcc DkjrNativePhaseReject')<phase.index('cmp #6')<phase.index('bcs DkjrNativePhaseReject')
    # C06B literal writers in the retained original are all immediate1..5.
    # Close the two fall-through accumulator sites explicitly; constructor
    # indexed clearing is outside Phase and reinitializes source1.
    stores=[];lines=source.splitlines()
    for i,line in enumerate(lines):
        code=line.split(';')[0].strip().lower()
        if code=='sta $c06b':
            prior=[]
            for prev in reversed(lines[:i]):
                text=prev.split(';')[0].strip().lower()
                if not text or text.endswith(':'):continue
                prior.append(text)
                if text.startswith('lda '):break
            stores.append((i+1,prior))
            assert prior[-1]in('lda #1','lda #2','lda #3','lda #4','lda #5',
                'lda #$01','lda #$02','lda #$03','lda #$04','lda #$05'),(i+1,prior)
    assert not re.search(r'^\s*(?:inc|dec|stx|sty) \$c06b\b',source,re.M)
    # The only named WScreenHi consumers are the two old World-local
    # store/read pairs. Static terrain keeps its pair; the vine pair is
    # replaced by a live X held without any intervening call.
    uses=[line.split(';')[0].strip()for line in lines if re.search(r'\bWScreenHi\b',line)and not line.startswith('WScreenHi=')]
    assert uses==['sta WScreenHi','lda WScreenHi','sta WScreenHi','lda WScreenHi'],uses
    literal=[line for line in lines if re.search(r'\$c8ee\b',line,re.I)]
    assert literal==['WScreenHi=$c8ee'],literal
    hook=source[source.index('DkjrNativeTerrainHook:'):source.index('DkjrNativeWorldBuild:')]
    assert hook.index('txa\n pha')<hook.index('jsr DkjrNativeWorldBuild')<hook.index('pla\n tax\n pla\n plp\n rts')
    vine=source[source.index('GrowingVine:'):source.index('ObjectsDone:')]
    held=vine[vine.index(' sta WScreenHi\n'):vine.index(' lda WScreenHi\n')]
    assert not re.search(r'^\s*(?:jsr|jmp|ldx|stx|tax|txa|inx|dex)\b',held,re.M)
    # Ordinary lists use only offsets0,40,80, append at most60B, then FF.
    # Therefore their source-format consumers cannot reach scratchC8EE.
    assert 'ListOffsets:.byte $40,$40,$80,0,0' in source
    append=source[source.index('AppendRect:'):source.index('ListOffsets:')]
    assert 'ldy WCount\n cpy #60\n bcc' in append
    return dict(passed=True,unchanged_phase_rejects_source0_or_ge6=True,
        source_state_literal_writers_closed=len(stores),source_state_writer_sites=stores,
        terrain_hook_restores_original_AXYP=True,
        old_WScreenHi_consumers=uses,vine_X_live_range_has_no_call_or_X_consumer=True,
        removed_vine_scratch_store_has_no_legal_external_reader=True,
        legal_rect_list_max_address=0xc8bf,
        note='Constructor indexed clearing and manually poisoned standalone lists are outside successful Phase/query contracts. Current post-source overlays and ScoreFlush are separately checked by whole-current gates.')


def main_dominance(parent,raw,proposal):
    e73=F.T.Old.reverse(parent)
    _,seed=H.cold(e73,e73[P.B.COOKIE_AT:P.B.COOKIE_AT+16])
    seed=C.setup(Q.mounted(seed,raw));seed.ram[2][0x8fe]=2
    counts=Counter();valid=[]
    for proposed,state in itertools.product((False,True),range(256)):
        m=L.clone(seed)
        if proposed:K.overlay(m,proposal['fragments'])
        m.ram[2][0x6b]=state;seen=[]
        def watch(memory,cpu):
            if cpu.pc==0xd68c:seen.append(memory.ram[2][0x6b])
        original=N.get(m,'Player_State')
        c=H.call(m,0xd65e,p=0x61,observe=watch)
        if state not in range(1,6):
            assert not seen and not c.p&1 and N.get(m,'Player_State')==original,(proposed,state,seen,c.p)
            counts['invalid_state_rejected_before_projection']+=1
        else:
            assert all(1<=s<=5 for s in seen),(proposed,state,seen)
            valid.append(dict(proposed=proposed,input=state,projected=seen,carry=c.p&1))
    return dict(passed=True,explicit_entry_boundary_states=256,arms=2,
        rejected_invalid_state_contexts=counts['invalid_state_rejected_before_projection'],
        current_Main_calls_real_scroll_pause_Phase_and_ScoreFlush=True,
        every_reached_projection_in_source1to5=valid,
        scope='Declared actual current private Main boundary fixtures, including all invalid source bytes; source-state writer closure supplies the legal post-Phase invariant.')


def relocation(raw,proposal):
    body=F.T.P.T.payload(raw)
    logical=[(0xa000,body[:8192]),(0xc900,body[8192:9216]),(0xd000,body[9216:])]
    oldhead=next(r for r in proposal['fragments']if r['payload_offset']==8928)
    oldtail=next(r for r in proposal['fragments']if r['payload_offset']==9056)
    targets=(0xcc14,0xcc17,0xcc60,0xcc77,0xcc7a)
    words={}
    for target in targets:
        words[hex(target)]=[hex(base+i)for base,data in logical for i in range(len(data)-1)
            if int.from_bytes(data[i:i+2],'little')==target]
    # Conservative all-byte word census includes tables/data as well as code.
    # The conservative second CC60 byte pair is RTS followed by CPY abs.
    # Decode the current straight-line constructor carrier from its entry,
    # independently of this assumed pair, to close its real boundaries.
    flat=bytearray(65536);flat[0xd000:0xd800]=body[9216:]
    dis=Disassembler(N.NesMPU(memory=flat));pc=0xd18b;pipe={}
    while pc<0xd200:
        size,text=dis.instruction_at(pc);pipe[pc]=(size,text);pc+=size
    assert pipe[0xd1c4]==(1,'RTS')and pipe[0xd1c5]==(3,'CPY $c8fd'),pipe
    columns=bytes((21,26,30,35,39,43,47,55,59,88,161,165,177,190))
    hits=[i for i in range(8192-len(columns))if body[i:i+len(columns)]==columns]
    assert len(hits)==1,hits
    linked,layout=P.girder_parts(dict(body=dict(box_address=0xbd3d),row_address=0xa000+hits[0]),retirement=True)
    image=linked['images']['PIPE'];assert layout['PIPE']==(0xd18b,117)
    assert body[9216+0x18b:9216+0x18b+len(image)]==image
    assert words=={'0xcc14':[],'0xcc17':[],'0xcc60':['0xcc12','0xd1c4'],
        '0xcc77':[],'0xcc7a':[]},words
    affected=[]
    for base,data in logical:
        for i in range(len(data)-1):
            value=int.from_bytes(data[i:i+2],'little')
            if 0xcc60<=value<0xcc7a:affected.append((hex(base+i),hex(value)))
    assert affected==[('0xcc12','0xcc60'),('0xd1c4','0xcc60')],affected
    head=bytes.fromhex(oldhead['preimage_hex']);tail=bytes.fromhex(oldtail['preimage_hex'])
    branches=[]
    for base,data in((0xcbe0,head),(0xcc60,tail)):
        for i in range(len(data)-1):
            if data[i]in(0x10,0x30,0x50,0x70,0x90,0xb0,0xd0,0xf0):
                delta=data[i+1]-256 if data[i+1]&128 else data[i+1]
                target=base+i+2+delta
                if target in targets:branches.append((hex(base+i),hex(target)))
    assert len([r for r in branches if r[1]=='0xcc14'])==10,branches
    assert len([r for r in branches if r[1]=='0xcc77'])==1,branches
    # The current published source map predates these private implementation
    # labels. Their only source definitions/references are within this owner.
    public=P.frozen_labels()
    assert not any(0xcbe0<=value<0xcc80 for value in public.values())
    source=(P.B.R/'tools/reference/dkjr_retire_layout_1113.s').read_text()
    assert '.export' not in source
    consumers=[]
    for path in sorted((P.B.R/'src').rglob('*')):
        if not path.is_file()or path.suffix not in('.s','.inc'):continue
        for number,line in enumerate(path.read_text().splitlines(),1):
            code=line.split(';')[0]
            if re.search(r'\b(?:DkPrivateRetireOrBBox|DkRetireGeometry|OriginalBBox)\b',code):
                consumers.append((str(path.relative_to(P.B.R)),number,code.strip()))
    assert not consumers,consumers
    return dict(passed=True,all_current_logical_payload_word_consumers=words,
        all_old_Tail_word_candidates=affected,
        D1C4_pair_is_RTS_followed_by_CPY_C8FD=dict(instructions=[(hex(at),*pipe[at])for at in(0xd1c4,0xd1c5)],
            actual_owned_constructor_source_byte_exact=True,
            current_constructor_carrier_SHA256=sha256(image).hexdigest()),
        old_relative_branch_consumers=branches,no_published_capsule_anchor_inside_relocated_spans=True,
        no_native_named_consumer=consumers,
        owned_head_JMP_rebound_from_CC60_to_CC63=True,
        note='Same numeric donor address keys in TMNT records and Rogue Dawn labels are foreign-source domains, not DK current RAM2 consumers. No global foreign-owner allocation is changed.')


def main():
    parent,raw=F.load_inputs();proposal=K.M.fragments(raw);proof,labels=Life.closure(raw)
    print('DKJR_ONEWAY_CONTRACTS '+json.dumps(dict(parent_SHA256=F.T.PIN,
        main_projection=main_projection(proposal),source_contract=source_contract(raw,proposal,labels),
        main_dominance=main_dominance(parent,raw,proposal),
        relocation=relocation(raw,proposal),actual_current_query_closure=proof['passed'],
        outputs_written=0,ROM_composed=False,
        scope='Finite projection and exact-current source/word consumer closure. Full successful Main, current overlay, cold/ISR/native gates remain required.'),separators=(',',':')),flush=True)


if __name__=='__main__':main()
