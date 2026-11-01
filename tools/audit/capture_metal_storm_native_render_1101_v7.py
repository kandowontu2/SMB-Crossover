"""Freeze only the exact linked renderer/CHR/SMC witnesses, never a ROM copy."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
OUT=ROOT/'build/metal-storm-render-host-1101-v7'
ROM=ROOT/'build/karnov-host-resource-base-1101-v1/candidate.nes'
SHA='0ffb1d79c4fbc52bb337a4726f8e61f984f30e4795fd2555b204322140c0a717'
DBG='baa9374b19d338f408029d4540866ddd1c49c5293ec4e35d9534ee5258793e31'
NAMES='MetaspriteRenderLoop X5PublishChr X5SetPhysicalChr FarCallCommon SafecallA_SMC FarcallJmpTarget_SMC CurrentBank CurrentBankC CurrentCHRBank CurrentOAMOffset GuestOamRotationActive RgOamRotation SelectedCharacter Player_X_Position Player_Y_Position Player_Y_HighPos ScreenLeft_X_Pos ScreenLeft_PageLoc Player_SprAttrib SsChrActive SsChrPhysical VRAM_Buffer1 VRAM_Buffer1_Offset ObjectMetasprite SmPosePtr OperMode GameEngineSubroutine R0 R1 R2 R3 R4 R5 R6 R7 X5ChrMode X5WideChrActive ReloadCHRBank X5SpecialChrUpper InvHudActive InvHudPhysical X5HudChrUpper ChrPhysicalMap'.split()
def main():
    if '--compact-existing'in sys.argv:
        path=OUT/'native-render-witness.json';result=json.loads(path.read_text())
        result['syms']={n:{k:v for k,v in s.items()if k in['name','val','seg','addrsize','size','type']}for n,s in result['syms'].items()}
        result['segs']={n:{k:v for k,v in s.items()if k in['id','name','start','size','addrsize','type','ooffs']}for n,s in result['segs'].items()}
        path.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,compacted=True,bytes=path.stat().st_size)));return
    assert hashlib.sha256(ROM.read_bytes()).hexdigest()==SHA
    assert hashlib.sha256(ROM.with_suffix('.dbg').read_bytes()).hexdigest()==DBG
    b=scoped_load(ROM);spans=[]
    for name,size in [('MetaspriteRenderLoop',182),('X5PublishChr',588),('ChrPhysicalMap',256)]:
        at=location(b,name);data=b['raw'][at:at+size]
        spans.append(dict(name=name,pc=address(b,name),offset=at,size=size,hex=data.hex(),sha256=hashlib.sha256(data).hexdigest()))
    smc=next(g for g in b['segs'].values()if g.get('name')=='"SMCCODE"')
    at,size=int(smc['ooffs'],0),int(smc['size'],0);data=b['raw'][at:at+size]
    spans.append(dict(name='SMCCODE',pc=int(smc['start'],0),offset=at,size=size,hex=data.hex(),sha256=hashlib.sha256(data).hexdigest()))
    syms={n:{k:v for k,v in b['syms'][n].items()if k in['name','val','seg','addrsize','size','type']}for n in NAMES}
    ids={s['seg']for s in syms.values()if 'seg'in s}|{smc['id']}
    segs={i:b['segs'][i]for i in ids}
    result=dict(passed=True,scope='Exact emitted native helper subset; no whole ROM/PRG/debug copy, native timing or admission claim.',ROM_sha256=SHA,debug_sha256=DBG,raw_length=len(b['raw']),spans=spans,syms=syms,segs=segs,total_witness_bytes=sum(s['size']for s in spans))
    (OUT/'native-render-witness.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True,witness_bytes=result['total_witness_bytes'],symbols=len(syms))))
if __name__=='__main__':main()
