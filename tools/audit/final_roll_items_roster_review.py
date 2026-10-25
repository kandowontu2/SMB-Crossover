"""Bind an explicit offline selected-frame review; never starts an emulator or edits receipts."""
from pathlib import Path
import argparse,csv,hashlib,json
from PIL import Image

SHA='8ff245ae662059abbc77c5de517260032775b7ba881a5201b8b54686ccf08277'
SELECTED=[('darkwing','easy'),('roll','easy'),('sophia','easy'),('kirby','easy'),('meta','easy'),('mac','easy'),('mike','easy'),('vic','easy'),('octopus','easy'),('twinbee','easy'),('pentarou','easy'),('raphael','easy'),('michelangelo','easy'),('mario3','easy'),('luigi3','easy'),('grant','easy'),('rygar','easy'),('leonardo','easy'),('ryu','easy'),('ryu','hard'),('donatello','easy'),('scrooge','easy'),('link','easy'),('dale','hard'),('simon','easy'),('chip','easy')]
EXTRA={('sophia','easy'):[3651,3653],('octopus','easy'):[585,587,588],('bass','hard'):[2737,2739,2750],('mike','easy'):[1980,1981,1982],('luigi3','easy'):[1353,1354,1355],('ryu','easy'):[2830,2831,2832]}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--batch',type=Path,required=True);p.add_argument('--bass-batch',type=Path,required=True)
    p.add_argument('--notes',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();source=[a.batch/'proof.json',a.bass_batch/'proof.json'];before={str(q):sha(q)for q in source}
    batches=[json.loads(q.read_text(encoding='utf-8'))for q in source];assert all(q['ROM_sha256']==SHA for q in batches)
    notes={}
    for line in a.notes.read_text(encoding='utf-8').splitlines():
        q=json.loads(line);notes[q['identity'],q['mode']]=q
    profiles=[];bindings=before.copy();context=[]
    for name,mode in SELECTED+[('bass','hard')]:
        z=batches[1 if name=='bass'else 0];r=next(q for q in z['runs']if(q['identity'],q['mode'])==(name,mode))
        assert len(r['samples'])==8 and notes[name,mode]['reviewed_frames']==8
        assert 'pending'not in notes[name,mode]['classification']
        for key in ['direct_proof','scan_proof','sample_sheet']:
            q=Path(r[key]);assert sha(q)==r[key+'_sha256'];bindings[str(q)]=sha(q)
        folder=Path(r['direct_proof']).parent;index=folder/'direct-frame-index.csv';direct=json.loads(Path(r['direct_proof']).read_text(encoding='utf-8'))
        assert sha(index)==direct['frame_index_sha256'];bindings[str(index)]=sha(index)
        with index.open(encoding='utf-8')as f:idx={int(q['frame']):q for q in csv.DictReader(f)}
        sheet=Image.open(r['sample_sheet']).convert('RGB');assert sheet.size==(1024,528)
        samples=[]
        for i,s in enumerate(r['samples']):
            q=Path(s['PNG']);im=Image.open(q).convert('RGB');rgb=hashlib.sha256(im.tobytes()).hexdigest()
            assert sha(q)==s['PNG_sha256']==idx[s['frame']]['PNG_sha256']
            assert rgb==idx[s['frame']]['RGB_sha256']
            x,y=(i%4)*256,(i//4)*264+24;assert sheet.crop((x,y,x+256,y+240)).tobytes()==im.tobytes()
            bindings[str(q)]=sha(q);samples.append(dict(s,RGB_sha256=rgb))
        for n in EXTRA.get((name,mode),[]):
            q=folder/'frames'/f'{n:06d}.png';rgb=hashlib.sha256(Image.open(q).convert('RGB').tobytes()).hexdigest()
            assert sha(q)==idx[n]['PNG_sha256'] and rgb==idx[n]['RGB_sha256'];bindings[str(q)]=sha(q)
            context.append(dict(identity=name,mode=mode,frame=n,PNG=str(q),PNG_sha256=sha(q),RGB_sha256=rgb))
        for q in r['candidate_sheets']:assert sha(Path(q['path']))==q['sha256'];bindings[q['path']]=q['sha256']
        profiles.append(dict(identity=name,mode=mode,sample_sheet=r['sample_sheet'],sample_sheet_sha256=r['sample_sheet_sha256'],samples=samples,notes=notes[name,mode],candidate_sheets=r['candidate_sheets'],direct_proof=r['direct_proof'],direct_proof_sha256=r['direct_proof_sha256'],scan_proof=r['scan_proof'],scan_proof_sha256=r['scan_proof_sha256']))
    for name in ['sophia','octopus']:
        r=next(q for q in profiles if q['identity']==name);folder=Path(r['direct_proof']).parent
        for n in ['render.csv','oam.csv','trace.csv']:bindings[str(folder/n)]=sha(folder/n)
    assert all(sha(Path(q))==v for q,v in bindings.items())
    a.output.mkdir(parents=True,exist_ok=False)
    result=dict(status='selected_frame_review_complete_with_open_findings',review_complete=True,goal_complete=False,
        every_frame_reviewed=False,source_fidelity_certified=False,no_new_native_launch=True,game_changes=False,
        ROM_sha256=SHA,script_sha256=sha(Path(__file__)),notes_sha256=sha(a.notes),selected_sheets=27,
        selected_actual_frames=216,selected_unique_identities=26,extra_context_frames=len(context),
        all_sheet_cells_exact_to_hashed_actual_PPU_PNGs=True,all_selected_and_context_RGBs_exact_to_direct_indices=True,
        profiles=profiles,extra_context=context,immutable_input_bindings=bindings,
        open_visibility_findings=['Octopus586/587bodydropout relative585/588; sourcepriority/causeunproved.','Sophia3651..3653bodyobscuredbylargeweapon/effectcluster; sourcepriority/causeunproved.'],
        known_issue='Luigi1354contextalso showsknownM3Pmetercloudglyphs, separatefromflaggedquestion-blockcell. LaterROOTrepairnotreviewedhere.',
        scanner_classification='Mike1981cell15,5; Luigi1354cell14,5; Ryu2831cells5,5/2,9/5,9/8,9 all locatequestionblockregions withordinaryanimation/scrollalignment variation. No new green-stagecorruption demonstrated by these3flags. Notanallgraphicsverdict.',
        limits=['27sheetsx8samples plus17specificneighbor/contextframes, notall183205scannedframes orall37identities.','TwoRyumodesareoneidentity. Historical8ffframesnotrelabeledcurrent/adoptedROM.','CHRmapping/body-constructionchecks do not close actual pixelvisibility/flicker concerns. Ordinaryspritelimit explanation alone is notclosure.','No everypowerup/form/ability/sourcepixel/audio/cadence/performance certification; originalandfailedreceipts unchanged.'])
    (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items()if k not in ['profiles','extra_context','immutable_input_bindings','limits']}))
    print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'))))


if __name__=='__main__':main()
