"""Prepare finite actual-earned Kirby/Meta units; no emulator launch."""
from pathlib import Path
import argparse,hashlib,json,re,sys
from current_kirby_meta_earned_cpu_v1 import ALLOWED,FORBIDDEN,EXPECTED,plans,FAMILIES
from link_pit_rygar_sophia_audit_cpu import Arena,scoped_load
from check_tmnt_render_oa import address,location
from observe_chip_committed_write import lua
from current_roster_compact_11_v1 import navigation

ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')
GUARD_SHA='2b3aa5da62ebdd76723bc3ad87991e63695f15ac151213718f58b55f0211d70c'

def classifier_controls(b):
    rows=[]
    for family,(enemy,_)in enumerate(FAMILIES,1):
        q=Arena(b,13);q.set('Enemy_ID',address(b,enemy));q.set('Enemy_Flag',1);q.set('Enemy_State',0)
        c,_=q.invoke('KbFamilyForEnemy',x=0);assert c.a==family
        rows.append(dict(enemy=enemy,ID=address(b,enemy),family=c.a))
    for label,id,flag,state,x in [('absent',6,0,0,0),('duplicate-controller',6,128,0,0),('defeated',6,1,32,0),('flattened-Goomba',6,1,2,0),('unknown',255,1,0,0),('wrong-slot',6,1,0,6)]:
        q=Arena(b,13);q.set('Enemy_ID',id);q.set('Enemy_Flag',flag);q.set('Enemy_State',state)
        c,_=q.invoke('KbFamilyForEnemy',x=x);assert c.a==0,(label,c.a)
        rows.append(dict(negative=label,result=c.a))
    return rows

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--unit',choices=['basics','copies-low','copies-high','meta'],required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output=a.output.resolve()
    assert a.output.is_relative_to(ROOT/'build')and not a.output.exists()
    rom=ROOT/'build/mega_proto_body_palette_9ea.nes';assert sha(rom)==EXPECTED
    fixture=ROOT/'tools/audit/current_kirby_meta_earned_v1.lua';text=fixture.read_text();guard=ROOT/'tools/audit/current_rygar_powerups_v1.lua';old=guard.read_text()
    begin='-- All callback registration is startup-static.';end='emu.addEventCallback(function()\n if not entered'
    block=text[text.index(begin):text.index(end)];assert block==old[old.index(begin):old.index(end)]
    assert len(block.encode())==4058 and hashlib.sha256(block.encode()).hexdigest()==GUARD_SHA
    assert text.count('emu.write(')==2 and 'removeMemoryCallback'not in text and 'dofile('not in text
    assert not set(ALLOWED)&set(FORBIDDEN)
    literal_writes=set(re.findall(r"w\('([A-Za-z_][A-Za-z_0-9]*)'",text));assert literal_writes<=set(ALLOWED)and not literal_writes&set(FORBIDDEN)
    b=scoped_load(rom);raw=b['raw'];plan=plans(a.unit,b);variant=int(a.unit=='meta')
    assert sum(bool(t.get('image'))for t in plan)<=8
    key={'basics':'kirby-basics','copies-low':'kirby-copies-low','copies-high':'kirby-copies-high','meta':'meta-earned'}[a.unit]
    source_path=ROOT/'build'/('current-ab221e-'+key+'-source-v2.json');source=json.loads(source_path.read_text())
    assert source['passed']and source['source_CPU_only']and not source['native_run']and source['ROM_sha256']==EXPECTED and source['unit']==a.unit and source['variant']==variant and source['plan']==plan and source['GameLoop_calls']+30+len(plan)<3000
    # Every accepted defeat was a real native call from one of four actual
    # compiled JSRs, never a same-PC callback reached with a stale slot.
    dest=address(b,'ShellOrBlockDefeat');needle=bytes([32,dest&255,dest>>8]);returns=[]
    for name,wanted in [('KbWeapons',2),('KbBodyContact',1),('MkWeapons',1)]:
        at=location(b,name);n=int(b['syms'][name]['size'],0);body=raw[at:at+n]
        indices=[i for i in range(n-2)if body[i:i+3]==needle];assert len(indices)==wanted
        for i in indices:returns.append(dict(owner=name,bank=(at-16)//8192,pc=address(b,name)+i+3,JSR_pc=address(b,name)+i,bytes=list(needle)))
    for case in source['cases']:
        for d in case['defeats']:assert any(q['pc']==d['return_PC']and q['bank']==d['callerA']for q in returns)
    def hook(n,delta=0,size=3):
        at=location(b,n)+delta;bs=list(raw[at:at+size]);k=(at-16)//8192;banks=[k]
        if k==127:
            clone=16+125*8192+(at-16)%8192;assert raw[clone:clone+size]==bytes(bs);banks=[125,127]
        return dict(pc=address(b,n)+delta,banks=banks,bytes=bs,source_symbol=n,source_delta=delta)
    mapping=dict(Capture='KbWeapons::Capture',Swallow='KbWeapons::Swallow',CopyAttack='KbWeapons::CopyAttack',Spawn='KbWeapons::Spawn',Pickup='KbPickupDispatch',Heal='KbHealPickup',Injury='KbInjuryStart',BodyContact='KbBodyContact',MetaStart='MkWeapons::Start',DropCopy='KbDropCopy',Defeat='ShellOrBlockDefeat',NmiEntry='NonMaskableInterrupt',IrqEntry='IrqScrollSplit')
    hooks={k:hook(v)for k,v in mapping.items()}
    assert raw[location(b,'GameLoop'):location(b,'GameLoop')+5]==bytes([0xa9,255,0x8d,address(b,'NmiDisable')&255,address(b,'NmiDisable')>>8]);hooks['GameLoopOwned']=hook('GameLoop',5)
    for k,n,op in [('GameLoopFinish','GameLoop',0x60),('NmiReturn','NonMaskableInterrupt',0x40),('IrqReturn','IrqScrollSplit',0x40)]:
        delta=int(b['syms'][n]['size'],0)-1;assert raw[location(b,n)+delta]==op;hooks[k]=hook(n,delta,1)
    mirror=address(b,'Mirror_PPUMASK');load=bytes([0xa5,mirror])if mirror<256 else bytes([0xad,mirror&255,mirror>>8]);post=location(b,'PostDmaMaskEnable')
    assert raw[post-3:post]==b'\x8d\x14\x40'and raw[post:post+len(load)+3]==load+b'\x8d\x01\x20';hooks['DmaComplete']=hook('PostDmaMaskEnable',len(load))
    clone_owners={}
    for n in ['NonMaskableInterrupt','OAMandReadJoypad']:
        at=location(b,n);size=int(b['syms'][n]['size'],0);clone=16+125*8192+(at-16)%8192;assert(at-16)//8192==127 and raw[at:at+size]==raw[clone:clone+size];clone_owners[n]=dict(bytes=size,banks=[125,127],sha256=hashlib.sha256(raw[at:at+size]).hexdigest())
    names=set(re.findall(r"'([A-Za-z_][A-Za-z_0-9]*)'",text))|set(ALLOWED)|set(FORBIDDEN)
    ram={n:address(b,n)for n in names if n in b['syms']and(address(b,n)<0x2000 or 0x5c00<=address(b,n)<0x8000)}
    literal=set(re.findall(r"\b[rw]\('([A-Za-z_][A-Za-z_0-9]*)'",text))|set(re.findall(r'C\.ram\.([A-Za-z_][A-Za-z_0-9]*)',text))|set(ALLOWED)|set(FORBIDDEN)
    dynamic=set('Square1SoundQueue Square2SoundQueue NoiseSoundQueue'.split());assert not(literal|dynamic)-ram.keys(),('Missing actual RAM',sorted((literal|dynamic)-ram.keys()))
    assert raw[location(b,'X5MenuCharacters')+12]==13
    cfg=dict(ROM_sha256=EXPECTED,identity='meta'if variant else'kirby',unit=a.unit,character=13,variant=variant,mode=1,ram=ram,hooks=hooks,defeat_returns=returns,plan=plan,setup_allowed={n:True for n in ALLOWED},forbidden=FORBIDDEN,hardware_guard_sha256=GUARD_SHA,dma_store_return=address(b,'PostDmaMaskEnable'),navigation=navigation(raw,lambda n:location(b,n),12),smc=[address(b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2],metatiles={n:dict(bank=(location(b,n)-16)//8192,offset=(location(b,n)-16)%8192)for n in ['MTileTopLeft','MTileTopRight','MTileBotLeft','MTileBotRight','MTileAttribute']})
    a.output.mkdir(parents=True);put(a.output/'config.json',cfg)
    finite=dict(passed=True,Lua_VM_executed=False,source_proof=str(source_path),source_proof_sha256=sha(source_path),source_CPU_tool_sha256=sha(ROOT/'tools/audit/current_kirby_meta_earned_cpu_v1.py'),classifier=classifier_controls(b),actual_defeat_callsite_returns=returns,all_observed_CPU_defeats_match_real_callsites=True,all_literal_dynamic_RAM_names_reconciled=True,forbidden_setup_disjoint=True,hardware_guard=dict(bytes=4058,sha256=GUARD_SHA,whole_clone_owners=clone_owners),source_native_difference='Source supplies normal FrameCounter/video and clock399 only. Native never writes either. Input Down/Select/B is held/read back until real source action/ownership acknowledgment, rather than one-poll hidden booleans.')
    put(a.output/'source-controls.json',finite);(a.output/'run.lua').write_text('CURRENT_KIRBY_META_EARNED='+lua(cfg)+'\ndofile([=['+fixture.as_posix()+']=])\n',newline='\n')
    argv=[sys.executable,'-B',str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(a.output/'native'),'--emulator','C:/Mesen2/Mesen.exe',str(a.output/'run.lua'),str(rom),'--timeout','1200','--option=--doNotSaveSettings','--option=--nes.removeSpriteLimit=false','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false'];put(a.output/'command.json',dict(PREPARED_DO_NOT_RUN=True,ROOT_owns_native_lease=True,argv=argv))
    tools=['current_kirby_meta_earned_cpu_v1.py','current_rygar_powerups_prepare_v1.py','current_roster_compact_11_v1.py','link_pit_rygar_sophia_audit_cpu.py','check_tmnt_render_oa.py','verify_native_relocation.py','observe_chip_committed_write.py','run_mesen_isolated.py','capture_budget.py']
    sources=list((ROOT/'src').glob('kirby*'))+[ROOT/'src'/n for n in ['meta_knight.s','meta_knight_art.inc','roster.s','game.s','object.s','mario_source.s']]
    files=[rom,rom.with_suffix('.dbg'),rom.with_suffix('.lbl'),fixture,Path(__file__),guard,ROOT/'tools/run_mesen.py',ROOT/'chr/characters/kirby.chr',source_path]+[ROOT/'tools/audit'/n for n in tools]+sources+[a.output/n for n in ['config.json','source-controls.json','run.lua','command.json']]+[ROOT/'build'/n for n in ['mm_player_prg_owner_metasprite_engine.s','mm_player_prg_owner_megaman_weapons.s','proto_normal_palette_ack_9ea_source.s','mega_proto_body_palette_9ea_build.json']]
    assert all(p.is_file()for p in files);files=list(dict.fromkeys(files))
    ready=dict(status='PREPARED_DO_NOT_RUN',native_run=False,passed=False,goal_complete=False,ROM_sha256=EXPECTED,identity=cfg['identity'],unit=a.unit,variant=variant,actual_numeric_mode=1,source_CPU_passed=True,source_GameLoop_calls=source['GameLoop_calls'],plan=plan,all_literal_dynamic_RAM_names_reconciled=True,Lua_VM_executed=False,literal_hardware_guard_bytes=4058,literal_hardware_guard_sha256=GUARD_SHA,caps=dict(updates=3000,wall_frames=8000,host_seconds=1200,bytes=2_000_000_000,files=64,PNGs=8),setup='Complete native-boundary logical+visible map/player position/default-health NPCs/mature food actors. Copy acquisition actual warmed inhale/capture/Down; health deficits actual injury. No tested HP, copy, mouth, ability, input-edge, form, tier, shot, resources, timer or outcomes written. No frame tree/copies.',limitations='No native/Lua VM/PPU/cadence/audio-fidelity claim. Mature collection rather than physical reveal/rise. Authored SMB enemy-copy adaptations; Meta has grounded/real-jump sword actions, no inflation/flight. No underwater/drop-star reacquisition/fullpool/star/1up/allfacings/allpixel/fullroute claim.',bindings=[dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))for p in files])
    put(a.output/'prepared-not-run.json',ready);assert all(sha(Path(q['path']))==q['sha256']for q in ready['bindings'])
    print(json.dumps(dict(prepared=True,native_run=False,ready=str(a.output/'prepared-not-run.json'),sha256=sha(a.output/'prepared-not-run.json'),bindings=len(files),source_GameLoops=source['GameLoop_calls'],cases=len(plan))))

if __name__=='__main__':main()
