"""Literal old/new full native name-producer ABI, including returned carry."""
from pathlib import Path
import hashlib,importlib.util,json,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';D=V/'root49-sophia-source-terrain-ib';G=V/'ryu49-head-status-bridge-g'
sys.path.insert(0,str(G));s=importlib.util.spec_from_file_location('names_bus',G/'check.py');g=importlib.util.module_from_spec(s);s.loader.exec_module(g);CPU=g.loadcpu().NesMPU
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
 out=D/'status-name-ie.json';assert not out.exists();report=dict(status='RUNNING',script_sha256=sha(__file__),maps=[])
 for mapper in ['mmc3','mmc5']:
  old=g.Image(V/'root49-sophia-source-body-hs/source/build'/('smb-crossover-'+mapper+'.nes'));new=g.Image(D/'source/build'/old.path.name);cases=[]
  for char in range(14):
   for variant in [0,1]:
    ram=bytearray((i*37+13)&255 for i in range(10240));L=new.ram
    for n,value in [('SelectedCharacter',char),('BillVariant',variant),('CurrentBank',3|(128 if new.mapper==5 else 0))]:ram[g.at(L[n])]=value
    if new.mapper==4:ram[g.at(L['BankShadow'])]=0x47
    sp=0xe9;ram[0x101+sp]=(g.RET-1)&255;ram[0x102+sp]=(g.RET-1)>>8
    banks={0x8000:62,0xa000:3,0xc000:36,0xe000:63};regs=[0,0x55,0x33,0x81,sp]
    a=g.execute(old,CPU,ram,regs,banks,old.hook('CrossoverPatchStatusName')['address'],g.RET,native_status=True)
    b=g.execute(new,CPU,ram,regs,banks,new.hook('CrossoverPatchStatusName')['address'],g.RET,native_status=True)
    assert a['ram']==b['ram'],('Every10240RAM/name/stack byte',mapper,char,variant)
    semantic_a=[(x[2],x[4])for x in a['trace']];semantic_b=[(x[2],x[4])for x in b['trace']]
    assert semantic_a==semantic_b,('Every ordered actual VRAM-buffer/scratch/push write',mapper,char,variant)
    cases.append(dict(character=char,variant=variant,old=a['regs'],new=b['regs'],sameRegisters=a['regs']==b['regs'],cyclesDelta=b['cycles']-a['cycles']))
  report['maps'].append(dict(mapper=mapper,cases=cases,all_RAM_and_ordered_name_writes_literal=True))
 report['status']='PASS'if all(x['sameRegisters']for m in report['maps']for x in m['cases'])else'FAIL_RETAINED_RETURN_STATUS'
 out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status=report['status'],cases=56,differences=sum(not x['sameRegisters']for m in report['maps']for x in m['cases']))))
 raise SystemExit(0 if report['status']=='PASS'else 1)


if __name__=='__main__':main()
