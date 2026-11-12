"""Exercise actual supplied controls and asynchronous museum navigation; never save changes."""
import unreal as u,json,time,traceback,hashlib,os
from pathlib import Path
R=Path(u.Paths.project_dir());O=Path(os.environ['WEEK11_VALIDATION_DIR']);O.mkdir(parents=True,exist_ok=True)
L=u.get_editor_subsystem(u.LevelEditorSubsystem);E=u.get_editor_subsystem(u.EditorActorSubsystem);H=u.PCGGraphParametersHelpers
import museum
assert not hasattr(u,'TrailBiomeAuthoringLibrary')
state={'phase':'start','start':time.monotonic()};rows=[]
u.EditorPythonScripting.set_keep_python_script_alive(True)
def outputs():
 result={}
 for a in E.get_all_level_actors():
  c=a.get_component_by_class(u.PCGComponent)
  if not c:continue
  if c.get_editor_property('generation_in_progress'):return None
  data=[]
  for ism in a.get_components_by_class(u.InstancedStaticMeshComponent):
   for i in range(ism.get_instance_count()):
    t=ism.get_instance_transform(i,True)
    data.append([ism.static_mesh.get_path_name(),str(t.translation),str(t.rotation),str(t.scale3d)])
  result[a.get_actor_label()]={'count':len(data),'signature':hashlib.sha256(json.dumps(sorted(data)).encode()).hexdigest()}
 return result
def finish(error=None):
 state['phase']='done';(O/'lesson-actions.json').write_text(json.dumps({'status':'FAIL' if error else 'PASS','error':error,'checks':rows,'maps_saved':False,'engine':u.SystemLibrary.get_engine_version()},indent=2))
 u.unregister_slate_post_tick_callback(handle);u.EditorPythonScripting.set_keep_python_script_alive(False)
 if not error and os.environ.get('WEEK11_THEN_CAPTURE'):
  script=Path(os.environ['WEEK11_THEN_CAPTURE']);exec(compile(script.read_text(),str(script),'exec'),{'__name__':'__main__'});return
 u.SystemLibrary.quit_editor()
def tick(dt):
 try:
  phase=state['phase']
  if phase=='done':return
  if time.monotonic()-state['start']>240:raise TimeoutError(phase)
  if phase=='start':
   assert L.load_level('/Game/Trail/Maps/Trail_Student');museum.focus(3);state.update(phase='navigation',start=time.monotonic());return
  if time.monotonic()-state['start']<9:return
  data=outputs()
  if data is None:return
  if phase=='baseline':
   assert {k:v['count'] for k,v in data.items()}=={'PCG_Trees':202,'PCG_Rocks':23,'PCG_Scrub':412},data
   state['baseline']=data
   actor=next(a for a in E.get_all_level_actors() if a.get_actor_label()=='PCG_Scrub');c=actor.get_component_by_class(u.PCGComponent);state['scrub']=c
   assert H.get_int32_parameter(c.graph_instance,'VariationSeed')==41
   H.set_double_parameter(c.graph_instance,'KeepFraction',.5);c.generate_local(True);state.update(phase='changed',start=time.monotonic());return
  if phase=='changed':
   assert data['PCG_Scrub']['count']==268,data
   assert all(data[k]==state['baseline'][k] for k in ['PCG_Trees','PCG_Rocks'])
   rows.append({'test':'Scrub KeepFraction .78 to .50','before':412,'after':268,'other_layers_identical':True})
   H.set_double_parameter(state['scrub'].graph_instance,'KeepFraction',.78);state['scrub'].generate_local(True);state.update(phase='restored',start=time.monotonic());return
  if phase=='restored':
   assert data==state['baseline'],'Restore changed native instance transforms'
   rows.append({'test':'Restore original scrub result','exact_instance_signature_match':True})
   finish();return
  if phase=='navigation':
   selected=E.get_selected_level_actors();assert selected and all(a.get_actor_label().startswith('M03_') for a in selected),[a.get_actor_label() for a in selected]
   assert sum(v['count'] for k,v in data.items() if k.startswith('M03_'))==6
   rows.append({'test':'Enter museum from trail, request station 3, wait for ready callback','selected_station':3,'count':6})
   museum.show_all();state.update(phase='all',start=time.monotonic());return
  if phase=='all':
   assert all(not a.is_hidden_ed() for a in E.get_all_level_actors() if a.get_actor_label().startswith('M03_PCG'))
   rows.append({'test':'Show all after focus','PASS':True})
   assert L.load_level('/Game/Trail/Maps/Trail_Student');state.update(phase='baseline',start=time.monotonic())
 except Exception:finish(traceback.format_exc())
handle=u.register_slate_post_tick_callback(tick)
