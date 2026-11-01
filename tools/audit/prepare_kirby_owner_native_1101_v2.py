"""Bounded real Main inhale/shell checks with disclosed native actor setup."""
from pathlib import Path
import argparse,json,re,sys
from prepare_selected_native_packet_v1 import R,prepare,sha
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from observe_chip_committed_write import lua
from current_kirby_meta_earned_cpu_v1 import ALLOWED,FORBIDDEN


def once(t,a,b):
    assert t.count(a)==1,(a[:100],t.count(a));return t.replace(a,b)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--rom',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--baseline',action='store_true');a=ap.parse_args();b=scoped_load(a.rom);raw=b['raw']
    template=R/'tools/audit/current_kirby_meta_earned_v1.lua';t=template.read_text()
    t=once(t,'local function setup(task)\n arena()','local function setup(task)\n arena()\n w(\'PlayerFacingDir\',task.face or 1);w(\'Player_MovingDir\',task.face or 1)')
    t=once(t,"not rec.added and r('KbAction')==1 and r('KbActionAge')==0","not rec.added and r('SavedJoypadBits')&64~=0")
    t=once(t,"actor(task.enemy or 6,world()+8,r('Player_Y_Position')+8,0)","actor(task.enemy or 6,world()+((task.face or 1)==1 and 8 or -8),184,0)")
    # Stand the target on the real native208px floor; never align it to the
    # projectile's origin. Both shell powers must cross actual Goomba bounds.
    point=" if task.kind=='sword'then\n"
    t=once(t,point," if task.kind=='copy'and(task.family==2 or task.family==3)then\n  if pool()==0 then return end\n  x=world()+((task.face or 1)==1 and 100 or -80);y=184\n elseif task.kind=='sword'then\n")
    # The old generic component harness intentionally staged an enemy only
    # after warming the inhale. Here every case starts at the freshB edge.
    t=once(t,"assert(C.plan[index].kind=='hurt','Only declared real hurt contact')","assert(C.plan[index].kind=='hurt','Unexpected injury during fresh inhale or grounded shell use')")
    t=once(t,"assert(images<8,'At most8 actual whole-frame screenshots')","assert(images<4,'At most4 actual whole-frame screenshots')")
    t=once(t,"event('update');assert(age<task.limit+120,'Finite current component deadline')",'''if phase=='warm'and rec.added and r('KbMouth')==0 then
  assert(hp()==rec.before.hp,'No injury during the eight-update mouth opening')
  assert(r('Enemy_Y_Position',0)<=184,'Inhaled native enemy stays above the floor')
 end
 event('update');assert(age<task.limit+120,'Finite current component deadline')''')
    t=once(t,"ROM_sha256=C.ROM_sha256,identity=C.identity,", "ROM_sha256=C.ROM_sha256,disclosed_scene_actor_setup=true,no_ability_or_health_seeds=true,identity=C.identity,")
    t=once(t,"scope='Actual native enemy inhale/Down copy, mature food and real hurt; Meta native sword/no inflation. Explicit bounded scene/actor setup; no tested ability/health/input-edge/resource/outcome seeds. No emergence/RNG/star/1up/underwater/allfacings/allpixel/audio-fidelity/full-route claim.'", "scope='Cold real Hard-mode selection, freshB close enemy inhale, actual capture/Down acquisition, then both ground shell powers versus normally grounded Goombas. Disclosed flat native map/player/NPC setup only. No ability, health, shot, input-edge or outcome seeds; hardware DMA/CHR/ISR guards retained. No full-stage or exact-color/audio claim.'")
    mapping=dict(Capture='KbWeapons::Capture',Swallow='KbWeapons::Swallow',CopyAttack='KbWeapons::CopyAttack',Spawn='KbWeapons::Spawn',Pickup='KbPickupDispatch',Heal='KbHealPickup',Injury='KbInjuryStart',BodyContact='KbBodyContact',MetaStart='MkWeapons::Start',DropCopy='KbDropCopy',Defeat='ShellOrBlockDefeat',NmiEntry='NonMaskableInterrupt',IrqEntry='IrqScrollSplit')
    def hook(n,delta=0,size=3):
        at=location(b,n)+delta;k=(at-16)//8192;banks=[k]
        if k==127:
            clone=16+125*8192+(at-16)%8192;assert raw[clone:clone+size]==raw[at:at+size];banks=[125,127]
        return dict(pc=address(b,n)+delta,banks=banks,bytes=list(raw[at:at+size]),source_symbol=n,source_delta=delta)
    hooks={k:hook(n)for k,n in mapping.items()}
    assert raw[location(b,'GameLoop'):location(b,'GameLoop')+5]==bytes([169,255,141,address(b,'NmiDisable')&255,address(b,'NmiDisable')>>8])
    hooks['GameLoopOwned']=hook('GameLoop',5)
    for k,n,op in [('GameLoopFinish','GameLoop',96),('NmiReturn','NonMaskableInterrupt',64),('IrqReturn','IrqScrollSplit',64)]:
        d=int(b['syms'][n]['size'],0)-1;assert raw[location(b,n)+d]==op;hooks[k]=hook(n,d,1)
    mirror=address(b,'Mirror_PPUMASK');load=bytes([165,mirror])if mirror<256 else bytes([173,mirror&255,mirror>>8]);at=location(b,'PostDmaMaskEnable')
    assert raw[at-3:at]==bytes([141,20,64])and raw[at:at+len(load)+3]==load+bytes([141,1,32]);hooks['DmaComplete']=hook('PostDmaMaskEnable',len(load))
    returns=[];dest=address(b,'ShellOrBlockDefeat');jsr=bytes([32,dest&255,dest>>8])
    for n in ['KbWeapons','KbBodyContact','MkWeapons']:
        at=location(b,n);body=raw[at:at+int(b['syms'][n]['size'],0)]
        for i in range(len(body)-2):
            if body[i:i+3]==jsr:returns.append(dict(owner=n,bank=(at-16)//8192,pc=address(b,n)+i+3))
    assert len(returns)==4
    names=set(re.findall(r"'([A-Za-z_][A-Za-z_0-9]*)'",t))|set(ALLOWED)|set(FORBIDDEN)|{'Square1SoundQueue','Square2SoundQueue','NoiseSoundQueue'}
    ram={n:address(b,n)for n in names if n in b['syms']and(address(b,n)<8192 or 0x5c00<=address(b,n)<0x8000)}
    needed=set(re.findall(r"\b[rw]\('([A-Za-z_][A-Za-z_0-9]*)'",t))|set(ALLOWED)|set(FORBIDDEN)
    assert not needed-ram.keys(),sorted(needed-ram.keys())
    edges={k:list(raw[location(b,'X5Menu'+k.title()):location(b,'X5Menu'+k.title())+32])for k in ['left','right','up','down']}
    navigation=[]
    for start in range(32):
        queue=[(start,[])];seen={start}
        for node,route in queue:
            if node==12:navigation.append(route[0]if route else'');break
            for key,table in edges.items():
                z=table[node];assert 0<=z<32
                if z not in seen:seen.add(z);queue.append((z,[*route,key]))
        else:raise AssertionError('Menu route')
    plan=[dict(name='fresh-inhale-spit',kind='spit',face=1,limit=180,image=True),
          dict(name='ground-green-shell',kind='copy',family=2,enemy=address(b,'GreenKoopa'),face=1,limit=430,image=True),
          dict(name='ground-red-shell',kind='copy',family=3,enemy=address(b,'RedKoopa'),face=2,limit=430,image=True)]
    cfg=dict(ROM_sha256=sha(a.rom),identity='kirby',unit='fresh-inhale-and-ground-shells',character=13,variant=0,mode=1,
        ram=ram,hooks=hooks,defeat_returns=returns,plan=plan,setup_allowed={n:True for n in ALLOWED},forbidden=FORBIDDEN,
        navigation=navigation,smc=[address(b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2],
        dma_store_return=address(b,'PostDmaMaskEnable'),metatiles={n:dict(bank=(location(b,n)-16)//8192,offset=(location(b,n)-16)%8192)for n in ['MTileTopLeft','MTileTopRight','MTileBotLeft','MTileBotRight','MTileAttribute']})
    controller='CURRENT_KIRBY_META_EARNED='+lua(cfg)+'\n'+t
    sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'));from lupa.lua54 import LuaRuntime
    ok,error=LuaRuntime(unpack_returned_tuples=True).eval('function(s)local f,e=load(s);return f~=nil,e end')(controller);assert ok,error
    a.output.parent.mkdir(exist_ok=True)
    prepare(a.output,a.rom,controller,[Path(__file__),template,R/'tools/audit/current_kirby_meta_earned_cpu_v1.py',R/'tools/audit/current_rygar_powerups_prepare_v1.py'],
        expected=cfg['ROM_sha256'],timeout=220,scope='Cold Hard-mode Kirby. Flat native terrain/player/NPC fixture at owned Main boundary; real freshB inhale/capture/Down shell acquisition and grounded target defeats. No ability, health, shot, edge or outcome writes. FourPNG cap. Baseline expected to reject startup injury.'if a.baseline else'Cold Hard-mode Kirby with disclosed flat native terrain/player/NPC setup; actual freshB inhale, capture/Down copy and both grounded shell powers. All DMA/CHR/ISR guards retained; no tested ability/health/shot/input-edge/outcome writes. FourPNG cap; not full1-1.')
    p=a.output/'ready.json';q=json.loads(p.read_text());q.update(emulated_writes=True,declared_setup=ALLOWED,forbidden_tested_state=FORBIDDEN,baseline_expected_failure=a.baseline);p.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':main()
