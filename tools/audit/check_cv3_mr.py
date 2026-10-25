"""Combined CV3 source-pixel and native gameplay admission over MQ."""
from pathlib import Path
import hashlib,importlib.util,itertools,json,re,sys
R=Path(__file__).resolve().parents[2]
D=R/'build/player-guide-agent/cv3-private'
V=R/'build/verification/cv3-adoption-mr'
O=V/'final-v2'
P=V/'cv3-final-v2.nes'

def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
    O.mkdir(exist_ok=True)
    sys.path.append('C:/Users/kando/AppData/Local/Programs/Python/Python314/Lib/site-packages')
    source=(D/'check_candidate.py').read_text().replace("P=D/'cv3-expanded.nes'","P=Path("+repr(str(P))+")").replace("(D/'component-proof.json')","(Path("+repr(str(O))+ ")/'component-proof.json')")
    assert "P=D/'cv3-expanded.nes'" not in source
    (O/'component-check.py').write_text(source)
    exec(compile(source,str(D/'check_candidate.py'),'exec'),{'__file__':str(D/'check_candidate.py'),'__name__':'root_cv3'})
    g=module('mr_cpu',R/'build/player-guide-agent/check_mmc5_expand.py')
    oldp=R/'build/checkpoints/palette-roster-mq/build/smb-crossover-mmc5-expanded.nes'
    oldl=g.labels(oldp);l=g.labels(P)
    moved={n:(oldl[n],l[n]) for n in oldl.keys()&l.keys() if oldl[n]!=l[n] and n in ('RosterGraphicsBank','MegaManCollisionAdder','MegaManCollisionBox','ExpandedCollisionBox','ExpandedCollisionAdder','ExpandedGraphicsBank','IrqScrollSplit','PlayerGfxHandler','GameEngine')}
    assert not moved,moved
    c=g.make(P,l);m=c.memory;smc=bytes(m.ram[0x15a:0x1f0]);names=palette=0
    for variant,area,bg in itertools.product(range(4),range(4),range(8)):
        m.ram[:]=bytes(65536);m.ram[0x15a:0x15a+len(smc)]=smc;m.banks=[126,78,83,127]
        m.ram[l['CurrentBank']]=206;m.ram[l['CurrentBankC']]=211
        for n,v in [('SelectedCharacter',5),('AreaType',area),('BackgroundColorCtrl',bg)]:m.ram[l[n]]=v
        m.ram[0x5fe7]=variant
        g.execute(c,l['X5GetPlayerColors'])
        offset=m.ram[l['VRAM_Buffer1_Offset']];data=bytes(m.ram[l['VRAM_Buffer1']:l['VRAM_Buffer1']+offset+1])
        if variant:
            colors={1:(8,21,56),2:(33,17,32),3:(15,21,54)}[variant]
            assert data[-7:]==bytes((0x3f,0x11,3,*colors,0));palette+=1
        m.ram[l['VRAM_Buffer1_Offset']]=0;m.banks[1]=66;m.ram[l['CurrentBank']]=194
        g.execute(c,l['QueueSelectName'])
        result=bytes(m.ram[l['VRAM_Buffer1']+3:l['VRAM_Buffer1']+19])
        name=[' SIMON BELMONT  ','     GRANT      ','     SYPHA      ','    ALUCARD     '][variant]
        assert result==bytes(0x24 if x==' ' else ord(x)-55 for x in name),(variant,result)
        names+=1
    raw=P.read_bytes();asset=(R/'chr/characters/cv3.chr').read_bytes()
    assert len(asset)==65536 and raw[16+1048576+460*1024:16+1048576+524*1024]==asset
    (O/'integration-proof.json').write_text(json.dumps(dict(passed=True,sha256=hashlib.sha256(raw).hexdigest(),palette_cases=palette,native_name_cases=names,physical_CHR_slice=True,selected_legacy_public_PCs_fixed=True),indent=2)+'\n')
    runner=module('mr_mesen',R/'tools/run_mesen.py')
    results={}
    for v,name in enumerate(('grant','sypha','alucard'),1):
        folder=O/name;folder.mkdir(exist_ok=True)
        # Inline the shared scripts so this candidate writes no private packet evidence.
        body=(D/'native_cv3.lua').read_text()
        features=(D/'native_features.lua').read_text().split('dofile([[',1)[0]
        script=folder/(name+'.lua');script.write_text('CV3_VARIANT='+str(v)+'\n'+features+'\n'+body)
        runner.ROOT=folder;results[name]=runner.run(script,P,timeout=45);assert results[name]==0,name
    regressions=[('ship',R/'build/vic-viper-ml-private/native_vic_gear_v3.lua'),('turtle',R/'build/verification/vic-adoption-mp/final-turtle-natural/turtle-natural.lua'),('chip',R/'build/verification/chip-dale-candidate-agent/native_chip_interactions.lua'),('kirby',R/'build/verification/kirby-adoption-me/final-fixtures/food-v5.lua'),('darkwing',R/'build/verification/palette-adoption-mq/darkwing/darkwing.lua'),('zelda2',R/'build/verification/palette-adoption-mq/zelda2/zelda2.lua'),('proto',R/'build/verification/protoman-candidate-agent/native_proto.lua')]
    for name,path in regressions:
        folder=O/('regression-'+name);folder.mkdir(exist_ok=True)
        text=path.read_text().replace("st['cpu.pc']>=0xe000","st['cpu.pc']>=L.IrqScrollSplit and st['cpu.pc']<L.IrqScrollSplit+68")
        script=folder/(name+'.lua');script.write_text(text);runner.ROOT=folder
        results[name]=runner.run(script,P,timeout=45);assert results[name]==0,name
    (O/'native-results.json').write_text(json.dumps(results,indent=2)+'\n')
    print('PASS combined source pixels, native threeCV3 menus/features and seven existing new-profile regressions')

if __name__=='__main__':main()
