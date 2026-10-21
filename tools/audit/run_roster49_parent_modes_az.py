"""Observe old tapes' actual behavior settings before comparing their motion."""
from pathlib import Path
import csv,hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'root49-parent-modes-az'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(p):
    with p.open(newline='')as f:return list(csv.DictReader(f))
def main():
    H.mkdir(exist_ok=True);assert not(H/'preparation.json').exists(),'Unique evidence tag required'
    parent=V/'root49-d-remaining-routes-ax/preparation.json';q=json.loads(parent.read_text())
    specs=[p for p in q['parents']if p['character']not in[0,8,1,4]]
    policy=H/'observe.lua'
    policy.write_text(r'''local frame,seen=0,false
local function r(n)return L[n]and emu.read(L[n],emu.memType.nesDebug)or-1 end
local f=assert(io.open(ROSTER_CONFIG.out..'actual-parent-mode.csv','w'))
f:write('frame,selected,behavior,marioVariant,billVariant,outlinesOff,x,y,vx,vy\n')
emu.addEventCallback(function()
 frame=frame+1
 if r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 then
  local a={frame,r('SelectedCharacter'),r('CrossoverBehaviorVersion'),r('MarioVariant'),r('BillVariant'),r('PlayerOutlinesOff'),r('Player_X_Position')+256*r('Player_PageLoc'),r('Player_Y_Position'),r('Player_X_Speed'),r('Player_Y_Speed')}
  f:write(table.concat(a,',')..'\n');f:flush()
 end
end,emu.eventType.endFrame)
return function()return{}end
''')
    (H/'preparation.json').write_text(json.dumps(dict(status='PREPARED_READ_ONLY_OLD_ROM_BEHAVIOR_OBSERVATION',
      script_sha256=sha(__file__),parent_preparation_sha256=sha(parent),parents=specs,policy_sha256=sha(policy),
      frame_limit=650,emulated_writes=False,state_loads=False,
      phase_cap_bytes=300000000,global_cap_bytes=70000000000),indent=2)+'\n')
    pool=list((R/'build/checkpoints').rglob('*.nes'))
    for ref in q['parents']:pool.extend((R/ref['path']).glob('*.nes'))
    roms={sha(p):p for p in pool}
    for ref in specs:
        meta=json.loads((R/ref['path']/'manifest.json').read_text());assert meta['rom_sha256']in roms,ref['name']
    results=[]
    for s in specs:
        p=R/s['path'];m=json.loads((p/'manifest.json').read_text());ident=s['character']
        assert sha(p/'manifest.json')==s['manifest_sha256']and sha(p/'inputs.csv')==s['inputs_sha256']
        rom=roms[m['rom_sha256']];assert sha(rom)==m['rom_sha256']
        print('START',s['name'],flush=True)
        args=[sys.executable,str(R/'tools/playthroughs/roster_run.py'),'--character',str(ident),'--mapper','mmc3','--rom',str(rom),
          '--tag','root49-parent-mode-az','--policy',str(policy),'--replay',str(p/'inputs.csv'),'--frames','650','--timeout','180','--workspace-cap-gb','70']
        with(H/f'native-{ident}.log').open('wb')as log:run=subprocess.run(args,cwd=R,stdout=log,stderr=subprocess.STDOUT)
        out=R/f'build/roster-through-2-2/root49-parent-mode-az-{ident}-v0-mmc3'
        a,b=rows(p/'trace.csv'),rows(out/'trace.csv');obs=rows(out/'actual-parent-mode.csv')
        assert obs and len(b)==650 and a[:650]==b,'Actual old trace must remain literal to its original full proof'
        assert rows(out/'inputs.csv')==rows(p/'inputs.csv')[:649]
        assert all(int(x['selected'])==ident for x in obs)
        actual=sorted({int(x['behavior'])for x in obs});assert len(actual)==1
        result=dict(character=ident,name=s['name'],original_ROM_sha256=sha(rom),first_active=obs[0],last_active=obs[-1],
          observed_behavior=actual[0],old_650_trace_rows_literal=True,current_D_actual_behavior=0,
          same_raw_behavior=actual[0]==0,returncode=run.returncode,
          files={x.name:dict(bytes=x.stat().st_size,sha256=sha(x))for x in out.iterdir()if x.is_file()})
        results.append(result);(H/'progress.json').write_text(json.dumps(dict(status='RUNNING'if len(results)<len(specs)else'ALL_OBSERVATIONS_TERMINAL',results=results),indent=2)+'\n')
        print('END',s['name'],'behavior',actual[0],flush=True)
    print('DONE',len(results),flush=True)
if __name__=='__main__':main()
