"""Private native PLAYER entry handoff; fixed cache209 remains its parent.

Code and exact preimages are inspectable without writing a ROM. Funding must
be qualified before proposal(): the native legacy MegaMan jump tweak has no
live caller; Luigi and every foreign direct-call ABI remain exact.
"""
from contextlib import contextmanager
from hashlib import sha256
import json
from unittest.mock import patch
import re

import prince_draw_cache_1113 as Cache
from check_prince_wall_sweep_1110_v6 import assemble

R=Cache.Packet.R
PARENT=Cache.CANDIDATE
CANDIDATE='309bbdae23b2dbe76951d3320c5afcb895e25b0fd081a558e93241b12f96389c'
HOOK=0xa04f
HOOK_OLD=bytes.fromhex('ad1307c906f004c907d053')
PROFILE=0xab5e
PROFILE_OLD=bytes.fromhex('ad0260c901d01bad0607d015a50fc908d00fa9408d0b078d0c078d0206a9fb858e60c908d0fb4c23b9')
HELPER=PROFILE+11
SOURCE=R/'tools/reference/prince_entrance_handoff_1113.s'


def offset(pc):
    assert 0xa000<=pc<0xc000
    return 16+8192+pc-0xa000


def code():
    symbols=dict(SelectedCharacter=0x6002,AreaType=0x753,
                 AutoControlPlayer=0xa0c1,Player_State=0x1e,PlayerRdy=0xa0ad)
    helper,labels=assemble(SOURCE.read_text(),HELPER,symbols)
    assert len(helper)==25 and labels['Ready']==0xab7f
    dispatch,_=assemble('''
 lda SelectedCharacter
 cmp #8
 bne Done
 jmp LuigiNativeJump
Done:
 rts
''',PROFILE,dict(SelectedCharacter=0x6002,LuigiNativeJump=0xb923))
    assert len(dispatch)==11
    # LSR/CMP3 recognizes precisely headers6/7. Both pipe paths then run
    # their unchanged LDA Player_SprAttrib, making A/NZ exact as well.
    hook=bytes.fromhex('ad13074ac903f0034c')+HELPER.to_bytes(2,'little')
    replacement=(dispatch+helper).ljust(len(PROFILE_OLD),b'\xea')
    assert len(hook)==len(HOOK_OLD)==11 and len(replacement)==41
    return ((HOOK,HOOK_OLD,hook),(PROFILE,PROFILE_OLD,replacement))


def frozen_parent():
    import check_prince_natural_sword_1113 as P
    raw=P.Base.C.ROM.read_bytes()
    digest=sha256(raw).hexdigest()
    if digest=='526ef1df172c3172fccbd35aa0471a9ff9a5a256a416acba8f7530d147a5b3f2':
        import compose_karnov_ladder_native_1113 as Karnov
        raw=Karnov.inverse_current(raw)
        digest=sha256(raw).hexdigest()
    if digest==Cache.PARENT:
        raw,_=Cache.proposal(raw)
    assert sha256(raw).hexdigest()==PARENT
    return raw


def preimages(raw):
    assert sha256(raw).hexdigest()==PARENT
    for pc,old,_new in code():
        assert raw[offset(pc):offset(pc)+len(old)]==old,hex(pc)
    return dict(parent_SHA256=PARENT,native_bank=1,
                code=[dict(CPU_half_open=[pc,pc+len(old)],old=old.hex(),new=new.hex())
                      for pc,old,new in code()],
                helper_CPU_half_open=[HELPER,HELPER+25],
                profile_bytes=41,remaining_dispatch_bytes=11,helper_bytes=25,padding_bytes=5,
                new_RAM=0,new_CHR_pages=0,private_streams_changed=False)


def funding(raw):
    """Exact linked bindings plus the closed native fresh-jump admission."""
    import check_prince_earned_sword_combat_1113 as F
    preimages(raw)
    b=F.P.W.Symbols.bundle()
    reservation=json.loads((R/'docs/qa/allocations/prince-entrance-player-1113.json').read_text())
    assert reservation['profile']['complete_preimage']==PROFILE_OLD.hex()
    assert reservation['entrance_hook']['complete_preimage']==HOOK_OLD.hex()
    assert sha256(PROFILE_OLD).hexdigest()==reservation['profile']['preimage_SHA256']
    assert sha256(HOOK_OLD).hexdigest()==reservation['entrance_hook']['preimage_SHA256']
    assert F.P.W.location(b,'CrossoverJumpProfile')==offset(PROFILE)
    assert F.P.W.address(b,'LuigiNativeJump')==0xb923
    native=raw[16:16+128*8192]
    refs=[(i//8192,i%8192) for i in range(len(native)-1)
          if native[i:i+2]==PROFILE.to_bytes(2,'little')]
    assert refs==[(1,0x8a3),(23,0x8e4),(37,0xac3),(37,0xacb)],refs
    assert native[8192+0x8a2:8192+0x8a5]==bytes.fromhex('205eab')
    rogue=0
    for count,banks,highs in ((192,'RdaLowerBankTable','RdaLowerHighTable'),
                              (32,'RdaUpperRawBankTable','RdaUpperRawHighTable')):
        at,hi=F.P.W.location(b,banks),F.P.W.location(b,highs)
        for index in range(count):
            assert raw[at+index]&127!=1,(banks,index,raw[hi+index])
            rogue+=1
    bank1=native[8192:16384]
    assert not [(i,int.from_bytes(bank1[i:i+2],'little')) for i in range(8191)
                if PROFILE<int.from_bytes(bank1[i:i+2],'little')<PROFILE+len(PROFILE_OLD)]
    # Fixed-bank farcall targets are split immediate operands rather than
    # literal words. Their native bank81 qualification matters here.
    farcalls=re.finditer(rb'\xa9(.)\x8d\x6c\x01\xa9(.)\x8d\x6d\x01\xa9\x81[\x20\x4c]\x5a\x01',native,re.S)
    for match in farcalls:
        target=match[1][0]+256*match[2][0]
        assert not PROFILE<=target<PROFILE+len(PROFILE_OLD),(match.start(),hex(target))
    # This is sound_table_00 row15's sound_0F command-data pointer, consumed
    # by the Contra sequencer in native23. It has no bank1 code meaning.
    assert F.P.W.location(b,'ContraNative::sound_table_00')==16+23*8192+0x8b6
    assert F.P.W.address(b,'ContraNative::sound_0f')==PROFILE
    assert native[23*8192+0x8e3:23*8192+0x8e6]==bytes.fromhex('055eab')
    assert F.P.W.location(b,'ExpandedWeapons::DiskReach')==16+37*8192+0xb5e
    for at,opcode in ((0xac3,0xd9),(0xacb,0xb9)):
        assert native[37*8192+at-1]==opcode
    # There is no split-constant farcall to this entry. The only source
    # definition/reference are the native profile and its fresh-jump JSR.
    assert bytes.fromhex('a95e8d6c01a9ab8d6d01') not in native
    sites=[]
    for path in (R/'src').rglob('*.s'):
        text=path.read_text(encoding='utf-8-sig')
        if 'CrossoverJumpProfile' in text:
            sites.extend((path.relative_to(R).as_posix(),line.strip())
                         for line in text.splitlines() if 'CrossoverJumpProfile' in line)
    sites.sort()
    assert sites==[('src/characters.s','.proc CrossoverJumpProfile'),
                  ('src/player.s','jsr CrossoverJumpProfile')],sites
    assert not any('CrossoverJumpProfile::' in path.read_text(encoding='utf-8-sig')
                   for path in (R/'src').rglob('*.s'))
    # Authenticate the complete still-linked source routine, including its
    # otherwise unreachable MM engine8 write instructions, before retiring it.
    source=(R/'src/characters.s').read_text()
    profile=source.split('.proc CrossoverJumpProfile\n',1)[1].split('.endproc',1)[0]
    old,_=assemble(profile,PROFILE,dict(SelectedCharacter=0x6002,SwimmingFlag=0x706,
        GameEngineSubroutine=15,VerticalForce=0x70b,VerticalForceDown=0x70c,
        Player_Y_MoveForce=0x602,Player_Y_Speed=0x8e,LuigiNativeJump=0xb923,
        CHARACTER_MEGAMAN=1,CHARACTER_LUIGI=8))
    assert old==PROFILE_OLD
    # Actual native instruction windows that enforce the caller exclusions.
    critical={}
    for name in ('PlayerMovementSubs','CrossoverGuestDispatch','CrossoverGuestControl',
                 'CrossoverVanillaMovement','PlayerPhysicsSub','CheckForJumping','InitJS','GetYPhy',
                 'GuestInjuryStart','GuestLegacyInjuryTry','GuestInjuryMovement',
                 'MegaManHurtMovement','GuestVictoryGuestControl','PlayerChangeSize',
                 'PlayerFireFlower','PlayerDeath','CheatsGameRoutinesGate'):
        at=F.P.W.location(b,name)
        critical[name]=dict(bank=(at-16)//8192,pc=F.P.W.address(b,name),
                            first64_SHA256=sha256(raw[at:at+64]).hexdigest())
    player=(R/'src/player.s').read_text()
    assert 'lda JumpspringAnimCtrl' in player.split('CheckForJumping:',1)[1].split('ProcJumping:',1)[0]
    assert 'beq InitJS' in player.split('ProcJumping:',1)[1].split('InitJS:',1)[0]
    assert 'rts' in player.split('PlayerPhysicsSub:',1)[1].split('CheckForJumping:',1)[0]
    files=('src/player.s','src/characters.s','src/guest_injury.s','src/guest_legacy_injury.s',
           'src/guest_victory_control.s','src/megaman_injury.s','src/megaman_physics.s','src/special_weapons.s',
           'src/cheats_four.s','src/luigi_native.s','src/audio/roster/contra.inc','src/expanded_weapons.s')
    bindings={name:sha256((R/name).read_bytes()).hexdigest() for name in files if (R/name).exists()}
    from check_prince_entrance_handoff_1113 import compiled_semantics
    actual=compiled_semantics(raw)
    assert actual['passed']
    return dict(passed=True,reservation='docs/qa/allocations/prince-entrance-player-1113.json',
        sole_native_profile_JSR=dict(bank=1,pc=0xa8a2),typed_numeric_references=refs,
        native1_interior_literal_targets=0,native81_constant_farcalls_into_profile=0,
        current_Rogue_raw_page_rows_excluding_native1=rogue,
        source_references=sites,current_compiled_bindings=critical,source_bindings=bindings,
        actual_compiled_control_fixtures=actual,
        MM_context_closure={
            '0_6':'Setup/lose-life do not invoke PlayerCtrlRoutine.',
            '1':'Native climbing exits PlayerPhysicsSub before fresh-jump admission.',
            '2_3_4_5_7':'Scripted AutoControlPlayer inputs0/1/4/8 have no A bit; WATCH supplies only0/1.',
            '8':'MM source movement bypasses native physics. Its native fallbacks are spring/nonzero or climbing3; native physics rejects spring before fresh-A and returns on climbing.',
            '9_12':'Guest size/flower handlers dispatch NrNativePowerupDispatch and return.',
            '10':'Legitimate modern MM injury staysengine8, masks parsed action buttons and runs MegaManHurtMovement; legacy freeze isengine9. Native injury10 is not entered by MM.',
            '11':'MM PlayerDeath dispatches MegaManDeathUpdate and returns.',
            'cheats':'CheatsActive restricts toengine8 and adds no native profile call; source movement/spring/climb gates still apply.'},
        outputs=0)


def proposal(raw):
    assert sha256(raw).hexdigest()==PARENT
    funding(raw)
    image=bytearray(raw)
    for pc,old,new in code():
        at=offset(pc);assert image[at:at+len(old)]==old
        image[at:at+len(old)]=new
    image=bytes(image)
    assert sha256(image).hexdigest()==CANDIDATE
    info=preimages(raw)
    info.update(image_SHA256=sha256(image).hexdigest(),
                cookie=image[Cache.Packet.COOKIE:Cache.Packet.COOKIE+16].hex(),
                changed_bytes=sum(a!=b for a,b in zip(raw,image)))
    assert Cache.Packet.extract(image)==Cache.Packet.extract(raw)
    return image,info


def reverse(image):
    assert sha256(image).hexdigest()==CANDIDATE
    out=bytearray(image)
    for pc,old,new in code():
        at=offset(pc);assert out[at:at+len(new)]==new
        out[at:at+len(old)]=old
    out=bytes(out)
    assert sha256(out).hexdigest()==PARENT
    assert proposal(out)[0]==image
    return out


@contextmanager
def current_binding(raw):
    """Only ROM authentication changes; the frozen controller stays byte exact."""
    import check_prince_natural_sword_1113 as P
    parent=reverse(raw)
    assert Cache.Packet.extract(raw)==Cache.Packet.extract(parent)
    with Cache.current_binding(parent):
        proof,recovery=P.proof_parent,P.recovery_controller
        def same(image):
            assert image==raw
            return proof(parent)
        text=recovery(parent)
        def same_recovery(image):
            assert image==raw
            return text
        with patch.object(P,'proof_parent',same),patch.object(P,'recovery_controller',same_recovery):
            yield


def dispatcher_abi(raw):
    """All flags/all non-MM IDs; direct immutable instruction fixtures only."""
    from verify_native_relocation import NesMPU
    preimages(raw)
    pair=[bytearray(65536) for _ in range(2)]
    for memory in pair:
        memory[0xa000:0xc000]=raw[16+8192:16+2*8192]
    new=code()[1][2]
    pair[1][PROFILE:PROFILE+len(new)]=new
    cpus=[NesMPU(memory=memory) for memory in pair]
    cases=0
    for character in range(256):
        if character==1:continue # Statically unreachable caller, not an ABI claim.
        for flags in range(256):
            results=[]
            for cpu,memory in zip(cpus,pair):
                memory[0x6002]=character
                memory[0x706]=1
                memory[0x0f]=8
                cpu.pc,cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp=PROFILE,85,7,91,flags,224
                cpu.stPushWord(0x5aff)
                for _ in range(50):
                    if cpu.pc==0x5b00:break
                    cpu.step()
                else:raise AssertionError(('Dispatcher instruction bound',character,flags))
                results.append((cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp))
            assert results[0]==results[1],(character,flags,results)
            cases+=1
    # All dry Luigi velocity/fraction values also run the unchanged native
    # routine. Its engine/water rejects and dry engine8 writes are retained.
    luigi=0
    for engine in (0,1,7,8,9,10,11,12):
        for swim in (0,1):
            for fraction in range(256):
                results=[]
                for cpu,memory in zip(cpus,pair):
                    memory[0x6002]=8;memory[0x706]=swim;memory[0xf]=engine
                    memory[0x602]=fraction;memory[0x8e]=fraction^85
                    cpu.pc,cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp=PROFILE,85,7,91,0x61,224
                    cpu.stPushWord(0x5aff)
                    for _ in range(50):
                        if cpu.pc==0x5b00:break
                        cpu.step()
                    else:raise AssertionError('Luigi native jump instruction bound')
                    results.append((cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp,memory[0x602],memory[0x8e]))
                assert results[0]==results[1],(engine,swim,fraction,results)
                luigi+=1
    return dict(passed=True,non_MM_ID_all_flags_cases=cases,Luigi_full_native_cases=luigi,
                Selected1_direct_call_ABI_claim=False,
                scope='Instruction fixtures only; caller retirement, mounted Main and ISR are separate gates.',outputs=0)


if __name__=='__main__':
    raw=frozen_parent()
    image,info=proposal(raw)
    assert reverse(image)==raw
    print(json.dumps(dict(info=info,dispatcher_ABI=dispatcher_abi(raw),
                          exact_reverse=True,Mesen=False,outputs=0)),flush=True)
