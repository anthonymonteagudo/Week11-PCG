"""Seven focused PCG bays; six core concepts followed by one optional assembly."""
import unreal as u,json,traceback
from pathlib import Path
R=Path(u.Paths.project_dir());O=R/'Validation/MuseumPass';O.mkdir(parents=True,exist_ok=True);B='/Game/Trail/Museum';A=u.EditorAssetLibrary;T=u.AssetToolsHelpers.get_asset_tools();E=u.get_editor_subsystem(u.EditorActorSubsystem);L=u.get_editor_subsystem(u.LevelEditorSubsystem);H=u.PCGGraphParametersHelpers
stations=[
 {'id':1,'title':'Candidates','question':'Where do points come from?','change':'Change grid cell size.','expected':'Candidate count changes before meshes.','centre':[0,0,0]},
 {'id':2,'title':'Transform variation','question':'What can vary without adding points?','change':'Change the Transform Points seed.','expected':'Count stays fixed; transforms change.','centre':[3200,0,0]},
 {'id':3,'title':'Closed spline exclusion','question':'Which side of a boundary survives?','change':'Move the closed exclusion spline.','expected':'Difference removes points inside it.','centre':[6400,0,0]},
 {'id':4,'title':'Projection and suitability','question':'How do points respond to a surface?','change':'Raise the minimum normal dot product.','expected':'Ground contact remains; steeper points disappear.','centre':[0,3600,0]},
 {'id':5,'title':'Shared rules, asset profiles','question':'Can one graph produce two populations?','change':'Swap a graph instance AssetSet.','expected':'Meshes change while placement stays shared.','centre':[3200,3600,0]},
 {'id':6,'title':'Bounds and overlap','question':'Which nearby candidates compete?','change':'Change the shared point influence bounds.','expected':'Pruning changes the accepted subset.','centre':[6400,3600,0]},
 {'id':7,'title':'Building dependencies','question':'Which parts follow the floor count?','change':'Change Cells Z on the building instance.','expected':'Walls and corner posts repeat; the roof follows.','centre':[3200,7200,0],'optional':True}]
try:
 if A.does_asset_exist(B+'/Maps/PCG_Museum'):
  assert json.loads((O/'build.json').read_text())['status']=='FAIL','Museum exists; refine it instead of rebuilding.'
  assert L.load_level(B+'/Maps/PCG_Museum');assert not any(a.get_actor_label().startswith('M01_') for a in E.get_all_level_actors()),'Populated map must be refined, not rebuilt.'
 else:assert L.new_level(B+'/Maps/PCG_Museum')
 def spawn(cls,label,xyz,rotation=None):
  a=E.spawn_actor_from_class(cls,u.Vector(*xyz),rotation or u.Rotator());a.set_actor_label(label);a.set_actor_scale3d(u.Vector(1,1,1));return a
 def material(name,color):
  m=A.load_asset(B+'/Materials/'+name)
  if m:return m
  m=T.create_asset(name,B+'/Materials',u.Material,u.MaterialFactoryNew());v=u.MaterialEditingLibrary.create_material_expression(m,u.MaterialExpressionConstant3Vector,-200,0);v.set_editor_property('constant',u.LinearColor(*color,1));u.MaterialEditingLibrary.connect_material_property(v,'',u.MaterialProperty.MP_BASE_COLOR);u.MaterialEditingLibrary.recompile_material(m);A.save_loaded_asset(m);return m
 slate=material('M_MuseumSlate',(.075,.095,.11));board=material('M_MuseumBoard',(.015,.045,.06));marker=material('M_MuseumMarker',(.05,.7,.55))
 def static(label,xyz,scale,mesh,mat):
  a=spawn(u.StaticMeshActor,label,xyz);a.static_mesh_component.set_static_mesh(A.load_asset(mesh));a.set_actor_scale3d(u.Vector(*scale));a.static_mesh_component.set_material(0,mat);return a
 def text(label,message,xyz,size):
  a=spawn(u.TextRenderActor,label,xyz,u.Rotator(yaw=-90));c=a.get_component_by_class(u.TextRenderComponent);c.set_text(message);c.set_world_size(size);c.set_text_render_color(u.Color(220,245,240,255));return a
 def graph(name,description):
  if A.does_asset_exist(B+'/Graphs/'+name):
   old=A.load_asset(B+'/Graphs/'+name);assert str(old.description)==description;assert json.loads((O/'build.json').read_text())['status']=='FAIL';assert A.delete_asset(B+'/Graphs/'+name)
  g=T.create_asset(name,B+'/Graphs',u.PCGGraph,u.PCGGraphFactory());g.set_editor_property('description',description);return g
 def node(g,cls,title,x,y,comment='',**kw):
  n,s=g.add_node_of_type(cls);n.set_editor_property('node_title',title);n.set_node_position(x,y)
  if comment:u.TrailBiomeAuthoringLibrary.comment_node(n,comment)
  for k,v in kw.items():s.set_editor_property(k,v)
  return n,s
 def pins(n,d='input_pins'):return [str(p.properties.label) for p in n.get_editor_property(d)]
 def wire(g,a,b,ap='Out',bp='In'):assert ap in pins(a,'output_pins') and bp in pins(b),(a.node_title,b.node_title,ap,bp,pins(b));g.add_edge(a,ap,b,bp)
 def grid(g,title='01 Candidate grid',ext=(600,450,0),cell=300):return node(g,u.PCGCreatePointsGridSettings,title,-900,0,comment='Grid spacing proposes candidates. Point count is inspected before choosing a mesh.',grid_extents=u.Vector(*ext),cell_size=u.Vector(cell,cell,100),coordinate_space=u.PCGCoordinateSpace.LOCAL_COMPONENT,set_points_bounds=False,point_steepness=1.,cull_points_outside_volume=False)[0]
 def xf(g,src,title,x,y,offset=(0,0,25),scale=.3,jitter=0,yaw=0):
  n,s=node(g,u.PCGTransformPointsSettings,title,x,y,offset_min=u.Vector(offset[0]-jitter,offset[1]-jitter,offset[2]),offset_max=u.Vector(offset[0]+jitter,offset[1]+jitter,offset[2]),scale_min=u.Vector(scale,scale,scale),scale_max=u.Vector(scale,scale,scale),rotation_min=u.Rotator(),rotation_max=u.Rotator(yaw=yaw));wire(g,src,n);return n,s
 def spawner(g,src,title,x,y,mesh='/Game/Northwood/EpicContent/Meshes/SM_Rock',mat=None,by_attribute=False):
  n,s=node(g,u.PCGStaticMeshSpawnerSettings,title,x,y,synchronous_load=True)
  if by_attribute:s.set_mesh_selector_type(u.PCGMeshSelectorByAttribute);s.mesh_selector_parameters.attribute_name='Mesh'
  else:
   e=u.PCGMeshSelectorWeightedEntry();d=e.get_editor_property('descriptor');d.set_editor_property('static_mesh',A.load_asset(mesh))
   if mat:d.set_editor_property('override_materials',[mat])
   e.set_editor_property('descriptor',d);e.set_editor_property('weight',1);s.mesh_selector_parameters.set_editor_property('mesh_entries',[e])
  wire(g,src,n);wire(g,n,g.get_output_node(),bp='Out');return n
 def actor_for(g,station,suffix='',offset=(0,0,0)):
  p=station['centre'];a=spawn(u.PCGVolume,f"M{station['id']:02d}_PCG{suffix}",[p[i]+offset[i] for i in range(3)]);a.set_folder_path(f"Museum/{station['id']:02d} {station['title']}");c=a.get_component_by_class(u.PCGComponent);c.regenerate_in_editor=False;c.set_graph(g);station.setdefault('actors',[]).append(a.get_actor_label());return a
 def save(g):g.get_output_node().set_node_position(1500,0);A.save_loaded_asset(g,False)
 # 01: points made tangible as small markers, explicitly a point visualization.
 g=graph('PCG_M01_Candidates','One concept: create a candidate grid. Small cubes visualize the point positions.');n=grid(g);n,_=xf(g,n,'02 Point visualization size',-400,0,scale=.14);spawner(g,n,'03 Show candidate markers',50,0,'/Engine/BasicShapes/Cube',marker);save(g);actor_for(g,stations[0])
 # 02: same point topology, bounded transform changes, real rock assets.
 g=graph('PCG_M02_Transforms','One concept: bounded seeded transforms preserve candidate count.');n=grid(g);n,s=xf(g,n,'02 Seeded transform variation',-400,0,jitter=90,yaw=360);s.set_editor_property('scale_min',u.Vector(.2,.2,.2));s.set_editor_property('scale_max',u.Vector(.4,.4,.4));spawner(g,n,'03 Show varied real meshes',50,0);save(g);actor_for(g,stations[1])
 # 03: a closed region, not a painted material or a landscape edit.
 g=graph('PCG_M03_ClosedDifference','One concept: subtract a closed spline interior from candidate points.');n=grid(g);q,qs=node(g,u.PCGGetSplineSettings,'02 Tagged closed exclusion',-900,500,comment='Select the single closed spline for this bay. Moving it changes the exclusion.');sel=qs.actor_selector;sel.actor_filter=u.PCGActorFilter.ALL_WORLD_ACTORS;sel.actor_selection=u.PCGActorSelection.BY_TAG;sel.actor_selection_tag='Museum_ClosedExclusion';sel.select_multiple=True;qs.actor_selector=sel;qs.always_requery_actors=True;qs.set_editor_property('track_actors_only_within_bounds',False)
 surface,_=node(g,u.PCGCreateSurfaceFromSplineSettings,'03 Closed interior surface',-450,500);wire(g,q,surface);diff,_=node(g,u.PCGDifferenceSettings,'04 Remove points in the region',-100,0,comment='Binary Difference rejects point candidates. It does not guarantee mesh collision clearance.',density_function=u.PCGDifferenceDensityFunction.BINARY,keep_zero_density_points=False);wire(g,n,diff,bp='Source');wire(g,surface,diff,bp='Differences');n,_=xf(g,diff,'05 Display scale',300,0,scale=.14);spawner(g,n,'06 Show surviving markers',700,0,'/Engine/BasicShapes/Cube',marker);save(g);actor_for(g,stations[2])
 bp=A.load_asset('/Game/Trail/Blueprints/BP_HabitatRegion');p=stations[2]['centre'];region=spawn(bp.generated_class(),'M03_ClosedExclusion',p);region.set_editor_property('tags',['Museum_ClosedExclusion']);region.set_folder_path('Museum/03 Closed spline exclusion');s=region.get_component_by_class(u.SplineComponent);s.set_editor_property('spline_has_been_edited',True);s=region.get_component_by_class(u.SplineComponent);s.modify();s.clear_spline_points(False)
 for xyz in [(-250,-300,0),(250,-300,0),(250,300,0),(-250,300,0)]:s.add_spline_point(u.Vector(*xyz),u.SplineCoordinateSpace.LOCAL,False)
 for k in range(4):s.set_spline_point_type(k,u.SplinePointType.LINEAR,False)
 s.set_closed_loop(True,True);s.set_editor_property('spline_curves',s.get_editor_property('spline_curves'));stations[2]['input_actor']=region.get_actor_label()
 # 04: projection reads the collision surface and transfers its normal first.
 g=graph('PCG_M04_SurfaceSuitability','One concept: project onto a tagged terrain, inspect its normal, filter suitability.');n=grid(g,ext=(750,550,0),cell=150);ray,rs=node(g,u.PCGWorldRayHitSettings,'02 Tagged terrain collision query',-900,500);q=rs.query_params
 for k,v in {'override_default_params':True,'ray_origin':u.Vector(0,0,3000),'ray_direction':u.Vector(0,0,-1),'ray_length':6000.,'ignore_pcg_hits':True,'trace_complex':True,'actor_tag_filter':u.PCGWorldQueryFilter.REQUIRE,'actor_tags_list':'Museum_Surface'}.items():q.set_editor_property(k,v)
 rs.query_params=q;proj,ps=node(g,u.PCGProjectionSettings,'03 Transfer position and normal',-450,0,force_collapse_to_point=True);pp=ps.projection_params;pp.project_positions=True;pp.project_rotations=True;pp.project_scales=False;ps.projection_params=pp;wire(g,n,proj);wire(g,ray,proj,bp='Projection Target');normal,_=node(g,u.PCGNormalToDensitySettings,'04 Normal dot world up',0,0,normal=u.Vector(0,0,1),density_mode=u.PCGNormalToDensityMode.SET);wire(g,proj,normal);filt,_=node(g,u.PCGDensityFilterSettings,'05 Accept flatter ground',400,0,comment='Raise Lower Bound to reject steeper points. This value is a dot product, not degrees.',lower_bound=.975,upper_bound=1.);wire(g,normal,filt);n,_=xf(g,filt,'06 Marker scale',800,0,offset=(0,0,12),scale=.12);spawner(g,n,'07 Show suitable points',1200,0,'/Engine/BasicShapes/Cube',marker);save(g);actor_for(g,stations[3]);p=stations[3]['centre'];terrain=static('M04_Surface',[p[0],p[1],15],(.08,.08,.4),'/Game/Trail/Environment/SM_TrailTerrain',A.load_asset('/Game/Trail/Building/M_BuildingGround'));terrain.set_editor_property('tags',['Museum_Surface']);terrain.set_folder_path('Museum/04 Projection and suitability');stations[3]['input_actor']=terrain.get_actor_label()
 # 05: two instances of one short graph, not two per-population graphs.
 g=graph('PCG_M05_AssetProfiles','One concept: two graph instances select different persistent asset tables under shared placement rules.');u.TrailBiomeAuthoringLibrary.add_museum_profile_parameters(g);n=grid(g,ext=(400,350,0),cell=300);n,_=xf(g,n,'02 Shared display transform',-450,0,scale=.3)
 table,ts=node(g,u.PCGLoadDataTableSettings,'03 Mesh and weight table',-450,500,data_table=A.load_asset('/Game/Trail/Biome/AssetSets/DT_TreesMixed'),output_type=u.PCGExclusiveDataType.PARAM,synchronous_load=True);param,_=node(g,u.PCGGenericUserParameterGetSettings,'AssetSet',-900,700,property_path='AssetSet',output_attribute_name='AssetSet');wire(g,param,table,bp='DataTable');match,ms=node(g,u.PCGMatchAndSetAttributesSettings,'04 Choose from the profile',0,0,match_attributes=False,use_weight_attribute=True,keep_unmatched=False);v=ms.weight_attribute;v.import_text('(Selection=Attribute,AttributeName="Weight")');ms.weight_attribute=v;wire(g,n,match);wire(g,table,match,bp='Match Data');seed,_=node(g,u.PCGGenericUserParameterGetSettings,'VariationSeed',-450,-350,property_path='VariationSeed',output_attribute_name='VariationSeed');wire(g,seed,match,bp='Seed');spawner(g,match,'05 Spawn selected mesh attribute',500,0,by_attribute=True);H.set_object_parameter(g,'AssetSet',A.load_asset('/Game/Trail/Biome/AssetSets/DT_TreesMixed'));save(g)
 for name,tab,offset in [('Trees','TreesMixed',(-600,0,0)),('Scrub','ScrubMixed',(600,0,0))]:
  gi=T.create_asset('PGI_M05_'+name,B+'/Instances',u.PCGGraphInstance,u.PCGGraphInstanceFactory());gi.set_editor_property('graph',g);H.set_object_parameter(gi,'AssetSet',A.load_asset('/Game/Trail/Biome/AssetSets/DT_'+tab));H.set_int32_parameter(gi,'VariationSeed',17);A.save_loaded_asset(gi);actor_for(gi,stations[4],'_'+name,offset)
 # 06: one common candidate set, a raw branch and a pruning branch.
 g=graph('PCG_M06_LocalPruning','One concept: compare the same candidates before and after point-bound competition.');n=grid(g,ext=(400,400,0),cell=150);raw,_=xf(g,n,'02 Before pruning',0,-250,offset=(-650,0,25),scale=.25);spawner(g,raw,'03 Raw candidates',500,-250)
 bounds,_=node(g,u.PCGBoundsModifierSettings,'02 Competition neighborhood',-450,300,comment='This is a point influence box. It is not full mesh collision.',mode=u.PCGBoundsModifierMode.SET,bounds_min=u.Vector(-140,-140,-140),bounds_max=u.Vector(140,140,140),affect_steepness=True,steepness=1.);wire(g,n,bounds);prune,pr=node(g,u.PCGSelfPruningSettings,'03 Resolve local competition',0,300);pp=pr.parameters;pp.pruning_type=u.PCGSelfPruningType.ALL_EQUAL;pp.randomized_pruning=True;pr.parameters=pp;wire(g,bounds,prune);after,_=xf(g,prune,'04 After pruning',400,300,offset=(650,0,25),scale=.25);spawner(g,after,'05 Accepted candidates',850,300);save(g);actor_for(g,stations[5])
 gi=T.create_asset('PGI_M07_Building',B+'/Instances',u.PCGGraphInstance,u.PCGGraphInstanceFactory());gi.set_editor_property('graph',A.load_asset('/Game/Trail/Building/PCG_ModularBuilding'));H.set_vector_parameter(gi,'Cells',u.Vector(2,2,2));H.set_object_parameter(gi,'FacadeSet',A.load_asset('/Game/Trail/Building/Profiles/DT_Facade_Windows'));H.set_int32_parameter(gi,'VariationSeed',17);A.save_loaded_asset(gi);actor_for(gi,stations[6])
 for st in stations:
  p=st['centre'];folder=f"Museum/{st['id']:02d} {st['title']}";floor=static(f"M{st['id']:02d}_Floor",[p[0],p[1],-20],(25,23,.4),'/Engine/BasicShapes/Cube',slate);floor.set_folder_path(folder);wall=static(f"M{st['id']:02d}_Board",[p[0],p[1]+1100,525],(25,.3,10.5),'/Engine/BasicShapes/Cube',board);wall.set_folder_path(folder)
  text(f"M{st['id']:02d}_Title",f"{st['id']:02d}  {st['title']}",[p[0]-1100,p[1]+1070,950],58).set_folder_path(folder);text(f"M{st['id']:02d}_Prompt",st['question']+'\n'+st['change']+'\n'+st['expected'],[p[0]-1100,p[1]+1065,800],32).set_folder_path(folder)
  cam=spawn(u.CameraActor,f"M{st['id']:02d}_Camera",[p[0],p[1]-2500,1650],u.Rotator(pitch=-25,yaw=90));cam.set_folder_path(folder);st['camera']=cam.get_actor_label()
 sun=spawn(u.DirectionalLight,'Museum sun',[0,0,6000],u.Rotator(pitch=-45,yaw=-40));sun.get_component_by_class(u.DirectionalLightComponent).set_intensity(6.)
 sky=spawn(u.SkyLight,'Museum sky light',[0,0,5000]);sc=sky.get_component_by_class(u.SkyLightComponent);sc.set_editor_property('source_type',u.SkyLightSourceType.SLS_SPECIFIED_CUBEMAP);sc.set_editor_property('cubemap',A.load_asset('/Game/Trail/Presentation/T_CloudSky_CC0'));sc.set_intensity(.12)
 pp=spawn(u.PostProcessVolume,'Museum exposure',[0,0,0]);pp.set_editor_property('unbound',True);settings=pp.get_editor_property('settings');settings.set_editor_property('override_auto_exposure_bias',True);settings.set_editor_property('auto_exposure_bias',-.6);pp.set_editor_property('settings',settings)
 L.save_current_level();(O/'build.json').write_text(json.dumps({'status':'PASS','map':B+'/Maps/PCG_Museum','stations':stations,'core_stations':6,'optional_station':7,'engine':u.SystemLibrary.get_engine_version(),'runtime_custom_plugin_required':False},indent=2))
except Exception:(O/'build.json').write_text(json.dumps({'status':'FAIL','error':traceback.format_exc()},indent=2));u.log_error(traceback.format_exc())
u.SystemLibrary.quit_editor()
