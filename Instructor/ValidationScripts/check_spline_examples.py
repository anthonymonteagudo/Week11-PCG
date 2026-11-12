import unreal as u,time,json,traceback,math,os
from pathlib import Path
R=Path(u.Paths.project_dir());O=Path(os.environ.get('WEEK11_SPLINE_CHECK_DIR',str(R/'Validation/SplineExamples/NodeReview')));O.mkdir(parents=True,exist_ok=True)
A=u.EditorAssetLibrary;E=u.get_editor_subsystem(u.EditorActorSubsystem);L=u.get_editor_subsystem(u.LevelEditorSubsystem);MP='/Game/Trail/Teaching/Maps/Spline_Examples';GP='/Game/Trail/Teaching/Graphs/PCG_SplineExamples'
assert L.load_level(MP);g=A.load_asset(GP);named={a.get_actor_label():a for a in E.get_all_level_actors()};actor=named['PCG_SplineExamples'];c=actor.get_component_by_class(u.PCGComponent);c.generate_local(True)
state={'phase':'wait','start':time.monotonic()};report={'map':MP,'graph':GP};helper=getattr(u,'TrailBiomeAuthoringLibrary',None)
u.EditorPythonScripting.set_keep_python_script_alive(True)
def finish(error=None):
 report.update(status='FAIL' if error else 'PASS',error=error,engine=u.SystemLibrary.get_engine_version(),private_helper_loaded=bool(helper));(O/'check.json').write_text(json.dumps(report,indent=2));u.unregister_slate_post_tick_callback(handle);u.EditorPythonScripting.set_keep_python_script_alive(False);u.SystemLibrary.quit_editor()
def inside(x,y,poly):
 yes=False;j=len(poly)-1
 for i in range(len(poly)):
  a,b=poly[i],poly[j]
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:yes=not yes
  j=i
 return yes
def tick(dt):
 try:
  if state['phase']=='wait':
   if c.get_editor_property('generation_in_progress') or time.monotonic()-state['start']<5:return
   spline=named['ClosedSpline_Input'].get_component_by_class(u.SplineComponent);assert spline.is_closed_loop();assert not named['OpenSpline_Input'].get_component_by_class(u.SplineComponent).is_closed_loop();poly=[(p.x,p.y)for p in [spline.get_location_at_spline_point(k,u.SplineCoordinateSpace.WORLD)for k in range(spline.get_number_of_spline_points())]]
   counts={};outside=[]
   for ism in actor.get_components_by_class(u.InstancedStaticMeshComponent):
    name=ism.static_mesh.get_name();counts[name]=counts.get(name,0)+ism.get_instance_count()
    if 'Juniper' in name:
     for k in range(ism.get_instance_count()):
      p=ism.get_instance_transform(k,True).translation
      if not inside(p.x,p.y,poly):outside.append([p.x,p.y])
   assert counts['SM_Wall_Pillar_400_01a']==10 and counts['SM_JuniperBush_01a']==38,counts;assert not outside,outside
   report.update(counts=counts,closed_spline_points=spline.get_number_of_spline_points(),roots_outside_closed_region=outside)
   reg=u.AssetRegistryHelpers.get_asset_registry();reg.search_all_assets(True);opts=u.AssetRegistryDependencyOptions(include_soft_package_references=True,include_hard_package_references=True,include_searchable_names=False,include_soft_management_references=False,include_hard_management_references=False);seen=set();todo=[MP]
   while todo:
    p=todo.pop()
    if p in seen or not p.startswith('/Game/'):continue
    seen.add(p);todo.extend(str(x)for x in reg.get_dependencies(p,opts))
   report['dependency_closure']=sorted(seen)
   if not helper:finish();return
   u.get_editor_subsystem(u.AssetEditorSubsystem).open_editor_for_assets([g]);helper.set_pcg_inspection_source(g,c);state.update(phase='focusClosed',start=time.monotonic());return
  if time.monotonic()-state['start']<2:return
  if state['phase']=='focusClosed':helper.focus_pcg_node_for_capture(g,'06 Scatter inside the region');state.update(phase='captureClosed',start=time.monotonic());return
  if state['phase']=='captureClosed':
   for panel in ['graph','details']:helper.capture_pcg_panel(g,panel,str(O/('Closed-'+panel+'.png')))
   helper.focus_pcg_node_for_capture(g,'02 Posts every 250 cm');state.update(phase='captureOpen',start=time.monotonic());return
  if state['phase']=='captureOpen':
   for panel in ['graph','details']:helper.capture_pcg_panel(g,panel,str(O/('Open-'+panel+'.png')))
   finish()
 except Exception:finish(traceback.format_exc())
handle=u.register_slate_post_tick_callback(tick)
