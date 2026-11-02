import json,re
from pathlib import Path
import prepare_metal_storm_decline_1101_v40 as P
from prepare_selected_native_packet_v1 import prepare,sha
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address

def main():
 dest=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
 rom=P.O/'candidate.nes';assert sha(dest)==sha(rom)
 ref=P.O/'idle/controller.lua';t=ref.read_text();b=scoped_load(rom)
 names=set(re.findall(r"\br\('([^']+)'",t))|set(re.findall(r'\bL\.(\w+)',t))
 t='\n'.join(f'L[{json.dumps(n)}]={address(b,n)}' for n in sorted(names))+'\n'+t
 out=P.O/'downloads'
 prepare(out,rom,t,[Path(__file__),ref,dest],expected=sha(rom),timeout=90,scope='Actual Downloads path, cold title/select and120 idle plus120 walking; explicit symbol addresses only, no emulated state writes.')
 p=out/'ready.json';q=json.loads(p.read_text());q['ROM']=str(dest);p.write_text(json.dumps(q,indent=2)+'\n')
if __name__=='__main__':main()
