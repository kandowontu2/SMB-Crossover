"""Compare real linked Samus audio before/after the C-bank relocation."""
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from check_tmnt_render_oa import load,Memory,address
from verify_native_relocation import NesMPU


def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--baseline',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    old,new=load(a.baseline),load(a.rom)
    def labels(p):return {q[2]:q[1]for line in p.with_suffix('.lbl').read_text().splitlines()if len(q:=line.split())==3}
    before,after=labels(a.baseline),labels(a.rom)
    text=(a.baseline.with_suffix('.dbg').read_text() if a.baseline.with_suffix('.dbg').exists()
          else gzip.decompress(a.baseline.with_suffix('.dbg.gz').read_bytes()).decode())
    scopes={};symbols=[]
    for line in text.splitlines():
        if not line.startswith(('scope\t','sym\t')):continue
        z=dict(q.split('=',1)for q in line.split('\t',1)[1].split(',')if '='in q)
        if line.startswith('scope\t'):scopes[z['id']]=z
        else:symbols.append(z)
    private={(q['name'].strip('"'),int(q['val'],0))for q in symbols
             if 'val'in q and scopes.get(q.get('scope'),{}).get('name')=='"SamusAudioUpdate"'}
    moved={n:[v,after.get(n)]for n,v in before.items()if after.get(n)!=v}
    # ld65's flat label file merges repeated local names. Only this moved
    # procedure's proven private labels may differ; every other label is stable.
    assert all((n[1:],int(v[0],16))in private for n,v in moved.items()),moved
    stats={};count=0
    for stream in range(8):
        contexts=[]
        for b in (old,new):
            m=Memory(b);c=NesMPU(memory=m)
            def put(n,v,m=m,b=b):m[address(b,n)]=v&255
            m.page(1,0);m.page(2,13)
            for n,v in [('SelectedCharacter',2),('OperMode',1),('CurrentBank',128),('CurrentBankC',141),('BankShadow',0x47)]:
                if n in b['syms']:put(n,v)
            for i in range(12):m[0xe0+i]=(stream*53+i*17)&255
            contexts.append((b,m,c,put))
        def call(name,number):
            nonlocal count
            rows=[];cycles=[]
            for b,m,c,put in contexts:
                m[0x1fe]=0xff;m[0x1ff]=0x7e;m.writes=[]
                c.a=number&255;c.x=(number*17)&255;c.y=(number*31)&255;c.p=(number*59)&255;c.sp=0xfd
                c.pc=address(b,name);c.processorCycles=0
                for _ in range(20000):
                    if c.pc==0x7f00:break
                    c.step()
                else:raise AssertionError(('CPU timeout',name,stream,number,hex(c.pc),m.banks))
                hardware=[(at,v)for at,v in m.writes if 0x4000<=at<=0x4017 or 0x5000<=at<=0x5015]
                # Only the discarded CPU stack is excluded. Lower stack-page
                # SMC state, all ordinary RAM, all mapper shadows and APU writes match.
                ram=bytes(m[:0x1a0])+bytes(m[0x200:0x8000])
                rows.append((c.a,c.x,c.y,c.p,c.sp,ram,hardware,list(m.banks)));cycles.append(c.processorCycles)
            assert rows[0]==rows[1],dict(entry=name,stream=stream,case=number,registers=[r[:5]for r in rows],
                hardware=[r[-2]for r in rows],banks=[r[-1]for r in rows],
                RAM_differences=[(hex(i),contexts[0][1][i],contexts[1][1][i])for i in range(0x8000)
                    if not 0x1a0<=i<0x200 and contexts[0][1][i]!=contexts[1][1][i]][:16])
            z=stats.setdefault(name,dict(cases=0,min_cycle_delta=10000,max_cycle_delta=-10000))
            z['cases']+=1;z['min_cycle_delta']=min(z['min_cycle_delta'],cycles[1]-cycles[0]);z['max_cycle_delta']=max(z['max_cycle_delta'],cycles[1]-cycles[0]);count+=1
        call('SamusAudioInit',stream)
        for tick in range(2000):
            for b,m,c,put in contexts:
                put('FrameCounter',tick);put('PlayerStatus',stream%3)
                put('AreaMusicQueue',(1,2,4,8,16,32,64,128)[stream]if tick in (0,768,1408)else 0)
                put('EventMusicQueue',(1,2,4,8,16,32,64,128)[stream]if tick in (512,1024)else 0)
                active=(tick//128)&1
                put('Square1SoundQueue',(1<<((tick+stream)%8))if active and tick%5==0 else 0)
                put('SmSfx',(1<<((tick//3+stream)%7))if active and tick%3==0 else 0)
                put('GamePauseStatus',1 if 1600<=tick<1604 else 0)
                put('OperMode',0 if tick==1800 else 1)
            call('SamusAudioUpdate',stream*2000+tick)
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    q=dict(passed=True,ROM_sha256=sha(a.rom),baseline_ROM_sha256=sha(a.baseline),cases=count,stats=stats,
           all_preexisting_global_labels_unchanged=True,relocated_procedure_private_flat_labels=moved,
           scope='Eight coherent2000-update Samus music/effect/pause/mute/restart streams on actual linked binaries; exact A/X/Y/allP/SP, RAM outside discarded CPU stack, final physical banks and ordered hardware audio writes. No interrupts, waveform, DMC playback or controller traversal claim.',
           checker_sha256=sha(Path(__file__)),dependencies={str(p):sha(p)for p in [Path(__file__).with_name('check_tmnt_render_oa.py'),Path(__file__).with_name('verify_native_relocation.py')]})
    (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
