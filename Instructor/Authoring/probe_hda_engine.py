"""Test the Unreal-side Engine route in an isolated optional project.
API reference: SideFX Houdini Engine Public API and its bundled ramp example.
No Houdini authoring or conversion of noncommercial assets is attempted.
"""
import unreal as u,json,time,traceback
from pathlib import Path
R=Path(u.Paths.project_dir());O=R/'Validation';O.mkdir(exist_ok=True);state={'phase':'session','start':time.monotonic()};result={'engine':u.SystemLibrary.get_engine_version(),'test':'Unreal plug-in Engine session and official commercial .hda example','houdini_authoring_test':False};wrapper=None
u.EditorPythonScripting.set_keep_python_script_alive(True)
def finish(status,error=None):
 state['phase']='done';result.update(status=status,error=error);(O/'engine-test.json').write_text(json.dumps(result,indent=2));u.unregister_slate_post_tick_callback(handle);u.EditorPythonScripting.set_keep_python_script_alive(False);u.SystemLibrary.quit_editor()
def post_cook(w,success):result['cook_reported_success']=bool(success)
def processed(w):
 result['outputs']=w.get_num_outputs();result['parameters']=list(w.get_parameter_tuples().keys());finish('COOKED' if result['outputs']>0 else 'EMPTY_OUTPUT')
def tick(dt):
 global wrapper
 if state['phase']=='done':return
 try:
  if state['phase']=='session':
   state['phase']='starting';api.create_session();state.update(phase='wait_session',start=time.monotonic());return
  if state['phase']=='wait_session':
   if api.is_session_valid():
    result['session_valid']=True;asset=u.load_asset('/HoudiniEngine/Examples/hda/ramp_example_1_0');assert asset,'Installed HDA example not found';result['asset']=asset.get_path_name();wrapper=api.instantiate_asset(asset,u.Transform());assert wrapper,'HDA instantiation did not return a wrapper';wrapper.on_post_cook_delegate.add_callable(post_cook);wrapper.on_post_processing_delegate.add_callable(processed);state.update(phase='cook',start=time.monotonic());return
   if time.monotonic()-state['start']>30:result['session_valid']=False;finish('SESSION_UNAVAILABLE',api.get_last_error_message())
  elif state['phase']=='cook' and time.monotonic()-state['start']>90:finish('COOK_TIMEOUT',wrapper.get_last_error_message())
 except Exception:finish('FAILED',traceback.format_exc())
api=u.HoudiniPublicAPIBlueprintLib.get_api();handle=u.register_slate_post_tick_callback(tick)
