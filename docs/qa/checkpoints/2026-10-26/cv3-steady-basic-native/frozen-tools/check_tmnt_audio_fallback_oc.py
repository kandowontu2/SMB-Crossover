"""Exact non-TMNT dispatcher/DMC compatibility and qualified label ownership."""
from pathlib import Path
import argparse
import gzip
import hashlib
import itertools
import json
from check_tmnt_render_oa import load,Memory,address,location
from verify_native_relocation import NesMPU


def qualified(path):
    f=path.with_suffix('.dbg');text=f.read_text()if f.exists()else gzip.decompress(path.with_suffix('.dbg.gz').read_bytes()).decode()
    scopes={};symbols=[]
    for line in text.splitlines():
        if not line.startswith(('scope\t','sym\t')):continue
        z=dict(q.split('=',1)for q in line.split('\t',1)[1].split(',')if '='in q)
        if line.startswith('scope\t'):scopes[z['id']]=z
        else:symbols.append(z)
    def prefix(i):
        names=[]
        while i in scopes:
            q=scopes[i];name=q.get('name','""').strip('"')
            if name.startswith('$anon'):return None
            if name:names.append(name)
            i=q.get('parent')
        return tuple(reversed(names))
    result={}
    for q in symbols:
        if 'val'not in q or q.get('type')not in ('lab','equ'):continue
        path=prefix(q.get('scope'));name=q['name'].strip('"')
        if path is not None and not name.startswith('$anon'):result[path+(name,)]=int(q['val'],0)
    return result


def execute(b,name,seed,a=0x55,x=3,y=7,flags=0x30,cbank=38):
    m=Memory(b);m.page(2,cbank)
    m[address(b,'CurrentBankC')]=cbank|128
    for n,v in seed.items():
        if isinstance(n,int):m[n]=v
        else:m[address(b,n)]=v
    m[0x1fe]=0xff;m[0x1ff]=0x7e;m.writes=[]
    c=NesMPU(memory=m,pc=name if isinstance(name,int)else address(b,name));c.a=a;c.x=x;c.y=y;c.p=flags;c.sp=0xfd
    for _ in range(50000):
        if c.pc==0x7f00:break
        c.step()
    else:raise AssertionError(('Fallback timeout',name,seed,hex(c.pc),m.banks))
    return c,m


def result(c,m):
    # Discarded CPU stack only. SMC operands, every ordinary RAM byte,
    # register image, mapper shadows and final bank mappings remain compared.
    return(c.a,c.x,c.y,c.p&0xcf,c.sp,bytes(m[:0x1a0])+bytes(m[0x200:0x8000]),list(m.banks),
           [(at,v)for at,v in m.writes if 0x4000<=at<=0x4017 or 0x5000<=at<=0x5015])


def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--baseline',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);old,new=load(a.baseline),load(a.rom)
    qb,qa=qualified(a.baseline),qualified(a.rom)
    assert qa[('_FARCALL_COUNT',)]==qb[('_FARCALL_COUNT',)]+3,'Two old calls replaced by five new resident calls'
    changed={str(n):[v,qa.get(n)]for n,v in qb.items()if qa.get(n)!=v and n!=('_FARCALL_COUNT',)and not(len(n)>1 and n[0]=='SamusAudioUpdate')}
    assert not changed,list(changed.items())[:20]
    # Compiler-generated anonymous scope IDs change when an earlier scope is
    # added. Pin the actual bytes instead of treating their names as an ABI.
    before,after=old['raw'],new['raw'];vg=location(old,'VgAudioDispatch')
    changed38={i for i in range(8192)if before[16+38*8192+i]!=after[16+38*8192+i]}
    assert changed38=={vg-16-38*8192+21,vg-16-38*8192+22}
    assert before[vg+20]==after[vg+20]==0x4c
    foreground={1:set(),4:set()}
    for name,size,gate in [('TnFastGraphicsSpan',18,'TnFastGraphicsGate'),('TnFastSpecialSpan',18,'TnFastSpecialGate'),('TnFastDrawSpan',3,'TnFastDrawGate')]:
        pos=location(new,name);bank=(pos-16)//8192;assert bank in foreground
        foreground[bank].update(range(pos-16-bank*8192,pos-16-bank*8192+size))
        assert after[pos:pos+3]==bytes([0x20,address(new,gate)&255,address(new,gate)>>8])
        if size==18:assert after[pos+3]==0x4c and after[pos+6:pos+18]==bytes([0xea])*12
    for bank,allowed in foreground.items():
        actual={i for i in range(8192)if before[16+bank*8192+i]!=after[16+bank*8192+i]}
        assert actual<=allowed,(bank,actual-allowed)
    off=address(old,'DmcOff');init=address(old,'AudioInit');update=address(old,'AudioUpdate');changed_fixed=[]
    assert before[location(old,'AudioInit'):location(old,'AudioInit')+5]==bytes([0xa9,0,0x8d,address(old,'PauseModeFlag')&255,address(old,'PauseModeFlag')>>8])
    assert before[location(old,'AudioUpdate')]==0xad and after[location(new,'AudioUpdate')]==0x20
    for i in range(8192):
        if before[16+127*8192+i]!=after[16+127*8192+i]:
            pc=0xe000+i;assert 0xe874<=pc<0xeb42 or off-8<=pc<off or init<=pc<init+5 or update<=pc<update+3,hex(pc);changed_fixed.append(pc)
    for bank in range(128):
        if bank not in [1,4,38,123,124,125,127]:assert before[16+bank*8192:16+(bank+1)*8192]==after[16+bank*8192:16+(bank+1)*8192]
    hold=address(new,'TnAudioDacHold');dmc_cases=dispatch_cases=native_cases=0
    drain=address(new,'TnDmcDrain');assert drain==address(new,'BassAudioSavedApu')+6
    init_cases=gate_cases=transition_cases=0
    # Run the exact displaced linked instructions, followed by an RTS in RAM.
    # Both machines have the same test trampoline bytes at the same address.
    def span(b,name,size,seed,**kw):
        code=b['raw'][location(b,name):location(b,name)+size]+bytes([0x60])
        c,m=execute(b,0x7e00,seed|{0x7e00+i:v for i,v in enumerate(code)},**kw)
        # The test trampoline contains different old/new instructions; it is
        # harness memory, not application output. Every other RAM byte remains.
        m[0x7e00:0x7e00+len(code)]=[0]*len(code)
        return c,m
    for pending,acc,flags in itertools.product([0,1,127,255],[0,85,255],[0x30,0x71,0x39,0xee]):
        seed={drain:pending,'PauseModeFlag':37}
        c,m=span(old,'AudioInit',5,seed,a=acc,flags=flags);d,n=span(new,'AudioInit',5,seed,a=acc,flags=flags)
        m[drain]=0
        assert result(c,m)==result(d,n),'Exact AudioInit displaced span plus owned drain initialization'
        init_cases+=1
    for marker,char,mode,flags in itertools.product(list(range(15))+[254,255],range(21),[0,1],[0x30,0x71,0x39,0xee]):
        seed={'XgAudioCharacter':marker,'SelectedCharacter':char,'OperMode':mode,drain:0,0x4011:7,hold:37}
        c,m=span(old,'AudioUpdate',3,seed,flags=flags);d,n=span(new,'AudioUpdate',3,seed,flags=flags)
        assert result(c,m)==result(d,n),(marker,char,mode,flags)
        gate_cases+=1
    for char,mode,owner,flags in itertools.product(range(21),[0,1],[0,1,2,4],[0x30,0x71,0x39,0xee]):
        seed={'XgAudioCharacter':253,'SelectedCharacter':char,'OperMode':mode,drain:0,hold:44,
              'BassDmcActive':owner,'GuestCombinedEnable':31,0x4011:44}
        c,m=span(new,'AudioUpdate',3,seed,flags=flags)
        assert(c.a,c.x,c.y,c.p&0xcf,c.sp)==(mode,3,7,(flags&0x4d)|(2 if mode==0 else 0),0xff)
        if char==19 and mode==1:
            assert m[drain]==0 and m[hold]==44 and m[0x4011]==44 and m[address(new,'BassDmcActive')]==owner
        else:
            assert m[drain]==1 and m[hold]==0 and m[0x4011]==0 and m[address(new,'BassDmcActive')]==0
            assert m[address(new,'XgAudioCharacter')]==255 and m[0x4015]==15
        transition_cases+=1
    for owner,marker,flags in itertools.product([0,1,2,3,4],[0,2,6,14,253,254,255],[0x30,0x71,0x39,0xee]):
        c,m=span(new,'AudioUpdate',3,{'XgAudioCharacter':marker,'SelectedCharacter':19,'OperMode':1,
            drain:1,hold:99,'BassDmcActive':owner,0x4011:44},flags=flags)
        assert m[drain]==0 and m[0x4011]==(0 if owner==0 else 44) and m[hold]==99
        assert m[address(new,'BassDmcActive')]==owner,'Pending cleanup must preserve a new live sample owner'
        transition_cases+=1
    for char,owner,status,acc,flags in itertools.product(range(21),[0,1,2,3,4,5,255],[0,16,31],[0,15,16,31,255],[0x30,0x71,0x39,0xee]):
        seed={'SelectedCharacter':char,'BassDmcActive':owner,0x4015:status,0x4011:7,hold:37}
        c,m=execute(old,'GuestDmcStatus',seed,a=acc,flags=flags)
        d,n=execute(new,'GuestDmcStatus',seed,a=acc,flags=flags)
        native=char==19 and owner==4 and status&16==0
        if native:
            assert(c.a,c.x,c.y,c.p&0xcf,c.sp)==(d.a,d.x,d.y,d.p&0xcf,d.sp)
            assert n[address(new,'BassDmcActive')]==0 and n[hold]==44 and n[0x4011]==7
            assert not any(at==0x4011 for at,v in n.writes)
            native_cases+=1
        else:assert result(c,m)==result(d,n),(char,owner,status,acc,flags)
        dmc_cases+=1
    for char,area,event,paused,variant in itertools.product([6,7,9,10,11,12,13,14,15,16,17,18],[1,2,4,8,16,32,64,128],[0,4,64],[0,1],[0,1]):
        seed={'SelectedCharacter':char,'OperMode':1,'AreaMusicQueue':area,'EventMusicQueue':event,'GamePauseStatus':paused,
              'VvVariant':variant,'KbVariant':variant,'RlVariant':variant,'CurrentBank':0xd7}
        c,m=execute(old,'VgAudioDispatch',seed);d,n=execute(new,'VgAudioDispatch',seed)
        assert result(c,m)==result(d,n),(char,area,event,paused,variant)
        dispatch_cases+=1
    proof=dict(passed=True,ROM_sha256=hashlib.sha256(new['raw']).hexdigest(),baseline_ROM_sha256=hashlib.sha256(old['raw']).hexdigest(),
               named_qualified_preexisting_symbols_checked=len(qb),all_unmoved_named_symbols_preserved=True,
               changed_fixed_bytes_within_exact_owned_ranges=len(changed_fixed),unchanged_other_PRG_banks=True,
               build_only_farcall_counter_delta=3,
               allowed_relocation='Only procedure-private SamusAudioUpdate labels; its global entry and all other qualified symbols remain fixed.',
               DMC_cases=dmc_cases,native_hold_cases=native_cases,non_Tmnt_dispatch_cases=dispatch_cases,
               cold_init_span_cases=init_cases,non_native_global_gate_cases=gate_cases,transition_gate_cases=transition_cases,
               scope='Actual linked CPU units with seeded coherent request states. Exact non-TMNT A/X/Y/meaningfulP/SP, RAM outside discarded stack, hardware writes and physical banks. Native completed owner4 preserves hardware DAC and records source hold44. No native waveform or campaign claim.',
               checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof,indent=2))


if __name__=='__main__':main()
