"""One ordinary current Burns Main: bounded SFC/request/effect aggregates."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import argparse,json
import current_contra_force_readonly_1327_1116 as M

N,W,Frames=M.N,M.W,M.Frames
BRIDGE_SHA='2fd8fc83a6d3d55f967bb5ccef3efbcb25c7cd6638acc3ca7235ec13c7115c94'


def run(raw,right=False):
    assert M.H(Path(M.__file__).read_bytes())==BRIDGE_SHA
    q=M.bindings(raw);m=M.cold(raw);b=m.bundle
    for _ in range(4):m.controller_pad=0;Frames.frame(m,whole_pass=True)
    game=W.address(b,'GameLoop');gameTag=((W.location(b,'GameLoop')-16)//8192)|128
    safeA=W.address(b,'SafecallA_SMC')+1
    zp=tuple(W.address(b,'R'+str(i))for i in range(2,8))
    assert zp==(5,6,7,8,9,10),'Actual compiled R2..R7 domain'
    carrier=q['carrier'];targets=[carrier[8192+0x1f49+i]+256*carrier[8192+0x1f6d+i]for i in range(36)]
    base=N.NesMPU;reader=type(m).__getitem__;writer=type(m).__setitem__
    totals=Counter();groups={};queryGroups={};cells=Counter();header=Counter();fieldFirst={};protocol=Counter();objects=[]
    ctx={'cpu':None,'instruction':False};ordinal=0
    fields={W.address(b,n):n for n in('SelectedCharacter','FmGroups','Player_X_Position','Player_PageLoc','Player_Y_Position',
        'CrouchingFlag','PlayerStatus','NumberofLives','GamePauseStatus','AreaAddrsLOffset')}
    def tag(pc):return m.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else-1
    def ret(c):
        pc=(m[256+((c.sp+1)&255)]+256*m[256+((c.sp+2)&255)]+1)&65535
        return pc,(c.sp+2)&255,tag(pc)
    def regs(c):return(c.a,c.x,c.y,c.p)
    def group(key):
        assert len(groups)<192 or key in groups,'Bounded SFC aggregate capacity'
        return groups.setdefault(key,dict(calls=0,returns=0,inclusive=0,exclusive=0,requests=Counter(),results=Counter(),parent_paths=Counter(),reads=Counter(),writes=Counter(),changes={},transport_writes=Counter()))
    def physical(at):
        return(tag(at),at&8191)if at>=0x8000 else(-1,at)
    class CPU(base):
        def __init__(self,*a,**kw):
            super().__init__(*a,**kw);self.main=None;self.sfcs=[];self.queries=[];self.interrupts=[];self.doneISR=0;self.previous=None;objects.append(self)
        def interrupt(self,kind):
            old=self.pc,self.sp;start=self.processorCycles;out=super().nmi()if kind=='NMI'else super().irq()
            if(self.pc,self.sp)!=old:self.interrupts.append((old,start))
            return out
        def nmi(self):return self.interrupt('NMI')
        def irq(self):return self.interrupt('IRQ')
        def settle(self):
            while self.interrupts and(self.pc,self.sp)==self.interrupts[-1][0]:
                _,start=self.interrupts.pop()
                if not self.interrupts:self.doneISR+=self.processorCycles-start
            if self.interrupts:return
            now=self.pc,self.sp,tag(self.pc)
            while self.queries and now==self.queries[-1]['return']:
                node=self.queries.pop();slot=node['slot'];g=queryGroups[slot];g['returns']+=1
                g['inclusive']+=self.processorCycles-node['start']-(self.doneISR-node['ISR'])
                g['results'][regs(self)+tuple(m[i]for i in zp)]+=1
                if slot in(10,14):
                    pointer=m[zp[4]]+256*m[zp[5]];cell=(pointer+m[zp[0]])&65535
                    key=(cell,m[zp[1]]);cells[key]+=1;g['cell_keys'][(cell,m[zp[1]],m[zp[2]],m[zp[3]])]+=1
            while self.sfcs and now==self.sfcs[-1]['return']:
                node=self.sfcs.pop();g=group(node['key']);g['returns']+=1
                g['inclusive']+=self.processorCycles-node['start']-(self.doneISR-node['ISR'])
                g['exclusive']+=node['exclusive'];g['results'][regs(self)]+=1
            if self.main==now:self.main=None;totals['Main_returns']+=1
        def step(self):
            nonlocal ordinal
            self.settle();ctx['cpu']=self
            if self.interrupts:return super().step()
            owner=tag(self.pc);pc=self.pc
            if(owner,pc)==(gameTag,game):assert self.main is None;self.main=ret(self);totals['Main_entries']+=1
            if self.main is not None:
                if pc==0x15a or(pc==0x15d and not(self.sfcs and self.sfcs[-1]['entrySP']==self.sp)):
                    bank=self.a if pc==0x15a else m[0x162];target=m[0x16c]+256*m[0x16d]
                    previous=self.previous or(-1,-1,-1)
                    returned=ret(self);key=(bank,target,previous[0],previous[1],returned[2],returned[0])
                    node=dict(key=key,entrySP=self.sp,return_=returned,start=self.processorCycles,ISR=self.doneISR,exclusive=0)
                    node['return']=node.pop('return_');parent_path=tuple(n['key']for n in self.sfcs)
                    self.sfcs.append(node);g=group(key);g['calls']+=1;g['parent_paths'][parent_path]+=1
                    request=(m[safeA],self.x,self.y,self.p,m[0x7da1],m.rawtags[2],self.sp)
                    g['requests'][request]+=1;totals['SFC_entries']+=1
                if owner==215 and 0xb020<=pc<0xb08c and(pc-0xb020)%3==0:
                    slot=(pc-0xb020)//3;self.queries.append(dict(slot=slot,return_=ret(self),start=self.processorCycles,ISR=self.doneISR,outer_reads=set()))
                    self.queries[-1]['return']=self.queries[-1].pop('return_')
                    g=queryGroups.setdefault(slot,dict(calls=0,returns=0,inclusive=0,requests=Counter(),results=Counter(),cell_keys=Counter(),private_entries=0))
                    g['calls']+=1;g['requests'][(self.a,self.x,self.y,self.p,N.get(m,'Player_X_Position'),N.get(m,'Player_PageLoc'),N.get(m,'Player_Y_Position'),N.get(m,'CrouchingFlag'))]+=1
                if owner==2 and 0xbe00<=pc<0xbe6c and(pc-0xbe00)%3==0:
                    assert self.queries;queryGroups[self.queries[-1]['slot']]['private_entries']+=1
                    assert self.queries[-1]['outer_reads']==set(range(16))
            mode=self.disassemble[m[pc]][1]
            size=1 if mode in('acc','imp')else 2 if mode in('imm','zpg','zpx','zpy','rel','inx','iny')else 3
            ctx['fetch']=(owner,pc,pc+size)
            start=self.processorCycles;ctx['instruction']=True
            try:out=super().step()
            finally:ctx['instruction']=False
            delta=self.processorCycles-start
            if self.main is not None:
                ordinal+=1;totals['Main_cycles']+=delta
                if self.sfcs:self.sfcs[-1]['exclusive']+=delta
                else:totals['root_cycles']+=delta
            self.previous=(owner,pc);return out
    def read(bus,at):
        c=ctx['cpu']
        if ctx['instruction']and c and c.main is not None and not c.interrupts and isinstance(at,int):
            fetchTag,lo,hi=ctx['fetch'];isfetch=lo<=at<hi and tag(at)==fetchTag
            if c.sfcs and not isfetch and not 0x100<=at<0x200:group(c.sfcs[-1]['key'])['reads'][physical(at)]+=1
            if at>=0x8000 and tag(at)==2 and 0x1fe0<=at&8191<0x1ff0:
                layer='outer'if tag(c.pc)==197 else'inner'if tag(c.pc)==2 else'other'
                slot=c.queries[-1]['slot']if c.queries else-1;header[slot,layer,(at&8191)-0x1fe0]+=1
                if layer=='outer'and c.queries:c.queries[-1]['outer_reads'].add((at&8191)-0x1fe0)
        return reader(bus,at)
    def write(bus,at,value):
        c=ctx['cpu']
        if ctx['instruction']and c and c.main is not None and not c.interrupts and isinstance(at,int):
            g=group(c.sfcs[-1]['key'])if c.sfcs else None
            transport=0x15a<=at<0x17b or at in(0x145,0x7da0,0x7da1,0x5114,0x5115,0x5116,0x5117)or 0x100<=at<0x200
            if transport:
                if g is not None:g['transport_writes'][at]+=1
            elif at<0x2000 or at>=0x6000:
                key=physical(at);old=reader(bus,at);value&=255
                if g is not None:
                    g['writes'][key]+=1
                    if old!=value:
                        change=g['changes'].setdefault(key,dict(before=old,after=value,first_ordinal=ordinal,first_PC=c.pc,first_tag=tag(c.pc),changes=0))
                        change['after']=value;change['changes']+=1
                label=fields.get(at)if at<0x8000 else('RAM'+str(key[0])+'header'+str(key[1]-0x1fe0)if key[0]in(2,3)and 0x1fe0<=key[1]<0x1ff0 else None)
                if label and old!=value:
                    fieldFirst.setdefault(label,dict(address=at,physical=key,before=old,after=value,ordinal=ordinal,PC=c.pc,tag=tag(c.pc)))
                if key[0]in(2,3)and 0x1fe0<=key[1]<0x1ff0:protocol['header_writes']+=1
            else:
                if g is not None:g['transport_writes'][at]+=1
        return writer(bus,at,value)
    with patch.object(N,'NesMPU',CPU),patch.object(type(m),'__getitem__',read),patch.object(type(m),'__setitem__',write):
        m.controller_pad=int(right);Frames.frame(m,whole_pass=True)
    for c in objects:c.settle();assert c.main is None and not c.sfcs and not c.queries and not c.interrupts
    M.empty(m);assert totals['Main_entries']==totals['Main_returns']==1
    assert all(g['calls']==g['returns']for g in groups.values())and all(g['calls']==g['returns']==g['private_entries']for g in queryGroups.values())
    assert totals['root_cycles']+sum(g['exclusive']for g in groups.values())==totals['Main_cycles']
    rows=[]
    for key,g in sorted(groups.items(),key=lambda item:-item[1]['exclusive']):
        bank,target,callerTag,callerPC,returnTag,returnPC=key
        changes=[dict(tag=t,address=a,**v)for(t,a),v in sorted(g['changes'].items(),key=lambda item:item[1]['first_ordinal'])]
        rows.append(dict(bank_tag=bank,target_PC=target,caller_tag=callerTag,caller_PC=callerPC,return_tag=returnTag,return_PC=returnPC,
            calls=g['calls'],inclusive_cycles=g['inclusive'],exclusive_cycles=g['exclusive'],
            request_AXYP_Cshadow_Cmap_SP=[dict(values=k,calls=v)for k,v in g['requests'].items()],
            parent_SFC_paths=[dict(path=k,calls=v)for k,v in g['parent_paths'].items()],
            returned_AXYP=[dict(values=k,calls=v)for k,v in g['results'].items()],
            data_read_count=sum(g['reads'].values()),distinct_data_read_addresses=len(g['reads']),
            data_reads_top8=[dict(tag=t,address=a,reads=n)for(t,a),n in g['reads'].most_common(8)],
            data_write_count=sum(g['writes'].values()),distinct_data_write_addresses=len(g['writes']),
            actual_changed_addresses=len(changes),first8_changed_addresses=changes[:8],
            all_changed_address_records_SHA256=M.H(json.dumps(changes,sort_keys=True,separators=(',',':')).encode()),
            transport_write_count=sum(g['transport_writes'].values())))
    queries=[dict(slot=slot,handler_PC=targets[slot],calls=g['calls'],returns=g['returns'],inclusive_cycles=g['inclusive'],
        requests=[dict(AXYP_nativeXY_crouch=k,calls=v)for k,v in g['requests'].items()],
        results=[dict(AXYP_R2_R3_R4_R5_R6_R7=k,calls=v)for k,v in g['results'].items()],
        cell_keys=[dict(cell_tile_fraction_column=k,calls=v)for k,v in g['cell_keys'].items()])for slot,g in sorted(queryGroups.items())]
    out=dict(passed=True,owning_SHA256=M.H(raw),phase='Right'if right else'idle',bindings=q['current_proof'],compiled_R2_R7=zp,
        actual_Main=dict(totals),SFC_groups=rows,queries=queries,
        native_tile_cell_repeats=[dict(address=a,tile=t,reads=n)for(a,t),n in cells.items()],
        header_reads16=[dict(slot=s,layer=l,counts=[header[s,l,i]for i in range(16)])for s,l in sorted({(s,l)for s,l,i in header})],
        first_changed_watched_fields=fieldFirst,protocol=dict(protocol),
        retained_observer_cell_domain_negative=dict(job=50037,source_SHA256='87297975eec69c77e9283145f5694bbe7a8ff593b523647957c2cfc56fc79756',
            receipt_SHA256='48810bb55902a0b12f103430f0910b1ac67a56bb35454b9c8457c9b5f3a35723',scope='SFC/caller/cycles/effects valid; hardcoded ZP2..7 cell fields unqualified and ignored. Current code binds actual compiled R2..R7=5..10.'),
        scope='One genuine-menu/cold Burns Main after4warm; SFC exclusive includes unlabelled callee work. Nested inclusive costs overlap. No new game code, masks, seeds, native or cadence claim.',outputs=0)
    out['receipt_SHA256']=M.H(json.dumps(out,sort_keys=True,separators=(',',':')).encode());return out


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--right',action='store_true');a=p.parse_args();raw=M.load_current_image()
    original=Path.read_bytes
    def read(path):
        assert path.resolve()!=M.ROM.resolve(),'No second mutable Nightly read'
        return original(path)
    def deny(*a,**k):raise AssertionError('Read-only request audit attempted files/native')
    with patch.object(Path,'read_bytes',read),patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):out=run(raw,a.right)
    print('RESULT '+json.dumps(out,separators=(',',':')),flush=True)
