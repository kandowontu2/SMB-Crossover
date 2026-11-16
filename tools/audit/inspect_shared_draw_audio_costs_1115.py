"""Read-only reached DrawAll/Audio callsite costs on exact current7fb CPU."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import argparse,json
from py65.disassembler import Disassembler
from py65.devices.mpu6502 import MPU
import replay_battletoads_attribution_7fb_1115 as Current

C,W,N,Frames=Current.C,Current.W,Current.N,Current.Model.Frames


def run(raw):
    m=Current.cold(raw);b=m.bundle;base=N.NesMPU
    points=Current.config(raw)['attribution']['points']
    targets={(((h['offset']//8192)|128),h['pc']):name for name,h in points.items()if name in('DrawAllMetasprites','AudioUpdate')}
    assert targets=={(132,0xa000):'DrawAllMetasprites',(255,0xf05d):'AudioUpdate'}
    for _ in range(4):m.controller_pad=0;Frames.frame(m,whole_pass=True)
    names_cache={}
    def names(tag,pc):
        key=tag,pc
        if key in names_cache:return names_cache[key]
        out=[]
        for name,s in b['syms'].items():
            if 'val'not in s or int(s['val'],0)!=pc:continue
            try:
                seg=b['segs'].get(s.get('seg'),{})
                actual=3 if seg.get('name','').startswith('"BT_CACHE')else((W.location(b,name)-16)//8192)|128
            except(KeyError,AssertionError):continue
            if actual==tag:out.append(name)
        names_cache[key]=out[:5];return names_cache[key]
    phases=[]
    for phase,pad in(('idle',0),('Right',1)):
        calls=Counter();costs=Counter();own=Counter();pcs=Counter();unwinds=Counter();root_calls=Counter();root_cycles=Counter();examples={};instances=[]
        class Probe(base):
            def __init__(self,*a,**kw):
                super().__init__(*a,**kw);self.scope=None;self.frames=[];instances.append(self)
            def step(self):
                tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
                while self.frames:
                    row=self.frames[-1]
                    if(self.pc,self.sp)==row['return']:
                        self.frames.pop();calls[row['key']]+=1;costs[row['key']]+=self.processorCycles-row['start']
                        if row['key']not in examples:examples[row['key']]=dict(row['entry'],returned=dict(A=self.a,X=self.x,Y=self.y,P=self.p,SP=self.sp,PC=self.pc))
                    elif self.sp>row['return'][1]:
                        self.frames.pop();unwinds[row['key']]+=1
                    else:break
                if self.scope and(self.pc,self.sp)==self.scope['return']:
                    assert not self.frames,('Unreturned scoped JSR',self.scope,self.frames)
                    root_calls[self.scope['name']]+=1;root_cycles[self.scope['name']]+=self.processorCycles-self.scope['start'];self.scope=None
                if(tag,self.pc)in targets:
                    assert self.scope is None,('Overlapping root source scopes',self.scope,self.pc)
                    ret=(m[0x100+((self.sp+1)&255)]+256*m[0x100+((self.sp+2)&255)]+1)&65535
                    self.scope=dict(name=targets[tag,self.pc],start=self.processorCycles,**{'return':(ret,(self.sp+2)&255)})
                if self.scope and m[self.pc]==0x20:
                    target=m[self.pc+1]+256*m[self.pc+2];tt=m.rawtags[(target-0x8000)//8192]if target>=0x8000 else-1
                    bank,word=(self.a,m[0x16c]+256*m[0x16d])if target==0x15a else(-1,-1)
                    key=self.scope['name'],len(self.frames),tag,self.pc,tt,target,bank,word
                    entry=dict(A=self.a,X=self.x,Y=self.y,P=self.p,SP=self.sp,opcode=bytes(m[self.pc:self.pc+3]).hex())
                    self.frames.append(dict(key=key,start=self.processorCycles,entry=entry,**{'return':((self.pc+3)&65535,self.sp)}))
                pc=self.pc;scope=self.scope['name']if self.scope else None;depth=len(self.frames);before=self.processorCycles
                result=super().step();cost=self.processorCycles-before
                if scope:
                    pcs[scope,tag,pc]+=cost
                    if not depth:own[scope]+=cost
                return result
        with patch.object(N,'NesMPU',Probe):
            for _ in range(4):
                m.controller_pad=pad;Frames.frame(m,whole_pass=True)
                assert (N.get(m,'SelectedCharacter'),N.get(m,'NumberofLives'),N.get(m,'PlayerStatus'))==(33,2,0)
                assert m.ram[3][W.address(b,'BtSrc_Objects_Life')&8191]==47
                assert not any(N.get(m,'Enemy_Flag',i)for i in range(6))
        assert root_calls==Counter(DrawAllMetasprites=4,AudioUpdate=4),root_calls
        assert not any(c.scope or c.frames for c in instances)
        rows=[]
        for scope in('DrawAllMetasprites','AudioUpdate'):
            direct=[];hot=[]
            for key,cycles in sorted(costs.items(),key=lambda r:r[1],reverse=True):
                s,depth,ct,pc,tt,target,bank,word=key
                if s!=scope:continue
                row=dict(depth=depth,caller_tag=ct,caller_PC=pc,target_tag=tt,target_PC=target,target_names=names(tt,target),
                    calls_per_scope=calls[key]/4,cycles_per_scope=cycles/4,far_bank=bank,far_target=word,example=examples[key])
                if bank>=0:row['far_names']=names(bank,word)
                if depth==0:direct.append(row)
                if len(hot)<12:hot.append(row)
            top=[]
            for(s,tag,pc),cycles in pcs.most_common():
                if s!=scope:continue
                top.append(dict(tag=tag,PC=pc,cycles_per_scope=cycles/4,names=names(tag,pc)))
                if len(top)==8:break
            rows.append(dict(scope=scope,calls=root_calls[scope],mean_cycles=root_cycles[scope]/4,
                root_instructions_outside_JSR=own[scope]/4,direct_calls=direct,top_nested_calls=hot,top_instructions=top))
        phases.append(dict(phase=phase,rows=rows,
            nonlocal_JSR_unwinds=[dict(key=list(k),count=n)for k,n in unwinds.items()],
            actual_current7fb_bytes=True,source_cycles_not_native_cadence=True))
        print('PROGRESS '+json.dumps(dict(phase=phase,scope_cycles={k:root_cycles[k]/4 for k in root_calls})),flush=True)
    return dict(ROM_SHA256=C.digest(raw),phases=phases,genuine_compiled_Rash_cold=True,ordinary_idle_Right_only=True,
        no_gameplay_actor_health_position_or_terrain_seeds=True,nested_spans_overlap=True,
        source_only=True,outputs=0,Mesen_run=False,code_or_image_changes=False)


def inspect_current(raw):
    b=Current.symbols(raw);rows=[]
    wanted=['KbDrawDispatch','ThSharedDrawHot','NrDraw','HuDraw','RlSpecialDrawDispatch','ExpandedAudioUpdate','VgAudioDispatch']
    wanted.extend(n for n in b['syms']if n.startswith('Nr')and any(x in n for x in('Resolve','Family')))
    for name in dict.fromkeys(wanted):
        if name not in b['syms']:continue
        at=W.location(b,name);pc=W.address(b,name);assert 16<=at<1048592
        size=50 if name=='KbDrawDispatch'else 96;data=raw[at:at+size]
        memory=[0]*65536;memory[pc:pc+size]=data;d=Disassembler(MPU(memory=memory));listing=[];cursor=pc
        for _ in range(28):
            if cursor>=pc+size:break
            n,text=d.instruction_at(cursor);listing.append(dict(PC=cursor,hex=bytes(memory[cursor:cursor+n]).hex(),op=text));cursor+=n
        rows.append(dict(name=name,PC=pc,file=at,tag=((at-16)//8192)|128,inspected_bytes=size,SHA256=C.digest(data),prefix_hex=data[:32].hex(),listing=listing,
            bytes_are_live_code_or_data_not_free_padding=True))
    return dict(ROM_SHA256=C.digest(raw),actual_current_compiled_points=rows,source_only=True,outputs=0,
        Mesen_run=False,code_or_image_changes=False,no_funding_or_allocation_claim=True)


def funding(raw):
    # Count an existing retained source packing, without assembling/emitting
    # replacement instructions. The old FF-specialized recipe is not applied.
    source=C.R/'tools/reference/ff_hot_draw_forwarding_1110.s';text=source.read_text()
    count=0;data=0;instructions=0
    implied={'php','pha','txa','tya','pla','tay','tax','plp'}
    for original in text.splitlines():
        line=original.split(';',1)[0].strip()
        if not line or line.endswith(':')or line.startswith(('.setcpu','.segment')):continue
        if line.startswith('.byte'):
            data+=len(line.split(None,1)[1].split(','));continue
        op,*rest=line.split(None,1);operand=rest[0]if rest else''
        if op in implied:size=1
        elif op in('bne','beq','bcs'):size=2
        elif op in('ldx','cmp','and')and operand.startswith('#'):size=2
        elif op in('lda','sta','jmp'):size=3
        else:raise AssertionError(('Uncounted retained packing instruction',original))
        count+=size;instructions+=1
    assert(count,data)==(89,27)
    start,end=545972,546090;body=raw[start:end];table=body[-27:]
    assert C.digest(body)=='0991df9191ae7b3cf47a4c520515e5f91598d0004e4c57d80bebd09067fdd22e'
    assert all(table[i+1]==table[i+2]for i in(0,9,18))
    records=[dict(row=i,bank=table[18+i],PC=table[i]+256*table[9+i])for i in range(9)]
    assert records[1]['bank']==records[2]['bank']==207 and records[1]['PC']==records[2]['PC']==0xa8f0
    return dict(ROM_SHA256=C.digest(raw),proposed_owner='Raw33 Rash/Zitz through existing public BT draw router',
        physical_envelope=[start,end],CPU_envelope=[0xb4a4,0xb51a],physical_PRG_bank=66,
        current_SHA256=C.digest(body),current_records=records,
        retained_packing_source=str(source.relative_to(C.R)),retained_packing_SHA256=C.digest(source.read_bytes()),
        retained_source_instruction_count=instructions,packing_instruction_bytes=count,packing_table_bytes=data,
        proposed_maximum_bytes=count+data,existing_envelope_bytes=118,
        logical_funding='Identical rows1/2 fold to one Cd target; row2 reused. Compact existing classification reclaims8 code bytes;6 pay for the special owner test',
        proposed_row2=dict(bank=215,PC=0xb026,public_service='BtServiceVeneers+6, unchanged full BtCheck'),
        all_other_target_records_retained=True,all_ThShared108_following_bytes_retained_SHA256=C.digest(raw[end:end+108]),
        Kb_gate50_retained_SHA256=C.digest(raw[40924:40924+50]),
        declared_body_tail_is_live_not_funding=True,new_RAM_CHR_or_physical_space=0,
        source_noop_routing_cycles_avoided=507,estimated_extra_classifier_cycles=8,estimated_net_per_render=499,
        new_bytes_assembled_or_emitted=False,no_proposed_image_composed=True,
        public_flags_SMC_fault_foreign_cost_and_reached_ISR_qualification_still_required=True,
        allocation_or_implementation_authorized=False,outputs=0,Mesen_run=False)


def main():
    ap=argparse.ArgumentParser();group=ap.add_mutually_exclusive_group();group.add_argument('--inspect',action='store_true');group.add_argument('--funding',action='store_true');args=ap.parse_args()
    raw=Current.load_current_image()
    def deny(*a,**kw):raise AssertionError('Read-only cost inspection attempted output/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch.object(C.Prior.Packet.Frozen.Cold.Runner.Native,'run',deny):q=(funding if args.funding else inspect_current if args.inspect else run)(raw)
    q['source_receipt_SHA256']=C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)


if __name__=='__main__':main()
