"""Declared actual-candidate callback components; not gameplay qualification."""
import current_bowser_life_gain_1116 as Current

C,N,W=Current.C,Current.N,Current.W

def clear(m):
    m.writes.clear();m.ram_writes.clear();m.ppu_log.clear()

def fork(m):
    q=N.fork(m);clear(q);return q

def reference(m,parent):
    q=fork(m);q.bundle=dict(q.bundle,raw=parent)
    e=C.lease()['envelope'];lo,hi=e['CPU_half_open']
    q.ram[3][lo&8191:hi&8191]=bytes.fromhex(e['old_hex'])
    q.ram[3][0x1fe0:0x1ff0]=bytes.fromhex(C.lease()['cookie_views']['old_hex'])
    for slot,tag in enumerate(q.rawtags):
        if tag&128:q.raw_page(slot,tag)
    clear(q);return q

def call(m,name,*,a=85,x=7,y=91,p=0x31,tag=None,stop=None,watch=None):
    b=m.bundle;target=W.address(b,name)
    if tag is None:tag=3 if name in('BwConstruct','BwEnsure','BwMovement','BwWeaponTail','BwInjury','BwGraphics','BwSelectPlayer','BwSavePlayer')else((W.location(b,name)-16)//8192)|128
    m[W.address(b,'SafecallA_SMC')+1]=a
    m[W.address(b,'FarcallJmpTarget_SMC')+1]=target&255;m[W.address(b,'FarcallJmpTarget_SMC')+2]=target>>8
    c=N.NesMPU(memory=m,pc=W.address(b,'FarCallCommon'));c.a=tag;c.x=x;c.y=y;c.p=p;c.sp=224;c.stPushWord(0x5aff)
    low=c.sp
    for steps in range(500000):
        if c.pc==0x5b00 or stop and stop(m,c):break
        if watch:watch(m,c)
        low=min(low,c.sp);assert m[c.pc],('Component BRK',name,hex(c.pc),m.rawtags);c.step()
    else:raise AssertionError(('Component call bound',name,hex(c.pc)))
    if stop is None:assert c.sp==224
    return c,dict(A=c.a,X=c.x,Y=c.y,P=c.p,SP=c.sp,PC=c.pc,cycles=c.processorCycles,minimum_SP=low,steps=steps)

def flags(n):return 0x30|sum(v for i,v in enumerate((1,2,4,8,64,128))if n>>i&1)

def application_equal(a,b):
    lo,hi=C.lease()['envelope']['CPU_half_open'];excluded=set(range(lo&8191,hi&8191))|set(range(0x1fe0,0x1ff0))
    assert bytes(a[:0x800])==bytes(b[:0x800]),'Native component effects differ'
    for bank in range(4):
        if bank==3:assert all(x==y for i,(x,y)in enumerate(zip(a.ram[bank],b.ram[bank]))if i not in excluded)
        else:assert a.ram[bank]==b.ram[bank]
    assert a.rawtags==b.rawtags and a.chr_latches==b.chr_latches
