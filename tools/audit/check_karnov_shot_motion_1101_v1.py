"""Original actor→projectile order through actual native host controller service."""
from pathlib import Path
import hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import battletoads_current_loader_controls_v1 as L
import ff_wram_host_controls_v7 as H
from check_tmnt_render_oa import address
from check_karnov_actor_1101_v1 import Memory
from verify_native_relocation import NesMPU
from recover_karnov_actor_1101_v1 import ROM
O=R/'build/karnov-host-resource-base-1101-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    q=dict(passed=False,source_CPU=True,native=False,installed=False,menu_admitted=False)
    try:
        stage=json.loads((O/'terrain-assembly.json').read_text());assert stage['passed']and stage['render']
        for p,h in stage['bindings'].items():assert sha(p)==h,p
        b=H.C.qualified(O/'candidate.nes');raw=ROM.read_bytes();digest=hashlib.sha256();compared=0
        def start(m,row,**kw):
            c=H.start(m,'KrServiceVeneers',**kw);at=address(b,'KrServiceVeneers')+3*row
            m[address(b,'FarcallJmpTarget_SMC')+1]=at&255;m[address(b,'FarcallJmpTarget_SMC')+2]=at>>8;return c
        def call(m,row,**kw):return H.finish(m,start(m,row,**kw))[0]
        seed=L.make(b);H.put(seed,SelectedCharacter=7,FmAlts=1,Player_Y_Position=176,Player_Y_HighPos=1,Player_State=0,Player_X_Position=120,Player_PageLoc=0,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0)
        c,_=L.call(seed,'KrLoad');assert c.p&1;c=call(seed,15);assert c.p&1
        def step(m):
            nonlocal compared
            pending=[];references=[]
            def hook(mem,c,i):
                nonlocal compared
                if c.pc==address(b,'KrSourceFrame'):
                    n=Memory();n[:2048]=mem.ram[2][:2048];n[0xa000:0xc000]=raw[16+11*8192:16+12*8192];n[0xc000:]=raw[16+14*8192:16+16*8192]
                    n[0xfa06:0xfa09]=bytes([0x4c,0x5c,0xfa])
                    for entry in [0xf28d,0xaab2]:
                        nc=NesMPU(memory=n,pc=entry);nc.a,nc.x,nc.y,nc.p,nc.sp=c.a,c.x,c.y,c.p,224;nc.stPushWord(0x5aff)
                        for _ in range(10000):
                            if nc.pc==0x5b00:break
                            if nc.pc in [0xc1c7,0xc81d,0xc3d8]:
                                if nc.pc==0xc3d8:nc.a=0;nc.FlagsNZ(nc.a)
                                nc.pc=(nc.stPopWord()+1)&65535;continue
                            assert n[nc.pc]!=0;nc.step()
                        else:raise AssertionError(('original update bound',hex(entry)))
                    references.append(n)
                if c.pc==address(b,'KrSourceWeapons'):
                    pending.append(((mem[0x101+c.sp]|mem[0x102+c.sp]<<8)+1)&65535)
                if pending and c.pc==pending[0]:
                    pending.pop();n=references.pop();skip=set(range(256,512))|{0x58,0x59,0x7fe,0x7ff}
                    delta=[at for at in range(2048)if at not in skip and n[at]!=mem.ram[2][at]]
                    assert not delta,('actor/projectile state divergence',[(hex(at),n[at],mem.ram[2][at])for at in delta[:8]])
                    digest.update(bytes(mem.ram[2][0x62:0x89]));compared+=1
            c=H.finish(m,start(m,0),hook)[0];assert c.p&1 and not pending and not references
        peaks={};first={}
        for boots,weapon in itertools.product([0,128],[0,1,2,8]):
            m=L.fork(seed);m.ram[2][0x65]=boots|weapon;peak=0
            for tick in range(80):
                held=(64 if tick in [0,6,12,48]else 0)|(128 if 24<=tick<40 else 0)|(1 if tick<60 else 2 if tick<76 else 0)
                H.put(m,FrameCounter=tick,SavedJoypadBits=held);step(m)
                alive=sum(bool(m.ram[2][0x6e+3*n]&128)for n in range(9));peak=max(peak,alive)
                if tick==0:first[(boots,weapon)]=alive
                if H.get(m,'Player_Y_Position')>=176 and H.get(m,'Player_Y_Speed')<128:H.put(m,Player_Y_Position=176,Player_State=0,Player_Y_Speed=0)
                call(m,27)
            assert first[(boots,weapon)]=={0:1,1:2,2:3,8:1}[weapon]
            peaks[str((boots,weapon))]=peak
        camera_cases=[]
        for shotx,newcam,expected in [(50,10,46),(3,10,None),(50,256,None),(50,1,55)]:
            m=L.fork(seed);m.ram[2][0x6e]=0x84;m.ram[2][0x6f]=shotx;m.ram[2][0x70]=120
            H.put(m,ScreenLeft_X_Pos=newcam&255,ScreenLeft_PageLoc=newcam>>8,SavedJoypadBits=0,FrameCounter=1);step(m)
            active=bool(m.ram[2][0x6e]&128)
            assert active==(expected is not None)
            if active:assert m.ram[2][0x6f]==expected
            camera_cases.append(dict(original_X=shotx,camera=newcam,new_X=m.ram[2][0x6f],active=active))
        q.update(passed=True,ROM_sha256=stage['ROM_sha256'],actor_projectile_updates=compared,source_engine_executions=compared*4,weapon_peaks=peaks,camera_cases=camera_cases,trace_sha256=digest.hexdigest(),original_actor_then_weapon_order=True,all_nine_slots_updated=True,scope='Actual linked host input/movement service, original actor and original weapon routines; eight80-update coherent source comparisons including single/double/triple/boomerang, two jump upgrades and release/repress controls. Source physics callbacks have declared empty terrain/sound/scene boundaries. Flat support is a unit fixture. Camera rebasing and offscreen clearing are explicit host adaptations. No earned upgrade, native combat, raster or menu-admission claim.')
    except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
    q['bindings']={str(p.resolve()):sha(p)for p in [Path(__file__),O/'terrain-assembly.json',O/'candidate.nes',O/'candidate.dbg',O/'kr-kernel.bin',ROM]}
    (O/'shot-motion-CPU-controls.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','traceback']}));assert q['passed'],q.get('error')

if __name__=='__main__':main()
