"""Measure exact owned World foreground lifetime/sole-caller funding."""
from hashlib import sha256
import argparse
from collections import Counter
from itertools import product
import json
import re
import zipfile
from unittest.mock import patch
from types import SimpleNamespace

import compose_smb2_pipe_priority_1113 as Priority
from compose_metal_head_bridge_1112 import assemble_segments

F=Priority.Check.F
SOURCE=F.R/'tools/reference/smb2_pipe_foreground_1113.s'
AT=973246
SIZE=207


def measure(raw,*,components=False,_original=True):
    if _original:assert sha256(raw).hexdigest()==F.PIN
    W=F.W;b=dict(W.Symbols.bundle(),raw=raw)
    old,new,recipe=Priority.Mirror.Flag.source_recipe(raw)
    before=new['world'];assert len(before)==SIZE
    # The owning assembler includes its supplied symbols in this result.
    constants=dict(recipe['labels'])
    constants['Player_SprAttrib']=W.address(b,'Player_SprAttrib')
    code,labels=assemble_segments(SOURCE.read_text(),{'S2_FOREGROUND_WORLD':W.address(b,'S2MainWorld')},constants)
    after=code['S2_FOREGROUND_WORLD'];assert len(after)==SIZE
    oldsrc=Priority.Mirror.Flag.Check.SOURCE.read_text().split('.segment "S2_FLAG_WORLD"',1)[1]
    assert oldsrc.count('stx S2HeadPage')==2
    assert'stx S2HeadPage'not in SOURCE.read_text()
    world=W.address(b,'S2MainWorld');word=world.to_bytes(2,'little');own=[];allcalls=[]
    for i in range(16,16+128*8192-2):
        if raw[i]in(0x20,0x4c)and raw[i+1:i+3]==word:
            allcalls.append(i)
            if(i-16)//8192==118:own.append(i)
    begin=W.location(b,'S2MainPlayer');end=W.location(b,'S2MainOwnerMask')
    assert len(own)==1 and begin<=own[0]<end
    consumer=bytes.fromhex('688d')+W.address(b,'S2HeadPage').to_bytes(2,'little')
    assert raw[own[0]+3:own[0]+7]==consumer
    native=bytes.fromhex('a5bdc9409016a50fc905f010c907f00cc9049008ad870529df8d8705')
    assert raw[8582:8582+len(native)]==native
    assert W.address(b,'S2HeadPage')==0x5c7e and W.address(b,'Player_SprAttrib')==0x587
    # The logical7ef parent has the pre-flag loop. Census the authenticated
    # current World body instead, not that superseded implementation.
    scoped=bytearray(raw);scoped[AT:AT+SIZE]=before
    target=bytes.fromhex('ad7e5c');reads=[i for i in range(16,16+128*8192-2)if scoped[i:i+3]==target]
    ownreads=[i for i in reads if(i-16)//8192==118]
    # SourceMainGame has sole8 dispatch toMainPlayer; all non8/non11 native
    # handoffs bypass source MainWorld. Bind that real current literal too.
    game=W.location(b,'S2MainGame')
    assert raw[game:game+10]==bytes.fromhex('a50fc908f016c90bf015')
    q=dict(parent_recipe_SHA256=F.PIN,successor_parent_SHA256=Priority.CANDIDATE,
        current_World_span=[AT,SIZE],current_World_SHA256=sha256(before).hexdigest(),
        current_code_bytes=recipe['world_bytes'],current_padding=recipe['world_padding'],
        new_source_SHA256=sha256(SOURCE.read_bytes()).hexdigest(),new_code_bytes=len(after),new_padding=0,
        source_owned_dead_cache_bytes=6,padding_reused_bytes=2,new_guard_bytes=8,
        sole_source_caller=own,all_raw_transfer_matches=allcalls,immediate_caller_cache_reset=consumer.hex(),
        native_priority_fragment=[8582,len(native),native.hex()],HeadPage_direct_reads=ownreads,
        cache_census_scope='Exact7ef with source-authenticated current World; priority/mirror changes contain no direct cache loads',
        new_labels={n:labels[n]for n in re.findall(r'^(\w+):',SOURCE.read_text(),re.M)},offscreen_source_pages='Unchanged early return before visible priority clearing',
        visible_policy='Actual source engine8 caller, YPage0, nativeY>=64 clears source-owned normal attribute before draw',
        no_new_RAM_ROM_CHR=True,candidate_prepared=False,outputs=0,Mesen_run=False)
    return(q,before,after,labels,b)if components else q


def parent(raw):
    return Priority.proposal(Priority.Mirror.all_mirrors_proposal(Priority.Mirror.Flag.proposal(raw)[0])[0])[0]


def pair_images(raw):
    import compose_smb2_pipe_foreground_1113 as C
    before=parent(raw);after,q=C.proposal(before)
    assert C.inverse(after)==before
    return before,after,q


def state(m,*,leaf=False,attr=False):
    """Only dead stack bytes are excluded; no scratch/SMC/audio/cache mask."""
    data=bytearray(m[:0x8000]);data[0x100:0x1e1]=bytes(225)
    if leaf:data[0x5c7e]=0  # Explicit direct-callee negative; caller test does NOT.
    if attr:data[0x587]=0
    return bytes(data),tuple(bytes(z)for z in m.ram),tuple(m.rawtags)


def finite(raw):
    before,image,q=pair_images(raw);N=F.W.N;counts=Counter();cache_differences=0
    seed=F.cold(before,4)
    def compare(fixture,kind):
        nonlocal cache_differences
        a=F.view(fixture,before);b=F.view(fixture,image)
        ra=N.invoke(a,'S2MainWorld');rb=N.invoke(b,'S2MainWorld')
        assert tuple(ra[k]for k in('A','X','Y','P'))==tuple(rb[k]for k in('A','X','Y','P')),(kind,'ABI',ra,rb)
        visible=N.get(fixture,'S2YPage')==0 and N.get(fixture,'Player_Y_Position')>=64
        # Native down-pipe creates20 after the foreground clear; retain it.
        expected=0 if visible else N.get(a,'Player_SprAttrib')
        if N.get(b,'GameEngineSubroutine')==3:expected=N.get(a,'Player_SprAttrib')
        assert N.get(b,'Player_SprAttrib')==expected,(kind,'priority',visible,expected,N.get(b,'Player_SprAttrib'))
        assert state(a,leaf=True,attr=visible)==state(b,leaf=True,attr=visible),(kind,'all nondead RAM')
        cache_differences+=N.get(a,'S2HeadPage')!=N.get(b,'S2HeadPage')
        counts[kind]+=1
        return a,b
    for page,y,headpage in product((0,1,255),(7,8,32,63,64,151,167,168,207,208,239),(0,53)):
        fixture=F.world_fixture(seed,y=y)
        N.put(fixture,S2YPage=page,S2HeadPage=headpage,Player_SprAttrib=32)
        compare(fixture,'visible_HUD_offscreen_Y_boundaries')
    for offset in range(9):
        fixture=F.world_fixture(seed,x=248,y=112)
        N.put(fixture,Player_SprAttrib=32,S2HeadPage=53)
        F.cell(fixture,248+(2,7,12)[offset%3],112+(11,22,32)[offset//3],0xc2)
        a,b=compare(fixture,'native_coin_points')
        assert N.get(b,'CoinTallyFor1Ups')==N.get(fixture,'CoinTallyFor1Ups')+1
    for tile,status in product((0x51,0x54,0x61,0xc0,0xc1,0xc4),(0,1)):
        fixture=F.world_fixture(seed)
        N.put(fixture,S2HeadX=112,S2HeadPage=0,S2HeadY=144,PlayerStatus=status,AreaType=1,Player_SprAttrib=32)
        F.cell(fixture,112,144,tile);compare(fixture,'native_head_transactions')
    for page in(0,1):
        fixture=F.world_fixture(seed,x=120,y=112,page=page,down=4)
        N.put(fixture,Player_SprAttrib=32)
        F.cell(fixture,page*256+123,144,0x10);F.cell(fixture,page*256+132,144,0x11)
        a,b=compare(fixture,'native_down_pipe')
        assert N.get(b,'GameEngineSubroutine')==3 and N.get(b,'Player_SprAttrib')&32
    accepted=0
    for variant in range(8):
        own=F.cold(before,variant)
        for nibble,y in product(range(16),(7,8,32,63,64,151,167,168,207,208)):
            fixture=F.flag_fixture(own,3152+nibble,y);N.put(fixture,Player_SprAttrib=32)
            a,b=compare(fixture,'all8_native_flag_boundary')
            yes=6<=nibble<10 and 8<=y<168
            assert(N.get(b,'GameEngineSubroutine')==4)==yes
            accepted+=yes
    assert cache_differences>0
    return dict(passed=True,ROM_SHA256=q['ROM_SHA256'],counts=dict(counts),native_flag_accepts=accepted,
        direct_callee_dead_cache_differences=cache_differences,
        direct_callee_negative_scope='HeadPage differs after consumed query; no standalone ABI claim for that dead output',
        AXYP_and_all_other_scratch_SMC_RAM_equal=True,synthetic_directed_fixtures=True,outputs=0,Mesen_run=False)


def caller(raw):
    before,image,q=pair_images(raw);N=F.W.N;counts=Counter();visited=Counter()
    sole=0xa000+(973033-16)%8192;entry=F.W.address(dict(F.W.Symbols.bundle(),raw=before),'S2MainWorld')
    native=N.NesMPU
    class Trace(native):
        def step(self):
            m=self.memory
            if self.pc==entry and m.rawtags[1]==246:visited['World']+=1
            if self.pc==sole+7 and m.rawtags[1]==246:visited['priorY_cache_restored_before_Box']+=1
            return native.step(self)
    for variant in range(8):
        seed=F.cold(before,variant)
        for pad,y in product((0,1,2,4,128,129,64,68),(32,63,64,112,176)):
            fixture=F.world_fixture(seed,y=y)
            N.put(fixture,Player_SprAttrib=32,S2Clock=0,S2State=0,S2Hurt=0,
                S2Y=y,S2YPage=0,SavedJoypadBits=pad,S2Held=0)
            a=F.view(fixture,before);b=F.view(fixture,image)
            with patch.object(N,'NesMPU',Trace):
                ra=N.invoke(a,'S2MainPlayer');rb=N.invoke(b,'S2MainPlayer')
            assert tuple(ra[k]for k in('A','X','Y','P'))==tuple(rb[k]for k in('A','X','Y','P')),(variant,pad,y,'complete caller ABI',ra,rb)
            assert N.get(a,'S2HeadPage')==N.get(b,'S2HeadPage'),('live priorY cache',variant,pad,y)
            assert N.get(b,'S2HeadPage')==y,('actual saved pre-motor Y',variant,pad,y)
            assert state(a,attr=True)==state(b,attr=True),(variant,pad,y,'complete caller RAM')
            assert N.get(b,'Player_SprAttrib')in(0,32)
            counts['all8_actual_MainPlayer_complete_Box_continuations']+=1
        # The real collision bridge's body callback consumes priorY only
        # after MainPlayer has restored it. These are explicit synthetic
        # admitted-contact fixtures, not natural enemy-contact claims.
        for prior_y,slot in product((112,176),(0,1)):
            fixture=F.world_fixture(seed,y=prior_y)
            N.put(fixture,Player_SprAttrib=32,S2Clock=0,S2State=0,S2Hurt=0,SavedJoypadBits=0,
                S2Held=0,CrossoverBehaviorVersion=1)
            a=F.view(fixture,before);b=F.view(fixture,image)
            for m in(a,b):
                N.invoke(m,'S2MainPlayer')
                assert N.get(m,'S2HeadPage')==prior_y
                N.put(m,S2VY=0,S2Fresh=0,AreaType=1)
                m[F.W.address(m.bundle,'Enemy_Flag')+slot]=1
                m[F.W.address(m.bundle,'Enemy_State')+slot]=0
                m[F.W.address(m.bundle,'Enemy_ID')+slot]=6
                m[F.W.address(m.bundle,'BoundingBox_UL_Corner')+4*(slot+1)+1]=prior_y+32
            ra=N.invoke(a,'S2MainBody',x=slot);rb=N.invoke(b,'S2MainBody',x=slot)
            assert tuple(ra[k]for k in('A','X','Y','P'))==tuple(rb[k]for k in('A','X','Y','P'))
            assert rb['P']&1 and state(a,attr=True)==state(b,attr=True)
            assert N.get(b,'Player_Y_Position')==prior_y
            counts['synthetic_admitted_body_contact_after_real_priorY_restore']+=1
    assert visited['World']==visited['priorY_cache_restored_before_Box'] and visited['World']>0
    return dict(passed=True,ROM_SHA256=q['ROM_SHA256'],counts=dict(counts),reached=dict(visited),
        no_HeadPage_scratch_SMC_audio_mask=True,complete_return_AXYP_SP_equal=True,
        synthetic_positions_ordinary_pad_and_real_motor=True,outputs=0,Mesen_run=False)


def references(raw):
    before,image,q=pair_images(raw);W=F.W;b=dict(W.Symbols.bundle(),raw=before)
    measured,old,new,labels,_=measure(raw,components=True)
    assert measured['HeadPage_direct_reads']==[971050,973268,973658]
    source=(F.R/'src/smb2_roster_main_v2.s').read_text()
    body=source.split('.proc S2MainPlayer\n',1)[1].split('.endproc',1)[0]
    names=set(re.findall(r'\b[A-Za-z_][A-Za-z_0-9]*\b',body))
    symbols={n:W.address(b,n)for n in names if n in b['syms']}
    compiled=assemble_segments('.segment "CALLER"\n'+Priority.Check.normalized(body),
        {'CALLER':W.address(b,'S2MainPlayer')},symbols)[0]['CALLER']
    at=W.location(b,'S2MainPlayer')
    assert before[at:at+len(compiled)]==compiled and image[at:at+len(compiled)]==compiled
    # All changed internal coin/helper labels are private to this source body.
    oldlabels=Priority.Mirror.Flag.source_recipe(raw)[2]['labels'];inbound={}
    own_start=16+118*8192;own_end=own_start+8192
    for name in('WorldCoins','WorldFlag','WorldCoinStart','WorldCoinLoop','WorldCoinNext',
        'WorldPipe','WorldDone','WorldPlayerCell','WorldCoinX','WorldCoinY'):
        pc=oldlabels[name];word=pc.to_bytes(2,'little')
        outside=[i for i in range(own_start,own_end-1)if before[i:i+2]==word and not AT<=i<AT+SIZE]
        assert not outside,(name,'unclosed current-bank external pointer',outside)
        literal=bytes((0xa9,pc&255,0x8d,0x6c,1,0xa9,pc>>8,0x8d,0x6d,1,0xa9,246))
        assert literal not in before[16:16+128*8192],(name,'unexpected farcall')
        inbound[name]=dict(old=pc,new=labels[name],outside_own_words=outside)
    # The two other raw B9AE transfers live in distinct A-window banks; their
    # target is their own bank's B9AE, not bank118. They remain byte-identical.
    foreign=[]
    for at in(214760,524036):
        bank=(at-16)//8192;pc=0xa000+(at-16)%8192
        assert bank!=118 and before[at:at+3]==image[at:at+3]
        foreign.append(dict(file=at,physical_bank=bank,CPU=pc,hex=before[at:at+3].hex()))
    assert image[:AT]==before[:AT]and image[AT+SIZE:]==before[AT+SIZE:]
    assert image[AT+SIZE:AT+SIZE+16]==before[AT+SIZE:AT+SIZE+16]
    return dict(passed=True,ROM_SHA256=q['ROM_SHA256'],exact_source_MainPlayer_bytes=len(compiled),
        sole_same_bank_caller=measured['sole_source_caller'],immediate_cache_reset=measured['immediate_caller_cache_reset'],
        HeadPage_reads=dict(head_callback_before_World=971050,World_early_head=973268,Body_after_caller_reset=973658),
        moved_private_reference_closure=inbound,unrelated_raw_transfer_matches=foreign,
        following_MainPickup_and_all_other_bytes_exact=True,outputs=0,Mesen_run=False)


def render(raw):
    """Real World->DrawBody, including all existing pose producer inputs."""
    before,image,q=pair_images(raw);N=F.W.N;counts=Counter();native_map=(0,3,2,1,0,1,2,3)
    for variant in range(8):
        seed=F.cold(before,variant)
        for size,face,held,animation in product((0,1),(0,1),(0,1),range(11)):
            fixture=F.world_fixture(seed,y=112)
            N.put(fixture,S2Size=size,S2Face=face,S2Holding=held,S2Animation=animation,S2Hurt=0,
                CurrentOAMOffset=0,GuestOamRotationActive=0,Player_SprAttrib=32)
            a=F.view(fixture,before);b=F.view(fixture,image)
            # Reference foreground is the old source's intended normal zero;
            # new path must obtain that value through the actual World worker.
            N.put(a,Player_SprAttrib=0)
            N.invoke(a,'S2MainWorld');N.invoke(b,'S2MainWorld')
            assert N.get(b,'Player_SprAttrib')==0
            ra=N.invoke(a,'S2DrawBody');rb=N.invoke(b,'S2DrawBody')
            assert tuple(ra[k]for k in('A','X','Y','P'))==tuple(rb[k]for k in('A','X','Y','P'))
            assert bytes(a[0x200:0x300])==bytes(b[0x200:0x300])
            assert a.chr_latches==b.chr_latches and bytes(a[0x5c90:0x5ca1])==bytes(b[0x5c90:0x5ca1])
            assert N.get(b,'R3')==0 and N.get(b,'R5')==0
            assert tuple(N.get(b,n)for n in('S2Variant','S2NativeCharacter','S2Size','S2Face','S2Holding','S2Animation'))==(
                variant,native_map[variant],size,face,held,animation),'Ensure reset instead of pose coverage'
            counts['all8_normal_World_to_actual_native_OAM_pose_color_CHR']+=1
        for sourcepage,y in((0,32),(0,63),(1,112),(255,112)):
            fixture=F.world_fixture(seed,y=y)
            N.put(fixture,S2YPage=sourcepage,Player_SprAttrib=32,CurrentOAMOffset=0,GuestOamRotationActive=0)
            a=F.view(fixture,before);b=F.view(fixture,image)
            for m in(a,b):
                N.invoke(m,'S2ExportPosition')
                assert N.get(m,'Player_Y_HighPos')==(sourcepage+1)&255
                N.invoke(m,'S2MainWorld');N.invoke(m,'S2DrawBody')
            assert N.get(b,'Player_SprAttrib')==32 and bytes(a[0x200:0x300])==bytes(b[0x200:0x300])
            counts['HUD_and_offscreen_priority_OAM_unchanged']+=1
    return dict(passed=True,ROM_SHA256=q['ROM_SHA256'],counts=dict(counts),
        actual_8constructor_classes=list(native_map),all11_source_animations_without_reset=True,
        normal_foreground_OAM_equal_original_zero_contract=True,synthetic_render_inputs=True,outputs=0,Mesen_run=False)


def faults(raw):
    import compose_smb2_pipe_foreground_1113 as C
    before,image,q=pair_images(raw);N=F.W.N;W=F.W;b=dict(W.Symbols.bundle(),raw=before)
    member='build/doki-current-component-1101-v1/src/smb2_roster_core.s'
    with zipfile.ZipFile(Priority.Check.ARCHIVE)as z:source=z.read(member).decode()
    export=source.split('.proc S2ExportPosition\n',1)[1].split('.endproc',1)[0]
    names=set(re.findall(r'\b[A-Za-z_][A-Za-z_0-9]*\b',export))
    symbols={n:W.address(b,n)for n in names if n in b['syms']}
    compiled=assemble_segments('.segment "EXPORT"\n'+Priority.Check.normalized(export),
        {'EXPORT':W.address(b,'S2ExportPosition')},symbols)[0]['EXPORT']
    at=W.location(b,'S2ExportPosition');assert before[at:at+len(compiled)]==compiled
    seed=F.cold(image,4);pages=[]
    for page in(0,1,255):
        m=F.world_fixture(seed,y=112);N.put(m,S2YPage=page,Player_SprAttrib=32)
        N.invoke(m,'S2ExportPosition');N.invoke(m,'S2MainWorld')
        assert N.get(m,'Player_Y_HighPos')==(page+1)&255
        assert N.get(m,'Player_SprAttrib')==(0 if page==0 else 32)
        pages.append(dict(source_page=page,native_high=N.get(m,'Player_Y_HighPos'),attribute=N.get(m,'Player_SprAttrib')))
    positions=sorted(set(range(AT,AT+SIZE))|{0,AT-1,AT+SIZE,972351,972799,len(image)-1})
    failures=Counter()
    for which,base,fn in(('parent',before,C.proposal),('candidate',image,C.inverse)):
        for at in positions:
            z=bytearray(base);z[at]^=1
            try:fn(bytes(z))
            except AssertionError:failures[which]+=1
            else:raise AssertionError(('Accepted corrupt strict image',which,at))
    return dict(passed=True,ROM_SHA256=q['ROM_SHA256'],exact_inverse_and_forward=True,
        corrupt_preimage_and_successor_rejections=dict(failures),no_installed_image_dependency_in_inverse=True,
        exact_Ready85_export_source_bytes=len(compiled),source_member_SHA256=sha256(source.encode()).hexdigest(),
        actual_source_export_page_contract=pages,outputs=0,Mesen_run=False)


def normalization(raw):
    import compose_smb2_foreground_current_1113 as Current
    public=F.ROM.read_bytes()
    if sha256(public).hexdigest()==Current.CANDIDATE:public=Current.inverse(public)
    assert sha256(public).hexdigest()==Current.PIN
    merged,_=Current.proposal(public);assert Current.inverse(merged)==public
    with patch.object(F,'Path',lambda path:SimpleNamespace(read_bytes=lambda:merged)):
        assert F.load_input('memory-only3684')==raw
    bad=bytearray(merged);bad[0]^=1
    with patch.object(F,'Path',lambda path:SimpleNamespace(read_bytes=lambda:bytes(bad))):
        try:F.load_input('unknownimage')
        except AssertionError:pass
        else:raise AssertionError('Unknown CLI image accepted')
    return dict(passed=True,explicit_CLI_only_path=[Current.CANDIDATE,Current.PIN,F.PIN],
        strict_private_proposal_and_inverse_PINs_unchanged=True,outputs=0,Mesen_run=False)


def cache_lifetime(raw):
    before,image,q=pair_images(raw);N=F.W.N;W=F.W;counts=Counter();reads=[]
    seed=F.cold(image,4);world=measure(raw)['new_labels']['WorldCoins'];reset=0xa000+(973033-16)%8192+4
    busclass=type(seed);getter=busclass.__getitem__;native=N.NesMPU
    def checked_get(m,at):
        if isinstance(at,int)and at==0x5c7e and getattr(m,'cache_consumed',False):
            reads.append(dict(pc=getattr(m,'current_cpu_pc',None),value=getter(m,at)))
        return getter(m,at)
    class Trace(native):
        def step(self):
            m=self.memory;m.current_cpu_pc=self.pc
            if m.rawtags[1]==246:
                if self.pc==world:m.cache_consumed=True;counts['consumed_intervals']+=1
                elif self.pc==reset:
                    assert m.cache_consumed
                    assert bytes(m[self.pc:self.pc+3])==bytes.fromhex('8d7e5c')
                    m.cache_consumed=False;counts['actual_caller_priorY_resets']+=1
            return native.step(self)
    with patch.object(busclass,'__getitem__',checked_get),patch.object(N,'NesMPU',Trace):
        for pad,y in product((0,1,2,4,128,129,64,68),(32,63,64,112,176)):
            fixture=F.world_fixture(seed,y=y)
            N.put(fixture,Player_SprAttrib=32,S2Clock=0,S2State=0,S2Hurt=0,SavedJoypadBits=pad,S2Held=0)
            N.invoke(fixture,'S2MainPlayer')
            assert not fixture.cache_consumed
            counts['real_complete_MainPlayer_calls']+=1
    assert not reads and counts['consumed_intervals']==counts['actual_caller_priorY_resets']
    return dict(passed=True,ROM_SHA256=q['ROM_SHA256'],counts=dict(counts),
        every_actual_CPU_cache_read_monitored=True,reads_after_consumption_before_real_priorY_reset=reads,
        no_scratch_SMC_cache_audio_mask=True,synthetic_position_and_pad_matrix=True,outputs=0,Mesen_run=False)


def handoffs(raw):
    import check_smb2_foot_mirror_1113 as Fixed
    before,image,q=pair_images(raw);N=F.W.N;W=F.W;seed=F.cold(before,4)
    # Reuse the authenticated actual boundary runner, substituting only its
    # explicit pair. Demand whole RAM here: no query-scratch/dead-stack mask.
    with patch.object(Priority.Mirror.Flag,'proposal',return_value=(image,q)),patch.object(F,'comparable',Fixed.exact_state):
        foreign=F.foreign(before)
    previews=[]
    for rom in(before,image):
        with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(dict(seed.bundle,raw=rom),0)
        for key in(4,4,4):W.UI.key(m,key)
        rows=[]
        for variant in range(8):
            rows.append((bytes(m[0x200:0x300]),bytes(m.vram),tuple(m.chr_latches)))
            W.UI.key(m,32)
        previews.append(rows)
    assert previews[0]==previews[1]
    start=W.address(seed.bundle,'FarCallCommon');target=W.address(seed.bundle,'S2MainGame')
    game_at=W.location(seed.bundle,'S2MainGame');game=before[game_at:game_at+28]
    # This source-native handoff saves A into016A first; the outer raw-owner
    # boundary has a different A14D target. Bind this actual literal separately.
    assert game==bytes.fromhex('a50fc908f016c90bf0158d6a01a9218d6c01a9a08d6d01a9814c5a01')
    native_target=game[14]+256*game[19]
    cases=0
    def native_handoff(m,engine):
        N.put(m,GameEngineSubroutine=engine,Player_SprAttrib=32)
        m[W.address(m.bundle,'SafecallA_SMC')+1]=85
        m[W.address(m.bundle,'FarcallJmpTarget_SMC')+1]=target&255
        m[W.address(m.bundle,'FarcallJmpTarget_SMC')+2]=target>>8
        c=N.NesMPU(memory=m,pc=start);c.a=246;c.x=7;c.y=91;c.p=0x31;c.sp=224;c.stPushWord(0x5aff)
        for step in range(2000):
            if step and c.pc==start and c.a==129:
                to=m[W.address(m.bundle,'FarcallJmpTarget_SMC')+1]+256*m[W.address(m.bundle,'FarcallJmpTarget_SMC')+2]
                assert to==native_target,(engine,hex(to),hex(native_target))
                assert N.get(m,'Player_SprAttrib')==32
                return(c.a,c.x,c.y,c.p,c.sp,c.pc)
            assert not(m.rawtags[1]==246 and 0xb9ae<=c.pc<0xba7d),'Non8 native handoff reached World'
            assert m[c.pc];c.step()
        raise AssertionError('Native handoff bound')
    for engine in(0,1,2,3,4,5,6,7,9,10):
        a=F.view(seed,before);b=F.view(seed,image)
        assert native_handoff(a,engine)==native_handoff(b,engine)
        assert Fixed.exact_state(a)==Fixed.exact_state(b);cases+=1
    return dict(passed=True,ROM_SHA256=q['ROM_SHA256'],all_non25_actual_gate_whole_RAM_pairs=foreign['legacy_entry_pairs'],
        real8menu_preview_OAM_VRAM_CHR_pairs=8,native_non8_non11_handoff_pairs=cases,
        authenticated_native_GameRoutines_target=native_target,
        native_pipe_end_latches_preserved=True,uninitialized_foreign_native_physics_executed=False,outputs=0,Mesen_run=False)


def vectors(raw):
    """Actual original IRQ/busy-NMI plus changed foreground continuation."""
    import check_smb2_foot_mirror_1113 as Fixed
    import check_bub_current_budget_1113 as Frames
    before,image,q=pair_images(raw);N=F.W.N;seed=F.cold(image,4);busy=None
    for tick in range(240):
        seed.controller_pad=1;Frames.frame(seed)
        if N.get(seed,'S2AudioActiveBank')in(119,120)and seed[0x4015]&16 and not N.get(seed,'S2Clock')&8:
            busy=dict(Main=tick+1,x=N.get(seed,'Player_X_Position')+256*N.get(seed,'Player_PageLoc'),
                y=N.get(seed,'Player_Y_Position'),health=N.get(seed,'S2Health'),bank=N.get(seed,'S2AudioActiveBank'))
            break
    assert busy
    native=N.NesMPU;busclass=type(seed);getter=busclass.__getitem__
    points=set();counts=Counter();minimum=255;music=0;testing=False;cache_reads=[]
    def getter_checked(m,at):
        if isinstance(at,int)and at==0x5c7e and getattr(m,'in_actual_ISR',False):cache_reads.append(m.current_irq_pc)
        return getter(m,at)
    class Probe(native):
        _origin=None
        def irq(self):
            self._origin=(self.pc,self.sp);self.memory.in_actual_ISR=True
            return native.irq(self)
        def nmi(self):
            self._origin=(self.pc,self.sp);self.memory.in_actual_ISR=True
            return native.nmi(self)
        def step(self):
            nonlocal testing,minimum,music
            m=self.memory
            if self._origin:
                if(self.pc,self.sp)==self._origin:self._origin=None;m.in_actual_ISR=False
                else:
                    m.current_irq_pc=self.pc
                    assert not(m.rawtags[1]==246 and 0xb9ae<=self.pc<0xba7d),'ISR entered Main-only World'
            tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else -1
            if not testing and tag==246 and 0xb9ae<=self.pc<0xba7d:
                key=(self.pc,self.sp,self.p&4)
                if key not in points:
                    points.add(key);testing=True
                    for kind in('IRQ','busy-lagNMI'):
                        if kind=='IRQ'and self.p&4:continue
                        low,advance=Fixed.paired_interrupt(m,self,before,image,kind)
                        minimum=min(minimum,low);counts[kind]+=1
                        if kind=='busy-lagNMI':music+=advance
                    testing=False
            result=native.step(self)
            # The paired runner stops immediately on RTI, before another
            # foreground step; do not count its later snapshot as ISR reads.
            if self._origin and(self.pc,self.sp)==self._origin:
                self._origin=None;m.in_actual_ISR=False
            return result
    with patch.object(busclass,'__getitem__',getter_checked),patch.object(N,'NesMPU',Probe):
        for x,y in((3155,151),(3158,151),(3158,32),(3158,207)):
            m=F.flag_fixture(seed,x,y);N.put(m,Player_SprAttrib=32,NmiDisable=255)
            N.invoke(m,'S2MainWorld')
        for tile in(0,0xc0,0xc1,0xc2,0x54):
            m=F.world_fixture(seed);N.put(m,Player_SprAttrib=32,NmiDisable=255)
            if tile==0xc2:F.cell(m,119,134,tile)
            elif tile:
                N.put(m,S2HeadX=112,S2HeadPage=0,S2HeadY=144);F.cell(m,112,144,tile)
            N.invoke(m,'S2MainWorld')
        m=F.world_fixture(seed,x=120,down=4);N.put(m,Player_SprAttrib=32,NmiDisable=255)
        F.cell(m,123,144,0x10);F.cell(m,132,144,0x11);N.invoke(m,'S2MainWorld')
        for y in(32,63,64,176):
            m=F.world_fixture(seed,y=y)
            N.put(m,Player_SprAttrib=32,NmiDisable=255,S2Clock=0,SavedJoypadBits=1)
            N.invoke(m,'S2MainPlayer')
    assert counts['IRQ']and counts['busy-lagNMI']and music and minimum>=128 and not cache_reads,dict(
        counts=dict(counts),music=music,minimum=minimum,cache_reads=cache_reads[:8],cache_read_count=len(cache_reads))
    return dict(passed=True,ROM_SHA256=q['ROM_SHA256'],reached_changed_instruction_SP_points=len(points),
        actual_paired_vectors=dict(counts),minimum_SP=minimum,genuine_busy_source_prefix=busy,
        exact_paired_music_advances=music,actual_ISR_HeadPage_read_attempts=cache_reads,
        no_audio_clock_SMC_cache_scratch_stack_mask=True,whole_original_ISR_and_new_foreground_continuation_equal=True,
        synthetic_transaction_inputs=True,outputs=0,Mesen_run=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in('finite','caller','references','render','cache','vectors','handoffs','faults','normalization'):p.add_argument('--'+name,action='store_true')
    args=p.parse_args();raw=F.load_input()
    q=finite(raw)if args.finite else caller(raw)if args.caller else references(raw)if args.references else render(raw)if args.render else cache_lifetime(raw)if args.cache else vectors(raw)if args.vectors else handoffs(raw)if args.handoffs else faults(raw)if args.faults else normalization(raw)if args.normalization else measure(raw)
    print(json.dumps(q,separators=(',',':')),flush=True)
