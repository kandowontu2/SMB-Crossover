"""Actual controller-only smoke matrix for every implemented identity."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,re
R=Path(__file__).resolve().parents[2]

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--complete',action='store_true',help='Require every identity linked by this build')
    p.add_argument('--names',nargs='*',help='Run only these named identities')
    a=p.parse_args();rom=a.rom.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
    labels={m[2]:int(m[1],16) for line in rom.with_suffix('.lbl').read_text().splitlines() if(m:=re.fullmatch(r'al ([0-9A-Fa-f]+) \.(\S+)',line))}
    cases=[('Mario',0,0,0,0),('Luigi',0,8,labels['MarioVariant'],1),('Mega Man',1,1,labels['ProtoVariant'],0),('Proto Man',1,1,labels['ProtoVariant'],1),('Samus',2,2,0,0),('Bill',3,3,labels['BillVariant'],0),('Lance',3,3,labels['BillVariant'],1),('Link',4,4,labels['Z2Variant'],0),('Zelda II Link',4,4,labels['Z2Variant'],1),('Simon',5,5,0x5fe7,0),('Grant',5,5,0x5fe7,1),('Sypha',5,5,0x5fe7,2),('Alucard',5,5,0x5fe7,3),('Pit',6,6,0,0),('Rygar',7,7,0,0),('Scrooge',8,12,labels['DarkwingVariant'],0),('Darkwing',8,12,labels['DarkwingVariant'],1),('Bass',9,9,0,0),('Ryu',10,10,0,0),('Sophia',11,11,0,0),('Kirby',12,13,0,0),('Chip',13,14,0x5fe1,0),('Dale',13,14,0x5fe1,1),('SMB3 Mario',16,17,0x5fe4,0),('SMB3 Luigi',16,17,0x5fe4,1),('Vic Viper',17,18,0,0),('Leonardo',18,19,0x5fe6,0),('Raphael',18,19,0x5fe6,1),('Michelangelo',18,19,0x5fe6,2),('Donatello',18,19,0x5fe6,3)]
    if any(n in labels for n in ('MacMovement','LmMovement','LmMovementGate')):cases.append(('Little Mac',14,15,0,0))
    if any(n in labels for n in ('JnMovement','MjMovement','StMovement')):cases.append(('Mike Jones',15,16,0,0))
    if 'KbVariant' in labels:cases.append(('Meta Knight',12,13,labels['KbVariant'],1))
    if 'VvVariant' in labels:
        cases.extend((name,17,18,labels['VvVariant'],variant)for name,variant in [('Octopus',1),('TwinBee',2),('Pentarou',3)])
    if 'RlVariant'in labels:cases.append(('Roll',9,9,labels['RlVariant'],1))
    if a.complete:assert len(cases)==(37 if 'RlVariant'in labels else 36 if 'VvVariant'in labels else 33 if 'KbVariant' in labels else 32),'Final profile symbols must be confirmed before full-roster admission'
    if a.names:cases=[case for case in cases if case[0] in a.names]
    s=importlib.util.spec_from_file_location('roster_mesen',R/'tools/run_mesen.py');runner=importlib.util.module_from_spec(s);s.loader.exec_module(runner)
    digest=hashlib.sha256(rom.read_bytes()).hexdigest();results={}
    for name,slot,char,address,variant in cases:
        key=name.lower().replace(' ','-');folder=out/key;folder.mkdir(exist_ok=True)
        menu_name={'Samus':'SAMUS ARAN','Bill':'BILL RIZER','Lance':'LANCE BEAN','Simon':'SIMON BELMONT','Scrooge':'SCROOGE MCDUCK','Darkwing':'DARKWING DUCK','Ryu':'RYU HAYABUSA','Sophia':'SOPHIA III'}.get(name,name.upper())
        constants=f'TARGET_NAME={json.dumps(name)}\nTARGET_MENU_NAME={json.dumps(menu_name)}\nTARGET_SLOT={slot}\nTARGET_CHARACTER={char}\nTARGET_VARIANT_ADDRESS={address}\nTARGET_VARIANT={variant}\n'
        script=folder/'entry.lua';script.write_text(constants+(R/'tests/full-roster-entry.lua').read_text());runner.ROOT=folder
        code=runner.run(script,rom,timeout=45);results[name]=dict(exit=code,script_sha256=hashlib.sha256(script.read_bytes()).hexdigest())
        (out/'results.json').write_text(json.dumps(dict(rom_sha256=digest,identities=len(cases),results=results),indent=2)+'\n')
        assert code==0,name
    print('PASS all'+str(len(cases))+' cold controller identities')

if __name__=='__main__':main()
