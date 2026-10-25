from pathlib import Path
import hashlib,json,sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'tools/audit'))
from check_tmnt_render_oa import load,location
from check_tmnt_audio_fallback_oc import qualified
A=D/'food-candidate-v2/candidate.nes';B=D/'food-candidate-v3/candidate.nes'
a,b=load(A),load(B);qa,qb=qualified(A),qualified(B)
assert qa==qb, 'HUD position must preserve every symbol/address'
diff=[i for i,(x,y) in enumerate(zip(a['raw'],b['raw'])) if x!=y]
assert len(diff)==2
assert sorted((a['raw'][i],b['raw'][i]) for i in diff)==[(12,0),(108,4)]
pattern=bytes([0xa9,108,0x85,4,0xa9,0,0x85,5,0xa9,12,0x85,6])
# R4/R5/R6 are assembler symbols rather than assumed zero-page aliases.
pattern=bytes([0xa9,108,0x85,qa[('R4',)],0xa9,0,0x85,qa[('R5',)],0xa9,12,0x85,qa[('R6',)]])
assert a['raw'].count(pattern)==1
start=a['raw'].index(pattern);assert diff==[start+1,start+9]
assert a['raw'][16+1048576:]==b['raw'][16+1048576:]
parent=json.loads((D/'food-static-v2.json').read_text());assert parent['passed'] and parent['ROM_sha256']==hashlib.sha256(A.read_bytes()).hexdigest()
wave=json.loads((D/'wave-static-v1.json').read_text());assert wave['passed']
q=dict(passed=True,ROM_sha256=hashlib.sha256(B.read_bytes()).hexdigest(),parent_ROM_sha256=hashlib.sha256(A.read_bytes()).hexdigest(),previous_qualified_symbols_exact=len(qa),changed_ROM_bytes=2,changed_PRG_banks=sorted({(i-16)//8192 for i in diff}),CHR_changes=0,HUD_old_origin=[108,12],HUD_new_origin=[4,0],opcode_and_instruction_cycles_unchanged=True,other_ROM_bytes_exact=True,parent_collection_proof_sha256=hashlib.sha256((D/'food-static-v2.json').read_bytes()).hexdigest(),parent_wave_proof_sha256=hashlib.sha256((D/'wave-static-v1.json').read_bytes()).hexdigest(),scope='Only two HUD coordinate immediate operands differ from the verified combined candidate. No extra sprite, art or timing. Parent collection and motion proofs remain explicitly parent-hash evidence; current native regressions and physical HUD review are separate gates.')
(D/'food-hud-static-v3.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))
