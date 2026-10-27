"""Bind an existing exact current3b ROM/debug alias; never restore removed trees."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
D=Path(r'C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
O=D/'current3b-cheats-four-draft-v8/baseline-alias-v1.json'
assert not O.exists()
p=ROOT/'build/smb-crossover-mmc5-expanded.nes'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(p)=='3b112e1d79ba7348f2f7a4c426f4675845a5781017ab74690feb235121a66287'
b=scoped_load(p)
expected={
 'GuestGameRoutinesBridge':(127,0xe02b,'ad1c6ff0128d6a01a9c98d6c01a9b78d6d01a98a4c5a018d6a01a9218d6c01a9a08d6d01a9814c5a01'),
 'GuestWaterStompPolicy':(127,0xe054,'ade37f60'),
 'CheatsInjuryTimer':(126,0x8d28,'ad9b070dfb7f60'),
 'GameRoutines':(1,0xa021,'a50f20098aaaa2e3a122a201a238a556'),
 'PlayerCtrlRoutine':(1,0xa0c3,'a50fc90bf04fad5307d020a4a4d00fad'),
 'NonMaskableInterrupt':(127,0xe33c,'488a489848ada17d48ad39011031ee3a')}
rows=[]
for n,(bank,pc,hx)in expected.items():
 off=location(b,n)
 assert (off-16)//8192==bank and address(b,n)==pc
 assert b['raw'][off:off+len(bytes.fromhex(hx))]==bytes.fromhex(hx),n
 rows.append(dict(name=n,physical_bank=bank,PC=pc,file_offset=off,compiled_bytes=hx))
assert address(b,'GuestBodyStompAllowed')==0x7fe3
assert address(b,'CheatInvincible')==0x7ffb and address(b,'InjuryTimer')==0x079b
vectors=b['raw'][16+128*8192-6:16+128*8192]
assert int.from_bytes(vectors[:2],'little')==address(b,'NonMaskableInterrupt')
old=D/'root-current-roster-composition-v1/candidate.nes'
assert not old.exists() and not old.with_suffix('.dbg').exists()
v=dict(passed=True,source_CPU_only=True,baseline_alias_changed_only=True,
 bindings=[dict(path=str(z),size=z.stat().st_size,sha256=sha(z))for z in[p,p.with_suffix('.dbg'),p.with_suffix('.lbl')]],
 compiled_hook_bindings=rows,native_vectors=vectors.hex(),
 missing_prior_path=str(old),removed_tree_not_recreated=True,
 retained_setup_failure=dict(path=str(D/'current3b-cheats-four-draft-v8/cpu-final-wrapper-v1'),
 classification='FileNotFoundError loading removed baseline debug before any wrapper assertions; no game failure or ROM change.'),
 limits='Exact ROM plus selected actual compiled-label/code/vector checks. Full qualified-symbol and caller comparisons run separately on this same alias.')
O.write_text(json.dumps(v,indent=2)+'\n',newline='\n')
print(json.dumps(dict(passed=True,output=str(O),sha256=sha(O))))
