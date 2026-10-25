from pathlib import Path
import importlib.util,json
D=Path(__file__).resolve().parent;base=D/'extend_pz_mmc3_v11.py';spec=importlib.util.spec_from_file_location('v11',base);v11=importlib.util.module_from_spec(spec);spec.loader.exec_module(v11)
def once(t,a,b):
 assert t.count(a)==1,(a,t.count(a));return t.replace(a,b)
def apply(source):
 v11.apply(source)
 p=source/'smb1base-mmc3-oversized.cfg';t=p.read_text()
 for bank in ('F7','F8','FC'):t=once(t,f'M3_FREE_{bank}: start=$a000',f'M3_FREE_{bank}: start=$c000')
 t=once(t,'M3_MENU: load=M3_FREE_F7,type=ro;','M3_MENU: load=M3_FREE_F9,type=ro;');p.write_text(t)
 (source.parent/'window-fix-v12.json').write_text(json.dumps(dict(scope='Preserve actual original CPU windows when relocating newer banks. Roll and two Parodius art pools are C-window data; Parodius NMI also executes in C. The A-window menu shares the spacious existing Parodius bells bank.',new_RAM_bytes=0,C_window_banks=['F7','F8','FC'],menu_A_window_bank='F9',no_audio_disabled=True),indent=2))
