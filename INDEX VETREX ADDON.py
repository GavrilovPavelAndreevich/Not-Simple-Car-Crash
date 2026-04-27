bl_info = {
    "name": "NSCC Vertex Tool",
    "author": "User",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "category": "3D View",
}

import bpy
import bmesh

class GetVertices(bpy.types.Operator):
    bl_idname = "mesh.get_vertices"
    bl_label = "Get Data"
    
    def execute(self, context):
        if context.mode != 'EDIT_MESH':
            context.scene.vout = "Select Edit Mode!"
            return {'FINISHED'}
        
        tool_settings = context.tool_settings
        if tool_settings.mesh_select_mode[1]:
            return self.edges_mode(context)
        
        objs = context.selected_objects
        if len(objs) == 2:
            return self.connecting(context, objs)
        return self.single(context, context.active_object)
    
    def edges_mode(self, context):
        obj = context.active_object
        bm = bmesh.from_edit_mesh(obj.data)
        sel = [e.index for e in bm.edges if e.select]
        
        if not sel:
            context.scene.vout = "Select at least 1 edge"
            return {'FINISHED'}
        
        context.scene.vout = '<edge_ids>' + ' '.join(str(i) for i in sel) + '</edge_ids>'
        return {'FINISHED'}
    
    def single(self, context, obj):
        bm = bmesh.from_edit_mesh(obj.data)
        sel = [v.index for v in bm.verts if v.select]
        cnt = len(sel)
        
        if cnt == 0:
            context.scene.vout = "---"
        elif cnt == 1:
            context.scene.vout = f'vertex_id="{sel[0]}"'
        elif cnt == 2:
            active = None
            for e in bm.select_history:
                if isinstance(e, bmesh.types.BMVert):
                    active = e.index
                    break
            if active and active in sel:
                v1, v2 = (active, sel[0]) if sel[0] != active else (active, sel[1])
            else:
                v1, v2 = sel[0], sel[1]
            context.scene.vout = f'vertex_id_1="{v1}" vertex_id_2="{v2}"'
        else:
            context.scene.vout = f"Select 1-2 vertices (found {cnt})"
        
        return {'FINISHED'}
    
    def connecting(self, context, objs):
        active = context.active_object
        other = objs[0] if objs[0] != active else objs[1]
        
        bm = bmesh.from_edit_mesh(active.data)
        a_sel = [v.index for v in bm.verts if v.select]
        a_active = None
        for e in bm.select_history:
            if isinstance(e, bmesh.types.BMVert):
                a_active = e.index
                break
        
        bpy.context.view_layer.objects.active = other
        bm = bmesh.from_edit_mesh(other.data)
        o_sel = [v.index for v in bm.verts if v.select]
        
        bpy.context.view_layer.objects.active = active
        
        if len(a_sel) != 1 or len(o_sel) != 1:
            context.scene.vout = "Select 1 vertex in each object"
            return {'FINISHED'}
        
        v_this = a_active if a_active and a_active in a_sel else a_sel[0]
        v_other = o_sel[0]
        
        context.scene.vout = f'vertex_id_this="{v_this}" vertex_id_other="{v_other}" other_part_name="{other.name}"'
        return {'FINISHED'}

class CopyOutput(bpy.types.Operator):
    bl_idname = "mesh.copy_output"
    bl_label = "Copy"
    
    def execute(self, context):
        context.window_manager.clipboard = context.scene.vout
        return {'FINISHED'}

class VIEW3D_PT_vertex(bpy.types.Panel):
    bl_label = "NSCC Tool"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "NSCC"
    
    def draw(self, context):
        layout = self.layout
        layout.operator("mesh.get_vertices")
        
        row = layout.row(align=True)
        row.prop(context.scene, "vout", text="")
        row.operator("mesh.copy_output", text="", icon='COPYDOWN')

def register():
    bpy.utils.register_class(GetVertices)
    bpy.utils.register_class(CopyOutput)
    bpy.utils.register_class(VIEW3D_PT_vertex)
    bpy.types.Scene.vout = bpy.props.StringProperty(default="---")

def unregister():
    bpy.utils.unregister_class(GetVertices)
    bpy.utils.unregister_class(CopyOutput)
    bpy.utils.unregister_class(VIEW3D_PT_vertex)
    del bpy.types.Scene.vout

if __name__ == "__main__":
    register()