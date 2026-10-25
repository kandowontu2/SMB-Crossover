"""Execute the actual weapon caller, including its authentic A/P setup."""
from pathlib import Path
import argparse,hashlib,itertools,json
from check_tmnt_render_oa import load,Memory,address,location
from verify_native_relocation import NesMPU
def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    old,new=load(a.baseline),load(a.rom);entry=address(new,'TnFastWeaponsSpan')-7
    bank=(location(new,'TnFastWeaponsSpan')-16)//8192
    off=16+bank*8192+(entry-0xa000)
    expected=bytes([0xad,address(old,'SelectedCharacter')&255,address(old,'SelectedCharacter')>>8,0xc9,6,0x90])
    assert old['raw'][off:off+6]==new['raw'][off:off+6]==expected
    assert old['raw'][off+6:off+7]==new['raw'][off+6:off+7]
    def run(b,char,variant,mode,scenario,flags):
        m=Memory(b);m.page(1,bank);m[address(b,'CurrentBank')]=bank|128
        seed=dict(SelectedCharacter=char,TnVariant=variant,CrossoverBehaviorVersion=mode,RlVariant=variant,
          Cv3Variant=variant,Z2Variant=variant,OperMode=1,OperMode_Task=3,GameEngineSubroutine=8 if scenario<2 else 9,
          TimerControl=1 if scenario==2 else 0,MmDeathFlag=1 if scenario==3 else 0,Player_Y_HighPos=1,
          Player_X_Position=64,Player_Y_Position=176,PlayerFacingDir=1,PlayerStatus=1,PlayerSize=0,
          TnSeq=128,TnPhase=0,TnUpdateTick=1,TnInputFrame=255,TnTickFrame=255,FrameCounter=7,
          SavedJoypadBits=0 if scenario!=1 else 64)
        for n,v in seed.items():m[address(b,n)]=v
        for i in range(4):m[address(b,'TnHealth')+i]=128
        c=NesMPU(memory=m,pc=entry);c.sp=0xed;c.stPushWord(0x7eff);c.a=0x56;c.x=3;c.y=7;c.p=flags;m.writes=[]
        stop=address(b,'ProcAirBubbles')
        for _ in range(100000):
            if c.pc==stop and m.banks[1]==bank:break
            c.step()
        else:raise AssertionError(('Actual caller timeout',char,variant,scenario,hex(c.pc)))
        excluded=set(range(256,512))|set(range(0x5114,0x5118))
        for g in b['segs'].values():
            if g['name']=='"SMCCODE"':excluded.update(range(int(g['start'],0),int(g['start'],0)+int(g['size'],0)))
        for n in ['SafecallA','safecall_a']:
            if n in b['syms']:excluded.add(address(b,n))
        ram=bytes(0 if i in excluded else m[i]for i in range(0x8000))
        io=[(at,v)for at,v in m.writes if 0x4000<=at<0x4018 or 0x5000<=at<0x5114 or 0x5118<=at<0x5207]
        return (c.a,c.x,c.y,c.p&0xcf,c.sp),ram,io,m.banks,c.processorCycles
    rows=[]
    for char,variant,mode,scenario,flags in itertools.product(range(20),range(4),range(2),range(4),[0x30,0x71,0x39,0xee]):
        x=run(old,char,variant,mode,scenario,flags);y=run(new,char,variant,mode,scenario,flags)
        assert x[:4]==y[:4],(char,variant,mode,scenario,hex(flags),x[0],y[0],[(hex(i),x[1][i],y[1][i])for i in range(32768)if x[1][i]!=y[1][i]][:12])
        rows.append(dict(character=char,variant=variant,mode=mode,scenario=scenario,flags=flags,cycles_saved=x[4]-y[4]))
    native=[r['cycles_saved']for r in rows if r['character']==19];others=[-r['cycles_saved']for r in rows if 6<=r['character']<19]
    q=dict(passed=True,ROM_sha256=hashlib.sha256(new['raw']).hexdigest(),baseline_ROM_sha256=hashlib.sha256(old['raw']).hexdigest(),cases=len(rows),
      native_cycles_saved=[min(native),max(native)],other_admitted_cycles_added=[min(others),max(others)],
      source_caller_A_P_setup_authenticated=True,scope='Actual LDA/CMP/BCC through original ProcAirBubbles boundary; all20legal IDs, four alternate values, both modes, active/idle/frozen/death and flag states. Exact registers/meaningfulP/SP, application RAM, ordered non-banking writes and final banks. No arbitrary helper-entry precondition or campaign claim.')
    (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');(a.output/'cases.json').write_text(json.dumps(rows,separators=(',',':'))+'\n');print(json.dumps(q),flush=True)
if __name__=='__main__':main()
