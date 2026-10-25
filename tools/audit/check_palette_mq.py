"""Palette changes must not starve native deferred block replacement."""
from pathlib import Path
import hashlib, importlib.util, itertools, json, re, sys

R=Path(__file__).resolve().parents[2]
O=R/'build/verification/palette-adoption-mq'
P=O/'palette-final.nes'

def module(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
    sys.path.append('C:/Users/kando/AppData/Local/Programs/Python/Python314/Lib/site-packages')
    g=module('mq_cpu',R/'build/player-guide-agent/check_mmc5_expand.py')
    oldp=R/'build/checkpoints/vic-roster-mp/build/smb-crossover-mmc5-expanded.nes'
    def setup(p):
        l=g.labels(p);c=g.make(p,l);smc=bytes(c.memory.ram[0x15a:0x1f0]);return l,c,smc
    new,old=setup(P),setup(oldp)
    def reset(d,fields):
        l,c,smc=d;m=c.memory;m.ram[:]=bytes(65536);m.ram[0x15a:0x15a+len(smc)]=smc
        m.banks=[126,78,80,127];m.ram[l['CurrentBank']]=206;m.ram[l['CurrentBankC']]=208
        for n,v in fields.items():m.ram[l[n] if isinstance(n,str) else n]=v
    def call(d,routine,bank=78):
        l,c,_=d;m=c.memory;m.banks[1]=bank;m.ram[l['CurrentBank']]=bank|128
        g.execute(c,l[routine]);n=m.ram[l['VRAM_Buffer1_Offset']]
        return bytes(m.ram[l['VRAM_Buffer1']:l['VRAM_Buffer1']+n+1])
    exact=changed=0
    for char,variant,area,bg in itertools.product(list(range(15))+[18,19],range(2),range(4),range(8)):
        fields=dict(SelectedCharacter=char,PlayerStatus=1,DarkwingVariant=variant,Z2Variant=variant,AreaType=area,BackgroundColorCtrl=bg)
        reset(new,fields);reset(old,fields)
        result=call(new,'X5GetPlayerColors')
        if (char,variant) not in ((4,1),(12,1)):
            assert result==call(old,'X5GetPlayerColors'),fields;exact+=1
        else:
            colors=(0x18,0x36,0x2a) if char==4 else (0x13,0x30,0x27)
            assert result[-7:]==bytes((0x3f,0x11,3,*colors,0)),fields
            backdrop=(0x22,0x22,0xf,0xf,0xf,0x22,0xf,0xf)[bg if bg else area]
            assert bytes((0x3f,0x10,1,backdrop)) in result;changed+=1
    draw=0
    for char,routine,bank in ((12,'DwScroogeGraphics',67),(4,'Z2GraphicsGate',69)):
        reset(new,dict(SelectedCharacter=char,DarkwingVariant=1,Z2Variant=1,AreaType=1))
        call(new,'X5GetPlayerColors')
        l,c,_=new
        for frame in range(240):
            c.memory.ram[l['VRAM_Buffer1_Offset']]=0;c.memory.ram[l['VRAM_Buffer1']]=0
            c.memory.ram[l['FrameCounter']]=frame
            assert call(new,routine,bank)==bytes((0,)),(char,frame)
            draw+=1
    # Shield is the one dynamic ZeldaII body color; retry a rejected queue.
    l,c,_=new;m=c.memory
    reset(new,dict(SelectedCharacter=4,Z2Variant=1,AreaType=1))
    call(new,'X5GetPlayerColors');assert m.ram[0x5e2d]==0x80
    m.ram[l['InvAmmo']+9]=1;m.ram[l['VRAM_Buffer1_Offset']]=0x70
    call(new,'Z2GraphicsGate',69);assert m.ram[0x5e2d]==0x80
    m.ram[l['VRAM_Buffer1_Offset']]=0
    assert call(new,'Z2GraphicsGate',69)==bytes((0x3f,0x11,3,0x18,0x36,0x16,0))
    assert m.ram[0x5e2d]==0x81
    m.ram[l['VRAM_Buffer1_Offset']]=0;m.ram[l['InvAmmo']+9]=0
    assert call(new,'Z2GraphicsGate',69)==bytes((0x3f,0x11,3,0x18,0x36,0x2a,0))
    report=dict(passed=True,sha256=hashlib.sha256(P.read_bytes()).hexdigest(),unchanged_palette_cases=exact,corrected_alternate_palette_cases=changed,draws_without_constant_queue=draw,shield_change_and_queue_retry=True)
    (O/'cpu-proof.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
    runner=module('mq_mesen',R/'tools/run_mesen.py')
    result={}
    for name,source in [('darkwing',R/'build/player-guide-agent/darkwing-private/native_darkwing.lua'),('zelda2',R/'build/verification/zelda2-link-candidate-agent/native_z2_interactions.lua')]:
        folder=O/name;folder.mkdir(exist_ok=True);script=folder/(name+'.lua');script.write_text(source.read_text());runner.ROOT=folder
        result[name]=runner.run(script,P,timeout=45);assert result[name]==0,name
    for target in ('darkwing','zelda2'):
        folder=O/(target+'-blocks');folder.mkdir(exist_ok=True)
        script=folder/'blocks.lua';script.write_text('TARGET="'+target+'"\n'+(R/'tests/alternate-block-publication-mq.lua').read_text());runner.ROOT=folder
        result[target+'-blocks']=runner.run(script,P,timeout=45);assert result[target+'-blocks']==0,target
    (O/'native-results.json').write_text(json.dumps(result,indent=2)+'\n')

if __name__=='__main__':main()
