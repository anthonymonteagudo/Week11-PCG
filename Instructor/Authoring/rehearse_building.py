"""Reload, generate and inspect real native ISMs with the private bridge disabled."""
import unreal as u,json,traceback,math,time,hashlib
from pathlib import Path
R=Path(u.Paths.project_dir());O=R/'Validation/BuildingPass';B='/Game/Trail/Building';H=u.PCGGraphParametersHelpers;L=u.get_editor_subsystem(u.LevelEditorSubsystem);E=u.get_editor_subsystem(u.EditorActorSubsystem)
build=json.loads((O/'build.json').read_text());assert build['status']=='PASS';assert not hasattr(u,'TrailBiomeAuthoringLibrary'),'Validate without the private authoring bridge.'
assert L.load_level(B+'/Maps/Building_Examples');named={a.get_actor_label():a for a in E.get_all_level_actors()}
# Use only source assets already required by the portable Old West setup.
mat=u.load_asset(B+'/M_BuildingGround')
if not mat:
 mat=u.AssetToolsHelpers.get_asset_tools().create_asset('M_BuildingGround',B,u.Material,u.MaterialFactoryNew());M=u.MaterialEditingLibrary
 pos=M.create_material_expression(mat,u.MaterialExpressionWorldPosition,-800,0);mask=M.create_material_expression(mat,u.MaterialExpressionComponentMask,-600,0)
 for key,value in [('r',True),('g',True),('b',False),('a',False)]:mask.set_editor_property(key,value)
 M.connect_material_expressions(pos,'',mask,'Input')
 scale=M.create_material_expression(mat,u.MaterialExpressionMultiply,-400,0);scale.set_editor_property('const_b',1/900);M.connect_material_expressions(mask,'',scale,'A');sample=M.create_material_expression(mat,u.MaterialExpressionTextureSample,-200,0);sample.set_editor_property('texture',u.load_asset('/Game/Northwood/Textures/Landscape/TX_Grass_Mix_01a_ALB'));M.connect_material_expressions(scale,'',sample,'Coordinates');M.connect_material_property(sample,'RGB',u.MaterialProperty.MP_BASE_COLOR)
 rough=M.create_material_expression(mat,u.MaterialExpressionConstant,-200,300);rough.set_editor_property('r',.9);M.connect_material_property(rough,'',u.MaterialProperty.MP_ROUGHNESS);M.recompile_material(mat);u.EditorAssetLibrary.save_loaded_asset(mat)
named['Building demonstration ground'].static_mesh_component.set_material(0,mat)
for a in named.values():
 if a.get_actor_label().startswith('Building_'):a.set_actor_scale3d(u.Vector(1,1,1))
base=build['cases'];cases=[dict(c,case='saved') for c in base]+[dict(base[1],name='Lodge',case='repeat'),dict(base[1],name='Lodge',case='change_cells',cells=[5,2,3]),dict(base[1],name='Lodge',case='restore'),dict(base[1],name='Lodge',case='fractional_clamp',cells=[0,2.9,1]),dict(base[1],name='Lodge',case='restore_after_clamp')]
check_only=(O/'check-only').exists();state={'i':0,'phase':'start','time':time.monotonic(),'frames':0};results=[];captures=[] if check_only else ['Cabin','Lodge','Tower','Rotated'];u.EditorPythonScripting.set_keep_python_script_alive(True)
def finish(error=None):
 state['phase']='done'
 (O/'verification.json').write_text(json.dumps({'status':'FAIL' if error else 'PASS','error':error,'engine':u.SystemLibrary.get_engine_version(),'authoring_plugin_loaded':hasattr(u,'TrailBiomeAuthoringLibrary'),'cases':results,'limits':['Rectangular footprints only','Flat platform roof baseline','No interior circulation or habitable-building claim','Replacement kits need measured dimensions/pivots','Actor scale must remain one']},indent=2));u.unregister_slate_post_tick_callback(handle);u.EditorPythonScripting.set_keep_python_script_alive(False);u.SystemLibrary.quit_editor()
def inspect(a,case):
 counts={'walls':0,'floors_and_roof':0,'corners':0};points=[];r,c,f=[max(1,min(12,math.floor(q))) for q in case['cells']];frame=a.get_actor_transform();centres=set();wallz=[]
 for ism in a.get_components_by_class(u.InstancedStaticMeshComponent):
  m=ism.static_mesh
  if not m:continue
  stem=m.get_name();kind='corners' if 'Pillar' in stem else ('floors_and_roof' if 'Floor' in stem else 'walls')
  for k in range(ism.get_instance_count()):
   t=ism.get_instance_transform(k,True);v=frame.inverse_transform_location(t.translation);counts[kind]+=1;points.append([stem,*[round(getattr(v,d),3) for d in ['x','y','z']],*[round(getattr(t.rotation,d),5) for d in ['x','y','z','w']]])
   if kind=='walls':
    # Undo the authored wall start-pivot shift to recover its face centre.
    rot=t.rotation.rotator();localYaw=math.radians(rot.yaw-a.get_actor_rotation().yaw);x=v.x+200*math.sin(localYaw);y=v.y-200*math.cos(localYaw)
    assert abs(abs(x)-r*200)<.1 or abs(abs(y)-c*200)<.1,('Interior wall survived',case,x,y,r,c)
    key=tuple(round(q,2) for q in [x,y,v.z]);assert key not in centres,('Duplicate wall face',key);centres.add(key);wallz.append(v.z)
 expected={'walls':2*(r+c)*f,'floors_and_roof':r*c*(f+1),'corners':4*f};assert counts==expected,(case['name'],case['case'],counts,expected)
 assert {round(z,2) for z in wallz}=={350.*k for k in range(f)},('Wrong floor elevations',wallz)
 return {'counts':counts,'expected':expected,'effective_cells':[r,c,f],'actor_scale':str(a.get_actor_scale3d()),'signature':hashlib.sha256(json.dumps(sorted(points)).encode()).hexdigest(),'exterior_faces_only':True,'unique_wall_faces':len(centres),'floor_elevations_cm':sorted({round(z,2) for z in wallz})}
def tick(dt):
 try:
  state['frames']+=1
  if state['phase'] in ['saving','done']:return
  if state['phase']=='gallery':
   if state['frames']==20:u.AutomationLibrary.take_high_res_screenshot(1800,1100,str(O/'Gallery.png'),named['Building overview camera'])
   if state['frames']>55 and (O/'Gallery.png').exists():finish()
   assert time.monotonic()-state['time']<120,'Gallery capture timeout'
   return
  case=cases[state['i']];a=named['Building_'+case['name']];comp=a.get_component_by_class(u.PCGComponent)
  if state['phase']=='start':
   comp.regenerate_in_editor=False;comp.cleanup_local(True);H.set_vector_parameter(comp.graph_instance,'Cells',u.Vector(*case['cells']));comp.generate_local(True);state.update(phase='wait',time=time.monotonic(),frames=0);return
  if state['phase']=='wait':
   assert time.monotonic()-state['time']<100,'PCG building generation timeout'
   if state['frames']<90 or comp.get_editor_property('generation_in_progress'):return
   data=inspect(a,case)
   if case['case'] in ['repeat','restore','restore_after_clamp']:assert data['signature']==next(x['signature'] for x in results if x['name']=='Lodge' and x['case']=='saved'),'Restore or regeneration changed native output'
   results.append({'name':case['name'],'case':case['case'],**data});(O/'progress.json').write_text(json.dumps(results,indent=2));state.update(phase='next',frames=0)
   if case['case']=='saved' and case['name'] in captures:
    cam=named['Building overview camera'];p=a.get_actor_location();rr,cc,ff=data['effective_cells'];size=max(rr*400,cc*400,ff*350);cam.set_actor_location(p+u.Vector(-size*1.6,-size*1.75,size*1.25+500),False,False);cam.set_actor_rotation(u.Rotator(pitch=-25,yaw=48),False);u.EditorLevelLibrary.set_level_viewport_camera_info(cam.get_actor_location(),cam.get_actor_rotation());file=O/(case['name']+'.png')
    if file.exists():file.unlink()
    state.update(phase='warm',time=time.monotonic(),frames=0)
   return
  if state['phase']=='warm':
   if time.monotonic()-state['time']<5:return
   state.update(phase='capture',frames=0,time=time.monotonic());return
  if state['phase']=='capture':
   if state['frames']==1:u.AutomationLibrary.take_high_res_screenshot(1600,900,str(O/(case['name']+'.png')),named['Building overview camera'])
   if state['frames']<35 or not (O/(case['name']+'.png')).exists():
    assert time.monotonic()-state['time']<120,'Capture timeout'
    return
   state['phase']='next'
  if state['phase']=='next':
   state['i']+=1
   if state['i']==len(cases):
    if check_only:finish();return
    # Save generated native components so opening the example shows the baseline.
    state['phase']='saving';cam=named['Building overview camera'];cam.set_actor_location(u.Vector(-7600,-10500,7800),False,False);cam.set_actor_rotation(u.Rotator(pitch=-30,yaw=55),False)
    if (O/'Gallery.png').exists():(O/'Gallery.png').unlink()
    L.save_current_level();state.update(phase='gallery',frames=0,time=time.monotonic());return
   state.update(phase='start',frames=0)
 except Exception:finish(traceback.format_exc())
handle=u.register_slate_post_tick_callback(tick)
