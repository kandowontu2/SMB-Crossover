"""Compare full relocated spring procedure to the old compiled source routine."""
from pathlib import Path
import hashlib,importlib.util,json,sys,collections
R=Path(__file__).resolve().parents[2];V=R/'build/verification';D=V/'root49-sophia-source-terrain-if';G=V/'ryu49-head-status-bridge-g'
sys.path.insert(0,str(G));s=importlib.util.spec_from_file_location('spring_bus',G/'check.py');g=importlib.util.module_from_spec(s);s.loader.exec_module(g);CPU=g.loadcpu().NesMPU
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
 out=D/'spring-ih.json';assert not out.exists();report=dict(status='RUNNING',script_sha256=sha(__file__),maps=[],scope='Direct compiled original/candidate spring ABI and allRAM/ordered semantic writes, explicit component seeds. Actual native spring caller/interrupt testing remains required on the final composed runtime.')
 try:
  for mapper in ['mmc3','mmc5']:
   old=g.Image(V/'root49-sophia-source-body-hs/source/build'/('smb-crossover-'+mapper+'.nes'));new=g.Image(D/'source/build'/old.path.name);L=new.ram;rows=[];cycles=collections.Counter()
   for char in range(14):
    for mode in [0,1]:
     for force in [0xf9,0xf4]:
      for flags in [0,0xcf]:
       initial=bytearray((i*37+19)&255 for i in range(10240))
       for seg in new.segs.values():
        if seg['name']=='SMCCODE':initial[seg['start']:seg['start']+seg['size']]=new.raw[seg['ooffs']:seg['ooffs']+seg['size']]
       for n,v in [('SelectedCharacter',char),('CrossoverBehaviorVersion',mode),('JumpspringForce',force),('RgDoubleJump',0),('SmSourceJumped',0),('CurrentBankC',36)]:initial[g.at(L[n])]=v
       if new.mapper==4:initial[g.at(L['BankShadow'])]=0x47
       sp=0xe9;initial[0x101+sp]=(g.RET-1)&255;initial[0x102+sp]=(g.RET-1)>>8
       regs=[0xa5,0x59,0x33,flags,sp];outputs=[]
       for im in [old,new]:
        ram=bytearray(initial);bank=im.hook('MegaManSpringVelocityModes')['physical_bank'];ram[g.at(L['CurrentBank'])]=bank|(128 if im.mapper==5 else 0)
        outputs.append(g.execute(im,CPU,ram,regs,{0x8000:62,0xa000:bank,0xc000:36,0xe000:63},im.hook('MegaManSpringVelocityModes')['address'],g.RET,native_status=True))
       a,b=outputs
       assert a['regs']==b['regs'],('Complete registers/return',mapper,char,mode,force,flags,a['regs'],b['regs'])
       expected=bytearray(a['ram']);expected[g.at(L['CurrentBank'])]=58|(128 if new.mapper==5 else 0)
       if char==11:expected[g.at(L['RgDoubleJump'])]=1
       pushes={t[3]:t for t in b['trace']if t[1]in [8,0x48,0x20]and 0x100<=t[3]<=0x100+sp}
       changes=[]
       for i,(x,y)in enumerate(zip(expected,b['ram'])):
        if x==y:continue
        address=i if i<2048 else i-2048+0x6000
        assert address in pushes and pushes[address][4]==y,('Only individually decoded last push residue',mapper,char,mode,force,flags,address,x,y)
        expected[i]=y;changes.append(dict(address=address,writerPC=pushes[address][0],opcode=pushes[address][1],value=y))
       assert bytes(expected)==b['ram']
       assert b['ram'][0x101+sp:0x200]==initial[0x101+sp:0x200],('Every live incoming caller stack',mapper,char)
       def semantic(result):return[(t[2],t[4])for t in result['trace']if not(0x100<=t[3]<0x200)and t[2]not in [L['CurrentBank'],0x8001,0x5115]and not(char==11 and t[2]==L['RgDoubleJump'])]
       assert semantic(a)==semantic(b),('Every ordered nonstack original semantic/SMC/selector write',mapper,char,mode,force,flags)
       cycles[b['cycles']-a['cycles']]+=1
       rows.append(dict(character=char,mode=mode,force=force,P=flags,registers=True,all10240RAM=True,ordered_writes=True,individual_stack_relocations=changes,cycle_delta=b['cycles']-a['cycles']))
   report['maps'].append(dict(mapper=mapper,cases=rows,cycle_deltas=dict(cycles)))
   out.write_text(json.dumps(report,indent=2)+'\n')
  report['status']='PASS_COMPILED_SPRING_ABI_SOURCE_FLAG_AND_EXACT_WRITES'
 except Exception as exc:report.update(status='FAIL_RETAINED',error=str(exc));raise
 finally:out.write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(dict(status=report['status'],cases=sum(len(x['cases'])for x in report['maps']))))


if __name__=='__main__':main()
