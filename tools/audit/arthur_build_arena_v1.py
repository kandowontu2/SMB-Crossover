from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[2];O=ROOT/'build/arthur-source-v1';B=ROOT/'tools/Windows/cc65/bin'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    art=json.loads((O/'art-source.json').read_text());poses={r['pose']:r for r in art['records']}
    lines=['.segment "ARTHUR_ART"','.export ArArtLo,ArArtHi,ArAttrLo,ArAttrHi,ArOriginalPalette','ArArtLo:']
    for i in range(256):lines.append(f' .byte <ArArt{i if i in poses else 0}')
    lines.append('ArArtHi:')
    for i in range(256):lines.append(f' .byte >ArArt{i if i in poses else 0}')
    for k in('Lo','Hi'):
        lines.append('ArAttr'+k+':')
        lines +=[f' .byte {"<"if k=="Lo"else">"}ArAttr{k2 if k2 in(0,1,2,3,8)else 0}'for k2 in range(32)]
    rom=Path(art['original_ROM']).read_bytes();bank=rom[16+4*16384:16+5*16384]
    for key in(0,1,2,3,8):
        at=int.from_bytes(bank[0x1ae7+key*2:0x1ae9+key*2],'little')-0x8000
        lines+=['ArAttr'+str(key)+':',' .byte '+','.join(str(x)for x in bank[at:at+16])]
    for i,r in poses.items():
        values=[len(r['parts'])]
        for p in r['parts']:values +=[p['tile'],p['attribute'],p['x']&255,p['y']&255]
        lines+=['ArArt'+str(i)+':',' .byte '+','.join(str(x)for x in values)]
    lines+=['ArOriginalPalette:',' .byte '+','.join(str(x)for x in art['palette']['hardware_indices'])]
    (O/'arena-art.s').write_text('\n'.join(lines)+'\n')
    bg=bytearray(4096);bg[16:24]=bytes([255]*8) # plain technical floor, not character art
    (O/'arena.chr').write_bytes((O/'arthur-original-sprites.chr').read_bytes()+bg)
    commands=[]
    for name in('arena','arena-art'):
        args=[str(B/'ca65.exe'),'-g','-I',str(O),'-o',str(O/(name+'.o')),str(O/(name+'.s'))]
        commands.append(args);subprocess.run(args,cwd=ROOT,check=True)
    args=[str(B/'ld65.exe'),'-C',str(O/'arena.cfg'),'-o',str(O/'arena.nes'),'-Ln',str(O/'arena.lbl'),
          '--dbgfile',str(O/'arena.dbg'),'-m',str(O/'arena.map')]+[str(O/(n+'.o'))for n in('native-kernels','component','arena','arena-art')]
    commands.append(args);subprocess.run(args,cwd=ROOT,check=True)
    cpu=json.loads((O/'cpu-receipt.json').read_text());length=sum(cpu['capacity'][k]for k in('native_code_bytes','authored_leaf_bytes'))
    assert(O/'arena.nes').read_bytes()[16:16+length]==(O/'leaf.bin').read_bytes()[:length]
    deps=[Path(__file__),O/'arena.s',O/'arena.cfg',O/'arena-art.s',O/'arena.chr',O/'cpu-receipt.json',O/'art-source.json',O/'leaf.bin',O/'component.s',O/'native-kernels.s']
    p=O/'arena-build-proof.json';p.write_text(json.dumps(dict(status='ISOLATED_NATIVE_ARENA_SOURCE_BUILT',ROM_sha256=sha(O/'arena.nes'),
      exact_CPU_reviewed_leaf_prefix_bytes=length,commands=commands,bindings={str(q.resolve()):sha(q)for q in deps},
      fixture='Flat floor/source sprite renderer; Select cycles authentic pickup kinds6..10, Up+Select armor fixture. No progression admission or host leases.'),indent=2)+'\n')
    print(json.dumps(dict(ROM_sha256=sha(O/'arena.nes'),leaf_prefix_bytes=length,proof_sha256=sha(p))))
if __name__=='__main__':main()
