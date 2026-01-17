"""
Teste pentru config_loader
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from src.common.utils.config_loader import ConfigLoader, load_config


class TestConfigLoader:
    """Teste pentru ConfigLoader"""
    
    def test_load_config_success(self):
        """Test încărcare config valid"""
        # Creează un fișier YAML temporar
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "test_config.yaml"
            config_data = {
                "app": {"mode": "paper", "debug": True},
                "ibkr": {"host": "127.0.0.1", "port": 7497}
            }
            
            with open(config_path, 'w') as f:
                yaml.dump(config_data, f)
            
            # Testează încărcarea
            loader = ConfigLoader(config_dir=Path(tmpdir))
            config = loader.load_config("test_config.yaml")
            
            assert config["app"]["mode"] == "paper"
            assert config["app"]["debug"] is True
            assert config["ibkr"]["host"] == "127.0.0.1"
            assert config["ibkr"]["port"] == 7497
    
    def test_load_config_file_not_found(self):
        """Test eroare când fișierul nu există"""
        with tempfile.TemporaryDirectory() as tmpdir:
            loader = ConfigLoader(config_dir=Path(tmpdir))
            
            with pytest.raises(FileNotFoundError):
                loader.load_config("nonexistent.yaml")
    
    def test_get_with_dot_notation(self):
        """Test obținere valoare cu dot notation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "test_config.yaml"
            config_data = {
                "app": {"mode": "paper"},
                "ibkr": {"host": "127.0.0.1", "port": 7497}
            }
            
            with open(config_path, 'w') as f:
                yaml.dump(config_data, f)
            
            loader = ConfigLoader(config_dir=Path(tmpdir))
            loader.load_config("test_config.yaml")
            
            assert loader.get("app.mode") == "paper"
            assert loader.get("ibkr.host") == "127.0.0.1"
            assert loader.get("ibkr.port") == 7497
            assert loader.get("nonexistent.key", "default") == "default"
    
    def test_load_multiple_configs(self):
        """Test încărcare și combinare mai multe fișiere"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Config 1
            config1_path = Path(tmpdir) / "config1.yaml"
            with open(config1_path, 'w') as f:
                yaml.dump({"app": {"mode": "paper"}, "ibkr": {"host": "127.0.0.1"}}, f)
            
            # Config 2
            config2_path = Path(tmpdir) / "config2.yaml"
            with open(config2_path, 'w') as f:
                yaml.dump({"ibkr": {"port": 7497}, "risk": {"capital": 500}}, f)
            
            loader = ConfigLoader(config_dir=Path(tmpdir))
            combined = loader.load_multiple("config1.yaml", "config2.yaml")
            
            assert combined["app"]["mode"] == "paper"
            assert combined["ibkr"]["host"] == "127.0.0.1"
            assert combined["ibkr"]["port"] == 7497
            assert combined["risk"]["capital"] == 500
    
    def test_helper_function_load_config(self):
        """Test funcția helper load_config"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "test_config.yaml"
            config_data = {"app": {"mode": "paper"}}
            
            with open(config_path, 'w') as f:
                yaml.dump(config_data, f)
            
            config = load_config(config_dir=Path(tmpdir), filename="test_config.yaml")
            assert config["app"]["mode"] == "paper"
