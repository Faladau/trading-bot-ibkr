"""
Config Loader - Încărcare configurație din YAML și variabile de mediu
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional
import yaml
from dotenv import load_dotenv


class ConfigLoader:
    """Încarcă configurație din fișiere YAML și variabile de mediu (.env)"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Inițializează config loader
        
        Args:
            config_dir: Directorul cu fișierele de config (default: config/)
        """
        if config_dir is None:
            # Caută config/ relativ la root-ul proiectului
            project_root = Path(__file__).parent.parent.parent
            config_dir = project_root / "config"
        
        self.config_dir = Path(config_dir)
        self._config: Dict[str, Any] = {}
        
        # Încarcă variabilele de mediu din .env
        env_file = self.config_dir.parent / ".env"
        if env_file.exists():
            load_dotenv(env_file)
    
    def load_config(self, filename: str = "config.yaml") -> Dict[str, Any]:
        """
        Încarcă configurația dintr-un fișier YAML
        
        Args:
            filename: Numele fișierului de config (default: config.yaml)
            
        Returns:
            Dict cu configurația
            
        Raises:
            FileNotFoundError: Dacă fișierul nu există
            yaml.YAMLError: Dacă fișierul YAML este invalid
        """
        config_path = self.config_dir / filename
        
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}
        
        # Suprascrie cu variabile de mediu dacă există
        config = self._override_with_env(config)
        
        self._config = config
        return config
    
    def load_multiple(self, *filenames: str) -> Dict[str, Any]:
        """
        Încarcă mai multe fișiere de config și le combină
        
        Args:
            *filenames: Numele fișierelor de config
            
        Returns:
            Dict combinat cu toate configurările
        """
        combined = {}
        
        for filename in filenames:
            config = self.load_config(filename)
            combined = self._deep_merge(combined, config)
        
        return combined
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Obține o valoare din config folosind dot notation
        
        Args:
            key: Cheia în format "section.subsection.key"
            default: Valoarea default dacă cheia nu există
            
        Returns:
            Valoarea sau default
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def _override_with_env(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Suprascrie valori din config cu variabile de mediu
        
        Variabilele de mediu trebuie să fie în format: SECTION_SUBSECTION_KEY
        Ex: IBKR_HOST, IBKR_PORT, RISK_CAPITAL_INITIAL
        """
        # IBKR settings
        if 'ibkr' in config:
            config['ibkr']['host'] = os.getenv('IBKR_HOST', config['ibkr'].get('host', '127.0.0.1'))
            config['ibkr']['port'] = int(os.getenv('IBKR_PORT', config['ibkr'].get('port', 7497)))
            config['ibkr']['clientId'] = int(os.getenv('IBKR_CLIENT_ID', config['ibkr'].get('clientId', 1)))
            config['ibkr']['paper'] = os.getenv('PAPER_TRADING', str(config['ibkr'].get('paper', True))).lower() == 'true'
        
        # Risk settings
        if 'risk' in config:
            capital = os.getenv('INITIAL_CAPITAL')
            if capital:
                config['risk']['capital_initial'] = float(capital)
        
        return config
    
    def _deep_merge(self, base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
        """
        Combină două dict-uri recursiv (deep merge)
        
        Args:
            base: Dict-ul de bază
            update: Dict-ul cu actualizări
            
        Returns:
            Dict combinat
        """
        result = base.copy()
        
        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result


def load_config(config_dir: Optional[Path] = None, filename: str = "config.yaml") -> Dict[str, Any]:
    """
    Funcție helper pentru încărcare rapidă de config
    
    Args:
        config_dir: Directorul cu fișierele de config
        filename: Numele fișierului de config
        
    Returns:
        Dict cu configurația
    """
    loader = ConfigLoader(config_dir)
    return loader.load_config(filename)
