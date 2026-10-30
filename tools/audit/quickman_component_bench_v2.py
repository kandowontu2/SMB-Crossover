"""Compile the private component and compare controller streams to native CX."""
from pathlib import Path
import json,hashlib,subprocess,sys,re
from py65.devices.mpu6502 import MPU
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
import quickman_component_v2 as q
O=q.O;B=q.B
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def compile():
    info=q.generate();mapping={int(k,16):v for k,v in info['native_to_private_state'].items()};out=O/'bench';out.mkdir(exist_ok=True);grid,stage=q.make_world();(out/'native-stage-fixture.bin').write_bytes(stage);(out/'material-grid.bin').write_bytes(bytes(v for row in grid for v in row))
    def mem(a):return f'QuickManScratch+${a:02X}'if a<18 else f'QuickManState+${mapping[a]:03X}'
    lines=['.setcpu "6502"','.export QuickManState,QuickManWorldProbe,QuickManSound,QuickManScrollStrip,QuickManProjectileContact,QuickManDeath,QuickManYield,QuickManEffectSpawn,ProbeDone,FixtureStatus','.exportzp QuickManScratch','.segment "QMSTATE"',f'QuickManState: .res {info["state_bytes"]}','FixtureStatus: .res 1','.segment "QMZP": zeropage','QuickManScratch: .res 18','.segment "FIXTURE"','QuickManWorldProbe:', 'lda '+mem(0xb),'beq ProbeYReady','bmi ProbeTop','lda #$f0','bne ProbeClamp','ProbeTop: lda #0','ProbeClamp: sta '+mem(0xa),'ProbeYReady:','lda '+mem(0xa),'lsr','lsr','lsr','lsr','tax','lda GridRowLo,x','sta '+mem(0xc),'lda GridRowHi,x','sta '+mem(0xd),'lda '+mem(0x8),'lsr','lsr','lsr','lsr','sta '+mem(0),'lda '+mem(0x9),'and #3','asl','asl','asl','asl','ora '+mem(0),'tay','lda ('+mem(0xc)+'),y','sta '+mem(0),'ProbeDone:','lda #$3c','rts','QuickManSound:','QuickManScrollStrip:','QuickManProjectileContact:','rts','QuickManEffectSpawn: sec','rts','QuickManDeath: lda #1','sta FixtureStatus','rts','QuickManYield: lda #2','sta FixtureStatus','rts','GridRowLo: .byte '+','.join('<(MaterialGrid+'+str(i*64)+')'for i in range(16)),'GridRowHi: .byte '+','.join('>(MaterialGrid+'+str(i*64)+')'for i in range(16)),'MaterialGrid: .incbin "'+str(out/'material-grid.bin').replace('\\','/')+'"']
    (out/'fixture.s').write_text('\n'.join(lines)+'\n');(out/'link.cfg').write_text('MEMORY { Z:start=$20,size=$12,type=rw; S:start=$6000,size=$1000,type=rw; P:start=$8000,size=$8000,file=%O,type=ro; }\nSEGMENTS { QMZP:load=Z,type=zp; QMSTATE:load=S,type=bss; QUICKMAN:load=P,type=ro; FIXTURE:load=P,type=ro; }\n')
    ca=R/'tools/Windows/cc65/bin/ca65.exe';ld=R/'tools/Windows/cc65/bin/ld65.exe';commands=[]
    for src,obj in[(O/'component/component.s',out/'component.o'),(out/'fixture.s',out/'fixture.o')]:commands.append([str(ca),'-g',str(src),'-o',str(obj)])
    commands.append([str(ld),'-C',str(out/'link.cfg'),'-o',str(out/'component-fixture.bin'),'--dbgfile',str(out/'component.dbg'),'-Ln',str(out/'labels.txt'),'-m',str(out/'link.map'),str(out/'component.o'),str(out/'fixture.o')])
    logs=[]
    for cmd in commands:
        p=subprocess.run(cmd,capture_output=True,text=True);logs.append(dict(command=cmd,rc=p.returncode,stdout=p.stdout,stderr=p.stderr));
        if p.returncode:
            (out/'compile-negative.json').write_text(json.dumps(logs,indent=2));raise AssertionError(p.stderr[:6000])
    labels={k:int(v,16)for v,k in re.findall(r'al ([0-9A-Fa-f]+) \.(\w+)',(out/'labels.txt').read_text())};(out/'compile.json').write_text(json.dumps(dict(commands=logs,ca65_sha256=sha(ca),ld65_sha256=sha(ld),genuine_debug_sha256=sha(out/'component.dbg')),indent=2)+'\n');return info,mapping,labels,stage

class Native(q.CoreBus):
    def __init__(self,stage):super().__init__(B);self.stage=stage;self.current_PC=0;self.player_type_writes=[]
    def __getitem__(self,a):
        if isinstance(a,slice):return [self[i]for i in range(a.start or 0,a.stop,a.step or 1)]
        if 0x8000<=a<0xa000 and self.bank==0:return self.stage[a-0x8000]
        return super().__getitem__(a)
    def __setitem__(self,a,v):
        if 0x400<=a<0x410:self.player_type_writes.append([f'{self.current_PC:04X}',f'{a:04X}',v]);self.player_type_writes=self.player_type_writes[-32:]
        super().__setitem__(a,v)

def invoke(memory,pc,A=0,hook=None,X=0,registers=None):
    memory[0x1fe]=0xfe;memory[0x1ff]=0x7f;m=MPU(memory=memory);m.pc=pc;m.sp=0xfd;m.a=A;m.x=X;n=0;history=[]
    while m.pc!=0x7fff:
        if hook:hook(m)
        history.append(m.pc);history=history[-32:];m.step();n+=1
        assert n<100000,('did not return',hex(m.pc),[hex(x)for x in history])
    if registers is not None:registers.update(A=m.a,X=m.x,Y=m.y,P=m.p)
    return m.processorCycles

def differential(info,mapping,labels,stage):
    image=(O/'bench/component-fixture.bin').read_bytes();out=O/'bench';results=[]
    masks=[]
    cases=[('idle',80,120,lambda f:0),('run_into_wall',80,180,lambda f:128),('wall_climb',80,200,lambda f:128|(1 if any(a<=f<b for a,b in[(5,25),(50,70),(95,115),(140,160)])else 0)|(2 if 20<=f<180 else 0)),('fast_wall_climb',80,200,lambda f:128|(1 if any(a<=f<b for a,b in[(5,25),(50,70),(95,115),(140,160)])else 0)|(32 if any(a<=f<b for a,b in[(3,25),(48,70),(93,115),(138,160)])else 0)|(2 if 20<=f<180 else 0)),('wall_kick_away',80,180,lambda f:(128 if f<95 or f>=135 else 64)|(1 if 5<=f<25 or 50<=f<70 or 95<=f<120 else 0)|(2 if 15<=f<160 else 0)),('left_page_cross',300,180,lambda f:64|(1 if 20<=f<45 or 80<=f<100 else 0)|(2 if 10<=f<150 else 0)),('held_A_single_edge',112,120,lambda f:1 if 5<=f<95 else 0),('A_release_repress',112,160,lambda f:1 if any(a<=f<b for a,b in[(5,25),(50,70),(100,120)])else 0)]
    cases.append(('moving_support',200,180,lambda f:128 if f>=120 else 0))
    for name,x,ticks,buttons in cases:
        component=bytearray(65536);component[0x8000:0x8000+len(image)]=image;invoke(component,labels['QuickManInit']);native=Native(stage)
        for a,i in mapping.items():native.ram[a]=component[labels['QuickManState']+i]
        native.ram[0x61]=0x3c;native.ram[0x62]=0x3d;native.ram[0x63]=6
        for a,v in [(0x460,x&255),(0x440,x>>8)]:native.ram[a]=v;component[labels['QuickManState']+mapping[a]]=v
        if name=='moving_support':
            for a,v in [(0x4a0,100),(0x640,255)]:native.ram[a]=v;component[labels['QuickManState']+mapping[a]]=v
        nquery=[];cquery=[];npending=[];cpending=[];rows=[];states=set();source_cycles=[];component_cycles=[]
        def nh(m):
            native.current_PC=m.pc
            if m.pc==0xcbc0:npending.append([native.ram[8]+256*native.ram[9],native.ram[0xa],native.ram[0xb]])
            if m.pc==0xcc2e:nquery.append(npending.pop()+[native.ram[0]])
        def ch(m):
            z=labels['QuickManScratch']
            if m.pc==labels['QuickManWorldProbe']:cpending.append([component[z+8]+256*component[z+9],component[z+0xa],component[z+0xb]])
            if m.pc==labels['ProbeDone']:cquery.append(cpending.pop()+[component[z]])
        for tick in range(ticks):
            # Actual native queue-clear tail, modeling the host's completed PPU
            # submission at each fixture frame boundary. This is not a fake NMI.
            invoke(native,0xd1d7)
            if name=='moving_support':
                for a,v in {0x160:24,0x170:144,0x430:0xc0,0x470:200+tick//4,0x4b0:144,0x450:0,0x610:0,0x630:64}.items():
                    native.ram[a]=v;component[labels['QuickManState']+mapping[a]]=v
            held=buttons(tick);previous=native.ram[0x23];native.ram[0x25]=previous;native.ram[0x23]=held
            # Execute the actual four native edge-owner instructions.
            m=MPU(memory=native);m.pc=0xc095
            while m.pc!=0xc09d:m.step()
            native.bank=0x3c;native.bank7=0x3d;native.ram[0x61]=0x3c;native.ram[0x62]=0x3d
            cyc=invoke(native,0x84ee,hook=nh)+invoke(native,0xdcdf,hook=nh)
            native.bank=0x1c;native.ram[0x61]=0x1c;cyc+=invoke(native,0xcd21,hook=nh);native.ram[0x1c]=(native.ram[0x1c]+1)&255
            cc=invoke(component,labels['QuickManTick'],A=held,hook=ch)
            diffs=[dict(address=f'{a:04X}',source=native.ram[a],component=component[labels['QuickManState']+i])for a,i in mapping.items()if native.ram[a]!=component[labels['QuickManState']+i]]
            if diffs or nquery!=cquery or component[labels['FixtureStatus']]:
                negative=dict(case=name,tick=tick,held=held,first_state_diffs=diffs[:24],source_queries=nquery,component_queries=cquery,fixture_status=component[labels['FixtureStatus']],source_recent_type_writes=native.player_type_writes)
                p=out/f'negative-{name}-{tick:04d}.json';p.write_text(json.dumps(negative,indent=2)+'\n');raise AssertionError((name,tick,diffs[:8],len(nquery),len(cquery),component[labels['FixtureStatus']]))
            for slot in [0,2,3,4]:
                expected=0
                if native.ram[0x420+slot]&128:
                    typ=native.ram[0x400+slot];lo=0x9000 if slot==0 else 0x9180;hi=0x90c0 if slot==0 else 0x9240
                    ptr=B[q.at((0x1c,lo+typ))]+256*B[q.at((0x1c,hi+typ))];expected=B[q.at((0x1c,ptr+2+native.ram[0x6a0+slot]))]
                regs={};invoke(component,labels['QuickManGetFrame'],X=slot,registers=regs);assert regs['A']==expected,(name,tick,slot,expected,regs)
                if not expected and native.ram[0x420+slot]&128:
                    # Actual source renderer's zero-frame deactivation opcode.
                    m=MPU(memory=native);m.pc=0xcde3;m.x=slot;m.step()
            states.add(native.ram[0x2c]);source_cycles.append(cyc);component_cycles.append(cc)
            rows.append(dict(tick=tick,held=held,X=native.ram[0x460]+256*native.ram[0x440]+native.ram[0x480]/256,Y=native.ram[0x4a0]+native.ram[0x4c0]/256,state=native.ram[0x2c],vy=[native.ram[0x640],native.ram[0x660]],vx=[native.ram[0x600],native.ram[0x620]],support=native.ram[0x40],down_latch=native.ram[0x4e0],new_edges=native.ram[0x27],active_projectiles=[i for i in range(2,5)if native.ram[0x420+i]&128],pose=native.ram[0x400],animation=native.ram[0x6a0]))
        (out/f'{name}-trajectory.json').write_text(json.dumps(rows,separators=(',',':'))+'\n')
        results.append(dict(case=name,ticks=ticks,states=sorted(states),tile_probes=len(nquery),minimum_Y=min(r['Y']for r in rows),maximum_X=max(r['X']for r in rows),source_cycles_max=max(source_cycles),component_cycles_max=max(component_cycles),source_and_component_state_equal_bytes=len(mapping),all_ordered_tile_queries_equal=True,trajectory_sha256=sha(out/f'{name}-trajectory.json')))
    paths={r['case']:json.loads((out/(r['case']+'-trajectory.json')).read_text())for r in results}
    assertions=[]
    def check(name,passed,evidence):
        assert passed,(name,evidence)
        assertions.append(dict(name=name,pass_=True,evidence=evidence))
    check('solid wall clamps body atX152',max(r['X']for r in paths['run_into_wall'])==152,dict(maximum_X=152,wall_left=160))
    p=paths['wall_climb'];check('falling into wall enters12 and Aedge jumps from it',p[94]['state']==12 and p[95]['state']==6 and p[95]['vy']==[4,223],dict(before=p[94],after=p[95]))
    check('wall jumps climb above initial head position',min(r['Y']for r in p)<80,dict(minimum_Y=min(r['Y']for r in p),initial_Y=p[0]['Y']))
    f=paths['fast_wall_climb'];check('previous Down latch changes walljump speed to2.C0',p[95]['vx']==[1,192]and f[95]['vx']==[2,192]and f[94]['down_latch']==32,dict(normal=p[95],fast=f[95]))
    k=paths['wall_kick_away'];check('opposite direction and Aedge leaves wall leftward',k[94]['X']==152 and k[95]['X']==150.25 and k[95]['state']==6,dict(before=k[94],after=k[95]))
    for name,expected in [('held_A_single_edge',[5]),('A_release_repress',[5,50,100])]:
        starts=[r['tick']for r in paths[name]if r['vy']==[4,223]and r['state']==6]
        check(name+' jump-store ticks',starts==expected,dict(actual=starts,expected=expected))
        check(name+' low ceiling bonks atY155',min(r['Y']for r in paths[name])==155,dict(minimum_Y=155,ceiling_bottom=144))
    for name in ['wall_climb','wall_kick_away','left_page_cross']:
        check(name+' heldB produces complete three-shot fan',any(r['active_projectiles']==[2,3,4]for r in paths[name]),dict(three_shot_ticks=sum(r['active_projectiles']==[2,3,4]for r in paths[name])))
    s=paths['moving_support'];riding=[r for r in s if r['support']]
    check('native support landing aligns body at top minus12',len(riding)>20 and all(r['Y']==132 for r in riding),dict(support_ticks=len(riding),first=riding[0],last=riding[-1]))
    check('support velocity carries an idle player horizontally',s[119]['X']==226.75 and s[119]['held']==0 and s[119]['support']==1,dict(landing=riding[0],before_input=s[119],platform_velocity=[0,64]))
    report=dict(status='ALL_CONTROLLER_STREAMS_SOURCE_DIFFERENTIAL_PASS',cases=results,semantic_assertions=assertions,fixtures='Actual original CX instructions and native32x32-stage format data versus relocated ca65 source component and real6502 host tile callback. No native emulator and no game-clear/unlock claim.',native_original_ROM_sha256=q.sha(q.ROM),component_sha256=sha(O/'bench/component-fixture.bin'))
    (out/'differential.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':
    info,mapping,labels,stage=compile();print('compiled',info['state_bytes'],'RAM',len((O/'bench/component-fixture.bin').read_bytes()),'fixture image bytes',hex(labels['QuickManTick']));d=differential(info,mapping,labels,stage);print(d['status'])
