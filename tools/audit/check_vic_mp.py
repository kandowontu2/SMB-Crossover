"""Root native integration and graphics timing checks for the expanded ship."""
from pathlib import Path
import hashlib
import importlib.util
import json

R=Path(__file__).resolve().parents[2]
O=R/'build/verification/vic-adoption-mp'
P=O/'vic-composed-final.nes'


def main():
    spec=importlib.util.spec_from_file_location('root_mesen',R/'tools/run_mesen.py')
    runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
    tests=[('ship-controller',R/'build/vic-viper-ml-private/native_vic_entry_v5.lua'),
           ('ship-gear',R/'build/vic-viper-ml-private/native_vic_gear_v3.lua'),
           ('ship-contacts',R/'build/vic-viper-ml-private/native_vic_contacts.lua'),
           ('turtle-smoke',R/'build/verification/tmnt-adoption-mn/turtle-smoke/turtle-smoke.lua'),
           ('turtle-natural',R/'build/verification/tmnt-adoption-mn/turtle-natural/turtle-natural.lua'),
           ('turtle-health',R/'build/verification/tmnt-adoption-mn/turtle-health/turtle-health.lua'),
           ('turtle-attacks',R/'build/verification/tmnt-adoption-mn/turtle-attacks/turtle-attacks.lua'),
           ('chip',R/'build/verification/chip-dale-candidate-agent/native_chip.lua'),
           ('chip-interactions',R/'build/verification/chip-dale-candidate-agent/native_chip_interactions.lua'),
           ('kirby-food',R/'build/verification/kirby-adoption-me/final-fixtures/food-v5.lua'),
           ('darkwing',R/'build/player-guide-agent/darkwing-private/native_darkwing.lua'),
           ('zelda2',R/'build/verification/zelda2-link-candidate-agent/native_z2_interactions.lua'),
           ('proto',R/'build/verification/protoman-candidate-agent/native_proto.lua')]
    results={}
    for name,source in tests:
        folder=O/('final-'+name);folder.mkdir(exist_ok=True)
        text=source.read_text().replace("st['cpu.pc']>=0xe000","st['cpu.pc']>=L.IrqScrollSplit and st['cpu.pc']<L.IrqScrollSplit+68")
        if name.startswith('turtle-'):
            assert text.count('right=f==130 or f==140')==1
            text=text.replace('right=f==130 or f==140','right=f==125 or f==130 or f==140')
        script=folder/(name+'.lua');script.write_text(text)
        runner.ROOT=folder
        code=runner.run(script,P,timeout=45)
        results[name]=dict(exit=code,script_sha256=hashlib.sha256(script.read_bytes()).hexdigest())
        (O/'final-native-results.json').write_text(json.dumps(results,indent=2)+'\n')
        assert code==0,name
    raw=P.read_bytes()
    for page,name in ((256,'protoman.chr'),(276,'darkwing.chr'),(308,'zelda2-link-body.chr'),(335,'zelda2-link-items.chr'),(340,'kirby.chr'),(380,'vic-viper.chr'),(412,'chip-dale.chr'),(604,'tmnt.chr')):
        asset=(R/'chr/characters'/name).read_bytes();start=16+1048576+page*1024
        assert raw[start:start+len(asset)]==asset,name
    print('PASS thirteen root native scenes, IRQ font timing, source ship interactions and eight physical asset slices')


if __name__=='__main__':main()
