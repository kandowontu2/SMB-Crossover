"""Retain S's negative; prepare exact cursor/audio layering and actual-size guard."""
from pathlib import Path
import ast,hashlib,json

ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    original=ROOT/'tools/audit/build_private49_menu_s.py'
    oldreport=json.loads((ROOT/'build/verification/root49-menu-options-private-s/report.json').read_text())
    assert sha(original)==oldreport['script_sha256']
    target=original.with_name('build_private49_menu_s2.py');assert not target.exists()
    code=original.read_text().replace('root49-menu-options-private-s','root49-menu-options-private-s2')
    marker="    contract=json.loads((MENU/'contract.json').read_text());parent=contract['parent_catalog']\n"
    assert code.count(marker)==1
    extra='''    source_paths={n:MENU/'source'/n for n in contract['changed']}
    CURSOR=ROOT/'build/verification/menu-options-title-cursor-b'
    AUDIO=ROOT/'build/verification/agent49-menu-stomp-audio-overlay-b'
    for folder,digest in [(CURSOR,'b3129d53146a6d4c0f2d462f1282f13fdc34be5c4dd3b4a8de4a815c4af8c534'),(AUDIO,'63fc7682d2879e3bcc0032a207b4b06055dd52167fd9fcee150a3d364c1950c5')]:
        assert sha(folder/'freeze.json')==digest
        for n,pin in json.loads((folder/'freeze.json').read_text())['files'].items():
            assert sha(folder/n)==pin['sha256']and (folder/n).stat().st_size==pin['bytes']
    cursor=json.loads((CURSOR/'contract.json').read_text())
    assert contract['changed'][cursor['source']]['after_sha256']==cursor['before_sha256']
    contract['changed'][cursor['source']]['after_sha256']=cursor['after_sha256']
    source_paths[cursor['source']]=CURSOR/'character_select.after.s'
    audio=json.loads((AUDIO/'contract.json').read_text())
    for n,r in audio['files'].items():
        assert n not in contract['changed']and parent[n]==r['before']['sha256']
        assert sha(Path(r['after']['path']))==r['after']['sha256']
        contract['changed'][n]=dict(before_sha256=r['before']['sha256'],after_sha256=r['after']['sha256'])
        source_paths[n]=Path(r['after']['path'])
    # Actual first-S DBG classifies exactly one backward JNE shortening by3B.
    # Keep that failure and A's original static claim; require the corrected
    # exact actual size on BOTH real links in this new candidate.
    resource=ROOT/'build/verification/menu-options-layout-c/report.json'
    assert sha(resource)=='ffba1c75db2013e670e2bbd8d61f78f5c57f1460c22f8a293cb5a2b2911f1b76'
    for mm,n in [('mmc3',2897),('mmc5',2907)]:
        assert contract['budgets'][mm]['new_char_select_static']==n+3
        contract['budgets'][mm]['new_char_select_static']=n
'''
    code=code.replace(marker,marker+extra)
    old="    for n in contract['changed']:(SOURCE/n).write_bytes((MENU/'source'/n).read_bytes())"
    assert code.count(old)==1
    code=code.replace(old,"    for n in contract['changed']:(SOURCE/n).write_bytes(source_paths[n].read_bytes())")
    marker="        base_build_sha256=sha(BASE/'report.json'),source410_hashes=expected,workspace_before=used,builds=[])"
    assert code.count(marker)==1
    code=code.replace(marker,"        base_build_sha256=sha(BASE/'report.json'),source410_hashes=expected,workspace_before=used,builds=[],\n        additional_overlays=dict(cursor_sha256=sha(CURSOR/'freeze.json'),audio_sha256=sha(AUDIO/'freeze.json')),\n        original_S_layout_negative_preserved=True,actual_resource_classification_sha256=sha(resource))")
    marker="            row['layout']=dict(old_RAM_addresses_exact=True"
    assert code.count(marker)==1
    extra="""            if mm=='mmc3':
                initial=(ROOT/'build/verification/root49-menu-options-private-s/source/build/smb-crossover-mmc3.nes').read_bytes()
                assert hashlib.sha256(initial).hexdigest()=='8a997a3fcd0e0acd118740f7a4431dd52623284fe284718a9bd266abb8716b91'
                diffs=[(x,y)for x,y in zip(initial,after.raw)if x!=y]
                assert sorted(diffs)==[(8,12),(8,12),(63,42)],diffs
"""
    code=code.replace(marker,extra+marker)
    code=code.replace('source-menu-options-s.zip','source-menu-options-s2.zip').replace('PASS_PRIVATE_MENU_S_BUILD_LAYOUT_ONLY','PASS_PRIVATE_MENU_S2_BUILD_LAYOUT_ONLY')
    ast.parse(code);target.write_text(code)
    print('Prepared',target,sha(target))

if __name__=='__main__':main()
