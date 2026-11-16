"""Same header/Ready/Fresh checks; use actual resident kernel-retire seam."""
from pathlib import Path
from unittest.mock import patch
import inspect,json
import check_mini_weapon_owner_guards_1116 as Previous

C,N,W,Public=Previous.C,Previous.N,Previous.W,Previous.Public

def retire(m):
    raw=m.bundle['raw'];at=16+65*8192+(0xae00&8191)
    assert raw[at:at+19]==bytes.fromhex('08488a489848a900f00808488a489848a90148')
    # The actual CoCold BEQ skips this saved-AXYP mode1 entry. Source
    # CoRetire uses the same saved state/CoRetireOwners/CoInvalidate path.
    m[W.address(m.bundle,'SafecallA_SMC')+1]=85;m[W.address(m.bundle,'FarcallJmpTarget_SMC')+1]=10;m[W.address(m.bundle,'FarcallJmpTarget_SMC')+2]=0xae
    c=N.NesMPU(memory=m,pc=W.address(m.bundle,'FarCallCommon'));c.a=193;c.x=7;c.y=91;c.p=0x31;c.sp=224;c.stPushWord(0x5aff);minimum=224;entry=None
    for _ in range(500000):
        if c.pc==0x5b00:break
        if c.pc==0xae0a and m.rawtags[1]==193:entry=dict(PC=c.pc,SP=c.sp,bank=65)
        minimum=min(minimum,c.sp);assert m[c.pc],('Actual CoRetire BRK',c.pc);c.step()
    else:raise AssertionError('Actual resident CoRetire return bound')
    assert entry and c.sp==224 and(c.a,c.x,c.y,c.p&239)==(85,7,91,0x21)
    return dict(entry=entry,A=c.a,X=c.x,Y=c.y,P=c.p,SP=c.sp,minimum_SP=minimum,CPU=c.processorCycles)

def run(parent):
    source=inspect.getsource(Previous.run)
    start=source.index('    a=Public.parent_clone(seed,parent);b=N.fork(seed)\n    assert \'FmNativePrepare\'')
    end=source.index('    q=dict(passed=True',start)
    new="""    a=Public.parent_clone(seed,parent);b=N.fork(seed)
    old=N.invoke(a,'FmNativePrepare');new=N.invoke(b,'FmNativePrepare')
    assert Public.state(a)==Public.state(b)and all(old[k]==new[k]for k in('A','X','Y','P'))
    graphics_headers=[bytes(b.ram[k][0x1fe0:0x1ff0]).hex()for k in(2,3)]
    a=Public.parent_clone(seed,parent);b=N.fork(seed)
    for t in(a,b):N.put(t,SelectedCharacter=0)
    old_retire=retire(a);new_retire=retire(b)
    assert Public.state(a)==Public.state(b)and old_retire==new_retire
    retired=[bytes(b.ram[k][0x1fe0:0x1ff0]).hex()for k in(2,3)]
    assert all(b.ram[k][0x1fe0]==0 for k in(2,3)),retired
    entries.clear();N.put(b,SelectedCharacter=41,PlayerStatus=2,A_B_Buttons=64,PreviousA_B_Buttons=0,SavedJoypadBits=64)
    with patch.object(N,'NesMPU',CPU):after=Public.public(b,34)
    assert not entries and not after['hits'].get('Mini_native_weapon',0),(retired,entries,after)
"""
    source=source[:start]+new+source[end:]
    source=source.replace('actual_FmNativePrepare=dict(parent=old,candidate=new,retired_headers=retired,after_weapon=after)',"actual_FmNativePrepare=dict(parent=old,candidate=new,headers_after_graphics_prepare=graphics_headers,kernel_retirement_not_assumed=True),actual_resident_CoRetire=dict(parent=old_retire,candidate=new_retire,retired_headers=retired,after_weapon=after)")
    env=dict(Previous.__dict__,retire=retire);exec(compile(source,str(Path(__file__))+':actual-retire-seam','exec'),env);return env['run'](parent)

if __name__=='__main__':
    parent=C.ROM.read_bytes()
    def deny(*a,**kw):raise AssertionError('Mini lifecycle attempted artifacts/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(parent)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
