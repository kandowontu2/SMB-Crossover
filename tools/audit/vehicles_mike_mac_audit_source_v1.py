"""Current-hash bounded original-ROM gear/tier and assembled mode/audio audit."""
from pathlib import Path
import argparse, hashlib, itertools, json, sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools/audit'))
from vehicles_mike_mac_audit_cpu_v1 import Arena
from check_tmnt_render_oa import load, address
from verify_native_relocation import NesMPU


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def original_call(cpu, pc, traps=()):
    cpu.pc, cpu.sp = pc, 0xfd
    cpu.stPushWord(0x5aff)
    events = []
    for _ in range(10000):
        if cpu.pc == 0x5b00:
            return events
        if cpu.pc in traps:
            events.append((cpu.pc,cpu.a))
            cpu.pc=cpu.stPopWord()+1
        else:
            cpu.step()
    raise AssertionError(('original timeout',hex(pc),hex(cpu.pc)))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--source-root',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    bundle=load(a.rom)
    originals={name:Path('C:/NES')/name for name in [
        'Gradius (USA).nes','Parodius Da! (Japan).nes','StarTropics (USA).nes',
        'Teenage Mutant Ninja Turtles (USA).nes']}
    proof=dict(ROM_sha256=sha(a.rom),tool_sha256=sha(Path(__file__)),passed=False,
               original_ROMs={name:sha(p)for name,p in originals.items()},
               cases={},source_files={},
               scope='Bounded actual original-ROM CPU gear/tier comparisons plus current assembled '
                     'mode and audio-family selection. No physical PPU, music listening, full '
                     'controller route, source-complete weapons, or constant frame-rate claim.')
    for stem in ['vic_gear.s','vic_adapter.s','vic_dispatch.s','parodius_adapter.s',
                 'parodius_render.s','tmnt_core.s','tmnt_combat.s','tmnt_equipment.s',
                 'tmnt_projectiles.s','mike_jones_core.s','mike_jones_motion.s',
                 'mike_jones_weapons.s','mike_jones_pickups.s','little_mac_core.s',
                 'little_mac_combat.s','little_mac_pickups.s','expanded_audio.s',
                 'gradius_audio.s','guest_audio.s','remaining_audio.s','roster_audio.s']:
        proof['source_files']['src/'+stem]=sha(a.source_root/'src'/stem)
    raw=originals['Gradius (USA).nes'].read_bytes()
    assert sha(originals['Gradius (USA).nes'])=='38c44e0e6f531a2779271f10cd4daa08ee2616c59c49d476b6f4e9dc482bf5f3'
    native=raw[16:32784]
    fields=[(0x35,'VvAutoFire'),(0x40,'VvSpeed'),(0x41,'VvMissile'),(0x42,'VvMeter'),
            (0x44,'VvGun'),(0x45,'VvOptions'),(0x46,'VvShield')]
    count=0
    for alive,held,meter,speed,missile,gun,options,shield in itertools.product(
            [0,1],[0,0x40],range(7),[0,255],[0,1],range(3),range(3),[0,5]):
        c=NesMPU();c.memory[0x8000:]=native;c.memory[0x100]=alive;c.memory[7]=held
        q=Arena(bundle);q.put(VvAlive=alive,VvHeld=held)
        values=[20,speed,missile,meter,gun,options,shield]
        for (at,name),value in zip(fields,values):
            c.memory[at]=value;q.set(name,value)
        events=original_call(c,0x8974,[0xec1e,0x8a30,0x8455,0x845b])
        q.call('VvBuyUpgrade')
        for at,name in fields:assert c.memory[at]==q.get(name),(name,values,c.memory[at],q.get(name))
        sounds=[v for pc,v in events if pc==0xec1e]
        assert q.get('VvSfxEvent')==(sounds[-1]if sounds else 0)
        count+=1
    proof['cases']['Gradius_original_8974_upgrade_ownership_speed_wrap']=count
    count=0
    for meter,digit in itertools.product(range(7),[0,5,15,16,21,255]):
        c=NesMPU();c.memory[0x8000:]=native;c.memory[0x42]=meter;c.memory[0x35]=20;c.memory[0x7e5]=digit
        q=Arena(bundle);q.put(VvMeter=meter,VvAutoFire=20,VvScoreDigit=digit)
        events=original_call(c,0x894b,[0xec1e,0x8a30,0x8455,0x845b]);q.call('VvTakeCapsule')
        assert(c.memory[0x42],c.memory[0x35])==(q.get('VvMeter'),q.get('VvAutoFire'))
        assert q.get('VvScoreBonus')==int(any(pc==0x8455 and v==0x10 for pc,v in events))
        count+=1
    proof['cases']['Gradius_original_894B_capsule_meter_rapidfire_bonus']=count
    # The source's late equipment/HP recomputation is compared to actual USA
    # bank26:A783. The A7B8 graphics tail is observed as an external event.
    raw=originals['StarTropics (USA).nes'].read_bytes();count=0
    for owned,hp,prior in itertools.product([1,2,3],range(1,45),[1,2,3]):
        if owned==1 and prior!=1:continue
        c=NesMPU();c.memory[0xa000:0xc000]=raw[16+26*8192:16+27*8192]
        c.memory[0x128]=owned;c.memory[0x112]=hp;c.memory[0x120]=prior
        original_call(c,0xa783,[0xa7b8])
        q=Arena(bundle);q.put(JnOwnedTier=owned,JnHealth=hp,JnTier=prior);q.call('JnEffectiveTier')
        assert q.get('JnTier')==c.memory[0x120],(owned,hp,prior,q.get('JnTier'),c.memory[0x120])
        count+=1
    proof['cases']['StarTropics_original_bank26_A783_health_weapon_tier']=count
    # Existing native weapon selection only offers stocked equipment and
    # always includes the normal primary attack.
    count=0
    for mask in [0,1,2,5,0x155,0x2aa,0x3ff]:
        choices=[0]+[i+1 for i in range(10)if mask&(1<<i)]
        for selected in choices:
            q=Arena(bundle);q.put(JnSelected=selected,SelectedCharacter=16,
                                  SavedJoypadBits=address(bundle,'Select_Button'),JnPrevious=0)
            for i in range(10):q.set('JnAmmo',20 if mask&(1<<i) else 0,i)
            q.call('JnInputs')
            assert q.get('JnSelected')==choices[(choices.index(selected)+1)%len(choices)]
            count+=1
    proof['cases']['Mike_select_cycles_only_stocked_weapons_and_primary']=count
    count=0
    for name,char,variant in [('TnBodyDispatch',19,0),('JnBodyDispatch',16,0),
                              ('LmBodyGate',15,0),('VvBody',18,0),('VvBody',18,1)]:
        for mode,area in itertools.product([0,1],range(4)):
            q=Arena(bundle);q.put(SelectedCharacter=char,VvVariant=variant,
                                  CrossoverBehaviorVersion=mode,AreaType=area)
            q.call(name)
            want=(0,1)if char==18 else(area,mode)
            assert(q.get('GuestBodyStompAllowed'),q.get('GuestBodyNoStomp'))==want,(name,mode,area)
            count+=1
    proof['cases']['mode_stomp_admission_flags_only']=count
    # Inspect the real assembled selection, avoiding an inference solely from
    # a source routine's name. This is an observed missing music wiring issue.
    audio=[]
    for name,char,variant in [('Mac',15,0),('Mike',16,0),('Vic',18,0),
                              ('Octopus',18,1),('TwinBee',18,2),('Pentarou',18,3),
                              ('TMNT',19,0)]:
        q=Arena(bundle);q.put(SelectedCharacter=char,VvVariant=variant)
        c=q.call('KbAudioFamily')
        family=c.a
        audio.append(dict(character=name,character_ID=char,variant=variant,
                          generic_family=family,
                          dispatch='native Gradius via VgAudioDispatch'if char==18 and variant==0 else'generic ExpandedAudioTick',
                          issue=None if char==18 and variant==0 else
                          'Falls back to '+('Rygar'if family==7 else'Pit')+' playlist rather than its own source music.'))
    proof['cases']['audio_family_machine_code_inspections']=len(audio)
    proof['audio_selection']=audio
    proof['observed_open_issues']=['Mac, Mike, Parodius alternates and TMNT currently select fallback music families. '
                                   'Historical TMNT native audio symbol is absent from this current build. '
                                   'This audit does not repair or qualify audio.']
    proof['passed']=True
    (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps({k:v for k,v in proof.items()if k!='source_files'},indent=2))


if __name__=='__main__':main()
