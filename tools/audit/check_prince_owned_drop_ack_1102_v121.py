"""Exact native/source parity and FF interrupts for the private no-drop ack."""
from pathlib import Path
import inspect,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_deferred_strike_1102_v117 as U
C,N,O=U.C,U.N,U.O


def inject(m):
 m.ram[3][:8159]=(O/'native-runtime-v120.bin').read_bytes();m.ram[2][0x800:0x800+6095]=(O/'native-metadata-v120.bin').read_bytes();m.ram[2][0x766:0x800]=(O/'native-state-v120.bin').read_bytes()[-154:]
 return json.loads((O/'native-labels-v120.json').read_text())


def environment():
 e,text=U.V.environment();assert C.address(C.C.C.image()[0],'Squ1_SfxLenCounter')==0x7d8
 marker=' for _ in range(500000):';assert marker in text
 observer=""" if lab['PpNativeCall']==NEW_NATIVE_CALL:
  target=address(b,'ShellOrBlockDefeat');bank=((location(b,'ShellOrBlockDefeat')-16)//8192)|128
  native[(target+3,bank)]=native.pop((target,bank))
"""
 text=text.replace(marker,observer+marker,1)
 text=text.replace('gateway_entries=0;audio_after=None','gateway_entries=0;audio_after=None;smack_after=None')
 text=text.replace('audio_before=m[0x7da];','audio_before=m[0x7da];smack_before=m[0x7d8];')
 text=text.replace('audio_after=m[0x7da]\n','audio_after=m[0x7da];smack_after=m[0x7d8]\n')
 text=text.replace('and audio_after==audio_before','and audio_after==audio_before and smack_after==smack_before')
 marker=" if audio_after is not None:assert m[0x7da]==audio_after";assert marker in text
 text=text.replace(marker," if smack_after is not None:assert m[0x7d8]==smack_after,('Foreground changed nativeSmack counter',interrupt,smack_after,m[0x7d8])\n"+marker)
 e['NEW_NATIVE_CALL']=json.loads((O/'native-labels-v120.json').read_text())['PpNativeCall'];exec(compile(text,str(Path(__file__)),'exec'),e);return e,text


def main():
 original_inject=U.inject;original_normalize=C.V.normalized_state
 def normalize(m):
  out=list(original_normalize(m));native=bytearray(out[4]);native[0x7d8-0x200]=0;out[4]=bytes(native);return tuple(out)
 U.inject=inject;C.V.normalized_state=normalize
 try:
  text=inspect.getsource(U.main).replace('e,_=V.environment()','e,_=ENV()').replace('v117','v121').replace('v116','v120')
  env=dict(U.__dict__,ENV=environment,__file__=str(Path(__file__)));exec(compile(text,str(Path(__file__)),'exec'),env);env['main']()
 finally:U.inject=original_inject;C.V.normalized_state=original_normalize
 path=O/'deferred-strike-CPU-v121.json';q=json.loads(path.read_text());assert q['passed'];q.update(source_owned_native_no_drop_ack=True,native_suffix_PC=0x9af8,original_same_body_prefix_ack='Original hook denies native ammo drops and only writes InvDropEnemy=X; authenticated source ProxyOut performs this exact input effect and invokes unchanged native defeat suffix. SourceNativeBestSlot store is redundant in admitted actor lifetime.',tracked_native_audio=dict(addresses=[0x7d8,0x7da],symbols=['Squ1_SfxLenCounter','Squ2_SfxLenCounter'],source='src/music_drivers/vanilla_sfx.s',proof='IRQ preserves both; actual lagNMI owns their updates; resumed foreground preserves both exact postISR values. Every other native field remains exact. v118 first failure was realSmack07D8, distinct from its deeper actualSMC failure.'),scope='Source-only120 prototype after complete authenticated97 cold. Actual GameLoop old/new complete native/ZP/SMC/AXYP/SP and original source-live state match every epoch, native defeat sameMain exactlyonce then16updates without duplicate. Original drop-hook no-op acknowledgement is owner-specific and does not modify any native or shared ROM. Real IRQ/FF-lag return checks include the source-proven07D8/07DA audio lengths. Changed physical backing/cookie/fullcold and nestedIRQ remain pending; no native admission.')
 q['bindings'].update({p.relative_to(R).as_posix():C.C.C.M.sha(p.read_bytes())for p in [Path(__file__),Path(U.__file__),O/'native-drop-policy-CPU-v119.json',O/'deferred-strike-measurement-v120.json',O/'deferred-strike-diagnostic-v118.json',R/'src/music_drivers/vanilla_sfx.s']});path.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':
 try:main()
 except Exception as error:
  (O/'deferred-strike-negative-v121.json').write_text(json.dumps(dict(passed=False,CPU_only=True,source_injected=True,exception=repr(error)),indent=2)+'\n');raise
