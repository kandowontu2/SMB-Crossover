"""Exact12397 cheat-owner diagnosis; source CPU units and zero output files.

Flags are changed only by the actual compiled CheatsMenuInput routine using
explicit focus/pressed mailboxes. This is a labelled menu-call unit, not an
execution of the title/options opening; actual UI receipt86e0 is separate.
No actor, position, source health, ability or cheat-flag seed is introduced.
"""
import argparse
from collections import Counter
from hashlib import sha256
import json
from zipfile import ZipFile

import compose_smb2_postbg_mirror_1113 as C
import check_bub_current_budget_1113 as Frames

W=C.W
N=C.N
Flag=C.Owner.Terrain.Flag
PIN=C.CANDIDATE
ROWS=((1,0),(2,2),(4,3),(8,4),(16,5))
RESTORE=bytes.fromhex(
    'a200689503e8e00890f868a868aa6828ad1c6ff012'
    '8d6a01a9c98d6c01a9b78d6d01a98a4c5a01'
    '8d6a01a9218d6c01a9a08d6d01a9814c5a01')
# Isolated unit proposal only: these bytes are never installed into a ROM by
# this module. Root must grant the15-byte source padding before a composer.
DRAFT_RESTORE=bytes.fromhex(
    'a2f868950be8d0fa68a868aa6828ad1c6ff012'
    '8d6a01a9c98d6c01a9b78d6d01a98a4c5a01'
    'ad02604919f008a9008d6a014cf0aaa9004c40ad')
DRAFT_TAIL=bytes.fromhex('a9218d6c01a9a08d6d01a9814c5a01')
NAMES=('S2BoundaryGame','CheatsGameRoutinesGate',
       'CheatsGameRoutinesGate::Native','HuGameRoutinesDirect','GameRoutines',
       'S2MainGame','S2MainPlayer','S2NativeStart','PlayerCtrlRoutine')


def bindings(raw):
    assert sha256(raw).hexdigest()==PIN
    assert C.proposal(C.inverse(raw))[0]==raw
    b=dict(W.Symbols.bundle(),raw=raw)
    expected={
      'CheatsMenuInput':'8d6a01a9008d6c01a9a08d6d01a9bf4c5a01',
      'CheatsGameRoutinesGate::Restore':
        'a200689503e8e00890f868a868aa6828ad1c6ff012',
      'CheatsGameRoutinesGate::Native':
        '8d6a01a9218d6c01a9a08d6d01a9814c5a01',
      'S2BoundaryGame':
        '0848ad0260c919f01468288d6a01a94d8d6c01a9a18d6d01a9814c5a01'
        '68288d6a01a96f8d6c01a9b88d6d01a9f64c5a01',
      'S2MainGame':
        'a50fc908f016c90bf0158d6a01a9218d6c01a9a08d6d01a9814c5a01'
        '4c97b82091b020ce8a4c8c8a',
      'HuGameRoutinesDirect':
        'ad02604918f00e491ad007adee5f4901f0034c21a04c33e0',
    }
    windows={}
    for name,h in expected.items():
        at=W.location(b,name);code=bytes.fromhex(h)
        assert raw[at:at+len(code)]==code,(name,'compiled preimage')
        windows[name]=dict(pc=W.address(b,name),rawbank=((at-16)//8192)|128,
                           bytes=len(code),SHA256=sha256(code).hexdigest())
    points={(W.address(b,n),((W.location(b,n)-16)//8192)|128):n for n in NAMES}
    return b,points,windows


def menu_mask(m,mask):
    """Actual menu routine unit: only documented UI input mailboxes change."""
    assert 0<=mask<32 and N.get(m,'CheatInvincible')==0
    start=N.get(m,'CheatStartLevel')
    for bit,row in ROWS:
        if mask&bit:
            N.put(m,CrossoverOptionsFocus=row,CrossoverMenuPressed=128)
            N.invoke(m,'CheatsMenuInput')
    assert N.get(m,'CheatInvincible')==mask
    assert N.get(m,'CheatStartLevel')==start


def funding(raw):
    """A source-owned padding request, not a grant or a ROM transform."""
    b,_,_=bindings(raw)
    at=W.location(b,'CheatsGameRoutinesGate::Restore')
    assert at==16+63*8192+0x2a9 and raw[at:at+57]==RESTORE
    palette=W.location(b,'S2TypedWorldPalette')
    assert palette==16+63*8192+0xae2
    assert raw[palette:palette+14]==bytes.fromhex('ad53070a85030a1865036906a860')
    pad=palette+14
    assert raw[pad:pad+16]==b'\xff'*16
    assert W.location(b,'S2ServiceVeneers')==pad+16
    zpath=W.R/'docs/qa/checkpoints/2026-11-01/ready85-doki-native-v1/source.zip'
    member='build/doki-current-component-1101-v1/src/smb2_roster_host_v5.s'
    with ZipFile(zpath)as z:source=z.read(member)
    assert sha256(source).hexdigest()=='ec181a33ecc6a7bd74d5f0856ec6cf40f76b00946a71e603cdf8a446f10e3220'
    assert b'.res 223-(*-S2TypedHostBegin),$ff\nS2ServiceVeneers:'in source
    assert b' adc #6\n tay\n rts\n.endproc'in source
    # Exact current data consumers are read from their current tables. A
    # historical linker gap alone does not retire a Rogue 256-byte reader.
    pages=[]
    for mode,count,banks,highs in (
        ('lower',192,'RdaLowerBankTable','RdaLowerHighTable'),
        ('upper',32,'RdaUpperRawBankTable','RdaUpperRawHighTable')):
        bank_at,high_at=W.location(b,banks),W.location(b,highs)
        for i in range(count):
            bank=raw[bank_at+i]&127;start=(raw[high_at+i]-0xa0)*256
            assert 0<=start<=8192-256
            assert bank!=63
            pages.append((mode,i,bank,start))
    image=raw[16+63*8192:16+64*8192]
    direct=[(0xa000+i,int.from_bytes(image[i+1:i+3],'little'))
            for i in range(8190)if image[i]in(0x20,0x4c)
            and 0xaaf0<=int.from_bytes(image[i+1:i+3],'little')<0xab00]
    assert not direct
    return dict(passed=True,ROM_SHA256=PIN,physical_bank=63,
        owned_gate_restore_half_open=[0xa2a9,0xa2e2],gate_bytes=57,
        restore_preimage_SHA256=sha256(RESTORE).hexdigest(),
        proposed_padding_half_open=[0xaaf0,0xaaff],bytes_requested=15,
        retained_last_FF=0xaaff,padding16_SHA256=sha256(b'\xff'*16).hexdigest(),
        file_half_open=[pad,pad+15],source_member=member,
        source_member_SHA256=sha256(source).hexdigest(),
        padding_source_line=84,preceding_exact_palette_returns=True,
        unchanged_36_veneers_begin=0xab00,local_literal_JSR_JMP_into_padding=direct,
        current_Rogue_page_readers_excluding_bank63=len(pages),
        candidate_or_ROM_changes=False,formal_grant=False,outputs=0)


class UnitMemory(list):
    """Only the code/stack/register unit; no running game or ROM overlay."""
    def __init__(self,proposed):
        super().__init__([0]*65536)
        body=DRAFT_RESTORE if proposed else RESTORE
        list.__setitem__(self,slice(0xa2a9,0xa2e2),body)
        list.__setitem__(self,slice(0xaaf0,0xaaff),DRAFT_TAIL)
        # This is the authenticated existing AD40 owner tail, omitting only
        # its preceding PLA/PLP, since the real Cheats restore already did so.
        list.__setitem__(self,slice(0xad40,0xad52),bytes.fromhex(
            '8d6a01a96f8d6c01a9b88d6d01a9f64c5a01'))
        self.writes=[]

    def __setitem__(self,at,value):
        assert at in (*range(3,11),0x16a,0x16c,0x16d),hex(at)
        self.writes.append((at,value))
        list.__setitem__(self,at,value)


def unit(memory,owner,p,hurt):
    # Arbitrary original R0..R7, X/Y/A/P in their actual pop order. Every
    # slot spans all256 data values across the owner domain, independently
    # of P. Pop data never controls the fixed-count loop or owner selector.
    scratch=tuple((owner+31*i)&255 for i in range(8))
    stack=(*scratch,owner^85,owner^170,owner^90,p)
    for at,value in ((0x6002,owner),(0x6f1c,hurt),
                     *((0x100+201+i,v)for i,v in enumerate(stack))):
        list.__setitem__(memory,at,value)
    memory.writes.clear()
    cpu=N.NesMPU(memory=memory,pc=0xa2a9)
    cpu.sp,cpu.a,cpu.x,cpu.y,cpu.p=200,17,99,171,p
    for _ in range(100):
        if cpu.pc==0x15a:
            assert cpu.sp==212
            assert tuple(memory[3:11])==scratch
            assert (cpu.x,cpu.y)==(owner^170,owner^85)
            assert memory[0x16a]==(hurt if hurt else 0)
            assert tuple(memory.writes[:8])==tuple((3+i,v)for i,v in enumerate(scratch))
            assert [at for at,_ in memory.writes[8:]]==[0x16a,0x16c,0x16d]
            return ((cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp,cpu.pc),
                    tuple(memory.writes),bytes(memory[0x100+201:0x100+213]))
        assert memory[cpu.pc] in (0xa2,0x68,0x95,0xe8,0xe0,0x90,0xd0,
                                 0xa8,0xaa,0x28,0xad,0xf0,0x8d,0xa9,0x4c,0x49)
        cpu.step()
    raise AssertionError('Bounded restore/selector unit')


def draft_abi(raw):
    """All-flags/data isolated ABI proposal; no code placement or ROM edit."""
    funding(raw)
    assert len(DRAFT_RESTORE)==len(RESTORE)==57 and len(DRAFT_TAIL)==15
    b,_,_=bindings(raw)
    own=W.location(b,'S2BoundaryGame')+31
    assert raw[own:own+18]==bytes.fromhex('8d6a01a96f8d6c01a9b88d6d01a9f64c5a01')
    old,new=UnitMemory(False),UnitMemory(True)
    foreign=own_cases=injury=0
    for owner in range(256):
        for p in range(256):
            a,z=unit(old,owner,p,0),unit(new,owner,p,0)
            if owner!=25:
                assert a==z,(owner,p,'foreign exact ABI/ordered RAM/live stack')
                foreign+=1
            else:
                assert a[0][1:]==z[0][1:] and a[0][0]==0x81 and z[0][0]==0xf6
                assert a[1][:-2]==z[1][:-2] and a[2]==z[2]
                assert z[1][-2:]==((0x16c,0x6f),(0x16d,0xb8))
                own_cases+=1
    for hurt in range(1,256):
        for p in range(256):
            assert unit(old,25,p,hurt)==unit(new,25,p,hurt)
            injury+=1
    return dict(passed=True,ROM_SHA256=PIN,isolated_proposal_only=True,
                foreign_raw_owner_all_P_pairs=foreign,SMB2_all_P_pairs=own_cases,
                nonzero_hurt_all_P_pairs=injury,
                every_R0_to_R7_slot_all256_values_for_every_P=True,
                original_R0_to_R7_pop_and_write_order_exact=True,
                original_injury_route_and_foreign81_A021_exact=True,
                additional_stack_or_RAM_writes=0,
                proposed_bytes=dict(restore=DRAFT_RESTORE.hex(),padding=DRAFT_TAIL.hex()),
                formal_grant=False,ROM_changes=0,outputs=0)


def snapshot(m):
    q={n:N.get(m,n) for n in ('CheatInvincible','SelectedCharacter','S2Variant',
       'S2Ready','S2Health','S2MaxHealth','S2Held','S2VX','S2Clock',
       'SavedJoypadBits','NumberofLives','GameEngineSubroutine','GuestHurtKind')}
    q['x']=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc')
    q['y']=N.get(m,'Player_Y_Position')
    return q


def matrix(raw,updates=8):
    _,points,windows=bindings(raw)
    counts=Counter();cases=[];native_preconditions=Counter()
    for variant in range(8):
        seed=Flag.cold(raw,variant)
        assert N.get(seed,'CheatInvincible')==0
        for mask in range(32):
            m=N.fork(seed);menu_mask(m,mask)
            before=snapshot(m);calls=Counter()
            def observe(mm,c):
                if c.pc<0x8000:return
                name=points.get((c.pc,mm.rawtags[(c.pc-0x8000)//8192]))
                if name:
                    calls[name]+=1
                    if name=='CheatsGameRoutinesGate::Native':
                        # Actual immediately preceding LDA GuestHurtKind/BEQ
                        # establishes A/N/Z; C/V/D/I are inherited, not assumed.
                        assert N.get(mm,'GuestHurtKind')==0
                        assert c.a==0 and c.p&0x82==2,(variant,mask,c.a,c.p)
                        native_preconditions['A0_Z1_N0_actual_entries']+=1
            for _ in range(updates):
                m.controller_pad=1
                Frames.frame(m,observe,whole_pass=True)
            after=snapshot(m)
            assert after['CheatInvincible']==mask and after['NumberofLives']==2
            assert after['GameEngineSubroutine']==8 and after['S2Ready']==178
            assert after['SavedJoypadBits']==1
            assert (after['S2Clock']-before['S2Clock'])&255==updates
            if mask:
                assert calls['CheatsGameRoutinesGate']==updates
                assert calls['CheatsGameRoutinesGate::Native']==updates
                assert calls['GameRoutines']==updates
                assert calls['PlayerCtrlRoutine']==updates
                assert all(calls[n]==0 for n in ('S2BoundaryGame','S2MainGame',
                                                'S2MainPlayer','S2NativeStart'))
                assert after['x']==before['x']==40
                assert after['S2Held']==0 and after['S2VX']==0
                counts['all_nonzero_masks_missing_owner_update']+=1
            else:
                assert all(calls[n]==updates for n in ('S2BoundaryGame','S2MainGame',
                                                     'S2MainPlayer','S2NativeStart'))
                assert calls['CheatsGameRoutinesGate']==0
                assert after['x']>before['x']==40 and after['S2Held']==1
                counts['ordinary_owner_updates_and_movement']+=1
            cases.append(dict(variant=variant,mask=mask,before=before,after=after,
                              calls=dict(calls)))
        print(json.dumps(dict(progress_variant=variant,cases=len(cases)),separators=(',',':')),flush=True)
    digest=sha256(json.dumps(cases,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return dict(passed=True,ROM_SHA256=PIN,updates_per_case=updates,cases=len(cases),
                counts=dict(counts),native_preconditions=dict(native_preconditions),
                semantic_trace_SHA256=digest,compiled_windows=windows,
                all31_supported_nonzero_masks=True,all8_actual_constructors=True,
                menu_call_units=True,title_opening_source_claim=False,
                actual_UI_native_receipt='86e0977aefd42f0233e3fecee4c2177fefdde315ac51b95f97c2dbe6516fa0e1',
                actor_position_health_ability_flag_seeds=0,ROM_changes=0,outputs=0)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mode',choices=('bindings','matrix','funding','draft-abi'),default='matrix')
    args=p.parse_args();raw=C.Owner.NIGHTLY.read_bytes()
    out=(dict(passed=True,ROM_SHA256=PIN,compiled_windows=bindings(raw)[2],outputs=0)
         if args.mode=='bindings' else funding(raw)if args.mode=='funding'
         else draft_abi(raw)if args.mode=='draft-abi'else matrix(raw))
    print(json.dumps(out,separators=(',',':')),flush=True)
