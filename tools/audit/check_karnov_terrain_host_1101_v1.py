"""Real typed ingress, native query ABI, source-step exports and SMB camera.

Floor/ceiling reconciliation is an explicit unit boundary, not a native stage
playthrough. Character menu and shared gameplay routing remain unmodified.
"""
from pathlib import Path
import hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import battletoads_current_loader_controls_v1 as L
import ff_wram_host_controls_v7 as H
from check_tmnt_render_oa import address
from verify_native_relocation import NesMPU
from check_karnov_actor_1101_v1 import Memory
from recover_karnov_actor_1101_v1 import ROM
O=R/'build/karnov-host-resource-base-1101-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    q=dict(passed=False,source_CPU=True,native=False,installed=False,menu_admitted=False)
    try:
        assembly=json.loads((O/'terrain-assembly.json').read_text());assert assembly['passed']
        post_row=36 if assembly.get('rebound')else 27
        for p,h in assembly['bindings'].items():assert sha(p)==h,p
        b=H.C.qualified(O/'candidate.nes');raw=ROM.read_bytes();original=raw[16+14*8192:16+16*8192]
        def service(m,row,**kw):
            deny_RAM=kw.pop('deny_RAM',False)
            c=H.start(m,'KrServiceVeneers',**kw);target=address(b,'KrServiceVeneers')+row*3
            m[address(b,'FarcallJmpTarget_SMC')+1]=target&255;m[address(b,'FarcallJmpTarget_SMC')+2]=target>>8
            def hook(mem,c,i):
                if deny_RAM:assert not(0xa000<=c.pc<0xc000 and mem.rawtags[1]==3),'Unauthenticated RAM opcode'
            return H.finish(m,c,hook)[0]
        def make(**kw):
            m=L.make(b);H.put(m,SelectedCharacter=7,FmAlts=1);H.put(m,**kw)
            c,_=L.call(m,'KrLoad');assert c.p&1
            c=service(m,15);assert c.p&1 and m.ram[2][address(b,'KrReady')&8191]==167
            return m
        def field(m,n):return m.ram[2][address(b,n)&8191]
        def fresh(m):m.writes.clear();m.ram_writes.clear();return m
        seed=make();image=bytes(seed.ram[3]);foreign=[bytes(z)for z in seed.ram[:2]]
        cookie_checks=0
        for bank,index in [(None,None)]+list(itertools.product([2,3],range(16))):
            m=L.fork(seed)
            if bank is not None:m.ram[bank][0x1fe0+index]^=1
            for f in range(64):
                prior=[bytes(z)for z in m.ram];c,_=L.call(m,'KrCheckCode',p=L.flags(f))
                assert bool(c.p&1)==(bank is None)and[bytes(z)for z in m.ram]==prior
                cookie_checks+=1
        rejected_routes=0;safe_ROM_routes=0
        for bank,index in list(itertools.product([2,3],range(16)))+[(None,0)]:
            m=L.fork(seed)
            if bank is None:H.put(m,FmAlts=0)
            else:m.ram[bank][0x1fe0+index]^=1
            for row in range(assembly.get('service_count',36)):
                prior=[bytes(z)for z in m.ram];fresh(m);c=service(m,row,y=30,deny_RAM=True)
                if assembly.get('menu')and bank is not None and row in [3,17,18,19,26,30,32]:
                    assert[bytes(z)for z in m.ram]==prior and not m.ram_writes;safe_ROM_routes+=1
                else:
                    assert not c.p&1 and(c.a,c.x,c.y)==(85,7,30)and[bytes(z)for z in m.ram]==prior
                    assert not m.ram_writes;rejected_routes+=1
        # Construction is allowed only under the real forced-blank contract.
        cold_negative=[]
        for n,v in [('DisableScreenFlag',0),('Mirror_PPUMASK',30),('NmiDisable',0),('FamilyMainCommit',0)]:
            m=L.fork(seed);H.put(m,**{n:v});prior=bytes(m.ram[2]);c=service(m,15)
            assert not c.p&1 and bytes(m.ram[2])==prior;cold_negative.append(n)
        # Query the actual SMB block buffers using the cache service and the
        # original ordinary query. This verifies complete live return scratch,
        # A/X/Y and the player's unchanged world anchor for every standing probe.
        probes=0
        for page,x,y in itertools.product([0,1,2,255],[0,7,15,16,239,250,255],[32,63,80,143,176,191]):
            for kind,slot,offset in [('head',10,30),('side',14,33),('side',14,34),('side',14,35),('side',14,36)]:
                m=L.fork(seed);H.put(m,Player_PageLoc=page,Player_X_Position=x,Player_Y_Position=y,CrouchingFlag=0)
                for buf in ['Block_Buffer_1','Block_Buffer_2']:
                    at=address(b,buf)
                    for i in range(208):m[at+i]=(i*29+(17 if buf.endswith('1')else 83))&255
                ref=L.fork(m);oldxy=[H.get(m,n)for n in ['Player_PageLoc','Player_X_Position','Player_Y_Position']]
                a=service(m,slot,y=offset);z,_=L.call(ref,'BlockBufferColli_Head'if kind=='head'else'BlockBufferColli_Side',y=offset)
                assert(a.a,a.x,a.y)==(z.a,z.x,z.y),(kind,page,x,y,a.a,z.a,a.x,z.x,a.y,z.y)
                assert a.p&0xcf==z.p&0xcf,(kind,page,x,y,'native flags',a.p,z.p)
                assert bytes(m[5:11])==bytes(ref[5:11]),(kind,page,x,y,'native R2..R7',m[5:11],ref[5:11])
                assert[H.get(m,n)for n in ['Player_PageLoc','Player_X_Position','Player_Y_Position']]==oldxy
                probes+=1
        # Both feet use the game's existing Mega profile, selected by KrAdder.
        m=L.fork(seed);c=service(m,12,y=91);assert c.p&1 and c.y==3
        for crouch,y in itertools.product([0,1],range(32)):
            m=L.fork(seed);H.put(m,CrouchingFlag=crouch,Player_Y_Position=y)
            c=service(m,28,x=7,y=30)
            assert(c.a,c.x,c.y,bool(c.p&1))==(y+(16 if crouch else 8),7,30,y+(16 if crouch else 8)>=32)
        for crouch,y in itertools.product([0,1],[16,24,32,80,176]):
            m=L.fork(seed);H.put(m,CrouchingFlag=crouch,Player_Rel_XPos=70,Player_Rel_YPos=y)
            service(m,16);box=[H.get(m,n)for n in ['BoundingBox_UL_Corner','BoundingBox_LR_Corner']]
            at=address(b,'BoundingBox_UL_Corner');assert bytes(m[at:at+4])==bytes([70,y+(16 if crouch else 8),85,(y+31)&255])
        for hard in [0,1]:
            m=L.fork(seed);H.put(m,CrossoverBehaviorVersion=hard);service(m,11)
            assert H.get(m,'GuestBodyStompAllowed')==1 and H.get(m,'GuestBodyNoStomp')==hard
        movement_negative=[]
        for name,value in [('OperMode',0),('GameEngineSubroutine',7),('GamePauseStatus',1),('CurrentPlayer',1),('NumberofLives',1)]:
            m=L.fork(seed);H.put(m,**{name:value});prior=bytes(m.ram[2]);c=service(m,0)
            assert not c.p&1 and bytes(m.ram[2])==prior;movement_negative.append(name)
        contacts=0
        for source_state,face in itertools.product([8|64,9|64,23,24],[0,128]):
            m=L.fork(seed);m.ram[2][0x62]=source_state|face;m.ram[2][0x66]=17;m.ram[2][0x6a]=55;m.ram[2][0x6b]=3
            H.put(m,Player_State=0);before=[H.get(m,n)for n in ['Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos']]
            service(m,post_row)
            assert m.ram[2][0x62]==face and not any(m.ram[2][i]for i in [0x66,0x6a,0x6b])
            assert[H.get(m,n)for n in ['Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos']]==before;contacts+=1
        for delta in [0,251]:
            m=L.fork(seed);m.ram[2][0x62]=8;m.ram[2][address(b,'KrDeltaY')&8191]=delta
            H.put(m,Player_State=2,Player_Y_Speed=1);service(m,post_row)
            assert m.ram[2][0x62]==72 and not any(m.ram[2][i]for i in [0x66,0x6a,0x6b]);contacts+=1
        m=L.fork(seed);H.put(m,Player_State=2);service(m,post_row);assert m.ram[2][0x62]==23;contacts+=1
        for pose,face in itertools.product([8,9],[0,128]):
            m=L.fork(seed);m.ram[2][0x62]=pose|64|face;m.ram[2][0x66]=17;m.ram[2][0x6a]=12;m.ram[2][0x6b]=4
            m.ram[2][address(b,'KrDeltaY')&8191]=0;H.put(m,Player_State=2,Player_Y_Speed=0)
            service(m,post_row)
            assert [m.ram[2][i]for i in [0x62,0x66,0x6a,0x6b]]==[pose|64|face,17,12,4],'Zero-step fall must advance its source gravity phase'
            contacts+=1
        # Compare every imported actor step to the original executable actor.
        # Only FA06's source-screen clamp is adapted in that explicit oracle;
        # all actual movement/jump/fall bytes/tables remain the original ROM.
        compared=0;digest=hashlib.sha256()
        def movement(m):
            nonlocal compared
            scratch=bytes(m[3:11])
            before=(H.get(m,'Player_X_Position')+256*H.get(m,'Player_PageLoc'),H.get(m,'Player_Y_Position')+256*H.get(m,'Player_Y_HighPos'))
            entering=[];pending=[]
            c=H.start(m,'KrServiceVeneers',y=51);target=address(b,'KrServiceVeneers')
            m[address(b,'FarcallJmpTarget_SMC')+1]=target&255;m[address(b,'FarcallJmpTarget_SMC')+2]=target>>8
            def hook(mem,c,step):
                nonlocal compared
                if c.pc==address(b,'KrSourceFrame'):
                    n=Memory();n[:2048]=mem.ram[2][:2048];n[0xc000:]=original;n[0xfa06:0xfa09]=bytes([0x4c,0x5c,0xfa]);n.writes.clear()
                    nc=NesMPU(memory=n,pc=0xf28d);nc.a,nc.x,nc.y,nc.p,nc.sp=c.a,c.x,c.y,c.p,224;nc.stPushWord(0x5aff)
                    oldx,oldy=n[0x63],n[0x64]
                    for _ in range(8000):
                        if nc.pc==0x5b00:break
                        if nc.pc in [0xc1c7,0xc81d,0xc3d8]:
                            if nc.pc==0xc3d8:nc.a=0;nc.FlagsNZ(nc.a)
                            nc.pc=(nc.stPopWord()+1)&65535;continue
                        assert n[nc.pc]!=0;nc.step()
                    else:raise AssertionError('Original actor bound')
                    ret=(mem[0x101+c.sp]|mem[0x102+c.sp]<<8)+1
                    entering.append(((n[0x63]-oldx+128)%256-128,(n[0x64]-oldy+128)%256-128))
                    pending.append((ret&65535,n))
                if pending and c.pc==pending[0][0]:
                    n=pending.pop()[1];skip=set(range(256,512))|{0x58,0x59,0x7fe,0x7ff}
                    delta=[i for i in range(2048)if i not in skip and n[i]!=mem.ram[2][i]]
                    assert not delta,('native actor state',[(hex(i),n[i],mem.ram[2][i])for i in delta[:8]])
                    compared+=1
            c,_=H.finish(m,c,hook);assert c.p&1 and len(entering)==1 and not pending
            assert bytes(m[3:11])==scratch,'Actor callbacks must preserve native foreground R0..R7'
            dx,dy=entering[0];after=(H.get(m,'Player_X_Position')+256*H.get(m,'Player_PageLoc'),H.get(m,'Player_Y_Position')+256*H.get(m,'Player_Y_HighPos'))
            assert after==((before[0]+dx)&65535,(before[1]+dy)&65535),('world export',before,after,dx,dy)
            assert H.get(m,'Player_X_Scroll')==dx&255
            assert H.get(m,'Player_X_Speed')==dx*16&255
            assert field(m,'KrDeltaX')==dx&255 and field(m,'KrDeltaY')==dy&255
            digest.update(bytes(m.ram[2][0x5e:0x8e]));return dx,dy
        traces=[]
        for boots,page in itertools.product([0,128],[0,1,255]):
            m=L.fork(seed);m.ram[2][0x65]=boots;H.put(m,Player_Y_Position=176,Player_Y_HighPos=1,Player_X_Position=250,Player_PageLoc=page,ScreenLeft_X_Pos=146,ScreenLeft_PageLoc=page,Player_State=0)
            peak=176
            for tick in range(120):
                held=128 if 3<=tick<45 else 0;H.put(m,SavedJoypadBits=held,FrameCounter=tick&255)
                movement(m);peak=min(peak,H.get(m,'Player_Y_Position'))
                # Declared flat floor. This unit does not replace the required
                # native collision/playthrough admission that follows.
                if H.get(m,'Player_Y_Position')>=176 and H.get(m,'Player_Y_Speed')<128:
                    H.put(m,Player_Y_Position=176,Player_Y_HighPos=1,Player_State=0,Player_Y_Speed=0)
                service(m,post_row)
            rise=176-peak;assert rise==(88 if boots else 48),(boots,page,rise)
            traces.append(dict(boots=boots,page=page,rise=rise))
        # Actual native camera routine consumes the exported committed step.
        m=L.fork(seed);H.put(m,Player_X_Position=80,Player_PageLoc=0,Player_Y_Position=176,Player_Y_HighPos=1,Player_State=0,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,ScreenRight_X_Pos=255,ScreenRight_PageLoc=0,Platform_X_Scroll=0,ScrollLock=0,SideCollisionTimer=0)
        maximum_camera=0
        for tick in range(420):
            H.put(m,SavedJoypadBits=1,FrameCounter=tick&255,Player_State=0);movement(m)
            service(m,post_row);L.call(m,'ScrollHandler')
            camera=H.get(m,'ScreenLeft_X_Pos')+256*H.get(m,'ScreenLeft_PageLoc');maximum_camera=max(camera,maximum_camera)
            relative=(H.get(m,'Player_X_Position')+256*H.get(m,'Player_PageLoc')-camera)&65535
            assert relative<=112,('camera drift',tick,relative,camera)
        assert maximum_camera>256
        prior=bytes(m.ram[2]);position=[H.get(m,n)for n in ['Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos']]
        c=service(m,0);assert c.p&1 and bytes(m.ram[2])==prior and[H.get(m,n)for n in ['Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos']]==position
        assert bytes(m.ram[3])==image and[bytes(z)for z in m.ram[:2]]==foreign
        q.update(passed=True,ROM_sha256=assembly['ROM_sha256'],cookie_checks=cookie_checks,corrupt_or_foreign_route_rejections=rejected_routes,safe_ROM_cold_routes=safe_ROM_routes,unauthenticated_RAM_opcodes=0,query_differentials=probes,head_extent_cases=64,landing_ceiling_ledge_boundaries=contacts,movement_negative=movement_negative,duplicate_epoch_no_second_step=True,source_step_comparisons=compared,source_traces=traces,native_camera_updates=420,maximum_camera=maximum_camera,trace_sha256=digest.hexdigest(),typed_query_returns_live=True,player_anchor_never_temporarily_changed_by_queries=True,scope='Actual linked cold loader and genuine36 JMP-row ingress; live child A/X/Y/scratch/flags. Standing head/side queries compared against actual SMB ordinary Mega-profile query. Original actor state and exported world deltas compared with sole declared FA06 viewport adaptation. Flat support and post-collision contact inputs are unit fixtures; actual ScrollHandler executes. Poisoned caches permit only declared immutable ROM UI callbacks in menu mode, never RAM execution. Shared Main/menu tests are separate receipts; no native stage or acoustic claim.')
    except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
    q['bindings']={str(p.resolve()):sha(p)for p in [Path(__file__),O/'terrain-assembly.json',O/'candidate.nes',O/'candidate.dbg',O/'kr-kernel.bin',ROM]}
    (O/'terrain-CPU-controls.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','traceback']}));assert q['passed'],q.get('error')

if __name__=='__main__':main()
