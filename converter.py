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

from PIL import Image
import io
import base64

# 定义 64x64 皮肤各部位的坐标和尺寸 (x, y, width, height)
# 格式: (目标区域左上角x, 目标区域左上角y, 目标区域宽度, 目标区域高度)
SKIN_LAYOUT_64 = {
    # 头
    'head_front': (8, 8, 8, 8),
    'head_back': (24, 8, 8, 8),
    'head_top': (8, 0, 8, 8),
    'head_bottom': (16, 0, 8, 8),
    'head_left': (16, 8, 8, 8),
    'head_right': (0, 8, 8, 8),
    # 头饰 (覆盖层)
    'hat_front': (40, 8, 8, 8),
    'hat_back': (56, 8, 8, 8),
    'hat_top': (40, 0, 8, 8),
    'hat_bottom': (48, 0, 8, 8),
    'hat_left': (48, 8, 8, 8),
    'hat_right': (32, 8, 8, 8),
    # 身体
    'body_front': (20, 20, 8, 12),
    'body_back': (32, 20, 8, 12),
    'body_top': (20, 16, 8, 4),
    'body_bottom': (28, 16, 8, 4),
    'body_left': (28, 20, 4, 12),
    'body_right': (16, 20, 4, 12),
    # 身体覆盖层
    'jacket_front': (20, 36, 8, 12),
    'jacket_back': (32, 36, 8, 12),
    'jacket_top': (20, 32, 8, 4),
    'jacket_bottom': (28, 32, 8, 4),
    'jacket_left': (28, 36, 4, 12),
    'jacket_right': (16, 36, 4, 12),
    # 左臂
    'left_arm_front': (44, 52, 4, 12),
    'left_arm_back': (52, 52, 4, 12),
    'left_arm_top': (44, 48, 4, 4),
    'left_arm_bottom': (48, 48, 4, 4),
    'left_arm_left': (48, 52, 4, 12),
    'left_arm_right': (40, 52, 4, 12),
    # 左臂覆盖层
    'left_sleeve_front': (44, 68, 4, 12), # 实际上是 44, 68 -> 44, 36 in 1.8+
    'left_sleeve_back': (52, 68, 4, 12), # 52, 68 -> 52, 36
    'left_sleeve_top': (44, 64, 4, 4), # 44, 64 -> 44, 32
    'left_sleeve_bottom': (48, 64, 4, 4), # 48, 64 -> 48, 32
    'left_sleeve_left': (48, 68, 4, 12), # 48, 68 -> 48, 36
    'left_sleeve_right': (40, 68, 4, 12), # 40, 68 -> 40, 36
    # 右臂 (与左臂类似，但位置不同)
    'right_arm_front': (36, 52, 4, 12),
    'right_arm_back': (44, 52, 4, 12),
    'right_arm_top': (36, 48, 4, 4),
    'right_arm_bottom': (40, 48, 4, 4),
    'right_arm_left': (40, 52, 4, 12),
    'right_arm_right': (32, 52, 4, 12),
    # 右臂覆盖层
    'right_sleeve_front': (52, 52, 4, 12), # 52, 52 -> 52, 36
    'right_sleeve_back': (60, 52, 4, 12), # 60, 52 -> 60, 36
    'right_sleeve_top': (52, 48, 4, 4), # 52, 48 -> 52, 32
    'right_sleeve_bottom': (56, 48, 4, 4), # 56, 48 -> 56, 32
    'right_sleeve_left': (56, 52, 4, 12), # 56, 52 -> 56, 36
    'right_sleeve_right': (48, 52, 4, 12), # 48, 52 -> 48, 36
    # 左腿
    'left_leg_front': (4, 52, 4, 12),
    'left_leg_back': (12, 52, 4, 12),
    'left_leg_top': (4, 48, 4, 4),
    'left_leg_bottom': (8, 48, 4, 4),
    'left_leg_left': (8, 52, 4, 12),
    'left_leg_right': (0, 52, 4, 12),
    # 左腿覆盖层
    'left_pants_front': (4, 68, 4, 12), # 4, 68 -> 4, 36
    'left_pants_back': (12, 68, 4, 12), # 12, 68 -> 12, 36
    'left_pants_top': (4, 64, 4, 4), # 4, 64 -> 4, 32
    'left_pants_bottom': (8, 64, 4, 4), # 8, 64 -> 8, 32
    'left_pants_left': (8, 68, 4, 12), # 8, 68 -> 8, 36
    'left_pants_right': (0, 68, 4, 12), # 0, 68 -> 0, 36
    # 右腿
    'right_leg_front': (20, 52, 4, 12),
    'right_leg_back': (28, 52, 4, 12),
    'right_leg_top': (20, 48, 4, 4),
    'right_leg_bottom': (24, 48, 4, 4),
    'right_leg_left': (24, 52, 4, 12),
    'right_leg_right': (16, 52, 4, 12),
    # 右腿覆盖层
    'right_pants_front': (4, 36, 4, 12), # 4, 36 -> 20, 36
    'right_pants_back': (12, 36, 4, 12), # 12, 36 -> 28, 36
    'right_pants_top': (4, 32, 4, 4), # 4, 32 -> 20, 32
    'right_pants_bottom': (8, 32, 4, 4), # 8, 32 -> 24, 32
    'right_pants_left': (8, 36, 4, 12), # 8, 36 -> 24, 36
    'right_pants_right': (0, 36, 4, 12), # 0, 36 -> 16, 36
}

# 定义 128x128 皮肤各部位的坐标和尺寸 (x, y, width, height)
# 注意：128x128 布局与 64x64 类似，但所有坐标和尺寸都加倍
SKIN_LAYOUT_128 = {
    # 头
    'head_front': (16, 16, 16, 16),
    'head_back': (48, 16, 16, 16),
    'head_top': (16, 0, 16, 16),
    'head_bottom': (32, 0, 16, 16),
    'head_left': (32, 16, 16, 16),
    'head_right': (0, 16, 16, 16),
    # 头饰 (覆盖层)
    'hat_front': (80, 16, 16, 16),
    'hat_back': (112, 16, 16, 16),
    'hat_top': (80, 0, 16, 16),
    'hat_bottom': (96, 0, 16, 16),
    'hat_left': (96, 16, 16, 16),
    'hat_right': (64, 16, 16, 16),
    # 身体
    'body_front': (40, 40, 16, 24),
    'body_back': (64, 40, 16, 24),
    'body_top': (40, 32, 16, 8),
    'body_bottom': (56, 32, 16, 8),
    'body_left': (56, 40, 8, 24),
    'body_right': (32, 40, 8, 24),
    # 身体覆盖层
    'jacket_front': (40, 72, 16, 24),
    'jacket_back': (64, 72, 16, 24),
    'jacket_top': (40, 64, 16, 8),
    'jacket_bottom': (56, 64, 16, 8),
    'jacket_left': (56, 72, 8, 24),
    'jacket_right': (32, 72, 8, 24),
    # 左臂
    'left_arm_front': (88, 104, 8, 24),
    'left_arm_back': (104, 104, 8, 24),
    'left_arm_top': (88, 96, 8, 8),
    'left_arm_bottom': (96, 96, 8, 8),
    'left_arm_left': (96, 104, 8, 24),
    'left_arm_right': (80, 104, 8, 24),
    # 左臂覆盖层 (1.8+ layout)
    'left_sleeve_front': (88, 72, 8, 24),
    'left_sleeve_back': (104, 72, 8, 24),
    'left_sleeve_top': (88, 64, 8, 8),
    'left_sleeve_bottom': (96, 64, 8, 8),
    'left_sleeve_left': (96, 72, 8, 24),
    'left_sleeve_right': (80, 72, 8, 24),
    # 右臂
    'right_arm_front': (72, 104, 8, 24),
    'right_arm_back': (88, 104, 8, 24),
    'right_arm_top': (72, 96, 8, 8),
    'right_arm_bottom': (80, 96, 8, 8),
    'right_arm_left': (80, 104, 8, 24),
    'right_arm_right': (64, 104, 8, 24),
    # 右臂覆盖层 (1.8+ layout)
    'right_sleeve_front': (104, 104, 8, 24),
    'right_sleeve_back': (120, 104, 8, 24),
    'right_sleeve_top': (104, 96, 8, 8),
    'right_sleeve_bottom': (112, 96, 8, 8),
    'right_sleeve_left': (112, 104, 8, 24),
    'right_sleeve_right': (96, 104, 8, 24),
    # 左腿
    'left_leg_front': (8, 104, 8, 24),
    'left_leg_back': (24, 104, 8, 24),
    'left_leg_top': (8, 96, 8, 8),
    'left_leg_bottom': (16, 96, 8, 8),
    'left_leg_left': (16, 104, 8, 24),
    'left_leg_right': (0, 104, 8, 24),
    # 左腿覆盖层 (1.8+ layout)
    'left_pants_front': (8, 72, 8, 24),
    'left_pants_back': (24, 72, 8, 24),
    'left_pants_top': (8, 64, 8, 8),
    'left_pants_bottom': (16, 64, 8, 8),
    'left_pants_left': (16, 72, 8, 24),
    'left_pants_right': (0, 72, 8, 24),
    # 右腿
    'right_leg_front': (40, 104, 8, 24),
    'right_leg_back': (56, 104, 8, 24),
    'right_leg_top': (40, 96, 8, 8),
    'right_leg_bottom': (48, 96, 8, 8),
    'right_leg_left': (48, 104, 8, 24),
    'right_leg_right': (32, 104, 8, 24),
    # 右腿覆盖层 (1.8+ layout)
    'right_pants_front': (40, 72, 8, 24),
    'right_pants_back': (56, 72, 8, 24),
    'right_pants_top': (40, 64, 8, 8),
    'right_pants_bottom': (48, 64, 8, 8),
    'right_pants_left': (48, 72, 8, 24),
    'right_pants_right': (32, 72, 8, 24),
}

def image_to_data_url(image: Image.Image) -> str:
    """将 PIL Image 对象转换为 Base64 编码的 Data URL。"""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{img_str}"


def convert_image_to_skin(image: Image.Image, size: str, options: dict) -> Image.Image:
    """将输入的 PIL Image 对象转换为 Minecraft 皮肤 (PIL Image 对象)。

    Args:
        image: 输入的 PIL Image 对象。
        size: 目标皮肤尺寸 ('64' 或 '128')。
        options: 其他转换选项 (字典，当前未使用)。

    Returns:
        转换后的皮肤 PIL Image 对象。
    """

def convert_image_to_skin(image: Image.Image, size: str, options: dict) -> Image.Image:
    """将输入的 PIL Image 对象转换为 Minecraft 皮肤 (PIL Image 对象)。

    Args:
        image: 输入的 PIL Image 对象。
        size: 目标皮肤尺寸 ('64' 或 '128')。
        options: 其他转换选项 (字典，当前未使用)。

    Returns:
        转换后的皮肤 PIL Image 对象。
    """
    target_width = int(size)
    target_height = int(size)

    # 确保输入图像是 RGBA 格式
    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    # 创建一个透明的皮肤画布
    skin_image = Image.new('RGBA', (target_width, target_height), (0, 0, 0, 0))

    if target_width == 64 and target_height == 64:
        layout = SKIN_LAYOUT_64
        # --- 基础映射逻辑 --- 
        # 1. 调整输入图像大小以适应主要区域 (例如，头部正面)
        head_coords = layout['head_front']
        body_coords = layout['body_front']
        arm_coords = layout['right_arm_front'] # 使用右臂尺寸作为参考
        leg_coords = layout['right_leg_front'] # 使用右腿尺寸作为参考

        # 调整图像大小，使其宽度大致等于身体宽度，高度大致等于头+身体高度
        target_body_width = body_coords[2]
        target_head_body_height = head_coords[3] + body_coords[3]
        
        # 保持宽高比缩放
        input_w, input_h = image.size
        aspect_ratio = input_w / input_h
        
        scaled_h = target_head_body_height
        scaled_w = int(scaled_h * aspect_ratio)
        
        if scaled_w < target_body_width:
            scaled_w = target_body_width
            scaled_h = int(scaled_w / aspect_ratio)
            
        resized_input = image.resize((scaled_w, scaled_h), Image.Resampling.LANCZOS)
        ri_w, ri_h = resized_input.size

        # 2. 提取图像中心区域用于映射
        # 假设主要内容在中心，提取对应头和身体尺寸的区域
        center_x, center_y = ri_w // 2, ri_h // 2
        
        # 提取头部区域 (从缩放图中心向上)
        head_extract_h = head_coords[3]
        head_extract_w = head_coords[2]
        head_y_start = max(0, center_y - head_extract_h)
        head_x_start = max(0, center_x - head_extract_w // 2)
        head_crop_box = (head_x_start, head_y_start, head_x_start + head_extract_w, head_y_start + head_extract_h)
        head_part = resized_input.crop(head_crop_box)
        # 确保尺寸完全匹配
        if head_part.size != (head_coords[2], head_coords[3]):
             head_part = head_part.resize((head_coords[2], head_coords[3]), Image.Resampling.LANCZOS)

        # 提取身体区域 (从缩放图中心向下)
        body_extract_h = body_coords[3]
        body_extract_w = body_coords[2]
        body_y_start = min(ri_h - body_extract_h, center_y)
        body_x_start = max(0, center_x - body_extract_w // 2)
        body_crop_box = (body_x_start, body_y_start, body_x_start + body_extract_w, body_y_start + body_extract_h)
        body_part = resized_input.crop(body_crop_box)
        # 确保尺寸完全匹配
        if body_part.size != (body_coords[2], body_coords[3]):
            body_part = body_part.resize((body_coords[2], body_coords[3]), Image.Resampling.LANCZOS)
            
        # 3. 将提取的部分粘贴到皮肤画布的正面区域
        skin_image.paste(head_part, (head_coords[0], head_coords[1]))
        skin_image.paste(body_part, (body_coords[0], body_coords[1]))

        # 4. 尝试更智能地填充其他部分
        # 头部
        head_w, head_h = head_part.size
        head_back_part = head_part.transpose(Image.FLIP_LEFT_RIGHT) # 简单翻转作为背面
        head_left_part = head_part.crop((0, 0, 1, head_h)).resize((head_w, head_h), Image.Resampling.NEAREST) # 取左边一列像素拉伸
        head_right_part = head_part.crop((head_w - 1, 0, head_w, head_h)).resize((head_w, head_h), Image.Resampling.NEAREST) # 取右边一列像素拉伸
        head_top_part = head_part.crop((0, 0, head_w, 1)).resize((head_w, head_h), Image.Resampling.NEAREST) # 取顶部一行像素拉伸
        head_bottom_part = head_part.crop((0, head_h - 1, head_w, head_h)).resize((head_w, head_h), Image.Resampling.NEAREST) # 取底部一行像素拉伸

        skin_image.paste(head_back_part, layout['head_back'][:2])
        skin_image.paste(head_top_part, layout['head_top'][:2])
        skin_image.paste(head_bottom_part, layout['head_bottom'][:2])
        skin_image.paste(head_left_part, layout['head_left'][:2])
        skin_image.paste(head_right_part, layout['head_right'][:2])

        # 身体
        body_w, body_h = body_part.size
        body_back_part = body_part.transpose(Image.FLIP_LEFT_RIGHT)
        body_left_part = body_part.crop((0, 0, 1, body_h)).resize((body_w, body_h), Image.Resampling.NEAREST)
        body_right_part = body_part.crop((body_w - 1, 0, body_w, body_h)).resize((body_w, body_h), Image.Resampling.NEAREST)
        body_top_part = body_part.crop((0, 0, body_w, 1)).resize((body_w, body_h), Image.Resampling.NEAREST)
        body_bottom_part = body_part.crop((0, body_h - 1, body_w, body_h)).resize((body_w, body_h), Image.Resampling.NEAREST)

        skin_image.paste(body_back_part, layout['body_back'][:2])
        #身体顶部和底部通常不可见或被头/腿遮挡，先用平均色填充
        try:
            avg_body_color = tuple(map(int, body_part.resize((1, 1)).getpixel((0, 0))))
        except Exception:
            avg_body_color = (100, 100, 100, 255)
        fill_img_body_top = Image.new('RGBA', (layout['body_top'][2], layout['body_top'][3]), avg_body_color)
        fill_img_body_bottom = Image.new('RGBA', (layout['body_bottom'][2], layout['body_bottom'][3]), avg_body_color)
        skin_image.paste(fill_img_body_top, layout['body_top'][:2])
        skin_image.paste(fill_img_body_bottom, layout['body_bottom'][:2])
        # 粘贴身体左右侧
        # 注意：身体左右侧在模板上宽度可能与正面不同，需要调整尺寸
        body_left_coords = layout['body_left']
        body_right_coords = layout['body_right']
        skin_image.paste(body_left_part.resize((body_left_coords[2], body_left_coords[3]), Image.Resampling.NEAREST), body_left_coords[:2])
        skin_image.paste(body_right_part.resize((body_right_coords[2], body_right_coords[3]), Image.Resampling.NEAREST), body_right_coords[:2])

        # 5. 尝试更智能地填充四肢
        # 假设手臂颜色接近头部，腿部颜色接近身体
        try:
            avg_arm_color = tuple(map(int, head_part.resize((1, 1)).getpixel((0, 0))))
        except Exception:
            avg_arm_color = (128, 128, 128, 255)
        try:
            avg_leg_color = tuple(map(int, body_part.resize((1, 1)).getpixel((0, 0))))
        except Exception:
            avg_leg_color = (100, 100, 100, 255)

        # 创建手臂和腿部的基础图像 (使用平均色)
        # 尺寸参考
        rarm_coords = layout['right_arm_front']
        rleg_coords = layout['right_leg_front']
        arm_w, arm_h = rarm_coords[2], rarm_coords[3]
        leg_w, leg_h = rleg_coords[2], rleg_coords[3]

        # 创建一个临时的手臂正面图像 (用平均色填充)
        arm_front_part = Image.new('RGBA', (arm_w, arm_h), avg_arm_color)
        # 创建一个临时的腿部正面图像 (用平均色填充)
        leg_front_part = Image.new('RGBA', (leg_w, leg_h), avg_leg_color)

        # 应用与头部/身体类似的逻辑填充四肢的各个面
        limbs_to_process = {
            'arm': {'front': arm_front_part, 'layout_prefix': 'arm', 'coords': rarm_coords},
            'leg': {'front': leg_front_part, 'layout_prefix': 'leg', 'coords': rleg_coords}
        }

        for limb_type, data in limbs_to_process.items():
            front_part = data['front']
            prefix = data['layout_prefix']
            coords_ref = data['coords'] # 使用右侧作为尺寸参考
            limb_w, limb_h = coords_ref[2], coords_ref[3]

            back_part = front_part.transpose(Image.FLIP_LEFT_RIGHT)
            left_part = front_part.crop((0, 0, 1, limb_h)).resize((limb_w, limb_h), Image.Resampling.NEAREST)
            right_part = front_part.crop((limb_w - 1, 0, limb_w, limb_h)).resize((limb_w, limb_h), Image.Resampling.NEAREST)
            top_part = front_part.crop((0, 0, limb_w, 1)).resize((limb_w, limb_h), Image.Resampling.NEAREST)
            bottom_part = front_part.crop((0, limb_h - 1, limb_w, limb_h)).resize((limb_w, limb_h), Image.Resampling.NEAREST)

            for side in ['left', 'right']:
                limb_prefix = f'{side}_{prefix}' # e.g., 'left_arm', 'right_leg'
                # 粘贴正面 (用平均色填充的)
                front_coords = layout[f'{limb_prefix}_front']
                skin_image.paste(front_part.resize((front_coords[2], front_coords[3]), Image.Resampling.NEAREST), front_coords[:2])
                # 粘贴背面
                back_coords = layout[f'{limb_prefix}_back']
                skin_image.paste(back_part.resize((back_coords[2], back_coords[3]), Image.Resampling.NEAREST), back_coords[:2])
                # 粘贴顶部
                top_coords = layout[f'{limb_prefix}_top']
                skin_image.paste(top_part.resize((top_coords[2], top_coords[3]), Image.Resampling.NEAREST), top_coords[:2])
                # 粘贴底部
                bottom_coords = layout[f'{limb_prefix}_bottom']
                skin_image.paste(bottom_part.resize((bottom_coords[2], bottom_coords[3]), Image.Resampling.NEAREST), bottom_coords[:2])
                # 粘贴左侧
                left_coords = layout[f'{limb_prefix}_left']
                skin_image.paste(left_part.resize((left_coords[2], left_coords[3]), Image.Resampling.NEAREST), left_coords[:2])
                # 粘贴右侧
                right_coords = layout[f'{limb_prefix}_right']
                skin_image.paste(right_part.resize((right_coords[2], right_coords[3]), Image.Resampling.NEAREST), right_coords[:2])

        print("[Converter] Applied improved 64x64 mapping logic (including limbs).")
        # --- 改进映射逻辑结束 ---

    elif target_width == 128 and target_height == 128:
        layout = SKIN_LAYOUT_128
        # --- 基础映射逻辑 (128x128) --- 
        # 与 64x64 类似，但使用 128 布局和尺寸
        head_coords = layout['head_front']
        body_coords = layout['body_front']
        # arm_coords = layout['right_arm_front'] # 尺寸参考
        # leg_coords = layout['right_leg_front'] # 尺寸参考

        target_body_width = body_coords[2]
        target_head_body_height = head_coords[3] + body_coords[3]
        
        input_w, input_h = image.size
        aspect_ratio = input_w / input_h
        
        scaled_h = target_head_body_height
        scaled_w = int(scaled_h * aspect_ratio)
        
        if scaled_w < target_body_width:
            scaled_w = target_body_width
            scaled_h = int(scaled_w / aspect_ratio)
            
        # 使用更适合像素风格的缩放算法，例如 NEAREST，但 LANCZOS 在缩小大图时效果通常更好
        resized_input = image.resize((scaled_w, scaled_h), Image.Resampling.LANCZOS)
        ri_w, ri_h = resized_input.size

        center_x, center_y = ri_w // 2, ri_h // 2
        
        # 提取头部区域
        head_extract_h = head_coords[3]
        head_extract_w = head_coords[2]
        head_y_start = max(0, center_y - head_extract_h)
        head_x_start = max(0, center_x - head_extract_w // 2)
        head_crop_box = (head_x_start, head_y_start, head_x_start + head_extract_w, head_y_start + head_extract_h)
        head_part = resized_input.crop(head_crop_box)
        # 确保尺寸完全匹配，使用 NEAREST 保持像素感
        if head_part.size != (head_coords[2], head_coords[3]):
             head_part = head_part.resize((head_coords[2], head_coords[3]), Image.Resampling.NEAREST)

        # 提取身体区域
        body_extract_h = body_coords[3]
        body_extract_w = body_coords[2]
        body_y_start = min(ri_h - body_extract_h, center_y)
        body_x_start = max(0, center_x - body_extract_w // 2)
        body_crop_box = (body_x_start, body_y_start, body_x_start + body_extract_w, body_y_start + body_extract_h)
        body_part = resized_input.crop(body_crop_box)
        # 确保尺寸完全匹配，使用 NEAREST 保持像素感
        if body_part.size != (body_coords[2], body_coords[3]):
            body_part = body_part.resize((body_coords[2], body_coords[3]), Image.Resampling.NEAREST)
            
        # 粘贴正面部分
        skin_image.paste(head_part, (head_coords[0], head_coords[1]))
        skin_image.paste(body_part, (body_coords[0], body_coords[1]))

        # 4. 尝试更智能地填充其他部分 (128x128)
        # 头部
        head_w, head_h = head_part.size
        head_back_part = head_part.transpose(Image.FLIP_LEFT_RIGHT)
        head_left_part = head_part.crop((0, 0, 1, head_h)).resize((head_w, head_h), Image.Resampling.NEAREST)
        head_right_part = head_part.crop((head_w - 1, 0, head_w, head_h)).resize((head_w, head_h), Image.Resampling.NEAREST)
        head_top_part = head_part.crop((0, 0, head_w, 1)).resize((head_w, head_h), Image.Resampling.NEAREST)
        head_bottom_part = head_part.crop((0, head_h - 1, head_w, head_h)).resize((head_w, head_h), Image.Resampling.NEAREST)

        skin_image.paste(head_back_part, layout['head_back'][:2])
        skin_image.paste(head_top_part, layout['head_top'][:2])
        skin_image.paste(head_bottom_part, layout['head_bottom'][:2])
        skin_image.paste(head_left_part, layout['head_left'][:2])
        skin_image.paste(head_right_part, layout['head_right'][:2])

        # 身体
        body_w, body_h = body_part.size
        body_back_part = body_part.transpose(Image.FLIP_LEFT_RIGHT)
        body_left_part = body_part.crop((0, 0, 1, body_h)).resize((body_w, body_h), Image.Resampling.NEAREST)
        body_right_part = body_part.crop((body_w - 1, 0, body_w, body_h)).resize((body_w, body_h), Image.Resampling.NEAREST)
        #身体顶部和底部先用平均色填充
        try:
            avg_body_color = tuple(map(int, body_part.resize((1, 1), Image.Resampling.NEAREST).getpixel((0, 0))))
        except Exception:
            avg_body_color = (100, 100, 100, 255)
        fill_img_body_top = Image.new('RGBA', (layout['body_top'][2], layout['body_top'][3]), avg_body_color)
        fill_img_body_bottom = Image.new('RGBA', (layout['body_bottom'][2], layout['body_bottom'][3]), avg_body_color)
        skin_image.paste(fill_img_body_top, layout['body_top'][:2])
        skin_image.paste(fill_img_body_bottom, layout['body_bottom'][:2])
        # 粘贴身体左右侧 (需要调整尺寸)
        body_left_coords = layout['body_left']
        body_right_coords = layout['body_right']
        skin_image.paste(body_left_part.resize((body_left_coords[2], body_left_coords[3]), Image.Resampling.NEAREST), body_left_coords[:2])
        skin_image.paste(body_right_part.resize((body_right_coords[2], body_right_coords[3]), Image.Resampling.NEAREST), body_right_coords[:2])
        skin_image.paste(body_back_part, layout['body_back'][:2]) # 粘贴身体背面

        # 5. 尝试更智能地填充四肢 (128x128)
        # 假设手臂颜色接近头部，腿部颜色接近身体
        try:
            avg_arm_color = tuple(map(int, head_part.resize((1, 1), Image.Resampling.NEAREST).getpixel((0, 0))))
        except Exception:
            avg_arm_color = (128, 128, 128, 255)
        try:
            avg_leg_color = tuple(map(int, body_part.resize((1, 1), Image.Resampling.NEAREST).getpixel((0, 0))))
        except Exception:
            avg_leg_color = (100, 100, 100, 255)

        # 创建手臂和腿部的基础图像 (使用平均色)
        # 尺寸参考 (128x128)
        rarm_coords = layout['right_arm_front']
        rleg_coords = layout['right_leg_front']
        arm_w, arm_h = rarm_coords[2], rarm_coords[3]
        leg_w, leg_h = rleg_coords[2], rleg_coords[3]

        # 创建一个临时的手臂正面图像 (用平均色填充)
        arm_front_part = Image.new('RGBA', (arm_w, arm_h), avg_arm_color)
        # 创建一个临时的腿部正面图像 (用平均色填充)
        leg_front_part = Image.new('RGBA', (leg_w, leg_h), avg_leg_color)

        # 应用与头部/身体类似的逻辑填充四肢的各个面 (128x128)
        limbs_to_process_128 = {
            'arm': {'front': arm_front_part, 'layout_prefix': 'arm', 'coords': rarm_coords},
            'leg': {'front': leg_front_part, 'layout_prefix': 'leg', 'coords': rleg_coords}
        }

        for limb_type, data in limbs_to_process_128.items():
            front_part = data['front']
            prefix = data['layout_prefix']
            coords_ref = data['coords'] # 使用右侧作为尺寸参考
            limb_w, limb_h = coords_ref[2], coords_ref[3]

            back_part = front_part.transpose(Image.FLIP_LEFT_RIGHT)
            left_part = front_part.crop((0, 0, 1, limb_h)).resize((limb_w, limb_h), Image.Resampling.NEAREST)
            right_part = front_part.crop((limb_w - 1, 0, limb_w, limb_h)).resize((limb_w, limb_h), Image.Resampling.NEAREST)
            top_part = front_part.crop((0, 0, limb_w, 1)).resize((limb_w, limb_h), Image.Resampling.NEAREST)
            bottom_part = front_part.crop((0, limb_h - 1, limb_w, limb_h)).resize((limb_w, limb_h), Image.Resampling.NEAREST)

            for side in ['left', 'right']:
                limb_prefix = f'{side}_{prefix}' # e.g., 'left_arm', 'right_leg'
                # 粘贴正面 (用平均色填充的)
                front_coords = layout[f'{limb_prefix}_front']
                skin_image.paste(front_part.resize((front_coords[2], front_coords[3]), Image.Resampling.NEAREST), front_coords[:2])
                # 粘贴背面
                back_coords = layout[f'{limb_prefix}_back']
                skin_image.paste(back_part.resize((back_coords[2], back_coords[3]), Image.Resampling.NEAREST), back_coords[:2])
                # 粘贴顶部
                top_coords = layout[f'{limb_prefix}_top']
                skin_image.paste(top_part.resize((top_coords[2], top_coords[3]), Image.Resampling.NEAREST), top_coords[:2])
                # 粘贴底部
                bottom_coords = layout[f'{limb_prefix}_bottom']
                skin_image.paste(bottom_part.resize((bottom_coords[2], bottom_coords[3]), Image.Resampling.NEAREST), bottom_coords[:2])
                # 粘贴左侧
                left_coords = layout[f'{limb_prefix}_left']
                skin_image.paste(left_part.resize((left_coords[2], left_coords[3]), Image.Resampling.NEAREST), left_coords[:2])
                # 粘贴右侧
                right_coords = layout[f'{limb_prefix}_right']
                skin_image.paste(right_part.resize((right_coords[2], right_coords[3]), Image.Resampling.NEAREST), right_coords[:2])

        print("[Converter] Applied improved 128x128 mapping logic (including limbs).")
        # --- 改进映射逻辑结束 --- 

    else:
        raise ValueError("Unsupported skin size. Only '64' and '128' are supported.")

    print(f"[Converter] Generated {target_width}x{target_height} skin canvas.")
    return skin_image

# image_to_data_url 函数已在上面添加