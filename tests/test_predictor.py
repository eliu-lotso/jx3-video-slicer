import os
import sys
import pytest
import tempfile

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from predictor import CLASS_NAMES, load_model_timm, predict_labels

def test_class_names():
    """测试类别名称"""
    assert CLASS_NAMES is not None
    assert isinstance(CLASS_NAMES, list)
    assert len(CLASS_NAMES) == 3
    assert "loading" in CLASS_NAMES
    assert "map" in CLASS_NAMES
    assert "other" in CLASS_NAMES

def test_load_model_timm_invalid_model():
    """测试加载无效模型"""
    with tempfile.TemporaryDirectory() as temp_dir:
        fake_model_path = os.path.join(temp_dir, "fake_model.pth")
        
        # 应该抛出异常
        with pytest.raises(Exception):
            load_model_timm("invalid_model", fake_model_path, "cpu")

def test_predict_labels_empty_directory():
    """测试空目录的预测"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # 空目录应该返回空列表
        labels = predict_labels(temp_dir, batch_size=64, progress=False)
        assert isinstance(labels, list)
        assert len(labels) == 0

def test_predict_labels_invalid_directory():
    """测试无效目录的预测"""
    non_existent_dir = "/non/existent/directory"
    
    # 应该抛出异常
    with pytest.raises(Exception):
        predict_labels(non_existent_dir, batch_size=64, progress=False) 