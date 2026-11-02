"""Fund complete-cookie unrolling by removing dead Arthur policy scratch work."""
from pathlib import Path
import hashlib,json,re,subprocess,zipfile
from prepare_selected_native_packet_v1 import R,sha
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from private_build_outputs_v1 import validate
O=R/'build/arthur-auth-fast-1101-v2'
BASE=R/'build/metal-storm-idle-shots-1101-v41/candidate.nes'

def main():
 O.mkdir(exist_ok=True);b=scoped_load(BASE);raw=bytearray(b['raw'])
 with zipfile.ZipFile(R/'build/_recovery/legacy-sources-2026-10-31.zip') as z:
  ix={q['path']:q for q in json.loads(z.read('index.json'))}
  q=ix['arthur-physical-clock-v2/joint/arthur/own-services.s']
  original=z.read('objects/'+q['sha256']).decode()
 names=[]
 for line in original.splitlines():
  if line.startswith('.import'):names.extend(line.split(None,1)[1].split(','))
 pre='\n'.join(f'{n}=${address(b,n):04x}' for n in sorted(set(names)))+'\n'
 t='\n'.join(line for line in original.splitlines() if not line.startswith('.import'))
 for n in re.findall(r'\.bank\((\w+)\)',t):t=t.replace(f'.bank({n})',str((location(b,n)-16)//8192))
 for op in ['lda','sta']:
  for n in ['R0','R1']:t=t.replace(f' {op} {n}\n',f' {op} a:{n}\n')
 cc=R/'tools/Windows/cc65/bin'
 cfg='MEMORY{M:start=$bd00,size=$300,file=%O;}SEGMENTS{ARTHUR_OWN_SERVICES:load=M,type=ro;}'
 (O/'own.cfg').write_text(cfg)
 def assemble(name,source,cfgname='own.cfg'):
  (O/(name+'.s')).write_text(source)
  for cmd in [[cc/'ca65.exe','-g',O/(name+'.s'),'-o',O/(name+'.o')],[cc/'ld65.exe','-C',O/cfgname,O/(name+'.o'),'-o',O/(name+'.bin'),'-Ln',O/(name+'.lbl')]]:
   cmd=list(map(str,cmd));validate(cmd,O,cwd=R);r=subprocess.run(cmd,capture_output=True,text=True);assert r.returncode==0,r.stderr
  return (O/(name+'.bin')).read_bytes()
 old=assemble('old-own',pre+t);at=16+70*8192+0x1d00
 assert old==raw[at:at+len(old)] and len(old)==768,'Exact current owning source required'
 # Each policy immediately overwrites both temporary fields in its common
 # return; none reads these incoming copies. No ISR consumes these fields.
 assert t.count('\n ArMergePolicyInput\n')==6
 t=t.replace('\n ArMergePolicyInput\n','\n')
 # These stores write each zero-page byte back unchanged, with no intervening
 # consumer. Preserve final bytes; do not claim intermediate write equality.
 dead=' lda a:R1\n sta a:R1\n lda a:R0\n sta a:R0\n';assert t.count(dead)==1;t=t.replace(dead,'')
 common=' lda #.lobyte(26|$80)\n sta NextBank_SMC+1\n jmp NextBank_SMC'
 assert t.count(common)==2
 first=t.index(common);t=t[:first]+'ArFastTailBank:\n'+t[first:]
 second=t.index(common,t.index(common)+len(common));t=t[:second]+' jmp ArFastTailBank'+t[second+len(common):]
 count=0
 for n in ['ArHostBodyPolicy','ArHostAdder','ArHostUi']:
  assert address(b,n)>>8==0xdf
  s=f' lda #>{n}\n sta ArDrawPtr+1\n lda SafecallA_SMC+1\n'
  assert t.count(s)==1;t=t.replace(s,' jsr ArFastPolicyHigh\n');count+=1
 s='ArMergePolicyReturn:\n sta ArTemp\n';assert t.count(s)==1
 t=t.replace(s,s+' sta SafereturnA_SMC+1\n')
 s=' lda ArTemp\n sta SafereturnA_SMC+1\n';assert t.count(s)==1;t=t.replace(s,'')
 s=' lda ArTempHi\n pha\n lda ArTemp\n plp\n ora #0\n';assert t.count(s)==1
 t=t.replace(s,' lda ArTempHi\n pha\n plp\n lda ArTemp\n')
 helper='ArFastPolicyHigh:\n lda #$df\n sta ArDrawPtr+1\n lda SafecallA_SMC+1\n rts\nArFastSpaceBegin:\n'
 marker='ArOwnMenuName:\n';assert t.count(marker)==1
 target=address(b,'ArOwnMenuName')
 t=t.replace(marker,helper+f' .res ${target-0xbd00:04x}-(*-ArOwnServices),$ff\n'+marker)
 new=assemble('new-own',pre+t)
 labs={n:int(a,16) for a,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',(O/'new-own.lbl').read_text(),re.M)}
 space=labs['ArFastSpaceBegin'];available=target-space
 assert available>=105,(space,target,available)
 # The old externally referenced clock/menu entry PCs remain fixed.
 for n in ['ArOwnServices','ArOwnUnavailable','ArOwnMenuName','ArHostNmiClock','ArClockPollC70','ArOwnComponentEnd']:
  assert labs[n]==address(b,n),(n,labs[n],address(b,n))
 raw[at:at+768]=new
 signature=bytes(raw[location(b,'ArCacheSignature'):location(b,'ArCacheSignature')+16])
 # Foreground mapping/save/restore stays at the same public entry. The
 # unrolled body never changes Y, so its old Y stack pair is unnecessary.
 start=address(b,'ArGenCheckForeground')+48 # C7B9, ordinary Cookie entry
 assert start==0xc7b9
 restore=start+30 # computed below from the assembled label, never guessed
 main=' .segment "P"\n lda CurrentBank\n pha\n lda #2\n sta CurrentBank\n sta $5115\n'
 for i in [15,14]:main+=f' lda ${0xbfe0+i:04x}\n cmp #${signature[i]:02x}\n bne Invalid\n'
 main+=f' jmp ${space+0x2000:04x}\nInvalid:clc\nRestore:pla\n sta CurrentBank\n sta $5115\n pla\n rts\n'
 (O/'auth.cfg').write_text(f'MEMORY{{M:start=${start:04x},size=$2a,file=%O,fill=yes,fillval=$ea;}}SEGMENTS{{P:load=M,type=ro;}}')
 auth=assemble('auth',f'CurrentBank=${address(b,"CurrentBank"):04x}\n'+main,'auth.cfg')
 al={n:int(a,16) for a,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',(O/'auth.lbl').read_text(),re.M)}
 body='.segment "P"\n'
 for i in range(13,-1,-1):body+=f' lda ${0xbfe0+i:04x}\n cmp #${signature[i]:02x}\n bne Invalid\n'
 body+=f' jmp ${al["Restore"]:04x}\nInvalid:clc\n jmp ${al["Restore"]:04x}\n'
 (O/'body.cfg').write_text(f'MEMORY{{M:start=${space+0x2000:04x},size={available},file=%O;}}SEGMENTS{{P:load=M,type=ro;}}')
 fast=assemble('auth-body',body,'body.cfg');assert len(fast)==105
 raw[16+70*8192+space-0xa000:16+70*8192+space-0xa000+len(fast)]=fast
 off=16+70*8192+start-0xc000;raw[off:off+len(auth)]=auth
 (O/'candidate.nes').write_bytes(raw)
 for ext in ['.lbl','.dbg']:(O/('candidate'+ext)).write_bytes(BASE.with_suffix(ext).read_bytes())
 result=dict(assembled=True,installed=False,ROM_sha256=sha(O/'candidate.nes'),base_sha256=sha(BASE),funded_bytes=available,helper_bytes=len(fast),helper_C_address=space+0x2000,auth_restore=al['Restore'],owner_source_sha256=q['sha256'],cookie=signature.hex(),scope='All16 cookie bytes still checked before cache execution; own-service final state preserved, dead scratch/self-writes removed. CPU and native verification pending.')
 (O/'assembly.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
