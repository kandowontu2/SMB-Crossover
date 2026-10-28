"""Real ordered RCR movement/BG regression; typed arenas, not native play."""
from pathlib import Path
import hashlib,itertools,json,sys
R=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from prepare_river_city_controls import fresh,address
from verify_native_relocation import NesMPU
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
FIELDS=['Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos',
        'Player_State','Player_Y_Speed','Player_X_Speed','PlayerStatus',
        'BlockBounceTimer','BlockBounceTimer2','Square1SoundQueue','Square2SoundQueue']
def fixture(b,variant=0,mode=0):
    q=fresh(b,variant,mode);q.put(AreaType=1,AreaAddrsLOffset=0);q.invoke('RcGlobalInit');return q
def tile(q,x,y,t):
    base=address(q.b,'Block_Buffer_2'if(x//256)%2 else'Block_Buffer_1')
    assert 32<=y<=224
    q.m[base+(x%256)//16+((y-32)//16)*16]=t
def pipe(q,left):
    for x in range(left-128,left+128,16):tile(q,x,208,0x61)
    for x,t in [(left,0x12),(left+16,0x13)]:
        tile(q,x,144,t)
        for y in (160,176,192):tile(q,x,y,0x14+int(x!=left))
def position(q,x,y,vy=4,face=1,state=1):
    q.put(Player_X_Position=x%256,Player_PageLoc=x//256,Player_Y_Position=y,
          Player_Y_HighPos=1,Player_Y_Speed=vy&255,Player_State=state,
          Player_X_Speed=56 if face==1 else 200,RcLastVx=56 if face==1 else 200,
          RcRun=1,RcPrevious=face,SavedJoypadBits=face,Left_Right_Buttons=face,
          Player_MovingDir=face,PlayerFacingDir=face,ScreenLeft_PageLoc=x//256)
    q.set('MmVY',vy&255,2)
    q.set('MmVX',3 if face==1 else 252,2);q.set('MmVX',128,1)
def state(q):return {k:q.get(k)for k in FIELDS if k in q.b['syms']}
def step(q):
    c,_=q.invoke('RcMovement');cycles=c.processorCycles
    c,_=q.invoke('PlayerBGCollision');return cycles+c.processorCycles
def main():
    old=R/'build/river-city-native-v1.nes';new=R/'build/river-city-native-v2.nes'
    assert sha(old)=='eef91abefad45c6057e15736c8f252c91427ee83e03174e0d74bce473476a913'
    assert sha(new)=='04631d6cf6b3487de2accb5eeb73e439902df111c7c4b65fb4f462437404d1fb'
    bundles=[scoped_load(p)for p in(old,new)];rows=[];deltas=[]
    # Exact real-CPU counterexample from the native negative's contact trace.
    pair=[]
    for b in bundles:
        q=fixture(b);pipe(q,736);position(q,721,142);step(q);pair.append(state(q))
    assert pair[0]['Player_State']==0 and pair[0]['Player_Y_Position']==144
    assert pair[1]['Player_State']!=0 and pair[1]['Player_Y_Position']==146
    rows.append(dict(check='retained-native-pipe-side-counterexample',old=pair[0],new=pair[1]))
    # Real side contacts at both directions, both variants/modes and page seams.
    for variant,mode,left,face,y in itertools.product((0,1),(0,1),(48,240,256,496,752,768),(1,2),(136,142,150,166)):
        q=fixture(bundles[1],variant,mode);pipe(q,left)
        x=left-15 if face==1 else left+32
        position(q,x,y,4,face);cycles=step(q)
        at=q.get('Player_X_Position')+256*q.get('Player_PageLoc')
        assert at<=left-14 if face==1 else at>=left+30,(left,face,y,at)
        assert q.get('Player_State')!=0,(left,face,y,state(q))
        assert q.get('Player_Y_Position')==y+4
        assert q.get('Player_X_Speed')==0
        rows.append(dict(check='vertical-side-does-not-land',variant=variant,mode=mode,pipe=left,face=face,Y=y,after=at,cycles=cycles))
    # Normal open motion, real floor/cap landings and ceiling bumps remain the
    # exact old behavior for both speed signs and crouch. No stubs intercept BG.
    for variant,mode,face,kind in itertools.product((0,1),(0,1),(1,2),('open','floor','cap','ceiling','crouch','coin','vine','hidden','spring','horizontal-pipe')):
        pairs=[];cost=[]
        for b in bundles:
            q=fixture(b,variant,mode)
            position(q,448,110 if kind=='cap'else 174 if kind=='floor'else 174 if kind=='ceiling'else 96,
                     -7 if kind=='ceiling'else 4,face)
            if kind=='floor':
                for x in range(400,512,16):tile(q,x,208,0x61)
            elif kind=='cap':
                for x in range(400,512,16):tile(q,x,144,0x12)
            elif kind=='ceiling':
                for x in range(400,512,16):tile(q,x,160,0xc4)
            elif kind=='crouch':
                q.put(Player_State=0,SavedJoypadBits=4,RcPrevious=4)
                for x in range(400,512,16):tile(q,x,96,0x61)
            elif kind in ('coin','vine','hidden','spring','horizontal-pipe'):
                t={'coin':0xc2,'vine':0x26,'hidden':0x5f,'spring':0x67,'horizontal-pipe':0x1f}[kind]
                for x in range(400,512,16):tile(q,x,112,t)
            cost.append(step(q));pairs.append(state(q))
        assert pairs[0]==pairs[1],(kind,variant,mode,face,pairs)
        if kind in ('cap','floor'):assert pairs[1]['Player_State']==0,(kind,pairs)
        if kind=='ceiling':assert pairs[1]['Player_Y_Speed']<128,pairs
        deltas.append(cost[1]-cost[0]);rows.append(dict(check='native-contact-preserved',variant=variant,mode=mode,face=face,kind=kind,state=pairs[1],additional_CPU=cost[1]-cost[0]))
    # Wrong identity: no application read/write beyond the selector, and no
    # transient state mutation. The private host never calls this for foreigners.
    foreign=[]
    for raw in list(range(21))+[22,23,24,255]:
        q=fixture(bundles[1]);q.put(SelectedCharacter=raw)
        before=bytes(q.m[0:0x100])+bytes(q.m[0x200:0x8000]);q.invoke('RcTerrainWallPrepass')
        after=bytes(q.m[0:0x100])+bytes(q.m[0x200:0x8000]);assert before==after
        foreign.append(raw)
    # Real ISR RTI at each executed instruction in the new side-separation path.
    b=bundles[1];q=fixture(b);pipe(q,736);position(q,724,146);q.set('RcTerrainOldY',142)
    saved=NesMPU.step;pcs=[]
    def record(c):
        if c.pc>=0x8000 and q.m.banks[(c.pc-0x8000)//8192]==81:pcs.append(c.pc)
        saved(c)
    NesMPU.step=record
    try:q.invoke('RcTerrainWallPrepass')
    finally:NesMPU.step=saved
    seams=[]
    for which,target in itertools.product(('NMI','IRQ'),sorted(set(pcs))):
        q=fixture(b);pipe(q,736);position(q,724,146);q.set('RcTerrainOldY',142);fired=[False]
        def interrupt(c):
            if not fired[0]and c.pc==target and q.m.banks[1]==81:
                fired[0]=True;before=(c.a,c.x,c.y,c.p&0xcf,c.sp,c.pc,list(q.m.banks),q.get('CurrentBank'),q.get('CurrentBankC'))
                if which=='NMI':c.nmi()
                else:c.stPushWord(c.pc);c.stPush(c.p&~c.BREAK|c.UNUSED);c.p|=c.INTERRUPT;c.pc=address(b,'IrqScrollSplit')
                for _ in range(20000):
                    saved(c)
                    if c.pc==before[5]and c.sp==before[4]:break
                else:raise AssertionError('RTI timeout')
                after=(c.a,c.x,c.y,c.p&0xcf,c.sp,c.pc,list(q.m.banks),q.get('CurrentBank'),q.get('CurrentBankC'));assert before==after,(which,target,before,after)
            saved(c)
        NesMPU.step=interrupt
        try:q.invoke('RcTerrainWallPrepass')
        finally:NesMPU.step=saved
        if fired[0]:seams.append(dict(kind=which,PC=target))
    out=R/'build/river-city-pipe-contact-controls-v2.json';assert not out.exists()
    proof=dict(passed=True,native_run=False,ROM_sha256=sha(new),retained_negative_ROM_sha256=sha(old),rows=rows,foreign=foreign,ISR_seams=seams,
        additional_CPU_range=[min(deltas),max(deltas)],limits=['Typed legal CPU arenas; native route/PPU/cadence still pending.','New prepass adds CPU; no FPS claim.'],
        bindings=[dict(path=str(p),sha256=sha(p))for p in [Path(__file__),R/'src/river_city_wall_prepass.s',old,new,new.with_suffix('.dbg')]])
    out.write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=True,rows=len(rows),foreign=len(foreign),ISR=len(seams),CPU=proof['additional_CPU_range'])))
if __name__=='__main__':main()
