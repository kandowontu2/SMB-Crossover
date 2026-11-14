"""Current421/82ec native OAM consumers and Prince/DK pose-window census.

This is a read-only, source CPU resource investigation, not a private-window
allocation. Historical window7 audit producers are never imported or run.
"""
import ast
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler

import compose_shared_world_chr_reset_1114 as C
import check_shared_world_sprite_images_1114 as Cold
import replay_shared_world_chr_reset_1114 as New
import check_bub_current_budget_1113 as Frames

W,N,R=New.W,New.N,New.R


def tile_window(tile):return(tile&1)*4+(tile>>6)


def native_consumers(raw):
    parent=C.inverse(raw);b=dict(W.Symbols.bundle(),raw=raw)
    # Current pointers, records and renderer are exact in both images; the
    # granted area macro is the only image difference and is outside PRG4.
    lo=W.location(b,'MetaspriteTableRightLo');hi=W.location(b,'MetaspriteTableRightHi')
    leftlo=W.location(b,'MetaspriteTableLeftLo');lefthi=W.location(b,'MetaspriteTableLeftHi')
    bank=(lo-16)//8192;start=16+bank*8192
    assert raw[start:start+8192]==parent[start:start+8192]
    with patch.object(Cold,'Factory',New):m=Cold.cold(raw,'hogan')
    first,last=W.address(b,'METASPRITE_POWERUP_STAR'),W.address(b,'METASPRITE_TOAD_STANDING')
    windows=Counter();cases=0;names={}
    for name in b['syms']:
        if name.startswith('METASPRITE_'):
            value=W.address(b,name)
            if first<=value<=last:names.setdefault(value,[]).append(name)
    counts=[]
    def blank():
        m[512:768]=bytes([248,0,0,0]*64)
        N.put(m,CurrentOAMOffset=0,GuestOamRotationActive=0)
    def draw(ptr,palette):
        blank();N.put(m,R0=ptr&255,R1=ptr>>8,R3=palette,R4=96,R5=0,R6=100,R7=1)
        N.invoke(m,'MetaspriteRenderLoop',a=0,x=0,y=0)
        used=N.get(m,'CurrentOAMOffset')
        return [m[513+k]for k in range(0,used,4)]
    for mid in range(first,last+1):
        for facing,tl,th in(('right',lo,hi),('left',leftlo,lefthi)):
            ptr=raw[tl+mid]+256*raw[th+mid];at=start+(ptr&8191);count=raw[at]
            assert count%4==0 and count<=64,(mid,count)
            for palette in range(4):
                tiles=draw(ptr,palette);assert len(tiles)*4==count,(mid,facing,palette,count,tiles)
                used={tile_window(t)for t in tiles}
                assert not used&{5,6,7},(names.get(mid),facing,palette,tiles)
                windows.update(used);cases+=1
                counts.append(len(tiles))
    direct=[]
    def emitted():return[m[513+k]for k in range(0,N.get(m,'CurrentOAMOffset'),4)]
    def add_direct(name,**fields):
        tiles=emitted();assert tiles and not{tile_window(t)for t in tiles}&{5,6,7},(name,fields,tiles)
        direct.append(dict(name=name,actual_tiles=tiles,windows=sorted({tile_window(t)for t in tiles}),**fields))
    for pose in(1,2):
        for facing in('LEFT','RIGHT'):
            ptr=W.address(b,f'MetaspriteData_GOOMBA_WALKING_{pose}_{facing}')
            for palette in range(4):
                blank();N.put(m,R0=ptr&255,R1=ptr>>8,R3=palette,R4=96,R5=0,R6=100,R7=1)
                N.invoke(m,'NativeGoombaRender',a=0,x=0,y=0)
                assert len(emitted())==2
                add_direct('NativeGoombaRender',pose=pose,facing=facing,palette=palette)
    # Current live crossover paths use their own immutable descriptors.
    for name in('FirebarSprite1','FirebarSprite2','DrawBrickDebris::Chunk'):
        at=W.location(b,name);record=raw[at:at+raw[at]+1]
        assert record==parent[at:at+len(record)]
        ptr=W.address(b,name)
        # R0's descriptor bank is mapped by the actual caller in production.
        # Here invoke the kernel with its actual current bank already visible.
        slot=(ptr-0x8000)//8192;old=m.rawtags[slot]
        m.raw_page(slot,((at-16)//8192)|128)
        try:tiles=draw(ptr,0)
        finally:m.raw_page(slot,old)
        assert tiles and {tile_window(t)for t in tiles}=={1}
        direct.append(dict(name=name,record=record.hex(),actual_tiles=tiles,windows=[1]))
    # Actual score-number selector, not just pointer-table inspection.
    for control in range(1,12):
        blank();N.put(m,FloateyNum_Control=control,FloateyNum_X_Pos=96,FloateyNum_Y_Pos=100)
        N.invoke(m,'FloateyNumberRender',a=0,x=0,y=0)
        tiles=[m[513+k]for k in range(0,N.get(m,'CurrentOAMOffset'),4)]
        assert tiles and {tile_window(t)for t in tiles}=={1},(control,tiles)
        direct.append(dict(name='FloateyNumberRender',control=control,actual_tiles=tiles,windows=[1]))
    # Live crossover paths supersede the dead legacy direct writers.
    for frame in range(16):
        blank();N.put(m,FrameCounter=frame,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0)
        for i in range(6):
            m[W.address(b,'Enemy_Flag')+i]=int(i==0)
            m[W.address(b,'Enemy_ID')+i]=0x1b if i==0 else 0
            m[W.address(b,'FirebarPartCount')+i]=12 if i==0 else 0
        for i in range(12):
            m[W.address(b,'FirebarPartX')+i]=96+i*4;m[W.address(b,'FirebarPartY')+i]=100
        N.invoke(m,'DrawWorldFirebars',a=0,x=0,y=0);assert len(emitted())==12
        add_direct('DrawWorldFirebars',frame=frame)
    for frame in(0,4,8,12):
        blank();N.put(m,FrameCounter=frame,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,Block_State=2)
        m[W.address(b,'Block_State')+1]=0
        for i in range(4):
            for name,value in(('Block_X_Position',96+i*8),('Block_PageLoc',0),('Block_Y_Position',100+i*8),('Block_Y_HighPos',1)):
                m[W.address(b,name)+i]=value
        N.put(m,Block_Orig_XPos=96,Block_PageLoc2=0)
        N.invoke(m,'DrawBrickDebris',a=0,x=0,y=0);assert len(emitted())==4
        add_direct('DrawBrickDebris',frame=frame)
    for side in(0,1):
        blank();N.put(m,Enemy_Rel_XPos=96,Enemy_Rel_YPos=100,Vine_Start_Y_Position=100,
            Vine_FlagOffset=1,Vine_Height=96,Enemy_Flag=1,Enemy_ID=47,ObjectOffset=0,Enemy_OffscreenBits=0,
            CurrentOAMOffset=128)
        original_owner=N.get(m,'SelectedCharacter');N.put(m,SelectedCharacter=0)
        m[W.address(b,'Vine_ObjOffset')+side]=0
        W.clear_logs(m)
        result=N.invoke(m,'DrawVine',a=0,x=0,y=side)
        N.put(m,SelectedCharacter=original_owner)
        tiles=[value for at,value in m.writes if 0x200<=at<0x300 and at%4==1]
        assert tiles and{tile_window(t)for t in tiles}=={3},('DrawVine',side,tiles,result,
            bytes(m[512:552]).hex(),[(at,v)for at,v in m.writes if 512<=at<768])
        direct.append(dict(name='DrawVine',fixture_native_selected0=True,side=side,actual_tile_writes=tiles,windows=[3],returned_OAM_cursor=N.get(m,'CurrentOAMOffset')))
    selector_paths=[]
    for animation in range(5):
        N.put(m,JumpspringAnimCtrl=animation);N.invoke(m,'DrawJumpSpring',a=0,x=0,y=0)
        mid=N.get(m,'EnemyMetasprite');ptr=raw[lo+mid]+256*raw[hi+mid]
        tiles=draw(ptr,0);assert tiles and{tile_window(t)for t in tiles}=={3}
        selector_paths.append(dict(name='DrawJumpSpring',animation=animation,mid=mid,tiles=tiles,windows=[3]))
    for score in range(5):
        N.put(m,FlagpoleCollisionYPos=100,FlagpoleScore=score)
        m[W.address(b,'MiscMetasprite')+5]=0
        N.invoke(m,'FlagpoleGfxHandler',a=0,x=0,y=0)
        for name,mid,want in(('flag',N.get(m,'EnemyMetasprite'),3),('score',N.get(m,'MiscMetasprite',5),1)):
            ptr=raw[lo+mid]+256*raw[hi+mid];tiles=draw(ptr,0)
            assert tiles and{tile_window(t)for t in tiles}=={want}
            selector_paths.append(dict(name='FlagpoleGfxHandler_'+name,score=score,mid=mid,tiles=tiles,windows=[want]))
    return dict(parent421_SHA256=C.PIN,candidate82ec_SHA256=C.CANDIDATE,
        current_native_PRG=bank,bank_SHA256=sha256(raw[start:start+8192]).hexdigest(),
        native_metatable_domain=[first,last],native_world_cases=cases,
        native_world_windows=sorted(windows),sprite_count_range=[min(counts),max(counts)],
        current_mouse_metasprites=[name for name in b['syms']if name.startswith('METASPRITE_MOUSE_')],
        direct_current_paths=direct,actual_selector_paths=selector_paths,
        scope='Current native-world emitters; owner/lifecycle checks are separate --owners/--lifecycle gates',
        allocation_granted=False,Mesen_run=False,outputs=0)


def owner_exclusions(raw):
    results=[]
    for key in('prince','donkey_kong'):
        with patch.object(Cold,'Factory',New):m=Cold.cold(raw,key)
        b=m.bundle;windows={W.address(b,'CurrentCHRBank')+i for i in(5,6,7)}|{0x73e0+i for i in(5,6,7)}|set(range(0x5125,0x5128))
        for name in('RlIsActive','VvIsActive','InventorySupported','InventoryDrawPickups','SamusDrawShots','MegaManFullShotBank'):
            W.clear_logs(m);before=bytes(m[0x73e0:0x73ef]);r=N.invoke(m,name,a=0,x=0,y=0)
            writes=[(at,value)for at,value in m.writes if at in windows]
            assert not writes,(key,name,writes)
            assert bytes(m[0x73e0:0x73ef])==before,(key,name,'mode side effect')
            if name in('RlIsActive','VvIsActive','InventorySupported'):assert not r['P']&1,(key,name,r)
            at=W.location(b,name)
            results.append(dict(owner=key,entry=name,carry=r['P']&1,window5_6_7_writes=0,
                current_entry=dict(PC=W.address(b,name),PRG=(at-16)//8192,first24=raw[at:at+24].hex())))
    return dict(ROM_SHA256=C.CANDIDATE,current_selected_owner_exclusion_cases=results,
        scope='Actual selected-owner gates; unconditional private publisher leaves must not be invoked for another owner',
        allocation_granted=False,private_changes=0,outputs=0,Mesen_run=False)


def lifecycle(raw):
    """Current ordinary dispatch plus explicit finite retirement/HUD units.

    The retirement unit models a borrowed private window, not a gameplay seed.
    It invokes the compiled native-menu preparation owner; no candidate exists.
    """
    rows=[]
    for key in('prince','donkey_kong'):
        with patch.object(Cold,'Factory',New):m=Cold.cold(raw,key)
        b=m.bundle;bank=W.address(b,'CurrentCHRBank');mode=W.address(b,'X5ChrMode')
        baseline=[m[bank+i]for i in(5,6,7)]
        assert [m[mode+i]for i in(5,6,7)]==[0,0,0]
        W.clear_logs(m)
        for _ in range(8):m.controller_pad=0;Frames.frame(m,whole_pass=True)
        writes=[(at,value)for at,value in m.writes if at in{bank+i for i in(5,6,7)}|{mode+i for i in(5,6,7)}]
        assert not writes,(key,writes)
        assert [m[bank+i]for i in(5,6,7)]==baseline
        assert N.get(m,'SelectedCharacter')==({'prince':38,'donkey_kong':28}[key])
        rows.append(dict(owner=key,ordinary_idle_Main=8,foreign_window5_6_7_software_writes=0,
            final_banks5_6_7=baseline,final_modes5_6_7=[m[mode+i]for i in(5,6,7)]))
        # Exact public physical setter and menu retirement, tested in memory.
        # Physical pages200..202 are arbitrary unit values, not an allocation.
        for window in(5,6,7):N.invoke(m,'X5SetPhysicalChr',a=195+window,x=1,y=window)
        assert [m[mode+i]for i in(5,6,7)]==[129]*3
        N.invoke(m,'FmNativePrepare',a=0,x=0,y=0)
        assert list(m[mode:mode+12])==[0]*12
        at=W.location(b,'CHRBankInitValues');expected=list(raw[at:at+8])
        assert list(m[bank:bank+8])==expected
        N.invoke(m,'X5PublishChr',a=0,x=0,y=0)
        mapping=W.location(b,'ChrPhysicalMap')
        expected_physical=[raw[mapping+v]for v in expected]
        assert m.chr_latches[:8]==expected_physical
        rows[-1].update(explicit_retirement_fixture=True,retired_logical_banks=expected,
            actual_published_physical_banks=expected_physical)
    # HUD owns BG8; it cannot consume sprite5/6/7 through an alias.
    with patch.object(Cold,'Factory',New):m=Cold.cold(raw,'hogan')
    N.put(m,InvHudActive=1,InvHudPhysical=200,SsChrActive=0,X5HudChrUpper=0,X5WideChrActive=1)
    bank=W.address(m.bundle,'CurrentCHRBank');mode=W.address(m.bundle,'X5ChrMode')
    for i in range(12):m[bank+i]=20;m[mode+i]=0
    W.clear_logs(m);N.invoke(m,'X5PublishChr',a=0,x=0,y=0)
    writes={at:value for at,value in m.writes if 0x5120<=at<=0x512b}
    assert writes[0x5128]==200 and all(writes[0x5120+i]!=200 for i in(5,6,7))
    return dict(ROM_SHA256=C.CANDIDATE,current_owner_dispatch=rows,
        HUD_resource_fixture=True,HUD_actual_window=8,actual_CHR_writes=writes,
        scope='Current live owner isolation and compiled native-menu retirement. Candidate death/pipe/menu/pose/NMI qualification remains required after a private grant.',
        allocation_granted=False,private_changes=0,Mesen_run=False,outputs=0)


def pure_function(path,name,space):
    node=next(n for n in ast.parse(path.read_text()).body if isinstance(n,ast.FunctionDef)and n.name==name)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),str(path),'exec'),space)
    return space[name]


def prince_render(raw):
    """Execute current authenticated renderer for every present pose/facing.

    Source-frame/pose setters here are explicit finite rendering fixtures. They
    do not qualify any gameplay route, private allocation or future remap.
    """
    P=New.Previous.Prince;_,chunks,_=P.extract(raw);runtime,metadata,_=chunks
    geometry=pure_function(R/'tools/audit/prepare_prince_climb_funded_1109_v1.py','geometry',{})
    geometry=pure_function(R/'tools/audit/check_prince_run_support_funding_1110.py','geometry',{'P':SimpleNamespace(geometry=geometry)})
    with patch.object(Cold,'Factory',New):m=Cold.cold(raw,'prince')
    assert bytes(m.ram[3][:0x1fa3])==runtime[:0x1fa3]
    m.raw_page(2,2);N.put(m,CurrentBankC=2,GuestOamRotationActive=1,RgOamRotation=0)
    base=N.NesMPU;events=[];indices=[];carries=[]
    class Trace(base):
        def step(self):
            if self.pc==0xbc40 and m.rawtags[1]==3:
                # The current page metadata index is X only before the high
                # helper; at this point X is its derived physical high byte.
                indices.append((m[0xbd04],self.x,self.y))
            if self.pc==0xa275 and m.rawtags[1]==190:events.append((self.y,self.a,self.x))
            if self.pc==0xbc7e and m.rawtags[1]==3:carries.append(self.p&1)
            return super().step()
    def invoke():
        N.put(m,CurrentOAMOffset=0)
        m.ram[3][0x1cfe:0x1d02]=bytes((48,0,176,1))
        m[W.address(m.bundle,'SafecallA_SMC')+1]=83
        target=W.address(m.bundle,'FarcallJmpTarget_SMC')
        m[target+1:target+3]=(0xbbc1).to_bytes(2,'little')
        cpu=Trace(memory=m,pc=W.address(m.bundle,'FarCallCommon'))
        cpu.a=3;cpu.x=71;cpu.y=109;cpu.p=0x61;cpu.sp=224;cpu.stPushWord(0x5aff)
        for _ in range(100000):
            if cpu.pc==0x5b00:break
            assert m[cpu.pc]!=0,('Current renderer BRK',hex(cpu.pc),m.rawtags)
            cpu.step()
        else:raise AssertionError('Current renderer bounded return')
        assert cpu.sp==224 and (cpu.a,cpu.x,cpu.y)==(83,71,109)and cpu.p&1
        return cpu
    cases=parts=0;three=[];page_ids=set();stream_y_changes=0
    for frame in range(239):
        result=geometry(metadata,frame)
        if result is None:continue
        prefix,records=result;count=prefix[0]&15;pages=list(prefix[1:1+((prefix[0]>>4)&3)])
        for facing in(0,1):
            m.ram[2][0x617]=frame;m.ram[2][0x615]=facing
            events.clear();indices.clear();carries.clear();W.clear_logs(m);invoke()
            assert len(events)==len(pages)==len(indices),(frame,facing,pages,events,indices)
            expected=[]
            for index,page in enumerate(pages):
                physical=runtime[0x1da4+page]+256*(1+int(page>=22))
                expected.append((index,physical&255,physical>>8));page_ids.add(page)
            assert events==expected,(frame,facing,events,expected)
            assert [i[0]for i in indices]==list(range(len(pages)))
            assert [i[1]for i in indices]==[1+int(p>=22)for p in pages]
            assert [i[2]for i in indices]==list(range(2,2+len(pages))),'Current metadata stream Y must survive page publication'
            packet=bytes(m.ram[2][0x200:0x201+count*4])
            assert packet[0]==count*4 and list(packet[1::4])==list(reversed(records[1::3]))
            assert len(carries)==count
            cases+=1;parts+=count
            if len(pages)==3:three.append(dict(frame=frame,facing=facing,pages=pages,actual_publisher_calls=list(events)))
    assert cases==408
    return dict(ROM_SHA256=C.CANDIDATE,current_runtime_SHA256=sha256(runtime).hexdigest(),
        explicit_render_fixtures=cases,actual_parts=parts,page_id_domain=sorted(page_ids),
        current_page_loop=0xbc30,current_window_load=0xbc40,current_tile_store=0xbc7e,
        current_window_indices=[0,1,2],stream_Y_saved_and_restored=True,
        source_page_X_consumed_by_high_helper=True,tile_carry_values_observed='Not a liveness proof; future helper must preserve flags or independently prove consumers',
        three_page_cases=three,scope='Current renderer only; no remap placed or qualified',
        allocation_granted=False,private_changes=0,Mesen_run=False,outputs=0)


def private_pose_census(raw):
    parent=C.inverse(raw);P=New.Previous.Prince
    assert P.extract(raw)==P.extract(parent)
    _,chunks,_=P.extract(raw);metadata=chunks[1]
    # Reuse only the two pure geometry readers, without importing their old
    # proof graphs, producers, historical ROMs or generated asset trees.
    base=R/'tools/audit/prepare_prince_climb_funded_1109_v1.py'
    mixed=R/'tools/audit/check_prince_run_support_funding_1110.py'
    geometry=pure_function(base,'geometry',{})
    geometry=pure_function(mixed,'geometry',{'P':SimpleNamespace(geometry=geometry)})
    page_counts=Counter();windows=Counter();tile_ids=set();parts=Counter();absent=[];max_rows=[];remap_parts=0
    for frame in range(239):
        result=geometry(metadata,frame)
        if result is None:absent.append(frame);continue
        prefix,records=result;n=prefix[0]&15;pages=(prefix[0]>>4)&3
        assert len(records)==3*n and 1<=pages<=3
        tiles=records[1::3];used={tile_window(t)for t in tiles}
        assert not any(t&1 for t in tiles)and used<=set(range(pages))
        for tile in tiles:
            target=tile if tile<64 else tile|1
            assert tile_window(target)==({0:0,1:5,2:6}[tile_window(tile)])
            assert target&62==tile&62
            remap_parts+=1
        page_counts[pages]+=1;parts[n]+=1;windows.update(used);tile_ids.update(tiles)
        if pages>1:max_rows.append(dict(frame=frame,pages=list(prefix[1:1+pages]),windows=sorted(used),tiles=list(tiles)))
    dk=dk_pose_census(raw)
    return dict(ROM_SHA256=C.CANDIDATE,prince_cookie=raw[P.COOKIE:P.COOKIE+16].hex(),
        decoded_metadata_SHA256=sha256(metadata).hexdigest(),frame_domain=239,absent_frames=absent,
        page_counts=dict(page_counts),body_windows=sorted(windows),part_count_histogram=dict(parts),
        body_tile_ids=sorted(tile_ids),multi_page_pose_examples=max_rows[:12],
        three_page_poses=[row for row in max_rows if len(row['pages'])==3],
        proposed_window_map={0:0,1:5,2:6},unchanged_pattern_pair_offset_cases=remap_parts,
        proposal_math_only=True,
        pure_reader_bindings={p.name:sha256(p.read_bytes()).hexdigest()for p in(base,mixed)},
        donkey_kong=dk,
        allocation_granted=False,private_changes=0,Mesen_run=False,outputs=0)


def dk_pose_census(raw):
    b=dict(W.Symbols.bundle(),raw=raw);records=[]
    for family,low,high,count in(('body','DkPoseLo','DkPoseHi',9),('barrel','DkBarrelLo','DkBarrelHi',6)):
        lo,hi=W.location(b,low),W.location(b,high);bank=(lo-16)//8192
        for pose in range(count):
            ptr=raw[lo+pose]+256*raw[hi+pose];at=16+bank*8192+(ptr&8191)
            size=raw[at];record=raw[at:at+size+1]
            assert size%4==0 and size<=64
            tiles=record[1::4];assert tiles and all(t<64 and not t&1 for t in tiles)
            records.append(dict(family=family,pose=pose,CPU=ptr,record_SHA256=sha256(record).hexdigest(),tiles=list(tiles),source_windows=[0]))
    begin=W.address(b,'DkDraw');at=W.location(b,'DkDraw')
    memory=bytearray(65536);memory[begin:begin+512]=raw[at:at+512]
    dis=Disassembler(MPU(memory=memory));pc=begin;sites=[]
    # Bound the actual original public routine through its final RTS. Its only
    # earlier RTS is the selected-owner rejection, so use the source end size
    # derived from the last CMP36/BCC Loop/RTS tail, not that rejection.
    tail=raw[at:at+512].find(bytes.fromhex('c92490'))
    assert tail>=0 and raw[at+tail+4]==0x60
    end=begin+tail+5
    while pc<end:
        size,text=dis.instruction_at(pc);code=bytes(memory[pc:pc+size])
        if code in(bytes.fromhex('a001'),bytes.fromhex('0940')):
            sites.append(dict(PC=pc,file=at+pc-begin,preimage=code.hex(),instruction=text))
        pc+=size
    assert len(sites)==3 and[site['preimage']for site in sites]==['a001','0940','0940']
    gate=bytes.fromhex('0848ad')+W.address(b,'SelectedCharacter').to_bytes(2,'little')+bytes.fromhex('c91cf00368')
    assert raw[at:at+len(gate)]==gate,(hex(begin),raw[at:at+16].hex(),gate.hex())
    return dict(current_record_cases=len(records),all_body_and_barrel_source_tiles_even_below64=True,
        records=records,current_DkDraw_half_open=[begin,end],current_DkDraw_SHA256=sha256(raw[at:at+end-begin]).hexdigest(),
        exact_existing_private1_sites=sites,selected_owner=28,
        proposed_private7_operand_values=['a007','09c1','09c1'],proposal_placed=False)


def prince_runtime_binding(raw):
    P=New.Previous.Prince;_,chunks,_=P.extract(raw);runtime,metadata,_=chunks
    memory=bytearray(65536);memory[0xa000:0xa000+len(runtime)]=runtime
    memory[0xc800:0xc800+len(metadata)]=metadata
    dis=Disassembler(MPU(memory=memory));rows=[]
    for begin,end in((0xbbc1,0xbc70),(0xbc6f,0xbc9b),(0xbdc3,0xbde2)):
        pc=begin
        while pc<end:
            size,text=dis.instruction_at(pc);rows.append(dict(PC=pc,hex=bytes(memory[pc:pc+size]).hex(),instruction=text));pc+=size
    window_loads=[0xa000+i for i in range(len(runtime)-2)if runtime[i:i+3]==bytes.fromhex('ac04bd')]
    tile_stores=[0xa000+i for i in range(len(runtime)-2)if runtime[i:i+3]==bytes.fromhex('9d00c2')]
    return dict(ROM_SHA256=C.CANDIDATE,runtime_SHA256=sha256(runtime).hexdigest(),
        known_renderer_entry=0xbbc1,retained_label_page_loop=0xbc2d,
        retained_page_counter=0xbd03,retained_source_window_index=0xbd04,
        actual_Window_BD04_load_sites=window_loads,actual_native_packet_tile_stores=tile_stores,
        current_bound_instructions=rows,private_changes=0,allocation_granted=False,outputs=0)


def vine_trace(raw):
    with patch.object(Cold,'Factory',New):m=Cold.cold(raw,'hogan')
    b=m.bundle;N.put(m,CurrentOAMOffset=128,GuestOamRotationActive=0,Enemy_Rel_XPos=96,
        Enemy_Rel_YPos=100,Vine_Start_Y_Position=100,Vine_FlagOffset=1,Vine_Height=96,
        Enemy_Flag=1,Enemy_ID=47,ObjectOffset=0,Enemy_OffscreenBits=0)
    base=N.NesMPU;rows=[]
    class Trace(base):
        def step(self):
            if self.pc>=0x8000 and len(rows)<100:
                rows.append(dict(PC=self.pc,tag=m.rawtags[(self.pc-0x8000)//8192],
                    hex=bytes(m[self.pc+i]for i in range(3)).hex(),A=self.a,X=self.x,Y=self.y,P=self.p))
            return super().step()
    W.clear_logs(m)
    with patch.object(N,'NesMPU',Trace):result=N.invoke(m,'DrawVine',a=0,x=0,y=0)
    return dict(result=result,trace=rows,OAM_writes=[(at,value)for at,value in m.writes if 512<=at<768],
        source_entries={name:dict(CPU=W.address(b,name),PRG=(W.location(b,name)-16)//8192)for name in('DrawVine','MmReserveVine','RyuPlatformOriginalDrawVine')},outputs=0)


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--poses',action='store_true');p.add_argument('--runtime',action='store_true');p.add_argument('--owners',action='store_true');p.add_argument('--lifecycle',action='store_true');p.add_argument('--render',action='store_true');p.add_argument('--vine-trace',action='store_true');a=p.parse_args()
    raw=C.load_current_image()
    def forbid(*args,**kwargs):raise RuntimeError('Read-only resource audit attempted output/Mesen')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Cold.Native,'run',forbid):
        q=vine_trace(raw)if a.vine_trace else prince_render(raw)if a.render else lifecycle(raw)if a.lifecycle else owner_exclusions(raw)if a.owners else prince_runtime_binding(raw)if a.runtime else private_pose_census(raw)if a.poses else native_consumers(raw)
    q['file_and_Mesen_traps']=True
    print(json.dumps(q,separators=(',',':')),flush=True)
