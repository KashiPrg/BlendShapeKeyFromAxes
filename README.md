# BlendShapeKeyFromAxes

Blenderの`Blend from Shape`をX, Y, Z軸それぞれに対して実行するオペレータを追加します。

## 使い方

1. `blend_shapekey_from_axes.py`をアドオンとしてインポートし、有効にしてください。  
2. 編集対象のオブジェクトを選択してください。  
3. 編集対象のシェイプキーを選択してください。  
4. `Edit Mode`に移行してください。  
5. `Ctrl + V`で`Vertex`メニューを出します。  
6. `Blend from Shape based on Axes`を選択します。このアドオンを追加した直後なら、メニューの一番下にあるはずです。
7. 基本的な挙動は標準の`Blend from Shape`と同様です。`Weights`が各軸の成分に分割されている点が異なります。  
