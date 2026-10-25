"""Interrupt-qualified native inventory entry/return arenas; explicit staging."""
from pathlib import Path
from collections import deque
import argparse, hashlib, json, subprocess, sys
from check_tmnt_render_oa import load, address, location
from observe_chip_committed_write import lua
from py65.disassembler import Disassembler
from verify_native_relocation import NesMPU

ROOT = Path(__file__).resolve().parents[2]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for n in ['rom', 'output']: p.add_argument('--'+n, type=Path, required=True)
    p.add_argument('--emulator', required=True)
    p.add_argument('--profile', choices=['mega', 'proto', 'bass'], required=True)
    a = p.parse_args(); out = a.output.resolve()
    assert not out.is_relative_to(ROOT)
    out.mkdir(exist_ok=False); b = load(a.rom)
    def hook(n, delta=0):
        at = location(b, n)+delta
        return dict(pc=address(b,n)+delta, bank=(at-16)//8192,
                    code=list(b['raw'][at:at+4]))
    char, proto = (9,0) if a.profile=='bass' else (1,int(a.profile=='proto'))
    names = ['OperMode','OperMode_Task','GameEngineSubroutine','SelectedCharacter',
             'CrossoverMenuState','CrossoverMenuIndex','ProtoVariant','RlVariant',
             'CrossoverBehaviorVersion','GuestHurtTicks','InvPrevious','InvRefill','InvFresh',
             'InvOwnedLo','InvOwnedHi','InvSelected','GamePauseStatus',
             'SavedJoypad1Bits','SavedJoypadBits','PlayerStatus',
             'MmChargeFrames','MmCharging','MmBulletType','MmBulletX','MmBulletPage',
             'MmBulletY','MmBulletDir','MmBulletAge','Player_X_Position',
             'Player_PageLoc','Player_Y_Position','ScreenLeft_X_Pos','ScreenLeft_PageLoc']
    cfg = dict(ram={n:address(b,n)for n in names},character=char,proto=proto,
               entry=hook('InventoryUiTick'),nmi=hook('NonMaskableInterrupt'),
               nmi_return=hook('NonMaskableInterrupt',int(b['syms']['NonMaskableInterrupt']['size'],0)-1),
               smc=[address(b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC',
                         'SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2])
    # Decode instructions, so an operand byte $60 cannot become a return hook.
    memory = [0]*65536; at=location(b,'InventoryUiTick'); pc=address(b,'InventoryUiTick')
    size=int(b['syms']['InventoryUiTick']['size'],0)
    memory[pc:pc+size]=b['raw'][at:at+size]
    dis=Disassembler(NesMPU(memory=memory)); offset=0; returns=[]
    while offset<size:
        length,_=dis.instruction_at(pc+offset)
        if memory[pc+offset]==0x60: returns.append(hook('InventoryUiTick',offset))
        offset+=length
    assert offset==size and returns
    cfg['returns']=returns
    count=address(b,'X5MenuPresent')-address(b,'X5MenuCharacters')
    table=lambda n:list(b['raw'][location(b,n):location(b,n)+count])
    target=table('X5MenuCharacters').index(char)
    maps={n.lower():table('X5Menu'+n)for n in ['Up','Down','Left','Right']}
    cfg['menu_target']=target;cfg['menu_moves']=[]
    for start in range(count):
        todo=deque([(start,[])]);seen={start}
        while todo:
            node,path=todo.popleft()
            if node==target:
                cfg['menu_moves'].append(path[0]if path else '');break
            for direction,links in maps.items():
                next_node=links[node]
                if next_node not in seen:
                    seen.add(next_node);todo.append((next_node,path+[direction]))
        else:raise AssertionError('Target profile is not menu-reachable')
    cfg['cases']=[dict(name=name,owned=owned,selected=selected,pause=pause,
                       button=button,want=want,clear=clear) for name,owned,selected,pause,button,want,clear in [
        ('no-op-direct-buster',1,0,0,32,0,0),
        ('no-op-paused-buster',1,0,1,32,0,0),
        ('no-op-paused-forward',1,0,1,1,0,0),
        ('no-op-paused-backward',1,0,1,2,0,0),
        ('switch-to-super-arm',3,0,0,32,1,1),
        ('switch-to-buster',3,1,0,32,0,1),
        ('paused-default',3,1,1,32,0,1),
        ('paused-forward',3,0,1,1,1,1),
        ('paused-backward',3,0,1,2,1,1)]]
    fixture=ROOT/'tests/robots-weapon-native.lua'
    script=out/'run.lua';script.write_text('ROBOT_CONFIG='+lua(cfg)+'\n'+fixture.read_text())
    with (out/'host.log').open('w')as log:
        result=subprocess.run([sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),
            '--output',str(out),'--emulator',a.emulator,str(script),str(a.rom.resolve()),
            '--timeout','90','--option=--doNotSaveSettings',
            '--option=--nes.ramPowerOnState=AllZeros',
            '--option=--nes.randomizeCpuPpuAlignment=false',
            '--option=--nes.randomizeMapperPowerOnState=false'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    q=json.loads((out/'proof.json').read_text())if(out/'proof.json').exists()else dict(passed=False)
    q.update(ROM_sha256=hashlib.sha256(b['raw']).hexdigest(),emulator_exit=result.returncode,
             profile=a.profile,passed=result.returncode==0 and q.get('passed',False),
             fixture_sha256=hashlib.sha256(fixture.read_bytes()).hexdigest(),goal_complete=False)
    (out/'native-proof.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps(q));raise SystemExit(0 if q['passed']else 1)


if __name__=='__main__': main()
