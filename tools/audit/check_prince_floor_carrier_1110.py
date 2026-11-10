"""Conditional page329 funds the frozen Prince floor adapter, in memory only.

The existing Zelda-II alias is mandatory. Sonic321..328 stays byte-identical.
No ROM, receipt, compiler temporary or other generated file is written.
"""
import argparse
from collections import Counter
from hashlib import sha256
import json
import struct
from unittest.mock import patch

import check_prince_native_foot_motion_1110 as Foot
import check_sonic_seventh_cold_owner_1110 as Sonic
import check_sonic_fairy_funding_1110 as Alias
import qualify_prince_previous_sole_1110 as Previous

C,N,I,P=Foot.C,Foot.N,Foot.I,Foot.C.P
R=C.R
CHR=1048592
PAGE=329
ADMISSION=R/'tools/reference/prince_native_floor_admission_1110.s'
ADMISSION_PC=0xd53e
PARENT='d07012de9762e93ca76cb283ba84e9b8a9a7bd532364fd94ce4ca6101687cb72'
FROZEN={
    R/'tools/reference/prince_native_foot_motion_1110.s':'98dd9c59e473a3952a7002b634e806bf5f1f5aa9654c54eb9094b5d01104997e',
    R/'tools/audit/check_prince_native_foot_motion_1110.py':'438250e4dd3955e8db70e09adb982e07a143c4fbc9998b2b4063c015fa252eee',
}


def digest(data):return sha256(data).hexdigest()


def streams(seed):
    original,_,state=P.Q.source_images()
    rt=bytearray(seed.ram[3][:len(original)])
    rt[0x1fa3:0x1fd8]=original[0x1fa3:0x1fd8]
    assert P.live(rt)==bytes(seed.ram[3][:len(rt)])
    return bytes(rt),bytes(seed.ram[2][0x800:0x1fcc]),state


def admission_code(bundle):
    with patch.object(Foot,'SOURCE',ADMISSION),patch.object(Foot,'ORIGIN',ADMISSION_PC):
        return Foot.code(bundle)


def apply_admission(seed):
    worker=admission_code(seed.bundle);at=ADMISSION_PC-0xc000
    assert bytes(seed.ram[3][0x1d3e:0x1d42])==bytes.fromhex('4cd7d4ea')
    assert bytes(seed.ram[2][at:at+len(worker)])==bytes([255])*len(worker)
    seed.ram[2][at:at+len(worker)]=worker
    seed.ram[3][0x1d3e:0x1d42]=bytes([0x4c])+ADMISSION_PC.to_bytes(2,'little')+bytes([0xea])
    return seed


def proposal(*,admission=True):
    for path,pin in FROZEN.items():assert digest(path.read_bytes())==pin,path
    public=C.ROM.read_bytes();assert digest(public)==C.PIN
    combined,program,sonic_packet,_,old_rows,_=Sonic.proposal(public)
    assert digest(combined)==PARENT
    alias=json.loads((R/'docs/qa/allocations/sonic-sms-fairy-repack-1110.json').read_bytes())
    change=alias['mandatory_atomic_source_change'];at=change['file_offset']
    assert combined[at:at+27]==bytes.fromhex(change['new_hex'])
    assert set(range(321,329))==set(sonic_packet['code_pages'])|{sonic_packet['metadata_page']}
    private=Foot.F.Exit.ROM.read_bytes();assert digest(private)==Foot.F.Exit.PIN
    own=C.Start.W.bundle(private);seed,_=P.Q.C.C.cold(own,38)
    before=streams(seed);changed=Foot.apply(N.fork(seed))
    if admission:changed=apply_admission(changed)
    after=streams(changed)
    assert before[2]==after[2]
    encode=P.Q.M.CODEC.encode
    old_packed=list(map(encode,before));packed=list(map(encode,after))
    assert list(map(len,old_packed))==[6386,5668,1232]
    assert len(packed[0])<6500 and len(packed[1])<6000 and len(packed[2])==1232
    rows=sorted((q for q in C.read(P.OLD)['patches'] if 'physical_CHR' in q),key=lambda q:q['source_offset'])
    assert len(rows)==44 and len({q['physical_CHR'] for q in rows})==44
    pages=[q['physical_CHR'] for q in rows]
    assert PAGE not in pages and not set(pages)&set(range(321,335))
    old_payload=b''.join(private[q['file_offset']:q['file_offset']+1024] for q in rows)
    decoder=(P.V.O/'cold-decoder-v25.bin').read_bytes();assert len(decoder)==254
    decoder_end=31072+len(decoder);loader_end=decoder_end+444
    assert old_payload[31072:decoder_end]==decoder
    old_loader=old_payload[decoder_end:loader_end]
    assert old_payload[loader_end:]==b''.join(old_packed)
    lo,hi=old_loader[-28:-14],old_loader[-14:]
    assert [a+256*b for a,b in zip(lo,hi)]==pages[-14:]
    config_at=444-52
    config=lambda sizes:struct.pack('<12H',0xc500,0xa000,sizes[0],len(after[0]),
        0xe100-sizes[1],0xc800,sizes[1],len(after[1]),0xc300,0xc100,sizes[2],len(after[2]))
    assert old_loader[config_at:config_at+24]==config(list(map(len,old_packed)))
    assert old_loader[config_at-3:config_at]==bytes.fromhex('011a0c')
    loader=bytearray(old_loader[:-28]+lo+bytes([PAGE&255])+hi+bytes([PAGE>>8]))
    # Boot97B is unchanged. Its existing512B copy includes349B worker/data.
    old_hi=0xc100+(444-14)-97;new_hi=old_hi+1
    pattern=bytes([0xbd])+old_hi.to_bytes(2,'little')
    hits=[i for i in range(config_at) if loader[i:i+3]==pattern]
    assert len(hits)==1,hits
    loader[hits[0]+1:hits[0]+3]=new_hi.to_bytes(2,'little')
    loader[config_at-2]=0x1c
    loader[config_at:config_at+24]=config(list(map(len,packed)))
    assert len(loader)==446 and loader[:97]==old_loader[:97]
    data_hits=[i for i in range(config_at) if loader[i:i+5]==bytes.fromhex('9103d103d0')]
    assert len(data_hits)==1,data_hits
    read_hits=[i for i in range(config_at) if loader[i:i+6]==bytes.fromhex('ad0720ee25c2')]
    assert len(read_hits)==1,read_hits
    assert 0xc100+len(loader)-97==0xc25d<0xc300
    payload=old_payload[:decoder_end]+bytes(loader)+b''.join(packed)
    assert payload[:31072]==old_payload[:31072] and len(payload)<45*1024
    assert len(payload)<=45*1024
    cookie=bytes([0xa7,38,2])+sha256(b''.join(after)+payload).digest()[:13]
    image=bytearray(combined);cookie_at=Sonic.C.off(65,0xab9f)
    assert image[cookie_at:cookie_at+3]==bytes([0xa7,38,2])
    image[cookie_at:cookie_at+16]=cookie
    for index,page in enumerate(pages+[PAGE]):
        part=payload[index*1024:(index+1)*1024].ljust(1024,b'\xff')
        image[CHR+page*1024:CHR+(page+1)*1024]=part
    assert all(image[CHR+p*1024:CHR+(p+1)*1024]==combined[CHR+p*1024:CHR+(p+1)*1024] for p in range(321,329))
    assert image[:cookie_at]+image[cookie_at+16:CHR]==combined[:cookie_at]+combined[cookie_at+16:CHR]
    trial=C.Start.W.bundle(bytes(image));parent=C.Start.W.bundle(combined)
    report=dict(parent_SHA256=PARENT,in_memory_SHA256=digest(image),Prince_cookie=cookie.hex(),
        cookie_CPU=[65,0xab9f],carrier_pages=pages+[PAGE],new_conditional_page=PAGE,
        old_carriers_exact_art_bytes=31072,loader_bytes=446,worker_end=0xc25d,
        fixed_boot_copy=[0xc100,0xc300],packed_bytes=list(map(len,packed)),
        payload_bytes=len(payload),capacity=45*1024,spare=45*1024-len(payload),
        new_page_payload_bytes=len(payload)-44*1024,
        metadata_input=0xe100-len(packed[1]),metadata_cold_fragment=[0xc300,0xc800],
        page329_preimage_SHA256=digest(Alias.page_bytes(public,PAGE)),
        page329_new_SHA256=digest(bytes(image[CHR+PAGE*1024:CHR+(PAGE+1)*1024])),
        payload_SHA256=digest(payload),stream_SHA256=list(map(digest,after)),
        Sonic321_328_unchanged=True,future_conditional_pages=list(range(330,335)),
        frozen_worker_bytes=103,admission_PC=ADMISSION_PC,admission_bytes=len(admission_code(trial)) if admission else 0,
        data_op_PC=0xc100+data_hits[0]-97,physical_hi_load_PC=0xc100+hits[0]-97,
        read_source_PC=0xc100+read_hits[0]-97,
        ROM_written=False,outputs_written=0)
    return parent,trial,after,report,program,sonic_packet,old_rows


def actual_cold(trial,chunks,layout,program,*,overlap_negative=False):
    """Track every staged input read and reject any overwrite before consumption."""
    m=Sonic.O.blank(trial);bus=type(m);read,write=bus.__getitem__,bus.__setitem__
    cpu=N.NesMPU;active=None;results=[];mapped=Counter()
    config=[(0xc500,0xa000,len(chunks[0]),layout['packed_bytes'][0]),
            (layout['metadata_input'],0xc800,len(chunks[1]),layout['packed_bytes'][1]),
            (0xc300,0xc100,len(chunks[2]),layout['packed_bytes'][2])]
    class Trace(cpu):
        def step(self):
            nonlocal active
            if self.memory is m and self.pc==0xc000 and m.rawtags[2]==2:
                if active is not None:
                    assert active['cursor']==len(active['addresses']),active
                    results.append(dict(stage=active['stage'],consumed=active['cursor'],
                        minimum_unread_margin=active['margin']))
                stage=len(results);start,dest,size,count=config[stage]
                end=min(start+count,0xdc00)
                addresses=list(range(start,end))+list(range(0xc300,0xc300+count-(end-start)))
                assert len(addresses)==count and len(set(addresses))==count
                active=dict(stage=stage,dest=dest,size=size,addresses=addresses,
                    indices={a:i for i,a in enumerate(addresses)},cursor=0,margin=65536)
            return super().step()
    def reader(self,key):
        if self is m and isinstance(key,int):
            if key==0x2007:mapped[m.chr_latches[3]]+=1
            if active is not None:
                cursor=active['cursor'];addresses=active['addresses']
                if cursor<len(addresses) and key==addresses[cursor]:active['cursor']+=1
        return read(self,key)
    def writer(self,key,value):
        if self is m and active is not None and isinstance(key,int) and active['dest']<=key<active['dest']+active['size']:
            index=active['indices'].get(key)
            if index is not None:
                assert index<active['cursor'],('Unread staged input overwritten',active['stage'],hex(key),index,active['cursor'])
                active['margin']=min(active['margin'],active['cursor']-index)
        return write(self,key,value)
    with patch.object(bus,'__getitem__',reader),patch.object(bus,'__setitem__',writer),patch.object(N,'NesMPU',Trace),patch.object(Sonic.O,'NesMPU',Trace):
        try:result=Sonic.C.cold(m,38,program['new'])
        except AssertionError as error:
            if not overlap_negative:raise
            assert isinstance(error.args[0],tuple) and error.args[0][0]=='Unread staged input overwritten',error
            assert Sonic.O.headers(m)==(bytes(16),bytes(16))
            return m,dict(expected_overlap_rejected=list(error.args[0]),both_headers_invalid=True)
    assert not overlap_negative,'Expected unread-input negative did not fail'
    assert active['cursor']==len(active['addresses'])
    results.append(dict(stage=active['stage'],consumed=active['cursor'],minimum_unread_margin=active['margin']))
    assert bytes(m.ram[3][:len(chunks[0])])==P.live(chunks[0])
    assert bytes(m.ram[2][0x800:0x800+len(chunks[1])])==chunks[1]
    cookie=bytes.fromhex(layout['Prince_cookie'])
    assert Sonic.O.headers(m)==(cookie,cookie)
    assert set(mapped)<=set(layout['carrier_pages']) and mapped[PAGE]>0,mapped
    assert Sonic.C.invoke(m,Sonic.O.AUTH)['P']&1
    return m,dict(cold=result,staged_inputs=results,physical_reads=dict(mapped),both_headers=cookie.hex())


def overlap_negative(trial,chunks,layout,program):
    image=bytearray(trial['raw']);offset=31072+254+(444-52)+8
    page=layout['carrier_pages'][offset//1024];at=CHR+page*1024+offset%1024
    assert image[at:at+2]==layout['metadata_input'].to_bytes(2,'little')
    image[at:at+2]=(0xc800).to_bytes(2,'little')
    bad=dict(trial,raw=bytes(image));_,result=actual_cold(bad,chunks,dict(layout,metadata_input=0xc800),program,overlap_negative=True)
    return result


def poses(parent,trial,new):
    old,_=P.Q.C.C.cold(parent,38)
    before=bytes(old.ram[2][0x800:0x1fcc]);after=bytes(new.ram[2][0x800:0x1fcc])
    assert all(C.Camera.Funded.Pack.geometry(before,f)==C.Camera.Funded.Pack.geometry(after,f) for f in range(239))
    Sonic.O.clear_logs(old);Sonic.O.clear_logs(new)
    return dict(geometry_exact=239,**P.test_pose(old,new))


def admission_matrix(seed):
    base=Sonic.slim_fork(seed);Sonic.O.clear_logs(base)
    C.Seam.terrain(base,lambda x,y:0x54 if y>=208 else 0);Sonic.O.clear_logs(base)
    counts=Counter()
    for dy in range(256):
        for residue in range(16):
            m=Sonic.slim_fork(base);m.raw_page(2,2);N.put(m,CurrentBankC=2,GameEngineSubroutine=8,
                Player_X_Position=900&255,Player_PageLoc=900>>8,Player_Y_HighPos=1,
                Player_Y_Position=176+residue,Player_Y_Speed=dy)
            m.ram[2][0x84:0x86]=(208+residue).to_bytes(2,'little');m.ram[2][0x88]=residue+3
            if dy<128:
                native=N.invoke(m,'GuestLandingWindow',a=84,x=71,y=residue,p=0x71)
                repair=bool(native['P']&1)
                assert repair==(residue>=max(5,dy+1)),(dy,residue,native)
                counts['actual_native_window_calls']+=1
            else:repair=False
            prefix=bytes(m.ram[2][:0x800]);scratch=bytes(m[3:11])
            out=I.invoke(m,3,0xbd3e,(83,71,109,0x71))['regs']
            assert out==[83,71,6,0x71,224],(dy,residue,out)
            assert N.get(m,'Player_Y_Position')==(176 if repair else 176+residue),(dy,residue)
            assert N.get(m,'Player_Y_Speed')==dy and bytes(m.ram[2][:0x800])==prefix and bytes(m[3:11])==scratch
            counts['rejected_window_geometry_calls' if repair else 'original_native_cases_preserved']+=1
            counts['DY_residue_cases']+=1
    for engine in range(256):
        m=Sonic.slim_fork(base);m.raw_page(2,2);N.put(m,CurrentBankC=2,GameEngineSubroutine=engine,
            Player_X_Position=132,Player_PageLoc=3,Player_Y_Position=181,Player_Y_HighPos=1,Player_Y_Speed=0)
        m.ram[2][0x84:0x86]=(213).to_bytes(2,'little');m.ram[2][0x88]=8
        I.invoke(m,3,0xbd3e,(83,71,109,0x71))
        assert N.get(m,'Player_Y_Position')==(176 if engine==8 else 181),engine
        counts['engine_gate_cases']+=1
    return dict(counts)


def landing_and_lifecycle(trial):
    entries=C.read(C.OUT/'proof.json')['layout']['entries']
    with patch.object(C,'CAPTURE',entries['PpCapturePreviousSole']),patch.object(C,'CONTACT',entries['PpLandingContact']),patch.object(C,'OPERAND',entries['PreviousSole']+1):
        replay,held,(env,labels,seeds)=C.replay(trial)
    assert replay['result']=='landing-repaired' and replay['terminal']['hp']==5 and len(seeds)==1
    contacts=Previous.contacts(seeds[0],entries)
    lifecycle=Previous.lifecycle(seeds[0],entries)
    return dict(replay={k:v for k,v in replay.items() if k not in ('exports','injuries')},
                contact_cases=contacts,lifecycle=lifecycle),held[90],(env,labels)


def fixture_diagnostic(trial):
    env,m,labels,_=C.Failure.Roof.Climb.Earned.fixture(trial)
    C.Seam.terrain(m,C.Failure.Roof.terrain)
    C.Seam.layout(m,811-255,678,scroll=0);C.Route.install_group(m)
    pad=0;history=[]
    for tick in range(172):
        pad={0:1,8:0,51:8,106:9,112:8}.get(tick,pad)
        C.Route.controls(env,m,labels,pad)
        if tick%4==3:history.append(C.Recovery.sample(m,tick+1))
    return dict(terminal=C.Recovery.sample(m,172),trace=history)


def owner_regressions(parent,trial,chunks,layout,program,packet,rows):
    counts=Counter();seeds={}
    for owner in range(37,43):
        print('OWNER_REGRESSION '+str(owner),flush=True)
        old,new=Sonic.O.blank(parent),Sonic.O.blank(trial)
        a=Sonic.C.cold(old,owner,program['new']);b=Sonic.C.cold(new,owner,program['new'])
        if owner!=38:Sonic.C.parity(old,new,a,b)
        else:
            assert bytes(old.ram[2][:0x800])==bytes(new.ram[2][:0x800])
            assert bytes(new.ram[3][:len(chunks[0])])==P.live(chunks[0])
            assert bytes(new.ram[2][0x800:0x800+len(chunks[1])])==chunks[1]
            assert Sonic.O.headers(new)==(bytes.fromhex(layout['Prince_cookie']),)*2
            assert (a['A'],a['X'],a['Y'],a['P'])==(b['A'],b['X'],b['Y'],b['P'])
            assert bytes(old[3:11])==bytes(new[3:11])
            assert [old[i] for i in Sonic.O.SMC]==[new[i] for i in Sonic.O.SMC]
            assert old.rawtags==new.rawtags and old.chr_latches==new.chr_latches
        counts['cold_owners']+=1;seeds[owner]=old,new
        saved=tuple(map(bytes,new.ram));warm=Sonic.slim_fork(new)
        result=Sonic.C.cold(warm,owner,program['new'])
        assert result['PPU_reads']==0 and tuple(map(bytes,warm.ram))==saved
        counts['warm_owners']+=1
        for bank in (2,3):
            for index in range(16):
                m=Sonic.slim_fork(new);m.ram[bank][0x1fe0+index]^=1
                saved=tuple(map(bytes,m.ram));Sonic.O.clear_logs(m)
                assert not Sonic.C.invoke(m,Sonic.O.AUTH)['P']&1
                assert tuple(map(bytes,m.ram))==saved and not m.ram_writes
                counts['header_poison_bytes']+=1
        for fields in (dict(SelectedCharacter=44),dict(OperMode=0),dict(FamilyMainCommit=0),
                       dict(DisableScreenFlag=0),dict(Mirror_PPUMASK=24),dict(NmiDisable=0)):
            m=Sonic.O.blank(trial);Sonic.O.scene(m,owner);N.put(m,**fields);Sonic.O.clear_logs(m)
            saved=tuple(map(bytes,m.ram));out=Sonic.C.invoke(m)
            assert not out['P']&1 and tuple(map(bytes,m.ram))==saved and not m.ram_writes
            counts['guard_cases']+=1
        for fault in ('write-protection',(2,0),(3,0) if rows[owner]['code_rows'] else (2,0x1000)):
            m=Sonic.O.blank(trial)
            if fault=='write-protection':m.protection=[0,0]
            else:m.corrupt_at=fault
            out=Sonic.C.cold(m,owner,program['new'],expect_success=False)
            assert not out['P']&1 and not Sonic.C.invoke(m,Sonic.O.AUTH)['P']&1
            assert not m.ram[2][0x1fe0] and not m.ram[3][0x1fe0]
            counts['readback_fault_cases']+=1
    for source in range(37,43):
        for dest in range(37,43):
            a,b=(Sonic.slim_fork(m) for m in seeds[source])
            left=Sonic.C.cold(a,dest,program['new']);right=Sonic.C.cold(b,dest,program['new'])
            assert Sonic.O.headers(b)==Sonic.O.headers(seeds[dest][1])
            if source!=38 and dest!=38:Sonic.C.parity(a,b,left,right)
            else:
                intended={(bank,at) for bank in (2,3) for at,(x,y) in enumerate(zip(seeds[38][0].ram[bank],seeds[38][1].ram[bank])) if x!=y}
                assert all(x==y or (bank,at) in intended for bank,(u,v) in enumerate(zip(a.ram,b.ram))
                           for at,(x,y) in enumerate(zip(u,v))),(source,dest)
                assert bytes(a[3:11])==bytes(b[3:11]) and a.rawtags==b.rawtags and a.chr_latches==b.chr_latches
            assert Sonic.C.invoke(b,Sonic.O.AUTH)['P']&1
            counts['ordered_owner_transitions']+=1
    extra,sonic=Sonic.seventh(trial,program,packet,seeds)
    counts.update(extra)
    assert C.Start.Menu.inventory(parent['raw'])==C.Start.Menu.inventory(trial['raw'])
    counts['current_named_menu_entries_unchanged']=100
    return dict(counts=dict(counts),Sonic_cold=sonic,
        scope='Five unaffected owners retain exact full cold RAM/maps/PPU/ABI; Prince source prefix/constructor and intended new code/header verified separately. All six owners warm/header/fault/guard/ordered transitions; Sonic cold-only, no gameplay admission.')


def transition_diagnostic(parent,trial,program):
    old,new=Sonic.O.blank(parent),Sonic.O.blank(trial)
    for m in (old,new):Sonic.C.cold(m,39,program['new'])
    a=Sonic.C.cold(old,42,program['new']);b=Sonic.C.cold(new,42,program['new'])
    Sonic.C.parity(old,new,a,b)
    fresh=Sonic.O.blank(trial);Sonic.C.cold(fresh,42,program['new'])
    written={(bank,at) for bank,at,_ in new.ram_writes}
    different=[(bank,hex(at),new.ram[bank][at],fresh.ram[bank][at]) for bank,at in sorted(written)
               if new.ram[bank][at]!=fresh.ram[bank][at]]
    return dict(transition=[39,42],exact_parent_vs_proposal=True,
                foreign_retire_writes_differ_from_fresh_constructor=different)


def alias_regression(trial):
    public=C.ROM.read_bytes();original=C.Start.W.bundle(public)
    authority=Alias.finite_sources(public,original)
    assert Alias.page_bytes(public,PAGE)==Alias.page_bytes(public,Alias.canonical(PAGE))
    with patch.object(N,'Bus',Alias.FundingBus):seeds=[N.fresh(b) for b in (original,trial)]
    counts=Counter()
    for pose in range(256):
        for face in (1,2):
            pair=[]
            for seed in seeds:
                m=Sonic.slim_fork(seed)
                N.put(m,SelectedCharacter=5,Z2Variant=1,PlayerFacingDir=face,
                    Player_SprAttrib=0,VRAM_Buffer1_Offset=0,NmiDisable=255,FamilyMainCommit=1)
                a=N.invoke(m,'Z2SetPose',x=pose);b=N.invoke(m,'Z2PublishBody');Alias.regular_nmi(m)
                pair.append((m,a,b))
            assert pair[0][1:]==pair[1][1:] and Alias.normalize_state(pair[0][0])==Alias.normalize_state(pair[1][0]),(pose,face)
            assert not any(p in Alias.TARGETS for _,p,_ in pair[1][0].pattern_events)
            counts['actual_pose_and_regular_NMI_pairs']+=1
    for pose in range(27):
        for face in (1,2):
            for scene in ('menu','lives','gameplay'):
                pair=[]
                for seed in seeds:
                    m=Sonic.slim_fork(seed)
                    N.put(m,SelectedCharacter=5,Z2Variant=1,PlayerFacingDir=face,
                        OperMode=0 if scene=='menu' else 1,GameEngineSubroutine=8,
                        Z2CachedPose=pose if pose<11 else 3,Z2ActiveSpells=1 if pose<11 else 9,
                        FrameCounter=0 if pose<11 else (pose-11)*4,Player_SprAttrib=0,
                        VRAM_Buffer1_Offset=0,NmiDisable=255,FamilyMainCommit=1,MmDeathFlag=0,
                        CurrentOAMOffset=0,Player_Rel_XPos=96,Player_Rel_YPos=176,Player_Y_HighPos=1)
                    if scene=='menu':N.invoke(m,'Z2PortraitGate')
                    elif scene=='lives':N.invoke(m,'DrawPlayer_Intermediate')
                    else:N.invoke(m,'Z2GraphicsGate');N.invoke(m,'Z2DrawShots')
                    Alias.regular_nmi(m);pair.append(m)
                assert Alias.normalize_state(pair[0])==Alias.normalize_state(pair[1]),(pose,face,scene)
                counts[scene+'_world_HUD_pairs']+=1
    alias=json.loads((R/'docs/qa/allocations/sonic-sms-fairy-repack-1110.json').read_bytes())['mandatory_atomic_source_change']
    broken=bytearray(trial['raw']);at=alias['file_offset'];broken[at:at+27]=bytes.fromhex(alias['old_hex'])
    with patch.object(N,'Bus',Alias.FundingBus):m=N.fresh(dict(trial,raw=bytes(broken)))
    N.put(m,SelectedCharacter=5,Z2Variant=1,PlayerFacingDir=1,NmiDisable=255,FamilyMainCommit=1)
    N.invoke(m,'Z2SetPose',x=21);N.invoke(m,'Z2PublishBody');Alias.regular_nmi(m)
    assert any(p==PAGE and h!=digest(Alias.page_bytes(public,PAGE)) for _,p,h in m.pattern_events)
    counts['undo_alias_page329_negative']+=1
    return dict(counts=dict(counts),sole_original_domain_overlap=authority['sole_domain_overlap'],
        future_conditional_pages=list(range(330,335)),page329_now_Prince=True)


def append_readback_faults(trial,chunks,layout,program):
    cases=[]
    for kind in ('copy-first','copy-last','reread-first','reread-last','decoder-state-last'):
        m=Sonic.O.blank(trial);bus=type(m);read,write=bus.__getitem__,bus.__setitem__
        native=N.NesMPU;pc=-1;starts=0;injected=False
        at=(0xc300+layout['packed_bytes'][2]-layout['new_page_payload_bytes']
            if kind.endswith('first') else 0xc300+layout['packed_bytes'][2]-1)
        class Trace(native):
            def step(self):
                nonlocal pc,starts
                if self.memory is m:
                    pc=self.pc
                    if pc==0xc000 and m.rawtags[2]==2:starts+=1
                return super().step()
        def reader(self,key):
            nonlocal injected
            value=read(self,key)
            if self is m and not injected and kind.startswith('reread') and key==0x2007 and pc==layout['read_source_PC']:
                lo=0 if kind.endswith('first') else layout['new_page_payload_bytes']-1
                if m.ram[2][0x224]==14 and m.ram[2][0x225]==lo and m.ram[2][layout['data_op_PC']-0xc000]==0xd1:
                    injected=True;return value^1
            return value
        def writer(self,key,value):
            nonlocal injected
            if self is m and not injected:
                copy=kind.startswith('copy') and pc==layout['data_op_PC'] and m.ram[2][0x224]==14 and key==at
                decode=kind=='decoder-state-last' and starts==3 and pc==0xc0c8 and key==0xc100+len(chunks[2])-1
                if copy or decode:injected=True;value^=1
            return write(self,key,value)
        with patch.object(bus,'__getitem__',reader),patch.object(bus,'__setitem__',writer),patch.object(N,'NesMPU',Trace),patch.object(Sonic.O,'NesMPU',Trace):
            result=Sonic.C.cold(m,38,program['new'],expect_success=False)
        assert injected and Sonic.O.headers(m)==(bytes(16),bytes(16)),kind
        assert not Sonic.C.invoke(m,Sonic.O.AUTH)['P']&1
        cases.append(dict(kind=kind,actual_fault_injected=True,both_headers_invalid=True,cold=result))
    return cases


def main():
    cli=argparse.ArgumentParser(description=__doc__);cli.add_argument('--static',action='store_true')
    cli.add_argument('--poses',action='store_true');cli.add_argument('--lifecycle',action='store_true')
    cli.add_argument('--negative',action='store_true')
    cli.add_argument('--fixture',action='store_true')
    cli.add_argument('--owners',action='store_true')
    cli.add_argument('--admission',action='store_true')
    cli.add_argument('--alias',action='store_true')
    cli.add_argument('--readback',action='store_true')
    cli.add_argument('--transition-diagnostic',action='store_true')
    args=cli.parse_args();parent,trial,chunks,layout,program,packet,rows=proposal()
    print('FUNDED_LAYOUT '+json.dumps(layout),flush=True)
    if args.static:return
    model,cold=actual_cold(trial,chunks,layout,program)
    print('ACTUAL_COLD '+json.dumps(cold),flush=True)
    geometry=N.fork(model);geometry.ram[3][0x1d3e:0x1d42]=bytes.fromhex('4cd7d4ea')
    print('FROZEN_DIRECT_GEOMETRY '+json.dumps(Foot.matrix(geometry)),flush=True)
    if args.admission:print('ADMISSION_MATRIX '+json.dumps(admission_matrix(model)),flush=True)
    if args.negative:print('OVERLAP_NEGATIVE '+json.dumps(overlap_negative(trial,chunks,layout,program)),flush=True)
    if args.poses:print('ALL_POSES '+json.dumps(poses(parent,trial,model)),flush=True)
    if args.lifecycle:print('LANDING_LIFECYCLE '+json.dumps(landing_and_lifecycle(trial)[0]),flush=True)
    if args.fixture:print('FIXTURE_DIAGNOSTIC '+json.dumps(fixture_diagnostic(trial)),flush=True)
    if args.owners:print('ALL_OWNERS '+json.dumps(owner_regressions(parent,trial,chunks,layout,program,packet,rows)),flush=True)
    if args.alias:print('Z2_ALIAS '+json.dumps(alias_regression(trial)),flush=True)
    if args.readback:print('APPEND_READBACK_FAULTS '+json.dumps(append_readback_faults(trial,chunks,layout,program)),flush=True)
    if args.transition_diagnostic:print('TRANSITION_DIAGNOSTIC '+json.dumps(transition_diagnostic(parent,trial,program)),flush=True)


if __name__=='__main__':main()
