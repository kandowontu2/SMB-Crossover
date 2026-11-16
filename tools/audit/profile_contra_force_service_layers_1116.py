"""Read-only actualffbb per-service/layer/transport attribution, no rewrite."""
from collections import Counter,defaultdict
from pathlib import Path
from unittest.mock import patch
import json,re
import contra_force_p1_work_marker_model_1116 as M
import compose_battletoads_mature8_1116 as BT

C,N,W,Frames=M.C,M.N,M.W,M.Frames


def load_reference():
    """Explicit current BT join is a reference extraction, not CF execution."""
    actual=C.ROM.read_bytes()
    if C.H(actual)==C.PIN:return actual,C.PIN
    assert C.H(actual)==BT.CANDIDATE,'Only explicit exact91dc or6a3 input'
    assert C.H(Path(BT.__file__).read_bytes())=='6db3aa513aac81d022efdc881b01bdcb93a639ccd4f99e8671fed3f8986bb27c'
    reference=BT.inverse(actual)
    assert C.H(reference)==C.PIN and BT.proposal(reference)[0]==actual
    return reference,C.H(actual)


def profile(raw,busy):
    parent=M.parent(raw);z,s=C.Plan.inputs(parent);b=M.symbols(raw)
    carrier=raw[C.Plan.Audit.P.CHR+935*1024:C.Plan.Audit.P.CHR+959*1024]
    lo=8192+(s['CfOwnLo']&8191);hi=8192+(s['CfOwnHi']&8191)
    targets=[carrier[lo+i]+256*carrier[hi+i]for i in range(36)]
    names={pc:min((n for n,v in s.items()if v==pc and n.startswith('Cf')),key=len,default=f'{pc:04X}')for pc in set(targets)}
    points={}
    def add(tag,pc,name,kind):
        if(tag,pc)not in points:points[tag,pc]=(name,kind)
    for name in('GameLoop','CfOrBtCheck','NrMovement','NrDraw','HuMovement','HuDraw'):
        at=W.location(b,name);add(((at-16)//8192)|128,W.address(b,name),name,'main'if name=='GameLoop'else'outer_header'if name=='CfOrBtCheck'else'generic_wrapper')
    # Only genuine .proc/macro API roots, not every interior symbol bearing
    # an Nr/Hu prefix. SFC destinations below are bound dynamically as well.
    source=(C.R/'src/new_roster_dispatch.s').read_text()
    roots=set(re.findall(r'^NrGate\s+(Nr\w+),',source,re.M))|set(re.findall(r'^\.proc\s+(Nr\w+)',source,re.M))
    roots|={'Hu'+n[2:]for n in tuple(roots)}
    for name in sorted(roots):
        try:at=W.location(b,name);pc=W.address(b,name)
        except(KeyError,AssertionError):continue
        if pc>=0x8000:add(((at-16)//8192)|128,pc,name,'generic_wrapper')
    for tag,pc,name,kind in((215,0xb08e,'ROM87Router','generic_router'),(224,0xb799,'WfResolve96','generic_resolver'),
        (195,0xb22b,'BwCfResolve67','generic_resolver'),(2,0xbe6e,'CfA2Router','private_router'),(2,s['CfCallA'],'CfCallA','private_transport')):
        add(tag,pc,name,kind)
    for pc in set(targets):add(3,pc,names[pc],'leaf')
    # The frozen metadata model caches by equal byte value but deliberately
    # authenticates its returned raw object's identity. Reuse that exact
    # cached reference object; actual execution remains owning `raw` below.
    reference=M.P.Model.symbols(z['reference'])['raw']
    assert reference==z['reference']
    q=M.P.bindings(reference)
    for(tag,pc),p in q['points'].items():
        if tag in(1,2,3):add(tag,pc,p['name'],'private_internal')
    m=M.cold(raw)
    for _ in range(4):m.controller_pad=0;Frames.frame(m,whole_pass=True)
    base=N.NesMPU;rows=[]
    for phase,pad in(('idle',0),('Right',1)):
        calls=Counter();returned=Counter();inclusive=Counter();exclusive=Counter();service=Counter();leaf=Counter();header=Counter();readPC=Counter();transport=Counter();before_private=[]
        ISR=Counter();SFCphysical=Counter();contexts=[];instances=[];minimum=255;ctx={'cpu':None,'inside':False}
        class CPU(base):
            def __init__(self,*a,**kw):
                super().__init__(*a,**kw);self.pending=[];self.interrupts=[];self.doneISR=0;self.injected=False;instances.append(self)
            def interrupt(self,kind):
                ret=(self.pc,self.sp);start=self.processorCycles
                out=super().nmi()if kind=='NMI'else super().irq()
                if(self.pc,self.sp)!=ret:self.interrupts.append((ret,start,kind))
                return out
            def nmi(self):return self.interrupt('NMI')
            def irq(self):return self.interrupt('IRQ')
            def settle(self):
                while self.interrupts and(self.pc,self.sp)==self.interrupts[-1][0]:
                    _,start,kind=self.interrupts.pop();cy=self.processorCycles-start
                    if not self.interrupts:self.doneISR+=cy;ISR[kind]+=cy
                if self.interrupts:return
                tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
                while self.pending and(self.pc,self.sp,tag)==self.pending[-1]['return']:
                    node=self.pending.pop();wall=self.processorCycles-node['start']-(self.doneISR-node['ISR'])
                    key=(node['kind'],node['name']);returned[key]+=1;inclusive[key]+=wall;exclusive[key]+=node['exclusive']
                    queries=node['queries'];query=next(iter(queries))if len(queries)==1 else-1
                    service[query,node['kind'],'exclusive']+=node['exclusive'];service[query,node['kind'],'calls']+=1
                    if node['kind']=='query':service[query,'query','inclusive']+=wall;service[query,'query','returns']+=1
                    if node['kind']=='leaf':leaf[query,'calls']+=1;leaf[query,'inclusive']+=wall;leaf[query,'exclusive']+=node['exclusive']
            def enter(self,name,kind,query=None):
                sp=self.sp;pc=(m[0x100+((sp+1)&255)]+256*m[0x100+((sp+2)&255)]+1)&65535
                tag=m.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else-1
                inherited=next((n['queries']for n in reversed(self.pending)if n['kind']=='query'),set())
                node=dict(name=name,kind=kind,start=self.processorCycles,ISR=self.doneISR,exclusive=0,queries=set(inherited))
                node['return']=(pc,(sp+2)&255,tag)
                self.pending.append(node);calls[kind,name]+=1
                if query is not None:
                    for parent_node in self.pending:parent_node['queries'].add(query)
                    node['outer_reads']=set()
            def step(self):
                nonlocal minimum
                self.settle();ctx['cpu']=self
                if self.interrupts:
                    return super().step()
                tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
                if busy and not self.injected and(tag,self.pc)==(3,s['CfHostMovement']):
                    assert N.get(m,'NmiDisable')&128;self.injected=True;self.nmi();return
                current_query=next((next(iter(n['queries']))for n in reversed(self.pending)if n['kind']=='query'),None)
                if self.pc==0x15a or(self.pc==0x15d and not(self.pending and self.pending[-1]['kind']=='SFC'and self.pending[-1]['entrySP']==self.sp)):
                    bank=self.a if self.pc==0x15a else m[0x162];target=m[0x16c]+256*m[0x16d]
                    self.enter(f'SFC->{bank:02X}','SFC');self.pending[-1]['entrySP']=self.sp
                    transport[bank,target]+=1
                if tag==215 and 0xb020<=self.pc<0xb08c and(self.pc-0xb020)%3==0:
                    current_query=(self.pc-0xb020)//3;self.enter('Query'+str(current_query),'query',current_query)
                if tag==2 and 0xbe00<=self.pc<0xbe6c and(self.pc-0xbe00)%3==0:
                    offset=(self.pc-0xbe00)//3
                    query_node=next(n for n in reversed(self.pending)if n['kind']=='query')
                    outer=query_node['outer_reads']
                    before_private.append((offset,tuple(sorted(outer))))
                point=points.get((tag,self.pc))
                if point:
                    name,kind=point
                    if kind=='leaf':
                        ret=(m[0x100+((self.sp+1)&255)]+256*m[0x100+((self.sp+2)&255)]+1)&65535
                        if ret==0xca2b and current_query is not None:
                            assert targets[current_query]==self.pc,(current_query,self.pc)
                            name='Leaf'+str(current_query)+':'+name
                        else:kind='private_internal'
                    self.enter(name,kind)
                start=self.processorCycles;minimum=min(minimum,self.sp);ctx['inside']=True
                try:out=super().step()
                finally:ctx['inside']=False
                if self.pending:self.pending[-1]['exclusive']+=self.processorCycles-start
                if self.pending and self.pending[-1]['kind']=='SFC':
                    # A scope spanning FarCall also contains any unlabelled
                    # callee body. Separate actual lowRAM transport from it.
                    owner='lowRAM'if tag==-1 else f'RAM{tag}'if tag<128 else f'PRG{tag&127}'
                    SFCphysical[owner]+=self.processorCycles-start
                return out
        reader=type(m).__getitem__
        def read(bus,at):
            c=ctx['cpu']
            if ctx['inside']and c and not c.interrupts and isinstance(at,int)and at>=0x8000:
                tag=bus.rawtags[(at-0x8000)//8192]
                if tag==2 and 0x1fe0<=at&8191<0x1ff0:
                    query=next((next(iter(n['queries']))for n in reversed(c.pending)if n['kind']=='query'),-1)
                    layer=next((n['kind']for n in reversed(c.pending)if n['kind']in('outer_header','private_router')),'other')
                    header[query,layer,(at&8191)-0x1fe0]+=1
                    if layer=='outer_header':
                        query_node=next(n for n in reversed(c.pending)if n['kind']=='query')
                        query_node['outer_reads'].add((at&8191)-0x1fe0)
                    pc_tag=bus.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
                    readPC[pc_tag,c.pc,layer]+=1
            return reader(bus,at)
        with patch.object(N,'NesMPU',CPU),patch.object(type(m),'__getitem__',read):
            for _ in range(4):m.controller_pad=pad;Frames.frame(m,whole_pass=True);M.empty(m,'burns')
        for c in instances:
            c.settle();assert not c.pending and not c.interrupts,('Unclosed attribution scope',[(n['name'],n['return'])for n in c.pending])
        assert calls==returned
        assert sum(exclusive.values())==inclusive['main','GameLoop'],'Exclusive scopes must partition actual Main'
        main_count=calls['main','GameLoop'];table=[]
        for i,pc in enumerate(targets):
            table.append(dict(service=i,command_offset=3*i,handler_PC=pc,handler=names[pc],calls=leaf[i,'calls'],
                handler_inclusive_cycles=leaf[i,'inclusive'],handler_exclusive_cycles=leaf[i,'exclusive'],
                query_inclusive_cycles=service[i,'query','inclusive'],query_returns=service[i,'query','returns'],
                exclusive_layers={kind:n for(qry,kind,metric),n in service.items()if qry==i and metric=='exclusive'}))
        row=dict(phase=phase,busy_NMI_component=busy,actual_Main=main_count,main_inclusive_excluding_ISR=inclusive['main','GameLoop'],
            all_named_entries_returns_exact=True,minimum_SP=minimum,services36=table,
            aggregate_layers=[dict(kind=kind,name=name,calls=n,inclusive_cycles=inclusive[kind,name],exclusive_cycles=exclusive[kind,name])for(kind,name),n in sorted(calls.items())],
            actual_SFC_destinations=[dict(bank_tag=bank,PC=pc,calls=n)for(bank,pc),n in sorted(transport.items())],
            innermost_SFC_physical_exclusive=dict(SFCphysical),
            header_reads16=[dict(service=q,layer=l,counts=[header[q,l,i]for i in range(16)])for q,l in sorted({(q,l)for q,l,i in header})],
            actual_header_read_PCs=[dict(tag=t,PC=pc,layer=l,reads=n)for(t,pc,l),n in sorted(readPC.items())],
            preprivate_outer16_signatures=[dict(service=q,bytes=list(signature),calls=n)for(q,signature),n in sorted(Counter(before_private).items())],
            ISR_cycles=dict(ISR),no_actor_shot_health_position_or_terrain_seeds=True)
        rows.append(row);print('PROGRESS '+json.dumps(dict(phase=phase,busy=busy,Main=main_count,private_handlers=sum(leaf[i,'calls']for i in range(36)),cycles=row['main_inclusive_excluding_ISR'])),flush=True)
    return rows


if __name__=='__main__':
    parent,input_pin=load_reference();raw,_=C.proposal(parent)
    def deny(*a,**kw):raise AssertionError('Layer attribution attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
        q=dict(ROM_SHA256=C.H(raw),normal=profile(raw,False),busy_catchup=profile(raw,True),outputs=0,native=False,
            actual_input_SHA256=input_pin,execution_scope='Frozen6a3 parent to exact RAMffbb; current BT inverse reference only',
            inclusive_rows_overlap_exclusive_layers_partition_observed_Main=True,no_funding_or_new_code_proposed=True)
    q['source_receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
