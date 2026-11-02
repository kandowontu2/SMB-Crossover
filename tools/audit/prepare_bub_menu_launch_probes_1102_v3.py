"""Bind revised existing-family launch probes without touching passed packets."""
from pathlib import Path
import argparse,json,sys,copy
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from prepare_selected_native_packet_v1 import prepare,sha
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
import prepare_bub_menu_qualification_1102_v2 as N
O=N.O;W=O/'ordered-input-v3'

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--modes',default='bt-start,cf-start')
    ap.add_argument('--rom',type=Path,default=O/'candidate.nes')
    ap.add_argument('--sha256',default='90a7108003343ad9f5f9719f860f44f09d1e1932194d5eac1c89bc473e932dd8')
    a=ap.parse_args();modes=a.modes.split(',');assert modes and set(modes)<=set(['bub-start','bob-start','bt-start','cf-start'])
    rom=a.rom.resolve();assert sha(rom)==a.sha256;b=scoped_load(rom)
    plans=json.loads((W/'native-menu-plans.json').read_text())['plans'];source=R/'tools/audit/bub_menu_qualification_1102_v2.lua';body=source.read_text()
    outputs=[]
    for mode in modes:
        if mode in['bub-start','bob-start']:assert b['raw'][16+66*8192+0xd64]==0x18,'Unready raw39 launch remains forbidden by actual SEC gate'
        q=copy.deepcopy(plans[mode]);at=location(b,'GroundPaletteData');q['restore']=list(b['raw'][at+24:at+27])
        names=['CrossoverMenuState','CrossoverMenuIndex','OperMode','OperMode_Task','SelectedCharacter','FmGroups','VRAM_Buffer1_Offset','VRAM_Buffer1','GameEngineSubroutine']
        prefix='\n'.join(f'L[{json.dumps(n)}]={address(b,n)}'for n in names)+'\nlocal Q='+N.lua(q)+'\n'
        output=O/('native-ordered-'+mode)
        refs={Path(__file__),source,Path(N.__file__),W/'native-menu-plans.json',W/'CPU-ordered-input.json',O/'metadata-repair.json',R/'docs/qa/allocations/bub-menu-static-1102-v3.json'}
        prepare(output,rom,prefix+body,refs,expected=a.sha256,timeout=120,scope=q['scope']+' Correct original Select-before-confirm ordering; root execution pending.',allow_interactive=True)
        outputs.append(output.relative_to(R).as_posix())
    files=[p for p in O.rglob('*')if p.is_file()];assert sum(p.stat().st_size for p in files)<32000000 and len(files)<=128
    print(json.dumps(dict(prepared=outputs,native=False,executed=False,bytes=sum(p.stat().st_size for p in files),files=len(files))))
if __name__=='__main__':main()
