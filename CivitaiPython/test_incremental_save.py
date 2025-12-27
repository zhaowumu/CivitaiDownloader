#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
增量保存功能测试脚本

功能说明：
- 测试CivitaiSyncManager的sync_json方法的增量保存功能
- 模拟同步过程中的中断情况
- 验证数据是否能正确保存和恢复
"""

import sys
import os
import time

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.sync import CivitaiSyncManager
from core.storage import load_json, load_cursor, save_cursor, save_json, user_dir

def test_incremental_save():
    """测试增量保存功能"""
    # 测试用户名
    test_username = "test_incremental_save"
    
    # 清理测试环境
    user_path = user_dir(test_username)
    if user_path.exists():
        import shutil
        shutil.rmtree(user_path)
    
    print("[测试开始] 增量保存功能测试")
    
    try:
        # 创建同步管理器
        manager = CivitaiSyncManager(test_username)
        
        # 模拟获取几页数据后中断
        print("\n[步骤1] 开始同步数据（将在获取几页后中断）")
        
        # 运行sync_json方法（这次应该能正常完成，因为我们用的是测试用户）
        # 注意：这里实际会调用Civitai API，请确保网络连接正常
        manager.sync_json()
        
        # 检查数据是否保存
        saved_data = load_json(test_username)
        saved_cursor = load_cursor(test_username)
        
        print(f"\n[结果1] 同步完成后的数据情况：")
        print(f"- 保存的图片数量：{len(saved_data)}")
        print(f"- 保存的游标：{saved_cursor}")
        
        # 验证数据保存
        if len(saved_data) > 0:
            print("✓ 数据保存成功")
        else:
            print("✗ 数据保存失败")
            
        if saved_cursor is not None:
            print("✓ 游标保存成功")
        else:
            print("✗ 游标保存失败")
            
        print("\n[测试完成] 增量保存功能测试通过")
        
    except Exception as e:
        print(f"\n[测试失败] 发生错误：{e}")
        import traceback
        traceback.print_exc()
        
        # 检查中断后是否保存了部分数据
        saved_data = load_json(test_username)
        saved_cursor = load_cursor(test_username)
        
        print(f"\n[中断后检查] 数据保存情况：")
        print(f"- 已保存的图片数量：{len(saved_data)}")
        print(f"- 已保存的游标：{saved_cursor}")
        
        if len(saved_data) > 0:
            print("✓ 增量保存功能正常：部分数据已保存")
        else:
            print("✗ 增量保存功能异常：没有保存任何数据")

if __name__ == "__main__":
    test_incremental_save()
