"""Root integration checks: names, palette buffers, physical art and native play."""
from pathlib import Path
import hashlib
import importlib.util
import itertools
import json
import re
import shutil
import sys

R = Path(__file__).resolve().parents[2]
O = R / 'build/verification/chip-adoption-mj'
P = O / 'chip-final.nes'


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def main():
    sys.path.append('C:/Users/kando/AppData/Local/Programs/Python/Python314/Lib/site-packages')
    g = module('root_mmc5', R / 'build/player-guide-agent/check_mmc5_expand.py')
    def setup(p):
        labels = g.labels(p)
        memory = g.Mmc5Memory(p)
        cpu = g.NesMPU(memory=memory)
        text = p.with_suffix('.dbg').read_text()
        s = re.search(r'seg\s+[^\n]*name="SMCCODE",[^\n]*size=(0x[0-9a-fA-F]+),[^\n]*ooffs=(\d+)', text)
        return labels, memory, cpu, memory.rom[int(s[2]):int(s[2])+int(s[1],16)]
    new = setup(P)
    old = setup(R / 'build/checkpoints/kirby-roster-mg/build/smb-crossover-mmc5-expanded.nes')
    def call(data, fields, routine, bank=78):
        labels, memory, cpu, smc = data
        memory.ram[:] = bytes(65536)
        memory.ram[0x15a:0x15a+len(smc)] = smc
        memory.banks = [126, bank, 80, 127]
        memory.ram[labels['CurrentBank']] = bank | 128
        memory.ram[labels['CurrentBankC']] = 208
        for n,v in fields.items():
            memory.ram[labels[n] if isinstance(n,str) else n] = v
        g.execute(cpu, labels[routine])
        count = memory.ram[labels['VRAM_Buffer1_Offset']]
        return bytes(memory.ram[labels['VRAM_Buffer1']:labels['VRAM_Buffer1']+count+1])
    unchanged = kirby = chip = 0
    for character,power,area,bg in itertools.product(range(15),range(3),range(4),range(8)):
        fields = dict(SelectedCharacter=character,PlayerStatus=power,AreaType=area,BackgroundColorCtrl=bg)
        result = call(new,fields,'X5GetPlayerColors')
        backdrop = (0x22,0x22,0x0f,0x0f,0x0f,0x22,0x0f,0x0f)[bg if bg else area]
        if character < 13:
            assert result == call(old,fields,'X5GetPlayerColors'), fields
            unchanged += 1
        elif character == 13:
            assert bytes((0x3f,0x10,1,backdrop)) in result
            assert result[-7:] == bytes((0x3f,0x11,3,0x35,0x25,0x0f,0))
            kirby += 1
        else:
            assert result == bytes((0x3f,0x10,4,backdrop,0x0f,0x37,0x16,0))
            chip += 1
    names = ['     MARIO      ','    MEGA MAN    ','   SAMUS ARAN   ','   BILL RIZER   ','      LINK      ',' SIMON BELMONT  ','      PIT       ','     RYGAR      ','     LUIGI      ','      BASS      ',' RYU HAYABUSA   ','   SOPHIA III   ','SCROOGE MCDUCK  ','     KIRBY      ','     CHIP       ']
    name_cases = 0
    for selected,variant in itertools.product(range(15),range(2)):
        fields = dict(SelectedCharacter=selected,ProtoVariant=variant,Z2Variant=variant,DarkwingVariant=variant,BillVariant=variant)
        fields[0x5fe1] = variant
        result = call(new,fields,'QueueSelectName',66)
        name = {1:'   PROTO MAN    ',3:'   LANCE BEAN   ',4:' ZELDA II LINK  ',12:' DARKWING DUCK  ',14:'     DALE       '}.get(selected,names[selected]) if variant else names[selected]
        expected = bytes(0x24 if ch==' ' else ord(ch)-ord('A')+10 for ch in name)
        assert result[3:19] == expected,(selected,variant,result.hex())
        name_cases += 1
    raw = P.read_bytes()
    for page,name in ((256,'protoman.chr'),(276,'darkwing.chr'),(308,'zelda2-link-body.chr'),(335,'zelda2-link-items.chr'),(340,'kirby.chr'),(412,'chip-dale.chr')):
        asset = (R/'chr/characters'/name).read_bytes()
        start = 16+1048576+page*1024
        assert raw[start:start+len(asset)] == asset,name
    report = dict(passed=True,sha256=hashlib.sha256(raw).hexdigest(),old_palette_cases_exact=unchanged,Kirby_backdrop_cases=kirby,ChipDale_palette_cases=chip,menu_name_cases=name_cases,physical_asset_slices=6)
    (O/'admission.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report),flush=True)
    runner = module('root_mesen',R/'tools/run_mesen.py')
    sources = R/'build/verification/chip-dale-candidate-agent'
    fixtures = O/'fixtures'
    fixtures.mkdir(exist_ok=True)
    tests = [('chip',sources/'native_chip.lua',0),('dale',sources/'native_chip.lua',1),('interactions',sources/'native_chip_interactions.lua',None),('kirby-food',R/'build/verification/kirby-adoption-me/final-fixtures/food-v5.lua',None)]
    for name,source,variant in tests:
        script = fixtures/(name+'.lua')
        script.write_text(('TEST_VARIANT='+str(variant)+'\n' if variant is not None else '')+source.read_text())
        runner.ROOT = O/name
        runner.ROOT.mkdir(exist_ok=True)
        assert runner.run(script,P,timeout=45)==0,name
    print('PASS root native Chip/Dale interactions and Kirby regression',flush=True)


if __name__ == '__main__':
    main()
