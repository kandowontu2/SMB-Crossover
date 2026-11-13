"""Zero-output semantic funding and accepted-head qualification."""
import argparse
from hashlib import sha256
from itertools import product
import json
import re
from unittest.mock import patch

import check_dkjr_powerups_current_1113 as B
import compose_dkjr_head_bridge_1113 as T

N,W,L=B.N,B.W,B.L


def call(m,pc,*,a=0,x=0,y=0,p=0x31,observe=None):
    m.raw_page(1,3);m.raw_page(2,2);N.put(m,CurrentBank=3,CurrentBankC=2)
    c=N.NesMPU(memory=m,pc=pc);c.a,c.x,c.y,c.p,c.sp=a,x,y,p,224
    c.stPushWord(0x5aff)
    for step in range(100000):
        if(c.pc,c.sp)==(0x5b00,224):return c
        if observe:observe(m,c)
        assert m[c.pc],('BRK',hex(c.pc),c.sp)
        c.step()
    raise AssertionError(('CPU bound',hex(c.pc),c.sp))


def mounted(seed,raw,cookie):
    m=L.clone(seed);m.bundle=dict(seed.bundle,raw=raw)
    body=T.payload(raw)
    m.ram[3][:0x1fe0]=body[:0x1fe0]
    m.ram[2][0x1000:0x1800]=body[9*1024:]
    for bank in(2,3):m.ram[bank][0x1fe0:0x1ff0]=cookie
    m.ram[2][T.HEAD_X-0xc000:T.HEAD_TOP-0xc000+1]=bytes(3)
    return m


def rect_funding(seed,parent,candidate,info):
    rows=0;minimum=255
    # Both typed native RAM lists and the original low-2KB virtual pointers.
    # Include signed offsets, byte wraps, FF in non-sentinel coordinates,
    # overlap edges, misses, all caller flags and varied entry registers.
    pointers=(0x0700,0xc700)
    origins=((0,0),(13,32),(240,239),(255,255))
    records=(bytes([0,0,15,15,255]),bytes([1,1,255,255,255]),
        bytes([16,32,31,47,240,128,255,144,255]),bytes([255]))
    for kind,ptr,origin,record,flags in product(range(3),pointers,origins,records,(0x20,0x21,0x64,0xa1)):
        outputs=[]
        for raw,cookie in((parent,B.COOKIE),(candidate,bytes.fromhex(info['cookie']))):
            m=mounted(seed,raw,cookie)
            m.ram[2][0x700:0x720]=record.ljust(32,b'\xff')
            m.ram[2][0:4]=bytes([origin[0],origin[1],ptr&255,ptr>>8])
            m.ram[2][0x3e:0x42]=bytes([0,0,15,15])
            c=call(m,T.RECT_START,a=kind,x=71,y=203,p=flags)
            minimum=min(minimum,c.sp)
            outputs.append(((c.a,c.x,c.y,c.p,c.sp),bytes(m.ram[2][:0x800]),
                bytes(m[:0x100]),tuple(m.rawtags)))
        assert outputs[0]==outputs[1],(kind,ptr,origin,record.hex(),flags,outputs[0][0],outputs[1][0])
        rows+=1
    return dict(paired_cases=rows,all_original_source_RAM_equal=True,complete_AXYP_SP_equal=True,
        pointer_conversion_preserved=True,minimum_return_SP=minimum,
        scope='Declared source rectangle fixtures; does not grant native gameplay coverage.')


def source_closure(parent,candidate,info):
    text,_,_,_=T.old_source();start=text.index('D_eb75:');end=text.index('D_ebe3:')
    outside=text[:start]+text[end:]
    private=('D_eb75','D_eb96','D_ebb6','D_ebb8','D_ebba','D_ebc1','D_ebc9','D_ebcd','D_ebd0','D_ebd9')
    references=[]
    for line in outside.splitlines():
        code=line.split(';',1)[0].strip()
        if not code or code.startswith(('.export ','.setcpu')):continue
        if any(re.search(r'\b'+name+r'\b',code)for name in private):references.append(code)
    assert references==['jmp D_eb75','jmp D_eb75'],references
    body=T.payload(parent)
    assert body[T.RECT_START-0xa000-12:T.RECT_START-0xa000]==bytes.fromhex('a9004ceaada9014ceaada902')
    cache_refs=[line.strip()for line in text.splitlines()if re.search(r'\$c4b[4567]\b',line,re.I)]
    assert len(cache_refs)==8 and all(line.startswith(('sta ','stx ','sty ','lda ','ldx ','ldy '))for line in cache_refs)
    atlas=json.loads(T.retained(T.ATLAS,'dkjr-native-services-v50',
        'b4f92c29b524a6c4fe0a4ceb92ab95a1e2878ee19a997a84605e04ef3adcc682'))
    pixels=0
    for row in atlas['all_legal_8x16_selections']:
        if row['native_tile']in(89,91,93,95):continue # Existing qualified aliases129..135.
        at=B.CHR+1024*row['physical_page'];lo,hi=row['physical_byte_half_open']
        assert parent[at+lo:at+hi]==candidate[at+lo:at+hi]
        pixels+=hi-lo
    assert parent[B.CHR+960*1024+384:B.CHR+960*1024+395]==candidate[B.CHR+960*1024+384:B.CHR+960*1024+395]
    return dict(original_entry_kinds=[0,1,2],only_two_absolute_callers_plus_kind2_fallthrough=True,
        internal_source_labels_not_published_as_data=True,retired_AXYP_cache_literal_references=len(cache_refs),
        retained_original_source_SHA256=T.FROZEN_SHA,all_live_art_bytes_equal=pixels,
        existing_hanging_alias_unchanged=True,no_tree_extraction=True)


def indirect_reads(seed,parent,candidate,info):
    count=0
    for pointer,y in product((0x0000,0x0700,0xa000,0xb700,0xc700,0xe000),range(256)):
        results=[]
        for raw,cookie,pc,stop in((parent,B.COOKIE,0xae0d,0xae26),
            (candidate,bytes.fromhex(info['cookie']),info['labels']['RectRead'],0x5b00)):
            m=mounted(seed,raw,cookie)
            m.ram[2][2:4]=bytes([pointer&255,pointer>>8])
            m.raw_page(1,3);m.raw_page(2,2)
            c=N.NesMPU(memory=m,pc=pc);c.a,c.x,c.y,c.p,c.sp=83,71,y,y,224;c.stPushWord(0x5aff)
            for _ in range(100):
                if c.pc==stop:break
                c.step()
            else:raise AssertionError(('Read primitive bound',hex(c.pc)))
            results.append((c.a,c.x,c.y,c.p,bytes(m.ram[2][:0x800])))
        assert results[0]==results[1],(pointer,y,results[0][:4],results[1][:4])
        count+=1
    return dict(paired_pointer_Y_flag_cases=count,all_256_Y_and_P_values=True,
        virtual_low_RAM_and_native_ROM_conversion_equal=True)


def cold(raw,cookie):
    bundle=W.Symbols.bundle();bundle['raw']=raw;body=T.payload(raw)
    checks=[];pending=None;Base=N.NesMPU
    class Probe(Base):
        def step(self):
            nonlocal pending
            m=self.memory
            if self.pc==0xd25e and m.rawtags[2]==2:
                pending=(m[0x100+((self.sp+1)&255)]+256*m[0x100+((self.sp+2)&255)]+1,(self.sp+2)&255)
            if pending==(self.pc,self.sp):
                assert self.p&1 and bytes(m.ram[3][:0x1fe0])==body[:0x1fe0]
                assert bytes(m.ram[2][0x1000:0x1800])==body[9*1024:]
                checks.append(True);pending=None
            return Base.step(self)
    with patch.object(N,'NesMPU',Probe):opening,m=B.C.cold(bundle,B.ROW)
    assert checks and all(bytes(m.ram[i][0x1fe0:0x1ff0])==cookie for i in(2,3))
    # The parent still uses C4B6 as its saved register cache. Only the new
    # authenticated payload interprets it as a head-event record.
    if cookie!=B.COOKIE:assert m.ram[2][T.HEAD_TOP-0xc000]==0
    return opening,m


def capture(seed,parent,candidate,info):
    results=[]
    for world_mode,head_top,bottom,start in product((0,1),(143,158,159,160,170),(159,),(158,159,162)):
        m=mounted(seed,candidate,bytes.fromhex(info['cookie']))
        m.ram[2][0x8da]=world_mode;m.ram[2][0x3f]=head_top
        m.ram[2][0x42:0x46]=bytes([100,144,115,bottom]);m.ram[2][0x76]=start
        N.put(m,ScreenLeft_X_Pos=236,ScreenLeft_PageLoc=0)
        c=call(m,T.HOOK,a=1,x=255,y=29,p=0x31)
        queued=bool(m.ram[2][T.HEAD_TOP-0xc000])
        expected=bool(world_mode and 0<=bottom-head_top<2 and bottom<start)
        assert queued==expected and(c.a,c.x,c.y,c.p&0xc3)==(4,255,29,0x01)
        assert m.ram[2][0x6b]==4
        if queued:assert bytes(m.ram[2][T.HEAD_X-0xc000:T.HEAD_TOP-0xc000+1])==bytes([80,1,144])
        results.append(dict(mode=world_mode,source_head_top=head_top,cell_bottom=bottom,jump_start=start,queued=queued))
    return dict(guard_cases=len(results),cases=results,original_fall_AXY_CNZ_preserved=True)


def effect_gates(seed,candidate,info):
    labels=info['labels'];bank=labels['NativeHeadBank'];entry=labels['NativeHeadEffect']
    class Entered(Exception):pass
    rows=admitted=0
    for tile,guard in product(range(256),('none','bounce','hurt','pause')):
        m=mounted(seed,candidate,bytes.fromhex(info['cookie']))
        m.ram[2][T.HEAD_X-0xc000:T.HEAD_TOP-0xc000+1]=bytes([80,1,144])
        m[0x445]=tile
        N.put(m,BlockBounceTimer=int(guard=='bounce'),GuestHurtTicks=int(guard=='hurt'),TimerControl=int(guard=='pause'))
        seen=[]
        def observe(memory,cpu):
            if cpu.pc==entry and memory.rawtags[1]==bank:
                seen.append(cpu.a);raise Entered
        try:call(m,labels['DkHeadFlush'],observe=observe)
        except Entered:pass
        expected=(m[W.address(m.bundle,'MTileAttribute')+tile]&7)==1 and guard=='none'
        assert bool(seen)==expected,(tile,guard,seen,expected)
        assert not m.ram[2][T.HEAD_TOP-0xc000]
        if seen:
            assert seen==[tile]and(m[5],m[9],m[10])==(112,0xd5,3)
            admitted+=1
        rows+=1
    return dict(material_timer_cases=rows,admitted=admitted,all_pending_records_consumed=True,
        exact_contact_packet=True,scope='CPU gate stopped at actual native effect entry; not a gameplay/item claim.')


def native_effect(seed,candidate,info):
    rows=[]
    for amount,flags in product((0,0x12),(0x20,0x21,0x64,0xa1)):
        m=mounted(seed,candidate,bytes.fromhex(info['cookie']))
        reference=mounted(seed,seed.bundle['raw'],B.COOKIE)
        m.ram[2][T.HEAD_X-0xc000:T.HEAD_TOP-0xc000+1]=bytes([80,1,144])
        m.ram[2][0x8f9]=amount;m[0x445]=193
        reference.ram[2][0x8f9]=amount
        original=call(reference,T.SCORE_START,a=83,x=71,y=109,p=flags)
        expected=(original.a,original.x,original.y,original.p,original.sp)
        N.put(m,BlockBounceTimer=0,GuestHurtTicks=0,TimerControl=0)
        scratch=bytes(m[3:11]);smc=bytes(m[0x15a:0x17b]);obj=N.get(m,'ObjectOffset')
        events=[];minimum=255
        def observe(memory,cpu):
            nonlocal minimum
            minimum=min(minimum,cpu.sp)
            if cpu.pc==info['labels']['NativeHeadEffect']and memory.rawtags[1]==info['labels']['NativeHeadBank']:
                events.append(dict(A=cpu.a,packet=[m[5],m[9],m[10]]))
        c=call(m,T.SCORE_START,a=83,x=71,y=109,p=flags,observe=observe)
        assert(c.a,c.x,c.y,c.p,c.sp)==expected,((c.a,c.x,c.y,c.p,c.sp),expected)
        assert bytes(m[3:11])==scratch and bytes(m[0x15a:0x17b])==smc
        assert N.get(m,'ObjectOffset')==obj and tuple(m.rawtags[1:3])==(3,2)
        assert len(events)==1 and events[0]['A']==193 and events[0]['packet']==[112,0xd5,3]
        assert m[0x445]==35 and N.get(m,'BlockBounceTimer')==16
        assert not m.ram[2][T.HEAD_TOP-0xc000]
        c2=call(m,T.SCORE_START,a=83,x=71,y=109,p=flags,observe=observe)
        assert len(events)==1 and(c2.a,c2.x,c2.y,c2.p)==expected[:4]
        rows.append(dict(score=amount,flags=flags,minimum_SP=minimum,actual_head_calls=len(events),cell_after=m[0x445]))
    return dict(cases=rows,borrowed_scratch_SMC_ObjectOffset_maps_restored=True,one_Main_record_no_replay=True,
        scope='Declared contact record fixture through real native block core. Natural earned-item route remains separate.')


def allocator(seed,candidate,info):
    _,linked=T.girder_images();labels=linked['symbols']
    lefts=(336,416,480,560,624,688,752,880,944,1408,2576,2640,2832,3040)
    scope=0;births=0
    def fixture(camera,seen):
        m=L.clone(seed)
        N.put(m,ScreenLeft_X_Pos=camera&255,ScreenLeft_PageLoc=camera>>8,AreaDataLow=0xce)
        m.ram[2][0x8fd]=seen
        return m
    # All camera values plus exhaustive prior ordinals at every admission edge.
    cases={(cam,0)for cam in range(12*256)}
    cases|={(left-d,seen)for left in lefts for d in(288,287,256,255)for seen in range(256)}
    for camera,seen in sorted(cases):
        m=fixture(camera,seen)
        expected=next((i for i,left in enumerate(lefts)if camera<11*256 and i>=seen and 256<=left-camera<=287),None)
        c=call(m,labels['DkPipeScope'])
        assert bool(c.p&1)==(expected is not None),(camera,seen,expected)
        assert m.ram[2][0x8fd]==(seen if expected is None else expected)
        scope+=1
    for row,left in enumerate(lefts):
        for available in range(6):
            m=fixture(left-287,row)
            for i in range(6):
                m[W.address(m.bundle,'Enemy_Flag')+i]=int(i!=available)
                m[W.address(m.bundle,'Enemy_ID')+i]=6
            prior_scratch=bytes(m[3:14]);prior_smc=bytes(m[0x15a:0x17b])
            c=call(m,labels['DkRefreshPlatform'],a=83,x=71,y=109,p=0x21)
            assert(c.a,c.x,c.y,c.p&0xc3,c.sp)==(83,71,109,1,224)
            assert bytes(m[3:14])==prior_scratch and bytes(m[0x15a:0x17b])==prior_smc
            horizontal=row==9
            assert N.get(m,'Enemy_Flag',available)==1
            assert N.get(m,'Enemy_ID',available)==(40 if horizontal else 37)
            assert N.get(m,'Enemy_X_Position',available)+256*N.get(m,'Enemy_PageLoc',available)==left
            assert N.get(m,'Enemy_Y_Position',available)==(208 if horizontal else 192)
            assert m[0x646+available]==(6 if horizontal else 5)
            assert m.ram[2][0x8fd]==row+1
            births+=1
    return dict(scope_cases=scope,slot_birth_cases=births,rows=14,
        all_thirteen_previous_placements_retained=True,original_six_helper_slots_retained=True,
        caller_AXYP_scratch_SMC_preserved=True)


def foreign(before,after):
    count=0
    for owner in range(44):
        if owner==40:continue
        for alt in((0,16,32)if owner==9 else(0,)):
            for name in('HuMovement','HuHead','HuSide','HuFresh','HuPickup'):
                results=[]
                for seed in(before,after):
                    m=L.clone(seed);N.put(m,SelectedCharacter=owner,FmAlts=alt)
                    baseline=tuple(bytes(bank)for bank in m.ram)
                    result=N.invoke(m,name,a=2,x=5,y=3,p=0x61)
                    delta=[(bank,i,a,z)for bank,(old,new)in enumerate(zip(baseline,m.ram))
                        for i,(a,z)in enumerate(zip(old,new))if a!=z]
                    results.append((tuple(result[k]for k in('A','X','Y','P')),delta,tuple(m.rawtags),
                        bytes(m[:0x100]),bytes(m[0x200:0x800]),bytes(m[0x5c00:0x8000])))
                assert results[0]==results[1],(owner,alt,name)
                count+=1
    return dict(foreign_callback_pairs=count,all_foreign_owners=43,raw9_three_forms=True,
        exact_AXYP_native_fields_maps_WRAM_deltas=True)


def rebase(installed,parent):
    baseline,old_info=T.transform(parent,helper=True)
    current,info=T.transform(installed,helper=True)
    old_delta=[(i,a,z)for i,(a,z)in enumerate(zip(parent,baseline))if a!=z]
    delta=[(i,a,z)for i,(a,z)in enumerate(zip(installed,current))if a!=z]
    assert delta==old_delta
    assert T.inverse(current)==installed and T.inverse(baseline)==parent
    return dict(installed_SHA256=sha256(installed).hexdigest(),proof_parent_SHA256=sha256(parent).hexdigest(),
        rebased_candidate_SHA256=info['candidate_SHA256'],AA_candidate_SHA256=old_info['candidate_SHA256'],
        identical_byte_edits=len(delta),all_Steve_bytes_retained=True,inverse_exact=True,ROM_written=False)


def cold_audit(seed,candidate,info):
    body=T.payload(candidate);cookie=bytes.fromhex(info['cookie']);rows=[]
    seed=L.clone(seed);seed.bundle=dict(seed.bundle)
    seed.bundle['syms']=dict(seed.bundle['syms']);seed.bundle['segs']=dict(seed.bundle['segs'])
    at=16+65*8192+0xe00
    assert candidate[at:at+10]==bytes.fromhex('08488a489848a900f008')
    seed.bundle['segs']['DKHeadCoCold']=dict(start=str(0xae00),ooffs=str(at))
    seed.bundle['syms']['CoCold']=dict(val=str(0xae00),seg='DKHeadCoCold')
    for fault in(None,T.RECT_START,T.HOOK):
        m=L.clone(seed);m.bundle=dict(seed.bundle,raw=candidate)
        m.ram[2][0x1fe0]=m.ram[3][0x1fe0]=0
        N.put(m,SelectedCharacter=40,OperMode=1,FamilyMainCommit=1,DisableScreenFlag=1,
            Mirror_PPUMASK=0,NmiDisable=255)
        Base=type(m)
        class Fault(Base):
            def __getitem__(self,at):
                value=Base.__getitem__(self,at)
                if fault is not None and at==fault and self.rawtags[1]==3:
                    self.fault_reads+=1;return value^1
                return value
        m.__class__=Fault;m.fault_reads=0
        before=m.ppu_reads
        result=N.invoke(m,'CoCold',p=0x21)
        assert bool(result['P']&1)==(fault is None)
        if fault is None:
            assert bytes(m.ram[3][:0x1fe0])==body[:0x1fe0]
            assert bytes(m.ram[2][0x1000:0x1800])==body[9*1024:]
            assert bytes(m.ram[2][:0x900])==bytes(0x900)
            assert all(bytes(m.ram[bank][0x1fe0:0x1ff0])==cookie for bank in(2,3))
            reads=m.ppu_reads;again=N.invoke(m,'CoCold',p=0x21)
            assert again['P']&1 and m.ppu_reads==reads
        else:
            assert m.fault_reads and not m.ram[2][0x1fe0]and not m.ram[3][0x1fe0]
        rows.append(dict(readback_fault=fault,accepted=bool(result['P']&1),PPU_reads=m.ppu_reads-before,
            fault_reads=m.fault_reads,minimum_SP=result['minimum_SP']))
    rejected=0
    for mask,disabled,lag in((24,1,255),(0,0,255),(0,1,0)):
        m=L.clone(seed);m.ram[2][0x1fe0]=m.ram[3][0x1fe0]=0
        N.put(m,Mirror_PPUMASK=mask,DisableScreenFlag=disabled,NmiDisable=lag)
        before=m.ppu_reads;result=N.invoke(m,'CoCold',p=0x21)
        assert not result['P']&1 and m.ppu_reads==before
        assert not m.ram[2][0x1fe0]and not m.ram[3][0x1fe0]
        rejected+=1
    stale=0
    for bank in(2,3):
        m=L.clone(seed);m.ram[bank][0x1fe0:0x1ff0]=B.COOKIE;seen=[]
        def observe(memory,cpu):
            if 0xa000<=cpu.pc<0xc000 and memory.rawtags[1]==3:seen.append(cpu.pc)
        before=m.ppu_reads;L.call(m,'HuMovement',p=0x21,observe=observe)
        assert not seen and m.ppu_reads==before
        stale+=1
    return dict(cold_rows=rows,wrong_phase_rejections=rejected,stale_old_cookie_rejections=stale,
        complete_code_metadata_readback=True,both_headers_commit_after_verify=True,warm_no_copy=True)


def interrupts(seed,candidate,info):
    import check_metal_head_bridge_1112 as Async
    from replay_dkjr_first_pickup_1113 import controller
    samples={};frame_keys=set();expected={};score_pending=None;deepest=256
    m=L.clone(seed)
    N.put(m,NmiDisable=255,FamilyMainCommit=1,GamePauseStatus=0)
    def observe(memory,cpu):
        nonlocal score_pending,deepest
        if score_pending==(cpu.pc,cpu.sp):score_pending=None
        if cpu.pc==T.SCORE_START and memory.rawtags[1]==3:
            score_pending=(memory[0x100+((cpu.sp+1)&255)]+256*memory[0x100+((cpu.sp+2)&255)]+1,(cpu.sp+2)&255)
        if score_pending and cpu.sp<deepest:
            deepest=cpu.sp;key=(0x10000,cpu.p&4)
            q,c=L.clone(memory,cpu);samples[key]=(q,c);frame_keys.add(key)
        if not 0xa000<=cpu.pc<0xc000 or memory.rawtags[1]!=3:return
        if not(any(pc<=cpu.pc<pc+size for pc,size in T.LAYOUT.values())):return
        key=(cpu.pc,cpu.p&4)
        if key not in samples or cpu.sp<samples[key][1].sp:
            q,c=L.clone(memory,cpu);samples[key]=(q,c);frame_keys.add(key)
    def after_frame(memory):
        if frame_keys:
            result=(tuple(memory.rawtags),bytes(memory.ram[2]),bytes(memory.ram[3]),
                B.state(memory),bytes(memory[0x15a:0x17b]))
            for key in frame_keys:expected[key]=result
            frame_keys.clear()
    result=B.route(m,candidate,2000,controller_text=controller(candidate),observe_extra=observe,after_frame=after_frame)
    assert result['passed']and samples
    counts=dict(IRQ=0,lagNMI=0);minimum=255
    stop=(W.address(m.bundle,'IdleLoop')+12,252)
    for key,(state,cpu)in sorted(samples.items()):
        for kind in('IRQ','lagNMI'):
            if kind=='IRQ'and cpu.p&4:continue
            q,c=L.clone(state,cpu)
            minimum=min(minimum,Async.inject(c,N.NesMPU,kind));counts[kind]+=1
            L.finish(q,c,stop)
            actual=(tuple(q.rawtags),bytes(q.ram[2]),bytes(q.ram[3]),B.state(q),bytes(q[0x15a:0x17b]))
            assert actual==expected[key],(key,kind,B.state(q),expected[key][3])
    assert counts['IRQ']and counts['lagNMI']and minimum>=128
    return dict(cuts=counts,unique_deepest_instruction_points=len(samples),minimum_ISR_SP=minimum,
        native_effect_deepest_SP=deepest,real_native_vectors=True,complete_interrupted_Main_matches=True,
        earned_route_controller_SHA256=result['controller_SHA256'])


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--helper-fixture',action='store_true')
    ap.add_argument('--current',action='store_true',help='Execute the exact authenticated installed successor rather than its frozen AA inverse.')
    ap.add_argument('--route',action='store_true');ap.add_argument('--allocator',action='store_true')
    ap.add_argument('--foreign',action='store_true');ap.add_argument('--cold-audit',action='store_true')
    ap.add_argument('--interrupts',action='store_true');ap.add_argument('--full-stage',action='store_true');args=ap.parse_args()
    installed=B.C.ROM.read_bytes();parent,input_info=B.proof_parent(installed)
    raw=installed if args.current else parent
    print('DKJR_PROOF_INPUT '+json.dumps(input_info,separators=(',',':')),flush=True)
    if installed!=parent:print('DKJR_HEAD_CURRENT_REBASE '+json.dumps(rebase(installed,parent),separators=(',',':')),flush=True)
    candidate,info=T.transform(raw,helper=args.route or args.allocator or args.interrupts or args.full_stage)
    assert T.inverse(candidate)==raw
    print('DKJR_HEAD_COMPOSE '+json.dumps({k:v for k,v in info.items()if k!='labels'},separators=(',',':')),flush=True)
    print('DKJR_HEAD_SOURCE_CLOSURE '+json.dumps(source_closure(raw,candidate,info),separators=(',',':')),flush=True)
    if raw==parent:_,seed,_=B.cold(raw)
    else:_,seed=cold(raw,B.COOKIE)
    print('DKJR_HEAD_RECT_FUNDING '+json.dumps(rect_funding(seed,raw,candidate,info),separators=(',',':')),flush=True)
    print('DKJR_HEAD_INDIRECT '+json.dumps(indirect_reads(seed,raw,candidate,info),separators=(',',':')),flush=True)
    print('DKJR_HEAD_CAPTURE '+json.dumps(capture(seed,raw,candidate,info),separators=(',',':')),flush=True)
    print('DKJR_HEAD_EFFECT_GATES '+json.dumps(effect_gates(seed,candidate,info),separators=(',',':')),flush=True)
    print('DKJR_HEAD_NATIVE_EFFECT '+json.dumps(native_effect(seed,candidate,info),separators=(',',':')),flush=True)
    opening,m=cold(candidate,bytes.fromhex(info['cookie']))
    assert B.state(m)==B.state(seed),(B.state(m),B.state(seed))
    print('DKJR_HEAD_CURRENT_COLD '+json.dumps(dict(opening=opening,final=B.state(m),readback=8160,metadata=2048),separators=(',',':')),flush=True)
    if args.allocator:print('DKJR_HEAD_ALLOCATOR '+json.dumps(allocator(m,candidate,info),separators=(',',':')),flush=True)
    if args.foreign:print('DKJR_HEAD_FOREIGN '+json.dumps(foreign(seed,m),separators=(',',':')),flush=True)
    if args.cold_audit:print('DKJR_HEAD_COLD_AUTH '+json.dumps(cold_audit(m,candidate,info),separators=(',',':')),flush=True)
    if args.interrupts:print('DKJR_HEAD_INTERRUPTS '+json.dumps(interrupts(m,candidate,info),separators=(',',':')),flush=True)
    if args.helper_fixture:
        result=B.helper_fixture(m,max_platform_slot=5,left=336,target_x=344,wait_maturity=True,followup_updates=30)
        print('DKJR_HEAD_HELPER_FIXTURE '+json.dumps(result,separators=(',',':')),flush=True)
        assert result['passed']
    if args.route:
        from replay_dkjr_first_pickup_1113 import controller
        text=controller(candidate)
        result=B.route(m,candidate,2000,controller_text=text)
        print('DKJR_HEAD_NATURAL_FIRST '+json.dumps({k:v for k,v in result.items()if k!='receipt'},separators=(',',':')),flush=True)
        assert result['passed']
    if args.full_stage:
        from replay_dkjr_first_pickup_1113 import full_stage_controller
        text=full_stage_controller(candidate)
        result=B.route(m,candidate,12000,controller_text=text)
        print('DKJR_HEAD_FULL_STAGE '+json.dumps({k:v for k,v in result.items()if k!='receipt'},separators=(',',':')),flush=True)
        assert result['passed']


if __name__=='__main__':main()
