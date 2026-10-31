"""Run original CPU/NMI and relocated Thomas source under the same untimed bus."""
from pathlib import Path
import argparse,hashlib,itertools,json,sys
R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
import thomas_original_cpu_1031_v1 as t

sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
dump=lambda p,v:Path(p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,default=R/'build/thomas-original-source-v2');ap.add_argument('--output',type=Path,default=R/'build/thomas-original-controls-v1');a=ap.parse_args()
    a.source=a.source.resolve();a.output=a.output.resolve();assert not a.output.exists();a.output.mkdir(parents=True)
    image=(a.source/'component.bin').read_bytes();syms=t.labels(a.source/'component.lbl')
    # Actual relocated instruction/data locations come from linked public/local labels.
    mapping={int(n[3:],16):v for n,v in syms.items()if n.startswith('Th_')}
    assert mapping[0xa482]==0x6000 and mapping[0xa936-1]<0x6800
    inverse={v:k for k,v in mapping.items()}
    inverse.update({v:int(n[7:],16)for n,v in syms.items()if n.startswith('ThData_')})
    def source_machine(ram=None):
        c=t.machine();list.__setitem__(c.memory,slice(0x6000,0x7000),image)
        if ram is not None:list.__setitem__(c.memory,slice(0,2048),ram)
        return c
    def pointer_ram(c):
        data=bytearray(c.memory[:2048])
        # These are the original core's genuine two ephemeral indirect pointers.
        # Normalize only linked pointer addresses; retain all other scratch/application bytes.
        for p in [0,2]:
            target=data[p]|data[p+1]<<8
            if target in inverse:data[p:p+2]=inverse[target].to_bytes(2,'little')
        return data
    def app(c):
        d=pointer_ram(c);return bytes(d[:256]+d[512:])
    def writes(c):
        # Pointer low/high stores have different linked values. Keep ordering and all
        # other RAM writes, including actual timer/action/position/audio queues.
        return [(p,None if p<4 else v)for p,v in c.memory.writes if not 0x100<=p<0x200]
    def complete_frame(c,pad=0,relocated=False,observe=None):
        c.memory.pad=[pad,0];c.memory.writes=[];c.memory.apu=[];c.memory.ppuwrites=[]
        c.nmi();n=0;used={};queues=[]
        while c.pc!=0x82d3:
            if c.pc in mapping:
                used[c.pc]=used.get(c.pc,0)+1
                if observe is not None and c.pc==0xa482:observe.append(bytes(c.memory[:2048]))
                if relocated:c.pc=mapping[c.pc]
            if c.pc==0xf831:queues.append(list(c.memory[0xfb:0x100]))
            c.step();n+=1;assert n<120000,hex(c.pc)
        return used,queues
    # Native reset/Start/parser is executed from the donor without synthetic ready/player state.
    old=t.boot();new=source_machine();t.until_idle(new)
    snapshots=[];events=[];counts={};maxdiff=[0,0];frames=0;actions=set();poses=set()
    segments=[('cold/start',650,lambda i:0x10 if 120<=i<125 else 0),
       ('walk-right',50,lambda i:1),('release',16,lambda i:0),('walk-left',50,lambda i:2),
       ('jump',65,lambda i:8 if i<12 else 0),('crouch',24,lambda i:4),
       ('standing-punch',42,lambda i:0x40 if 2<=i<8 else 0),
       ('standing-kick',42,lambda i:0x80 if 2<=i<8 else 0),
       ('crouching-punch',42,lambda i:4|(0x40 if 2<=i<8 else 0)),
       ('crouching-kick',42,lambda i:4|(0x80 if 2<=i<8 else 0)),
       ('air-punch',65,lambda i:(8 if i<3 else 0)|(0x40 if 8<=i<12 else 0)),
       ('air-kick',65,lambda i:(8 if i<3 else 0)|(0x80 if 8<=i<12 else 0))]
    csv=['frame,policy,pad,mode,scene,state,counter,xlo,xhi,y,hp,pose,audio_queues']
    for name,length,policy in segments:
        for f in range(length):
            pad=policy(f);before=old.processorCycles
            u,q=complete_frame(old,pad,observe=snapshots);oldcost=old.processorCycles-before
            before=new.processorCycles;complete_frame(new,pad,True);newcost=new.processorCycles-before
            assert app(old)==app(new),(name,f,'RAM',[(p,old.memory[p],new.memory[p])for p in range(2048)if not 256<=p<512 and pointer_ram(old)[p]!=pointer_ram(new)[p]][:12])
            assert (old.a,old.x,old.y,old.p,old.sp)==(new.a,new.x,new.y,new.p,new.sp),(name,f,'registers')
            assert writes(old)==writes(new),(name,f,'ordered native writes')
            assert old.memory.ppu==new.memory.ppu and old.memory.oam==new.memory.oam,(name,f,'PPU/OAM')
            assert old.memory.apu==new.memory.apu,(name,f,'ordered APU events')
            diff=newcost-oldcost;maxdiff=[min(maxdiff[0],diff),max(maxdiff[1],diff)]
            for k,v in u.items():counts[f'{k:04X}']=counts.get(f'{k:04X}',0)+v
            if old.memory[0x51]==2:
                actions.add(old.memory[0x69]&0x3e);poses.add(old.memory[0x52])
            if any(any(s)for s in q):events.append(dict(frame=frames,policy=name,queues=q,apu_writes=old.memory.apu))
            csv.append(','.join(map(str,[frames,name,pad,old.memory[0x50],old.memory[0x51],old.memory[0x69],old.memory[0x68],old.memory[0xd4],old.memory[0xe5],old.memory[0xb6],old.memory[0x4a6],old.memory[0x52],json.dumps(q,separators=(':',';'))])))
            frames+=1
    assert counts.get('A482',0)>100 and counts.get('A696',0)>100 and counts.get('A826',0)>100
    # Select distinct real states reached at the genuine donor input boundary.
    states={}
    for ram in snapshots:
        if ram[0x51]==2 and ram[0x4a6]<128:
            key=(ram[0x69]&0x3f,ram[0x68],ram[0x67])
            states.setdefault(key,ram)
    assert states, 'Native parser must have reached real gameplay'
    chosen=list(states.values())[::max(1,len(states)//12)][:12]
    flags=[0x20|(i&3)|((i&4)<<0)|((i&8)<<0)|((i&16)<<2)|((i&32)<<2)for i in range(64)]
    cases=0;entries=['ThomasInput','ThomasMove','ThomasAnimate','ThomasSelectPose']
    starts={'ThomasInput':0xa482,'ThomasMove':0xa696,'ThomasAnimate':0xa826,'ThomasSelectPose':0xa8eb}
    for index,(ram,entry,p)in enumerate(itertools.product(chosen,entries,flags)):
        x=(index*37)&255;y=(index*83)&255;av=(index*19)&255
        c=t.machine();list.__setitem__(c.memory,slice(0,2048),ram);d=source_machine(ram)
        r1=t.run(c,starts[entry],av,x,y,p);r2=t.run(d,syms[entry],av,x,y,p)
        assert r1[:5]==r2[:5],(entry,index,r1,r2)
        assert app(c)==app(d)and writes(c)==writes(d),(entry,index,'application/ordered writes')
        assert c.memory.apu==d.memory.apu and c.memory.ppuwrites==d.memory.ppuwrites
        cases+=1
    for ram,pad,p in itertools.product(chosen[:4],range(256),[0x20,0xef]):
        c=t.machine();list.__setitem__(c.memory,slice(0,2048),ram);c.memory[0x6a]=pad;d=source_machine(bytes(c.memory[:2048]))
        r1=t.run(c,0xa482,0x57,0x81,0x33,p);r2=t.run(d,syms['ThomasInput'],0x57,0x81,0x33,p)
        assert r1[:5]==r2[:5]and app(c)==app(d)and writes(c)==writes(d),('all raw input',pad,p)
        cases+=1
    (a.output/'native-cpu-trace.csv').write_text('\n'.join(csv)+'\n',encoding='utf-8')
    dump(a.output/'audio-events.json',events)
    # Real source-state corpus is small, reversible evidence for later adapters.
    (a.output/'native-input-states.bin').write_bytes(b''.join(chosen))
    report=dict(result='PASS',scope='Isolated original reset/Start/parser/full NMI CPU differential; untimed PPU-ready service, not native emulator/raster/host proof',
      donor_sha256=t.EXPECTED,source_stage_sha256=sha(a.source/'source-stage.json'),component_sha256=sha(a.source/'component.bin'),
      full_donor_frames=frames,relocated_core_entry_counts=counts,real_input_states=len(states),state_corpus=len(chosen),
      allflags_and_rawinput_pairs=cases,legal_actions=sorted(actions),observed_pose_commands=sorted(poses),
      compared='A/X/Y/P/SP; all2KB applicationRAM except deadstack; ordered nativewrites incl audioqueues; complete simulated PPU/OAM; exact ordered original APU events',
      normalization='Only genuine indirect pointer words00/02 rebound by linked address; ordered00..03 write values masked, addresses/order retained. No gameplay fields normalized.',
      source_frame_cpu_delta=maxdiff,
      original_audio_driver='F831 executed unchanged in both. Action event queues and resulting APU event streams are proven; no host audio port claimed.',
      exclusions=['No actual PPU deadlines/sprite-zero/raster timing','No source host terrain/camera/contacts/lifecycle integration','Original damage/grab/enemy/audio dependencies remain donor code'],
      bindings={str(p.resolve()):sha(p)for p in [Path(__file__),Path(t.__file__),a.source/'source-stage.json',a.source/'component.bin',a.source/'component.lbl',a.output/'native-cpu-trace.csv',a.output/'audio-events.json',a.output/'native-input-states.bin']})
    dump(a.output/'controls.json',report)
    print(json.dumps(dict(result='PASS',frames=frames,pairs=cases,source_stage=report['source_stage_sha256'],controls_sha256=sha(a.output/'controls.json'))))

if __name__=='__main__':main()
