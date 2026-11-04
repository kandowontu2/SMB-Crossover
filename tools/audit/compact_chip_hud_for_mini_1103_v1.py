"""Recover exactly two source-backed CD_LOGIC bytes for Mini's two-slot gate."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
from py65.devices.mpu6502 import MPU
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
import build_storage_guard_v1 as G
from prepare_mini_mario_native_power_1103_v56 import bundle,address
from check_tmnt_render_oa import location
O=R/'build/mini-constant-funding-1103-v1'
PARENT=R/'build/mini-final-candidate-1103/mini-optimized.nes'
PIN='f552fd7ba20d4bdee4455c1f577ef966197dd792a2b885e8ecaf2a32dd40a481'
sha=lambda b:hashlib.sha256(b).hexdigest()
SRC=R/'src/chip_hud_queue.s'


def transform(source):
    a=' beq RestoreAppend\n jmp Suppress'
    b='Fallback:\n ldy #0\n jmp Finished'
    assert source.count(a)==source.count(b)==1
    return source.replace(a,' beq RestoreAppend\n bne Suppress').replace(b,'Fallback:\n ldy #0\n beq Finished')


def assemble(stem,text):
    (O/(stem+'.s')).write_text(text)
    cfg=O/'hud.cfg'
    if not cfg.exists():cfg.write_text('MEMORY{M:start=$a98a,size=$152,file=%O;}SEGMENTS{CD_LOGIC:load=M,type=ro;}')
    cc=R/'tools/Windows/cc65/bin'
    for args in [[cc/'ca65.exe',O/(stem+'.s'),'-o',O/(stem+'.o')],
        [cc/'ld65.exe','-C',cfg,O/(stem+'.o'),'-o',O/(stem+'.bin')]]:
        p=subprocess.run(list(map(str,args)),capture_output=True,text=True);assert p.returncode==0,p.stderr
    (O/(stem+'.o')).unlink()
    return (O/(stem+'.bin')).read_bytes()


class CPU(MPU):
    def opADC(self,x):
        d=self.p&8;self.p&=~8;super().opADC(x);self.p|=d
    def opSBC(self,x):
        d=self.p&8;self.p&=~8;super().opSBC(x);self.p|=d


class Memory(bytearray):
    writes=None
    def __setitem__(self,a,v):
        super().__setitem__(a,v)
        if self.writes is not None:self.writes.append((a,v))


def main():
    G.preflight(private_root=O,reserved_bytes=60000,reserved_files=7,fresh=True);O.mkdir(exist_ok=True)
    raw=PARENT.read_bytes();assert sha(raw)==PIN;b=bundle(raw)
    assert address(b,'CdQueueHud')==0xa98a
    src=SRC.read_text();body=src[src.index('.proc CdQueueHud'):src.index('.endproc',src.index('.proc CdQueueHud'))+len('.endproc')]
    prefix='.setcpu "6502"\n.macpack longbranch\n.segment "CD_LOGIC"\n'+''.join(
        n+f'=${address(b,n):04x}\n' for n in ['VRAM_Buffer1','VRAM_Buffer1_Offset','CdHudText','CdHealth'])
    old=assemble('chip-hud-reference',prefix+body+'\n')
    new=assemble('chip-hud-fast',prefix+transform(body)+'\n')
    at=location(b,'CdQueueHud');assert old==raw[at:at+338] and len(old)==338 and len(new)==336
    assert raw[at+338:at+340]==raw[16+79*8192+0xadc:16+79*8192+0xade]
    # The source's only external consumer is CdHud's JMP to the unchanged
    # entry. Internal scoped labels are never exported as dynamic targets.
    hits=[]
    for p in [*R.joinpath('src').rglob('*.s'),*R.joinpath('src').rglob('*.inc'),*R.joinpath('tools/reference').rglob('*.s'),*R.joinpath('tools/reference').rglob('*.inc')]:
        text=p.read_text(errors='ignore')
        if p!=SRC and 'CdQueueHud' in text:hits.append((p.relative_to(R).as_posix(),[x.strip() for x in text.splitlines() if 'CdQueueHud' in x]))
        assert 'CdQueueHud::' not in text,(p,'External internal-label reference')
    assert hits==[('src/chip_dale_health.s',['jmp CdQueueHud'])],hits
    memories=[];cpus=[]
    for code in [old,new]:
        m=Memory(65536);m[0xa98a:0xa98a+len(code)]=code
        m[address(b,'CdHudText'):address(b,'CdHudText')+2]=b'HP'
        memories.append(m);cpus.append(CPU(memory=m))
    buf=address(b,'VRAM_Buffer1');off=address(b,'VRAM_Buffer1_Offset');health=address(b,'CdHealth')
    count=0;seen_old=set();seen_new=set();max_steps=0;cycles=set()
    def case(queue,n,h=3,y=0x7d,p=0x61):
        nonlocal count,max_steps
        outputs=[]
        for m,c in zip(memories,cpus):
            m.writes=None;m[buf:buf+256]=bytes(256);m[buf:buf+len(queue)]=bytes(queue);m[off]=n;m[health]=h
            c.pc=0xa98a;c.a=0x93;c.x=n;c.y=y;c.p=p;c.sp=0xe0;c.stPushWord(0x5aff);m.writes=[]
            start=c.processorCycles;steps=0
            for steps in range(10000):
                if c.pc==0x5b00:break
                (seen_old if m is memories[0] else seen_new).add(c.pc);c.step()
            else:raise AssertionError(('CPU bound',n,queue))
            outputs.append((c.a,c.x,c.y,c.p,c.sp,bytes(m[buf:buf+256]),m[off],tuple(m.writes),c.processorCycles-start))
            max_steps=max(max_steps,steps)
        assert outputs[0]==outputs[1],(n,h,y,p,queue,outputs[0][:5],outputs[1][:5])
        count+=1;cycles.add(outputs[0][-1]-outputs[1][-1])
    # Every caller-supported offset; arbitrary data and every native flag bit.
    for n in range(77):
        for seed in range(16):
            queue=[(i*73+seed*31)&255 for i in range(n+1)]
            case(queue,n,h=seed,y=(seed*17)&255,p=0x20|(seed*13&0xcf))
    hp=lambda h:[0x20,0x4b,4,0x24,0x48,0x50,h]
    for h in range(256):
        for y in [0,1,127,255]:
            case(hp(h)+[0],7,h,y)
            case(hp(h)+[0x20,0x60,1,9,0],11,h,y)
            case(hp(h)+[0x20,0x4b,4,0x24,0x48,0x50,h,0],14,h,y)
            case(hp(h)+[0x20,0x4c,1,9,0],11,h,y)
            case([0x24,0x20,1,9]+hp(h)+[0],11,h,y)
    # Headers/count flags/terminal aliases, including conservative fallbacks.
    for header in range(256):
        for length in range(256):
            case([header,0x4b,length,0x24,0x48,0x50,3,0],7)
    assert 0xaac6 in seen_old and 0xaacb in seen_old
    assert 0xaac6 in seen_new and 0xaaca in seen_new
    result=dict(passed=True,CPU_only=True,ROM_written=False,Mesen_run=False,
        parent_SHA256=PIN,origin=0xa98a,old_bytes=338,new_bytes=336,new_end=0xaada,
        recovered_half_open=[0xaada,0xaadc],source_funded=True,
        old_SHA256=sha(old),new_SHA256=sha(new),cases=count,maximum_instructions=max_steps,
        cycles_difference=sorted(cycles),full_AXYP_SP_queue_offset_and_all_writes_exact=True,
        branch_lemmas=[
            'AAC4 BEQ RestoreAppend is not taken before old AAC6 JMP Suppress; Z=0, so replacement BNE always takes.',
            'Old AAC9 LDY0 setsZ=1 before old AACB JMP Finished; replacement BEQ always takes.'],
        external_direct_consumers=hits,external_internal_label_consumers=[],
        fixed_following_PnFastDrawRecord=0xab00,
        source_recipe='compact_chip_hud_for_mini_1103_v1.transform(source first CdQueueHud proc); assemble atA98A with current four RAM/native symbols.',
        proposed_patch=dict(bank=79,CPU=0xa98a,old_hex=old.hex(),new_hex=new.hex()),
        bindings={p.relative_to(R).as_posix():sha(p.read_bytes()) for p in [Path(__file__),SRC,PARENT,R/'src/chip_dale_health.s',O/'chip-hud-reference.bin',O/'chip-hud-fast.s',O/'chip-hud-fast.bin']})
    (O/'proof.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['bindings','proposed_patch']}),flush=True)


if __name__=='__main__':main()
