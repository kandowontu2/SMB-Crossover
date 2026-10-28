"""Actual linked Mac terrain callers and authenticated mask geometry; no Mesen."""
from pathlib import Path
import argparse,hashlib,itertools,json,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import Arena,scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
HEAD=[(4,12),(5,14),(-6,-7)];LEFT=[2,0,2];RIGHT=[13,15,13]

def fresh(b,v=0,duck=0,worldx=352,y=176,vy=0):
    q=Arena(b,15)
    q.put(MacVariant=v,LmReady=0x4d,LmLife=3,NumberofLives=3,LmArea=0x25,AreaType=1,AreaAddrsLOffset=5,
      WorldNumber=0,LmWorld=0,GamePauseStatus=0,GameEngineSubroutine=8,OperMode=1,
      Player_X_Position=worldx&255,Player_PageLoc=worldx>>8,Player_Y_Position=y,Player_Y_HighPos=1,
      Player_Y_Speed=vy,Player_X_Speed=0,Player_State=1 if vy else 0,PlayerSize=0,PlayerStatus=1,
      RgCrouch=duck,CrouchingFlag=duck,PlayerFacingDir=1,Player_CollisionBits=255,DisableCollisionDet=0,
      GuestHurtTicks=0,BlockBounceTimer=0,ScreenLeft_PageLoc=max(0,(worldx>>8)-1),ScreenLeft_X_Pos=0,
      ScreenRight_PageLoc=worldx>>8,ScreenRight_X_Pos=255,Player_Rel_XPos=96,Player_Rel_YPos=y,
      NmiDisable=255,Sprite0HitDetectFlag=0,DisableScreenFlag=1)
    for n in ['Block_Buffer_1','Block_Buffer_2']:q.array(n,[0]*208)
    return q

def cell(q,x,y,tile):
    assert 32<=y<240
    at=address(q.b,'Block_Buffer_1'if (x>>8)&1==0 else'Block_Buffer_2')
    q.m[at+(x&255)//16+(y//16-2)*16]=tile

def floor(q,y=208):
    for x in range(0,512,16):cell(q,x,y,0xc4)

def pos(q):return q.get('Player_X_Position')+256*q.get('Player_PageLoc'),q.get('Player_Y_Position')

def run(q,name,a=0,x=0,y=0,p=0x30,sp=0xc0):
    s=q.b['syms'][name];g=q.b['segs'][s['seg']];pc=address(q.b,name)
    window=(pc-0x8000)//8192;bank=(int(g['ooffs'],0)-16)//8192
    q.m.page(window,bank)
    if window in (1,2):q.set('CurrentBank'if window==1 else'CurrentBankC',bank|128)
    c=NesMPU(memory=q.m,pc=pc);c.a,c.x,c.y,c.p,c.sp=a,x,y,p,sp;c.stPushWord(0x5aff)
    low=c.sp;pcs=[]
    for _ in range(100000):
        if c.pc==0x5b00:
            assert c.sp==sp,(name,c.sp,sp)
            return c,low,pcs
        pcs.append((c.pc,q.m.banks[(c.pc-0x8000)//8192]if c.pc>=0x8000 else -1));c.step();low=min(low,c.sp)
    raise AssertionError(('timeout',name,hex(c.pc),q.m.banks))

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--parent',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    b=scoped_load(a.rom);old=scoped_load(a.parent);rows=[];counterexamples=[];masks=[];interrupts=[];costs=[]
    seg=next(g for g in b['segs'].values()if g.get('name')=='"LM_CORE"')
    assert int(seg['start'],0)+int(seg['size'],0)<=0xb000,'LM_CORE encroaches proposed Celeste host tail'
    # Genuine bank89 fast endpoints retain their original addresses/spans;
    # the prior copied probes no longer bypass bank93 geometry.
    for n,size,target in [('TnMacHeadProbe',178,'MacRosterTerrainHead'),('TnMacSideProbe',196,'MacRosterTerrainSide')]:
        assert address(b,n)==address(old,n)
        off=location(b,n);code=b['raw'][off:off+size]
        assert code[18:]==bytes([0xea])*(size-18)
        assert code[3:5]==bytes([0xa9,address(b,target)&255])
        assert code[8:10]==bytes([0xa9,address(b,target)>>8])
    for n in ['TnFastHeadGate','TnFastSideGate','TnMacVisibleSideProbe']:
        size={'TnFastHeadGate':43,'TnFastSideGate':43,'TnMacVisibleSideProbe':30}[n]
        newcode=bytearray(b['raw'][location(b,n):location(b,n)+size]);oldcode=old['raw'][location(old,n):location(old,n)+size]
        if n=='TnFastSideGate':
            assert newcode[24]==address(b,'NrSide')&255 and newcode[29]==address(b,'NrSide')>>8
            assert oldcode[24]==address(old,'NrSide')&255 and oldcode[29]==address(old,'NrSide')>>8
            newcode[24],newcode[29]=oldcode[24],oldcode[29]
        assert bytes(newcode)==oldcode,n
    manifest=R/'chr/characters/mac-roster-manifest.json';m=json.loads(manifest.read_text());chrpath=R/'chr/characters/mac-roster.chr';chr_=chrpath.read_bytes()
    for f in m['frames']:
        if f['name']not in ['idle','duck']:continue
        pts=set()
        for part in f['parts']:
            for y in range(16):
                at=(f['page']-668)*1024+(part['tile']+y//8)*16+y%8
                for x in range(8):
                    if ((chr_[at]>>(7-x))&1)|(((chr_[at+8]>>(7-x))&1)<<1):pts.add((part['x']+x,part['y']+y))
        bounds=[min(x for x,y in pts),min(y for x,y in pts),max(x for x,y in pts)+1,max(y for x,y in pts)+1]
        v=m['variant_order'].index(f['family']);d=int(f['name']=='duck')
        assert bounds[0]<=LEFT[v]and RIGHT[v]<bounds[2]and HEAD[v][d]>=bounds[1]and bounds[3]==32
        assert HEAD[v][d]-bounds[1]==2
        masks.append(dict(family=f['family'],pose=f['name'],opaque=len(pts),opaque_bounds_exclusive=bounds,
          logical=[LEFT[v],HEAD[v][d],RIGHT[v],32],padding='2px top inset; symmetric torso inset, not a claim every logical pixel is opaque.'))
    for v,d,face,edge in itertools.product(range(3),[0,1],[1,2],[96,0,250]):
        x=256+edge;q=fresh(b,v,d,x,177,3);floor(q);q.put(PlayerFacingDir=face)
        q.invoke('PlayerBGCollision');assert pos(q)==(x,176)and q.get('Player_State')==0 and q.get('Player_Y_Speed')==0
        rows.append(dict(check='full-BG-floor',variant=v,duck=d,facing=face,worldX=x))
        q=fresh(b,v,d,x);q.invoke('Z2LegacyBoundingBoxGate',x=0,y=0)
        assert q.get('BoundingBox_UL_XPos')==96+LEFT[v]
        assert q.get('BoundingBox_LR_Corner')==96+RIGHT[v]
        assert q.get('BoundingBox_UL_YPos')==(176+HEAD[v][d])&255
        assert q.get('BoundingBox_LR_Corner',1)==208
    for v,d,x,tile in itertools.product(range(3),[0,1],[256,352,510],[0xc4,0x51]):
        h=HEAD[v][d];starty=160-h-2;q=fresh(b,v,d,x,starty,252)
        # A complete ceiling cell range covers centre and both profile edges.
        for at in range(x-16,x+33,16):cell(q,at,144,tile)
        q.invoke('PlayerBGCollision');assert pos(q)==(x,160-h),(v,d,x,tile,pos(q),160-h)
        assert q.get('Player_Y_Speed')==(254 if tile==0x51 else 1),(v,d,x,tile,q.get('Player_Y_Speed'),pos(q))
        if tile==0x51:
            assert q.get('Block_Y_Position')==144 and q.get('Block_Orig_YPos')==112
            assert q.get('Block_PageLoc')==((x+8)>>8)
        rows.append(dict(check='full-BG-ceiling/question',variant=v,duck=d,worldX=x,tile=tile,finalY=160-h,head=160))
    for v,d,side,wall in itertools.product(range(3),[0,1],[1,2],[256,384,512]):
        # Enter a real side cell by2px. No actor position/physics patch after setup.
        x=wall-RIGHT[v]+2 if side==1 else wall+16-LEFT[v]-2
        q=fresh(b,v,d,x);floor(q);q.put(Player_X_Speed=16 if side==1 else 240,PlayerFacingDir=side)
        for y in [144,160,176,192]:cell(q,wall,y,0xc4)
        q.invoke('PlayerBGCollision')
        expected=wall-RIGHT[v]-1 if side==1 else wall+16-LEFT[v]
        assert pos(q)==(expected,176),(v,d,side,wall,pos(q),expected)
        assert q.get('Player_X_Speed')==0 and q.get('Player_CollisionBits')&(side)==0
        rows.append(dict(check='full-BG-pipe-page-side',variant=v,duck=d,side=side,wallX=wall,finalX=expected))
    # Old head above the new art should no longer contact a block at all.
    for v in range(3):
        q=fresh(b,v,0,352,160,252);cell(q,352,144,0xc4);q.invoke('PlayerBGCollision')
        if v<2:assert pos(q)==(352,160)and q.get('Player_Y_Speed')==252
        z=fresh(old,v,0,352,160,252);cell(z,352,144,0xc4);z.invoke('PlayerBGCollision')
        counterexamples.append(dict(variant=v,parent_xy=pos(z),fixed_xy=pos(q),parent_vy=z.get('Player_Y_Speed'),fixed_vy=q.get('Player_Y_Speed')))
    for v,x in itertools.product(range(3),[256,352,510]):
        q=fresh(b,v,1,x,144);floor(q,176);q.invoke('LmStandBlocked');assert q.get('LmResult')==0
        if v<2:
            # Ceiling between standing and duck crown; use an actual cell row.
            y=160-HEAD[v][1];q=fresh(b,v,1,x,y)
            for at in range(x-16,x+33,16):cell(q,at,144,0xc4)
            c,_=q.invoke('LmStandBlocked');assert c.a!=0 and pos(q)==(x,y)
            rows.append(dict(check='standing-expansion-blocked',variant=v,worldX=x,y=y))
        else:
            q=fresh(b,v,1,x,160);cell(q,x,144,0xc4);c,_=q.invoke('LmStandBlocked');assert c.a==0
            rows.append(dict(check='Tyson-no-fake-short-duck',worldX=x))
    # Complete movement caller must consume held Down when standup really
    # expands into a solid crown, then release it once the actual cell clears.
    for v,x in itertools.product(range(3),[256,352,510]):
        y=160-HEAD[v][1];q=fresh(b,v,4,x,y);floor(q,(y+32)//16*16+16)
        for at in range(x-16,x+33,16):cell(q,at,144,0xc4)
        q.put(SavedJoypadBits=0,LmHealth=96,LmHearts=20,Player_State=0,TimerControl=0)
        q.invoke('LmMovementGate')
        assert bool(q.get('RgCrouch'))==(v<2),(v,q.get('RgCrouch'))
        assert q.get('SavedJoypadBits')==0 and pos(q)[0]==x
        for n in ['Block_Buffer_1','Block_Buffer_2']:q.array(n,[0]*208)
        q.put(Player_State=0);q.invoke('LmMovementGate');assert q.get('RgCrouch')==0
        rows.append(dict(check='actual-movement-stand-release',variant=v,worldX=x,Tyson_short_crouch_not_invented=v==2))
    # First actual occupied sample owns R2/R3/R6/R7; a later edge may not
    # replace its address with another tile or cross-page block destination.
    for v,d,edge in itertools.product(range(3),[0,1],['center','left','right']):
        x=250;h=HEAD[v][d];q=fresh(b,v,d,x,160-h-2,252)
        sample=x+8 if edge=='center'else x+LEFT[v]if edge=='left'else x+RIGHT[v]
        # x250 puts left and center on different pages, so all three ordered
        # probes are exercised without mocking the block-buffer helper.
        cell(q,sample,144,0xc4);c,_,pcs=run(q,'TnFastHeadGate',y=0)
        assert c.a==0xc4 and pos(q)==(x,160-h)
        assert q.get('R2')==112
        page=(sample>>8)&1;want=address(b,'Block_Buffer_2'if page else'Block_Buffer_1')+(sample&255)//16
        assert q.get('R6')+256*q.get('R7')==want,(v,d,edge,sample,q.get('R6'),want)
        assert (address(b,'MacRosterTerrainHead'),93)in pcs
        rows.append(dict(check='fast-head-first-hit-pointer',variant=v,duck=d,first=edge,world_column=sample//16,pointer=want))
    # Farcall wrappers preserve complete leaf-return AXYP and caller live
    # stack; only standard five SMC operands/mapper bookkeeping differ.
    for v,d,side,flags in itertools.product(range(3),[0,1],[0,3,4,5,6],[0x30,0x71]):
        outs=[]
        for fn in ['TnFastHeadGate'if side==0 else'TnFastSideGate','MacRosterTerrainHead'if side==0 else'MacRosterTerrainSide']:
            q=fresh(b,v,d,352,176,252 if side==0 else 0);q.put(R0=1,Local_eb=side)
            q.m[0x1c1:0x200]=bytes((i*13+7)&255 for i in range(63));before=bytes(q.m[0x1c1:0x200])
            c,_,_=run(q,fn,a=0x55,x=0,y=side,p=flags)
            assert bytes(q.m[0x1c1:0x200])==before
            outs.append((c.a,c.x,c.y,c.p&207,c.sp,pos(q),bytes(q.m[address(b,'R0'):address(b,'R0')+8])))
        assert outs[0]==outs[1],(v,d,side,flags,outs)
        rows.append(dict(check='fast-bridge-AXYP-SP-live-stack',variant=v,duck=d,side=side,flags=flags))
    for scene in ['head','side']:
        def arena(lag=False):
            q=fresh(b,2,0,352,164,252)if scene=='head'else fresh(b,1,0,371,176)
            if scene=='head':
                for at in [336,352,368]:cell(q,at,144,0xc4)
            else:
                floor(q)
                for yy in [144,160,176,192]:cell(q,384,yy,0xc4)
            q.put(NmiDisable=255 if lag else 0);return q
        _,_,pcs=run(arena(),'PlayerBGCollision')
        names=['TnMacHeadProbe','MacRosterTerrainHead','BlockBufferColli_Head']if scene=='head'else['TnMacSideProbe','MacRosterTerrainSide','LmVisibleSideProbe']
        seams=[next((pc,bank)for pc,bank in pcs if pc==address(b,n))for n in names]
        for kind,lag,(target,targetbank)in itertools.product(['IRQ','NMI'],[False,True],seams):
            q=arena(lag);oldstep=NesMPU.step;fired=[False];interrupt_low=[255]
            smc=[address(b,k)+d for k,d in [('NextBank_SMC',1),('SafecallA_SMC',1),('FarcallJmpTarget_SMC',1),('FarcallJmpTarget_SMC',2),('SafereturnA_SMC',1)]]
            def step(c):
                bank=q.m.banks[(c.pc-0x8000)//8192]if c.pc>=0x8000 else -1
                if not fired[0]and c.pc==target and bank==targetbank:
                    fired[0]=True
                    before=(c.a,c.x,c.y,c.p&207,c.sp,c.pc,tuple(q.m.banks),q.get('CurrentBank'),q.get('CurrentBankC'),bytes(q.m[z]for z in smc),bytes(q.m[0x101+c.sp:0x200]))
                    if kind=='NMI':c.nmi()
                    else:
                        c.stPushWord(c.pc);c.stPush(c.p&~c.BREAK|c.UNUSED);c.p|=c.INTERRUPT;c.pc=address(b,'IrqScrollSplit')
                    for _ in range(50000):
                        interrupt_low[0]=min(interrupt_low[0],c.sp);oldstep(c)
                        if c.pc==before[5]and c.sp==before[4]:break
                    else:raise AssertionError(('interrupt-timeout',scene,kind,hex(c.pc)))
                    after=(c.a,c.x,c.y,c.p&207,c.sp,c.pc,tuple(q.m.banks),q.get('CurrentBank'),q.get('CurrentBankC'),bytes(q.m[z]for z in smc),bytes(q.m[0x101+c.sp:0x200]))
                    assert before==after,(scene,kind,before,after)
                oldstep(c)
            NesMPU.step=step
            try:c,low,_=run(q,'PlayerBGCollision')
            finally:NesMPU.step=oldstep
            assert fired[0];interrupts.append(dict(scene=scene,kind=kind,lag=lag,PC=target,bank=targetbank,entry_SP=192,minimum_SP=min(low,interrupt_low[0]),AXYP_PC_SP_banks_five_SMC_live_stack_exact=True))
    # Foreign full selector returns, compared to the preserved baseline on
    # legal generic noncontact scenes. New Sunny is not retagged as old native.
    for char in range(22):
        if char==15:continue
        for fn,yy in [('LmHeadGate',0),('LmSideGate',3),('Z2WallLegacy',0)]:
            result=[]
            for bundle in [old,b]:
                q=fresh(bundle);q.put(SelectedCharacter=char,R0=1,Local_eb=3)
                c,_=q.invoke(fn,a=char,y=yy)
                result.append((c.a,c.x,c.y,c.p&207,c.sp,pos(q),bytes(q.m[address(bundle,'R0'):address(bundle,'R0')+8])))
            assert result[0]==result[1],(char,fn,result)
            rows.append(dict(check='foreign-full-selector',character=char,function=fn))
    for v,d,scene in itertools.product(range(3),[0,1],['empty','floor','ceiling','pipe']):
        out=[]
        for bundle in [old,b]:
            q=fresh(bundle,v,d,352,176,0)
            if scene=='floor':floor(q);q.put(Player_Y_Position=177,Player_Y_Speed=3)
            if scene=='ceiling':
                q.put(Player_Y_Position=160-HEAD[v][d]-2,Player_Y_Speed=252)
                for at in [336,352,368]:cell(q,at,144,0xc4)
            if scene=='pipe':
                q.put(Player_X_Position=(384-RIGHT[v]+2)&255,Player_PageLoc=1,Player_X_Speed=16)
                floor(q)
                for yy in [144,160,176,192]:cell(q,384,yy,0xc4)
            c,low,_=run(q,'PlayerBGCollision');out.append(dict(cycles=c.processorCycles,minimum_SP=low,xy=pos(q)))
        costs.append(dict(variant=v,duck=d,scene=scene,parent=out[0],candidate=out[1],delta=out[1]['cycles']-out[0]['cycles'],comparison='Same typed input arena; prior geometry/output is intentionally different, so this is CPU cost rather than equivalent gameplay performance.'))
    proof=dict(passed=True,native_run=False,ROM_sha256=sha(a.rom),parent_sha256=sha(a.parent),core_bytes=int(seg['size'],0),
      masks=masks,rows=rows,interrupts=interrupts,costs=costs,old_counterexamples=counterexamples,
      limits=['Typed actual-CPU full-BG arenas, not a native route/PPU/cadence claim.','Logical core uses explicit small insets; sparse glove/hair silhouette is not itself a solid rectangle.'],
      bindings=[dict(path=str(f),sha256=sha(f))for f in [Path(__file__),a.rom,a.rom.with_suffix('.dbg'),a.parent,a.parent.with_suffix('.dbg'),R/'src/little_mac_terrain.s',R/'src/tmnt_mac_probes.inc',manifest,chrpath]])
    a.output.write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=True,cases=len(rows),interrupts=len(interrupts),core_bytes=proof['core_bytes'],BG_cycle_delta=[min(t['delta']for t in costs),max(t['delta']for t in costs)])))
if __name__=='__main__':main()
