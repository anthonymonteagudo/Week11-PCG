"""Author one stock-node modular building graph; private bridge adds parameter types only.
The delivered graph runs with TrailBiomeAuthoring disabled.
"""
import unreal as u,json,traceback,math
from pathlib import Path
R=Path(u.Paths.project_dir());OUT=R/'Validation/BuildingPass';A=u.EditorAssetLibrary;T=u.AssetToolsHelpers.get_asset_tools();H=u.PCGGraphParametersHelpers
B='/Game/Trail/Building';levels=u.get_editor_subsystem(u.LevelEditorSubsystem);actors=u.get_editor_subsystem(u.EditorActorSubsystem)
try:
 if A.does_asset_exist(B+'/PCG_ModularBuilding'):
  assert json.loads((OUT/'build.json').read_text())['status']=='FAIL','Completed example exists: refine rather than rebuild.'
  assert str(A.load_asset(B+'/PCG_ModularBuilding').description).startswith('Rectangular Old West modular building.')
  assert A.delete_asset(B+'/PCG_ModularBuilding'),'Could not replace this pass\'s failed authoring draft.'
 g=T.create_asset('PCG_ModularBuilding',B,u.PCGGraph,u.PCGGraphFactory());u.TrailBiomeAuthoringLibrary.add_building_parameters(g)
 H.set_vector_parameter(g,'Cells',u.Vector(3,4,2))
 def pins(n,d='input_pins'):return [str(p.properties.label) for p in n.get_editor_property(d)]
 def node(cls,title,x,y,**kw):
  n,s=g.add_node_of_type(cls);n.node_title=title;n.set_node_position(x,y)
  for k,v in kw.items():s.set_editor_property(k,v)
  return n,s
 def wire(a,b,ap='Out',bp='In'):
  assert ap in pins(a,'output_pins') and bp in pins(b),(a.node_title,ap,b.node_title,bp,pins(b))
  g.add_edge(a,ap,b,bp)
 def selector(s,key,name):
  v=s.get_editor_property(key);v.import_text('(Selection=Attribute,AttributeName="'+name+'")');s.set_editor_property(key,v)
 def const(v,title,x,y):
  n,s=node(u.PCGCreateAttributeSetSettings,title,x,y);a=s.attribute_types;a.type=u.PCGMetadataTypes.VECTOR;a.vector_value=u.Vector(*v);s.attribute_types=a;selector(s,'output_target','Value');return n
 def mathnode(op,a,b,title,x,y):
  n,s=node(u.PCGMetadataMathsSettings,title,x,y,operation=getattr(u.PCGMetadataMathsOperation,op));selector(s,'input_source1','Value');selector(s,'output_target','Value');wire(a,n,bp='InA' if b else 'In')
  if b:selector(s,'input_source2','Value');wire(b,n,bp='InB')
  return n
 def mul(a,v,title,x,y):return mathnode('MULTIPLY',a,const(v,title+' factor',x-350,y+140),title,x,y)
 def override(a,b,suffix):
  p=[p for p in pins(b) if p==suffix or p.lower().endswith('/'+suffix.lower())];assert len(p)==1,(b.node_title,suffix,pins(b));wire(a,b,bp=p[0])
 def transform(src,title,x,y,offset=(0,0,0),yaw=0,scale=(1,1,1)):
  n,s=node(u.PCGTransformPointsSettings,title,x,y,offset_min=u.Vector(*offset),offset_max=u.Vector(*offset),rotation_min=u.Rotator(yaw=yaw),rotation_max=u.Rotator(yaw=yaw),scale_min=u.Vector(*scale),scale_max=u.Vector(*scale),uniform_scale=False);wire(src,n);return n
 def lift(src,offset,title,x,y):
  n=transform(src,title,x,y);override(offset,n,'OffsetMin');override(offset,n,'OffsetMax');return n
 def grid(title,x,y,ext,cell=(400,400,350),corners=False):
  n,s=node(u.PCGCreatePointsGridSettings,title,x,y,cell_size=u.Vector(*cell),grid_extents=u.Vector(),set_points_bounds=False,cull_points_outside_volume=False,point_steepness=1.,point_position=u.PCGPointPosition.CELL_CORNERS if corners else u.PCGPointPosition.CELL_CENTER);override(ext,n,'GridExtents');return n
 get,gs=node(u.PCGGenericUserParameterGetSettings,'01 Cells: rows / columns / floors',-3200,-800,property_path='Cells',output_attribute_name='Value')
 rounded=mathnode('FLOOR',get,None,'01 Whole module counts',-2850,-800)
 lower=mathnode('MAX',rounded,const((1,1,1),'Minimum one on every axis',-3200,-450),'01 Minimum one floor',-2500,-800)
 cells=mathnode('MIN',lower,const((12,12,12),'Maximum 12 on every axis',-2850,-300),'01 Bound the example workload',-2150,-800)
 ext=mul(cells,(200,200,175),'02 Grid half extents',-1700,-900)
 z=mul(cells,(0,0,175),'02 Half total height',-1700,-600)
 z=mathnode('ADD',z,const((0,0,-175),'Centre first storey at zero',-1700,-300),'02 Floor elevation shift',-1250,-600)
 raw=grid('03 Local cell centres',-800,-900,ext);floor=lift(raw,z,'03 Floors at 0, 350, 700...',-400,-900)
 # Exact coincident face centres cancel; point influence is a hard 2 cm box.
 shifts=[]
 for k,(label,off) in enumerate([('East',(200,0,0)),('West',(-200,0,0)),('North',(0,200,0)),('South',(0,-200,0))]):shifts.append(transform(floor,'04 '+label+' candidate faces',0,k*500-1000,offset=off))
 faces=[]
 for k,(label,yaw,pivot) in enumerate([('East',0,(0,200,0)),('West',180,(0,-200,0)),('North',90,(-200,0,0)),('South',-90,(200,0,0))]):
  n,s=node(u.PCGDifferenceSettings,'05 '+label+': remove internal faces',400,k*500-1000,density_function=u.PCGDifferenceDensityFunction.BINARY,keep_zero_density_points=False);wire(shifts[k],n,bp='Source');wire(shifts[k^1],n,bp='Differences');faces.append(transform(n,'06 '+label+' wall pivot + facing',800,k*500-1000,offset=pivot,yaw=yaw))
 merge,ms=node(u.PCGMergeSettings,'07 Merge exterior wall points',1250,-500)
 for f in faces:wire(f,merge)
 # Single shared table chooses interchangeable facade modules after topology.
 tables={};row=A.load_asset('/Game/Trail/Biome/ST_BiomeMesh')
 for name,entries in {'Windows':[('SM_Wall_Window_400_01a',5),('SM_Wall_400_01a',1)],'Solid':[('SM_Wall_400_01a',1)]}.items():
  factory=u.DataTableFactory();factory.struct=row;t=A.load_asset(B+'/Profiles/DT_Facade_'+name) or T.create_asset('DT_Facade_'+name,B+'/Profiles',u.DataTable,factory);assert t
  data=[{'Name':'Module'+str(k),'Mesh':'/Game/Northwood/Meshes/Structures/'+n+'.'+n,'Weight':float(w),'FootprintRadiusCm':0} for k,(n,w) in enumerate(entries)]
  assert u.DataTableFunctionLibrary.fill_data_table_from_json_string(t,json.dumps(data));A.save_loaded_asset(t);tables[name]=t
 H.set_object_parameter(g,'FacadeSet',tables['Windows'])
 table,ts=node(u.PCGLoadDataTableSettings,'07 Facade mesh / weight profile',1250,-100,data_table=tables['Windows'],output_type=u.PCGExclusiveDataType.PARAM,synchronous_load=True)
 p,ps=node(u.PCGGenericUserParameterGetSettings,'FacadeSet',850,100,property_path='FacadeSet',output_attribute_name='FacadeSet');override(p,table,'DataTable')
 match,ss=node(u.PCGMatchAndSetAttributesSettings,'08 Choose a compatible facade',1650,-500,match_attributes=False,use_weight_attribute=True,keep_unmatched=False);selector(ss,'weight_attribute','Weight');wire(merge,match);wire(table,match,bp='Match Data')
 seed,_=node(u.PCGGenericUserParameterGetSettings,'VariationSeed',1250,250,property_path='VariationSeed',output_attribute_name='VariationSeed');override(seed,match,'Seed')
 actor,aset=node(u.PCGDataFromActorSettings,'09 Building actor transform',1650,600,mode=u.PCGGetDataFromActorMode.GET_SINGLE_POINT);sel=aset.actor_selector;sel.actor_filter=u.PCGActorFilter.SELF;aset.actor_selector=sel
 def world(src,title,x,y):
  n,s=node(u.PCGCopyPointsSettings,title,x,y);wire(src,n,bp='Source');wire(actor,n,bp='Target');return n
 def spawn(src,title,x,y,mesh=None):
  n,s=node(u.PCGStaticMeshSpawnerSettings,title,x,y,synchronous_load=True)
  if mesh:
   e=u.PCGMeshSelectorWeightedEntry();d=e.get_editor_property('descriptor');d.set_editor_property('static_mesh',A.load_asset('/Game/Northwood/Meshes/Structures/'+mesh));e.set_editor_property('descriptor',d);e.set_editor_property('weight',1);sel=s.mesh_selector_parameters;sel.set_editor_property('mesh_entries',[e])
  else:s.set_mesh_selector_type(u.PCGMeshSelectorByAttribute);s.mesh_selector_parameters.attribute_name='Mesh'
  wire(src,n);wire(n,g.get_output_node(),bp='Out');return n
 spawn(world(match,'09 Local walls to world',2100,-500),'10 Spawn facade modules',2500,-500)
 floormesh=transform(floor,'06 Floor corner-pivot correction',800,1300,offset=(200,200,0));spawn(world(floormesh,'09 Local floors to world',2100,1300),'10 Spawn floor tiles',2500,1300,'SM_Floor_400_01a')
 ce=mul(cells,(200,200,0),'02 Footprint half extents',-1700,1600);step=mul(cells,(400,400,0),'02 Corner lattice step',-1700,1950);step=mathnode('ADD',step,const((0,0,1),'Positive unused Z cell size',-1700,2150),'02 Corner spacing',-1250,1950)
 cg=grid('03 Four footprint junctions',-800,1600,ce,cell=(400,400,1),corners=True);override(step,cg,'CellSize')
 he=mul(cells,(0,0,175),'02 Floor stack extents',-1700,2350);hg=grid('03 One point per floor',-800,2300,he,cell=(1,1,350));hg=lift(hg,z,'03 Floor stack from ground',-400,2300)
 cp,cps=node(u.PCGCopyPointsSettings,'04 Repeat four junctions on every floor',0,1800);wire(cg,cp,bp='Source');wire(hg,cp,bp='Target')
 corner=transform(cp,'06 Fit 450 cm post to 350 cm storey',800,1800,scale=(1.65,1.65,350/450));spawn(world(corner,'09 Local corners to world',2100,1800),'10 Spawn corner posts',2500,1800,'SM_Wall_Pillar_400_01a')
 rg=grid('03 Roof tile centres',-800,2900,ce);rz=mul(cells,(0,0,350),'02 Top of wall stack',-1700,2900);roof=lift(rg,rz,'04 Flat roof elevation',-400,2900);roof=transform(roof,'06 Roof tile pivot correction',800,2900,offset=(200,200,0));spawn(world(roof,'09 Local roof to world',2100,2900),'10 Close the roof',2500,2900,'SM_Floor_400_01a')
 g.description='Rectangular Old West modular building. Whole cell counts drive one native stock graph: exact face cancellation, module pivot correction, per-floor corner replication, weighted facade profiles, actor-local to world conversion. Flat platform roof baseline. 400 cm bays; 350 cm storeys. Actor scale 1.'
 A.save_loaded_asset(g,False)
 assert levels.load_level(B+'/Maps/Building_Examples') if A.does_asset_exist(B+'/Maps/Building_Examples') else levels.new_level(B+'/Maps/Building_Examples')
 assert not any(a.get_actor_label().startswith('Building_') for a in actors.get_all_level_actors()),'Existing populated example: do not rebuild.'
 def spawnactor(cls,label,xyz,rot=None):
  a=actors.spawn_actor_from_class(cls,u.Vector(*xyz),rot or u.Rotator());a.set_actor_label(label);return a
 # Reuse established presentation sky and material, without touching trail maps.
 ground=spawnactor(u.StaticMeshActor,'Building demonstration ground',(0,0,-205));ground.static_mesh_component.set_static_mesh(A.load_asset('/Engine/BasicShapes/Cube'));ground.set_actor_scale3d(u.Vector(160,110,4));ground.static_mesh_component.set_material(0,A.load_asset('/Game/Trail/Regions/Materials/M_Ground_Forest'))
 sun=spawnactor(u.DirectionalLight,'Building sun',(0,0,4000),u.Rotator(pitch=-38,yaw=-32));sun.get_component_by_class(u.DirectionalLightComponent).set_intensity(6.)
 sky=spawnactor(u.SkyLight,'Building sky light',(0,0,3000));sc=sky.get_component_by_class(u.SkyLightComponent);sc.set_editor_property('source_type',u.SkyLightSourceType.SLS_SPECIFIED_CUBEMAP);sc.set_editor_property('cubemap',A.load_asset('/Game/Trail/Presentation/T_CloudSky_CC0'));sc.set_intensity(.12)
 dome=spawnactor(u.StaticMeshActor,'Building photographic sky',(0,0,0));dome.static_mesh_component.set_static_mesh(A.load_asset('/Engine/BasicShapes/Sphere'));dome.set_actor_scale3d(u.Vector(20000,20000,20000));dome.static_mesh_component.set_material(0,A.load_asset('/Game/Trail/Presentation/M_PhotographicSky'));dome.static_mesh_component.set_collision_enabled(u.CollisionEnabled.NO_COLLISION);dome.static_mesh_component.set_editor_property('cast_shadow',False)
 spawnactor(u.CameraActor,'Building overview camera',(-7600,-10500,7800),u.Rotator(pitch=-30,yaw=55))
 cases=[('Cabin',(3,4,1),(-3000,-2200,0),0,'Windows'),('Lodge',(3,4,2),(0,-2200,0),0,'Windows'),('Tower',(2,2,4),(3000,-2200,0),0,'Windows'),('Longhouse',(1,6,1),(-3000,2200,0),0,'Solid'),('Rotated',(3,4,2),(0,2200,0),30,'Windows'),('Solid',(3,4,2),(3500,2200,0),0,'Solid')]
 records=[]
 for name,counts,location,yaw,profile in cases:
  i=T.create_asset('PGI_Building_'+name,B+'/Instances',u.PCGGraphInstance,u.PCGGraphInstanceFactory());i.set_editor_property('graph',g);H.set_vector_parameter(i,'Cells',u.Vector(*counts));H.set_object_parameter(i,'FacadeSet',tables[profile]);H.set_int32_parameter(i,'VariationSeed',17);A.save_loaded_asset(i,False)
  a=spawnactor(u.PCGVolume,'Building_'+name,location,u.Rotator(yaw=yaw));c=a.get_component_by_class(u.PCGComponent);c.regenerate_in_editor=False;c.set_graph(i)
  records.append({'name':name,'cells':counts,'position':location,'yaw':yaw,'profile':profile,'instance':i.get_path_name()})
 levels.save_current_level();(OUT/'build.json').write_text(json.dumps({'status':'PASS','engine':u.SystemLibrary.get_engine_version(),'graph':g.get_path_name(),'nodes':len(g.nodes),'cases':records,'runtime_custom_plugin_required':False},indent=2))
except Exception:(OUT/'build.json').write_text(json.dumps({'status':'FAIL','error':traceback.format_exc()},indent=2));u.log_error(traceback.format_exc())
u.SystemLibrary.quit_editor()
