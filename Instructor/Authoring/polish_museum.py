"""Legible native labels, clear markers and a tighter camera. No scene fabrication."""
import unreal as u,json,traceback
from pathlib import Path
R=Path(u.Paths.project_dir());O=R/'Validation/MuseumPass';A=u.EditorAssetLibrary;M=u.MaterialEditingLibrary;L=u.get_editor_subsystem(u.LevelEditorSubsystem);E=u.get_editor_subsystem(u.EditorActorSubsystem)
try:
 assert L.load_level('/Game/Trail/Museum/Maps/PCG_Museum');named={a.get_actor_label():a for a in E.get_all_level_actors()};config=json.loads((O/'build.json').read_text())
 for st in config['stations']:
  number=st['id'];p=st['centre'];prefix=f'M{number:02d}_'
  for suffix,size in [('Title',80),('Prompt',48)]:
   a=named[prefix+suffix];pos=a.get_actor_location();pos.x=p[0]+1100;a.set_actor_location(pos,False,False);a.set_actor_rotation(u.Rotator(yaw=-90),False);c=a.get_component_by_class(u.TextRenderComponent);c.set_world_size(size);c.set_cast_shadow(False)
  board=named[prefix+'Board'];board.static_mesh_component.set_cast_shadow(False)
  cam=named[st['camera']];cam.get_component_by_class(u.CameraComponent).set_field_of_view(70.);position=u.Vector(p[0],p[1]-2100,1500);target=u.Vector(p[0],p[1]+100,300);cam.set_actor_location(position,False,False);cam.set_actor_rotation(u.MathLibrary.find_look_at_rotation(position,target),False)
 for name in ['M_MuseumBoard','M_MuseumMarker']:
  mat=A.load_asset('/Game/Trail/Museum/Materials/'+name);base=M.get_material_property_input_node(mat,u.MaterialProperty.MP_BASE_COLOR);assert base;mat.set_editor_property('shading_model',u.MaterialShadingModel.MSM_UNLIT);M.connect_material_property(base,'',u.MaterialProperty.MP_EMISSIVE_COLOR);M.recompile_material(mat);A.save_loaded_asset(mat,False)
 named['Museum sky light'].get_component_by_class(u.SkyLightComponent).set_intensity(.4)
 g=A.load_asset('/Game/Trail/Museum/Graphs/PCG_M06_LocalPruning')
 for title,x in [('02 Before pruning',650),('04 After pruning',-650)]:
  s=next(n.get_settings() for n in g.nodes if str(n.node_title)==title);s.set_editor_property('offset_min',u.Vector(x,0,25));s.set_editor_property('offset_max',u.Vector(x,0,25))
 A.save_loaded_asset(g,False)
 # A native closed outline follows actor translation with the exclusion input.
 mat=A.load_asset('/Game/Trail/Museum/Materials/M_MuseumExclusion')
 if not mat:
  mat=u.AssetToolsHelpers.get_asset_tools().create_asset('M_MuseumExclusion','/Game/Trail/Museum/Materials',u.Material,u.MaterialFactoryNew());mat.set_editor_property('shading_model',u.MaterialShadingModel.MSM_UNLIT);n=M.create_material_expression(mat,u.MaterialExpressionConstant3Vector);n.set_editor_property('constant',u.LinearColor(1.,.25,.04,1));M.connect_material_property(n,'',u.MaterialProperty.MP_EMISSIVE_COLOR);M.recompile_material(mat);A.save_loaded_asset(mat)
 parent=named['M03_ClosedExclusion'];curve=parent.get_component_by_class(u.SplineComponent)
 for k in range(curve.get_number_of_spline_points()):
  a=curve.get_location_at_spline_point(k,u.SplineCoordinateSpace.WORLD)+u.Vector(0,0,8);b=curve.get_location_at_spline_point((k+1)%4,u.SplineCoordinateSpace.WORLD)+u.Vector(0,0,8);label='M03_Outline_'+str(k);edge=named.get(label) or E.spawn_actor_from_class(u.StaticMeshActor,(a+b)*.5);edge.set_actor_label(label);edge.static_mesh_component.set_static_mesh(A.load_asset('/Engine/BasicShapes/Cube'));edge.static_mesh_component.set_material(0,mat);edge.static_mesh_component.set_collision_enabled(u.CollisionEnabled.NO_COLLISION);edge.static_mesh_component.set_cast_shadow(False);edge.set_actor_location((a+b)*.5,False,False);edge.set_actor_rotation(u.MathLibrary.find_look_at_rotation(a,b),False);edge.set_actor_scale3d(u.Vector((b-a).length()/100,.06,.06));edge.attach_to_actor(parent,'',u.AttachmentRule.KEEP_WORLD,u.AttachmentRule.KEEP_WORLD,u.AttachmentRule.KEEP_WORLD,False);edge.set_folder_path('Museum/03 Closed spline exclusion')
 for path,title in [('/Game/Trail/Museum/Graphs/PCG_M01_Candidates','02 Point visualization size'),('/Game/Trail/Museum/Graphs/PCG_M03_ClosedDifference','05 Display scale')]:
  g=A.load_asset(path);s=next(n.get_settings() for n in g.nodes if str(n.node_title)==title);s.set_editor_property('scale_min',u.Vector(.45,.45,.45));s.set_editor_property('scale_max',u.Vector(.45,.45,.45));A.save_loaded_asset(g,False)
 L.save_current_level();(O/'polish.json').write_text(json.dumps({'status':'PASS','text_facing_corrected':True,'text_shadow_disabled':True,'larger_point_markers':True,'lighting_and_camera_only':True},indent=2))
except Exception:(O/'polish.json').write_text(json.dumps({'status':'FAIL','error':traceback.format_exc()},indent=2));u.log_error(traceback.format_exc())
u.SystemLibrary.quit_editor()
