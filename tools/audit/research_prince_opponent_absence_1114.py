"""Read-only original marker and exact importer research; no game overlay."""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import argparse,json,sys
from functools import lru_cache
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import prince_original_cpu_1101_v1 as Original
from py65.disassembler import Disassembler
from py65.devices.mpu6502 import MPU

START,END=0xddbe,0xde99


@lru_cache(maxsize=1)
def importer_plan(raw):
    """Assemble only detached arrays; no placement or ordinary-game mount."""
    import re
    import current_prince_body_research_571_1114 as Current
    import prince_cold_packet_1111 as Packet
    import build_prince_worldmaterial_research_1114 as Assembly
    if sha256(raw).hexdigest()=='ae669c7ec7536f1c912b3000597be7b3416c20f312638b2589f52fab55f0bc01':
        import current_prince_body_research_ae66_1114 as Current
        current=Current.normalize(raw,kind='bt-service-ae66')
    else:current=Current.normalize(raw,kind='score-571')
    reference=current.referenceF11
    chunks=Packet.extract(reference)[1];old=chunks[1][START-0xc800:END-0xc800]
    source=R/'build/prince-actor-1101-v1/native-proxy-v149.s';text=source.read_text()
    symbols={name:int(number,16)for name,number in re.findall(r'(?m)^(\w+)=\$([\da-fA-F]+)$',text)}
    labels=json.loads((source.parent/'native-labels-v153.json').read_text())
    symbols.update({k:labels[k]for k in('PpProxyBestSlot','PpProxyBestDistance')})
    symbols['GuardTemplate']=symbols['PpProxyBestDistance']+1
    original='PpNativeProxyIn:'+text.split('PpNativeProxyIn:',1)[1].split('PpNativeProxyOut:',1)[0]
    original=original.replace('jne Return','bne Return').replace(' lda Enemy_BoundBoxCtrl,x',' jsr $d466')
    original=original.replace('Return:rts','Return:\n rts')
    rebuilt,oldlabels,_=Assembly.assemble(original,symbols,origin=START,check_entries=False)
    assert rebuilt==old and len(old)==219,'Current box3/9 importer is not the retained source'
    after=original
    def replace(a,b):
        nonlocal after
        assert after.count(a)==1,a;after=after.replace(a,b,1)
    replace(' cmp #2\n bne Return\n jsr PpHostImportX',
            ' cmp #2\n beq ActivePhase\n rts\nActivePhase:\n jsr PpHostImportX')
    replace(' jsr PpSourceNear\n bcs Next\n lda $c017',' jsr PpSourceNear\n bcs Next')
    replace(' dey\n bpl Birth',' dey\n bne Birth')
    replace(' beq Import\n ldy #13',' beq Import\n pha\n ldy #13')
    replace(' bne Birth\n txa\n ora #$80\n sta $c61c',' bne Birth\n pla\n sta $c61c')
    replace(' lda #0\n sta $c711\n sta $c6de',' sty $c711\n sty $c6de')
    replace('Absent:\n lda #0\n sta $c6e0\n sta $c61c',
            'Absent:\n lda $c6e0\n beq ClearAbsent\n sta $c6de\nClearAbsent:\n lda #0\n sta $c6e0\n sta $c61c')
    proposed,newlabels,_=Assembly.assemble(after,symbols,origin=START,check_entries=False)
    assert len(proposed)==END-START and newlabels['PpNativeProxyIn']==START
    assert newlabels['ImportX']==oldlabels['ImportX']and newlabels['Return']==oldlabels['Return']
    assert proposed.count(bytes.fromhex('2066d4'))==1
    return dict(old=old,new=proposed,oldlabels=oldlabels,newlabels=newlabels,symbols=symbols,
        chunks=chunks,source=source,assembly=after,reference=reference,current=current)


def detached_importer(raw):
    plan=importer_plan(raw);rows=[]
    old,new=plan['old'],plan['new'];lo,hi=plan['oldlabels']['Absent'],plan['oldlabels']['ImportX']
    # SourceNear's C0 return leaves A equal to abs distance in C017. Exact
    # source bytes and its real early-return domains are checked separately.
    near=plan['symbols']['PpSourceNear'];near_blob=plan['chunks'][0][near-0xa000:near-0xa000+80]
    memory=[0]*65536;memory[near:near+len(near_blob)]=near_blob
    decoder=Disassembler(MPU(memory=memory));at=near;near_code=[]
    while at<near+len(near_blob):
        size,text=decoder.instruction_at(at);near_code.append([at,text]);at+=size
        if text=='RTS':break
    return dict(scope='Detached source-only assembled proposal; no candidate, allocation or gameplay overlay',
        current_input_SHA256=sha256(raw).hexdigest(),reference_F11_SHA256=sha256(plan['reference']).hexdigest(),
        live_envelope=[START,END],bytes=len(old),old_SHA256=sha256(old).hexdigest(),
        new_SHA256=sha256(new).hexdigest(),old_hex=old.hex(),new_hex=new.hex(),
        labels={key:[plan['oldlabels'][key],plan['newlabels'][key]]for key in('PpNativeProxyIn','Scan','Birth','Import','Absent','Return','ImportX')},
        funding=[dict(bytes=3,source='Remove redundant A reload after SourceNear C0 return'),
            dict(bytes=2,source='Copy template bytes13..1, use final Y0 for two zero stores; byte0 receives actual UID'),
            dict(bytes=2,source='Replace distant conditional return jump with immediate RTS'),
            dict(bytes=1,source='Preserve already-computed actual UID across Birth using PHA/PLA')],
        transition_only=True,no_target_ever_seen_preserves_manual_sheath_request=True,
        original_sheath_marker=1,SourceNear_declared_current_code=near_code,
        proposed_source=plan['assembly'],ROM_composed=False,mounted_arrays=0,Mesen=False,outputs=0)


def primitives(plan):
    """Declared flat CPU inputs, never a gameplay fixture or NesBus overlay."""
    from verify_native_relocation import NesMPU
    base=[0]*65536
    for origin,chunk in zip((0xa000,0xc800,0xc0b0),plan['chunks']):base[origin:origin+len(chunk)]=chunk
    # HostImportX is an unchanged external service. The fixture supplies its
    # source-coordinate output and uses a declared RTS oracle at its entry.
    base[plan['symbols']['PpHostImportX']]=0x60
    counts=Counter();maxdelta=-10000;mindelta=10000
    for phase in range(4):
      for flags in(0x20,0x21,0x24,0x60,0x61,0xa0,0xe1,0xe5):
       for scenario in range(24):
        seed=base[:];seed[0xc0a6]=phase;seed[0xc60f:0xc611]=(0xff,1)
        seed[0xc089:0xc08b]=(37,0);seed[0xc6de]=(0,1,85)[scenario%3]
        seed[0xc6e0]=(scenario//6)&1
        seed[0xc6ee]=2;seed[0xc61c]=0x80 if scenario%2 else 0
        for slot in range(6):
            x=(0x1ff+(-104,-103,-1,0,103,104)[slot]+(scenario//6-2)*256)&65535
            seed[0x10+slot]=1;seed[0x17+slot]=slot%7;seed[0x1f+slot]=0
            seed[0x646+slot]=9 if slot&1 else 3;seed[0xa5+slot]=1
            seed[0x76+slot]=x&255;seed[0x5d+slot]=x>>8
            seed[0xbe+slot]=128;seed[0x53f+slot]=1 if slot&1 else 2
        if scenario%6==1:
            for slot in range(6):seed[0x10+slot]=0
        if scenario%6==2:
            for slot in range(6):seed[0x1f+slot]=32
        if scenario%6==3:
            for slot in range(6):seed[0x646+slot]=4
        if scenario%6==4:
            for slot in range(6):seed[0xa5+slot]=2
        if scenario%6==5:
            for slot in range(6):seed[0x17+slot]=7
        outcomes=[]
        for which in('old','new'):
            mem=seed[:];mem[START:END]=plan[which]
            c=NesMPU(memory=mem,pc=START);c.a,c.x,c.y,c.p,c.sp=93,71,109,flags,224;c.stPushWord(0x5aff)
            birth_zero=False;birth_uid=False
            for n in range(3000):
                if c.pc==0x5b00:break
                assert mem[c.pc],('Flat importer unexpected BRK',which,hex(c.pc))
                if c.pc==plan[which+'labels']['Import']:
                    birth_zero=mem[0xc711]==0 and mem[0xc6de]==0
                    birth_uid=mem[0xc61c]==(128|c.x)
                c.step()
            else:raise AssertionError('Flat importer bounded return')
            outcomes.append((mem,(c.a,c.x,c.y,c.p&239,c.sp),c.processorCycles,birth_zero,birth_uid))
        left,right=outcomes;assert left[1]==right[1],('Caller AXYP/SP changed',phase,flags,scenario,left[1],right[1])
        allowed=set(range(START,END))|set(range(0x100,0x101+224))
        absent=phase==2 and right[0][0xc61c]==0
        if absent and seed[0xc6e0]:
            assert seed[0xc6e0]==1
            allowed.add(0xc6de);assert right[0][0xc6de]==1 and right[0][0xc6e0]==0
        differences={at for at,(a,b)in enumerate(zip(left[0],right[0]))if a!=b}
        assert differences<=allowed,('Unexpected primitive state change',phase,scenario,sorted(differences-allowed)[:12])
        assert left[3:]==right[3:]
        if right[0][0xc61c]&128 and phase==2:
            assert right[4]and right[3],'Template UID and zero initialization must precede Import'
        counts['absent'if absent else'other']+=1
        delta=right[2]-left[2];maxdelta=max(maxdelta,delta);mindelta=min(mindelta,delta)
    # SourceNear's full finite low-distance/page domain, with original code,
    # proves the removed load is redundant on every accepted C0 result.
    near=plan['symbols']['PpSourceNear'];near_cases=0
    for player in(0,255,256,511,65535):
      for delta in range(-260,261):
        mem=base[:];enemy=(player+delta)&65535
        mem[0xc60f:0xc611]=(player&255,player>>8);mem[0xc61d:0xc61f]=(enemy&255,enemy>>8)
        c=NesMPU(memory=mem,pc=near);c.sp,c.p=224,0x21;c.stPushWord(0x5aff)
        for _ in range(100):
            if c.pc==0x5b00:break
            assert mem[c.pc];c.step()
        else:raise AssertionError('SourceNear bounded return')
        if not c.p&1:assert c.a==mem[0xc017]and c.a<104
        near_cases+=1
    return dict(primitive_cases=sum(counts.values()),cases_by_kind=dict(counts),SourceNear_cases=near_cases,
        all_caller_AXYP_SP_exact=True,all_RAM_exact_except_intended_absent_marker_and_owned_stack_code=True,
        template_UID_and_zero_initialization_exact=True,minimum_cycle_delta=mindelta,maximum_cycle_delta=maxdelta,
        service_oracle='Unchanged HostImportX supplies source coordinates; SourceNear/box3or9/template execute real current code',
        scope='Flat explicit primitive vectors, not ordinary gameplay qualification')


def ingress(plan):
    import audit_prince_pose_consumer_roots_1114 as Census
    captured={};previous=sys.getprofile()
    def profile(frame,event,arg):
        if frame.f_code is Census.run.__code__ and event=='return':
            captured.update(visited=frame.f_locals['visited'],mem=frame.f_locals['mem'])
    sys.setprofile(profile)
    try:q=Census.run(plan['current'].reference571 if hasattr(plan['current'],'reference571')else plan['current'].original)
    finally:sys.setprofile(previous)
    memory=captured['mem'];cpu=MPU(memory=memory);calls=[];internal=[];operands=[];active_writers=[]
    for pc in captured['visited']:
        mnemonic,mode=cpu.disassemble[memory[pc]]
        if mode=='rel':
            delta=memory[pc+1];target=pc+2+delta-(256 if delta&128 else 0)
        elif mode in('abs','abx','aby','ind'):target=memory[pc+1]+256*memory[pc+2]
        else:continue
        if target==0xc6e0 and mnemonic in('STA','STX','STY','INC','DEC'):
            active_writers.append([pc,mnemonic,mode])
        if not START<=target<END:continue
        row=[pc,mnemonic,mode,target]
        if START<=pc<END:internal.append(row)
        elif mnemonic in('JSR','JMP')or mode=='rel':
            calls.append(row);assert target==START,('External entry into moved internal importer label',row)
        else:operands.append(row)
    assert calls and not operands,('Unexpected data reference to importer',operands)
    publications=[row for row in q['current_private_farcall_publications']if START<=row['target']<END]
    assert all(row['target']==START for row in publications)
    # Fixed data table and following export are outside the changed extent.
    assert plan['symbols']['GuardTemplate']==0xded9 and END==0xde99
    return dict(current_instruction_roots=q['current_direct_CFG_instruction_starts'],
        current_consumer_census_receipt=q['receipt_SHA256'],external_direct_control_entries=calls,
        private_farcall_publications=publications,external_data_operands=operands,
        original_script_command_and_indirect_domains='Reuse exact unchanged frozen decoded consumer closure',
        only_external_entry=START,public_next_function=END,
        unchanged_internal_Return=plan['newlabels']['Return'],unchanged_internal_ImportX=plan['newlabels']['ImportX'],
        current_direct_guard_active_writers=sorted(active_writers),
        template_UID_liveness='Template byte0 is overwritten by actual128|slot before Import; final Y is reloaded from Enemy_MovingDir before return',
        decoded_consumer_source_SHA256=sha256(Path(Census.__file__).read_bytes()).hexdigest())


def transition_primitives(plan):
    from verify_native_relocation import NesMPU
    named=json.loads((plan['source'].parent/'native-labels-v153.json').read_text())
    base=[0]*65536
    for origin,chunk in zip((0xa000,0xc800,0xc0b0),plan['chunks']):base[origin:origin+len(chunk)]=chunk
    base[plan['symbols']['PpHostImportX']]=0x60
    def call(mem,pc):
        c=NesMPU(memory=mem,pc=pc);c.a,c.x,c.y,c.p,c.sp=83,71,0,0x61,224;c.stPushWord(0x5aff)
        for _ in range(5000):
            if c.pc==0x5b00:return
            assert mem[c.pc],('Primitive control BRK',hex(c.pc));c.step()
        raise AssertionError('Primitive original combat control bounded return')
    rows=[]
    for player_facing in(0,255):
      for guard_facing in(0,255):
       for prior_active in(0,1):
        for request in(0,1,85):
            mem=base[:];mem[START:END]=plan['new'];mem[0xc0a6]=2
            mem[0xc60e]=128;mem[0xc615]=player_facing;mem[0xc623]=guard_facing
            mem[0xc617]=171;mem[0xc616]=0;mem[0xc6ee]=2;mem[0xc6e0]=prior_active;mem[0xc6de]=request
            mem[0xc60f:0xc611]=(0,2);mem[0xc61c]=128 if prior_active else 0
            for slot in range(6):mem[0x10+slot]=0
            call(mem,START)
            expected=1 if prior_active else request
            assert mem[0xc6de]==expected and mem[0xc6e0]==0 and mem[0xc61c]==0
            call(mem,named['PpCombatControls'])
            sheath=expected!=0 and player_facing!=guard_facing
            assert mem[0xc6ee]==(1 if sheath else 2)
            rows.append(dict(prior_active=prior_active,manual_request=request,
                player_facing=player_facing,guard_facing=guard_facing,
                request_after_absence=expected,sword_after_actual_original_combat=mem[0xc6ee]))
            # Real importer re-admission semantics, explicit component actor.
            mem[0x10]=1;mem[0x17]=0;mem[0x1f]=0;mem[0x646]=9;mem[0xa5]=1
            mem[0x76]=24;mem[0x5d]=2;mem[0xbe]=176;mem[0x53f]=2
            call(mem,START)
            assert mem[0xc61c]==128 and mem[0xc6de]==0 and mem[0xc6e0]==1
    return dict(component_cases=len(rows),actual_original_combat_cases=rows,
        no_prior_opponent_preserves_manual_request=True,re_admission_resets_marker_and_real_UID=True,
        equal_facing_original_early_return_retained=True,
        scope='Explicit flat source primitive states; ordinary free-draw/attack and loss replay remain separate')


def original_sheath_primitives():
    """Use actual original routine from an original reset descendant."""
    import copy
    seed=Original.boot();results=[]
    for marker in(0,1):
        c=copy.deepcopy(seed);m=c.memory;m.switch(5)
        # Explicit primitive vector only; never counted as natural gameplay.
        m[0x617]=171;m[0x6ee]=2;m[0x6de]=marker
        out=Original.call(c,0x8ae9,a=83,x=71,y=0,p=0x61)
        results.append(dict(marker=marker,final_sword=m[0x6ee],action=m[0x616],pose=m[0x617],registers=list(out)))
    assert results[0]['final_sword']==2 and results[1]['final_sword']==1
    return dict(explicit_primitive_not_gameplay=True,cases=results,
        actual_original_marker_writer=[5,0x85ed,'a9018dde06'],actual_original_consumer=[5,0x8ae9])


def donor_inspect(*,natural=False):
    raw=Original.donor();cpu=Original.machine();cpu.memory.switch(5)
    decoder=Disassembler(cpu);rows=[]
    for lo,hi in((0x85c9,0x861c),(0x8ae9,0x8b04)):
        at=lo
        while at<hi:
            size,text=decoder.instruction_at(at)
            rows.append([5,at,bytes(cpu.memory[at:at+size]).hex(),text]);at+=size
    operands=[]
    for bank in range(8):
        data=raw[16+16384*bank:16+16384*(bank+1)]
        for offset in range(len(data)-2):
            if data[offset+1:offset+3]==bytes.fromhex('de06'):
                operands.append([bank,0x8000+offset if bank!=7 else 0xc000+offset,data[offset:offset+3].hex()])
    q=dict(original_SHA256=sha256(raw).hexdigest(),declared_original_code=rows,
        opcode_like_marker_operands=operands,gameplay_qualified=False,outputs=0)
    if natural:
        writes=[];frame=-1;old=Original.Bus.__setitem__;c=None
        def put(m,a,v):
            if c is not None and isinstance(a,int)and a==0x6de:
                writes.append(dict(frame=frame,bank=7 if c.pc>=0xc000 else m.bank,
                    PC_after_operand=c.pc,value=v&255,pose=m[0x617],sword=m[0x6ee],guard=m[0x6e0]))
            return old(m,a,v)
        Original.Bus.__setitem__=put
        try:
            c=Original.boot()
            for frame in range(900):
                Original.frame(c,16 if 120<=frame<123 or 300<=frame<303 or 600<=frame<603 else 0)
        finally:Original.Bus.__setitem__=old
        q.update(natural_reset_and_Start_frames=900,marker_writes=writes[:64],marker_write_count=len(writes),
            terminal=dict(marker=c.memory[0x6de],sword=c.memory[0x6ee],guard=c.memory[0x6e0],pose=c.memory[0x617],hp=c.memory[0x6cf]),
            natural_scope='Original reset/Start peripheral CPU model; no physical cadence qualification')
    return q


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--natural-original',action='store_true');p.add_argument('--importer',action='store_true');p.add_argument('--primitives',action='store_true');p.add_argument('--ingress',action='store_true');args=p.parse_args()
    q=detached_importer(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())if args.importer else donor_inspect(natural=args.natural_original)
    if args.primitives:
        assert args.importer
        q['primitive_proof']=primitives(importer_plan(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()))
        q['original_sheath_primitive']=original_sheath_primitives()
        q['transition_primitive']=transition_primitives(importer_plan(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()))
    if args.ingress:
        assert args.importer
        q['ingress_proof']=ingress(importer_plan(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()))
    q['receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    print(json.dumps(q,separators=(',',':')),flush=True)
