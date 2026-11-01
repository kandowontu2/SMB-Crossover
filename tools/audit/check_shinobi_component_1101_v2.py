"""Execute original and relocated Shinobi instructions against equal host leaves."""
from pathlib import Path
import argparse, collections, hashlib, json, re, sys
from py65.devices.mpu6502 import MPU
R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/audit'))
import recover_shinobi_component_1101_v2 as S


def labels(p):
    return {name.lstrip('.'):int(a,16) for a,name in re.findall(r'^al ([0-9A-Fa-f]+) (\S+)',p.read_text(),re.M)}


class Engine:
    def __init__(self,out,portable):
        self.portable=portable;self.offset=0x6000 if portable else 0
        self.m=S.original_memory(S.ROM.read_bytes())
        self.labels=labels(out/('portable.lbl' if portable else 'original.lbl'))
        self.reverse={value:int(name[3:],16) for name,value in self.labels.items()
                      if re.fullmatch('Sh_[0-9A-F]{4}',name)}
        if portable:self.m.memory[0x9000:0xd000]=(out/'portable.bin').read_bytes()
        self.calls=[];self.cover=set();self.steps=0
        self.callback=set(int(x,16) for x in json.loads((out/'assembly.json').read_text())['callbacks'])
        self.m.memory[0x5ffe]=0x00

    def addr(self,a):return a if a<4 else a+self.offset
    def get(self,a):return self.m.memory[self.addr(a)]
    def put(self,a,v):self.m.memory[self.addr(a)]=v&255
    def fixture(self):
        for a in range(0x800):self.put(a,0)
        for a in range(0x200,0x300):self.put(a,0xf8 if a%4==0 else 0)
        for a,v in {0x379:0x80,0x38f:0xe0,0x413:0,0x541:4,0x2d:0x90,
                    0x53b:0,0x42:0,0x539:6,0x53a:6}.items():self.put(a,v)
        self.run(0x83ab)
        self.calls.clear()

    def leaf(self,pc):
        m=self.m;self.calls.append([pc,m.a,m.x,m.y])
        if pc==0xd2a4:
            # Declared synthetic flat floor. $00 is the original tile result.
            result=1 if self.get(0x38f+m.x)>=0xe0 else 0xff
            m.a=result;self.put(0,result)
        elif pc in [0xd213,0xd225,0xd25f,0xd1bc,0xd3ad]:m.a=0;self.put(0,0)
        elif pc in [0x8eed,0x8ec1]:self.put(0,0xff);self.put(1,0xff)
        elif pc in [0xfb33,0xfb3f]:
            # No viewport motion in these source-motion fixtures.
            self.put(0x54,0 if pc==0xfb33 else 1)
        elif pc==0xdaf7:m.a=0
        # Other leaves are deliberate no-op audio/UI/scene/enemy services.
        m.p=(m.p&~0x82)|(0x02 if m.a==0 else 0)|(m.a&0x80)
        m.pc=(m.stPopWord()+1)&65535

    def run(self,original,a=None,x=None,y=None):
        m=self.m;m.pc=self.labels[f'Sh_{original:04X}'] if self.portable else original
        if a is not None:m.a=a
        if x is not None:m.x=x
        if y is not None:m.y=y
        m.sp=0xef;m.stPushWord(0x5ffd)
        for n in range(100000):
            if m.pc==0x5ffe:break
            if m.pc in self.callback:self.leaf(m.pc);continue
            self.cover.add(m.pc);self.steps+=1;m.step()
        else:raise AssertionError(('non-return',self.portable,hex(original),hex(m.pc)))
        assert m.sp==0xef,('stack imbalance',self.portable,hex(original),m.sp)
        return m.a,m.x,m.y,m.p

    def state(self):return [self.get(a) for a in range(0x800)]


def normalize(source,candidate,b):
    # Data/SMC pointers carry source code addresses and must refer to the same
    # relocated labels, rather than coincidentally contain the same byte value.
    b=list(b)
    pairs=[(0,1),(0x17b,0x17c)]
    pairs += [(0x43f+i,0x44a+i) for i in range(11)]
    reverse=candidate.reverse
    for lo,hi in pairs:
        value=b[lo]+256*b[hi]
        if value in reverse:
            original=reverse[value];b[lo]=original&255;b[hi]=original>>8
        elif hi==1 and 0x6300<=value<=0x6531:
            original=value-0x6000;b[lo]=original&255;b[hi]=original>>8
    return b


def check(out):
    assembly=json.loads((out/'assembly.json').read_text())
    for p,h in assembly['bindings'].items():assert S.sha(p)==h,p
    stats=collections.Counter();coverage=[set(),set()];digest=hashlib.sha256();apex=[];weapon_cases=[];art=[]
    max_steps=[0,0]
    def pair():
        a,b=Engine(out,False),Engine(out,True);a.fixture();b.fixture();return a,b
    def compare(a,b,tag):
        x=a.state();y=normalize(a,b,b.state())
        # Hardware CPU stack is private in each engine. Original $017b/c are
        # game-owned indirect dispatch scratch, so retain those two fields.
        diff=[(i,x[i],y[i]) for i in range(0x800) if not(0x100<=i<0x200 and i not in [0x17b,0x17c]) and x[i]!=y[i]]
        assert not diff,(tag,[(hex(i),u,v) for i,u,v in diff[:12]])
        assert a.calls==b.calls,(tag,'callback differential',a.calls,b.calls)
        assert (a.m.a,a.m.x,a.m.y,a.m.p)==(b.m.a,b.m.x,b.m.y,b.m.p),(tag,'return AXYP',
            (a.m.a,a.m.x,a.m.y,a.m.p),(b.m.a,b.m.x,b.m.y,b.m.p))
        digest.update(bytes(x[:0x100])+bytes(x[0x200:]));stats[tag.split('/')[0]]+=1
        for i,e in enumerate([a,b]):coverage[i]|=e.cover;max_steps[i]=max(max_steps[i],e.steps)
    # Actual source frame order: state handler, movement integration, renderer.
    for name,held,edge,frames in [('idle',0,0,80),('right',0x80,0,100),('left',0x40,0,100),
        ('jump',0x81,1,100),('verticaljump',1,1,100),('crouch',0x20,0,40),
        ('crouchjump',0x21,1,100),('throw',2,2,60),('crouchthrow',0x22,2,60)]:
        for facing in [0,4]:
            a,b=pair();minimum=0xe0
            for e in [a,b]:e.put(0x363,facing)
            previous=0
            for f in range(frames):
                value=held if f<35 or name in ['right','left'] else 0
                for e in [a,b]:
                    e.put(0x31,value);e.put(0x3a,(value^previous)&value);e.put(0x541,4)
                    state=e.get(0x413);assert state<19,(name,f,state)
                    e.run(assembly['original_player_states'][state],x=0)
                    e.run(0xa196,x=0);e.run(0x83fc,x=0)
                previous=value;minimum=min(minimum,a.get(0x38f));compare(a,b,'motion/'+name)
            if 'jump' in name:apex.append(dict(case=name,facing=facing,rise=0xe0-minimum))
    # All real dispatch roots: no arbitrary nonexistent pose/state values.
    for state,root in enumerate(assembly['original_player_states']):
        for face in [0,4]:
            a,b=pair()
            for e in [a,b]:
                e.put(0x413,state);e.put(0x363,face);e.put(0x358,2);e.put(0x408,2)
                e.put(0x545,0x40);e.put(0x550,0);e.put(0x751,0)
                for j in range(5):e.put(0x738+j,0xff)
                e.put(0x738,0);e.run(root,x=0)
            compare(a,b,'states/'+str(state))
    for index,root in enumerate(assembly['magic_targets']):
        a,b=pair()
        for e in [a,b]:e.run(root,x=0)
        compare(a,b,'magic/'+str(index))
    # Source range checks select small throwing star, upgraded star, horizontal
    # blade/fire variants from the real four8-byte weapon descriptors.
    for power in range(4):
        for crouch in [0,1,2]:
            for face in [0,4]:
                a,b=pair()
                for e in [a,b]:
                    e.put(0x42,power);e.put(0x363,face);e.run(0xc880,a=crouch,x=0)
                compare(a,b,'weapon-spawn/'+str(power))
                initial=[a.get(0x481+1),a.get(0x3a5+1),a.get(0x3d1+1),a.get(0x300+1),a.get(0x38f+1)]
                for f in range(30):
                    for e in [a,b]:e.put(0x541,4);e.run(0xc9da)
                    compare(a,b,'weapon-motion/'+str(power))
                weapon_cases.append(dict(power=power,crouch=crouch,facing=face,initial=initial))
    # Original standing/walk/jump/crouch/attack/magic/melee pose groups. Every
    # renderer output is compared byte-for-byte after relocation, both facings.
    poses=S.POSES
    for pose in poses:
        for face in [0,4]:
            a,b=pair()
            for e in [a,b]:e.put(0x300,pose);e.put(0x363,face);e.run(0x83ab,x=0)
            count=a.get(0x321)
            for frame in range(count):
                for e in [a,b]:e.put(0x30b,frame);e.put(0x541,4);e.run(0x83fc,x=0)
                compare(a,b,'graphics/'+str(pose))
                art.append(dict(pose=pose,frame=frame,facing=face,OAM=a.state()[0x204:a.get(0x541)+0x200]))
    intro=(out/'intro-reference.bin').read_bytes()
    idle=next(x for x in art if x['pose']==0 and x['frame']==0 and x['facing']==0)
    assert bytes(idle['OAM'])==intro[18:18+len(idle['OAM'])], 'Original intro/body packet disagreement'
    chrdata=(out/'source-body.chr').read_bytes()
    assert chrdata==intro[270:270+4096], 'Original displayed body CHR disagreement'
    report=dict(passed=True,source_CPU=True,native=False,installed=False,donor_sha256=S.EXPECTED,
        case_counts=dict(stats),differential_pairs=sum(stats.values()),
        executed_instruction_coverage=[len(c) for c in coverage],
        code_end=max(v for k,v in labels(out/'portable.lbl').items() if k.startswith('Sh_')),
        maximum_cumulative_fixture_instructions=max_steps,trace_sha256=digest.hexdigest(),
        jump_fixtures=apex,weapon_cases=weapon_cases,
        source_pose_frames=len(art),
        return_AXYP_compared=True,original_intro_idle_OAM_exact=True,
        original_displayed_body_CHR_exact=True,
        state_fields=dict(held='31: Right80 Left40 Down20 Up10 Select04 Start08 B02 A01',fresh='3A',
            x='0379/0384',feet_y='038F/039A',state='0413',pose='0300',frame='030B',
            facing='0363 bit04',motion_flags='03FD right1 left2 up4 down8',weapon_upgrade='0042',
            magic_inventory='0738..073C; FF empty; six native magic indices',
            magic_request='0745/0746 and held03',magic_timer='054C/054D'),
        callbacks=dict(terrain='Synthetic flat floor atE0; empty sides/ceiling, not SMB collision',
            viewport='No-scroll callback leaves, not SMB scrolling',
            enemy='No-enemy distance leaves; collision kill/melee leaves stubbed',
            audio_UI_scene='No-op callbacks; authentic source event requests retained'),
        scope='Full RAM/output/callback differential for declared fixtures; code/data address fields normalized to their relocated labels. Stack bytes excluded except game indirect pointer017B/C. No full-game or native-host evidence.',
        bindings={str(p.resolve()):S.sha(p) for p in [Path(__file__),out/'assembly.json',out/'portable.bin',out/'original.bin']})
    S.save(out/'CPU-controls.json',report);S.save(out/'pose-packets.json',dict(source=True,native=False,poses=art))
    print(json.dumps({k:v for k,v in report.items() if k not in ['bindings','weapon_cases','state_fields']}))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=R/'build/shinobi-component-1101-v2')
    check(p.parse_args().output.resolve())
