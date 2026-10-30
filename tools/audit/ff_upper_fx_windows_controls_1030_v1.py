"""Actual FF source descriptors and final NMI-published world/spell patterns."""
from pathlib import Path
import hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import ff_joint_body_palette_controls_1030_v1 as P
import ff_joint_native_flash_controls_1030_v3 as F
import ff_host_pickups_vectors_v2 as V
from check_tmnt_render_oa import address,location
H=P.H;M=P.M;sha=P.sha
O=R/'build/ff-upper-fx-windows-1030-v1';H.O=O/'joint'
OLD=R/'build/ff-joint-native-flash-1030-v1'


def window(tile):return(tile>>6)+4*(tile&1)


def source_catalog(b):
    raw=b['raw'];rows=[];windows=set()
    assert address(b,'MOUSE_DISPLAY_CURSOR')==0
    assert not any(n.startswith('MetaspriteData_MOUSE_')for n in b['syms'])
    for face in['Left','Right']:
        lo=location(b,'MetaspriteTable'+face+'Lo');hi=location(b,'MetaspriteTable'+face+'Hi')
        for ident in range(1,address(b,'METASPRITE_MEGAMAN_STANDING')):
            ptr=raw[lo+ident]+256*raw[hi+ident]
            assert 0xa000<=ptr<0xc000,(face,ident,ptr)
            at=16+4*8192+ptr-0xa000;count=raw[at];assert count%4==0 and count<=252
            used=sorted({window(raw[at+1+i])for i in range(0,count,4)})
            assert all(i<=4 for i in used),(face,ident,used)
            windows.update(used);rows.append([face,ident,count//4,used])
    assert len(rows)==288 and windows==set(range(5))
    return dict(passed=True,compiled_native_records=len(rows),windows=sorted(windows),
                actual_compiled_mouse_disabled=True,rows=rows)


def canonical(b):
    m=P.seed(b);rows={}
    for entry,face in itertools.product(range(144,158),[1,2]):
        for chunk in range(8):
            H.put(m,FfSlot=face)
            c,_=H.invoke(m,'FwRenderChunk',a=entry,x=chunk,y=0)
            if not c.p&1:break
            at=address(b,'FfRenderBuffer');count=m[at]
            rows[(entry,face,chunk)]=(list(m[at:at+count+1]),H.get(m,'FfRenderPage'))
    assert len(rows)==88
    return rows


def set_projectile(m,slot,entry,face):
    kind,age=(1,entry-144)if entry<147 else(3,entry-147)if entry<152 else(2,entry-152)
    at=address(m.bundle,'FfProjectile')+slot
    for i in range(12):m[at+i]=0
    for i,v in[(0,kind),(1,age),(4,112+slot),(5,0),(7,160),(8,face)]:m[at+i]=v


def frame(base,entries,face,refs,world_kind='mushroom'):
    m=P.duplicate(base);b=m.bundle
    H.put(m,PlayerOutlinesOff=1,NmiDisable=255,ShouldSkipDrawSprites=0,
          VRAM_Buffer1_Offset=0,PlayerFacingDir=face,FrameCounter=0,
          GuestPowerupActive=0,StarInvincibleTimer=0,FfAction=0)
    for i in range(24):m[address(b,'ObjectMetasprite')+i]=0
    for i in range(36):m[address(b,'FfProjectile')+i]=0
    for slot,entry in entries:set_projectile(m,slot,entry,face)
    slot=5 if world_kind=='mushroom'else 0
    meta='METASPRITE_POWERUP_MUSHROOM'if world_kind=='mushroom'else'METASPRITE_GOOMBA_WALKING_1'
    m[address(b,'ObjectMetasprite')+slot+1]=address(b,meta)
    for n,v in[('Enemy_Flag',1),('Enemy_ID',address(b,'PowerUpObject')if world_kind=='mushroom'else 6),
                ('Enemy_State',0x80 if world_kind=='mushroom'else 0),('Enemy_X_Position',192),
                ('Enemy_PageLoc',0),('Enemy_Y_Position',160),('Enemy_Y_HighPos',1),('Enemy_SprAttrib',0)]:
        m[address(b,n)+slot]=v
    H.put(m,PowerUpType=0)
    H.invoke(m,'FwHostGraphics');H.invoke(m,'FwForceColors')
    decoded=[];drawn=[];pending=[];early=None
    buffer=address(b,'FfRenderBuffer')
    def observe(mem,c,i):
        nonlocal early
        # Match both return PC AND original post-JSR depth. Other callbacks
        # can revisit the same return PC inside an outer bank trampoline.
        for p in pending[:]:
            if c.pc==p['return_PC']and c.sp==p['sp']+2:
                pending.remove(p);end=H.get(mem,'CurrentOAMOffset')
                assert end>=p['start']and(end-p['start'])%4==0
                p['parts']=[]
                for logical in range(p['start'],end,4):
                    at=(logical+p['rotation'])&255
                    p['parts'].append(dict(at=at,data=list(mem[512+at:516+at])))
                drawn.append(p)
        if early and c.pc==early[0]and c.sp==early[1]+2:early=None
        raw=mem.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else -1
        if raw==3 and c.pc==address(b,'FfHostDrawShots'):
            early=(mem[0x101+c.sp]+256*mem[0x102+c.sp]+1,c.sp)
        if raw==3 and c.pc==address(b,'FfHostRenderChunk') and H.get(mem,'FfTargetW')in[0,12,24]:
            entry=H.get(mem,'FfTargetX');chunk=H.get(mem,'FfTargetPage');w=H.get(mem,'FfTargetY')
            original,page=refs[(entry,face,chunk)];want=original[:]
            for j in range(1,len(want),4):want[j]|=((w-4)<<6)|1
            got=list(mem[buffer:buffer+mem[buffer]+1])
            assert w in[5,6,7]and got==want,('canonical descriptor',entry,face,chunk,w,got,want)
            decoded.append([entry,chunk,w,page])
        if raw==132 and c.pc==address(b,'MetaspriteRenderLoop'):
            ptr=H.get(mem,'R0')+256*H.get(mem,'R1')
            isfx=bool(ptr==buffer and early and H.get(mem,'FfTargetW')in[0,12,24])
            p=dict(return_PC=mem[0x101+c.sp]+256*mem[0x102+c.sp]+1,sp=c.sp,
                   start=H.get(mem,'CurrentOAMOffset'),rotation=H.get(mem,'RgOamRotation')if H.get(mem,'GuestOamRotationActive')else 0,
                   kind='fx'if isfx else'body'if ptr==buffer else'world')
            if isfx:
                p.update(window=H.get(mem,'FfTargetY'),page=H.get(mem,'FfRenderPage'))
            pending.append(p)
    c,low=F.invoke_drawall(m,observe);assert not pending
    H.put(m,NmiDisable=0)
    cpu=H.NesMPU(memory=m,pc=0x5b00);cpu.a=91;cpu.x=7;cpu.y=133;cpu.p=0x30;cpu.sp=224
    irq=V.interrupt(m,cpu,'NMI')
    assert H.get(m,'Mirror_PPUCTRL')&32,'Actual8x16 sprite mode'
    assert any(a==0x4014 and v==2 for a,v in m.writes),'Actual native OAM DMA'
    raw=b['raw'];chrbase=1048592;world=[];fx=[]
    for p in drawn:
        for q in p['parts']:
            actual=list(m[512+q['at']:516+q['at']])
            assert actual==q['data'],('A later writer replaced admitted OAM',p['kind'],q,actual)
            if actual[0]>=240:continue
            w=window(actual[1]);physical=m.chr_latches[w];off=(actual[1]&0x3e)*16
            pattern=raw[chrbase+physical*1024+off:chrbase+physical*1024+off+32]
            assert len(pattern)==32
            digest=hashlib.sha256(pattern).hexdigest()
            if p['kind']=='fx':
                assert w==p['window']and physical==756+p['page'],('Final FX hardware page',w,physical,p)
                expected=raw[chrbase+(756+p['page'])*1024+off:chrbase+(756+p['page'])*1024+off+32]
                assert pattern==expected
                fx.append([w,physical,actual[1],digest])
            elif p['kind']=='world':
                assert w<=4,('Native world borrowed an FF upper window',actual,w)
                world.append([actual,digest,w,physical])
    assert world,'The native mushroom/Goomba must actually render'
    if entries:assert fx,'The requested source spell must actually render'
    H.exact(m)
    return dict(entries=entries,face=face,world_kind=world_kind,world=world,fx=fx,decoded=decoded,
                hardware=m.chr_latches[:8],CPU=c.processorCycles,minimum_SP=low,normal_NMI_CPU=irq['CPU'])


def hardware(b):
    refs=canonical(b);base=M.setup(b);rows=[]
    baselines={k:frame(base,[],1,refs,k)for k in['mushroom','goomba']}
    for entry,slot,face in itertools.product(range(144,158),[0,12,24],[1,2]):
        r=frame(base,[(slot,entry)],face,refs)
        assert sorted(r['world'])==sorted(baselines['mushroom']['world']),('World pattern changed beside FX',entry,slot,face)
        assert r['hardware'][1:5]==baselines['mushroom']['hardware'][1:5]
        rows.append(r)
    for entries,kind in itertools.product([[(0,144),(12,145),(24,146)],[(0,144),(12,149)],[(0,144),(24,154)]],['mushroom','goomba']):
        r=frame(base,entries,1,refs,kind)
        assert sorted(r['world'])==sorted(baselines[kind]['world'])
        assert r['hardware'][1:5]==baselines[kind]['hardware'][1:5]
        rows.append(r)
    return dict(passed=True,source_canonical_chunks=len(refs),actual_complete_DrawAll_NMI_cases=len(rows),rows=rows,
                final_admitted_FX_patterns_exact=True,world_OAM_patterns_and_windows1_to4_exact_to_noFX=True,
                includes_3_separate_Fire_pages_and_legal_Fire_Ice_Bolt_family_overlaps=True,
                declared_render_fixtures_not_earned_progression=True)


def old_negative(old,new):
    # The unchanged whole-world observer staged a real native mushroom and
    # one Fire in slot0. Show the exact world-window overwrite without
    # pretending this source fixture is a native emulator/campaign result.
    rows=[]
    for b,root in[(old,OLD),(new,O)]:
        prior=H.O;H.O=root/'joint';base=M.setup(b)
        # Current canonical records are identical originalCORE/ART; no copy
        # or register override changes the actual draw behavior.
        refs=canonical(b)
        try:r=frame(base,[(0,144)],1,refs)
        except AssertionError as e:
            if b is new:raise
            rows.append(dict(ancestor=sha(root/'joint/candidate.nes'),expected_failure=str(e)))
        else:
            assert b is new,'The old collision must be reproduced'
            rows.append(dict(successor=sha(root/'joint/candidate.nes'),world=r['world'],hardware=r['hardware']))
        finally:H.O=prior
    return dict(passed=True,old_wrong_window_reproduced=True,rows=rows)


def main():
    out=O/'upper-window-controls-v1.json';assert not out.exists()
    p=dict(passed=False,native=False,admitted=False,checks={})
    try:
        h=json.loads((O/'source-closure.json').read_text())
        for f,v in h['bindings'].items():assert sha(f)==v,f
        old=H.C.qualified(OLD/'joint/candidate.nes');new=H.C.qualified(H.O/'candidate.nes')
        for n,fn in [('native_window_catalog',lambda:source_catalog(new)),('world_and_FX_final_NMI_patterns',lambda:hardware(new)),
                     ('buffered_loader',lambda:dict(passed=True,**H.loader(new))),
                     ('palette_and_ISR_regression',lambda:F.palette_regression(new))]:
            p['checks'][n]=fn();print(n,'PASS',flush=True)
        p['passed']=True
    except Exception as e:p.update(error=repr(e),traceback=traceback.format_exc())
    p['bindings']={str(f.resolve()):sha(f)for f in[Path(__file__),Path(P.__file__),Path(F.__file__),Path(H.__file__),Path(M.__file__),Path(V.__file__),
        O/'source-closure.json',H.O/'candidate.nes',H.O/'candidate.dbg',OLD/'joint/candidate.nes',OLD/'joint/candidate.dbg']}
    target=out if p['passed']else O/'upper-window-controls-negative-v1.json';assert not target.exists()
    target.write_text(json.dumps(p,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(passed=p['passed'],checks=list(p['checks']),error=p.get('error'),path=str(target))),flush=True)
    assert p['passed']


if __name__=='__main__':main()
