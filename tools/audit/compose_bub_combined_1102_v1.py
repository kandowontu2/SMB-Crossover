"""Check the frozen frontend/backend union; emit only with root's exact grant."""
from pathlib import Path
import argparse,hashlib,json,re,sys,zipfile
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import plan_bub_combined_frontend_1102_v1 as F
from prepare_selected_native_packet_v1 import sha
O=F.O;BACK=R/'build/bubble-bobble-source-1101-v1'
MANIFEST=BACK/'native-proxy-shared-proposal-1966.json'
MANIFEST_PIN='2b7cb50eec12c4c60ce563a188daab2a8e2c42e28f2519c94f797377f406201c'
FREEZE=BACK/'native-proxy-qualified-1102-v5.json'

def verify_inputs():
    assert sha(F.BASE)==F.PIN and sha(MANIFEST)==MANIFEST_PIN
    backend=json.loads(MANIFEST.read_text());freeze=json.loads(FREEZE.read_text())
    assert backend['passed'] and backend['proposal_only'] and not backend['ROM_written'] and not backend['admitted']
    assert backend['base_ROM_SHA256']==F.PIN and freeze['manifest_SHA256']==MANIFEST_PIN
    archive=R/freeze['archive'];assert sha(archive)==freeze['archive_SHA256']
    with zipfile.ZipFile(archive)as z:
        assert z.testzip()is None
        for name,row in freeze['files'].items():
            assert sha(R/name)==row['SHA256'],name
            assert len(z.read(name))==row['bytes'] and hashlib.sha256(z.read(name)).hexdigest()==row['SHA256'],name
    for name,digest in backend['receipts'].items():
        assert sha(R/name)==digest and json.loads((R/name).read_text())['passed'],name
    front=json.loads((O/'frontend-current-freeze-v3.json').read_text())
    for name,digest in front['bindings'].items():assert sha(R/name)==digest,name
    frontrows=json.loads((R/'build/bub-menu-integration-1102-v1/controls-proposal.json').read_text())['all_patches']
    rows=backend['patches'];assert len(rows)==25
    raw=F.BASE.read_bytes();back,_,_=F.fold_patches(raw,rows)
    assert hashlib.sha256(back).hexdigest()==backend['in_memory_backend_only_over1966_SHA256']
    out,owned,changed=F.fold_patches(raw,frontrows+rows)
    assert out[F.GATE]==0x38 and out[792580:792583]==bytes.fromhex('3aaf88')
    frontout,_,frontchanged=F.fold_patches(raw,frontrows)
    assert len(frontchanged)==1249
    # Every frontend byte survives the backend overlay and all unowned bytes
    # remain current1966. The old37 veneers/real B0FB are explicitly unchanged.
    assert all(out[i]==frontout[i]for i in frontchanged)
    assert out[16+65*8192+0x108c:16+65*8192+0x10fb]==raw[16+65*8192+0x108c:16+65*8192+0x10fb]
    assert out[16+65*8192+0x10fb:16+65*8192+0x1100]==raw[16+65*8192+0x10fb:16+65*8192+0x1100]
    assert out[16+79*8192:16+80*8192]==raw[16+79*8192:16+80*8192]
    assert backend['bodygate_ordinary_contact_row']==37 and backend['HuBody11_profile_reject']
    return backend,frontrows,rows,out,changed

def approved(grant,frontrows,backrows):
    """A path alone is insufficient: the root grant binds every exact row."""
    q=json.loads(grant.read_text())
    assert q['granted'] and q['private_native_candidate_allowed'] and not q['production_menu_admitted']
    assert not q['native_playable']
    assert q['base_ROM_SHA256']==F.PIN and q['approved_proposal_SHA256']==MANIFEST_PIN
    key=lambda p:(p['offset'],p['old'],p['new'])
    gate={k:q['private_confirmation_patch'][k]for k in['offset','old','new']}
    assert gate==dict(offset=F.GATE,old='38',new='18')
    approved_shared={(p['file_offset'],p['old_hex'],p['new_hex'])for p in q['shared_exact_spans']}
    assert approved_shared=={key(p)for p in backrows[:16]}
    assert len(q['existing_carriers'])==9
    for p,row in zip(q['existing_carriers'],backrows[16:]):
        assert p['file_offset']==row['offset']
        assert p['old_SHA256']==hashlib.sha256(bytes.fromhex(row['old'])).hexdigest()
        assert p['new_SHA256']==hashlib.sha256(bytes.fromhex(row['new'])).hexdigest()
    # Root must bind the already-granted frontend and the successor backend
    # lease, rather than interpreting a former storage grant as admission.
    for path,digest in q['bindings'].items():assert sha(R/path)==digest,path
    for name in['bub-menu-1102-v1.json','bub-menu-flags-1102-v2.json','bub-menu-static-1102-v3.json','roster-rebase-1102-v4.json']:
        p=R/'docs/qa/allocations'/name;g=json.loads(p.read_text());assert g['granted'],name
    return q,gate

def emit_metadata(stem):
    # This exact complete minimal metadata was imported successfully by native
    # Mesen. Do not repeat the four incomplete synthetic segments from native1.
    source=O/'candidate.dbg';text=source.read_text()
    assert 'id=900000'not in text and 'info\t'in text
    assert all('def='not in s and'ref='not in s and'scope='not in s for s in text.splitlines()if s.startswith('sym\t'))
    from link_pit_rygar_sophia_audit_cpu import scoped_load
    b=scoped_load(F.BASE);old=scoped_load(O/'candidate.nes')
    ex=(R/'build/excitebike-pose-1101-v3/native5/controller.lua').read_text()
    names=set(old['syms'])|set(re.findall(r"r\('([^']+)'\)",ex))|set(re.findall(r"L\['([^']+)'\]",ex))
    names.update('FrameCounter Player_State Player_Y_HighPos A_B_Buttons ObjectMetasprite SmPosePtr PlayerFacingDir PlayerStatus PlayerSize InjuryTimer GamePauseStatus TimerControl Enemy_Flag Enemy_ID Enemy_State Enemy_X_Position Enemy_PageLoc Enemy_Y_Position Enemy_Y_HighPos Enemy_X_Speed Enemy_Y_Speed Enemy_MovingDir EnemyIntervalTimer PlatformCollisionFlag Player_X_Scroll Player_X_Speed Player_Y_Speed Player_XSpeedAbsolute SavedJoypadBits NumberofLives'.split())
    symbols=[];segments={}
    for name in sorted(names):
        assert name in b['syms'],name
        if name in old['syms']:assert b['syms'][name]['val']==old['syms'][name]['val'],name
        z={k:v for k,v in b['syms'][name].items()if k in['name','addrsize','size','val','seg','type']}
        z.update(id=len(symbols),name='"'+name+'"');symbols.append(z)
        if 'seg'in z:
            seg=z['seg'];segments[seg]={k:v for k,v in b['segs'][seg].items()if k in['name','start','size','addrsize','type','oname','ooffs']}
            segments[seg]['id']=seg
    fields=lambda d:','.join(k+'='+str(v)for k,v in d.items())
    assert all('addrsize'in s and'oname'in s for s in segments.values()if s['type']=='ro')
    lines=['version\tmajor=2,minor=0','info\t'+fields(dict(csym=0,file=0,lib=0,line=0,mod=0,scope=0,seg=len(segments),span=0,sym=len(symbols),type=0))]
    lines+=['seg\t'+fields(s)for s in segments.values()]+['sym\t'+fields(s)for s in symbols]
    stem.with_suffix('.dbg').write_text('\n'.join(lines)+'\n')
    stem.with_suffix('.lbl').write_text('\n'.join('al %06X .%s'%(int(s['val'],0),s['name'].strip('"'))for s in symbols)+'\n')

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--emit',action='store_true');ap.add_argument('--grant',type=Path)
    a=ap.parse_args();backend,frontrows,backrows,out,changed=verify_inputs()
    grant=None;gate=None
    if a.grant:grant,gate=approved(a.grant,frontrows,backrows)
    assert not a.emit or grant,'No ROM output before the exact root native-candidate grant'
    receipt=dict(passed=True,ROM_written=False,native=False,installed=False,menu_admitted=False,
        base_ROM_SHA256=F.PIN,backend_manifest_SHA256=MANIFEST_PIN,
        frontend_changed_bytes=1249,backend_patch_records=len(backrows),combined_changed_bytes=len(changed),
        blocked_combined_memory_SHA256=hashlib.sha256(out).hexdigest(),
        WWF3B_preserved=True,frontend_backend_disjoint=True,all_other_current_bytes_exact=True,
        old_Ex37_veneers_realB0FB_and_PRG79_exact=True,HuBody11_still_profile_reject=True,
        typed_ordinary_contact_row=37,confirmation_blocked=not bool(grant),
        actual_backend_exports=backend['exported_actual_entries'],
        required_pending_grant='Root exact commonrouting/contact/Shports plus private native-candidate with explicit AD64SEC-to-CLC row',
        native_candidate_granted=bool(grant),
        bindings={p.relative_to(R).as_posix():sha(p)for p in[Path(__file__),Path(F.__file__),F.BASE,MANIFEST,FREEZE,O/'frontend-current-freeze-v3.json',O/'combined-front-plan-v1.json']})
    if a.emit:
        patched=bytearray(out);assert patched[F.GATE]==0x38;patched[F.GATE]=0x18
        target=O/'combined.nes';assert not target.exists(),'Do not overwrite a frozen candidate'
        target.write_bytes(patched);emit_metadata(target)
        receipt.update(ROM_written=True,ROM=target.relative_to(R).as_posix(),ROM_SHA256=sha(target),
            grant=a.grant.relative_to(R).as_posix()if a.grant.is_absolute()else a.grant.as_posix(),
            grant_SHA256=sha(a.grant),confirmation_patch=gate,confirmation_blocked=False,
            scope='Private root-native candidate only; no release/gameplay qualification or install implied')
        receipt['bindings'].update({p.relative_to(R).as_posix():sha(p)for p in[target,target.with_suffix('.dbg'),target.with_suffix('.lbl')]})
        destination=O/'combined.json'
    else:destination=O/'combined-check-v1.json'
    assert not destination.exists(),'Qualified check/packet remains immutable'
    destination.write_text(json.dumps(receipt,indent=2)+'\n')
    files=[p for p in O.rglob('*')if p.is_file()]
    assert sum(p.stat().st_size for p in files)<32000000 and len(files)<=128
    print(json.dumps({k:v for k,v in receipt.items()if k not in['bindings','actual_backend_exports']}))

if __name__=='__main__':main()
