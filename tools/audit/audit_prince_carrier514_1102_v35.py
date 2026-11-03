"""Actual613b SMB3-source refinement and publisher proof for candidate514.

The old514 prohibition is retained as historical evidence. Only the exact
current factored selector can retire that old consumer; no blank-byte grant.
"""
from pathlib import Path
from types import SimpleNamespace
import contextlib,hashlib,io,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools/reference')]
import prepare_prince_successor_manifest_1102_v26 as M
from check_tmnt_render_oa import address,location
O=M.O;PAGE=514
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
 base,_,_,_=M.bundle();raw=base['raw'];pool=json.loads((O/'pool-proposal.json').read_text());assert all(PAGE not in v for v in pool['domains'].values())
 # Rebind the inherited complete actual writer instructions and private
 # source1KB carriers. None of these tests treats a private-image offset as
 # a main-ROM file offset.
 inv=R/'build/metal-storm-chr-closure-1101-v10/current-consumer-inputs.json';old=json.loads(inv.read_text());count=0;moved=[]
 helper=R/'build/wwf-helper-stable-1102-v2';helperbin=(helper/'proposed.bin').read_bytes();helpertext=(helper/'source.s').read_text();helperstart=16+26*8192+0x800
 assert raw[helperstart:helperstart+len(helperbin)]==helperbin
 for w in old['unchanged_inherited_writers']:
  if Path(w['file']).suffix!='.nes':continue
  at=w['file_offset'];data=bytes.fromhex(w['old_bytes'])
  if raw[at:at+len(data)]==data:count+=1;continue
  assert w['segment']=='CROSSOVER_HELPERS'and data[0]==0x9d and w['rule'].startswith(('HpConfigure91-byte clear','Helper source platform index0..2')),(w['segment'],at)
  assert w['source']['text']in helpertext,w['source']['text']
  moved.append(dict(old_file_offset=at,old_bytes=data.hex(),current_bytes=raw[at:at+len(data)].hex(),current_source=w['source']['text'],finite_rule=w['rule']))
 assert len(moved)==10
 assert address(base,'HpRamEnd')<=address(base,'X5ChrMode') and address(base,'HpRamStart')>address(base,'CurrentCHRBank')+12
 assert 'ldx #HpRamEnd-HpRamStart-1\nClear:\n  sta HpRamStart,x'in helpertext and 'cpx #3\n  bcs Next'in helpertext
 assert not any(n in helpertext for n in ['X5SetPhysicalChr','X5PublishChr','CurrentCHRBank','ChrPhysicalMap','SmChrBank'])
 private=[];prior=json.loads((O/'writer-preservation.json').read_text())
 for w in prior['private_writer_bindings']:
  matches=[p for p in w['source_page_matches']if hashlib.sha256(raw[1048592+1024*p:1048592+(p+1)*1024]).hexdigest()==w['source_chunk_SHA256']]
  assert matches,(w['segment'],w['source_offset']);private.append(dict(segment=w['segment'],source_offset=w['source_offset'],pages=matches))
 # The exact source-derived selector constraint that retired795 also
 # retires514: all low pointers select Form0 and high is literal2.
 m3=json.loads((O/'smb3-pages.json').read_text());priorrom=(R/'build/arthur-side-clamp-1101-v8/weapon-tail-candidate.nes').read_bytes();same=[]
 for name,n in [('M3ChrLoTableLo',7),('M3ChrLoTableHi',7),('M3ChrHiTableLo',7),('M3ChrHiTableHi',7),('M3Form0ChrLo',81),('MbChrOffsets',7)]:
  at=location(base,name);assert raw[at:at+n]==priorrom[at:at+n],name;same.append(dict(name=name,file_offset=at,bytes=n,SHA256=hashlib.sha256(raw[at:at+n]).hexdigest()))
 def cpu_bytes(name,expected):
  at=location(base,name);assert raw[at:at+len(expected)]==expected,name
 cpu_bytes('M3SetFrame::Chr',bytes.fromhex(m3['current_source_constraint']['exact_live_caller_bytes']));cpu_bytes('MbFloatReadChrLow',bytes.fromhex(m3['current_source_constraint']['exact_live_helper_bytes']))
 script=R/'tools/audit/check_excitebike_smb3_pages_1101_v1.py';text=script.read_text().replace('from link_pit_rygar_sophia_audit_cpu import scoped_load','scoped_load=SUPPLIED_LOAD').replace("O=R/'build/excitebike-pose-1101-v3'","O=R/'build/prince-actor-1101-v1'").replace("R/'build/shinobi-camera-1101-v20/candidate.nes'","R/'build/bub-menu-candidate-1102-v2/combined-event.nes'").replace("O/'smb3-pages.json'","O/'extra514-smb3-v35.json'")
 env=dict(__file__=str(script),__name__='prince_current514_smb3',SUPPLIED_LOAD=lambda path:base);exec(compile(text,str(script),'exec'),env)
 with contextlib.redirect_stdout(io.StringIO()):env['main']()
 current=json.loads((O/'extra514-smb3-v35.json').read_text());assert current['pages']==list(range(524,544))and current['ROM_SHA256']==M.A.PIN
 # Existing protocol tester reconstructs its own exact current native
 # symbol/span inventory and runs real lag-NMI setter/menu instruction cuts.
 pub=R/'tools/audit/check_prince_chr_publication_1102_v1.py';text=pub.read_text().replace('import audit_prince_pool_1102_v1 as A','A=PROVIDED')
 text=text.replace("env=dict(__file__=str(original)","source=source.replace('publication-CPU-controls.json','extra514-publication-v35.json')\n env=dict(__file__=str(original)")
 text=text.replace("O/'publication-CPU-controls.json'","O/'extra514-publication-v35.json'")
 adapter=SimpleNamespace(R=R,O=O,ROM=M.A.BASE,SHA=M.A.PIN,POOL=[PAGE],sha=sha)
 env=dict(__file__=str(pub),__name__='prince_current514_publication',PROVIDED=adapter);exec(compile(text,str(pub),'exec'),env)
 with contextlib.redirect_stdout(io.StringIO()):env['main']()
 publication=json.loads((O/'extra514-publication-v35.json').read_text());assert publication['passed']and publication['no_proposed_page_published']
 # All subsequent source-granted owners are explicit. CurrentBubv9 and
 # privatePrincev30 scatter descriptors do not acquire adjacent pages.
 occupied={*M.POOL,301,305,337,362,363,440,441,666,819,*range(728,740)};assert PAGE not in occupied
 page=raw[1048592+1024*PAGE:1048592+1024*(PAGE+1)]
 q=dict(passed=True,proposal_only=True,resource_granted=False,ROM_written=False,base_SHA256=M.A.PIN,candidate_page=PAGE,file_offset=1048592+1024*PAGE,bytes=1024,preimage_SHA256=hashlib.sha256(page).hexdigest(),source_funding='Historical514 consumer was retired by exact current SMB3 Form0+typedoffset factor. Actual7forms81frames2faces1134cases publish only524..543. Not a blank/zero-content inference.',inherited_direct_writer_instructions_exact=count,moved_helper_writers_source_rebound=moved,current_helper_exact_bytes=len(helperbin),current_helper_source_RAM_domain=[address(base,'HpRamStart'),address(base,'HpRamEnd')],current_helper_finite_domain_does_not_write_CHR_shadow=True,all_private_writer_source_chunks_exact=len(private),private_writer_bindings=private,source_selector_table_bindings=same,actual_M3SetFrame_cases=current['actual_M3SetFrame_cases'],current_SMB3_pages=current['pages'],actual_current_protocol=dict(setter_cuts=publication['actual_typed_setter_instruction_cuts'],native_menu_cuts=publication['actual_native_Mario_menu_clear_restore_cuts'],real_lag_NMI_returns=publication['real_NMI_returns'],unpublished_transient_pairs=publication['unpublished_transient_proposed_pairs'],no514_hardware_publication=True),finite_current_domains_exclude514=True,all_current_Prince43_Bub9_Ex12_excluded=True,old_prohibition='docs/qa/checkpoints/2026-11-01/shinobi-chr-resource-grant.json:514 actual old SMB3 form table. This proposal requires explicit root supersession for514 only;512 IRQ remains excluded.',remaining=['Root independent publication/preimage/finite consumer review and grant before any write.','Current native proxy/original full battle/palette/box policies and live RAM2fit remain separate.'],scope='Current613b exact finite-source carrier proposal;806inherited direct instructions and15private source chunks exact. Ten old helper-ledger stores moved in the root-installed WWF helper; exact2858Bcurrent source bind and finite91B/3entryledger domains replace stale PC assumptions. No new image, ROMsize, allocation or character admission.',bindings={p.relative_to(R).as_posix():sha(p)for p in [Path(__file__),inv,O/'pool-proposal.json',O/'writer-preservation.json',O/'smb3-pages.json',O/'extra514-smb3-v35.json',O/'extra514-publication-v35.json',helper/'source.s',helper/'proposed.bin',M.A.BASE,R/'docs/qa/checkpoints/2026-11-01/shinobi-chr-resource-grant.json']})
 (O/'extra-carrier514-v35.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','private_writer_bindings','source_selector_table_bindings']}))


if __name__=='__main__':main()
