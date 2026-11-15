"""Exact leased renderer arrays only; no ROM composition or gameplay claim."""
from collections import Counter
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import argparse,json,sys,subprocess
import plan_prince_window567_1114 as Plan
import check_prince_natural_sword_1113 as Game
import prince_cold_packet_1111 as Packet
import check_bub_current_budget_1113 as Frames

N,W=Game.N,Game.W
GRANT=Packet.R/'docs/qa/allocations/prince-window567-research-1114.json'
GRANT_SHA='b764a508c3115cadeadb8ad21dfbc406cf8f392ae2c95b5854ae6f247cf2d6a6'
PLAN_SHA='cd82f437cfc824c6c6f14cacfdaff3181701f930ea4f99993251c2f345dbacb6'


def arrays(raw):
    data=GRANT.read_bytes();assert sha256(data).hexdigest()==GRANT_SHA
    grant=json.loads(data);assert sha256(Path(Plan.__file__).read_bytes()).hexdigest()==PLAN_SHA
    assert sha256(raw).hexdigest()==grant['eligible_input_SHA256']
    original=Packet.extract(raw)[1];captured={};prior=sys.getprofile()
    def trace(frame,event,arg):
        if frame.f_code is Plan.run.__code__ and event=='return':captured['metadata']=bytes(frame.f_locals['transformed'])
    sys.setprofile(trace)
    try:math=Plan.run(raw)
    finally:sys.setprofile(prior)
    proposed=list(map(bytearray,original));proposed[1][:]=captured['metadata']
    for row in grant['envelopes']:
        lo=row['offset'];hi=lo+row['bytes'];stream=row['stream']
        if'old_hex'in row:
            assert original[stream][lo:hi]==bytes.fromhex(row['old_hex'])
            proposed[stream][lo:hi]=bytes.fromhex(row['new_hex'])
        else:
            assert sha256(original[stream][lo:hi]).hexdigest()==row['old_SHA256']
            assert sha256(proposed[stream][lo:hi]).hexdigest()==row['new_SHA256']
    for stream,(old,new)in enumerate(zip(original,proposed)):
        allowed={k for row in grant['envelopes']if row['stream']==stream for k in range(row['offset'],row['offset']+row['bytes'])}
        assert len(old)==len(new)and all(a==b for k,(a,b)in enumerate(zip(old,new))if k not in allowed)
    return tuple(map(bytes,proposed)),math


def cold(raw):
    def identity(image):assert image==raw;return raw
    with patch.object(Game,'proof_parent',identity):m,opening=Game.cold(raw)
    assert N.get(m,'SelectedCharacter')==38
    return m,dict(opening,scope='Compiled Select/Start peripheral unit; no real vblank/native cadence')


def mounted(seed,parts):
    m=N.fork(seed)
    # Only the three root-leased extents are mounted after real original cold.
    for row in json.loads(GRANT.read_bytes())['envelopes']:
        bank=3 if row['stream']==0 else 2;lo=row['live_PC']&8191
        m.ram[bank][lo:lo+row['bytes']]=parts[row['stream']][row['offset']:row['offset']+row['bytes']]
    return m


def run(raw,*,interrupts=False):
    parts,math=arrays(raw);seed,opening=cold(raw);original=Packet.extract(raw)[1]
    pair=(N.fork(seed),mounted(seed,parts));native=N.NesMPU;counts=Counter();minimum=255
    data_readers=Counter();data_writes=Counter()
    old_bounds=Plan.tile_locations(original[1])[1]
    bounds=[]
    for data in(original[1],parts[1]):
        rows={}
        for frame in range(239):
            tag=int.from_bytes(data[2*frame:2*frame+2],'little')
            if tag==65535:continue
            oldtag=int.from_bytes(original[1][2*frame:2*frame+2],'little');lo,hi=old_bounds[oldtag]
            start=0xc800+(tag&0x3fff);rows[frame]=(start,start+hi-lo)
        bounds.append(rows)
    for which,m in enumerate(pair):
        m._pose_bounds=bounds[which]
        parent=type(m)
        class DataBus(parent):
            def __getitem__(self,at):
                if isinstance(at,int)and 0xc800<=at<0xdfe0 and self.rawtags[2]==2 and getattr(self,'_render_pc',None)==(0xbcf4,3):
                    lo,hi=self._pose_bounds[self._render_frame]
                    assert lo<=at<hi,('Actual Byte reader exceeded the specific pose packet',self._render_frame,hex(at),hex(lo),hex(hi))
                if isinstance(at,int)and 0xc800<=at<0xd466 and self.rawtags[2]==2:
                    pc=getattr(self,'_render_pc',None)
                    if pc:data_readers[pc]+=1
                return super().__getitem__(at)
            def __setitem__(self,at,value):
                if isinstance(at,int)and 0xc800<=at<0xd466 and self.rawtags[2]==2:
                    data_writes[getattr(self,'_render_pc',None)]+=1
                return super().__setitem__(at,value)
        m.__class__=DataBus
    def interrupt(cpu,kind):
        nonlocal minimum
        m=N.fork(cpu.memory);c=native(memory=m,pc=cpu.pc)
        c.a,c.x,c.y,c.p,c.sp=cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp
        before=([bytes(r)for r in m.ram],bytes(m[3:11]),bytes(m[0x15a:0x17b]),m.rawtags[:],m.chr_latches[:])
        native_before=bytearray(m[0x200:0x800])
        regs=(c.a,c.x,c.y,c.p,c.sp,c.pc);skip=N.get(m,'NmiSkipped')
        protected_stack=bytes(m[0x101+regs[4]:0x200])
        c.irq()if kind=='IRQ'else c.nmi()
        for _ in range(100000):
            minimum=min(minimum,c.sp)
            if(c.pc,c.sp)==(regs[5],regs[4]):break
            assert c.sp<=regs[4]and m[c.pc]
            c.step()
        else:raise AssertionError('Renderer ISR bounded return')
        assert(c.a,c.x,c.y,c.p&239,c.sp,c.pc)==(*regs[:3],regs[3]&239,*regs[4:])
        after=([bytes(r)for r in m.ram],bytes(m[3:11]),bytes(m[0x15a:0x17b]),m.rawtags[:],m.chr_latches[:])
        assert before==after,'ISR private/scratch/mapper/CHR exact'
        native_after=bytearray(m[0x200:0x800])
        if kind=='busyNMI':
            assert N.get(m,'NmiSkipped')==(skip+1)&255
            native_before[0x7da-0x200]=native_after[0x7da-0x200]=0
        assert native_before==native_after,'ISR native RAM exact except busy audio duration'
        assert bytes(m[0x101+regs[4]:0x200])==protected_stack,'ISR wrote above its owned stack extent'
        counts[kind]+=1
    def invoke(m,frame,facing,changed,flags=97):
        m._render_frame=frame
        m.raw_page(2,2);N.put(m,CurrentBankC=2,GuestOamRotationActive=1,RgOamRotation=0,CurrentOAMOffset=0)
        m.ram[2][0x617]=frame;m.ram[2][0x615]=facing
        m.ram[3][0x1cfe:0x1d02]=bytes((48,0,176,1))
        m[W.address(m.bundle,'SafecallA_SMC')+1]=83
        at=W.address(m.bundle,'FarcallJmpTarget_SMC');m[at+1:at+3]=(0xbbc1).to_bytes(2,'little')
        events=[];cuts=set();stream=[]
        class CPU(native):
            def step(self):
                m._render_pc=(self.pc,m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else -1)
                if self.pc==0xa275 and m.rawtags[1]==190:events.append((self.y,self.a,self.x))
                if self.pc==0xbc40 and m.rawtags[1]==3:stream.append((m[0xbd04],self.y))
                if interrupts and changed and flags==97 and frame in(0,16,142,156,230,231)and self.pc in(0xbc40,0xbc41,0xbc42,0xd779,0xd77b):
                    key=(self.pc,self.sp)
                    if key not in cuts and not self.p&4:
                        cuts.add(key);interrupt(self,'IRQ')
                        if N.get(m,'NmiDisable')==255:interrupt(self,'busyNMI')
                return super().step()
        c=CPU(memory=m,pc=W.address(m.bundle,'FarCallCommon'))
        c.a,c.x,c.y,c.p,c.sp=3,71,109,flags,224;c.stPushWord(0x5aff)
        for _ in range(100000):
            if c.pc==0x5b00:break
            assert m[c.pc],('Renderer BRK',frame,facing,hex(c.pc))
            c.step()
        else:raise AssertionError('Renderer return bound')
        regs=(c.a,c.x,c.y,c.p&239,c.sp)
        assert(c.a,c.x,c.y,c.sp)==(83,71,109,224),(frame,facing,regs)
        if flags==97:assert c.p&239==97
        count=m.ram[2][0x200];packet=bytes(m.ram[2][0x200:0x201+count])
        geometry_fields=bytes(m.ram[2][0x4bc:0x4c4])+bytes(m.ram[2][0x6f1:0x6f3])+bytes(m.ram[2][0x70f:0x710])
        # The renderer selects software physical windows. The actual native
        # publisher commits those choices to MMC5 before pattern comparison.
        N.invoke(m,'X5PublishChr',a=0,x=0,y=0)
        return events,stream,packet,geometry_fields,c.processorCycles,regs
    state_equivalence_cases=0
    def private_equivalence(frame):
        nonlocal state_equivalence_cases
        count=pair[0].ram[2][0x200]
        for bank in(2,3):
            allowed=set()
            for row in json.loads(GRANT.read_bytes())['envelopes']:
                if(3 if row['stream']==0 else 2)==bank:
                    allowed.update(range(row['live_PC']&8191,(row['live_PC']&8191)+row['bytes']))
            if bank==2:
                allowed.add(0xd7b1&8191)
                allowed.add(0xd95f&8191)  # Cached tag high: low6 are relocated pointer bits.
                # Smaller poses leave old, unconsumed tiles in the same
                # existing53-byte synchronous renderer packet.
                allowed.update(0x201+offset for offset in range(0,52,4))
            else:allowed.update((0xbcf5&8191,0xbcf6&8191))
            diffs={i for i,(a,b)in enumerate(zip(pair[0].ram[bank],pair[1].ram[bank]))if a!=b}
            assert diffs<=allowed,(frame,bank,sorted(diffs-allowed)[:12])
        assert pair[0].ram[2][0xd95f&8191]&192==pair[1].ram[2][0xd95f&8191]&192
        assert all(a==b or b==a+65 for a,b in zip(pair[0].ram[2][0x201:0x235:4],pair[1].ram[2][0x201:0x235:4]))
        for which,m in enumerate(pair):
            tag=int.from_bytes((original[1]if which==0 else parts[1])[2*frame:2*frame+2],'little')
            pointer=int.from_bytes(m.ram[3][0xbcf5&8191:(0xbcf5&8191)+2],'little')
            assert pointer==0xc800+(tag&0x3fff)
        state_equivalence_cases+=1
    cases=pieces=tile255=0;max_extra=-100000;min_extra=100000;cycle_deltas=Counter()
    for frame in range(239):
        decoded=Plan.geometry(original[1],frame)
        if decoded is None:continue
        for facing in(0,1):
            left=invoke(pair[0],frame,facing,False);right=invoke(pair[1],frame,facing,True)
            assert[(y+5,a,x)for y,a,x in left[0]]==right[0]
            assert left[1]==right[1]and all(y==2+i for i,y in right[1])
            a,b=left[2],right[2];assert len(a)==len(b)
            assert all(new==(old+65 if k%4==1 else old)for k,(old,new)in enumerate(zip(a,b)))
            assert left[3]==right[3]
            assert left[5]==right[5]
            private_equivalence(frame)
            for old,new in zip(a[1::4],b[1::4]):
                ow,nw=Plan.Census.Old.tile_window(old),Plan.Census.Old.tile_window(new)
                assert pair[0].chr_latches[ow]==pair[1].chr_latches[nw]and old&62==new&62,(frame,facing,old,new,ow,nw,pair[0].chr_latches,pair[1].chr_latches)
                tile255+=new==255;pieces+=1
            extra=right[4]-left[4];max_extra=max(max_extra,extra);min_extra=min(min_extra,extra);cycle_deltas[extra]+=1
            cases+=1
    assert cases==408 and pieces==2578
    representatives={}
    for frame in range(239):
        tag=int.from_bytes(original[1][2*frame:2*frame+2],'little')
        if tag!=65535:representatives.setdefault(tag&0xc000,frame)
    flag_cases=0
    for frame in representatives.values():
        for flags in range(256):
            if flags&48!=32:continue  # U1/B0; every hardware flag combination.
            for facing in(0,1):
                left=invoke(pair[0],frame,facing,False,flags);right=invoke(pair[1],frame,facing,True,flags)
                assert left[5]==right[5]and left[3]==right[3]
                assert all(b==(a+65 if k%4==1 else a)for k,(a,b)in enumerate(zip(left[2],right[2])))
                flag_cases+=1
                private_equivalence(frame)
    assert not data_writes
    # Current poses stop short of tile255. This explicit native-kernel unit
    # uses the renderer's existing five-byte one-part C200 packet, not actor
    # state or a gameplay outcome, to close the 8x16 boundary value.
    boundary=pair[1];boundary.raw_page(2,2);N.put(boundary,CurrentBankC=2,CurrentOAMOffset=0)
    boundary.ram[2][0x200:0x205]=bytes((4,255,0,0,0))
    N.put(boundary,R0=0,R1=0xc2,R3=0,R4=48,R5=0,R6=176,R7=1)
    N.invoke(boundary,'MetaspriteRenderLoop',a=0,x=0,y=0)
    assert N.get(boundary,'CurrentOAMOffset')==4 and boundary[0x201]==255
    # Start from genuine original private0..2 publication. The compiled public
    # menu/portrait retirement must clear it, and the leased renderer must
    # thereafter preserve every native world window0..4.
    lifecycle=N.fork(seed);invoke(lifecycle,142,0,False)
    bank=W.address(lifecycle.bundle,'CurrentCHRBank');mode=W.address(lifecycle.bundle,'X5ChrMode')
    assert lifecycle[mode]&128
    N.invoke(lifecycle,'FmNativePrepare',a=0,x=0,y=0)
    assert list(lifecycle[mode:mode+12])==[0]*12
    init=W.location(lifecycle.bundle,'CHRBankInitValues');expected=list(raw[init:init+8])
    assert list(lifecycle[bank:bank+8])==expected
    N.invoke(lifecycle,'X5PublishChr',a=0,x=0,y=0)
    native_banks=lifecycle.chr_latches[:5];assert native_banks[1:3]==[16,17]
    fixed=mounted(lifecycle,parts);before_modes=bytes(fixed[mode:mode+5]);before_banks=bytes(fixed[bank:bank+5])
    invoke(fixed,142,0,True)
    assert fixed.chr_latches[:5]==native_banks and bytes(fixed[mode:mode+5])==before_modes and bytes(fixed[bank:bank+5])==before_banks
    # Source-model warm Main contexts are actual cold descendants. No actor,
    # health, terrain, position, weapon or busy-NMI state is supplied here.
    warm=mounted(seed,parts);seen=set()
    class WarmCPU(native):
        def step(self):
            if interrupts and self.memory is warm and self.pc in(0xbc40,0xbc41,0xbc42,0xd779,0xd77b):
                tag=warm.rawtags[(self.pc-0x8000)//8192]
                key=(self.pc,tag,self.sp)
                if tag in(2,3)and key not in seen and not self.p&4:
                    seen.add(key);interrupt(self,'MainIRQ')
                    if N.get(warm,'NmiDisable')==255:interrupt(self,'busyNMI')
            return super().step()
    with patch.object(N,'NesMPU',WarmCPU):
        for _ in range(8):warm.controller_pad=0;Frames.frame(warm,whole_pass=True)
    head=Packet.extract(raw)[0];packed=list(map(Packet.encode,parts));sizes=list(map(len,packed))
    assert sizes[0]<=6528 and 0xe100-sizes[1]>=0xc900
    assert len(head)+sum(sizes)<=len(Packet.PAGES)*1024
    q=dict(passed=True,input_F11_SHA256=sha256(raw).hexdigest(),lease_SHA256=GRANT_SHA,opening=opening,
        actual_render_cases=cases,actual_parts=pieces,actual_tile255_parts=tile255,
        all64_valid_hardware_flag_combinations=True,additional_ABI_flag_cases=flag_cases,format_representatives=representatives,
        full_private_RAM_equivalence_cases=state_equivalence_cases,
        only_private_differences='Three leased spans, renderer TileOut, synchronous packet tiles, bounded Byte SMC pointer, cached tag low6 pointer bits (format N/V exact)',
        every_actual_Byte_read_within_specific_pose_packet=True,ISR_caller_stack_above_entry_SP_exact=True,
        explicit_native_packet_tile255_case=True,former_private0_retired_by_compiled_FmNativePrepare=True,
        native0through4_after_retirement_and_remap=native_banks,
        pose_data_actual_reader_PC_map_counts=[[pc,tag,count]for(pc,tag),count in sorted(data_readers.items())],
        pose_data_writes=0,actual_warm_Main_updates=8,
        all_AXYP_SP_exact=True,all_non_tile_packet_bytes_and_geometry_fields_exact=True,
        all_pattern_pages_and_pair_offsets_exact=True,max_added_CPU_cycles=max_extra,min_added_CPU_cycles=min_extra,
        measured_render_cycle_delta_histogram=dict(cycle_deltas),
        IRQ_and_busyNMI_cuts=dict(counts),minimum_ISR_SP=minimum if counts else None,
        compressed_stream_bytes=sizes,carrier_spare=len(Packet.PAGES)*1024-len(head)-sum(sizes),
        pure_math_receipt=math,scope='Leased post-cold renderer arrays, explicit finite pose/face fixtures; no ROM or gameplay qualification',
        status_B_normalization='6502 PHP/PLP B bit excluded; hardware flags exact',
        pending=['static_direct_data_consumer_closure','all_lifecycle_paths'],ROM_composed=False,Mesen=False,outputs=0)
    q['receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return q


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--current-score-571',action='store_true');parser.add_argument('--interrupts',action='store_true');args=parser.parse_args()
    raw=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
    if args.current_score_571:
        import current_prince_body_research_571_1114 as Current
        current=Current.normalize(raw,kind='score-571');raw=current.referenceF11
    attempts=[]
    def deny(*a,**kw):attempts.append('output or launch');raise AssertionError('Source-only renderer attempted output/launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch.object(subprocess,'Popen',deny):
        q=run(raw,interrupts=args.interrupts)
    assert not attempts
    q['write_or_launch_attempts']=attempts
    if args.current_score_571:q['public_input']=current.metadata()
    print(json.dumps(q,separators=(',',':')),flush=True)
