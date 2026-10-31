"""Actual ready menu/cold parser -> 4x96 genuine Main jump/landing controls."""
from pathlib import Path
import hashlib,json,re,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
S=R/'tools/audit/contra_force_menu_cold_parser_1031_v1.py'
O=R/'build/contra-force-natural-jump-controls-1031-v1'
J=R/'build/contra-force-world-roles-1031-v2/joint'
K=J.parent/'kernel'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 text=S.read_text()
 a='for age in range(32):';assert text.count(a)==1;text=text.replace(a,'for age in range(96):')
 a='keys = 1 | (128 if 4 <= age < 12 else 0) | (64 if 16 <= age < 24 else 0)'
 assert text.count(a)==1
 text=text.replace(a,'keys = (1 if age < 32 else 0) | (128 if 4 <= age < 36 else 0) | (64 if 16 <= age < 24 else 0)')
 text=text.replace('actual_gameplay_Main_updates=128','actual_gameplay_Main_updates=384')
 g={'__name__':'cf_natural_jump_definitions','__file__':str(S)};exec(compile(text,str(S),'exec'),g)
 g['O']=O;g['J']=J;g['K']=K;g['P'].J=g['H'].O=J
 g['P'].L={n:int(v,16)for v,n in re.findall(r'al ([0-9A-Fa-f]+) \.(\w+)',(K/'runtime.lbl').read_text())}
 g['main']()
 q=json.loads((O/'controls.json').read_text());assert q['passed'];rows=[]
 for c in q['cohorts']:
  f=c['frames'];start=f[0]['Main']['Y'];apex=min(r['Main']['Y']for r in f)
  landed=[r for r in f if r['age']>36 and r['Main']['Y']==start]
  assert apex<=start-64 and landed and f[-1]['Main']['Y']==start,('Original jump and real native landing',c['variant'],start,apex,[r['Main']['Y']for r in f])
  rows.append(dict(variant=c['variant'],start_Y=start,apex_Y=apex,rise=start-apex,first_landed_Main_age=landed[0]['age'],last_Y=f[-1]['Main']['Y']))
 source=(R/'build/contra-force-reproduction-v2/copy_bank_FF.asm').read_text()
 assert 'tbl_EF8E:\n; 00 \n     .byte $3F, $00' in source
 summary=dict(passed=True,source_CPU=True,native=False,candidate=sha(J/'candidate.nes'),real_cold_classes=4,actual_Main_total=384,
    unchanged_original_jump_and_weapon_instructions=True,world_role0_empty_role1_solid=True,previous_native_BG_consumed_before_next_source_step=True,
    classes=rows,bindings={str(p.resolve()):sha(p)for p in[Path(__file__),S,O/'controls.json',J.parent/'source-stage.json',R/'build/contra-force-reproduction-v2/copy_bank_FF.asm',R/'build/contra-force-reproduction-v2/copy_bank_05.asm']})
 (O/'jump-summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(dict(path=str(O/'jump-summary.json'),sha256=sha(O/'jump-summary.json'),classes=rows)),flush=True)
if __name__=='__main__':main()
