"""Finite current publisher rebind for DK Jr's eleven proposed pages.

Reads existing compact ledgers and exact current bytes, not historical trees.
No output image or page write is made, and a positive audit is not a grant.
"""
import contextlib,io,json,re
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A
import audit_current_menu_indicators_1102_v1 as MENU
R=A.R;O=A.O;W=A.W;sha=A.sha


def main():
    raw=A.BASE.read_bytes();assert sha(raw)==A.PIN
    root=R/'docs/qa/checkpoints/2026-11-02';oldpath=R/'build/metal-storm-chr-closure-1101-v10/current-consumer-inputs.json'
    old=json.loads(oldpath.read_text());bbpath=root/'bubble-bobble-resources-v1/current3-domain-rebind.json';bb=json.loads(bbpath.read_text())
    princepath=root/'prince-resource-pool-v1/pool-proposal.json';prince=json.loads(princepath.read_text())
    domains=dict(bb['finite_domains'])
    for name in ['RCR extra','Kamikaze','Full roster preview','RCR','Celeste','SMB2 roster','GB Pit','MAAA','Rogue body','Rogue weapons','Rogue death','Rogue items','DragonPower actual body and wave','SMB3 current actual selector','KbFullChr']:
        domains[name]=prince['domains'][name]
    domains['Prince granted44']=[*prince['proposed_physical_CHR_pages'],291,514]
    domains['Bub granted9']=[301,305,337,362,363,440,441,666,819]
    domains['IRQ explicit excluded']=[512]
    domains['Turtle world weapon']=[628]
    targets=set(A.CODE+A.ART)
    collisions={k:sorted(set(v)&targets)for k,v in domains.items()if set(v)&targets};assert not collisions,collisions
    b=MENU.bundle();b['raw']=raw
    # Current family menu metadata overrides only its public names. Expanded
    # earlier debug metadata remains available for original native services.
    current=W.scoped_load(R/'build/menu-family-root-candidate-1102-v1/mr-gimmick-family.nes')
    mapping={}
    for key,value in current['segs'].items():
        new='DK_current_menu_'+str(key);b['segs'][new]=value;mapping[key]=new
    for key,value in current['syms'].items():
        row=dict(value)
        if 'seg'in row:row['seg']=mapping[row['seg']]
        b['syms'][key]=row
    # Rebind the exact complete inherited write instruction ledger. The ten
    # helper writes were source-relocated in the already delivered WWF helper.
    helper=R/'build/wwf-helper-stable-1102-v2';hb=(helper/'proposed.bin').read_bytes();ht=(helper/'source.s').read_text();at=16+26*8192+0x800;assert raw[at:at+len(hb)]==hb
    direct=0;moved=[];unbound=[]
    for x in old['unchanged_inherited_writers']:
        if Path(x['file']).suffix!='.nes':continue
        at=x['file_offset'];data=bytes.fromhex(x['old_bytes'])
        if raw[at:at+len(data)]==data:direct+=1;continue
        if x['segment']=='CROSSOVER_HELPERS'and data[0]==0x9d and x['rule'].startswith(('HpConfigure91-byte clear','Helper source platform index0..2'))and x['source']['text']in ht:
            moved.append(dict(old_offset=at,source=x['source']['text'],finite_rule=x['rule']))
        else:unbound.append(dict(segment=x['segment'],offset=at,old=data.hex(),current=raw[at:at+len(data)].hex()))
    assert not unbound,unbound
    assert len(moved)==10 and not any(n in ht for n in ['X5SetPhysicalChr','X5PublishChr','CurrentCHRBank','ChrPhysicalMap','SmChrBank'])
    wp=R/'build/prince-actor-1101-v1/writer-preservation.json';prior=json.loads(wp.read_text());private=[]
    for x in prior['private_writer_bindings']:
        pages=[p for p in x['source_page_matches']if sha(raw[1048592+p*1024:1048592+(p+1)*1024])==x['source_chunk_SHA256']]
        assert pages,(x['segment'],x['source_offset'])
        private.append(dict(segment=x['segment'],source_offset=x['source_offset'],pages=pages))
    # The current finite tables are rebound by exact bytes/hashes. Retired
    # SMB3 form tables are deliberately not reinstated as live domains.
    tables=[]
    def check(name,size,expected_sha):
        at=W.location(b,name);data=raw[at:at+size];assert sha(data)==expected_sha,(name,at)
        tables.append(dict(name=name,offset=at,bytes=size,SHA256=expected_sha));return data
    for x in bb['current_table_bindings']:check(x['name'],x['bytes'],x['SHA256'])
    for name,x in prince['current_table_proofs'].items():
        at=x['file_offset'];assert sha(raw[at:at+x.get('rows',x.get('bytes',0))])==x['sha256'],name
    # Specific prospective old consumers are source-bounded, never blank
    # image arguments: Gimmick816/818; Parodius18pool tables; Arthur868..880.
    for kind in ['Body','Special','Pickup']:
        lo_at=W.location(b,'PnPool'+kind+'Lo');hi_at=W.location(b,'PnPool'+kind+'Hi')
        pages=sorted(set(raw[lo_at+i]+256*raw[hi_at+i]for i in range(18)))
        assert pages==domains['Parodius '+kind],(kind,pages)
        tables.extend([dict(name='PnPool'+kind+'Lo',offset=lo_at,bytes=18,SHA256=sha(raw[lo_at:lo_at+18])),dict(name='PnPool'+kind+'Hi',offset=hi_at,bytes=18,SHA256=sha(raw[hi_at:hi_at+18]))])
    # Current complete Select cycle traverses all32 families. NMI hardware
    # publication cuts are a separate required protocol receipt.
    script=R/'tools/audit/inventory_playable_menu_1101_v3.py';source=script.read_text().replace("out/'inventory.json'","out/'resource-menu-v13.json'")
    env=dict(__file__=str(script),__name__='dk_current_menu_rebind');exec(compile(source,str(script),'exec'),env)
    env['scoped_load']=lambda path:b
    import sys
    saved=sys.argv;sys.argv=[str(script),'--rom',str(A.BASE),'--output',str(O)]
    try:
        with contextlib.redirect_stdout(io.StringIO()):env['main']()
    finally:sys.argv=saved
    menu=json.loads((O/'resource-menu-v13.json').read_text());assert menu['ROM_sha256']==A.PIN
    assert not any(x['raw']==40 for x in menu['rows'])
    q=dict(passed=True,proposal_only=True,resource_granted=False,ROM_written=False,current_ROM_SHA256=A.PIN,proposed_code=A.CODE,proposed_art=A.ART,
        preimages=[dict(page=p,offset=1048592+p*1024,SHA256=sha(raw[1048592+p*1024:1048592+(p+1)*1024]))for p in A.CODE+A.ART],
        current_finite_domains=domains,domain_collisions=collisions,current_table_bindings=tables,inherited_direct_writes_exact=direct,source_relocated_helper_writes=moved,private_writer_chunks_exact=private,
        current_menu=dict(select_states=menu['select_states'],distinct_names=menu['distinct_named_entries'],accepted_names=menu['confirmable_named_entries'],raw_values=sorted({x['raw']for x in menu['rows']}),new_raw40_absent=True,DK_slot27=[x for x in menu['rows']if x['slot']==27]),
        source_basis={'817':'Gimmick typed graphics and star routines publish816 or818;819 is already Bub code.','833/847/856/867':'Current18Parodius body/special/pickup pool tables exclude these four holes.','881/882/883':'Arthur current source body/common domain is868..880.','959/960/961':'Current Parodius pools were compacted away from these historical image pages. ContraForce cold domain ends958; Bowser927..934, Battletoads915..926, Quick884..892, FF893..900 are retained. Source-backed selector domains, not blank contents.'},
        complete_current_publisher_closure=True,complete_hardware_publication_protocol=False,
        remaining=['Actual typed setter/native menu/lagNMI transient publication controls for this exact11page set.','Root independent source/domain/preimage review and exact physical grant. No use of the Prince conservative832..1024 reservation is implied by this target-specific refinement.','New raw40 public constructor/service/IRQ/retirement and menu selector admission remain ungranted.'],
        scope='Current16a9 finite source/domain and instruction-writer rebind, exact proposed-page preimages and actual compiled full Select cycles. Exact inherited instruction and relocated-writer counts are reported separately. No arbitrary-shadow-value or Mesen guarantee.',
        bindings={p.relative_to(R).as_posix():sha(p.read_bytes())for p in[Path(__file__),A.BASE,bbpath,princepath,oldpath,wp,helper/'source.s',helper/'proposed.bin',script,O/'resource-menu-v13.json',R/'docs/qa/checkpoints/2026-11-02/sunny-palette-v9/receipt.json']})
    (O/'carrier-proposal-v13.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:q[k]for k in ['passed','current_ROM_SHA256','proposed_code','proposed_art','inherited_direct_writes_exact','complete_current_publisher_closure','complete_hardware_publication_protocol','current_menu']}))


if __name__=='__main__':main()
