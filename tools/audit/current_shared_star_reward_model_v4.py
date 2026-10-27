"""Exact source reward writers for the seven held shared Star/1-Up owners."""
from check_tmnt_render_oa import address,location

IDENTITIES=('zelda2','simon','grant','sypha','alucard','darkwing','ryu')


def metadata(b,identity,resources,character,variant):
    raw=b['raw'];hooks={};order=[];rules={}
    def add(name,n,delta=0,rule=None):
        off=location(b,n)+delta;hooks[name]=dict(pc=address(b,n)+delta,banks=[(off-16)//8192],bytes=list(raw[off:off+3]),source_symbol=n,source_delta=delta)
        order.append(name);rules[name]=rule or name
    def matches(n,pattern):
        off=location(b,n);size=int(b['syms'][n]['size'],0)
        return[i for i in range(size-len(pattern)+1)if raw[off+i:off+i+len(pattern)]==pattern]
    def writer(name,n,field,opcode,index=0):
        a=address(b,field);found=matches(n,bytes([opcode,a&255,a>>8]));assert found,(n,field)
        add(name,n,found[index]);return found
    family='z2'if identity=='zelda2'else'cv3'if identity in ['grant','sypha','alucard']else'darkwing'if identity=='darkwing'else'generic'
    targets=[]
    if family in ['generic','darkwing']:
        writer('RewardGenericSpawn','InventoryEnemyDrop','InvDropKind',0x9d)
        p=bytes([0xac,address(b,'InvDropEnemy')&255,address(b,'InvDropEnemy')>>8]);m=matches('InventoryEnemyDrop',p);assert len(m)==1;add('RewardGenericPublished','InventoryEnemyDrop',m[0])
        p=bytes([0xa9,8,0xbc,address(b,'InvDropKind')&255,address(b,'InvDropKind')>>8]);m=matches('InventoryUpdateDrops',p);assert len(m)==1;add('RewardGenericCollect','InventoryUpdateDrops',m[0])
        add('RewardRefillEntry','InventoryRefillAmount')
        p=bytes([0xae,address(b,'InvDropSlot')&255,address(b,'InvDropSlot')>>8,0xa9,0,0x9d]);m=matches('InventoryUpdateDrops',p);assert len(m)==1;add('RewardGenericReturn','InventoryUpdateDrops',m[0])
        if family=='generic':writer('RewardGenericAmmo','RemainingRefill','InvAmmo',0x9d);targets=[address(b,'InvAmmo')+16*character]
        else:add('RewardDwEntry','DwGiveItem');writer('RewardDwGas','DwGiveItem','DwGas',0x8d);targets=[address(b,'DwGas')]
    elif family=='cv3':
        writer('RewardCvSpawn','Cv3EnemyDropGate','Cv3DropType',0x9d)
        writer('RewardCvCredit','Cv3UpdateDrops','Cv3Hearts',0x99)
        writer('RewardCvKill','Cv3UpdateDrops','Cv3DropType',0x9d)
        targets=[address(b,'Cv3Hearts')+variant-1]
    else:
        writer('RewardZ2Accepted','Z2AwardEnemy','Z2EnemyExpReceipt',0x9d)
        add('RewardZ2Queue','Z2QueueExp');add('RewardZ2Tick','Z2ExpTick');add('RewardZ2Roll','Z2DropRoll')
        for n,field in [('RewardZ2QueueLo','Z2ExpPendingLo'),('RewardZ2QueueHi','Z2ExpPendingHi')]:
            found=writer(n,'Z2QueueExp',field,0x8d);assert len(found)==2
            add(n+'Cap','Z2QueueExp',found[1])
        for n,field in [('RewardZ2TickPendingLo','Z2ExpPendingLo'),('RewardZ2TickPendingHi','Z2ExpPendingHi'),('RewardZ2TickExpLo','Z2ExpLo'),('RewardZ2TickExpHi','Z2ExpHi')]:
            found=writer(n,'Z2ExpTick',field,0x8d);assert len(found)==1
        found=writer('RewardZ2Counter','Z2DropRoll','Z2DropCounters',0x8d,index=2);assert len(found)==4
        add('RewardZ2CounterWrap','Z2DropRoll',found[3])
        targets=[address(b,n)for n in ['Z2DropCounters','Z2ExpPendingLo','Z2ExpPendingHi','Z2ExpLo','Z2ExpHi']]
    index={};labels={};i=0
    for p in resources:
        for j in range(p['count']):
            at=address(b,p['name'])+p['index']+j;assert at not in index
            index[at]=i;labels[at]=p['name']+'['+str(p['index']+j)+']';i+=1
    assert all(at in index for at in targets)
    caps={c:raw[location(b,'InvMaxAmmo')+16*c]for c in [5,10]}
    return dict(family=family,character=character,variant=variant,hooks=hooks,order=order,rules=rules,targets=targets,
        resource_index={str(k):v for k,v in index.items()},resource_labels={str(k):v for k,v in labels.items()},
        generic_caps={str(c):cap for c,cap in caps.items()},darkwing_items=list(raw[location(b,'DwDropMade::Icons'):location(b,'DwDropMade::Icons')+8]),
        enemy_exp=raw[location(b,'EnemyExp')+6],enemy_group=raw[location(b,'EnemyDropGroup')+6])


class Model:
    def __init__(self,cfg,ram,read):
        self.c=cfg;self.ram=ram;self.r=read;self.expected=None;self.pending=None
        self.lookup={(h['pc'],bank):name for name,h in cfg['hooks'].items()for bank in h['banks']}
        self.born={};self.collection=None;self.z=None;self.tick=None;self.roll=None;self.queue=None
        self.events=[];self.credits=[];self.awards=0;self.collections=0

    def start(self,expected):self.expected=expected

    def emit(self,name,pc,bank,**data):self.events.append(dict(event=name,writer_pc=pc,physical_bank=bank,**data))

    def prepare(self,name,field,index,new,a,pc,bank,item,award=0,amount=0):
        assert self.pending is None,('Overlapping credit',name,self.pending)
        at=self.ram[field]+index;expected=self.expected[self.c['resource_index'][str(at)]];old=self.r(field,index)
        assert old==expected and a==new,('Exact source credit arithmetic',name,field,index,old,expected,a,new)
        self.pending=dict(writer_pc=pc,physical_bank=bank,address=at,field=field,index=index,old=old,new=a,item_kind=item,award_count=award,award_amount=amount,rule=name)

    def write(self,at,v,pc,bank):
        if self.expected is None or at not in self.c['targets']:return
        idx=self.c['resource_index'][str(at)]
        if self.pending:
            p=self.pending
            assert p['address']==at and p['new']==v and p['writer_pc']==pc and p['physical_bank']==bank,('Actual committed source writer',p,at,v,pc,bank)
            self.expected[idx]=v;self.credits.append(p.copy());self.awards+=p['award_count'];self.pending=None
        else:
            assert v==self.expected[idx],('Uncredited resource writer',dict(address=at,field=self.c['resource_labels'][str(at)],old=self.expected[idx],new=v,writer_pc=pc,physical_bank=bank))

    def event(self,pc,bank,a,x,y,phase,hits):
        if self.expected is None:return
        name=self.lookup.get((pc,bank))
        if name is None:return
        c=self.c;r=self.r;family=c['family']
        assert r('SelectedCharacter')==c['character']
        if name=='RewardGenericSpawn':
            assert phase=='contact'and hits['StarContact']==1 and 0<=x<4 and r('InvDropKind',x)==0 and r('InvDropEnemy')==0 and r('Enemy_ID',0)==6
            assert r('PseudoRandomBitReg',1)&3==0 and a==(1 if r('PseudoRandomBitReg',2)<192 else 2)
            self.born[x]=dict(kind=a,rng=r('PseudoRandomBitReg',2),published=False,consumed=False)
            self.emit(name,pc,bank,slot=x,old=0,new=a,item_kind=a,award_count=0)
        elif name=='RewardGenericPublished':
            b=self.born.get(x);assert b and not b['published']
            kind=r('InvDropKind',x);item=r('AvDropItem',x)
            assert kind==(1 if b['rng']<(205 if family=='generic'else 192)else 2)
            assert item==(0 if family=='generic'else c['darkwing_items'][b['rng']&7])
            b.update(kind=kind,item=item,published=True)
            self.emit(name,pc,bank,slot=x,item_kind=item,drop_size=kind,award_count=0)
        elif name=='RewardGenericCollect':
            b=self.born.get(x);assert phase=='expiry'and b and b['published']and not b['consumed']and r('InvDropKind',x)==b['kind']and r('AvDropItem',x)==b['item']
            assert r('InvDropSlot')==x and 0<r('InvDropAge',x)<256 and r('InvDropAgeHi',x)==0
            assert self.collection is None
            self.collection=dict(slot=x,kind=b['kind'],item=b['item'],amount=40 if b['kind']==2 else 8,refill=False,credited=False,give=False)
            self.collections+=1;self.emit(name,pc,bank,slot=x,item_kind=b['item'],drop_size=b['kind'],award_count=1)
        elif name=='RewardRefillEntry':
            q=self.collection;assert q and not q['refill']and a==q['amount']and r('AvRefillItem')==q['item']and r('InvDropSlot')==q['slot'];q['refill']=True
        elif name=='RewardGenericAmmo':
            q=self.collection;assert family=='generic'and q and q['refill']and not q['credited']and q['item']==0 and x==16*c['character']and r('InvItem')==0 and r('InvDropAmount')==q['amount']
            amount=(5 if q['amount']==40 else 1)if c['character']==5 else(10 if q['amount']==40 else 5)
            cap=99 if c['character']==10 and r('InvOwnedLo',10)&128 else c['generic_caps'][str(c['character'])]
            self.prepare(name,'InvAmmo',x,min(r('InvAmmo',x)+amount,cap),a,pc,bank,q['item'],1,amount);q['credited']=True
        elif name=='RewardDwEntry':
            q=self.collection;assert q and q['refill']and not q['give']and a==q['item']and 0x22<=a<=0x25
            assert r('DwHealth')==4,'Star protection retains cold full health before any reward heal';q['give']=True
        elif name=='RewardDwGas':
            q=self.collection;assert family=='darkwing'and q and q['give']and not q['credited']and q['item']in [0x24,0x25]
            amount=10 if q['item']==0x24 else 1
            self.prepare(name,'DwGas',0,min(r('DwGas')+amount,99),a,pc,bank,q['item'],1,amount);q['credited']=True
        elif name=='RewardGenericReturn':
            q=self.collection;assert q and q['refill']and(q['credited']if family=='generic'or q['item']in [0x24,0x25]else q['give'])
            assert r('InvDropKind',q['slot'])==q['kind'];self.born[q['slot']]['consumed']=True;self.collection=None
        elif name=='RewardCvSpawn':
            assert phase=='contact'and hits['StarContact']==1 and 0<=x<2 and r('Cv3DropType',x)==0 and r('Cv3HitSlot')==0 and r('Enemy_ID',0)==6
            assert r('PseudoRandomBitReg',1)&3==0 and a==(5 if r('PseudoRandomBitReg',2)>=192 else 1)
            self.born[x]=dict(kind=a,consumed=False);self.emit(name,pc,bank,slot=x,old=0,new=a,item_kind=a,award_count=0)
        elif name=='RewardCvCredit':
            b=self.born.get(x);assert phase=='expiry'and b and not b['consumed']and b['kind']==r('Cv3DropType',x)and r('Cv3DropAge',x)>0 and y==c['variant']-1 and r('Cv3HitSlot')==x
            self.prepare(name,'Cv3Hearts',y,min(r('Cv3Hearts',y)+b['kind'],99),a,pc,bank,b['kind'],1,b['kind'])
            b['consumed']=True;self.collections+=1;self.emit('physical-CV3-collection',pc,bank,slot=x,item_kind=b['kind'],award_count=1)
        elif name=='RewardCvKill':
            if x in self.born:assert self.born[x]['consumed']and a==0
        elif name=='RewardZ2Accepted':
            assert phase=='contact'and hits['StarContact']==1 and x==0 and r('Enemy_ID',0)==6 and r('Z2EnemyExpReceipt',0)&128==0 and a==(r('Z2EnemyExpReceipt',0)|128)and self.z is None
            assert c['enemy_exp']==2 and c['enemy_group']==1
            self.z=dict(exp=r('Z2ExpLo')+256*r('Z2ExpHi'),queued=False,rolled=False)
            self.emit(name,pc,bank,enemy_slot=0,item_kind='Goomba-EXP2/weak-counter',old=r('Z2EnemyExpReceipt',0),new=a,award_count=0)
        elif name=='RewardZ2Queue':
            assert self.z and not self.z['queued']and a==c['enemy_exp']and y==0 and r('Z2HitSlot')==0
            total=r('Z2ExpPendingLo')+256*r('Z2ExpPendingHi')+a;assert total<=65535
            self.queue=total;self.z['queued']=True
        elif name in ['RewardZ2QueueLo','RewardZ2QueueHi']:
            assert self.queue is not None
            low=name.endswith('Lo');field='Z2ExpPendingLo'if low else'Z2ExpPendingHi'
            self.prepare(name,field,0,self.queue&255 if low else self.queue>>8,a,pc,bank,'EXP2',1 if low else 0,2 if low else 0)
        elif name.endswith('Cap'):raise AssertionError(('Cold Goomba EXP2 cannot overflow',name))
        elif name=='RewardZ2Roll':
            assert self.z and not self.z['rolled']and a==1 and r('Z2DropCounters')==0;self.roll=1;self.z['rolled']=True
        elif name=='RewardZ2Counter':
            assert self.roll==1;self.prepare(name,'Z2DropCounters',0,1,a,pc,bank,'weak-defeat-counter',0,1)
        elif name=='RewardZ2CounterWrap':raise AssertionError('Cold one-Goomba counter cannot wrap')
        elif name=='RewardZ2Tick':
            pending=r('Z2ExpPendingLo')+256*r('Z2ExpPendingHi')
            if pending:
                assert self.z and self.z['queued'];amount=10 if pending>=10 else 1
                self.tick=dict(pending=pending-amount,exp=(r('Z2ExpLo')+256*r('Z2ExpHi')+amount)&65535,amount=amount)
            else:self.tick=None
        elif name.startswith('RewardZ2Tick'):
            assert self.tick is not None
            field={'RewardZ2TickPendingLo':'Z2ExpPendingLo','RewardZ2TickPendingHi':'Z2ExpPendingHi','RewardZ2TickExpLo':'Z2ExpLo','RewardZ2TickExpHi':'Z2ExpHi'}[name]
            value=self.tick['pending'if'Pending'in name else'exp'];value=value&255 if name.endswith('Lo')else value>>8
            self.prepare(name,field,0,value,a,pc,bank,'EXP-transfer',0,self.tick['amount'])
        else:raise AssertionError(('Unknown credit rule',name))

    def finish(self):
        assert self.pending is None and self.collection is None
        assert all(b['consumed']for b in self.born.values()),'No credit from an uncollected spawn'
        if self.c['family']=='z2':
            assert self.z and self.z['queued']and self.z['rolled']and self.awards==1
            assert self.r('Z2ExpPendingLo')==self.r('Z2ExpPendingHi')==0 and self.r('Z2ExpLo')+256*self.r('Z2ExpHi')==self.z['exp']+2 and self.r('Z2DropCounters')==1
        return dict(credits=self.credits,provenance_events=self.events,resource_awards=self.awards,physical_collections=self.collections)
