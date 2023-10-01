import bmesh
import bpy
from bpy.props import BoolProperty, EnumProperty, FloatVectorProperty
from bpy.types import Context
from mathutils import Vector
from types import NoneType

# アドオンに関する情報を保持する、bl_info変数
bl_info = {
    "name": "BlendShapeKeyFromAxes",
    "description": "Execute \"Blend from Shape\" operation based on X, Y, Z axes.",
    "author": "Kashiwagi_K",
    "version": (1, 0),
    "blender": (3, 4, 0),
    "location": "View3D > Mesh Edit Mode > Vertex",
    "warning": "",
    "support": "COMMUNITY",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Mesh"
}


# アクティブなオブジェクトからシェイプキーを取得し、EnumProperty用のitemsを生成
def get_shapekey_items(scene, context):
    # context.object.data -> 選択中のオブジェクトのメッシュデータ
    # keys の型がNoneType -> そのメッシュにはシェイプキー(key_blocksというアトリビュート)が無い
    keys = context.object.data.shape_keys
    if type(keys) == NoneType:
        return []

    # data.shape_keys.key_blocks -> メッシュデータに含まれるシェイプキーのリスト
    result = [
        (key.name, key.name, key.name)
        for i, key in enumerate(keys.key_blocks)
    ]

    # 表示順をBlender標準と同じにするために逆順のスライスを返す
    return result[::-1]


# X, Y, Z軸それぞれに関して重み付けをしてシェイプキーを合成するオペレータ
class BlendShapeKeyFromAxes(bpy.types.Operator):
    bl_idname = "mesh.blend_shapekey_from_axes"
    bl_label = "Blend from Shape based on Axes"
    bl_description = "Execute \"Blend from Shape\" operation based on X, Y, Z axes."
    bl_options = {'REGISTER', 'UNDO'}

    # 合成元のシェイプキーを選択するドロップダウンリスト
    # get_shapekey_itemsにitemsを生成させることで、シェイプキーのリストを動的に更新できる
    # ただしリストが不定な影響か、defaultを設定するとAttributeErrorが発生する
    # flake8のバグが発生するので無視用のコメントを記述
    prop_shape: EnumProperty(
        name="Shape",  # noqa: F821
        description="Shape key to use for blending:",    # noqa: F722
        items=get_shapekey_items
    )

    prop_weights: FloatVectorProperty(
        name="Weights",     # noqa: F821
        description="Factors for blending the shape key in the X, Y, and Z axes.",  # noqa: F722
        size=3,
        default=(1.0, 1.0, 1.0),
        soft_min=-2.0,
        soft_max=2.0,
        step=1
    )

    prop_add: BoolProperty(
        name="Add",     # noqa: F821
        description="Add rather than blend between shapes.",    # noqa: F722
        default=True
    )

    # メニューを実行したときに呼ばれる関数
    def execute(self, context: Context):
        obj = context.object
        mesh = obj.data
        # bpy.context.object.data.shape_keys の型がNoneType -> そのメッシュにはシェイプキー(key_blocksというアトリビュート)が無い
        # よって処理を続行できないのでエラー
        if type(mesh.shape_keys) == NoneType:
            self.report({'ERROR'}, "Active mesh does not have shape keys")
            return {'CANCELLED'}

        # メッシュを変更する準備
        bm = bmesh.from_edit_mesh(mesh)
        # これをやらないと、オペレータプロパティ(上記のprop_*類)を変更したときにエラーが発生する
        bm.verts.ensure_lookup_table()

        # シェイプキーを軸ごとに合成
        basis = mesh.shape_keys.key_blocks[0].data
        source_shape = mesh.shape_keys.key_blocks[self.prop_shape].data
        weights = Vector(self.prop_weights)

        for i in range(len(basis)):
            if bm.verts[i].select:
                add = (source_shape[i].co - basis[i].co) * weights
                if self.prop_add:
                    bm.verts[i].co = bm.verts[i].co + add
                else:
                    bm.verts[i].co = basis[i].co + add

        # 変更したメッシュを適用
        bmesh.update_edit_mesh(mesh)

        return {'FINISHED'}


# ↓アドオン有効/無効化時の処理


# メニューを構築する関数
def menu_fn(self, context: Context):
    self.layout.separator()
    self.layout.operator(BlendShapeKeyFromAxes.bl_idname)


# Blenderに登録するクラス
classes = [
    BlendShapeKeyFromAxes,
]


# アドオン有効化時の処理
def register():
    # オペレータを登録
    for c in classes:
        bpy.utils.register_class(c)

    # メニューを登録
    bpy.types.VIEW3D_MT_edit_mesh_vertices.append(menu_fn)


# アドオン無効化時の処理
def unregister():
    # メニューを削除
    bpy.types.VIEW3D_MT_edit_mesh_vertices.remove(menu_fn)

    # オペレータを削除
    for c in classes:
        bpy.utils.unregister_class(c)


# メイン処理
if __name__ == "__main__":
    register()
