"""Qualify the direct Mini body-box transport and its source-funded footprint."""

import argparse
from collections import defaultdict
from itertools import product
import json
from pathlib import Path
import subprocess
import tempfile

import check_mini_native_body_box_dispatch_1110 as D
from check_mini_funded_actor_1108_v3 import install, live_stack, registers, run, slim_fork


R, M, N = D.R, D.M, D.N
BASE = R/'build/mini-platform-firebar-native-1110/candidate.nes'
PIN = '6bd5e4b1976e26ecccd9b7c0512944020d6eb7a6e2c8c35ab50c53d0441e7491'
SOURCE = R/'tools/reference/mini_box_transport_1110_v1.s'
LIFECYCLE = R/'src/x5_bounce.s'
PROFILE = R/'build/mini-player-cost-profile-1110/capture/instruction-sample.json'
SPANS = (('STAGE86',0xa2a9,0xa2b8),('LIFE86',0xa2b8,0xa36a),
         ('PROBE86',0xa36a,0xa390),('FALLBACK86',0xa454,0xa463),
         ('RESTORE86',0xa521,0xa52d))
PATCH_SPANS = ((0xa2a9,0xa390),(0xa454,0xa463),(0xa521,0xa52d))
VARS = dict(X5BounceOwner=0x5ff0,X5BounceHi=0x5ff2,SelectedCharacter=0x6002,
            Cv3Variant=0x5fe7,OperMode=0x0771,OperMode_Task=0x0773,
            GameEngineSubroutine=0x0f,MmDeathFlag=0x6007,AreaPointer=0x0755,
            X5BounceArea=0x5ff3,NumberofLives=0x075f,X5BounceLife=0x5ff4,
            WorldNumber=0x0764,LevelNumber=0x0761,X5BounceKey=0x5ff5,
            Player_State=0x1e,Player_Y_Speed=0x8e,JnVY=0x5c08,
            JnJump=0x5c06,JnFallFrac=0x5c07,CdVYHi=0x5c09,CdVYLo=0x5c08,
            Cv3JumpPhase=0x5c03,Cv3JumpActive=0x5c05,Cv3JumpIndex=0x5c02,
            Cv3JumpDelay=0x5c06,Cv3VyLo=0x5c19,Cv3VyHi=0x5c1a,
            X5ClearImpulse=0xa28c)


def rom_slice(raw, bank, lo, hi):
    start = D.offset(bank,lo)
    return raw[start:start+hi-lo]


def replace(text, old, new):
    assert text.count(old)==1,old
    return text.replace(old,new)


def lifecycle_source():
    x5 = LIFECYCLE.read_text()
    assert x5.count('jsr X5BounceLifecycle')==1
    assert 'jmp X5OwnInventoryUi\n  .res 15,$ea' in x5
    assert 'jmp X5NewMovementFinish\n  .res 15,$ea' in x5
    assert 'jmp X5Cv3HorizontalFinish\n  .res 15,$ea' in x5
    assert 'jmp CameraResult\n  .res 12,$ea\nCameraResult:' in x5
    start = x5.index('.proc X5BounceLifecycle\n')
    end = x5.index('.endproc',start)+len('.endproc')
    old = x5[start:end]+'\n'
    new = replace(old,'  jeq Done\n  cmp SelectedCharacter\n  jne Clear\n',
                  '  bne OwnerActive\n  rts\nOwnerActive:\n'
                  '  cmp SelectedCharacter\n  beq OwnerMatches\nEarlyClear:\n'
                  '  jmp Clear\nOwnerMatches:\n')
    first, rest = new.split('  lda GameEngineSubroutine\n',1)
    assert first.count('jne Clear')==2 and first.count('jeq Clear')==1 and first.count('jcs Clear')==1
    first = first.replace('jne Clear','bne EarlyClear').replace('jeq Clear','beq EarlyClear').replace('jcs Clear','bcs EarlyClear')
    assert sum(rest.count(op) for op in ('jne Clear','jeq Clear','jmi Done','jpl Done'))==8
    rest = rest.replace('jne Clear','bne Clear').replace('jeq Clear','beq Clear').replace('jmi Done','bmi Done').replace('jpl Done','bpl Done')
    return old, first+'  lda GameEngineSubroutine\n'+rest


def compile_image(work, body, spans, transport=False):
    cfg,asm,obj,binary,lbl = (work/f'box.{ext}' for ext in ('cfg','s','o','bin','lbl'))
    cfg.write_text('MEMORY {\n'+''.join(f'{name}: start=${lo:04x},size=${hi-lo:x},file=%O;\n'
        for name,lo,hi in spans)+'}\nSEGMENTS {\n'+''.join(f'{name}: load={name},type=ro;\n'
        for name,_,_ in spans)+'}\n',encoding='utf-8')
    definition = '.setcpu "6502"\n.macpack longbranch\n.segment "LIFE86"\n'
    definition += ''.join(f'{name}=${value:02x}\n' for name,value in VARS.items())
    asm.write_text(definition+body+(SOURCE.read_text() if transport else ''),encoding='utf-8')
    cc = R/'tools/Windows/cc65/bin'
    subprocess.run([cc/'ca65.exe',asm,'-o',obj],check=True)
    subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',binary,'-Ln',lbl],check=True)
    labels = {line.split()[2][1:]:int(line.split()[1],16) for line in lbl.read_text().splitlines()}
    data = binary.read_bytes()
    assert len(data)==sum(hi-lo for _,lo,hi in spans)
    return data,labels


def census(raw):
    result = []
    for bank, base in ((86,0xa000),(126,0x8000),(127,0xe000)):
        data = rom_slice(raw,bank,base,base+0x2000)
        for i in range(len(data)-2):
            op = data[i]
            target = int.from_bytes(data[i+1:i+3],'little')
            if op in (0x20,0x4c) and 0xa2b8<=target<0xa390 and not (bank==86 and 0xa2b8<=base+i<0xa390):
                result.append((bank,base+i,target))
    assert result==[(86,0xa29d,0xa2b8),(126,0x83fe,0xa313)],result
    # The fixed-bank match is the original bank-0 MiscObjectsCore, called
    # between the explicitly selected OBJECT window and its endfar restore.
    assert rom_slice(raw,126,0x83b5,0x83c1)==bytes.fromhex('ad450148a9808d45018d1551')
    assert rom_slice(raw,126,0x83fb,0x8417)==bytes.fromhex(
        '2019852013a3208fab20d58520518620dfbf8d4401688d45018d1551')
    game = (R/'src/game.s').read_text().split('GameEngine:\n',1)[1].split('  endfar',1)[0]
    assert '  far OBJECT\n' in game and '    jsr MiscObjectsCore' in game
    return dict(lifecycle_only=result[:1],same_address_other_mapping=result[1:])


def compose(raw, output):
    assert M.sha(raw)==PIN
    assert rom_slice(raw,86,0xa2a9,0xa2b8)==bytes.fromhex('a9bc8d6c01a9b08d6d014c54a4eaea')
    assert rom_slice(raw,86,0xa454,0xa463)==bytes.fromhex('a9c1205a01b0034c4e9f60eaeaeaea')
    assert rom_slice(raw,86,0xa51e,0xa52d)==bytes.fromhex('4c2da5')+b'\xea'*12
    assert rom_slice(raw,85,0xb0bc,0xb0bf)==bytes.fromhex('4cdca8')
    assert rom_slice(raw,65,0xb0bc,0xb0bf)==bytes.fromhex('4c40a7')
    assert rom_slice(raw,126,0x80c2,0x80c9)==bytes.fromhex('8da17d8d165160')
    assert rom_slice(raw,93,0xa73b,0xa743)==bytes.fromhex('a9c8aca2add9d6da')
    callers = census(raw)
    old, new = lifecycle_source()
    with tempfile.TemporaryDirectory(prefix='link-',dir=output) as tmp:
        work = Path(tmp)
        original,_ = compile_image(work,old,(('LIFE86',0xa2b8,0xa390),))
        assert original==rom_slice(raw,86,0xa2b8,0xa390)
        data,labels = compile_image(work,new,SPANS,True)
    patches = []
    for lo,hi in PATCH_SPANS:
        length = hi-lo
        patch,data = data[:length],data[length:]
        patches.append(dict(file_offset=D.offset(86,lo),physical_PRG=86,CPU_half_open=[lo,hi],
                            old_hex=rom_slice(raw,86,lo,hi).hex(),new_hex=patch.hex()))
    assert not data and labels==dict(MiniBoxMiss=0xa454,MiniBoxProbe=0xa36a,
                                     MiniBoxRestore=0xa521,MiniBoxStage=0xa2a9)
    return install(raw,patches),patches,labels,callers


def box_cases(before,after):
    images = D.L.bundles(before,after)
    mini = [D.L.fixture(b,0,False,False) for b in images]
    foreign = [N.fresh(b) for b in images]
    stats = defaultdict(list)
    cases = [(raw,8,1,0x21,'foreign') for raw in range(42) if raw!=41]
    cases += [(41,engine,state,flags,proof) for engine,state,flags,proof in product(
              (4,5,7,8,9,11),(0,1,2),(0x21,0x60,0x65),
              ('active','epoch_stale','epoch_zero','ram2_marker','ram3_marker',
               'ram2_owner','ram3_owner','ram2_tail','ram3_tail'))]
    for owner,engine,state,flags,proof in cases:
        pair = [slim_fork(m) for m in (foreign if proof=='foreign' else mini)]
        for m in pair:
            N.put(m,SelectedCharacter=owner,GameEngineSubroutine=engine,Player_State=state,
                  Player_Y_Speed=4,FrameCounter=7,Player_Rel_XPos=72,Player_Rel_YPos=176,
                  CrossoverBehaviorVersion=0)
            if proof!='foreign':
                m.ram[2][0x3f0] = 7
                if proof=='epoch_stale':
                    m.ram[2][0x3f0] = 6
                elif proof=='epoch_zero':
                    N.put(m,FrameCounter=0)
                    m.ram[2][0x3f0] = 0
                elif proof.startswith('ram'):
                    index = ('marker','owner','tail').index(proof[5:])
                    m.ram[int(proof[3])][0x1fe0+index] ^= 0xff
        a,b = [D.direct(m,0xa703,flags) for m in pair]
        case = (owner,engine,state,flags,proof)
        assert a[0]==b[0],(case,a,b)
        D.compare_memory(*pair)
        assert pair[0][0x15a:0x17b]==pair[1][0x15a:0x17b],(case,a,b)
        for role in ('source','native','foot'):
            assert a[2].get(role)==b[2].get(role),(case,role,a,b)
        hot = proof in ('active','ram2_tail','ram3_tail')
        expected_auth = a[2].get('auth',0) if owner!=41 else int(not hot)
        assert b[2].get('auth',0)==expected_auth,(case,a,b)
        stats[proof].append(a[1]-b[1])
    return {name:dict(cases=len(cost),cycles_saved=[min(cost),max(cost)])
            for name,cost in stats.items()}


def lifecycle_cases(before,after):
    seeds = [N.fresh(b) for b in D.L.bundles(before,after)]
    defaults = dict(OperMode=1,OperMode_Task=3,GameEngineSubroutine=8,MmDeathFlag=0,
                    AreaPointer=35,X5BounceArea=35,NumberofLives=2,X5BounceLife=2,
                    WorldNumber=1,LevelNumber=2,X5BounceKey=6,Player_State=1,
                    Player_Y_Speed=3,X5BounceHi=128,CdVYHi=3)
    flips = {name:value^0xff for name,value in defaults.items()}
    flips.update(Player_State=0,SelectedCharacter=None)
    scenarios = (None,*flips)
    costs = defaultdict(list)
    for owner,cv3,p,change in product((0,1,5,14,16,41),(0,1,2,3,4,255),(0x21,0x60,0x65),scenarios):
        pair = [slim_fork(m) for m in seeds]
        results = []
        for m in pair:
            m.raw_page(1,214)
            N.put(m,CurrentBank=214)
            values = dict(defaults,SelectedCharacter=owner,X5BounceOwner=owner,Cv3Variant=cv3)
            if change:
                values[change] = (owner+1)%42 if change=='SelectedCharacter' else flips[change]
            for name,value in values.items():
                m[VARS[name]] = value
            c = N.NesMPU(memory=m,pc=0xa2b8)
            c.sp,c.a,c.x,c.y,c.p = 230,0x61,0x0a,0x39,p
            c.stPushWord(0x5aff)
            run(c,lambda z:(z.pc,z.sp)==(0x5b00,230))
            results.append((registers(c),live_stack(c),c.processorCycles))
        a,b = results
        assert a[:2]==b[:2],(owner,cv3,p,change,a,b)
        D.compare_memory(*pair)
        costs[str(owner)].append(a[2]-b[2])
    return {owner:dict(cases=len(cost),cycles_saved=[min(cost),max(cost)])
            for owner,cost in costs.items()}


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    args = cli.parse_args()
    out = args.output.resolve()
    assert out.is_relative_to(R/'build') and not (out/'proof.json').exists()
    out.mkdir(exist_ok=True)
    raw = BASE.read_bytes()
    candidate,patches,labels,callers = compose(raw,out)
    box = box_cases(raw,candidate)
    print('Body-box comparison passed.',flush=True)
    life = lifecycle_cases(raw,candidate)
    whole = D.check_full_cpu(raw,candidate,{})
    profile = json.loads(PROFILE.read_text())
    assert json.loads(PROFILE.with_name('binding.json').read_text())['ROM_sha256']==PIN
    assert (profile['scene']['frame'],profile['scene']['x'])==(1452,694)
    refs = (Path(__file__),SOURCE,BASE,LIFECYCLE,D.SOURCE,PROFILE,
            PROFILE.with_name('binding.json'),R/'src/mmc5.s',R/'src/game.s',
            R/'tools/reference/mini_mario_idle_fast.s')
    q = dict(passed=True,ROM_written=False,parent_SHA256=PIN,expected_memory_only_SHA256=M.sha(candidate),
             patches=patches,labels=labels,lifecycle_ingress=callers,lifecycle_freed_bytes=38,
             body_box=box,lifecycle=life,whole_GameCore=whole,
             bindings={p.resolve().relative_to(R).as_posix():M.sha(p.read_bytes()) for p in refs})
    (out/'proof.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in q.items() if k not in ('patches','bindings')},indent=2),flush=True)


if __name__=='__main__':
    main()
