"""Original1.21 action chains vs port with explicit source geometry boundaries.

No emulator, invented Metroid room image, shared source edit or native claim.
The typed rectangle world supplies declared probe/pixel/support callbacks.
"""
from pathlib import Path
from functools import lru_cache
import argparse,hashlib,itertools,json,re,subprocess,sys
from py65.devices.mpu6502 import MPU
import rogue_dawn_map_v1 as ref
import rogue_dawn_weapons_controls_v1 as weapons
import prepare_rogue_dawn_art_v1 as art
import prepare_rogue_dawn_control_v1 as recipe
R=Path(__file__).resolve().parents[1]
P={s:t for s,t in weapons.P.items()if not 0x317<=s<=0x31f};P.update(recipe.EXTRA)
CALLS={0xe7a2:'RdHostProbeUp',0xe7ad:'RdHostProbeDown',0xe880:'RdHostProbeRight',0xe88b:'RdHostProbeLeft',
  0xe457:'RdHostMoveUp',0xe4a3:'RdHostMoveDown',0xe626:'RdHostMoveLeft',0xe668:'RdHostMoveRight',
  0xd976:'RdHostFindSupport',0xe8be:'RdHostStagePosition',0xfd8f:'RdHostOffsetPosition',0xd638:'RdHostCommitPosition',
  0xb119:'RdHostLowHealthSound',0xb11c:'RdHostHealthSound',0xde4a:'RdHostDrawPlayer',0xd306:'RdHostSpawnProjectile',
  0xd3a8:'RdHostDoor',0xd423:'RdHostElevator'}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def symbols(p):
    return {z[2]:int(z[1],16)for l in p.read_text().splitlines()if(z:=re.match(r'al ([0-9a-fA-F]+) \.(\S+)',l))}

def build(folder):
    folder.mkdir(exist_ok=True,parents=True);text=recipe.generate(ref.ROM.read_bytes());assert (R/'src/rogue_dawn_control.s').read_text()==text
    names=sorted(set(re.findall(r'RdHost\w+',text)));callbacks={n:0x9000+3*i for i,n in enumerate(names)}
    wrapper=''.join(f'{n}=${at:04x}\n'for n,at in callbacks.items())+(R/'build/rogue-dawn-art-v1/render.s').read_text()+'.include "rogue_dawn_control.s"\n'
    (folder/'control.s').write_text(wrapper)
    (folder/'control.cfg').write_text('MEMORY { H:start=$AE00,size=$200,bank=124,file="'+str((folder/'aux.bin').resolve()).replace('\\','/')+'"; K:start=$B000,size=$1000,bank=124,file=%O; A:start=$D300,size=$D00,bank=94,file="'+str((folder/'art.bin').resolve()).replace('\\','/')+'"; }\nSEGMENTS { ROGUE_DAWN_CORE:load=K,type=ro; ROGUE_DAWN_ART:load=A,type=ro; ROGUE_DAWN_CONTROL_AUX:load=H,type=ro; }\n')
    cc=R/'tools/Windows/cc65/bin'
    for cmd in [[str(cc/'ca65.exe'),'-g','-I',str(R/'src'),str(folder/'control.s'),'-o',str(folder/'control.o')],
      [str(cc/'ld65.exe'),'-C',str(folder/'control.cfg'),'-o',str(folder/'control.bin'),'-Ln',str(folder/'control.lbl'),'--dbgfile',str(folder/'control.dbg'),str(folder/'control.o')]]:subprocess.run(cmd,check=True)
    code=(folder/'control.bin').read_bytes();aux=(folder/'aux.bin').read_bytes();data=(folder/'art.bin').read_bytes();labels=symbols(folder/'control.lbl')
    assert code[:2293]==(R/'build/rogue-dawn-art-v1/render.bin').read_bytes()
    assert len(code)<=4096 and len(aux)<=512
    return code,aux,data,labels,callbacks

class World:
    def __init__(self,floor=160,ceiling=32,left=32,right=224,support=False):self.floor,self.ceiling,self.left,self.right,self.support=floor,ceiling,left,right,support
    def __repr__(self):return str(vars(self))

class Runner:
    def __init__(self,raw,compiled,ported,world,state):
        self.ported,self.world,self.events=ported,world,[];self.owned=[];code,aux,data,self.labels,self.callbacks=compiled
        self.m=art.Memory(bytes(65536)if ported else ref.cpu_image(raw,lower_bank=2))
        if ported:self.m[0xb000:0xb000+len(code)]=code;self.m[0xae00:0xae00+len(aux)]=aux;self.m[0xd300:0xd300+len(data)]=data
        for k,v in state.items():self.set(k,v)
        self.staged=None;self.raw=raw
    def get(self,s):return self.m[P[s]if self.ported else s]
    def set(self,s,v):self.m[P[s]if self.ported else s]=v&255
    def ret(self,c):c.pc=(c.stPopWord()+1)&65535
    def source_flags(self,c,a=None):
        if a is not None:c.a=a&255;c.FlagsNZ(c.a)
    def callback(self,c,n):
        x,y,rx,ry=[self.get(s)for s in [0x30e,0x30d,0x302,0x301]];w=self.world
        self.events.append(dict(kind=n,action=self.get(0x300),frame=self.get(0x303),x=x,y=y,VY=self.get(0x308)))
        if n.startswith('RdHostProbe'):
            blocked={'Up':y-ry<=w.ceiling,'Down':y+ry>=w.floor,'Left':x-rx<=w.left,'Right':x+rx>=w.right}[n[11:]]
            c.p=(c.p&~1)|int(not blocked)
        elif n.startswith('RdHostMove'):
            axis=n[10:];blocked={'Up':y-ry<=w.ceiling,'Down':y+ry>=w.floor,'Left':x-rx<=w.left,'Right':x+rx>=w.right}[axis]
            if not blocked:
                if axis in ['Up','Down']:self.set(0x30d,y+(-1 if axis=='Up'else 1))
                else:self.set(0x30e,x+(-1 if axis=='Left'else 1))
                if axis=='Up':self.set(0x30f,self.get(0x30f)+1)
            else:self.set(0x58,0)
            c.p=(c.p&~1)|int(not blocked)
        elif n=='RdHostFindSupport':self.set(0x307,0);self.set(0x7d,int(w.support))
        elif n=='RdHostEnvironment':pass # owned source780E projection supplied by the scene boundary.
        elif n in ['RdHostRelativeX','RdHostRelativeY']:
            self.source_flags(c,x if n.endswith('X')else y);c.p|=1;c.opSBC(lambda:0x9ff0) # declared flat zero-scroll CPU arena.
        elif n=='RdHostStagePosition':
            self.staged=[self.get(0x30c+c.x),self.get(0x30d+c.x),self.get(0x30e+c.x)];self.source_flags(c,self.staged[2])
            if not self.ported:self.m[0x0b],self.m[0x08],self.m[0x09]=self.staged
        elif n=='RdHostOffsetPosition':
            assert self.staged is not None
            self.staged[1]=(self.staged[1]+signed(self.get(4)))&255;self.staged[2]=(self.staged[2]+signed(self.get(5)))&255
        elif n=='RdHostCommitPosition':
            for off,v in zip([0xc,0xd,0xe],self.staged):self.set(0x300+c.x+off,v)
            self.source_flags(c,self.staged[0]&1)
        elif n=='RdHostSpawnProjectile':
            slot=c.y;self.set(0x30d+slot,y+signed(self.get(4)));self.set(0x30e+slot,x+signed(self.get(5)));self.set(0x30c+slot,self.get(0x30c)&1);c.x=slot
            self.source_flags(c,self.get(0x30c)&1)
        elif n=='RdHostDrawPlayer':
            ry_,rx_,regs=native_draw(self.raw,self.get(0x303),self.get(0x4d),self.get(0x6b),self.get(0x300),y,x,c.p)
            self.set(0x301,ry_);self.set(0x302,rx_);c.a,c.x,c.y,c.p=regs
        elif n in ['RdHostLowHealthSound','RdHostHealthSound']:pass # sound bridge preserves complete caller AXYP.
        elif n=='RdHostDoorDirection':pass # scene/scroll owner intentionally outside player physics.
        elif n in ['RdHostDoor','RdHostElevator']:raise AssertionError('Scene-owned action cannot be silently treated as ordinary movement')
        else:raise AssertionError(n)
        self.ret(c)
    def step(self,pad,clock,pflags=0x30,entry=None):
        self.set(0x12,pad&~self.get(0x14));self.set(0x14,pad);self.set(0x16,0);self.set(0x2d,clock)
        start=self.labels[entry[1]if entry else'RdControlStep']if self.ported else entry[0]if entry else 0xcc0d
        c=MPU(memory=self.m,pc=start);c.sp=0xc0;c.p=pflags
        # Caller-live stack is above the entry SP; return/local stack below it
        # remains real 6502 storage rather than a broadly masked RAM region.
        self.m[0x1c1:0x200]=bytes((i*37+19)&255 for i in range(63))
        caller_stack=bytes(self.m[0x1c1:0x200]);c.stPushWord(0x5aff);low=c.sp;count=0
        self.m.writes.clear();self.m.reads.clear()
        inverse={v:k for k,v in self.callbacks.items()}
        owned={0xcfc3:'jump',0xcfbe:'aim-jump',0xd0b5:'morph',0xd0f1:'unmorph',0xda68:'wall-jump',0xa2ba:'spring-check',0xe2e8:'ground-contact'}
        portowned={self.labels[n]:tag for n,tag in [('RdStartJump','jump'),('RdControlUpJump','aim-jump'),('RdC_D0B5','morph'),('RdC_D0F1','unmorph'),('RdC_DA68','wall-jump'),('RdSpringAdmitted','spring-check'),('RdGroundCollisionResponse','ground-contact')]}
        for _ in range(100000):
            if c.pc==0x5b00:
                assert c.sp==0xc0
                assert bytes(self.m[0x1c1:0x200])==caller_stack,'Caller-live stack changed'
                allowed=(set(P.values())|set(range(0x5c35,0x5c38))|{0x5c3a,0x5c3b})if self.ported else set(P)|{0x0c,0x0d,0x69,0x6a,0x08,0x09,0x0b,0x51,0x52,0x6e,0x6f}
                assert all(k in allowed or 0x100<=k<0x200 for k in self.m.writes),('foreign-write',self.ported,[hex(k)for k in self.m.writes if k not in allowed and not 0x100<=k<0x200])
                assert not any(0x6000<=k<0x6800 for k in self.m.reads),'Accidental source room-memory read'
                return c,low,count
            if self.ported and c.pc in inverse:self.callback(c,inverse[c.pc]);continue
            marker=(portowned if self.ported else owned).get(c.pc)
            if marker:self.owned.append(marker)
            if not self.ported:
                if c.pc==0xdbe6:
                    self.events.append(dict(kind='RdHostEnvironment',action=self.get(0x300),frame=self.get(0x303),x=self.get(0x30e),y=self.get(0x30d),VY=self.get(0x308)))
                    c.pc=0xe2a9;continue # declared native environment-prefix boundary, then REAL native motion.
                if c.pc in [0xe2ac,0xe31d]:
                    self.events.append(dict(kind='RdHostRelativeY'if c.pc==0xe2ac else'RdHostRelativeX',action=self.get(0x300),frame=self.get(0x303),x=self.get(0x30e),y=self.get(0x30d),VY=self.get(0x308)))
                if c.pc==0xe37a:
                    # Execute the original vertical-admission owner; D976 is
                    # the explicit actor-support boundary below.
                    pass
                if c.pc==0xe1cb:c.stPushWord(0xd11d);c.pc=0xa2ad;continue # real physical61 Spring body, no fake room restore.
                if c.pc in CALLS:self.callback(c,CALLS[c.pc]);continue
            assert self.m[c.pc]!=0,('BRK',self.ported,hex(c.pc),self.get(0x300))
            c.step();low=min(low,c.sp);count+=1
        raise AssertionError(('timeout',self.ported,hex(c.pc)))

def signed(v):return v-256 if v&128 else v

@lru_cache(None)
def native_draw(raw,frame,face,color,action,y,x,p):
    m=art.Memory(ref.cpu_image(raw,lower_bank=2));m[0x4b]=0;m[0x55]=1;m[0x300]=action;m[0x303]=frame
    m[0x30d],m[0x30e]=y,x;m[0x49]=2;m[0x6b]=color;m[0x69b3]=0
    c=art.call(m,0xde4a,p=p)
    return m[0x301],m[0x302],(c.a,c.x,c.y,c.p)

def state(gear=0,action=0,x=128,y=144):
    return {0x6878:gear,0x780e:128,0x300:action,0x301:16,0x302:6,0x303:8,0x304:0,0x305:7,0x306:7,
      0x30c:1,0x30d:y,0x30e:x,0x4d:0,0x0106:0x99,0x0107:9,0x53:9}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=R/'build/rogue-dawn-control-v1/controls.json');a=p.parse_args()
    raw=ref.ROM.read_bytes();assert ref.digest(raw)==ref.EXPECTED;compiled=build(a.output.parent);rows=[];gates=[];screws=[];animations=[];damage=[]
    table=compiled[3]['RdControlMorphByteWindow']-0xb000
    assert compiled[0][table:table+256]==raw[16+62*8192+0xcc0:16+62*8192+0xdc0]
    campaigns=[('stand-run-release-reverse',0,[0]*3+[1]*35+[0]*8+[2]*35+[0]*8,World()),
      ('ordinary-jump-cut',0,[0]*2+[128]*4+[0]*55,World()),('run-jump-screw',8,[1]*12+[129]*25+[1]*35,World()),
      ('high-jump',2,[129]*40+[1]*45,World()),('aim-up-jump',0,[8]*4+[136]*22+[8]*35,World()),
      ('morph-spring-unmorph',0x11,[4]*3+[0]*4+[128]*4+[0]*20+[8]*2+[0]*35,World()),
      ('wall-right',4,[1]*28+[129]*35+[1]*12,World(right=160)),('wall-left',4,[2]*28+[130]*35+[2]*12,World(left=96)),
      ('morph-no-spring',1,[4]*3+[128]*8+[0]*20+[8]*2+[0]*10,World()),
      ('hurt-blink',0,[0]*55,World()),('death-animation',0,[0]*28,World()),
      ('stand-up-fire-fullpool',0,[64,0,72,8,64,0,64,0,0]*3,World()),
      ('run-jump-fire-order',192,[1]*8+[65,1,193]+[129]*12+[65,1,65,1,65,1],World()),
      ('morph-bomb-allocation',1,[4,0,64,0,64,0,64,0,64,0]*3,World())]
    for (name,gear,pads,world),flags in itertools.product(campaigns,[0x30,0x31,0x70,0x71]):
        start=state(gear)
        if name=='hurt-blink':start.update({0x30a:0x20,0x73:128})
        if name=='death-animation':start.update({0x300:7,0x305:0x32,0x306:0x32,0x0106:0,0x0107:0})
        n,q=Runner(raw,compiled,False,world,start),Runner(raw,compiled,True,world,start)
        costs=[];minimum_sp=0xc0
        for i,pad in enumerate(pads):
            if name=='hurt-blink'and i==1:n.set(0x30a,0);q.set(0x30a,0)
            c,lo,_=n.step(pad,i,flags);d,lp,_=q.step(pad,i,flags)
            costs.append([c.processorCycles,d.processorCycles]);minimum_sp=min(minimum_sp,lo,lp)
            differences=[(hex(s),n.get(s),q.get(s))for s in P if n.get(s)!=q.get(s)]
            assert not differences,(name,i,pad,differences)
            assert (c.a,c.x,c.y,c.p,c.sp)==(d.a,d.x,d.y,d.p,d.sp),(name,i,'AXYP',[(c.a,c.x,c.y,c.p,c.sp),(d.a,d.x,d.y,d.p,d.sp)])
        assert n.events==q.events,(name,'boundary-order',n.events[:8],q.events[:8])
        assert n.owned==q.owned
        rows.append(dict(name=name,flags=flags,updates=len(pads),gear=gear,world=vars(world),final_action=q.get(0x300),final_xy=[q.get(0x30e),q.get(0x30d)],boundary_events=len(q.events),source_owned_entries={k:q.owned.count(k)for k in sorted(set(q.owned))},minimum_SP=minimum_sp,internal_CPU_cycles_excluding_declared_boundaries=dict(source=sum(z[0]for z in costs),port=sum(z[1]for z in costs),per_update_delta=[min(z[1]-z[0]for z in costs),max(z[1]-z[0]for z in costs)])))
    for action,gear,down,cooldown,wall,fresh in itertools.product([1,2],[0,4,16],[0,4],[0,8],[False,True],[False,True]):
        start=state(gear,action,x=128,y=96);start.update({0x301:15,0x302:4,0x303:16,0x305:12,0x306:13,0x308:252,0x314:24,0x2a:cooldown})
        pad=down if down else 129;start[0x14]=0 if fresh else pad
        world=World(floor=224,right=132 if wall else 224)
        n,q=Runner(raw,compiled,False,world,start),Runner(raw,compiled,True,world,start)
        c,_,_=n.step(pad,0);d,_,_=q.step(pad,0)
        assert all(n.get(s)==q.get(s)for s in P)
        assert (c.a,c.x,c.y,c.p,c.sp)==(d.a,d.x,d.y,d.p,d.sp)
        assert n.events==q.events and n.owned==q.owned
        expected_morph=bool(fresh and down and gear&16 and(action==1 or not cooldown))
        assert ('morph'in q.owned)==expected_morph,(action,gear,pad,cooldown,wall,fresh,q.owned)
        expected_wall=bool(action==1 and not down and gear&4 and wall and fresh)
        assert ('wall-jump'in q.owned)==expected_wall,(action,gear,pad,cooldown,wall,fresh,q.owned)
        gates.append(dict(action=action,gear=gear,pad=pad,cooldown=cooldown,wall=wall,fresh=fresh,morph=expected_morph,wall_jump=expected_wall))
    for gear,support,fresh in itertools.product([0,16],[False,True],[False,True]):
        start=state(gear,3,y=152 if support else 100);start.update({0x301:8,0x303:27,0x305:22,0x306:22,0x14:0 if fresh else 128})
        n,q=Runner(raw,compiled,False,World(),start),Runner(raw,compiled,True,World(),start)
        c,_,_=n.step(128,0);d,_,_=q.step(128,0)
        assert all(n.get(s)==q.get(s)for s in P)and(c.a,c.x,c.y,c.p,c.sp)==(d.a,d.x,d.y,d.p,d.sp)
        launched=bool(gear&16 and support and fresh);assert bool(q.get(0x308)&128)==launched
        gates.append(dict(kind='actual-morph-Spring-support',gear=gear,support=support,fresh=fresh,launched=launched))
    for blocked in [False,True]:
        start=state(0,3,y=100);start.update({0x301:8,0x303:27,0x305:22,0x306:22})
        n,q=Runner(raw,compiled,False,World(ceiling=90 if blocked else 32),start),Runner(raw,compiled,True,World(ceiling=90 if blocked else 32),start)
        c,_,_=n.step(8,0);d,_,_=q.step(8,0)
        assert all(n.get(s)==q.get(s)for s in P)and(c.a,c.x,c.y,c.p,c.sp)==(d.a,d.x,d.y,d.p,d.sp)
        assert q.get(0x300)==(3 if blocked else 2)
        gates.append(dict(kind='unmorph-real-up-probe',blocked=blocked,action=q.get(0x300),y=q.get(0x30d)))
    for action,gear,reset,index,vy,flags in itertools.product(range(9),[0,8],[12,14,32],[11,12,13,15],[252,0,2],[0x30,0x71]):
        start=state(gear,action);start.update({0x305:reset,0x306:index,0x308:vy})
        n,q=Runner(raw,compiled,False,World(),start),Runner(raw,compiled,True,World(),start)
        c,_,_=n.step(0,0,flags,entry=(0xcd9c,'RdControlScrew'));d,_,_=q.step(0,0,flags,entry=(0xcd9c,'RdControlScrew'))
        assert all(n.get(s)==q.get(s)for s in P)and(c.a,c.x,c.y,c.p,c.sp)==(d.a,d.x,d.y,d.p,d.sp)
        screws.append([action,gear,reset,index,vy,flags,c.p&1])
    for reset,indices in [(7,[7,8,9]),(12,[12,13,14]),(22,[22,23,24]),(153,[153,154,155,156,157])]:
        for index,delay,flags in itertools.product(indices,[0,1,2,5],[0x30,0x31,0x70,0x71]):
            start=state();start.update({0x305:reset,0x306:index,0x304:delay,0x6b:0x81})
            n,q=Runner(raw,compiled,False,World(),start),Runner(raw,compiled,True,World(),start)
            c,_,_=n.step(0,0,flags,entry=(0xdb96,'RdControlAdvance'));d,_,_=q.step(0,0,flags,entry=(0xdb96,'RdControlAdvance'))
            assert all(n.get(s)==q.get(s)for s in P)and(c.a,c.x,c.y,c.p,c.sp)==(d.a,d.x,d.y,d.p,d.sp)
            animations.append([reset,index,delay,flags,q.get(0x303),q.get(0x304),q.get(0x306)])
    # Damage arithmetic remains a genuine source owner, not ordinary Samus
    # HP. Feed its actual computed BCD image/carry into the new post-damage
    # action continuation and compare the real native continuation exactly.
    for hp,hi,amount,suit in itertools.product([0x01,0x50,0x99],[0,9],[0x01,0x10,0x99],[0,32]):
        m=art.Memory(ref.cpu_image(raw,lower_bank=2));m[0x106]=hp;m[0x107]=hi;m[0x6e]=amount;m[0x6878]=suit
        c=MPU(memory=m,pc=0xce92);c.sp=0xc0;c.stPushWord(0x5aff)
        for _ in range(2000):
            if c.pc==0xceda:break
            c.step()
        else:raise AssertionError('Native damage did not reach genuine post-debit continuation')
        start={s:m[s]for s in P};start.update({0x6b:0,0x55:0})
        n,q=Runner(raw,compiled,False,World(),start),Runner(raw,compiled,True,World(),start)
        x,_,_=n.step(0,0,c.p,entry=(0xceda,'RdControlDamageComplete'));y,_,_=q.step(0,0,c.p,entry=(0xceda,'RdControlDamageComplete'))
        assert all(n.get(s)==q.get(s)for s in P)and(x.a,x.x,x.y,x.p,x.sp)==(y.a,y.x,y.y,y.p,y.sp)
        damage.append(dict(before_BCD=[hp,hi],native_damage_BCD=amount,suit=suit,source_after_BCD=[m[0x106],m[0x107]],actual_source_carry=c.p&1,action=q.get(0x300),native_and_port_continuation_exact=True))
    q=Runner(raw,compiled,True,World(),state());q.set(0x69b3,1);before=bytes(q.m[0x5c00:0x5c80])+bytes(q.m[0x5fb0:0x5fc0])
    c,_,_=q.step(0,0);assert not c.p&1 and not q.events and before==bytes(q.m[0x5c00:0x5c80])+bytes(q.m[0x5fb0:0x5fc0])
    scene_boundaries=[]
    for action in [5,9]:
        q=Runner(raw,compiled,True,World(),state(action=action))
        try:q.step(0,0)
        except AssertionError as exc:
            assert str(exc)=='Scene-owned action cannot be silently treated as ordinary movement'
            scene_boundaries.append(dict(action=action,host_scene_boundary_required=True,no_ordinary_movement_fallback=True))
        else:raise AssertionError('Missing scene-boundary rejection')
    # Preserve the two actual source-dependency counterexamples rather than
    # weakening old receipts or silently turning source X into facing.
    start=state();start.update({0x305:153,0x306:153,0x304:0})
    n,q=Runner(raw,compiled,False,World(),start),Runner(raw,compiled,True,World(),start)
    n.step(0,0,entry=(0xdc8f,'RdAdvancePlayerFrame'));q.step(0,0,entry=(0xdc8f,'RdAdvancePlayerFrame'))
    assert n.get(0x303)==4 and q.get(0x303)==15
    extension_negative=dict(index=153,native_frame=n.get(0x303),frozen_render_leaf_frame=q.get(0x303),native_source_bytes=raw[16+2*8192+0x60b:16+2*8192+0x610].hex(),frozen_leaf_unchanged=True,corrected_by_separate_control_advance=True)
    _,_,draw_regs=native_draw(raw,8,0,0,3,128,128,0x30)
    draw_x=draw_regs[1];native_morph=raw[16+62*8192+0xcc0+draw_x]
    facing_only=raw[16+62*8192+0xcc0]
    assert draw_x==36 and native_morph==0x20 and facing_only==0x30
    proof=dict(passed=True,native_run=False,source_ROM_sha256=sha(ref.ROM),CORE_bytes=len(compiled[0]),AUX_bytes=len(compiled[1]),rows=rows,
      actual_morph_wall_spring_unmorph_gates=gates,exact_Screw_AXYP_cells=screws,
      exact_animation_AXYP_cells=animations,native_damage_to_postdebit_death_continuations=damage,alternate_costume_failclosed_without_callbacks=True,
      scene_boundary_negative_controls=scene_boundaries,caller_live_stack_1C1_1FF_exact=True,
      frozen_animation_extension_counterexample=extension_negative,morph_facing_only_counterexample=dict(source_draw_return_X=draw_x,source_CCC0_plus_X=native_morph,incorrect_facing_only_byte=facing_only,broader_contexts_in='draw-return.json'),
      geometry='Declared per-pixel rectangle/probe/support callbacks, not a Metroid room-memory reconstruction. Full AXYP and ordered boundary events compared.',
      bindings=[ref.binding(f)for f in [Path(__file__),R/'src/rogue_dawn_control.s',R/'tools/prepare_rogue_dawn_control_v1.py',ref.ROM,a.output.parent/'control.bin',a.output.parent/'aux.bin']])
    a.output.write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=True,campaigns=len(rows),updates=sum(x['updates']for x in rows),CORE_bytes=proof['CORE_bytes'],AUX_bytes=proof['AUX_bytes'])))
if __name__=='__main__':main()
