# This file is part of mcskingenerator.
# mcskingenerator is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# mcskingenerator is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with mcskingenerator. If not, see <https://www.gnu.org/licenses/>.

import os
import json
import base64
import io
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from PIL import Image
from converter import convert_image_to_skin, image_to_data_url

app = Flask(__name__, static_folder='webui', static_url_path='')

HISTORY_DIR = os.path.join(os.path.dirname(__file__), 'history')
if not os.path.exists(HISTORY_DIR):
    os.makedirs(HISTORY_DIR)

def decode_base64_image(base64_string):
    if ";base64," in base64_string:
        header, encoded = base64_string.split(";base64,", 1)
    else:
        encoded = base64_string

    try:
        image_data = base64.b64decode(encoded)
        return Image.open(io.BytesIO(image_data))
    except Exception as e:
        print(f"Error decoding base64 image: {e}")
        return None

def create_thumbnail(image: Image.Image, size=(64, 64)) -> str:
    thumb = image.copy()
    thumb.thumbnail(size, Image.Resampling.LANCZOS)
    return image_to_data_url(thumb)

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/convert', methods=['POST'])
def handle_convert():
    data = request.get_json()
    if not data or 'image' not in data or 'size' not in data:
        return jsonify({'success': False, 'message': '缺少必要的参数 (image, size)'}), 400

    image_data_url = data['image']
    size = data['size']
    options = data.get('options', {})

    if size not in ['64', '128']:
        return jsonify({'success': False, 'message': '无效的尺寸，必须是 "64" 或 "128"'}), 400

    try:
        original_image = decode_base64_image(image_data_url)
        if original_image is None:
             return jsonify({'success': False, 'message': '无法解码图片数据'}), 400

        skin_image = convert_image_to_skin(original_image, size, options)

        skin_data_url = image_to_data_url(skin_image)

        try:
            history_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            thumbnail_data_url = create_thumbnail(original_image)

            history_entry = {
                'id': history_id,
                'originalImage': thumbnail_data_url,
                'convertedSkin': skin_data_url,
                'size': size,
                'createdAt': timestamp
            }

            history_file_path = os.path.join(HISTORY_DIR, f"{history_id}.json")
            with open(history_file_path, 'w', encoding='utf-8') as f:
                json.dump(history_entry, f, ensure_ascii=False, indent=2)
            print(f"History entry saved: {history_file_path}")
        except Exception as e:
            print(f"Error saving history: {e}")

        return jsonify({
            'success': True,
            'skin': skin_data_url,
            'message': '转换成功'
        })

    except Exception as e:
        print(f"转换过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'转换失败: {str(e)}'}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    history_list = []
    if not os.path.exists(HISTORY_DIR):
        return jsonify({'success': True, 'history': [], 'total': 0})

    try:
        for filename in os.listdir(HISTORY_DIR):
            if filename.endswith('.json'):
                file_path = os.path.join(HISTORY_DIR, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        history_entry = json.load(f)
                        if all(k in history_entry for k in ('id', 'originalImage', 'convertedSkin', 'size', 'createdAt')):
                            history_list.append(history_entry)
                        else:
                            print(f"Skipping invalid history file: {filename}")
                except Exception as e:
                    print(f"Error reading history file {filename}: {e}")

        history_list.sort(key=lambda x: x.get('createdAt', ''), reverse=True)

        limit = request.args.get('limit', default=10, type=int)
        offset = request.args.get('offset', default=0, type=int)
        total = len(history_list)
        paginated_history = history_list[offset:offset + limit]

        return jsonify({
            'success': True,
            'history': paginated_history,
            'total': total
        })

    except Exception as e:
        print(f"Error fetching history: {e}")
        return jsonify({'success': False, 'message': '获取历史记录失败'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5001)