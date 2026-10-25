"""Execute the live pane: unchanged values, world priority and delayed refresh."""
from pathlib import Path
import argparse,hashlib,json
from check_tmnt_render_oa import load,Memory,address,location
from check_reported_contacts_pp import run
def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    def setup(path):
        b=load(path);m=Memory(b);m.page(1,(location(b,'Z2Hud')-16)//8192);m[address(b,'CurrentBank')]=m.banks[1]|128
        for n,v in dict(OperMode=1,OperMode_Task=3,GameEngineSubroutine=8,SelectedCharacter=4,Z2Variant=1,Z2Hp=127,Z2Mp=127,Z2Selection=1,Z2ExpLo=0x39,Z2ExpHi=0x30).items():m[address(b,n)]=v
        m.writes=[];return b,m
    b,m=setup(a.rom);before=bytes(m[address(b,'VRAM_Buffer1'):address(b,'VRAM_Buffer1')+128])
    c=run(b,m,'Z2Hud');initial=c.processorCycles
    assert m[address(b,'VRAM_Buffer1_Offset')]==34
    initial_packet=bytes(m[address(b,'VRAM_Buffer1'):address(b,'VRAM_Buffer1')+35])
    m[address(b,'VRAM_Buffer1_Offset')]=0;m[address(b,'VRAM_Buffer1')]=0;m.writes=[]
    c=run(b,m,'Z2Hud');unchanged=c.processorCycles
    assert m[address(b,'VRAM_Buffer1_Offset')]==0
    assert not any(address(b,'VRAM_Buffer1')<=at<address(b,'VRAM_Buffer2')for at,_ in m.writes)
    m.page(1,(location(b,'HudUpdateNumberLocal')-16)//8192);m[address(b,'CurrentBank')]=m.banks[1]|128
    run(b,m,'HudUpdateNumberLocal',a=2)
    assert m[address(b,'VRAM_Buffer1_Offset')]==0,'Native coins/score must not overwrite the owned spell/EXP row'
    m.page(1,(location(b,'Z2Hud')-16)//8192);m[address(b,'CurrentBank')]=m.banks[1]|128
    refreshes=0
    for n in ['Z2Hp','Z2Mp','Z2ExpLo','Z2ExpHi','Z2Selection']:
        m[address(b,n)]^=1
        m[address(b,'VRAM_Buffer1_Offset')]=10
        saved=bytes(m[address(b,'VRAM_Buffer1'):address(b,'VRAM_Buffer1')+128])
        run(b,m,'Z2Hud')
        assert bytes(m[address(b,'VRAM_Buffer1'):address(b,'VRAM_Buffer1')+128])==saved and m[address(b,'VRAM_Buffer1_Offset')]==10
        m[address(b,'VRAM_Buffer1_Offset')]=0
        run(b,m,'Z2Hud')
        assert m[address(b,'VRAM_Buffer1_Offset')]==34
        m[address(b,'VRAM_Buffer1_Offset')]=0;refreshes+=1
    old,prior=setup(a.baseline);c=run(old,prior,'Z2Hud');old_cycles=c.processorCycles
    assert bytes(prior[address(old,'VRAM_Buffer1'):address(old,'VRAM_Buffer1')+35])==initial_packet
    q=dict(passed=True,ROM_sha256=hashlib.sha256(a.rom.read_bytes()).hexdigest(),baseline_ROM_sha256=hashlib.sha256(a.baseline.read_bytes()).hexdigest(),native_packet_unchanged=True,delayed_field_refreshes=refreshes,
        CPU_cycles=dict(baseline_every_draw=old_cycles,candidate_initial=initial,candidate_unchanged=unchanged),scope='Linked live HUD routine only; whole-frame lag and IRQ timing require native replay.')
    (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q),flush=True)
if __name__=='__main__':main()
