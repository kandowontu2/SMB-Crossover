"""Verify composed turtle scenes and existing Chip/Kirby native interactions."""
from pathlib import Path
import hashlib
import importlib.util
import json

R=Path(__file__).resolve().parents[2]
O=R/'build/verification/tmnt-adoption-mn'
P=O/'tmnt-composed.nes'


def main():
    spec=importlib.util.spec_from_file_location('root_mesen',R/'tools/run_mesen.py')
    runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
    cases=[('turtle-smoke',R/'build/tmnt-kd-private/smoke-a.lua'),
           ('turtle-natural',R/'build/tmnt-kd-private/natural-a.lua'),
           ('turtle-health',R/'build/tmnt-kd-private/health-d.lua'),
           ('turtle-attacks',R/'build/tmnt-kd-private/attacks-a.lua'),
           ('chip',R/'build/verification/chip-dale-candidate-agent/native_chip.lua'),
           ('chip-interactions',R/'build/verification/chip-dale-candidate-agent/native_chip_interactions.lua'),
           ('kirby-food',R/'build/verification/kirby-adoption-me/final-fixtures/food-v5.lua')]
    results={}
    for name,original in cases:
        folder=O/name;folder.mkdir(exist_ok=True)
        text=original.read_text()
        if name.startswith('turtle-'):
            # The composed selector contains genuine Chip between Kirby/TMNT.
            assert text.count('right=f==140')==1
            text=text.replace('right=f==140','right=f==130 or f==140')
        if name=='turtle-natural':
            text='''local replaced=0
local bumped={}
'''+text
            text=text.replace("assert(r('SelectedCharacter')==19 and k(0x5f60)==128",'''assert(replaced>0,'Native used block replaces its transient bumped tile')
  assert(r('Block_Buffer_1',325)~=0x23,'Actual mushroom block never stays a bumped$23 cell')
  assert(r('SelectedCharacter')==19 and k(0x5f60)==128''')
            text+='''
emu.addMemoryCallback(function(a,v)
 if v==0x23 then bumped[a]=true
 elseif bumped[a] then replaced=replaced+1;bumped[a]=nil end
end,emu.callbackType.write,L.Block_Buffer_1,L.Block_Buffer_1+415)
'''
        script=folder/(name+'.lua');script.write_text(text)
        runner.ROOT=folder
        code=runner.run(script,P,timeout=45)
        results[name]=dict(exit=code,script_sha256=hashlib.sha256(script.read_bytes()).hexdigest())
        (O/'native-results.json').write_text(json.dumps(results,indent=2)+'\n')
        assert code==0,name
    raw=P.read_bytes()
    for page,name in ((256,'protoman.chr'),(276,'darkwing.chr'),(308,'zelda2-link-body.chr'),(335,'zelda2-link-items.chr'),(340,'kirby.chr'),(412,'chip-dale.chr'),(604,'tmnt.chr')):
        asset=(R/'chr/characters'/name).read_bytes();start=16+1048576+page*1024
        assert raw[start:start+len(asset)]==asset,name
    print('PASS root turtle integration, used-block replacement, Chip/Kirby regression and seven physical asset slices')


if __name__=='__main__':main()
