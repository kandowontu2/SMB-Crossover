"""SMB3 combined source geometry/core and native interaction verification."""
from pathlib import Path
import hashlib,importlib.util,json,sys
R=Path(__file__).resolve().parents[2]
D=R/'build/verification/smb3-mario-candidate-agent'
O=R/'build/verification/smb3-adoption-mu'
P=O/'smb3-final.nes'

def main():
    sys.path.append('C:/Users/kando/AppData/Local/Programs/Python/Python314/Lib/site-packages')
    for case in ('core','render'):
        receipt=O/(case+'-proof.json')
        if receipt.exists() and json.loads(receipt.read_text())['candidate_SHA256']==hashlib.sha256(P.read_bytes()).hexdigest():
            continue
        file=D/f'check_{case}.py';text=file.read_text().replace("P=O/'smb3-private.nes'","P=Path("+repr(str(P))+")")
        text=text.replace("gzip.decompress(P.with_suffix('.dbg.gz').read_bytes()).decode()","P.with_suffix('.dbg').read_text()")
        text=text.replace("(O/'"+case+"-proof.json')","(Path("+repr(str(O))+ ")/'"+case+"-proof.json')")
        assert "P=O/'smb3-private.nes'" not in text
        (O/f'check-{case}.py').write_text(text)
        exec(compile(text,str(file),'exec'),{'__file__':str(file),'__name__':'root_smb3'})
    raw=P.read_bytes();private=(D/'smb3-private.nes').read_bytes()
    assert raw[16+92*8192:16+93*8192]==private[16+92*8192:16+93*8192],'Authenticated native motion/projectile bank stays exact'
    asset=(R/'chr/characters/smb3-mario.chr').read_bytes()
    assert raw[16+1048576+524*1024:16+1048576+524*1024+len(asset)]==asset
    (O/'native-bank-and-CHR-proof.json').write_text(json.dumps(dict(passed=True,sha256=hashlib.sha256(raw).hexdigest(),native_PRG92_exact_private=True,CHR524_to544_exact_source_asset=True),indent=2)+'\n')
    s=importlib.util.spec_from_file_location('mu_runner',R/'tools/run_mesen.py');runner=importlib.util.module_from_spec(s);s.loader.exec_module(runner)
    cases=[('smb3-entry',D/'native_smb3.lua'),('smb3-forms',D/'native_smb3_forms.lua'),('ship',R/'build/vic-viper-ml-private/native_vic_gear_v3.lua'),('turtle',R/'build/verification/vic-adoption-mp/final-turtle-natural/turtle-natural.lua'),('chip',R/'build/verification/chip-dale-candidate-agent/native_chip_interactions.lua'),('kirby',R/'build/verification/kirby-adoption-me/final-fixtures/food-v5.lua')]
    results=json.loads((O/'native-results.json').read_text()) if (O/'native-results.json').exists() else {}
    for name,source in cases:
        if results.get(name)==0:continue
        folder=O/(name+'-v2' if name in results else name);folder.mkdir(exist_ok=True)
        text=source.read_text().replace("st['cpu.pc']>=0xe000","st['cpu.pc']>=L.IrqScrollSplit and st['cpu.pc']<L.IrqScrollSplit+68")
        if name=='turtle':
            text=text.replace('right=f==125 or f==130 or f==140','right=f==125 or f==130 or f==140 or f==150')
            text=text.replace('f=f+1','f=f+1\n if f==500 then assert(r("SelectedCharacter")==19,"Expanded menu actually chose a turtle")end')
        if name=='ship':
            # The extra source-profile dispatch may overlap a logic lag frame;
            # hold a real button across four polls rather than a single impulse.
            text=text.replace('b=frame==bFrame','b=frame>=bFrame and frame<bFrame+4')
            text=text.replace('down=frame==90 or frame==110,right=frame==130 or frame==150','down=frame==90 or frame==110,right=frame==130 or frame==150 or frame==165')
        script=folder/(name+'.lua');script.write_text(text);runner.ROOT=folder
        results[name]=runner.run(script,P,timeout=45)
        (O/'native-results.json').write_text(json.dumps(results,indent=2)+'\n')
        assert results[name]==0,name
    # Three full native CV3 suites keep their exact source-specific controls.
    for v,name in enumerate(('grant','sypha','alucard'),1):
        source=R/f'build/verification/cv3-adoption-mr/final-v2/{name}/{name}.lua'
        folder=O/name;folder.mkdir(exist_ok=True);script=folder/(name+'.lua');script.write_text(source.read_text());runner.ROOT=folder
        results[name]=runner.run(script,P,timeout=45);assert results[name]==0,name
    (O/'native-results.json').write_text(json.dumps(results,indent=2)+'\n')

if __name__=='__main__':main()
