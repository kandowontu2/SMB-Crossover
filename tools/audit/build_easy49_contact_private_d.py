"""Add source enemy stomp eligibility without expanding resident dispatch spans."""
from pathlib import Path
import hashlib,importlib.util,json,shutil,subprocess,sys
R=Path(__file__).resolve().parents[2];P=R/'build/verification/root49-easy-injury-private-a';H=R/'build/verification/root49-easy-contact-private-d';S=H/'source';B=R/'build/verification/root49-easy-hard-user-baseline-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
EXTRA='''; OldCharacter.hitEnemy tests bottom+enemy.stompable without a water ban.
; Original Bloopa and swimming Cheep cannot be stomped; flying Cheep can.
.pushseg
.segment "SRAM"
GuestBodyStompAllowed: .res 1
.segment "OAMALIGNED"
.proc GuestWaterStompPolicy
  lda GuestBodyStompAllowed
  rts
.endproc
.segment "SAMUS"
.proc GuestSourceStompPolicy
  lda AreaType
  sta GuestBodyStompAllowed
  lda CrossoverBehaviorVersion
  bne Done
  lda SelectedCharacter
  cmp #CHARACTER_SIMON+1
  bcs Done                    ; Later additions retain the existing policy.
  lda Enemy_ID,x
  cmp #Bloober
  beq Blocked
  cmp #GreyCheepCheep
  beq Blocked
  cmp #RedCheepCheep
  beq Blocked
  lda #1
  bne Store
Blocked:
  lda #0
Store:
  sta GuestBodyStompAllowed
Done:
  rts
.endproc
.popseg
'''
def main():
    sys.dont_write_bytecode=True;assert not H.exists()
    previous=json.loads((P/'build-review-c.json').read_text());assert all(sha(P/'source'/n)==h for n,h in previous['all_candidate_source_hashes'].items())
    base=json.loads((B/'baseline.json').read_text());assert all(sha(R/n)==h for n,h in base['current_source_hashes'].items())
    H.mkdir();shutil.copytree(P/'source',S,ignore=shutil.ignore_patterns('build','__pycache__'))
    body=S/'src/guest_body_contact.s';text=body.read_text();a=text.index('.proc GuestBodyContactBridge');z=text.index('.endproc',a)+len('.endproc')
    old=text[a:z];(H/'original-resident-bridge.s').write_text(old)
    # Exactly the old35-byte resident span: retain every following global PC.
    replacement='''.proc GuestBodyContactBridge
  farcall GuestBodyContact
  rts
  .res 35-(*-GuestBodyContactBridge),$ea
.endproc'''
    text=text[:a]+replacement+text[z:]
    needle='  pha\n  lda #1\n  sta GuestBodyNoStomp'
    assert text.count(needle)==1
    text=text.replace(needle,'''  pha
  jsr GuestSourceStompPolicy
  lda SelectedCharacter
  beq NativeBody
  cmp #CHARACTER_LUIGI
  beq NativeBody
  lda #1
  sta GuestBodyNoStomp''')
    needle='Ordinary:\n  pla\n'
    assert text.count(needle)==1
    text=text.replace(needle,'''NativeBody:
  lda #0
  sta GuestBodyNoStomp
Ordinary:
  pla
''')
    body.write_text(text)
    p=S/'src/collision.s';text=p.read_text();old='       lda AreaType                 ;branch if water type level\n       beq ContactInjury'
    assert text.count(old)==1
    text=text.replace(old,'       jsr GuestWaterStompPolicy    ;Cached native/source enemy eligibility.\n       beq ContactInjury');p.write_text(text)
    (S/'src/guest_source_stomp.s').write_text(EXTRA)
    with(S/'src/entrypoint.s').open('a')as f:f.write('\n.if ::ENABLE_CROSSOVER\n.include "guest_source_stomp.s"\n.endif\n')
    driver=H/'build-driver.py';code=(P/'corrected-build-driver-b.py').read_text();old='ROOT = Path('+repr(str(P/'source'))+')';assert code.count(old)==1;driver.write_text(code.replace(old,'ROOT = Path('+repr(str(S))+')'))
    report=dict(status='BUILDING_SOURCE_STOMP_ELIGIBILITY',script_sha256=sha(__file__),builds=[],main_changed=False,complete_Easy_behavior=False,accepted_release=False,goal_complete=False)
    def save():(H/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    save();spec=importlib.util.spec_from_file_location('stomp_image',R/'build/verification/agent49g-samus-crouch-fix-proposal-b/image.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    for mapper in ['mmc3','mmc5']:
        log=H/(mapper+'-build.log')
        with log.open('wb')as f:rc=subprocess.run([sys.executable,str(driver),'--mapper',mapper],cwd=R,stdout=f,stderr=subprocess.STDOUT).returncode
        row=dict(mapper=mapper,exit=rc,log_sha256=sha(log));report['builds'].append(row);save();assert rc==0
        im=mod.Image(S/('build/smb-crossover-'+mapper+'.nes'));before=mod.Image(P/('source/build/smb-crossover-'+mapper+'.nes'))
        assert all(im.ram[n]==v for n,v in before.ram.items())
        assert im.ram['GuestBodyStompAllowed']==0x7fe3
        assert im.raw[16+64*8192:]==before.raw[16+64*8192:]
        assert im.sym('GuestBodyContactBridge')['size']==before.sym('GuestBodyContactBridge')['size']==35
        for sym in before.data['sym']:
            if sym.get('scope')!=1 or 'seg'not in sym or 'val'not in sym:continue
            segment=before.segs[sym['seg']]['name']
            if segment in ['FIXED','OAMALIGNED','BASS_DPCM','COLLISION']:
                assert im.sym(sym['name'])['val']==sym['val'],('resident PC preserved',sym['name'])
        ds=next(v for v in im.segs.values()if v['name']=='BASS_DPCM');assert im.raw[ds['ooffs']:ds['ooffs']+ds['size']]==before.raw[ds['ooffs']:ds['ooffs']+ds['size']]
        row.update(ROM_sha256=sha(im.path),old_RAM_exact=True,resident_global_PCs_exact=True,CHR_exact=True,DPCM_exact=True,
            segments={n:next(v for v in im.segs.values()if v['name']==n)for n in ['SAMUS','OAMALIGNED','COLLISION','SRAM']});save()
    assert all(sha(R/n)==h for n,h in base['current_source_hashes'].items())
    report['status']='PASS_PRIVATE_SOURCE_STOMP_BUILD_ONLY';report['all_source_hashes']={n:sha(S/n)for n in previous['all_candidate_source_hashes']}|{'src/guest_source_stomp.s':sha(S/'src/guest_source_stomp.s')};save();print(report['status'],sha(H/'report.json'),flush=True)
if __name__=='__main__':main()
