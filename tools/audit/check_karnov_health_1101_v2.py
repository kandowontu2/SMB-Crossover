"""Original health/death leaves and genuine native injury/death boundary tests."""
from pathlib import Path
import argparse,hashlib,itertools,json,sys,traceback
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT/'tools/audit'),str(ROOT/'tools')]
import battletoads_current_loader_controls_v1 as L
import ff_wram_host_controls_v7 as H
from verify_native_relocation import NesMPU
from check_karnov_actor_1101_v1 import Memory
from check_tmnt_render_oa import address
from recover_karnov_actor_1101_v1 import ROM,EXPECTED
O=ROOT/'build/karnov-health-component-1101-v2';BASE=ROOT/'build/karnov-host-resource-base-1101-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--integrated',action='store_true');ap.add_argument('--output',type=Path);args=ap.parse_args()
    q=dict(passed=False,component_overlay_only=True,native_emulator=False,installed=False,root_modified=False)
    output=args.output or O/'CPU-controls.json'
    refs=[Path(__file__),ROOT/'tools/reference/karnov_health_1101_v2.inc',BASE/'candidate.nes',BASE/'candidate.dbg',ROM]
    try:
        a=json.loads(((BASE/'terrain-assembly.json')if args.integrated else(O/'assembly.json')).read_text())
        for p,h in a['bindings'].items():assert sha(p)==h,p
        assert sha(ROM)==EXPECTED
        b=H.C.qualified(BASE/'candidate.nes')
        if args.integrated:
            assert a['passed']and a['health']
            labels={n:address(b,n)for n in b['syms']if n.startswith('KrHealth')}
            origin=address(b,'KrHealthOriginal_CB69');size=address(b,'KrHealthEnd')-origin
            blob=(BASE/'kr-kernel.bin').read_bytes()[origin-0xa000:origin-0xa000+size]
            a=dict(a,base_ROM_sha256=a['ROM_sha256'],bytes=size)
            refs += [BASE/'terrain-assembly.json',BASE/'kr-kernel.bin']
        else:
            labels=a['labels'];blob=(O/'component.bin').read_bytes();origin=a['origin']
            refs += [O/'assembly.json',O/'component.bin']
        seed=L.make(b);H.put(seed,SelectedCharacter=34,FmAlts=1)
        c,_=L.call(seed,'KrLoad');assert c.p&1
        def service(m,row,**kw):
            c=H.start(m,'KrServiceVeneers',**kw);pc=address(b,'KrServiceVeneers')+row*3
            m[address(b,'FarcallJmpTarget_SMC')+1]=pc&255;m[address(b,'FarcallJmpTarget_SMC')+2]=pc>>8
            return H.finish(m,c)
        c,_=service(seed,15);assert c.p&1
        # This explicit in-memory component overlay is not a candidate build or
        # a new authenticated loader proof. The real guarded dispatcher runs.
        if not args.integrated:
            seed.ram[3][origin-0xa000:origin-0xa000+len(blob)]=blob
        for row,name in [(5,'KrHealthInjury'),(6,'KrHealthStatus'),(7,'KrHealthDeathStart'),(8,'KrHealthDeathUpdate')]:
            pc=labels[name];expected=bytes([0x4c,pc&255,pc>>8])
            if args.integrated:assert bytes(seed.ram[3][row*3:row*3+3])==expected
            else:seed.ram[3][row*3:row*3+3]=expected
        raw=ROM.read_bytes();fixed=raw[16+14*8192:16+16*8192]
        arena=Memory();arena[0xa000:0xc000]=seed.ram[3];arena[0xe000:0x10000]=bytes(seed[0xe000:0x10000]);arena[0xc000:0xe000]=seed.ram[2]
        for i in range(3,11):arena[i]=(i*37+17)&255
        def sethost(m,**values):
            for n,v in values.items():m[address(b,n)]=v
        def unit(m,pc,p=0x71):
            c=NesMPU(memory=m,pc=pc);c.a,c.x,c.y,c.p,c.sp=85,7,91,p,224;c.stPushWord(0x5ffe);low=c.sp;cycles=c.processorCycles
            for step in range(20000):
                if c.pc==0x5fff:break
                low=min(low,c.sp);assert m[c.pc]!=0,('component BRK',hex(c.pc));c.step()
            else:raise AssertionError(('unit bound',hex(c.pc)))
            assert c.sp==224
            return c,low,c.processorCycles-cycles
        def original(m,pc):
            c=NesMPU(memory=m,pc=pc);c.a,c.x,c.y,c.p,c.sp=85,7,91,0x71,224;c.stPushWord(0x5ffe);events=[]
            for step in range(10000):
                if c.pc==0x5fff:break
                if c.pc==0xc81d:
                    events.append(c.a);c.pc=(c.stPopWord()+1)&65535;continue
                assert m[c.pc]!=0,('donor BRK',hex(c.pc));c.step()
            else:raise AssertionError('source bound')
            return c,events
        digest=hashlib.sha256();pairs=0;status=0;minsp=224
        # Exact original CB69 including palette ring saturation/index, both
        # health polarities, unrelated lower68bits and all128 timer values.
        for health,count,index,flags in itertools.product(range(256),[0,7,8],[0,7],[0x30,0x71]):
            old=Memory();old[0xc000:]=fixed;old[0x68]=health;old[0x69]=37;old[0x70f]=count;old[0x710]=index
            new=Memory();new[:]=arena;new[0xc068]=health;new[0xc069]=37;new[0xc70f]=count;new[0xc710]=index
            oc,_=original(old,0xcb69);nc,low,_=unit(new,labels['KrHealthOriginal_CB69'],flags);minsp=min(minsp,low)
            assert bytes(old[0x34:0x37])==bytes(new[0xc034:0xc037])
            assert old[0x68:0x6a]==new[0xc068:0xc06a]
            assert old[0x70f:0x71a]==new[0xc70f:0xc71a]
            assert oc.a==nc.a
            pairs+=1;digest.update(bytes(new[0xc034:0xc037])+bytes(new[0xc068:0xc06a]))
        for health,selector,flags in itertools.product(range(256),[0,8,25,26,28,29],[0x30,0x71,0xff]):
            m=Memory();m[:]=arena;m[0xc068]=health;m[0xc062]=selector
            before=bytes(m[3:11]);c,low,_=unit(m,labels['KrHealthStatus'],flags);minsp=min(minsp,low)
            expected=int(selector>=25 or bool(health&64)or not bool(health&128))
            assert(c.a,c.x,c.y)==(expected,7,91)and c.p&0x4d==flags&0x4d,(health,selector,flags,c.a,c.x,c.y,c.p)
            assert bool(c.p&2)==(not bool(expected))and bytes(m[3:11])==before
            status+=1
        fatal=0
        for face,y,lock in itertools.product([0,128],[0,16,31,32,144,208,255],[0,1]):
            old=Memory();old[0xc000:]=fixed;old[0x62]=face|8;old[0x64]=y;old[0x5d]=lock
            new=Memory();new[:]=arena;new[0xc062]=face|8;new[0xc064]=y;new[0xc05d]=lock
            _,events=original(old,0xca31);unit(new,labels['KrHealthOriginal_CA31'])
            assert(old[0x62],old[0x64])==(new[0xc062],new[0xc064])
            assert new[0xc801]==(events[-1]if events else arena[0xc801]);fatal+=1
        # Source prefix expiry remains owned by accepted actor updates; injury
        # and status calls themselves consume no source clock or hurt tick.
        prefix=0
        for health,timer in itertools.product([0,64,128,192],range(256)):
            m=Memory();m[:]=arena;m[0xc068]=health;m[0xc069]=timer;m[0xc062]=29
            sethost(m,GameEngineSubroutine=11,FrameCounter=1,MmDeathPit=0,Player_Y_Position=144,Player_Y_HighPos=1)
            m[address(b,'KrHaveEpoch')]=0;clock=m[0xc0e8];before=bytes(m[3:11])
            c,low,_=unit(m,labels['KrHealthDeathUpdate']);minsp=min(minsp,low)
            expected_timer=(timer-1)&255;expected_health=health&191 if expected_timer==0 else health
            assert(m[0xc069],m[0xc068],m[0xc0e8])==(expected_timer,expected_health,(clock+1)&255)
            assert bytes(m[3:11])==before
            # Calling service8 again in this host epoch must not tick twice.
            state=bytes(m[0xc000:0xe000]);unit(m,labels['KrHealthDeathUpdate']);assert bytes(m[0xc000:0xe000])==state
            prefix+=1
        native=[]
        adapter_abi=0;support_cases=0;negative=0
        for name,flags in itertools.product(['KrHealthInjury','KrHealthDeathStart','KrHealthDeathUpdate'],[0x30,0x31,0x71,0xff]):
            m=Memory();m[:]=arena;m[0xc062]=0;m[0xc068]=0
            sethost(m,GameEngineSubroutine=11 if name.endswith('Update')else 8,FrameCounter=4,GamePauseStatus=0,MmDeathPit=0)
            before=bytes(m[3:11]);c,low,_=unit(m,labels[name],flags);minsp=min(minsp,low)
            assert(c.a,c.x,c.y)==(85,7,91)and c.p&0xce==flags&0xce and c.p&1
            assert bytes(m[3:11])==before;adapter_abi+=1
            m=Memory();m[:]=arena;m[address(b,'KrReady')]=0;before=bytes(m[3:11]);state=bytes(m[0xc000:0xe000])
            c,_,_=unit(m,labels[name],flags)
            assert not c.p&1 and(c.a,c.x,c.y)==(85,7,91)and bytes(m[3:11])==before and bytes(m[0xc000:0xe000])==state
            negative+=1
        for tile,x,page in itertools.product(range(256),[120,250],[0,1]):
            m=Memory();m[:]=arena;sethost(m,Player_Y_Position=175,Player_Y_HighPos=1,Player_X_Position=x,Player_PageLoc=page)
            for buf in ['Block_Buffer_1','Block_Buffer_2']:
                at=address(b,buf);m[at:at+208]=bytes([tile])*208
            before=bytes(m[3:11]);unit(m,labels['KrHealthSupport'])
            expected=2 if tile not in [0x5f,0x60]and m[address(b,'MTileAttribute')+tile]&3==1 else 0
            assert m[0xc08b]==expected and bytes(m[3:11])==before,(tile,x,page,expected,m[0xc08b]);support_cases+=1
        for health,playerstatus in itertools.product([0,128,192],[0,2]):
            m=L.fork(seed);H.put(m,GameEngineSubroutine=8,InjuryTimer=0,CheatInvincible=0,GuestHurtTicks=0,MmDeathFlag=0,MmDeathPit=0,PlayerStatus=playerstatus,TimerControl=0,Player_Y_Position=176,Player_Y_HighPos=1,VRAM_Buffer1_Offset=0)
            m.ram[2][0x68]=health;m.ram[2][0x69]=17;m.ram[2][0x62]=0;m.ram[2][0x64]=208
            before=bytes(m[3:11]);c,low=L.call(m,'InjurePlayer');minsp=min(minsp,low)
            if health==0:
                assert m.ram[2][0x68]==192 and m.ram[2][0x69]==128 and H.get(m,'GameEngineSubroutine')==8 and H.get(m,'MmDeathFlag')==0
                assert bytes(m[address(b,'VRAM_Buffer1'):address(b,'VRAM_Buffer1')+7])==bytes([63,17,3,16,28,15,0])
            elif health==128:
                assert H.get(m,'GameEngineSubroutine')==11 and H.get(m,'MmDeathFlag')==1 and m.ram[2][0x62]&31==25
                assert H.get(m,'Player_Y_Position')==144
            else:assert H.get(m,'GameEngineSubroutine')==8 and m.ram[2][0x69]==17 and H.get(m,'MmDeathFlag')==0
            native.append(dict(health=health,PlayerStatus=playerstatus,engine=H.get(m,'GameEngineSubroutine'),minimum_SP=low))
        # Real PlayerDeath -> dispatch8; both feet use actual host block buffers.
        # The original25fall reaches26rest and64source updates finish a life.
        m=L.fork(seed);H.put(m,GameEngineSubroutine=8,Player_Y_Position=176,Player_Y_HighPos=1,MmDeathFlag=1,MmDeathPit=0,GamePauseStatus=0)
        m.ram[2][0x62]=0;m.ram[2][0x65]=2;c,low=service(m,7);assert c.p&1
        floor=0x54
        assert m[address(b,'MTileAttribute')+floor]&3==1
        for buf in ['Block_Buffer_1','Block_Buffer_2']:
            at=address(b,buf)
            for i in range(208):m[at+i]=floor if i>=176 else 0
        trace=[]
        for tick in range(130):
            H.put(m,FrameCounter=tick&255)
            before=bytes(m[3:11]);c,low=L.call(m,'PlayerDeath');minsp=min(minsp,low)
            assert bytes(m[3:11])==before
            trace.append([tick,m.ram[2][0x62]&31,m.ram[2][0x64],m.ram[2][0x66],H.get(m,'GameEngineSubroutine')])
            if H.get(m,'GameEngineSubroutine')==6:break
        assert {25,26}<={t[1]for t in trace}and trace[-1][-1]==6 and m.ram[2][0x65]==0,trace[-8:]
        q.update(passed=True,base_ROM_sha256=a['base_ROM_sha256'],component_bytes=a['bytes'],original_health_leaf_pairs=pairs,original_fatal_leaf_pairs=fatal,source_status_cases=status,source_prefix_timer_epoch_cases=prefix,adapter_AXYP_cases=adapter_abi,context_rejection_cases=negative,native_support_classification_cases=support_cases,native_InjurePlayer_cases=native,native_PlayerDeath_updates=len(trace),native_death_selector_sequence=list(dict.fromkeys(t[1]for t in trace)),minimum_SP=minsp,original_health_death_trace_sha256=digest.hexdigest(),all_R0_R7_preserved=True,native_life_loss_engine=6,source_death_clears_gear=True,scope='Component only overlaid in memory into a genuine loaded/authenticated base kernel; actual native InjurePlayer and PlayerDeath consumers execute. Original health/palette-ring/fatal instructions compared directly to donor. No changed ROM, loader authentication of new bytes, real ISR/SMC cut qualification, acoustic/native emulator or complete character admission claim.')
        if args.integrated:
            q.update(component_overlay_only=False,authenticated_integrated_ROM=True,ROM_sha256=a['ROM_sha256'],scope='The genuine forced-blank loader authenticates and loads the composed health kernel; no RAM code or vector is overlaid. Original donor health/fatal/palette comparisons and actual native injury/death endpoints then execute. No live Main interrupt, emulator, next-life recovery or full-character claim.')
    except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
    q['bindings']={str(p.resolve()):sha(p)for p in refs}
    output.write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','traceback']}));assert q['passed'],q.get('error')
if __name__=='__main__':main()
