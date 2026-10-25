"""Native actor/carry/render/parser rechecks on the integrated roster."""
from pathlib import Path
import importlib.util,json
R=Path(__file__).resolve().parents[2]
D=R/'build/verification/level-platform-mr-candidate-agent'
O=R/'build/verification/level-platform-adoption-mx'

def main():
    s=importlib.util.spec_from_file_location('mx_runner',R/'tools/run_mesen.py');runner=importlib.util.module_from_spec(s);s.loader.exec_module(runner)
    results={}
    for mapper in ('mmc3','mmc5','expanded'):
        rom=O/f'level-platform-{mapper}-final.nes'
        for name,source in [('helpers',D/'native_helpers.lua'),('lift',R/'tools/audit/level_variant_lift_native_agent.lua'),('coin',R/'tools/audit/level_variant_coin_native_agent.lua')]:
            folder=O/(mapper+'-'+name);folder.mkdir(exist_ok=True);script=folder/(name+'.lua');script.write_text(source.read_text());runner.ROOT=folder
            results[mapper+'-'+name]=runner.run(script,rom,timeout=45)
            (O/'native-results.json').write_text(json.dumps(results,indent=2)+'\n');assert results[mapper+'-'+name]==0
    rom=O/'level-platform-expanded-final.nes';folder=O/'expanded-profiles';folder.mkdir(exist_ok=True)
    text=(D/'native_helpers_profiles.lua').read_text()
    old='{key=25,area=1,x=2568,y=160,width=32,axis=1,char=5,var=2}}'
    new=old[:-1]+',\n {key=0,area=37,x=3104,y=64,width=16,axis=0,char=15},\n {key=0,area=37,x=3104,y=64,width=16,axis=0,char=16},\n {key=25,area=1,x=2568,y=160,width=32,axis=1,char=5,var=3}}'
    assert text.count(old)==1;text=text.replace(old,new)
    script=folder/'profiles.lua';script.write_text(text);runner.ROOT=folder
    results['expanded-profiles']=runner.run(script,rom,timeout=45);assert results['expanded-profiles']==0
    for mapper in ('mmc3','expanded'):
        folder=O/(mapper+'-columns');folder.mkdir(exist_ok=True);script=folder/'columns.lua'
        script.write_text((D/('native_columns_'+mapper+'.lua')).read_text());runner.ROOT=folder
        results[mapper+'-columns']=runner.run(script,O/f'level-platform-{mapper}-final.nes',timeout=45);assert results[mapper+'-columns']==0
    (O/'native-results.json').write_text(json.dumps(results,indent=2)+'\n');print('PASS all12 native level/helper integration fixtures')

if __name__=='__main__':main()
