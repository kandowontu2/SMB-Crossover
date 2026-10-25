from pathlib import Path
import hashlib,json,sys
D=Path(__file__).resolve().parent;R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');V=D/'mmc3-static-call-v39';P=D/'mmc3-ship-lives-v25';O=V/'layout-v1';O.mkdir(exist_ok=False)
sys.path.insert(0,str(R/'tools/audit'))
from check_tmnt_render_oa import load,address,location
old=load(P/'candidate.nes');new=load(V/'candidate.nes');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert new['raw']==(D/'mmc3-static-call-v37/candidate.nes').read_bytes()
def seg(b,n):return next(z for z in b['segs'].values()if z['name']=='"'+n+'"')
a,b=seg(old,'SMCCODE'),seg(new,'SMCCODE');pad=seg(new,'M3_CALL_PADDING')
assert int(a['start'],0)==int(b['start'],0)==0x155 and int(a['size'],0)==49 and int(b['size'],0)==6
assert int(a['ooffs'],0)==int(b['ooffs'],0)and int(pad['ooffs'],0)==int(b['ooffs'],0)+6 and int(pad['size'],0)==43
expected=dict(NextBank_SMC=0x13e,SafecallA_SMC=0x155,FarcallJmpTarget_SMC=0x157,SafereturnA_SMC=0x159)
assert all(address(new,n)==v for n,v in expected.items())
assert (location(new,'FarCallCommon')-16)//8192==254 and (location(new,'M3ResetBlockHealthCold')-16)//8192==253
assert address(new,'MegaManResetBlockHealth')==address(old,'MegaManResetBlockHealth')and int(new['syms']['MegaManResetBlockHealth']['size'])==92
audio_old=seg(old,'VIC_NATIVE_AUDIO');audio_new=seg(new,'VIC_NATIVE_AUDIO');assert all(audio_old[k]==audio_new[k]for k in['start','size','ooffs'])
off,size=int(audio_old['ooffs'],0),int(audio_old['size'],0);assert old['raw'][off:off+size]==new['raw'][off:off+size]
for f in ['src/zelda2_link_state.inc','chr/characters/oversized-raw.chr']:
 assert (V/'source'/f).read_bytes()==(P/'source'/f).read_bytes()
cfg=(V/'source/smb1base-mmc3-oversized.cfg').read_text();assert 'M3_CALL_RAM'not in cfg
ram=[]
for n,s in old['syms'].items():
 g=old['segs'].get(s.get('seg'));v=int(s['val'],0)
 if s.get('type')=='lab'and g and g.get('type')=='rw'and v<0x8000 and n not in ['SMCCODE','NextBank','SafecallA','FarcallJmpTarget','SafereturnA']:
  assert n in new['syms']and address(new,n)==v,(n,hex(v),new['syms'].get(n));ram.append(n)
rows=json.loads((D/'mmc3-static-call-v37/abi-cpu-v1/cases.json').read_text());cycles={}
for kind in ['support','cell']:
 d=[z['candidate_cycles']-z['parent_cycles']for z in rows if z['kind']==kind];cycles[kind]=dict(cases=len(d),minimum_added_cycles=min(d),maximum_added_cycles=max(d))
q=dict(passed=True,goal_complete=False,ROM_sha256=sha(V/'candidate.nes'),parent_ROM_sha256=sha(P/'candidate.nes'),byte_identical_to_V37=True,existing_RAM_labels_checked=len(ram),all_checked_RAM_addresses_unchanged=True,ZeldaII_alias_source_exact=True,original_native_Gradius_driver_bytes_exact=True,unchanged_native_Gradius_segment_bytes=size,original_CHR_source_exact=True,tiny_code_run=[0x155,0x15b],old_code_run=[0x155,0x186],named_operand_aliases=expected,isolated_added_cycles=cycles,scope='Read-only linked layout and original-driver/source byte comparisons. Six actual stack-page bytes retain the original base, no Zelda II overlap or new board RAM/CHR. Resident common code and appended cold parser body have explicit native banks. Isolated cycle costs are measured; the cell-reset relocation adds parser work, so native performance benchmarking remains required. No constant60Hz, native all-music data-read or campaign/source-fidelity claim.')
(O/'proof.json').write_text(json.dumps(q,indent=2));print(json.dumps(q),flush=True)
