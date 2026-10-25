"""Compiled native-helper integration arenas; not a controller-route proof."""
from pathlib import Path
import argparse, hashlib, importlib.util, itertools, json, re, sys, traceback
R=Path(__file__).resolve().parents[2]
sys.path.insert(0,'C:/Users/kando/AppData/Local/Programs/Python/Python314/Lib/site-packages')
from verify_native_relocation import load
G=R/'build/player-guide-agent/platform-axis-private'
sys.path.insert(0,str(G))
from check_native16 import execute
P=R/'build/verification/crossover-helpers-jb'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--mapper',choices=('mmc3','mmc5'),required=True)
    ap.add_argument('--build',required=True);ap.add_argument('--tag',required=True);args=ap.parse_args()
    out=P/args.tag;assert not out.exists();out.mkdir()
    rom=P/args.build/f'smb-crossover-{args.mapper}.nes'
    cpu,l=load(rom);old,o=load(R/f'build/checkpoints/ryu-overlap-hr/build/smb-crossover-{args.mapper}.nes')
    records=json.loads((P/'source/src/crossover_helper_data.json').read_text())['records']
    records=[dict(r,key=r['world_level'],area=r['pointer']) for r in records]
    report=dict(status='RUNNING',mapper=args.mapper,ROM_sha256=sha(rom),script_sha256=sha(__file__),scope=__doc__,counts={})
    try:
        # Every original exported address stays fixed. The original baseline and
        # CHR are byte-identical; no old SRAM object moves to make room.
        def public(path):
            result=set()
            for line in path.with_suffix('.dbg').read_text().splitlines():
                if not line.startswith('sym\t'):continue
                fields=dict(re.findall(r'(\w+)=("[^"]*"|[^,]+)',line.split('\t',1)[1]))
                if fields.get('scope')=='1' and 'val' in fields and 'seg' in fields:
                    result.add((fields['name'],int(fields['val'],0)))
            return result
        baseline=R/f'build/checkpoints/ryu-overlap-hr/build/smb-crossover-{args.mapper}.nes'
        assert public(baseline)<=public(rom),(args.mapper,'original public address moved',public(baseline)-public(rom))
        assert old.memory.rom[:16]==cpu.memory.rom[:16]
        assert old.memory.rom[16+512*1024:]==cpu.memory.rom[16+512*1024:]
        report['all_previous_public_addresses_and_CHR_unchanged']=True
        def reset(c=cpu,n=l,bank=24):
            m=c.memory;m[:2048]=[0]*2048;m[0x6000:0x8000]=[0]*8192;m.switch(bank)
            m[n['__SMCCODE_RUN__']:n['__SMCCODE_RUN__']+len(m.smc)]=m.smc
            m[n['CurrentBank']]=bank
            if 'BankShadow' in n:m[n['BankShadow']]=0x47
        def put(name,value,i=0):cpu.memory[l[name]+i]=value&255
        def get(name,i=0):return cpu.memory[l[name]+i]
        def word(name,hi,i=0):return get(name,i)+256*get(hi,i)
        def call(name,x=0):return execute(cpu,l[name],13,x,29,0x25,30000)
        # Relocated PauseRoutine must return the same public registers and all
        # original non-stack RAM, across timer/button/mode admission branches.
        pause=0;deltas=[]
        for mode,task,timer,buttons,status in itertools.product(range(4),range(5),(0,1,43),(0,16,144),(0,1,128,129,255)):
            for c,n in ((old,o),(cpu,l)):
                reset(c,n,0)
                for name,v in (('OperMode',mode),('OperMode_Task',task),('GamePauseTimer',timer),('SavedJoypad1Bits',buttons),('GamePauseStatus',status)):
                    c.memory[n[name]]=v
            before,bc=execute(old,o['PauseRoutine'],37,71,113,0x45,30000)
            after,ac=execute(cpu,l['PauseRoutine'],37,71,113,0x45,30000)
            expected=list(before)
            # The native farcall's final LDA republishes A and therefore NZ.
            # Both flags are dead here: GameLoop next constructs a farcall
            # target with LDA, then InventoryUiTick begins LDA GuestHurtTicks.
            expected[3]=(expected[3]&~0x82)|(0x80 if expected[0]&128 else 0)|(2 if expected[0]==0 else 0)
            assert tuple(expected)==after,('pause registers',mode,task,timer,buttons,status,before,after)
            for low,high in ((0,256),(512,2048),(0x6000,0x8000)):
                assert old.memory[low:high]==cpu.memory[low:high],('pause RAM',mode,task,timer,buttons,status,low)
            pause+=1;deltas.append(ac-bc)
        report['counts']['pause']=pause;report['pause_added_cycles']=[min(deltas),max(deltas)]
        masks=(0,3,1,3,3,1,1,1,0,0,1,2,3)
        def eligible(rec,char,hard):
            # JSON's numerical source gates are generated independently of the
            # compiled table and retained in the generator's manifest.
            gate=rec['hard_gate'] if hard else rec['easy_gate']
            return char<6 if gate==4 else bool(gate&masks[char])
        # Include each area/key with every legacy character and behavior mode,
        # and negative area/world keys that must not publish any helper actor.
        contexts=sorted({(r['key'],r['area']) for r in records}|{(k,0x7f) for k in range(32)})
        configs=0
        for (key,area),char,hard in itertools.product(contexts,range(13),range(2)):
            reset();put('WorldNumber',key//4);put('LevelNumber',key%4);put('AreaPointer',area)
            put('SelectedCharacter',char);put('CrossoverBehaviorVersion',hard)
            call('HpConfigure')
            expected=[i for i,r in enumerate(records) if (r['key'],r['area'])==(key,area) and eligible(r,char,hard)]
            assert get('HpCount')==len(expected),('configure count',key,area,char,hard,get('HpCount'),expected)
            assert [get('HpRecord',i) for i in range(len(expected))]==expected
            configs+=1
        report['counts']['configure']=configs
        margins=0
        for hard,slot,screen,delta in itertools.product(range(2),range(3),(0,255,256,511,3071),range(-82,330)):
            reset();put('HpMode',hard);put('ScreenLeft_X_Pos',screen);put('ScreenLeft_PageLoc',screen>>8)
            center=(screen+delta)&65535;put('HpXLo',center,slot);put('HpXHi',center>>8,slot)
            regs,_=call('HpInSourceMargin',slot)
            expected=(-55<=delta<=295) if not hard else (-48<=delta<=288)
            assert regs[0]==int(expected),(hard,slot,screen,delta,regs)
            margins+=1
        report['counts']['source_margin']=margins
        # Full native initialization, no overwrite of a competing active actor,
        # source phase/carry, detached pause, owner cleanup and reused-slot guard.
        spawn=0;carry=0
        for record,slot in itertools.product(range(len(records)),range(6)):
            rec=records[record]
            reset();put('WorldNumber',rec['key']//4);put('LevelNumber',rec['key']%4);put('AreaPointer',rec['area'])
            char=3 if rec['hard_gate']&1 else 1
            put('SelectedCharacter',char);put('CrossoverBehaviorVersion',1);call('HpConfigure')
            runtime=next(i for i in range(get('HpCount')) if get('HpRecord',i)==record)
            screen=rec['center_x']-100
            put('ScreenLeft_X_Pos',screen);put('ScreenLeft_PageLoc',screen>>8)
            put('ScreenRight_X_Pos',screen+255);put('ScreenRight_PageLoc',(screen+255)>>8)
            for i in range(6):put('Enemy_Flag',1,i);put('Enemy_ID',6,i);put('Enemy_X_Position',37+i,i)
            # All six occupied: an eligible helper remains pending.
            call('HpSpawnAndTrack');assert get('HpActorSlot',runtime)==0
            assert all(get('Enemy_ID',i)==6 and get('Enemy_X_Position',i)==37+i for i in range(6))
            put('Enemy_Flag',0,slot);call('HpSpawnAndTrack')
            assert get('HpActorSlot',runtime)==slot+1
            assert get('HpActorOwner',slot)==runtime+1
            assert get('Enemy_ID',slot)==(0x25 if rec['axis'] else 0x28)
            assert get('Enemy_State',slot)==(0x60 if rec['width_tiles']==2 else 0x40)
            assert word('Enemy_X_Position','Enemy_PageLoc',slot)==rec['center_x']-4*rec['width_tiles']
            assert get('Enemy_Y_Position',slot)==rec['top_y']
            assert all(get('Enemy_ID',i)==6 and get('Enemy_X_Position',i)==37+i for i in range(6) if i!=slot)
            put('ObjectOffset',slot);put('PlatformCollisionFlag',0,slot)
            put('Player_X_Position',rec['center_x']);put('Player_PageLoc',rec['center_x']>>8)
            put('Enemy_Y_HighPos',1,slot);put('GameEngineSubroutine',8)
            for _ in range(80):
                before=word('Player_X_Position','Player_PageLoc')
                oldx=word('HpXLo','HpXHi',runtime)
                call('HpNativePlatformDispatch',slot)
                if rec['axis']==0:
                    assert word('Player_X_Position','Player_PageLoc')==(before+word('HpXLo','HpXHi',runtime)-oldx)&65535
                assert get('Player_Y_Position')==(get('Enemy_Y_Position',slot)-32)&255
                carry+=1
            phase=tuple(get(n,runtime) for n in ('HpPhaseLo','HpPhaseMid','HpPhaseHi'))
            put('HpVisible',0,runtime);call('HpNativePlatformDispatch',slot)
            assert phase==tuple(get(n,runtime) for n in ('HpPhaseLo','HpPhaseMid','HpPhaseHi'))
            # Slot was legitimately reused by a native Goomba. Releasing the old
            # helper must leave that new actor completely intact.
            put('Enemy_ID',6,slot);put('Enemy_State',0,slot);put('Enemy_X_Position',71,slot)
            call('HpReleaseActor',runtime)
            assert get('Enemy_Flag',slot)==1 and get('Enemy_ID',slot)==6 and get('Enemy_X_Position',slot)==71
            assert get('HpActorSlot',runtime)==0
            spawn+=1
        report['counts'].update(spawn_lifecycle=spawn,carry=carry)
        report['status']='PASS_COMPILED_NATIVE_HELPER_COMPONENTS'
    except Exception as exc:
        report.update(status='FAIL_RETAINED',error=repr(exc),traceback=traceback.format_exc());raise
    finally:
        (out/'summary.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))
if __name__=='__main__':main()
