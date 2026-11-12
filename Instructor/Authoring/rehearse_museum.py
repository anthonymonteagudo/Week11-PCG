"""Native focused-station changes/restores and full-tool regression check."""
import unreal as u,json,time,traceback,hashlib,sys,math
ue=u
from pathlib import Path
R=Path(u.Paths.project_dir());O=R/'Validation/MuseumPass';O.mkdir(parents=True,exist_ok=True);H=u.PCGGraphParametersHelpers;L=u.get_editor_subsystem(u.LevelEditorSubsystem);E=u.get_editor_subsystem(u.EditorActorSubsystem);sys.path.insert(0,str(R/'Tools'));sys.path.insert(0,str(R/'Content/Python'));import museum
config=json.loads((O/'build.json').read_text());assert config['status']=='PASS';assert not hasattr(u,'TrailBiomeAuthoringLibrary');assert L.load_level(config['map']);named={a.get_actor_label():a for a in E.get_all_level_actors()};cases=[(s['id'],c) for s in config['stations'] for c in ['baseline','change','restore']];state={'i':0,'phase':'start','frames':0,'time':time.monotonic()};results=[];bases={};u.EditorPythonScripting.set_keep_python_script_alive(True)
if (O/'recheck-trail-only').exists():results=json.loads((O/'progress.json').read_text());assert len(results)==21;state['i']=len(cases)
def signature(st):
 rows=[];counts={};local=[]
 for label in st['actors']:
  a=named[label];count=0
  for ism in a.get_components_by_class(u.InstancedStaticMeshComponent):
   m=ism.get_editor_property('static_mesh')
   for k in range(ism.get_instance_count()):
    t=ism.get_instance_transform(k,True);v=t.translation;s=t.scale3d;q=t.rotation;rows.append([label,m.get_path_name(),*[round(getattr(v,d),4) for d in ['x','y','z']],*[round(getattr(s,d),4) for d in ['x','y','z']],*[round(getattr(q,d),6) for d in ['x','y','z','w']]]);local.append([label,m.get_name(),v.x-a.get_actor_location().x,v.y-a.get_actor_location().y,v.z-a.get_actor_location().z]);count+=1
  counts[label]=count
 return {'count':len(rows),'actors':counts,'signature':hashlib.sha256(json.dumps(sorted(rows)).encode()).hexdigest(),'points':local}
def comp(label):return named[label].get_component_by_class(u.PCGComponent)
def graph(st):
 g=comp(st['actors'][0]).graph_instance
 while isinstance(g,u.PCGGraphInstance):g=g.get_editor_property('graph')
 return g
def settings(st,title):return next(n.get_settings() for n in graph(st).nodes if str(n.node_title)==title)
def apply(st,change):
 number=st['id']
 if number==1:settings(st,'01 Candidate grid').set_editor_property('cell_size',u.Vector(600,600,100) if change else u.Vector(300,300,100))
 elif number==2:settings(st,'02 Seeded transform variation').set_editor_property('seed',43 if change else 0)
 elif number==3:named[st['input_actor']].set_actor_location(u.Vector(*st['centre'])+(u.Vector(500,0,0) if change else u.Vector()),False,False)
 elif number==4:settings(st,'05 Accept flatter ground').set_editor_property('lower_bound',.995 if change else .975)
 elif number==5:H.set_object_parameter(comp(st['actors'][0]).graph_instance,'AssetSet',u.load_asset('/Game/Trail/Biome/AssetSets/DT_'+('ScrubMixed' if change else 'TreesMixed')))
 elif number==6:
  s=settings(st,'02 Competition neighborhood');radius=300 if change else 140;s.set_editor_property('bounds_min',u.Vector(-radius,-radius,-radius));s.set_editor_property('bounds_max',u.Vector(radius,radius,radius))
 elif number==7:H.set_vector_parameter(comp(st['actors'][0]).graph_instance,'Cells',u.Vector(2,2,3 if change else 2))
def finish(error=None):
 state['phase']='done';report={'status':'FAIL' if error else 'PASS','error':error,'engine':u.SystemLibrary.get_engine_version(),'authoring_plugin_loaded':hasattr(u,'TrailBiomeAuthoringLibrary'),'cases':results,'trail_regression':state.get('trail_regression'),'limits':['Editor demonstration; gameplay navigation is not validated','Point bounds are not full mesh collision','Houdini is a separate optional showcase']};(O/'verification.json').write_text(json.dumps(report,indent=2));u.unregister_slate_post_tick_callback(handle);u.EditorPythonScripting.set_keep_python_script_alive(False);u.SystemLibrary.quit_editor()
def nextcase():state.update(i=state['i']+1,phase='start',frames=0,time=time.monotonic())
def tick(dt):
 global named
 try:
  if state['phase'] in ['done','saving','loading']:return
  state['frames']+=1
  if state['phase']=='trail_load':
   state['phase']='loading';assert L.load_level('/Game/Trail/Maps/Trail_Student');named={a.get_actor_label():a for a in E.get_all_level_actors()}
   for n in ['Trees','Rocks','Scrub']:comp('PCG_'+n).cleanup_local(True);comp('PCG_'+n).generate_local(True)
   state.update(phase='trail_wait',frames=0,time=time.monotonic());return
  if state['phase']=='trail_wait':
   if state['frames']<120 or any(comp('PCG_'+n).get_editor_property('generation_in_progress') for n in ['Trees','Rocks','Scrub']):return
   global components,samples,H
   components={n:comp('PCG_'+n) for n in ['Trees','Rocks','Scrub']};from field_model import center
   samples=[(x,center(x)) for x in range(-11000,11001,50)];src=(R/'Tools/rehearse_biomes.py').read_text();exec(src[src.index('def distance'):src.index('def finish')],globals());data={n:inspect(n) for n in components};old=next(c for c in json.loads((R/'Validation/CompositionPass/report.json').read_text())['cases'] if c['region']=='Student' and c['case']=='baseline')['layers'];assert all(data[n]['signature']==old[n]['signature'] for n in components),'Graph cleanup changed the full trail result';state['trail_regression']={'status':'PASS','layers':data};finish();return
  if state['i']==len(cases):
   state['phase']='saving';museum.show_all()
   for st in config['stations']:u.EditorAssetLibrary.save_loaded_asset(graph(st),False)
   L.save_current_level();state.update(phase='trail_load',frames=0);return
  number,case=cases[state['i']];st=config['stations'][number-1]
  if state['phase']=='start':
   apply(st,case=='change')
   for label in st['actors']:c=comp(label);c.regenerate_in_editor=False;c.cleanup_local(True);c.generate_local(True)
   state.update(phase='wait',frames=0,time=time.monotonic());return
  if state['phase']=='wait':
   assert time.monotonic()-state['time']<90,'Station generation timeout'
   if state['frames']<100 or any(comp(a).get_editor_property('generation_in_progress') for a in st['actors']):return
   data=signature(st);base=bases.get(number)
   if case=='baseline':
    assert data['count']>0,('Empty station',number)
    if number in [1,2]:assert data['count']==12,(number,data['count'])
    if number==3:assert data['count']<12
    if number==4:assert data['count']<70
    if number==5:assert len(set(data['actors'].values()))==1
    if number==6:
     before=sum(p[2]>0 for p in data['points']);after=sum(p[2]<0 for p in data['points']);assert 0<after<before,(before,after);data['before_after']=[before,after]
    if number==7:assert data['count']==36
    bases[number]=data
   elif case=='restore':assert data['signature']==base['signature'],('Restore changed baseline',number)
   else:
    assert data['signature']!=base['signature'],('Control did not affect station',number)
    if number in [1,4,6]:assert data['count']<base['count']
    if number in [2,5]:assert data['count']==base['count']
    if number==7:assert data['count']==52
   results.append({'station':number,'case':case,**{k:v for k,v in data.items() if k!='points'}});(O/'progress.json').write_text(json.dumps(results,indent=2))
   if case=='restore':
    museum.focus(number);E.set_selected_level_actors([]);file=O/f'M{number:02d}.png'
    if file.exists():file.unlink()
    state.update(phase='warm',frames=0,time=time.monotonic());return
   nextcase();return
  if state['phase']=='warm':
   if time.monotonic()-state['time']<4:return
   state.update(phase='capture',frames=0,time=time.monotonic());return
  if state['phase']=='capture':
   file=O/f'M{number:02d}.png'
   if state['frames']==1:u.AutomationLibrary.take_high_res_screenshot(1600,900,str(file),named[st['camera']])
   if state['frames']<35 or not file.exists():assert time.monotonic()-state['time']<90,'Capture timeout';return
   nextcase()
 except Exception:finish(traceback.format_exc())
handle=u.register_slate_post_tick_callback(tick)
