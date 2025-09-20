"""
Gerenciador Centralizado de Banco de Dados
Conexões unificadas para todos os bancos de dados do sistema
"""
import sqlite3
import os
import threading
from datetime import datetime
from typing import Optional, Dict, Any
from contextlib import contextmanager

class DatabaseManager:
    """Gerenciador centralizado de todas as conexões de banco"""
    
    def __init__(self, base_dir: Optional[str] = None):
        if base_dir is None:
            self.base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'memoria')
        else:
            self.base_dir = base_dir
        
        # Garantir que diretório existe
        os.makedirs(self.base_dir, exist_ok=True)
        
        # Pool de conexões thread-safe
        self._connections = {}
        self._lock = threading.Lock()
        
        # Configurações de banco
        self.db_config = {
            'timeout': 30.0,
            'check_same_thread': False,
            'isolation_level': None  # autocommit mode
        }
        
        # Mapping de bancos disponíveis
        self.databases = {
            'users': 'user_profiles.db',
            'emotions': 'emotions.db', 
            'memory': 'eron_memory.db',
            'knowledge': 'knowledge.db',
            'preferences': 'preferences.db',
            'sensitive': 'sensitive_memory.db',
            'fast_learning': 'fast_learning.db',
            'feedback_system': 'feedback_system.db',
            'adaptation_system': 'adaptation_system.db',
            'pattern_recognition': 'pattern_recognition.db',
            'response_optimizer': 'response_optimizer.db'
        }
    
    def get_connection(self, db_name: str) -> sqlite3.Connection:
        """Obter conexão para banco específico"""
        if db_name not in self.databases:
            raise ValueError(f"Banco de dados '{db_name}' não encontrado")
        
        thread_id = threading.get_ident()
        connection_key = f"{db_name}_{thread_id}"
        
        with self._lock:
            if connection_key not in self._connections:
                db_path = os.path.join(self.base_dir, self.databases[db_name])
                conn = sqlite3.connect(db_path, **self.db_config)
                
                # Configurações de otimização
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("PRAGMA synchronous=NORMAL") 
                conn.execute("PRAGMA cache_size=10000")
                conn.execute("PRAGMA temp_store=MEMORY")
                
                self._connections[connection_key] = conn
            
            return self._connections[connection_key]
    
    @contextmanager
    def transaction(self, db_name: str):
        """Context manager para transações"""
        conn = self.get_connection(db_name)
        try:
            conn.execute("BEGIN")
            yield conn
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise
    
    def execute_query(self, db_name: str, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Executar query em banco específico"""
        conn = self.get_connection(db_name)
        return conn.execute(query, params)
    
    def fetch_one(self, db_name: str, query: str, params: tuple = ()) -> Optional[tuple]:
        """Buscar um registro"""
        cursor = self.execute_query(db_name, query, params)
        return cursor.fetchone()
    
    def fetch_all(self, db_name: str, query: str, params: tuple = ()) -> list:
        """Buscar todos os registros"""
        cursor = self.execute_query(db_name, query, params)
        return cursor.fetchall()
    
    def execute_many(self, db_name: str, query: str, params_list: list) -> sqlite3.Cursor:
        """Executar query múltipla"""
        conn = self.get_connection(db_name)
        return conn.executemany(query, params_list)
    
    def create_tables_for_db(self, db_name: str, table_definitions: Dict[str, str]):
        """Criar tabelas para um banco específico"""
        conn = self.get_connection(db_name)
        with self.transaction(db_name):
            for table_name, table_sql in table_definitions.items():
                conn.execute(table_sql)
    
    def backup_database(self, db_name: str, backup_path: Optional[str] = None) -> str:
        """Fazer backup de banco específico"""
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(
                self.base_dir, 
                f"backup_{db_name}_{timestamp}.db"
            )
        
        source_conn = self.get_connection(db_name)
        backup_conn = sqlite3.connect(backup_path)
        
        try:
            source_conn.backup(backup_conn)
            return backup_path
        finally:
            backup_conn.close()
    
    def optimize_database(self, db_name: str):
        """Otimizar banco específico"""
        conn = self.get_connection(db_name)
        conn.execute("VACUUM")
        conn.execute("ANALYZE")
    
    def get_database_info(self, db_name: str) -> Dict[str, Any]:
        """Obter informações sobre banco"""
        conn = self.get_connection(db_name)
        
        # Tamanho do arquivo
        db_path = os.path.join(self.base_dir, self.databases[db_name])
        file_size = os.path.getsize(db_path) if os.path.exists(db_path) else 0
        
        # Número de tabelas
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        
        # Informações do esquema
        schema_info = {}
        for table in tables:
            table_name = table[0]
            columns = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
            row_count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            
            schema_info[table_name] = {
                'columns': len(columns),
                'rows': row_count,
                'column_details': columns
            }
        
        return {
            'database': db_name,
            'file_path': db_path,
            'file_size_bytes': file_size,
            'tables_count': len(tables),
            'tables_info': schema_info
        }
    
    def close_all_connections(self):
        """Fechar todas as conexões"""
        with self._lock:
            for conn in self._connections.values():
                conn.close()
            self._connections.clear()
    
    def health_check(self) -> Dict[str, Any]:
        """Verificar saúde de todos os bancos"""
        health_status = {
            'overall_status': 'healthy',
            'databases': {},
            'checked_at': datetime.now().isoformat()
        }
        
        for db_name in self.databases.keys():
            try:
                # Teste básico de conexão
                conn = self.get_connection(db_name)
                conn.execute("SELECT 1").fetchone()
                
                # Informações básicas
                info = self.get_database_info(db_name)
                
                health_status['databases'][db_name] = {
                    'status': 'healthy',
                    'file_size': info['file_size_bytes'],
                    'tables_count': info['tables_count']
                }
                
            except Exception as e:
                health_status['databases'][db_name] = {
                    'status': 'error',
                    'error': str(e)
                }
                health_status['overall_status'] = 'degraded'
        
        return health_status

# Instância global do gerenciador
_db_manager = None

def get_db_manager() -> DatabaseManager:
    """Obter instância global do gerenciador de banco"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager

def get_db_connection(db_name: str) -> sqlite3.Connection:
    """Função de conveniência para obter conexão"""
    return get_db_manager().get_connection(db_name)

# Funções de conveniência para operações comuns
def execute_query(db_name: str, query: str, params: tuple = ()) -> sqlite3.Cursor:
    """Executar query com gerenciador global"""
    return get_db_manager().execute_query(db_name, query, params)

def fetch_one(db_name: str, query: str, params: tuple = ()) -> Optional[tuple]:
    """Buscar um registro com gerenciador global"""
    return get_db_manager().fetch_one(db_name, query, params)

def fetch_all(db_name: str, query: str, params: tuple = ()) -> list:
    """Buscar todos os registros com gerenciador global"""
    return get_db_manager().fetch_all(db_name, query, params)