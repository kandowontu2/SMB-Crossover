"""Read-only exact-current SMB2 native flag handoff ownership inspection."""
from hashlib import sha256
import argparse
from collections import Counter
from unittest.mock import patch
import json
from pathlib import Path

import check_ff_white_mushroom_current_1110 as W

PIN='7ef2de351d3a4ae60b3ada2eb1aa56b330873dc106ad43428ec6803bf420d4fc'
ROM=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
R=Path(__file__).resolve().parents[2]
SOURCE=R/'tools/reference/smb2_flag_handoff_1113.s'


def load_input(path=ROM):
    """CLI adapter only; strict proposal/controller/inverse PINs are unchanged."""
    raw=Path(path).read_bytes();digest=sha256(raw).hexdigest()
    if digest=='12397b1c2557834f6a2b7e23c9915d5dc40c6cabff7a6ee844c1adebf6564c52':
        source=R/'tools/audit/compose_smb2_postbg_mirror_1113.py'
        assert sha256(source.read_bytes()).hexdigest()=='415ca42d6efe1023a56c147a2d1dc0c8e32c75c98fef31b9f1a54e0fb71b7647'
        import compose_smb2_postbg_mirror_1113 as PostBG
        raw=PostBG.inverse(raw);digest=sha256(raw).hexdigest()
    if digest=='3684f3d2a418a484befd80fca351d0dc5f9b472f6f067a0a7894994ea343679d':
        source=R/'tools/audit/compose_smb2_foreground_current_1113.py'
        assert sha256(source.read_bytes()).hexdigest()=='3cade46f267ab926384de0687d59670b0fc16f5ea27b821aa683a973936d05f2'
        import compose_smb2_foreground_current_1113 as Current
        raw=Current.inverse(raw);digest=sha256(raw).hexdigest()
    if digest=='f88cfe5aee15bb3921c691b7f06d905246be9ff88b9b43eea71c2405722724a7':
        source=R/'tools/audit/bub_native_noops_1113.py'
        assert sha256(source.read_bytes()).hexdigest()=='6770cb6c8c9a0fe73eebd8c2c9b4c112ee55dc81def05c9aaf280b5a14e718e6'
        import bub_native_noops_1113 as Bub
        raw=Bub.combined_reverse(raw);digest=sha256(raw).hexdigest()
    assert digest==PIN
    return raw


def inspect(raw):
    assert sha256(raw).hexdigest()==PIN
    b=dict(W.Symbols.bundle(),raw=raw)
    names=('S2ComponentStart','S2NativeEnd','S2ComponentEnd','S2MainBegin','S2MainEndCode','S2MainWorld',
        'S2MainCell','S2WorldInteraction','S2GroundInteraction','S2PaletteLifecycleEnd','S2MainGatesEnd',
        'S2PaletteCDataEnd','HandleClimbing','FlagpoleCollision','CheckForCoinMTiles','HandleCoinMetatile',
        'PlayerHeadCollision')
    rows={}
    for name in names:
        try:
            pc,at=W.address(b,name),W.location(b,name)
            rows[name]=dict(pc=pc,pc_hex=hex(pc),file=at,bank=(at-16)//8192,bytes=raw[at:at+20].hex())
        except (KeyError,AssertionError)as error:rows[name]=dict(unavailable=str(error))
    for name in('S2ComponentEnd','S2MainEndCode'):
        if 'file'not in rows[name]:continue
        row=rows[name];n=8192-(row['file']-16)%8192;tail=raw[row['file']:row['file']+n]
        row['remaining_bank_bytes']=n;row['tail_SHA256']=sha256(tail).hexdigest()
        row['tail_values']=sorted(set(tail));row['tail_prefix']=tail[:64].hex()
    start=W.location(b,'S2MainWorld');end=W.location(b,'S2MainPickup')
    call=b'\x20'+W.address(b,'CheckForCoinMTiles').to_bytes(2,'little')
    body=raw[start:end]
    coins=[start+i for i in range(len(body)-2)if body[i:i+3]==call]
    post=[]
    for name,sym in b['syms'].items():
        if 'seg'not in sym:continue
        pc=int(sym['val'],0)
        if not 0xbead<=pc<0xc000:continue
        at=W.location(b,name)
        if(at-16)//8192==118:post.append(dict(name=name,pc=pc,file=at))
    segment=b['segs'][b['syms']['S2MainWorld']['seg']]
    attr=W.location(b,'MTileAttribute')
    return dict(ROM_SHA256=PIN,symbols=rows,flag_attributes={str(t):raw[attr+t]for t in(0x24,0x25,0x26,0x61)},world_segment=segment,post_main_symbols=sorted(post,key=lambda r:r['pc']),world_span=[start,end],world_SHA256=sha256(body).hexdigest(),coin_calls=coins,
        source_stub=(R/'src/smb2_roster_terrain.s').read_text().split('.proc S2WorldInteraction',1)[1].split('.endproc',1)[0],
        code_space_granted=False,ROM_or_state_writes=0,outputs=0,Mesen_run=False)


def measure(raw):
    from compose_metal_head_bridge_1112 import assemble_segments
    assert sha256(raw).hexdigest()==PIN
    b=dict(W.Symbols.bundle(),raw=raw)
    names=('R0','R1','R2','R4','R5','R6','R7','S2X','S2Y','S2Page','S2YPage','S2ProbeDirection',
        'S2HeadX','S2HeadPage','S2HeadY','S2Math0','S2DF011','S2DF055','GetBlockBufferAddr','MTileAttribute',
        'AreaType','BlockBounceTimer','S2MainCell','PlayerHeadCollision','S2MainVelocity','Player_Y_Position',
        'BlockBufferColli_Side','HandleClimbing','GameEngineSubroutine','CheckForCoinMTiles','HandleCoinMetatile',
        'S2Air','Up_Down_Buttons','HandlePipeEntry')
    constants={n:W.address(b,n)for n in names}
    origins=dict(S2_FLAG_PROBE=W.address(b,'S2NativeTileProbe'),S2_FLAG_WORLD=W.address(b,'S2MainWorld'))
    code,labels=assemble_segments(SOURCE.read_text(),origins,constants)
    probe_begin=W.location(b,'S2NativeTileProbe');probe_end=W.location(b,'S2GroundInteraction')
    world_begin=W.location(b,'S2MainWorld');world_end=W.location(b,'S2MainPickup')
    return dict(ROM_SHA256=PIN,source_SHA256=sha256(SOURCE.read_bytes()).hexdigest(),
        probe=dict(origin=origins['S2_FLAG_PROBE'],old_bytes=probe_end-probe_begin,new_bytes=len(code['S2_FLAG_PROBE']),
            shared_return=labels['S2FlagSharedReturn'],expected_world_stub=W.address(b,'S2WorldInteraction'),
            preimage_SHA256=sha256(raw[probe_begin:probe_end]).hexdigest()),
        world=dict(origin=origins['S2_FLAG_WORLD'],old_bytes=world_end-world_begin,new_bytes=len(code['S2_FLAG_WORLD']),
            preimage_SHA256=sha256(raw[world_begin:world_end]).hexdigest()),
        constants=constants,labels=labels,no_ROM_candidate=True,new_state_bytes=0,outputs=0,Mesen_run=False)


def cold(raw,variant):
    import check_bub_current_budget_1113 as Frames
    N=W.N;b=dict(W.Symbols.bundle(),raw=raw)
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
    for key in(4,4,4):W.UI.key(m,key)
    for _ in range(variant):W.UI.key(m,32)
    assert N.get(m,'SelectedCharacter')==25 and N.get(m,'S2Variant')==variant
    start=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    N.invoke(m,'PauseRoutine',a=0)
    for epoch in range(700):
        if tuple(N.get(m,k)for k in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):
            assert N.get(m,'S2Ready')==178 and N.get(m,'S2Health')==31
            return m
        m.controller_pad=0;Frames.frame(m,cold=True)
    raise AssertionError('SMB2 actual menu/constructor bound')


def view(seed,raw):
    m=W.N.fork(seed);m.bundle=dict(seed.bundle,raw=raw)
    for slot,tag in enumerate(tuple(m.rawtags)):m.raw_page(slot,tag)
    return m


def cell(m,x,y,t):
    assert 32<=y<240
    at=W.address(m.bundle,'Block_Buffer_1')+((x//256)%2)*208+((y-32)//16)*16+(x%256)//16
    m[at]=t


def flag_fixture(seed,x,y):
    """Explicit synthetic cell/position fixture, never a natural route claim."""
    N=W.N;m=N.fork(seed)
    N.put(m,Player_X_Position=x&255,Player_PageLoc=x>>8,Player_Y_Position=y,Player_Y_HighPos=1,
        Player_State=0,PlayerFacingDir=1,Player_X_Speed=0,Player_Y_Speed=0,ScreenLeft_X_Pos=0xb8,
        ScreenLeft_PageLoc=11,ScreenRight_X_Pos=0xb7,ScreenRight_PageLoc=12,GameEngineSubroutine=8,
        ScrollLock=0,FlagpoleSoundQueue=0,EventMusicQueue=0,S2HeadY=0,S2YPage=0,S2Air=0,
        S2X=x&255,S2Page=x>>8,S2Y=y,S2Held=0,Up_Down_Buttons=0,BlockBounceTimer=0)
    base=W.address(m.bundle,'Block_Buffer_1')
    for i in range(416):m[base+i]=0
    for yy in range(32,192,16):cell(m,3168,yy,0x24 if yy==32 else 0x25)
    cell(m,3168,192,0x61)
    for xx in range(3072,3328,16):cell(m,xx,208,0x54)
    return m


def cpu_matrix(raw):
    import compose_smb2_flag_handoff_1113 as C
    N=W.N;image,info=C.proposal(raw);assert C.inverse(image)==raw
    seed=cold(raw,4);pairs=0;intentional=0
    # Every raw native tile, both carry inputs, player/object callback owners.
    for tile in range(256):
      for direction in range(4):
        for owner in(0,3):
            for flags in(0x30,0x31):
                a=view(seed,raw);b=view(seed,image)
                for m in(a,b):
                    base=W.address(m.bundle,'Block_Buffer_1')
                    for i in range(416):m[base+i]=tile
                    for index in range(4):
                        m[W.address(m.bundle,'S2X')+index]=112;m[W.address(m.bundle,'S2Page')+index]=0
                        m[W.address(m.bundle,'S2Y')+index]=112;m[W.address(m.bundle,'S2YPage')+index]=0
                    N.put(m,S2ProbeDirection=direction,S2Math0=93)
                ra=N.invoke(a,'S2NativeTileProbe',x=owner,y=6,p=flags)
                rb=N.invoke(b,'S2NativeTileProbe',x=owner,y=6,p=flags)
                if tile in(0x24,0x25):
                    assert N.get(a,'S2Math0')==255 and N.get(b,'S2Math0')==0
                    intentional+=1
                else:
                    assert tuple(ra[k]for k in('A','X','Y','P'))==tuple(rb[k]for k in('A','X','Y','P')),(tile,owner,ra,rb)
                    assert bytes(a[:0x8000])==bytes(b[:0x8000]),('non-flag probe RAM',tile,direction,owner)
                    assert a.ram==b.ram and a.rawtags==b.rawtags
                    pairs+=1
    accepted=0;rejected=0;openings=[]
    for variant in range(8):
        own=cold(image,variant);openings.append(dict(variant=variant,health=N.get(own,'S2Health'),size=N.get(own,'S2Size'),ready=N.get(own,'S2Ready')))
        for nibble in range(16):
            for y in(7,8,32,151,152,167,168,207,208):
                m=flag_fixture(own,3152+nibble,y)
                result=N.invoke(m,'S2MainWorld',p=0x31)
                yes=6<=nibble<10 and 8<=y<168
                assert(N.get(m,'GameEngineSubroutine')==4)==yes,(variant,nibble,y,result,N.get(m,'GameEngineSubroutine'))
                if yes:
                    assert N.get(m,'Player_State')==3 and N.get(m,'ScrollLock')==1
                    assert N.get(m,'FlagpoleCollisionYPos')==y and N.get(m,'Player_X_Speed')==0
                    assert N.get(m,'FlagpoleSoundQueue')!=0
                    accepted+=1
                else:rejected+=1
                assert N.get(m,'S2Health')==31 and N.get(m,'NumberofLives')==2
    return dict(passed=True,ROM_SHA256=info['ROM_SHA256'],exact_inverse=True,
        synthetic_directed_fixtures=True,unchanged_nonflag_AXYP_RAM_cases=pairs,intentional_flag_passability_cases=intentional,
        actual_menu_openings=openings,native_flag_accepts=accepted,native_thin_or_cell_rejections=rejected,
        natural_fullstage_claim=False,outputs=0,Mesen_run=False)


def comparable(m):
    # R0..R7 are the documented Main query scratch. Stack below the returned
    # SP is dead; the actual caller/continuation is compared separately.
    native=bytes(m[:3])+bytes(m[11:0x100])+bytes(m[0x1e1:0x8000])
    return native,tuple(bytes(z)for z in m.ram),tuple(m.rawtags)


def world_fixture(seed,*,x=112,y=112,page=0,down=0,air=0):
    N=W.N;m=N.fork(seed)
    N.put(m,S2X=x,S2Page=page,S2Y=y,S2YPage=0,S2Air=air,S2Held=down,
        Up_Down_Buttons=down,S2HeadY=0,Player_X_Position=x,Player_PageLoc=page,
        Player_Y_Position=y,Player_Y_HighPos=1,Player_State=0,Player_X_Speed=0,
        Player_Y_Speed=0,BlockBounceTimer=0,GameEngineSubroutine=8)
    start=W.address(m.bundle,'Block_Buffer_1')
    for i in range(416):m[start+i]=0
    return m


def controls(raw):
    """Synthetic cell transactions plus actual MainPlayer continuations."""
    import compose_smb2_flag_handoff_1113 as C
    import check_bub_current_budget_1113 as Frames
    N=W.N;image,info=C.proposal(raw);seed=cold(raw,4);counts=Counter()
    # Match all source coin point locations/order, page carry, bounds, Down
    # pipe pairs and native head writers against the authenticated parent.
    for page in(0,1):
        for x in(112,248):
            for y in(7,32,112,207,239):
                for down,air in((0,0),(4,0),(4,1)):
                    fixture=world_fixture(seed,x=x,y=y,page=page,down=down,air=air)
                    a=view(fixture,raw);b=view(fixture,image)
                    N.invoke(a,'S2MainWorld');N.invoke(b,'S2MainWorld')
                    assert comparable(a)==comparable(b),('nonflag world',page,x,y,down,air)
                    counts['empty_world_page_bounds_pipe_inputs']+=1
    for offset in range(9):
        fixture=world_fixture(seed,x=248,y=112,page=0)
        xx=248+(2,7,12)[offset%3];yy=112+(11,22,32)[offset//3]
        cell(fixture,xx,yy,0xc2)
        a=view(fixture,raw);b=view(fixture,image)
        N.invoke(a,'S2MainWorld');N.invoke(b,'S2MainWorld')
        assert comparable(a)==comparable(b),('native coin point',offset)
        assert N.get(b,'CoinTallyFor1Ups')==N.get(fixture,'CoinTallyFor1Ups')+1
        counts['actual_native_coin_writer_points']+=1
    for tile in(0x51,0x54,0x61,0xc0,0xc1,0xc4):
        for status in(0,1):
            fixture=world_fixture(seed)
            N.put(fixture,S2HeadX=112,S2HeadPage=0,S2HeadY=144,PlayerStatus=status,
                AreaType=1,BlockBounceTimer=0)
            cell(fixture,112,144,tile)
            a=view(fixture,raw);b=view(fixture,image)
            N.invoke(a,'S2MainWorld');N.invoke(b,'S2MainWorld')
            assert comparable(a)==comparable(b),('native head',tile,status)
            counts['actual_native_head_writer_pairs']+=1
    for page in(0,1):
        fixture=world_fixture(seed,x=120,y=112,page=page,down=4)
        cell(fixture,page*256+123,144,0x10)
        cell(fixture,page*256+132,144,0x11)
        a=view(fixture,raw);b=view(fixture,image)
        N.invoke(a,'S2MainWorld');N.invoke(b,'S2MainWorld')
        assert comparable(a)==comparable(b),('native pipe transaction',page)
        assert N.get(b,'GameEngineSubroutine')==3
        counts['actual_native_down_pipe_entries']+=1
    # Real input publisher -> source motor -> rewritten World -> original Box
    # continuation consumes the dead query scratch and returns identical ABI.
    for pad in(0,1,2,4,128,129,130,64,68):
        for steps in(1,3):
            a=view(seed,raw);b=view(seed,image)
            for _ in range(steps):
                for m in(a,b):
                    m.controller_pad=pad;Frames.frame(m)
            assert comparable(a)==comparable(b),('actual Main continuation',pad,steps)
            counts['actual_Main_NMI_continuations']+=1
    return dict(passed=True,ROM_SHA256=info['ROM_SHA256'],synthetic_cells=True,
        actual_Menu_Main_inputs=True,counts=dict(counts),outputs=0,Mesen_run=False)


def foreign(raw):
    """Stop at genuine legacy entry; never run uninitialized foreign physics."""
    import compose_smb2_flag_handoff_1113 as C
    N=W.N;image,info=C.proposal(raw);seed=cold(raw,4)
    gate=W.address(seed.bundle,'S2BoundaryGame')
    gatetag=((W.location(seed.bundle,'S2BoundaryGame')-16)//8192)|128
    assert(gate,gatetag)==(0xad21,191)
    at=W.location(seed.bundle,'S2BoundaryGame');body=raw[at:at+49]
    assert body==image[at:at+49]
    # The live literal calls the current A14D dispatch chain, while this older
    # symbol bundle's GameRoutines names its A021 leaf. Authenticate the actual
    # immediate operands and stop before executing any foreign owner.
    assert body[:15]==bytes.fromhex('0848ad0260c919f01468288d6a01a9')
    assert body[16:20]==bytes.fromhex('8d6c01a9')and body[21:25]==bytes.fromhex('8d6d01a9')
    assert body[26:29]==bytes.fromhex('4c5a01')
    target=body[15]+256*body[20];targettag=body[25]
    assert(target,targettag)==(0xa14d,129)
    ownrange=(0xb128,0xba7d);cases=0
    def enter(m,flags):
        N.put(m,SelectedCharacter=owner)
        m[W.address(m.bundle,'SafecallA_SMC')+1]=85
        m[W.address(m.bundle,'FarcallJmpTarget_SMC')+1]=gate&255
        m[W.address(m.bundle,'FarcallJmpTarget_SMC')+2]=gate>>8
        c=N.NesMPU(memory=m,pc=W.address(m.bundle,'FarCallCommon'))
        c.a=gatetag;c.x=7;c.y=91;c.p=flags;c.sp=224;c.stPushWord(0x5aff)
        for _ in range(20000):
            tag=m.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else -1
            if(c.pc,tag)==(target,targettag):break
            assert not(tag==246 and ownrange[0]<=c.pc<ownrange[1]),('foreign own entry',owner,hex(c.pc))
            assert m[c.pc],('foreign gate BRK',owner,hex(c.pc),tag,hex(target),targettag)
            c.step()
        else:raise AssertionError('Foreign native gate bound')
        return(c.a,c.x,c.y,c.p,c.sp,c.pc)
    for owner in range(256):
        if owner==25:continue
        for flags in(0x30,0xf1):
            a=view(seed,raw);b=view(seed,image)
            assert enter(a,flags)==enter(b,flags)
            assert comparable(a)==comparable(b)
            cases+=1
    return dict(passed=True,ROM_SHA256=info['ROM_SHA256'],legacy_entry_pairs=cases,
        all_non25_raw_owners=True,uninitialized_foreign_physics_executed=False,outputs=0,Mesen_run=False)


def vectors(raw):
    """Actual IRQ/FF lag-NMI at reached changed instruction/SP boundaries."""
    import compose_smb2_flag_handoff_1113 as C
    import check_metal_head_bridge_1112 as Irq
    import check_bub_current_budget_1113 as Frames
    N=W.N;image,info=C.proposal(raw);seed=cold(image,4)
    N.put(seed,NmiDisable=255)
    native=N.NesMPU;points=set();counts=Counter();minimum=255
    spans=((246,0xb128,0xb1d6),(246,0xb9ae,0xba7d))
    class Probe(native):
        def step(self):
            nonlocal minimum
            m=self.memory
            tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else -1
            if any(tag==bank and lo<=self.pc<hi for bank,lo,hi in spans):
                point=(tag,self.pc,self.sp,self.p&4)
                if point not in points:
                    points.add(point)
                    for kind in('IRQ','lagNMI'):
                        if kind=='IRQ'and self.p&4:continue
                        z=N.fork(m);c=native(memory=z,pc=self.pc)
                        for field in('a','x','y','p','sp'):setattr(c,field,getattr(self,field))
                        try:depth=Irq.inject(c,native,kind)
                        except Exception as error:
                            raise AssertionError(dict(kind=kind,pc=hex(self.pc),SP=self.sp,
                                counts=dict(counts),cause=repr(error)))from None
                        minimum=min(minimum,depth);counts[kind]+=1
            return native.step(self)
    with patch.object(N,'NesMPU',Probe):
        for tile in(0,0x23,0x24,0x25,0x26,0x54,0x61,0xc2):
            for owner in(0,3):
                m=world_fixture(seed);start=W.address(m.bundle,'Block_Buffer_1')
                for i in range(416):m[start+i]=tile
                N.put(m,S2ProbeDirection=2)
                N.invoke(m,'S2NativeTileProbe',x=owner,y=6)
        for x,y in((3155,151),(3158,151),(3158,207)):
            N.invoke(flag_fixture(seed,x,y),'S2MainWorld')
        m=world_fixture(seed,x=120,down=4)
        cell(m,123,144,0x10);cell(m,132,144,0x11)
        N.invoke(m,'S2MainWorld')
        for tile in(0xc0,0xc1,0xc2,0x54):
            m=world_fixture(seed)
            if tile==0xc2:cell(m,119,134,tile)
            else:
                N.put(m,S2HeadX=112,S2HeadPage=0,S2HeadY=144)
                cell(m,112,144,tile)
            N.invoke(m,'S2MainWorld')
        m=N.fork(seed)
        for pad in(0,1,129):
            m.controller_pad=pad;Frames.frame(m)
    assert counts['IRQ']>0 and counts['lagNMI']>0 and minimum>=128
    return dict(passed=True,ROM_SHA256=info['ROM_SHA256'],reached_instruction_SP_points=len(points),
        real_vector_cuts=dict(counts),minimum_SP=minimum,changed_ranges=spans,
        exact_AXYP_live_SP_scratch_SMC_overlay_maps=True,synthetic_transaction_fixtures=True,
        actual_Main_NMI_inputs=True,cold_copy_changed=False,outputs=0,Mesen_run=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in('measure','cpu','controls','foreign','vectors'):p.add_argument('--'+name,action='store_true')
    args=p.parse_args();raw=load_input()
    q=vectors(raw)if args.vectors else foreign(raw)if args.foreign else controls(raw)if args.controls else cpu_matrix(raw)if args.cpu else measure(raw)if args.measure else inspect(raw)
    print(json.dumps(q,separators=(',',':')),flush=True)
