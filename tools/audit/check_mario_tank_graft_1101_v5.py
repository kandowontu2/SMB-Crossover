"""Re-run frozen real-ROM protocol on current two-row selected-worker graft."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from prepare_mario_tank_visible_1101_v5 import O
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 source=R/'tools/audit/check_mario_tank_loader_1101_v4.py';text=source.read_text()
 replacements=[
 ('from prepare_mario_tank_loader_1101_v4 import P,PIN,O,V2,REF,GATES,LOANS,CONTACT','from prepare_mario_tank_graft_1101_v5 import P,PIN,O,V2,REF,GATES,LOANS,CONTACT'),
 ("O/'assembly.json'","O/'graft-assembly.json'"),("O/'loader.lbl'","O/'graft.lbl'"),("'art502.chr'","'art-code502.bin'"),
 ("code=(O/'code501.bin').read_bytes();art=","code=(O/'code501.bin').read_bytes()+(O/'art-code502.bin').read_bytes();art="),
 ('0xd600<=i<0xda00','0xd600<=i<0xde00'),('len(self.code_reads)==1024','len(self.code_reads)==2048'),
 ('0x1600:0x1a00','0x1600:0x1e00'),('len(m.code_reads)==len(m.code_writes)==1024','len(m.code_reads)==len(m.code_writes)==2048'),
 ('seed.ppu_reads+2050','seed.ppu_reads+4100'),('range(0xd600,0xda00)','range(0xd600,0xde00)'),
 ("(V2/'host.lbl')","(O/'visible.lbl')"),
 ("('MtRomInjuryV3',32","('MtRomInjuryV3',58"),("('MtRomBeginPowerupV3',94","('MtRomBeginPowerupV3',35"),
 ('bytes(1024)','bytes(2048)'),('code_copy_and_readback_bytes=1024','code_copy_and_readback_bytes=2048')]
 for before,after in replacements:assert before in text,before;text=text.replace(before,after)
 ns=dict(__file__=str(Path(__file__)),__name__='tank_v5_graft_protocol');exec(compile(text,str(source),'exec'),ns);ns['main']()
 p=O/'CPU-controls.json';q=json.loads(p.read_text());q['derived_protocol_source']=dict(path=str(source.relative_to(R)),sha256=sha(source.read_bytes()),exact_replacements=[dict(before=a,after=b)for a,b in replacements]);q['scope_correction']='Current367 two-row2048B code/metadata/art loader; selected-only721B worker and306B clipped native renderer. Current old-owner fields in inherited limits/protocol remain historical and are superseded by this statement. This still does not execute owning Main or menu admission.'
 p.write_text(json.dumps(q,indent=2)+'\n')
if __name__=='__main__':main()
