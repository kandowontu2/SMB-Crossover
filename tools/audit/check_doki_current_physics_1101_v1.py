"""Execute current Doki modes against original FDS bytes and preserve USA modes."""
from pathlib import Path
import hashlib,json,re,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location,Memory
from verify_native_relocation import NesMPU
O=R/'build/doki-current-component-1101-v1';D=R/'build/doki-original-rebuild-1031-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    result=dict(passed=False,source_CPU=True,native=False,installed=False)
    try:
        source=json.loads((R/'build/doki-original-physics-audit-1031-v2/audit.json').read_text());port=json.loads((O/'port-assembly.json').read_text())
        for f,h in port['bindings'].items():assert sha(f)==h,f
        rec=json.loads((D/'reproduction.json').read_text());files={q['name']:q for q in rec['disk_files']}
        for name in ['MAIN-PRO','TEMP-PRG']:assert sha(files[name]['extracted'])==files[name]['sha256']
        main=(D/'original-files/main_pro.bin').read_bytes();temp=(D/'original-files/temp_prg.bin').read_bytes()
        old=scoped_load(R/'build/wwf-roster-native-1101-v1/candidate.nes');new=scoped_load(O/'candidate.nes')
        names=['S2Stats','S2X','S2Page','S2XF','S2Y','S2YPage','S2YF','S2VX','S2VY','S2Held','S2Fresh','S2Charge','S2Holding','S2Quicksand','S2Float','S2Clock','S2Air','S2Duck','S2Timer','S2State','S2Animation','S2HeldIndex','S2ObjectType','S2ObjectState','S2ObjectLift']
        keys=list(source['source_functions']['DDP']['fields'])
        assert len(keys)==len(names)
        fields={'DDP':source['source_functions']['DDP']['fields'],'OLD':dict(zip(keys,[address(old,n)for n in names])),'USA':dict(zip(keys,[address(new,n)for n in names])),'DOKI':dict(zip(keys,[address(new,n)for n in names]))}
        functions={'DDP':source['source_functions']['DDP']['func']}
        for k,b in [('OLD',old),('USA',new),('DOKI',new)]:functions[k]={n:address(b,t)for n,t in dict(jump='S2N8C99',gravity='S2N8CD9',X='S2N8EA6',Y='S2N8EA4',action='S2N8C1A',lift='S2N8A87').items()}
        def call(m,pc,*,x=0,stop=0x7fff):
            c=NesMPU(memory=m,pc=pc);c.sp=224;c.p=0x24;c.x=x;c.stPushWord(stop-1)
            for _ in range(30000):
                if c.pc==stop:return c
                assert m[c.pc]!=0,('BRK',hex(c.pc));c.step()
            raise AssertionError(('CPU leaf bound',hex(c.pc)))
        def make(k,v):
            if k=='DDP':
                m=bytearray(65536);m[0x6000:0xe000]=main;m[0x6000:0x65ff]=temp
                at=fields[k]['stats'];m[at:at+23]=bytes(source['stats'][v]['Doki'])
            else:
                b=old if k=='OLD'else new;m=Memory(b);m.page(1,(location(b,'S2NativeStart')-16)//8192)
                for n,value in dict(SelectedCharacter=25,S2Variant=([4,5,7,6]if k=='DOKI'else[0,3,1,2])[v],OperMode=1,AreaType=1,AreaAddrsLOffset=0,WorldNumber=0,NumberofLives=2,Player_X_Position=128,Player_PageLoc=0,Player_Y_Position=180,Player_Y_HighPos=1,Player_Rel_XPos=128).items():m[address(b,n)]=value
                call(m,address(b,'S2ColdInit'))
                assert list(m[fields[k]['stats']:fields[k]['stats']+23])==source['stats'][v]['Doki'if k=='DOKI'else'USA'],(k,v,'Cold stats')
                assert m[address(b,'S2Size')]==0
            return m
        def put(m,k,**data):
            for n,v in data.items():m[fields[k][n]]=v
        def get(m,k,n):return m[fields[k][n]]
        def go(m,k,n):return call(m,functions[k][n])
        counts=dict(jump=0,horizontal=0,lift=0,carry=0);digest=hashlib.sha256()
        for v in range(4):
            for context in range(8):
                for hold in [1,2,8,25,60,180]:
                    traces={}
                    for k in fields:
                        m=make(k,v);put(m,k,y=180,yh=0,vx=8 if context&4 else 0,charge=60 if context&2 else 0,holding=context&1,held=128);go(m,k,'jump');trail=[]
                        for tick in range(240):
                            put(m,k,held=128 if tick<hold else 0,frame=tick&255)
                            if tick:go(m,k,'gravity')
                            go(m,k,'Y');y=get(m,k,'y')+256*get(m,k,'yh');y=y-65536 if y>=32768 else y
                            trail.append([y,get(m,k,'yf'),get(m,k,'vy'),get(m,k,'float')])
                            if tick>1 and y>=180:break
                        traces[k]=trail
                    assert traces['OLD']==traces['USA'],('USA jump regression',v,context,hold)
                    assert traces['DDP']==traces['DOKI'],('Doki jump lineage',v,context,hold)
                    digest.update(json.dumps(traces).encode());counts['jump']+=1
            for pad in [1,2]:
                for run in [0,64]:
                    for carrying in [0,1]:
                        traces={}
                        for k in fields:
                            m=make(k,v);put(m,k,x=128,xh=0,held=pad|run,fresh=0,holding=carrying,obj_type=0,obj_state=1,held_index=0);trail=[]
                            for tick in range(100):
                                value=pad|run if tick<60 else 0 if tick<76 else (3^pad)|run
                                put(m,k,held=value,fresh=0,frame=tick&255);go(m,k,'action');go(m,k,'X')
                                trail.append([get(m,k,n)for n in ['x','xh','xf','vx']])
                            traces[k]=trail
                        assert traces['OLD']==traces['USA'],('USA running regression',v,pad,run,carrying)
                        assert traces['DDP']==traces['DOKI'],('Doki no-run lineage',v,pad,run,carrying)
                        digest.update(json.dumps(traces).encode());counts['horizontal']+=1
            traces={}
            for k in fields:
                m=make(k,v);put(m,k,state=2,timer=0,held_index=0,holding=1,obj_type=0,obj_state=1,lift_timer=7);trail=[]
                for tick in range(200):
                    go(m,k,'lift');trail.append([get(m,k,n)for n in ['state','timer','lift_timer','animation','air','duck']])
                    if get(m,k,'state')==0:break
                    if get(m,k,'timer'):put(m,k,timer=get(m,k,'timer')-1)
                traces[k]=trail
            assert traces['OLD']==traces['USA'] and traces['DDP']==traces['DOKI'],('Timed lift lineage',v)
            counts['lift']+=1
            print('Jump, motion and lift pass: '+source['stats'][v]['name'],flush=True)
        # Carry prefixes include high/low wrap, both facings, crouch, all
        # relevant hitbox branches and three source lift stages.
        labels={}
        for line in(D/'assembled/original.dbg').read_text().splitlines():
            if line.startswith('sym\t'):
                d=dict(re.findall(r'(\w+)=("[^"\n]*"|[^,\n]+)',line))
                if 'val'in d:labels[d['name'].strip('"')]=int(d['val'],0)
        animation_cases=0;size_cases=[];mode_switches=0
        for v in range(4):
            for air in [1,2]:
                rows={}
                for k in fields:
                    m=make(k,v);put(m,k,air=air,duck=0,animation=6)
                    if k=='DDP':
                        ft=labels['timer_player_traction'];phase=labels['player_mov_phase'];entry=labels['player_animate_movement']
                    else:
                        b=old if k=='OLD'else new;ft=address(b,'S2WalkTimer');phase=address(b,'S2WalkFrame');entry=address(b,'S2N8D6F')
                    m[ft]=0;m[phase]=0;call(m,entry);rows[k]=[get(m,k,'animation'),m[ft],m[phase]]
                assert rows['OLD']==rows['USA'] and rows['DDP']==rows['DOKI'],('Air animation lineage',v,air,rows)
                animation_cases+=1
            for k in ['OLD','USA','DOKI']:
                b=old if k=='OLD'else new;m=make(k,v);m[address(b,'S2Health')]=15;m[address(b,'S2Size')]=0
                call(m,address(b,'S2HandlePlayerState'),stop=address(b,'S2HandlePlayerState::Dispatch'))
                row=[m[address(b,n)]for n in ['S2State','S2Size','S2Timer']]
                assert row==([0,0,0]if k=='DOKI'else[8,0,30]),('Original no-shrink branch',v,k,row)
                size_cases.append(dict(character=v,engine=k,state=row))
            m=make('USA',v);m[address(new,'S2Health')]=15;m[address(new,'S2Size')]=1
            for mode,want_size in [([4,5,7,6][v],0),([0,3,1,2][v],1)]:
                m[address(new,'S2Variant')]=mode;call(m,address(new,'S2Ensure'))
                assert m[address(new,'S2Size')]==want_size and m[address(new,'S2Health')]==15
                want=source['stats'][v]['Doki'if mode>=4 else'USA'];at=address(new,'S2Stats');assert list(m[at:at+23])==want
                mode_switches+=1
        f={'x':'pos_x_lo_player','xh':'pos_x_hi_player','y':'pos_y_lo_player','yh':'pos_y_hi_player','face':'player_dir','animation':'player_ani_frame','heldstage':'timer_actor_held','hitbox':'col_box_actor','actorindex':'actor_index','actorX':'pos_x_lo_actor','actorXH':'pos_x_hi_actor','actorY':'pos_y_lo_actor','actorYH':'pos_y_hi_actor','actorface':'disp_dir_actor'}
        hf={'x':'S2X','xh':'S2Page','y':'S2Y','yh':'S2YPage','face':'S2Face','animation':'S2Animation','heldstage':'S2ObjectLift','hitbox':'S2ObjectHitbox','actorindex':'S2Source12','actorX':'S2X','actorXH':'S2Page','actorY':'S2Y','actorYH':'S2YPage','actorface':'S2ObjectFacing0'}
        ending=json.loads((R/'build/doki-carry-geometry-controls-1031-v4/controls.json').read_text())['Doki_prefix']['CPU'][1]
        carryfields={k:({n:labels[t]for n,t in f.items()}if k=='DDP'else{n:address(old if k=='OLD'else new,t)+(1 if n in ['actorX','actorXH','actorY','actorYH']else 0)for n,t in hf.items()})for k in fields}
        for v in range(4):
            for face in [0,1]:
                for crouch in [0,4]:
                    for stage in [1,4,7]:
                        for y in [0,13,14,100,250]:
                            for hitbox in [0,2,3]:
                                rows={}
                                for k in fields:
                                    m=make(k,v);z=carryfields[k]
                                    for n,val in dict(x=255,xh=1,y=y,yh=0,face=face,animation=crouch,heldstage=stage,hitbox=hitbox,actorindex=0).items():m[z[n]]=val
                                    b=old if k=='OLD'else new;entry=labels['actor_throw']if k=='DDP'else address(b,'S2O960F');stop=ending if k=='DDP'else address(b,'S2CarryGeometryReturn')
                                    call(m,entry,stop=stop);rows[k]=[m[z[n]]for n in ['actorX','actorXH','actorY','actorYH','actorface']]
                                assert rows['OLD']==rows['USA'],('USA carry regression',v,face,crouch,stage,y,hitbox,rows)
                                assert rows['DDP']==rows['DOKI'],('Doki carry lineage',v,face,crouch,stage,y,hitbox,rows)
                                digest.update(json.dumps(rows).encode());counts['carry']+=1
        result.update(passed=True,candidate=sha(O/'candidate.nes'),counts=counts,engine_executions=4*sum(counts.values()),air_animation_contexts=animation_cases,health_transition_prefixes=size_cases,same_class_mode_switches=mode_switches,trace_sha256=digest.hexdigest(),scope='Actual original FDS jump/gravity/Q4 action and carry-prefix execution against assembled current Doki modes; original four USA modes compared to installed81 parent. Air animation, no-shrink prefixes and same-native-class lineage changes also checked. Declared collisionless/lift/carry fixtures; no native/menu/graphics/new-identity admission or full-level claim.')
    except Exception as e:result.update(failure=repr(e),traceback=traceback.format_exc())
    result['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),O/'candidate.nes',O/'candidate.dbg',O/'port-assembly.json',D/'original-files/main_pro.bin',D/'original-files/temp_prg.bin']}
    (O/'physics-controls.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in result.items()if k!='bindings'}));assert result['passed']


if __name__=='__main__':main()
