"""Bound native cold menus, initial lives portrait and mapped CHR checks."""
from pathlib import Path
import argparse,json,subprocess,sys
from mmc3_native_v42_qualify import ROOT,D,V,lua,sha,bind_guard
from check_tmnt_render_oa import address,location

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    out=a.output.resolve();out.mkdir(parents=True,exist_ok=False);rom=V/'candidate.nes'
    report=dict(passed=False,goal_complete=False,adopted=False,ROM_sha256=sha(rom),runs=[])
    original=D/'mmc3-ship-lives-v25/cold-entries-v1/vic-viper/entry.lua'
    text=original.read_text();text=text[text.index('-- Cold controller-only'):]
    old="local function shared()local t={}for a=L.__SMCCODE_RUN__,L.__SMCCODE_RUN__+32 do t[#t+1]=emu.read(a,emu.memType.nesDebug)end;return table.concat(t,',')end"
    new="local function shared()local t={}for _,a in ipairs({0x13f,0x156,0x15a,0x158,0x159})do t[#t+1]=emu.read(a,emu.memType.nesDebug)end;return table.concat(t,',')end"
    assert old in text;text=text.replace(old,new)
    for name,menu,slot,char,variant,var,hard in [('sophia-hard','SOPHIA III',11,11,0,None,True),('chip-easy','CHIP',13,14,0,'CdVariant',False),('zelda2-easy','ZELDA II LINK',4,4,1,'Z2Variant',False),('vic-easy','VIC VIPER',17,18,0,None,False)]:
        folder=out/name;folder.mkdir();b,guard=bind_guard(rom,folder)
        portrait=(location(b,'X5PortraitRender')-16)//8192
        body=text.replace("actual(0xa000)==99",'actual(0xa000)=='+str(portrait))
        body=body.replace("if livesPending==0 then shot('lives');livesSaved=true end",'''if livesPending==0 then
    local profile=r('M3CacheProfile');local starts={52,256,276,308,340,380,412,460,460,460,668,708,524,604,304,832,896,960}
    local counts={116,20,32,32,40,32,48,64,64,64,40,48,80,64,76,64,64,64}
    local f=assert(io.open(RAW_CHR,'rb'));local raw=f:read('*a');f:close()
    assert(profile>=0 and profile<18,'Lives native family profile')
    for i=0,counts[profile+1]*1024-1 do assert(emu.read(52*1024+i,emu.memType.nesChrRam)==raw:byte(starts[profile+1]*1024+i+1),'Lives mapped family CHR exact')end
    shot('lives');livesSaved=true
   end''')
        body=body.replace("if t==140 then", "if t==140 then\n   assert(livesSaved,'Actual native initial lives portrait observed')")
        cfg=dict(TARGET_NAME=name,TARGET_MENU_NAME=menu,TARGET_SLOT=slot,TARGET_CHARACTER=char,
                 TARGET_VARIANT_ADDRESS=address(b,var)if var else 0,TARGET_VARIANT=variant,TARGET_HARD=hard,
                 RAW_CHR=(V/'source/chr/characters/oversized-raw.chr').as_posix())
        script=folder/'entry.lua';script.write_text('ROSTER_CONFIG={out=OUTPUT}\ndofile('+lua(guard.as_posix())+')\n'+'\n'.join(k+'='+lua(v)for k,v in cfg.items())+'\n'+body)
        cmd=[sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),'--emulator',str(D/'mmc3-flag-fix-v23/script-budget-probe-v2/emulator/Mesen.exe'),'--output',str(folder),str(script),str(rom),'--timeout','120','--option=--doNotSaveSettings','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
        with(folder/'host.log').open('w')as log:code=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT).returncode
        proof=json.loads((folder/'proof.json').read_text())if(folder/'proof.json').exists()else{}
        guards={n:json.loads((folder/(n+'.json')).read_text())if(folder/(n+'.json')).exists()else{}for n in ['full-smc-guard','mmc3-cache-guard','completed-loop-motion']}
        row=dict(identity=name,exit=code,passed=code==0 and proof.get('passed')and all(q.get('passed')for q in guards.values()),native=proof,guards=guards,lives_CHR_full_family_checked=True,portrait_actual_bank=portrait,script_sha256=sha(script))
        report['runs'].append(row);(out/'progress.json').write_text(json.dumps(report,indent=2));print(json.dumps(row),flush=True)
    report.update(passed=all(r['passed']for r in report['runs']),complete=True,
                  scope='Four actual cold menu choices, initial lives portrait observation/full mapped body-family CHR, boot262144CHR bytes, native140-frame movement and complete V42 guards. Small sample, not all37identity or all lives power/respawn paths.')
    (out/'proof.json').write_text(json.dumps(report,indent=2))

if __name__=='__main__':main()
