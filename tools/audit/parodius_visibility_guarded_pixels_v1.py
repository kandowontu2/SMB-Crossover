"""Bind all131 compiled defaults/32alternates and model185 actual epochs."""
from pathlib import Path
from collections import defaultdict,deque,Counter
import argparse,copy,hashlib,json
from check_tmnt_render_oa import address
from check_roll_renderer import Memory
from link_pit_rygar_sophia_audit_cpu import scoped_load
from verify_native_relocation import NesMPU
from parodius_visibility_combined_pixels_v2 import model
from check_parodius_body_pixels_v1 import pixels
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for n in ['rom','baseline-run','body-config','safe-poses','manifest','output']:ap.add_argument('--'+n,type=Path,required=True)
    a=ap.parse_args();a.output.mkdir(parents=True,exist_ok=False);b=scoped_load(a.rom);raw=b['raw'];chrraw=raw[1048592:]
    cfg=json.loads(a.body_config.read_text());rr=list(cfg['body_sources'].values());safe={(r['pool'],r['frame'])for r in json.loads(a.safe_poses.read_text())};manifest=json.loads(a.manifest.read_text());pools={p['index']:p for p in manifest['pools']};checked=[]
    def data(bank,ptr):
        at=16+bank*8192+ptr%8192;size=raw[at];return[list(raw[i:i+4])for i in range(at+1,at+1+size,4)]
    for r in rr:
        ref=r['refs'][0];original=pools[ref['pool']]['records'][str(ref['frame'])];assert data(r['bank'],r['pointer'])==original
        supported=(ref['pool'],ref['frame'])in safe;alternate=data(r['bank'],address(b,'PnGuardAlt_'+r['label']))if supported else original
        assert Counter(map(tuple,original))==Counter(map(tuple,alternate))
        assert pixels(chrraw,pools[ref['pool']],original)==pixels(chrraw,pools[ref['pool']],alternate)
        checked.append(dict(label=r['label'],pool=ref['pool'],frame=ref['frame'],supported=supported,original_pointer=r['pointer'],alternate_pointer=address(b,'PnGuardAlt_'+r['label'])if supported else None))
    epochs=[json.loads(s)for s in(a.baseline_run/'epochs.jsonl').read_text().splitlines()];rows=[]
    for e in epochs:
        pub=e['dma']['publication'];body=pub['body'];ref=body['source']['refs'][0];t=pub['transaction'];mem=bytearray(65536)
        vals=dict(CurrentBank=205,CurrentBankC=body['bank']|128,SelectedCharacter=18,VvVariant=ref['variant'],PnPool=ref['pool'],PnFrame=ref['frame'],Player_X_Position=t['world_x']&255,Player_PageLoc=t['world_x']>>8,ScreenLeft_X_Pos=t['camera']&255,ScreenLeft_PageLoc=t['camera']>>8,Player_Y_Position=t['player_y'],Player_Y_HighPos=1,CurrentOAMOffset=body['cursor_before'],RgOamRotation=body['rotation'],GuestOamRotationActive=1,ObjectVerticalFlip=0,GameEngineSubroutine=8)
        for n,v in vals.items():mem[address(b,n)]=v
        ptr=body['pointer'];mem[address(b,'SmPosePtr')]=ptr&255;mem[address(b,'SmPosePtr')+1]=ptr>>8
        stop=0x5b00;sp=217;mem[0x101+sp]=(stop-1)&255;mem[0x102+sp]=(stop-1)>>8
        bus=Memory(raw,mem,{0x8000:126,0xa000:77,0xc000:body['bank'],0xe000:127});c=NesMPU(memory=bus);c.pc=address(b,'PnBodyOrderBankStub');c.sp=sp;c.a=body['bank']|128
        for _ in range(1000):
            if c.pc==stop:break
            c.step()
        else:raise AssertionError('selector timeout')
        pointer=bus.data[address(b,'SmPosePtr')]+256*bus.data[address(b,'SmPosePtr')+1]
        hardware=copy.deepcopy(e);projected=defaultdict(deque)
        for part,physical in zip(reversed(body['source']['parts']),body['parts'],strict=True):projected[tuple(part)].append(physical)
        for i,part in zip(body['indices'],reversed(data(body['bank'],pointer)),strict=True):hardware['start_hardware'][i*4:i*4+4]=projected[tuple(part)].popleft()
        assert not any(projected.values())
        old,_=model(e,chrraw);new,_=model(hardware,chrraw)
        bp=[{p:v for p,v in z.items()if v[0]}for z in [old,new]];other=[{p:(v[1],v[2])for p,v in z.items()if not v[0]}for z in [old,new]]
        counts=[len(z)for z in bp];core=[sum(v[1]==0 for v in z.values())for z in bp]
        assert counts[1]>=counts[0]and core[1]>=core[0]and other[0]==other[1]
        rows.append(dict(actual_PPU=e['start']['frame'],DMA=e['dma']['id'],publication=pub['id'],source=body['source']['label'],compiled_selected_pointer=pointer,selected_alternate=pointer!=ptr,model_body_pixels=counts,model_core_pixels=core,other_pixels_exact=True))
    (a.output/'records.json').write_text(json.dumps(checked,indent=2)+'\n');(a.output/'actual-epoch-counterfactual.json').write_text(json.dumps(rows,indent=2)+'\n')
    q=dict(passed=True,native_run=False,model_only=True,actual_RGB_retagged=False,ROM_sha256=sha(a.rom),tool_sha256=sha(Path(__file__)),original_body_records=131,compiled_sorted_records=32,literal_original_records_fallback=99,unlimited_palette_index_pixels_exact=True,part_multisets_exact=True,modeled_actual_epochs=len(rows),CPU_selected_alternate_epochs=sum(r['selected_alternate']for r in rows),body_improved_epochs=sum(r['model_body_pixels'][1]>r['model_body_pixels'][0]for r in rows),core_improved_epochs=sum(r['model_core_pixels'][1]>r['model_core_pixels'][0]for r in rows),body_core_regressions=0,other_sprite_pixel_changes=0,frame586=next(r for r in rows if r['actual_PPU']==586),records_sha256=sha(a.output/'records.json'),epochs_sha256=sha(a.output/'actual-epoch-counterfactual.json'),limits='Counterfactual executes actual compiled selector against source-bound df515 completed publication inputs, then permutes source-matched hardware body parts in a host copy only. Native v4 is UNRUN; no actual v4 RGB/cadence/audio or lifetime verdict. Per-row dominance source study separately binds32poses; others remain literal original. No source/CHR/production edits.')
    (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
