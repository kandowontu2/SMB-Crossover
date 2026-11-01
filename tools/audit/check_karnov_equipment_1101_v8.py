"""Aggregate donor/relocated Bomb/Ladder CPU proof; no host ROM admission."""
from pathlib import Path
import hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from recover_karnov_actor_1101_v1 import ROM,EXPECTED
from verify_native_relocation import NesMPU
from check_karnov_actor_1101_v1 import Memory
O=R/'build/karnov-equipment-component-1101-v8';V7=R/'build/karnov-options-component-1101-v7'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
KINDS={'bomb':(0xae3d,'KrEquipmentBomb',11),'render':(0xa27b,'KrEquipmentBombRender',11),
 'blast':(0xccfc,'KrEquipmentBombBlast',None),'grow':(0xa4b6,'KrEquipmentLadderGrow',12),
 'restore':(0xa5bd,'KrEquipmentLadderRestore',12),'overlay':(0xb46f,'KrEquipmentLadderOverlay',12),
 'retract':(0xa5bd,'KrEquipmentLadderRetract',12),'rebuild':(0xa5bd,'KrEquipmentLadderRebuild',12),
 'rebase':(0xaf3f,'KrEquipmentOriginalRebase',12),
 'options':(0xeaa7,'KrOptionsNative',None),'timers':(0xada8,'KrOptionsNativeTimers',12)}


class Proof:
    def __init__(self,a):
        self.a=a;self.labels=a['labels'];self.raw=ROM.read_bytes();self.binary=(O/'component.bin').read_bytes()
        self.v7=json.loads((V7/'assembly.json').read_text());self.v7labels=self.v7['labels'];self.v7binary=(V7/'component.bin').read_bytes()
        assert sha(ROM)==EXPECTED
        self.count=0;self.normalizations=0;self.minimum=224;self.trace=hashlib.sha256();self.events={};self.reads=0
    def make(self,port,values=None):
        m=Memory()
        if port:
            m[0x9000:0x9000+len(self.binary)]=self.binary
            m[0x7000:0x7000+len(self.v7binary)]=self.v7binary
            m[0x2000:0x4000]=self.raw[16:16+8192]
            m[:256]=bytes((i*37+19)&255 for i in range(256))
        else:
            m[0xc000:]=self.raw[16+14*8192:16+16*8192]
            m[0x8000:0xa000]=self.raw[16:16+8192]
        fields={0x62:0,0x63:128,0x64:144,0x65:2,0x68:0,0x69:0,0x8b:2,0x8d:0x1c,
            0x8e:0,0x8f:255,0x90:1,0x94:0xa4,0x61:0,0x5e:0,0x71f:0,
            0xbb:2,0xbc:2,0xbd:2,0xbe:2,0xbf:2,0xc1:128,0xc2:144,0xc3:16,
            0x625:128,0x626:128}
        for i in range(128):fields[0x4cc+i]=(i*53+7)&255
        fields.update(values or{})
        for addr,value in fields.items():m[(0xc000 if port else 0)+addr]=value
        m.writes=[];return m
    def get(self,m,p,a):return m[(0xc000 if p else 0)+a]
    def put(self,m,p,values):
        for a,v in values.items():m[(0xc000 if p else 0)+a]=v
    def run(self,m,p,kind,flags=0x71):
        address,label,bank=KINDS[kind];v7=kind in['options','timers'];labels=self.v7labels if v7 else self.labels
        if p:pc=labels[label]
        else:
            pc=address
            if bank is not None:m[0xa000:0xc000]=self.raw[16+bank*8192:16+(bank+1)*8192]
        c=NesMPU(memory=m,pc=pc);c.a=85;c.x=7;c.y=91;c.p=flags;c.sp=224;c.stPushWord(0x5aff)
        before=bytes(m[:256])if p else None;events=[];last=[None,None,None];result=None;low=c.sp;dispatch=None
        aset={'LDA','PLA','TXA','TYA','ADC','SBC','AND','ORA','EOR'};xset={'LDX','TAX','TSX','INX','DEX'};yset={'LDY','TAY','INY','DEY'}
        if v7:
            traps={0xff10:'sound',0xff20:'unsupported-scene',0xff30:'actor-scene',0xff40:'terrain'}if p else{0xc81d:'sound',0xc6fc:'unsupported-scene',0xc1c7:'actor-scene',0xc3d8:'terrain'}
        else:traps={0xff10:'score',0xff20:'HUD',0xff30:'scene',0xff40:'draw',0xff50:'frame-gate'}if p else{0xc76e:'score',0xc534:'HUD',0xc1c7:'scene',0xdf61:'draw',0xc046:'frame-gate'}
        for step in range(15000):
            if c.pc==0x5b00:break
            low=min(low,c.sp)
            if p and c.pc==labels[label]+13:result=(c.a,c.x,c.y,c.p,last[:],dispatch)
            if not p and kind in['retract','rebuild']and c.pc==0x5b00:raise AssertionError('Owner step was skipped')
            if c.pc in traps:
                name=traps[c.pc];events.append((name,c.a,c.x,c.y,last[:],dispatch))
                c.pc=(c.stPopWord()+1)&65535;continue
            # Original A5BD RTS feeds the actual fixed-bank count/ownership
            # leaf. The port uses an explicit JSR+JMP core with the same order.
            if not p and kind in['retract','rebuild']and m[c.pc]==0x60 and c.sp==222:
                c.pc=0xd700 if kind=='retract'else 0xdb00;kind='owner-completion';continue
            mnemonic,mode=c.disassemble[m[c.pc]]
            dpc=labels['KrDispatch']if p else 0xc831
            if c.pc==dpc+13:
                ptr=m[3 if p else 0x58]|m[4 if p else 0x59]<<8
                dispatch=c.x|m[(ptr+c.y)&65535]<<8
            if p and not v7 and c.pc==self.labels['KrEquipmentReadStage']:self.reads+=1
            if mnemonic in aset or(mnemonic in['ASL','LSR','ROL','ROR']and mode=='acc'):last[0]=c.pc
            if mnemonic in xset:last[1]=c.pc
            if mnemonic in yset:last[2]=c.pc
            assert m[c.pc]!=0,('Source BRK',p,kind,hex(c.pc));c.step()
        else:raise AssertionError(('Source bound',p,kind,hex(c.pc)))
        assert c.sp==224,('Unbalanced stack',p,kind,c.sp)
        if p:
            assert bytes(m[:256])==before,'Host ZP including3/4 not restored'
            assert all(0xc000<=a<0xc800 or 0x100<=a<0x200 or a in[3,4]for a in m.writes),('Undeclared private write',[hex(a)for a in m.writes if not(0xc000<=a<0xc800 or 0x100<=a<0x200 or a in[3,4])][:10])
        return c,events,result,last,dispatch,low
    def normalize(self,x,y,old_writer,new_writer,index,old_target,new_target,labels):
        writer=0xc83e if index==0 else 0xc83c
        assert old_writer==writer and new_writer==labels['KrDispatch']+writer-0xc831,('Unproved register relocation',index,x,y,old_writer,new_writer)
        assert labels[f'Kr_{old_target:04X}']==new_target,('Pointer target',hex(old_target),hex(new_target))
        assert x==(old_target>>8 if index==0 else old_target&255)and y==(new_target>>8 if index==0 else new_target&255)
        self.normalizations+=1
    def pair(self,mems,kind,flags=0x71):
        results=[self.run(m,p,kind,flags)for p,m in enumerate(mems)]
        (a,ea,_,la,da,al),(z,ez,result,lz,dz,zl)=results
        assert result and(a.y,a.p&0x4d)==(z.y,z.p&0x4d),('Source Y/P',kind,a.y,z.y,a.p,z.p)
        labels=self.v7labels if kind in['options','timers']else self.labels
        for i,(x,y)in enumerate([(a.a,z.a),(a.x,z.x)]):
            if x!=y:self.normalize(x,y,la[i],result[4][i],i,da,result[5],labels)
        if a.p&0x82!=z.p&0x82:
            self.normalize(a.a,z.a,la[0],result[4][0],0,da,result[5],labels)
            nz=lambda v:(128 if v&128 else 0)|(2 if not v else 0)
            assert a.p&0x82==nz(a.a)and z.p&0x82==nz(z.a),'NZ difference must be proved pointer LDA'
        assert len(ea)==len(ez),('Callback count',kind,ea,ez)
        for e,f in zip(ea,ez):
            assert e[0]==f[0]and e[3]==f[3],('Callback type/Y',kind,e,f)
            for i in [0,1]:
                if e[i+1]!=f[i+1]:self.normalize(e[i+1],f[i+1],e[4][i],f[4][i],i,e[5],f[5],labels)
            self.events[e[0]]=self.events.get(e[0],0)+1
        skip=set(range(0x100,0x200))|{0x58,0x59,0x7fe,0x7ff}
        delta=[i for i in range(2048)if i not in skip and mems[0][i]!=mems[1][0xc000+i]]
        assert not delta,('Source state',kind,[(hex(i),mems[0][i],mems[1][0xc000+i])for i in delta[:10]])
        self.minimum=min(self.minimum,zl);self.trace.update(bytes(mems[0][0x5e:0xc4]));self.count+=1
        return ea


def bomb_pairs(p):
    n=0
    for state,x,y,timer,flags in itertools.product([0,0x80,0x81,0x82,0x83],[7,8,128,247,248],[31,32,144,191,192],[1,16],[0x31,0xf1]):
        p.pair([p.make(i,{0xc0:state,0xc1:x,0xc2:y,0xc3:timer})for i in range(2)],'bomb',flags);n+=1
    stage_checks=0;triggers=0
    fixed=p.raw[16+11*8192:16+12*8192]
    coords={3:[tuple(fixed[a:a+2])for a in range(0xec2,0xee4,2)],5:[(x,0x23)for x in range(0x34,0x39)],
        7:[tuple(fixed[a:a+2])for a in range(0xf12,0xf1c,2)],8:[(0x5f,12),(0x5e,12),(0x5f,13)]}
    for stage in range(9):
        for wx,wy in coords.get(stage,[(8,9)]):
            # Place camera so source screen anchor remains an ordinary valid
            # bomb coordinate, while genuine C460 computes the intended tile.
            fields={0xc0:0x83,0xc1:128,0xc2:144,0xc3:1,0x61:stage,0x9f:(wx-8)&255,0xa0:(wy-9)&255,0x5e:3}
            ms=[p.make(i,fields)for i in range(2)];p.pair(ms,'bomb');stage_checks+=1
            assert ms[0][0xc0]==0
            triggered=ms[0][0x5e]==8;triggers+=triggered
            if stage==5:assert triggered==(0x35<=wx<0x38)
            if stage==8:assert triggered==(wx==0x5f and wy==12)
    rendered=0
    for state,phase,x,y in itertools.product([0,0x80,0x81,0x82,0x83],[0,8,16,255],[8,128,247],[32,144,191]):
        fields={0xc0:state,0xc1:x,0xc2:y,0xe8:phase,**{a:0xf0 for a in range(0x250,0x258)}}
        ms=[p.make(i,fields)for i in range(2)];p.pair(ms,'render');rendered+=1
        if state==0:assert ms[0][0x250]==ms[0][0x254]==0xf0
        elif state==0x80:assert ms[0][0x251]in[0x41,0x43]and ms[0][0x254]==0xf0
        else:assert ms[0][0x255]==ms[0][0x251]+2 and ms[0][0x257]==(ms[0][0x253]+8)&255
    return dict(passed=True,update_pairs=n,stage_terrain_pairs=stage_checks,source_scene_triggers=triggers,render_pairs=rendered)


def blast_pairs(p):
    n=0
    for state,dx,dy,damage in itertools.product([0,0x80,0x81,0x82,0x83],[-17,-16,-1,0,15,16],[-1,0,15,16],[0,0x20,0x80]):
        fields={0xc0:state,0xc1:128,0xc2:144,0x44:0,0x650:1,0x651:0x80,0x652:(128-dx)&255,0x653:(144-dy)&255,0x655:damage}
        p.pair([p.make(i,fields)for i in range(2)],'blast');n+=1
    types=0;kills=0
    for kind,damage in itertools.product(range(64),[0,1,7,15,31,0x80,0xa0]):
        fields={0xc0:0x82,0xc1:128,0xc2:144,0x44:0,0x650:kind,0x651:0x80,0x652:128,0x653:144,0x655:damage}
        ms=[p.make(i,fields)for i in range(2)];events=p.pair(ms,'blast');types+=1;kills+=any(e[0]=='score'for e in events)
    return dict(passed=True,unsigned_blast_geometry_pairs=n,original_enemy_HP_score_pairs=types,original_defeats=kills)


def rebase_pairs(p):
    n=0;delta={0:(0,0),0x80:(0,1),0x90:(0,-1),0xa0:(1,0),0xb0:(-1,0)}
    for direction,x,y in itertools.product(delta,[0,1,127,255],[0,1,127,255]):
        fields={0xc4:direction,0xc1:x,0xc2:y,0x63:x,0x64:y}
        for i in range(6):
            fields[0x652+i*16]=x;fields[0x653+i*16]=y
            fields[0x6db+i*6]=x;fields[0x6dc+i*6]=y;fields[0x6dd+i*6]=1;fields[0x6de+i*6]=1
        ms=[p.make(i,fields)for i in range(2)];p.pair(ms,'rebase');n+=1
        dx,dy=delta[direction]
        assert(ms[0][0xc1],ms[0][0xc2])==((x+dx)&255,(y+dy)&255)
        assert(ms[0][0x63],ms[0][0x64])==((x+dx)&255,(y+dy)&255)
    return dict(passed=True,full_original_camera_owner_pairs=n,bomb_anchor_pixel_rebase_directions=delta,
        warning='Original owner also shifts private actor/enemy pools. Native host must adapt the bomb anchor once at its actual scroll boundary.')


def ladder_pairs(p):
    grow=restore=overlay=owner=0
    for count,y,x,tile,flags in itertools.product(range(9),[16,31,32,64,128,191],[8,128,248],[0,1,9,128,255],[0x31,0xf1]):
        fields={0x624:count,0x625:x,0x626:y,0x71f:3,0x5e:1,**{a:tile for a in range(0x40c,0x4cc)}}
        ms=[p.make(i,fields)for i in range(2)];p.pair(ms,'grow',flags);grow+=1
        if count==8 or y<32 or tile in[1,128,255]:assert ms[0][0x5e]==3 and ms[0][0x624]==count
        else:
            assert ms[0][0x624]==count+1 and ms[0][0x626]==(y-16)&255
            assert (ms[0][0xad],ms[0][0xae],ms[0][0xaf],ms[0][0xb0])==(0xbe,0xbf,0xbe,0xbf)
    # Real source map coordinates, scrolling direction and viewport clipping.
    for direction,cx,cy,worldx,worldy,metatile in itertools.product([0,0x80,0x90,0xa0,0xb0],[0,3],[0,12],[0,3,15,16],[0,3,11,12], [0,9,0x69,0xcf,255]):
        fields={0xc4:direction,0xc5:3,0x9f:cx,0xa0:cy,0x624:1,0x625:128,0x626:112,0x627:worldx,0x628:worldy,0x629:metatile}
        p.pair([p.make(i,fields)for i in range(2)],'restore');restore+=1
    for count,match,cache in itertools.product([0,1,8],[-1,0,3,21],[0,7,191]):
        fields={0x624:count,0x625:0 if count==0 else 128,0x626:0 if count==0 else 112,0x44:7,0x45:5,0x46:cache}
        for a in range(0,24,3):fields[0x627+a]=2;fields[0x628+a]=3
        if match>=0:fields[0x627+match]=7;fields[0x628+match]=5
        ms=[p.make(i,fields)for i in range(2)];p.pair(ms,'overlay');overlay+=1
        assert ms[0][0x54c+cache]==(0xcf if count and match>=0 else 0)
    for kind,count,scene in itertools.product(['retract','rebuild'],[1,2,8],[0,1]):
        fields={0x624:count,0x625:128,0x626:32,0x8f:0,0x8e:255,0x71f:3,0x5e:11,0x6b0:scene}
        for a in range(0,24,3):fields[0x627+a]=8;fields[0x628+a]=9;fields[0x629+a]=0
        ms=[p.make(i,fields)for i in range(2)];events=p.pair(ms,kind);owner+=1
        assert ms[0][0x624]==count-1
        assert [e[0]for e in events][-2:]==['draw','frame-gate']
        if count==1:
            if kind=='retract':assert ms[0][0x8f]&4 and ms[0][0x8e]==2 and ms[0][0x5e]==3 and ms[0][0x625]==ms[0][0x626]==0
            else:assert ms[0][0x5e]==1 and ms[0][0x625]==128 and ms[0][0x626]==136
    return dict(passed=True,growth_and_solid_stop_pairs=grow,restore_scroll_and_clipping_pairs=restore,offscreen_reentry_overlay_pairs=overlay,original_count_ownership_scene_pairs=owner)


def sequences(p):
    # Execute original earned Bomb activation, original timer scheduler and the
    # same source object update order. No generic native projectile is used.
    ms=[p.make(i,{0x8e:1,0x21:4,0xbb:1,0x90:1,0x0f:1,0xe8:1})for i in range(2)]
    events=p.pair(ms,'options');assert ms[0][0xc0]==0x80 and ms[0][0xbb]==0 and not(ms[0][0x8f]&2)
    transitions=[];previous=ms[0][0xc0];phase=1;anchor=(ms[0][0xc1],ms[0][0xc2])
    for frame in range(1,162):
        for i,m in enumerate(ms):p.put(m,i,{0x0f:phase,0xe8:phase})
        p.pair(ms,'bomb');p.pair(ms,'timers');p.pair(ms,'render')
        assert(ms[0][0xc1],ms[0][0xc2])==anchor,'Original parked bomb gained invented motion'
        state=ms[0][0xc0]
        if state!=previous:transitions.append([frame,state]);previous=state
        phase=(phase+1)&255
    assert transitions==[[128,0x81],[129,0x82],[145,0x83],[161,0]],transitions
    # Real activation -> background growth -> original retraction owner. The
    # source remains in scene1 while segments grow, then source071F resumes.
    ms=[p.make(i,{0x8e:2,0x21:4,0x90:1,0x63:128,0x64:144,0x5e:3,0x8b:2,0x625:0,0x626:0})for i in range(2)]
    p.pair(ms,'options');assert ms[0][0x5e]==1 and not(ms[0][0x8f]&4)
    heights=[]
    for frame in range(20):
        if ms[0][0x5e]!=1:break
        p.pair(ms,'grow');heights.append(ms[0][0x624])
    assert ms[0][0x5e]==3 and ms[0][0x624]==7,heights
    for i,m in enumerate(ms):p.put(m,i,{0x5e:11})
    restored=[]
    for frame in range(10):
        if ms[0][0x5e]!=11:break
        p.pair(ms,'retract');restored.append(ms[0][0x624])
    assert restored==[6,5,4,3,2,1,0]and ms[0][0x8f]&4 and ms[0][0x8e]==2
    return dict(passed=True,bomb_source_updates=161,bomb_transitions=transitions,bomb_anchor_constant=True,
        ladder_growth_counts=heights,ladder_retraction_counts=restored,ladder_ownership_returned=True,
        callbacks_real_source_order=True)


def activation_boundaries(p):
    n=0;unsupported=0
    for level,existing,state,scene_object in itertools.product(range(10),[False,True],[0,6,7],[0,128]):
        fields={0x8e:2,0x21:4,0x94:0xa4+level,0x62:state,0x6cf:scene_object,
            0x624:1 if existing else 0,0x625:128 if existing else 0,0x626:112 if existing else 0}
        ms=[p.make(i,fields)for i in range(2)];events=p.pair(ms,'options');n+=1
        requested=any(e[0]=='unsupported-scene'for e in events);unsupported+=requested
        assert requested==(state<7 and level in[3,6]and not scene_object)
    assert unsupported>0
    return dict(passed=True,original_ladder_activation_scene_boundary_pairs=n,
        unsupported_original_scene_requests_preserved=unsupported,
        note='C6FC is still an explicit unsupported host scene-object callback; this proof does not whitelist Ladder.')


def main():
    a=json.loads((O/'assembly.json').read_text());assert a['passed']
    for path,h in a['bindings'].items():assert sha(path)==h,path
    p=Proof(a);q=dict(passed=False,component_only=True,native=False,installed=False,host_modified=False,code_lease_granted=False)
    try:
        q.update(bomb=bomb_pairs(p),blast=blast_pairs(p),camera=rebase_pairs(p),ladder=ladder_pairs(p),activation=activation_boundaries(p),sequences=sequences(p),passed=True)
    except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
    q.update(source_pairs=p.count,engine_executions=p.count*2,minimum_standalone_SP=p.minimum,
        proved_pointer_register_normalizations=p.normalizations,assembled_stage_backend_reads=p.reads,
        source_trace_sha256=p.trace.hexdigest(),callbacks=p.events,
        limits=['No native host admission, ROM code allocation, new equipment whitelist or installed nightly.',
            'Original enemy pool HP/score tested; native SMB bomb blast enumeration/damage callback remains required.',
            'Ladder uses actual original background/collision/attribute packets. Native map reader, climbable collision, tile publication and frozen scene-job adapter remain required.',
            'Original object OAM stays private. Native OAM slots/CHR lease, bomb graphics and NMI budget not admitted.',
            'Stage0 ROM fixture supplies exact source map/tile data; all stage-specific bomb coordinate checks are source-tested, not native terrain edits.',
            'Standalone source stack is not actual host Main/ISR reserve qualification.'],
        bindings={str(path.resolve()):sha(path)for path in[Path(__file__),O/'assembly.json',O/'component.bin',O/'component.dbg',
            V7/'assembly.json',V7/'component.bin',R/'tools/audit/check_karnov_actor_1101_v1.py',R/'tools/audit/verify_native_relocation.py',ROM]})
    (O/'CPU-controls.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:v for k,v in q.items()if k not in['bindings','traceback']}))
    if not q['passed']:print(q['traceback']);raise SystemExit(1)
if __name__=='__main__':main()
