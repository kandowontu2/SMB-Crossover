"""Detached 224B/175B resolver fit and full public transport units; no mount."""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import argparse,json

import current_battletoads_resolver_research_1115 as Input
import compose_battletoads_idle_funded_1115 as C
import check_battletoads_idle_funded_1115 as Base
from measure_battletoads_passthrough_fit_1114 import Code,router as OldRouter

W,N=Base.W,Base.N
ROUTER_AT=16+87*8192+0x1020
WF_AT=16+96*8192+0x1799
WF_END=16+96*8192+0x1848


def router(base=0xb020,*,new=False,helper=None):
    if helper is None:helper=0xb799 if new else 0xb79d
    a=Code(base)
    for _ in range(36):a.absolute(0x4c,'Router')
    a.mark('Unavailable');a.emit('1860');a.mark('Router');a.emit('08488a489848ad026038e91bc907')
    a.branch(0xb0,'No')
    if new:a.emit('4a');a.branch(0xb0,'No');a.emit('a8')
    else:a.emit('2901');a.branch(0xd0,'No')
    a.emit('ad6c0138e920aa')
    if new:a.emit('8a8d6a01c003')
    else:a.emit('ad0260c921')
    a.branch(0xd0,'Common');a.emit('8a29b3c913');a.branch(0xf0,'No')
    a.emit('e033');a.branch(0xf0,'Portrait');a.emit('e04e')
    if not new:
        a.branch(0xd0,'Common');a.emit('a991');a.branch(0xd0,'Cold')
        a.mark('Portrait');a.emit('a911');a.mark('Cold');a.emit('8d6c01a9b08d6d01a9c8');a.branch(0xd0,'Target')
    else:
        a.branch(0xf0,'Colors');a.emit('a2ad')
    a.mark('Common')
    if not new:a.emit('8a8d6a01')
    a.emit('a9'+(helper&255).to_bytes(1,'little').hex()+'8d6c01a9'+(helper>>8).to_bytes(1,'little').hex()+'8d6d01a9e0205a01')
    a.branch(0x90,'No');a.mark('Target');a.emit('8d620168a868aa688d6a01284c5d01')
    a.mark('No');a.emit('68a868aa688d6a01281860')
    if new:
        a.mark('Portrait');a.emit('a911');a.branch(0xd0,'Cold')
        a.mark('Colors');a.emit('a991');a.mark('Cold');a.emit('8d6c01a9b08d6d01a9c8');a.branch(0xd0,'Target')
    out=a.done();assert len(out)==(223 if new else 224),(len(out),a.labels)
    if new:out+=b'\xea'
    return out,a.labels


def helper(raw,base=0xb799):
    old=raw[WF_AT:WF_END];assert len(old)==175
    assert old[:4]==bytes.fromhex('18603860'),'Exact old NoOp C0 and Visible C1'
    table=raw[16+96*8192+0x17dc:WF_END];assert len(table)==108
    rows=[]
    for slot in range(36):
        lo,hi,bank=table[slot*3:slot*3+3];target=lo+256*hi
        if(bank,target)!=(224,0xb799):rows.append((3*slot,lo,hi,bank))
    assert len(rows)==21
    # Offset99 is last visited. Hot movement/draw entries are visited first.
    rows.sort(key=lambda q:(q[0]in(0,6),q[0]))
    a=Code(base);a.mark('Entry');a.emit('c003');a.branch(0xf0,'Fast');a.emit('88');a.branch(0xf0,'Own')
    a.mark('Foreign');a.emit('a92b8d6c01a9b28d6d01a9c34c5a01')
    a.mark('Own');a.emit('ade85f2907c906');a.branch(0xb0,'Bad');a.emit('8ac964');a.branch(0xb0,'Bad')
    a.emit('a214');a.mark('Find');a.absolute(0xdd,'Offsets');a.branch(0xf0,'Found');a.emit('ca');a.branch(0x10,'Find')
    a.mark('Bad');a.emit('1860');a.mark('Found');a.absolute(0xbd,'Lo');a.emit('8d6c01');a.absolute(0xbd,'Hi');a.emit('8d6d01');a.absolute(0xbd,'Bank')
    a.mark('Visible');a.emit('3860')
    a.mark('Fast');a.emit('a9c08d6c018e6d01a9dd205a01');a.branch(0x90,'Foreign');a.emit('8d6c01a9a08d6d01a90360')
    for i,label in enumerate(('Offsets','Lo','Hi','Bank')):
        a.mark(label)
        for offset,lo,hi,bank in rows:
            value=(offset,lo,hi,bank)[i]
            if bank==224 and lo+256*hi==0xb79b and i in(1,2):value=(a.labels['Visible']>>(8*(i-1)))&255
            a.code.append(value)
    out=a.done();assert len(out)==175,(len(out),a.labels)
    assert a.labels['Own']-base==22 and a.labels['Fast']-a.labels['Own']==43
    return out,a.labels,rows


def shapes(parent,image):
    assert router()[0]==OldRouter()[0]==image[ROUTER_AT:ROUTER_AT+224]
    h,hl,rows=helper(image);r,rl=router(new=True)
    data=[]
    for at,new in((ROUTER_AT,r),(WF_AT,h)):
        old=image[at:at+len(new)];data.append(dict(file=[at,at+len(new)],old_hex=old.hex(),new_hex=new.hex(),
            old_SHA256=sha256(old).hexdigest(),new_SHA256=sha256(new).hexdigest(),changed=sum(a!=b for a,b in zip(old,new,strict=True))))
    return dict(reference_SHA256=C.CANDIDATE,detached_envelopes=data,owned_bytes=399,Router_labels=rl,helper_labels=hl,
        fit=dict(Router=224,Router_code=223,declared_owned_NOP=1,dispatcher=7,foreign_thunk=15,own29=43,raw33_fast=26,sparse_table=84,helper_total=175),
        internal_contracts=['Canonical Router gate passes Y=(Selected-27)/2 in0..3 only for owners27/29/31/33',
            'Canonical service offset is3*slot for public36 rows; SafeA receives it before X reuse',
            'Only raw33 query loads register X with AD, the high byte of immutable BtCheck at ADC0',
            'Owner29 keeps X=service offset; helper result X/Y are dead before original Router restoration',
            'Owner29 missing NoOp descriptors return query C0; complete public NoOp equivalence must be tested',
            'Raw33 check failure tail-delegates to unchanged Bw resolver, retaining cold/retired gates'],
        full_BtCheck_code_unchanged=True,query_fallback_full_checks_may_increase_only_on_rejection=True,
        no_mounted_overlay=True,no_new_whole_image=True,foreign_cycle_tradeoff_not_yet_measured=True)


def detached_seed(seed,new):
    """Independent arrays with actual low-byte/page crossings, no PRG replacement."""
    unit_router,_=router(0x4020,new=new,helper=0x5099 if new else 0xb79d)
    unit_helper,labels,_=helper(seed.bundle['raw'],0x5099)
    virtual={0x4020+i:v for i,v in enumerate(unit_router)}
    if new:virtual.update({0x5099+i:v for i,v in enumerate(unit_helper)})
    class Detached(type(seed)):
        def __getitem__(self,at):
            if isinstance(at,int)and at in virtual:return virtual[at]
            return super().__getitem__(at)
    m=Detached(seed.bundle)
    list.__setitem__(m,slice(None),list.__getitem__(seed,slice(None)))
    for key,value in vars(seed).items():setattr(m,key,value if key=='bundle'else deepcopy(value))
    return m,labels


def public_call(m,slot,a,x,y,p):
    target=0x4020+3*slot;m[0x16a]=a;m[0x16c]=target&255;m[0x16d]=target>>8
    c=N.NesMPU(memory=m,pc=0x15a);c.a=215;c.x=x;c.y=y;c.p=p;c.sp=236;c.stPushWord(0x5aff)
    low=c.sp;checks=0;trace=[]
    for step in range(20000):
        tag=m.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
        if(c.pc,c.sp)==(0x5b00,236):break
        if(c.pc,c.sp)==(0x15d,231):
            word=m[0x16c]+256*m[0x16d];bank=m[0x162]
            # Complete the ORIGINAL public NoOp/Visible leaf and return transport.
            # Stop all other private services before gameplay/constructor execution.
            visible=getattr(m,'flat_visible',-1)
            if not(bank==224 and word in(0xb799,0xb79b,visible,*getattr(m,'flat_extra_leaves',()))):break
        if(tag,c.pc)==(221,0xadc0):checks+=1
        if len(trace)<8 and c.pc in(0x4020+3*slot,0x5000,0xb79d,0xb22b,0xbf47):trace.append((tag,c.pc,c.a,c.x,c.y,c.sp))
        low=min(low,c.sp);assert m[c.pc],('Detached public BRK',slot,c.pc,c.sp);c.step()
    else:raise AssertionError(('Detached public bound',slot,c.pc,c.sp))
    return dict(PC=c.pc,A=c.a,X=c.x,Y=c.y,P=c.p&0xef,SP=c.sp,CPU=c.processorCycles,
        minimum_SP=low,BtCheck_calls=checks,target=m[0x16c]+256*m[0x16d],next_bank=m[0x162],trace=trace)


def public_units(parent,image):
    fit=shapes(parent,image)
    print('PROGRESS '+json.dumps(dict(exact_detached_shapes_passed=True,Router=224,helper=175)),flush=True)
    seed=Base.cold(image);pair=[]
    for new in(False,True):
        m,labels=detached_seed(seed,new);m.flat_visible=labels['Visible']if new else-1;pair.append(m)
    print('PROGRESS '+json.dumps(dict(genuine_Rash_cold=True)),flush=True)
    selected=W.address(seed.bundle,'SelectedCharacter');fm=W.address(seed.bundle,'FmGroups')
    original_cookie=bytes(seed.ram[3][0x1fe0:0x1ff0]);cases=0;minimum=255;cycles=Counter();smc=Counter();paths=Counter();check_calls=Counter();service_cycles=[]
    # Legal dispatch owners and malformed owners are separate component domains.
    vectors=[]
    for owner in range(256):
        for slot in range(36):vectors.append((owner,0,'valid',slot,0x21,85,7,91))
    for owner in(27,29,31,33):
        for group in range(8):
            for slot in range(36):
                for p in(0x20,0x69,0xe5):vectors.append((owner,group,'valid',slot,p,0,255,0))
    for state,bad in [('retired',-1)]+[('corrupt'+str(i),i)for i in range(16)]:
        for slot in range(36):vectors.append((33,bad,state,slot,0xe9,255,0,255))
    for owner,group,state,slot,p,a,x,y in vectors:
        out=[]
        for m in pair:
            # Each case starts with the same dead stack and executable SMC.
            # Otherwise a deeper previous case leaves non-live stack residues.
            list.__setitem__(m,slice(0x100,0x200),list.__getitem__(seed,slice(0x100,0x200)))
            m[selected]=owner;m[fm]=group if state=='valid'else 64
            m.ram[3][0x1fe0:0x1ff0]=original_cookie
            if state!='valid':m.ram[3][0x1fe0+(group if group>=0 else 0)]^=1
            m.writes.clear();m.ram_writes.clear()
            out.append(public_call(m,slot,a,x,y,p))
        fixed=('PC','A','X','Y','P','SP')
        assert all(out[0][k]==out[1][k]for k in fixed),('Complete public return',owner,group,state,slot,p,out)
        if out[0]['PC']==0x15d:
            assert(out[0]['target'],out[0]['next_bank'])==(out[1]['target'],out[1]['next_bank']),('Private destination',owner,slot,out)
            assert out[0]['BtCheck_calls']==out[1]['BtCheck_calls']or state!='valid'
        diff=Base.M.Research.compare(pair,out,('detached complete transport',owner,group,state,slot,p))
        delta={at for at in range(0x15a,0x17b)if pair[0][at]!=pair[1][at]}
        assert delta<={0x162,0x16c,0x16d},('Undeclared transport difference',owner,slot,delta)
        assert pair[0].vram==pair[1].vram and pair[0].ppuctrl==pair[1].ppuctrl
        smc[tuple(sorted(delta))]+=1;minimum=min(minimum,*(r['minimum_SP']for r in out))
        cycles[owner if owner in(27,29,31,33)else'foreign',state,out[0]['CPU']-out[1]['CPU']]+=1
        cohort=owner if owner in(27,29,31,33)else'foreign'
        check_calls[cohort,state,out[0]['BtCheck_calls'],out[1]['BtCheck_calls']]+=1
        if owner in(27,29,31,33)and group==0 and state=='valid'and p==0x21:
            service_cycles.append(dict(owner=owner,slot=slot,old_CPU=out[0]['CPU'],new_CPU=out[1]['CPU'],savings=out[0]['CPU']-out[1]['CPU'],
                public_complete_return=out[0]['PC']==0x5b00,carry=out[0]['P']&1))
        paths[owner,out[0]['PC']]+=1;cases+=1
        if cases%3000==0:print('PROGRESS '+json.dumps(dict(public_cases=cases)),flush=True)
    return dict(detached_fit=fit,detached_complete_transport_cases=cases,all256_selected_36_services=True,
        legal_cohort_27_29_31_33_three_more_P_corners_eight_groups=True,
        raw33_all16_cookie_corruptions_and_retired_cookie=True,minimum_SP=minimum,
        cycle_savings=[dict(owner=o,state=s,cycles=c,cases=n)for(o,s,c),n in sorted(cycles.items(),key=str)],
        BtCheck_counts=[dict(owner=o,state=s,old=a,new=b,cases=n)for(o,s,a,b),n in sorted(check_calls.items(),key=str)],
        legal_cohort_all36_service_cycles=service_cycles,
        explicit_opaque_SMC=[dict(addresses=list(k),cases=v)for k,v in smc.items()],
        public_NoOp_and_Visible_leaf_executed_to_full_return=True,
        real_private_handlers_stopped_at_original_Router_tail_transport=True,
        physical_ROM_PRG_WRAM_unmodified=True,no_mounted_overlay=True,
        component_selected_group_cookie_register_fixtures_not_natural_gameplay=True)


def ingress(parent,image):
    """Current typed source/descriptor domains, not arbitrary pointer arithmetic."""
    b=Base.symbols(image);targets=set(range(0xb799,0xb848));macros=[]
    def find(data):
        hits=[]
        for i in range(max(0,len(data)-11)):
            p=data[i:i+12]
            if p[0]==0xa9 and p[2:6]==bytes.fromhex('8d6c01a9')and p[7:]==bytes.fromhex('8d6d01a9e0'):
                target=p[1]+256*p[6]
                if target in targets:hits.append(dict(offset=i,target=target,hex=p.hex()))
        return hits
    macros=find(image[16:1048592]);assert len(macros)==1 and macros[0]['target']==0xb79d,macros
    containers=[]
    pages={37:(728,729,730,731,732,733),38:(),39:(301,305,337,362,363,440,819,666),40:(),41:(),42:(991,992),43:()}
    for owner,indices in pages.items():
        data=b''.join(image[1048592+p*1024:1048592+(p+1)*1024]for p in indices)
        hits=find(data);assert not hits,(owner,hits)
        containers.append(dict(role='common_code_rows_'+str(owner),pages=indices,bytes=len(data),SHA256=sha256(data).hexdigest(),farcall_hits=hits))
    import prince_cold_packet_1111 as Prince
    head,streams,_=Prince.extract(image)
    for name,data in zip(('Prince_runtime','Prince_metadata','Prince_staged_state'),streams,strict=True):
        hits=find(data);assert not hits,(name,hits);containers.append(dict(role=name,bytes=len(data),SHA256=sha256(data).hexdigest(),farcall_hits=hits))
    seen=set()
    for seg in b['segs'].values():
        if seg['name'].strip('"')not in('FF_STREAM','BW_STREAM','BT_STREAM','CF_CARRIER','QW_STREAM','KR_KERNEL_IMAGE','ARTHUR_CACHE_EXEC','WF_TEMPLATE_CHR'):continue
        at,size=int(seg['ooffs'],0),int(seg['size'],0)
        if(at,size)in seen:continue
        seen.add((at,size));data=image[at:at+size];hits=find(data);assert not hits,(seg['name'],hits)
        containers.append(dict(role=seg['name'],file=[at,at+size],SHA256=sha256(data).hexdigest(),farcall_hits=hits))
    tables=[]
    def table(name,rows):
        hits=[r for r in rows if r['bank']==224 and r['CPU']in targets]
        tables.append(dict(name=name,rows=len(rows),hits=hits));return hits
    # Actual mounted a90 four readers bind its relocated Hu planes.
    planes=[]
    for at in(653484,653490,653494,653500):
        assert image[at]==0xb9;pc=int.from_bytes(image[at+1:at+3],'little');planes.append(16+79*8192+(pc&8191))
    lo,ix,hi,bank=planes
    assert not table('Hu144',[dict(CPU=image[lo+i]+256*image[hi+image[ix+i]],bank=image[bank+image[ix+i]])for i in range(144)])
    wf=table('Wf36',[dict(slot=i,CPU=image[WF_AT+67+3*i]+256*image[WF_AT+68+3*i],bank=image[WF_AT+69+3*i])for i in range(36)])
    assert len(wf)==16 and {r['CPU']for r in wf}=={0xb799,0xb79b}
    planes=[W.location(b,n)for n in('BwColdLo','BwColdHi','BwColdBank')]
    assert not table('Bw8',[dict(CPU=image[planes[0]+i]+256*image[planes[1]+i],bank=image[planes[2]+i])for i in range(8)])
    data=image[16+124*8192:16+125*8192];nr=0
    for i in range(len(data)-42):
        code=data[i:i+27]
        if code[:9]!=bytes.fromhex('8d6a0108984820cca1'):continue
        if not(code[9]==code[15]==code[21]==0xb9 and code[12:15]==bytes.fromhex('8d6c01')and code[18:21]==bytes.fromhex('8d6d01')and code[24:27]==bytes.fromhex('4c0da6')):continue
        planes=[int.from_bytes(code[j:j+2],'little')&8191 for j in(10,16,22)]
        assert not table('Nr5@'+hex(0xa000+i),[dict(CPU=data[planes[0]+j]+256*data[planes[1]+j],bank=data[planes[2]+j])for j in range(5)]);nr+=1
    assert nr==13
    debug=[];names=('WfResolve','WfNoop','WfVisible','WfResolveTargets','BtRouter','BtServiceVeneers','BwServiceVeneers')
    for name in('kirby-approach-owner-1101-v3/candidate.dbg','bub-menu-candidate-1102-v2/combined-event.dbg','thomas-current-candidate-1102-v3/candidate.dbg'):
        text=(C.R/'build'/name).read_text();records=[];refs=set();segments={};lines=[];wanted=set()
        parse=lambda line:dict(x.split('=',1)for x in line.split('\t',1)[1].split(',')if'='in x)
        for line in text.splitlines():
            if line.startswith('sym\t')and any('name="'+n+'"'in line for n in names):
                row=parse(line);records.append(row);refs.update(row.get('ref','').split('+'))
        refs.discard('')
        for line in text.splitlines():
            if line.startswith('seg\t'):row=parse(line);segments[row['id']]=row
            elif line.startswith('line\t'):
                row=parse(line)
                if row['id']in refs:lines.append(row);wanted.update(row.get('span','').split('+'))
        spans=[]
        for line in text.splitlines():
            if not line.startswith('span\t'):continue
            row=parse(line)
            if row['id']not in wanted:continue
            seg=segments[row['seg']]
            if'ooffs'not in seg:continue
            at=int(seg['ooffs'],0)+int(row['start'],0);size=int(row['size'],0)
            spans.append(dict(file=at,CPU=int(seg['start'],0)+int(row['start'],0),size=size,current_hex=image[at:at+size].hex(),segment=seg['name']))
        debug.append(dict(path=name,SHA256=sha256(text.encode()).hexdigest(),records=records,current_reference_spans=spans))
    return dict(reference_SHA256=C.CANDIDATE,sole_PRG_bankE0_resolver_farcall=macros,
        scanned_executable_containers=containers,structured_indirect_domains=tables,compiler_symbol_reference_domains=debug,
        compiler_refs_and_macro_scans_require_final_owner_classification=True,no_mounted_overlay=True,no_new_whole_image=True)


def wwf_profile(parent,image):
    """Reached original services, with separately measured detached query costs."""
    names=('HULK HOGAN','TED DIBIASE','BAM BAM BIGELOW','HONKY TONK MAN','RANDY SAVAGE','ANDRE THE GIANT')
    b=Base.symbols(image)
    with patch.object(N,'Bus',W.ControllerBus):menu=W.UI.seed(b,0)
    for pad in([4]*3+[1]*4):W.UI.key(menu,pad)
    assert W.UI.menu_name(menu)[0]==names[0]
    rows=[];deltas={};source_cpu=N.NesMPU
    for role,name in enumerate(names):
        m=N.fork(menu)
        for _ in range(role):W.UI.key(m,32)
        assert(W.UI.menu_name(m)[0],N.get(m,'CrossoverMenuIndex'),N.get(m,'SelectedCharacter'),N.get(m,'FmGroups')&7)==(name,28,29,role)
        start=W.UI.key(m,16)
        N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
        N.invoke(m,'PauseRoutine',a=0)
        for _ in range(700):
            if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):break
            m.controller_pad=0;Base.Frames.frame(m,cold=True)
        else:raise AssertionError(('WWF actual constructor bound',role))
        assert N.get(m,'NumberofLives')==2 and N.get(m,'CheatInvincible')==N.get(m,'CheatStartLevel')==0
        for _ in range(4):m.controller_pad=0;Base.Frames.frame(m,whole_pass=True)
        phase_rows=[]
        for phase,pad in(('idle',0),('right',1)):
            calls=Counter();groups=Counter();main=0;returns=0;pending=[];observed=[];active=[];costs=[]
            game=W.address(b,'GameLoop');game_tag=((W.location(b,'GameLoop')-16)//8192)|128
            class Probe(source_cpu):
                def step(self):
                    nonlocal main,returns
                    tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
                    if pending and(self.pc,self.sp)==pending[-1]:pending.pop();returns+=1
                    if(tag,self.pc)==(game_tag,game):
                        ret=(m[0x101+self.sp]+256*m[0x102+self.sp]+1)&65535
                        pending.append((ret,self.sp+2));main+=1
                    if(tag,self.pc)==(215,0xb08e):
                        word=m[0x16c]+256*m[0x16d];offset=word-0xb020
                        assert N.get(m,'SelectedCharacter')==29 and 0<=offset<=105 and offset%3==0
                        group=N.get(m,'FmGroups');assert group&7==role
                        calls[offset//3]+=1;groups[group]+=1
                        if len(observed)<3:observed.append(dict(offset=offset,group=group,A=self.a,X=self.x,Y=self.y,P=self.p,SP=self.sp))
                    return super().step()
            with patch.object(N,'NesMPU',Probe):
                for tick in range(8):
                    old=main,returns;m.controller_pad=pad;costs.append(Base.Frames.frame(m,whole_pass=True))
                    assert(main-old[0],returns-old[1])==(1,1)
                    active.append([dict(slot=i,id=N.get(m,'Enemy_ID',i),x=256*N.get(m,'Enemy_PageLoc',i)+N.get(m,'Enemy_X_Position',i))for i in range(6)if N.get(m,'Enemy_Flag',i)])
            assert not pending
            needed={}
            for slot,count in calls.items():
                if slot not in deltas:
                    pair=[]
                    for new in(False,True):
                        z,labels=detached_seed(m,new);z.flat_visible=labels['Visible']if new else-1;pair.append(z)
                    out=[public_call(z,slot,85,7,91,0x21)for z in pair]
                    Base.M.Research.compare(pair,out,('WWF detached frequency weight',role,slot))
                    deltas[slot]=out[1]['CPU']-out[0]['CPU']
                needed[slot]=deltas[slot]
            delta=sum(count*deltas[slot]for slot,count in calls.items())
            phase_rows.append(dict(phase=phase,Main_entries=main,Main_returns=returns,mean_source_Main=sum(costs)/8,
                actual_service_calls=dict(calls),actual_FmGroups=dict(groups),actual_entry_examples=observed,
                detached_extra_cycles_per_query=needed,weighted_extra_cycles=delta,weighted_extra_cycles_per_Main=delta/8,
                active_native_actors_per_Main=active,actor_health_terrain_position_or_gameplay_seeds=0))
        rows.append(dict(identity=name,role=role,compiled_Select_cycles=role,source_phases=phase_rows))
        print('PROGRESS '+json.dumps(dict(identity=name,weighted_extra_cycles_per_Main=[r['weighted_extra_cycles_per_Main']for r in phase_rows])),flush=True)
    return dict(reference_SHA256=C.CANDIDATE,all_six_actual_compiled_Select_Start_constructors=True,rows=rows,
        actual_original_service_frequencies=True,weighted_new_query_costs_detached_only=True,
        query_arrays_match_actual_proposed_low_bytes_and_page_crossings=True,no_overlay_or_new_image=True,
        physical_cadence_or_FPS_claim=False)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--public',action='store_true');ap.add_argument('--ingress',action='store_true');ap.add_argument('--wwf-profile',action='store_true');args=ap.parse_args()
    parent,image,info=Input.load()
    def forbid(*a,**kw):raise RuntimeError('Detached proposal attempted output/native')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(C.Packet.Frozen.Cold.Runner.Native,'run',forbid):q=wwf_profile(parent,image)if args.wwf_profile else ingress(parent,image)if args.ingress else public_units(parent,image)if args.public else shapes(parent,image)
    q.update(info,outputs=0,Mesen_run=False)
    q['source_receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)


if __name__=='__main__':main()
