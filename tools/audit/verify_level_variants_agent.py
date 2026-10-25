"""Compiled component/ABI tests of the isolated authored-level candidate.

Seeded CPU component checks are not controller replays or campaign clears.
"""
from pathlib import Path
import collections,hashlib,importlib.util,json,re,sys,time
R=Path(__file__).resolve().parents[2];O=R/'build/verification/level-variants-candidate-agent';C=O/'source'
sys.path.insert(0,str(R/'build/verification/specialist-mario-easy-hard-source-a/deps'))
from py65.devices.mpu6502 import MPU
sp=importlib.util.spec_from_file_location('level_variant_image',R/'build/verification/agent49g-samus-crouch-fix-proposal-b/image.py');im=importlib.util.module_from_spec(sp);sp.loader.exec_module(im)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

class Bus(list):
    def __init__(self,image):
        super().__init__([0]*65536);self.i=image;self.selector=0
        self.map(0x8000,62);self.map(0xe000,63);self.map(0xa000,2);self.map(0xc000,0)
    def map(self,start,bank):list.__setitem__(self,slice(start,start+8192),self.i.raw[16+8192*bank:16+8192*(bank+1)])
    def __setitem__(self,k,v):
        if isinstance(k,int):
            if k==0x8000:self.selector=v;return
            if k==0x8001:
                n=self.selector&7
                if n in(6,7):self.map(0xa000 if n==7 else 0xc000,v&127)
                return
            if k in(0x5115,0x5116):self.map(0xa000 if k==0x5115 else 0xc000,v&127);return
            if k>=0x8000 or 0x5000<=k<0x6000:return
        super().__setitem__(k,v)

class Machine:
    def __init__(self,path):self.i=im.Image(path);self.m=Bus(self.i);self.cpu=MPU(memory=self.m);self.reset()
    def set(self,n,v,i=0):self.m[self.i.ram[n]+i]=v&255
    def get(self,n,i=0):return self.m[self.i.ram[n]+i]
    def reset(self):
        self.m[:0x800]=[0]*0x800;self.m[0x6000:0x8000]=[0]*8192
        s=next(s for s in self.i.segs.values()if s['name']=='SMCCODE');self.m[s['start']:s['start']+s['size']]=self.i.raw[s['ooffs']:s['ooffs']+s['size']]
        self.set('CurrentBank',2|(128 if self.i.mapper==5 else 0));self.m.map(0xa000,2);self.m.map(0xc000,0);self.cpu.p=0x24
    def call(self,n,scope=None,limit=150000):
        h=self.i.hook(n,scope);c=self.cpu
        if 0xa000<=h['address']<0xc000:
            self.m.map(0xa000,h['physical_bank']);self.set('CurrentBank',h['physical_bank']|(128 if self.i.mapper==5 else 0))
        c.pc=h['address'];c.sp=0xfd;self.m[0x1fe]=0xfe;self.m[0x1ff]=0x5f
        steps=0
        while c.pc!=0x5fff:
            c.step();steps+=1
            assert steps<limit,(n,hex(c.pc),hex(c.sp))
        return steps
    def area(self,pointer,width,world=0,char=0,version=0):
        self.reset();self.set('AreaPointer',pointer);self.set('WorldNumber',world)
        for n,v in [('SelectedCharacter',char),('CrossoverBehaviorVersion',version),('Hidden1UpFlag',1)]:
            if n in self.i.ram:self.set(n,v)
        self.call('GetAreaDataAddrs')
        for i in range(3):self.set('AreaObjectLength',255,i)
        rows=[]
        for col in range(width):
            self.call('AreaParserCore');rows.append([self.get('MetatileBuffer',y)for y in range(13)]);self.call('IncrementColumnPos')
        return rows

def labels(path):
    d={}
    for s in path.read_text().splitlines():
        p=s.split()
        if len(p)==3:d[p[2].lstrip('.')]=int(p[1],16)
    return d

def main():
    contract=json.loads((O/'implemented-cell-contract.json').read_text());cells=contract['cells'];coins=contract['coin_cells'];masks=[0,3,1,3,3,1,1,1,0,0,1,2,3]
    report=dict(scope='Compiled seeded components, not controller clears; unchanged main workspace',ROMs={},cases={},passed=False)
    machines={};parents={}
    for mapper in('mmc3','mmc5'):
        n=machines[mapper]=Machine(C/f'build/smb-crossover-{mapper}.nes');p=parents[mapper]=Machine(R/f'build/smb-crossover-{mapper}.nes')
        report['ROMs'][mapper]=sha(n.i.path)
        # VICE .lbl output drops lexical scopes and repeats internal names.
        # Compare actual global symbols, including every public procedure entry.
        old={s['name']:s['val']for s in p.i.data['sym']if s.get('scope')==1 and 'val'in s and 'seg'in s}
        new={s['name']:s['val']for s in n.i.data['sym']if s.get('scope')==1 and 'val'in s and 'seg'in s}
        changed={k:[v,new.get(k)]for k,v in old.items()if new.get(k)!=v}
        assert not changed,('Old labels changed',mapper,changed)
        assert p.i.ram=={k:v for k,v in n.i.ram.items()if k in p.i.ram}
        assert sha(C/f'build/smb-crossover-{mapper}-baseline.nes')==sha(R/f'build/smb-crossover-{mapper}-baseline.nes')
        seg=next(s for s in n.i.segs.values()if s['name']=='LEVEL_VARIANTS');assert seg['start']+seg['size']<=0xa800
        # A800..BBFF must remain completely available for root's helper leaves.
        assert n.i.raw[16+0x1a*8192+0x800:16+0x1a*8192+0x1c00]==bytes([255])*0x1400
        print('ABI/baseline',mapper,'cold bytes',seg['size'],flush=True)
    # Every candidate cell, both versions, every selectable ID, and key negatives.
    overlay_cases=0
    keys={(z['area'],z['world'],z['page'],z['column'])for z in cells}
    keys|={(a,w^7,p,c)for a,w,p,c in keys}|{(a,w,p^16,c)for a,w,p,c in keys}
    for mapper,n in machines.items():
        for a,w,p,c in sorted(keys):
            for version in(0,1):
                for char in range(13):
                    n.reset();n.set('AreaPointer',a);n.set('WorldNumber',w);n.set('CurrentPageLoc',p);n.set('CurrentColumnPos',c);n.set('SelectedCharacter',char);n.set('CrossoverBehaviorVersion',version)
                    n.set('AreaDataLow',0);n.set('AreaDataHigh',0x60);n.m[0x6000]=0xfd
                    for i in range(3):n.set('AreaObjectLength',255,i)
                    expected=[0x80+y for y in range(13)]
                    for y,t in enumerate(expected):n.set('MetatileBuffer',t,y)
                    for z in cells:
                        if (a,w,p,c)!=(z['area'],z['world'],z['page'],z['column']):continue
                        if z['mask']and not z['mask']&masks[char]:continue
                        t=z['hard'if version else'easy']
                        if t!=255:expected[z['row']]=t
                    n.call('CrossoverLevelColumn');actual=[n.get('MetatileBuffer',y)for y in range(13)]
                    assert actual==expected,('overlay',mapper,a,w,p,c,version,char,actual,expected)
                    overlay_cases+=1
        print('Overlay',mapper,overlay_cases,flush=True)
    report['cases']['all_cell_versions_characters_and_negative_keys']=overlay_cases
    # Read actual authored streams with the complete parser, not the synthetic EOD.
    full_columns=0;full_changes=[]
    stream_specs=[(k,t,i)for k,t,count in [('Water',0,3),('Ground',1,22),('Underground',2,3),('Castle',3,6)]for i in range(count)]
    for mapper in machines:
        n,p=machines[mapper],parents[mapper]
        for kind,typ,idx in stream_specs:
            pointer=typ*32+idx;worlds={z['world']for z in cells if z['area']==pointer}or{7 if pointer==2 else 0}
            for world in worlds:
                before=p.area(pointer,256,world)
                for version in(0,1):
                    after=n.area(pointer,256,world,version=version)
                    for x,(b,a)in enumerate(zip(before,after)):
                        exp=b[:]
                        for z in cells:
                            if z['mask']or z['area']!=pointer or z['world']!=world or z['page']*16+z['column']!=x:continue
                            tile=z['hard'if version else'easy']
                            if tile!=255:exp[z['row']]=tile
                        assert a==exp,('full parser',mapper,kind,idx,world,version,x,a,exp)
                        for y,(u,v)in enumerate(zip(b,a)):
                            if u!=v:full_changes.append(dict(mapper=mapper,area=pointer,world=world,version=version,column=x,row=y+2,old=u,new=v))
                        full_columns+=1
            print('Parser',mapper,kind,idx+1,flush=True)
    report['cases']['full_authored_parser_columns']=full_columns
    (O/'full-parser-differences.json').write_text(json.dumps(full_changes,indent=2)+'\n')
    # All original admitted actors/groups in the actual game routine, including
    # primary/secondary hard flags. Suppressed group member is retained in negatives.
    parsed=json.loads((R/'build/verification/level-layout-audit-agent/spawn-revision2/original-enemy-commands.json').read_text())
    spawn_cases=0;spawn_changes=[]
    for mapper in machines:
        for stream,rows in parsed.items():
            match=re.search(r'E_(\w+)Area(\d+)',stream);typ={'Water':0,'Ground':1,'Underground':2,'Castle':3}[match[1]];ptr=typ*32+int(match[2])-1
            worlds={0,1,3,4,5,6}if ptr in(1,0x23,0x25,0x62)else{7 if ptr==2 else 0}
            for z in rows:
                if z['kind']not in('actor','group'):continue
                for world in worlds:
                    for primary in(0,1):
                        for secondary in(0,1):
                            for version in(0,1):
                                actuals=[]
                                for n in(parents[mapper],machines[mapper]):
                                    n.area(ptr,0,world,version=version);n.set('PrimaryHardMode',primary);n.set('SecondaryHardMode',secondary);n.set('EnemyDataOffset',z['offset']);n.set('EnemyObjectPageLoc',z['page']);n.set('EnemyObjectPageSel',1);n.set('ObjectOffset',0);n.cpu.x=0
                                    right=z['x']-48;n.set('ScreenRight_X_Pos',right&255);n.set('ScreenRight_PageLoc',right>>8);n.call('ProcessEnemyData')
                                    actuals.append([dict(id=n.get('Enemy_ID',s),x=n.get('Enemy_X_Position',s)+256*n.get('Enemy_PageLoc',s),y=n.get('Enemy_Y_Position',s),state=n.get('Enemy_State',s),second_fraction=n.get('Enemy_X_Speed',s),spin=n.get('FirebarSpinSpeed',s))for s in range(6)if n.get('Enemy_Flag',s)])
                                before,after=actuals;exp=[dict(q)for q in before]
                                allowed=not z['hard_only']or secondary
                                if allowed and ((ptr==1 and world in(1,6)and z['offset']==23)or(ptr==0x23 and world==5 and z['offset']==14)):exp=[]
                                if allowed and ((ptr==0x25 and world==0 and version and z['offset']==23)or(ptr==0x23 and world==5 and z['offset']==32)):exp=exp[:1]
                                for q in exp:
                                    if 0x1b<=q['id']<=0x1f:q['spin']=40
                                    if ptr==0x62 and world in(1,4)and q['id']in(0x2b,0x2c):
                                        if world==1:q.update(id=q['id']^7,y=96,state=192,second_fraction=0)
                                        elif q['id']==0x2b:q.update(y=96,state=224,second_fraction=0)
                                        else:q.update(y=64,state=192,second_fraction=0)
                                assert after==exp,('spawn',mapper,stream,z['offset'],world,primary,secondary,version,before,after,exp)
                                if before!=after:spawn_changes.append(dict(mapper=mapper,stream=stream,offset=z['offset'],world=world,primary=primary,secondary=secondary,version=version,before=before,after=after))
                                spawn_cases+=1
        print('Spawns',mapper,spawn_cases,flush=True)
    report['cases']['full_authored_spawn_flags_versions_world_negatives']=spawn_cases
    (O/'spawn-differences.json').write_text(json.dumps(spawn_changes,indent=2)+'\n')
    # Single-coin completion, including buffer alias/page and version negatives.
    coin_cases=0
    for mapper,n in machines.items():
        for z in coins:
            for char in range(13):
                for mode in('single','easy','world_alias','page_alias'):
                    n.reset();n.set('AreaPointer',z['area']);n.set('WorldNumber',z['world']^(7 if mode=='world_alias'else 0));n.set('CrossoverBehaviorVersion',mode!='easy');n.set('SelectedCharacter',char);n.set('Player_PageLoc',z['page']+(2 if mode=='page_alias'else 0));n.set('Player_X_Position',z['column']*16);n.set('R0',z['hard']);n.set('R2',z['contactRow']);n.set('R6',z['bufferLo']);n.set('R7',z['bufferHi']);n.set('SprDataOffset_Ctrl',1);n.cpu.x=1;n.cpu.y=z['hard']
                    n.call('CrossoverLevelCoinBrick')
                    expected=0xc4 if mode=='single'else z['hard']
                    assert n.cpu.a==expected,('coin',mapper,z,char,mode,n.cpu.a,expected)
                    assert n.cpu.x==1
                    coin_cases+=1
        print('Coins',mapper,coin_cases,flush=True)
    report['cases']['single_coin_completion_and_negatives']=coin_cases
    # Independent constant lifts: exact rational Q8 cadence and individual wraps.
    lift_steps=0
    for mapper,n in machines.items():
        for world in(1,4):
            for ident,start,second in [(0x2b,96,192 if world==1 else 224),(0x2c,96 if world==1 else 64,192)]:
                n.reset();n.set('AreaPointer',0x62);n.set('WorldNumber',world);n.set('Enemy_ID',ident);n.set('Enemy_Y_Position',start);n.set('Enemy_State',second);n.cpu.x=0
                pos=[start*256,second*256];counter=0
                for frame in range(720):
                    step=[235,235,234][counter];counter=(counter+1)%3
                    for k in range(2):
                        pos[k]+= -step if ident==0x2b else step
                        if ident==0x2b and pos[k]<64*256:pos[k]=240*256
                        if ident==0x2c and pos[k]>240*256:pos[k]=64*256
                    n.call('CrossoverLiftMove');actual=[n.get('Enemy_Y_Position')*256+n.get('Enemy_YMoveForceFractional'),n.get('Enemy_State')*256+n.get('Enemy_X_Speed')]
                    assert actual==pos,('lift',mapper,world,ident,frame,actual,pos)
                    assert n.get('Enemy_Y_MoveForce')==counter
                    lift_steps+=1
                for key in('TimerControl','Enemy_OffscreenBits'):
                    n.set(key,1 if key=='TimerControl'else 15);before=n.m[:0x800]+n.m[0x6000:0x8000];n.call('CrossoverLiftMove');after=n.m[:0x800]+n.m[0x6000:0x8000]
                    for field in('Enemy_Y_Position','Enemy_YMoveForceFractional','Enemy_State','Enemy_X_Speed','Enemy_Y_MoveForce'):
                        a=n.i.ram[field];assert before[a]==after[a],('lift freeze',mapper,key,field)
                    n.set(key,0)
        print('Lift updates',mapper,lift_steps,flush=True)
    report['cases']['independent_lift_updates']=lift_steps
    report.update(passed=True,script_sha256=sha(__file__),candidate_build_sha256=sha(O/'build.json'),limits=['No ordinary controller traversal or media claim.','Castle expanded lengths, dynamic helpers and random generators are not changed by this candidate.','Native small-platform contact response remains the native player-body adapter, now with source24x8 lift rectangles.'])
    (O/'component-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)

if __name__=='__main__':main()
