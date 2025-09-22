"""
Utilitário de Gerenciamento de Logs - Eron.IA
=============================================

Ferramenta de linha de comando para gerenciar e analisar logs do sistema.

Funcionalidades:
- Visualizar logs em tempo real
- Filtrar logs por categoria, nível ou período
- Limpar logs antigos
- Analisar estatísticas de logs
- Rotacionar logs manualmente

Uso:
python tools/log_manager.py --help

Autor: Eron.IA System
Data: 2024
"""

import argparse
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import json
import re
from collections import Counter, defaultdict

# Adicionar diretório pai para imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from core.config import config
    from src.logging_system import logger_system, LogCategory
except ImportError as e:
    print(f"❌ Erro ao importar configurações: {e}")
    sys.exit(1)


class LogManager:
    """Gerenciador de logs do Eron.IA"""
    
    def __init__(self):
        self.log_dir = Path(config.logging['dir'])
        self.ensure_log_dir()
    
    def ensure_log_dir(self):
        """Garante que o diretório de logs existe"""
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def list_log_files(self):
        """Lista todos os arquivos de log disponíveis"""
        if not self.log_dir.exists():
            return []
        
        log_files = []
        for file_path in self.log_dir.glob("*.log*"):
            stat = file_path.stat()
            log_files.append({
                'name': file_path.name,
                'path': file_path,
                'size_mb': stat.st_size / (1024 * 1024),
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'lines': self._count_lines(file_path)
            })
        
        return sorted(log_files, key=lambda x: x['modified'], reverse=True)
    
    def _count_lines(self, file_path):
        """Conta linhas em um arquivo de log"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return sum(1 for _ in f)
        except:
            return 0
    
    def show_status(self):
        """Mostra status do sistema de logs"""
        print("📊 STATUS DO SISTEMA DE LOGGING")
        print("=" * 50)
        
        log_files = self.list_log_files()
        
        if not log_files:
            print("⚠️ Nenhum arquivo de log encontrado")
            return
        
        total_size = sum(f['size_mb'] for f in log_files)
        total_lines = sum(f['lines'] for f in log_files)
        
        print(f"📁 Diretório de logs: {self.log_dir}")
        print(f"📄 Total de arquivos: {len(log_files)}")
        print(f"💾 Tamanho total: {total_size:.2f} MB")
        print(f"📝 Total de linhas: {total_lines:,}")
        print()
        
        print("📋 ARQUIVOS DE LOG:")
        print("-" * 50)
        
        for log_file in log_files:
            print(f"• {log_file['name']}")
            print(f"  Tamanho: {log_file['size_mb']:.2f} MB")
            print(f"  Linhas: {log_file['lines']:,}")
            print(f"  Modificado: {log_file['modified']}")
            print()
    
    def tail_logs(self, file_pattern="general", lines=20, follow=False):
        """Mostra as últimas linhas dos logs"""
        
        # Encontrar arquivo de log
        log_file = None
        for file_info in self.list_log_files():
            if file_pattern in file_info['name']:
                log_file = file_info['path']
                break
        
        if not log_file:
            print(f"❌ Arquivo de log com padrão '{file_pattern}' não encontrado")
            return
        
        print(f"📜 ÚLTIMAS {lines} LINHAS: {log_file.name}")
        print("=" * 60)
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                
                # Pegar últimas linhas
                last_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                
                for line in last_lines:
                    line = line.rstrip()
                    if line:
                        # Colorir por nível de log
                        if 'ERROR' in line or 'CRITICAL' in line:
                            print(f"🔴 {line}")
                        elif 'WARNING' in line:
                            print(f"🟡 {line}")
                        elif 'INFO' in line:
                            print(f"🔵 {line}")
                        else:
                            print(f"⚪ {line}")
                    
                if follow:
                    print("\\n👀 Monitorando arquivo... (Ctrl+C para sair)")
                    try:
                        f.seek(0, 2)  # Ir para o final
                        while True:
                            line = f.readline()
                            if line:
                                line = line.rstrip()
                                if 'ERROR' in line or 'CRITICAL' in line:
                                    print(f"🔴 {line}")
                                elif 'WARNING' in line:
                                    print(f"🟡 {line}")
                                else:
                                    print(f"🔵 {line}")
                            else:
                                import time
                                time.sleep(1)
                    except KeyboardInterrupt:
                        print("\\n✅ Monitoramento interrompido")
        
        except Exception as e:
            print(f"❌ Erro ao ler arquivo: {e}")
    
    def filter_logs(self, category=None, level=None, since=None, pattern=None):
        """Filtra logs baseado em critérios"""
        
        print("🔍 FILTRAR LOGS")
        print("=" * 50)
        
        # Parâmetros de filtro
        filters = []
        if category:
            filters.append(f"Categoria: {category}")
        if level:
            filters.append(f"Nível: {level}")
        if since:
            filters.append(f"Desde: {since}")
        if pattern:
            filters.append(f"Padrão: {pattern}")
        
        print(f"Filtros aplicados: {', '.join(filters) if filters else 'Nenhum'}")
        print()
        
        # Processar logs
        for log_file in self.list_log_files():
            if log_file['name'].endswith('.log'):
                matches = self._filter_file(
                    log_file['path'], 
                    category, 
                    level, 
                    since, 
                    pattern
                )
                
                if matches:
                    print(f"📄 {log_file['name']} ({len(matches)} matches):")
                    for match in matches[-10:]:  # Últimos 10 matches
                        print(f"  {match}")
                    print()
    
    def _filter_file(self, file_path, category, level, since, pattern):
        """Filtra um arquivo específico"""
        matches = []
        since_dt = None
        
        if since:
            try:
                if 'h' in since:
                    hours = int(since.replace('h', ''))
                    since_dt = datetime.now() - timedelta(hours=hours)
                elif 'd' in since:
                    days = int(since.replace('d', ''))
                    since_dt = datetime.now() - timedelta(days=days)
            except:
                pass
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Filtro de categoria
                    if category and f"[{category}" not in line:
                        continue
                    
                    # Filtro de nível
                    if level and level.upper() not in line:
                        continue
                    
                    # Filtro de tempo
                    if since_dt:
                        timestamp_match = re.search(r'\\[(\\d{4}-\\d{2}-\\d{2}T[\\d\\.:]+)\\]', line)
                        if timestamp_match:
                            try:
                                log_dt = datetime.fromisoformat(timestamp_match.group(1))
                                if log_dt < since_dt:
                                    continue
                            except:
                                pass
                    
                    # Filtro de padrão
                    if pattern and pattern.lower() not in line.lower():
                        continue
                    
                    matches.append(line)
        
        except Exception as e:
            print(f"⚠️ Erro ao processar {file_path}: {e}")
        
        return matches
    
    def analyze_stats(self, days_back=7):
        """Analisa estatísticas dos logs"""
        print(f"📈 ANÁLISE DOS ÚLTIMOS {days_back} DIAS")
        print("=" * 50)
        
        stats = {
            'levels': Counter(),
            'categories': Counter(),
            'hourly': defaultdict(int),
            'daily': defaultdict(int),
            'errors': [],
            'performance': []
        }
        
        since_dt = datetime.now() - timedelta(days=days_back)
        
        # Analisar todos os arquivos de log
        for log_file in self.list_log_files():
            if log_file['name'].endswith('.log'):
                self._analyze_file(log_file['path'], stats, since_dt)
        
        # Mostrar estatísticas
        self._display_stats(stats)
    
    def _analyze_file(self, file_path, stats, since_dt):
        """Analisa um arquivo específico"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Extrair timestamp
                    timestamp_match = re.search(r'\\[(\\d{4}-\\d{2}-\\d{2}T[\\d\\.:]+)\\]', line)
                    if not timestamp_match:
                        continue
                    
                    try:
                        log_dt = datetime.fromisoformat(timestamp_match.group(1))
                        if log_dt < since_dt:
                            continue
                    except:
                        continue
                    
                    # Extrair nível
                    level_match = re.search(r'\\] (\\w+)\\s+\\[', line)
                    if level_match:
                        level = level_match.group(1)
                        stats['levels'][level] += 1
                    
                    # Extrair categoria
                    category_match = re.search(r'\\[([\\w_]+)\\s*\\]', line)
                    if category_match:
                        category = category_match.group(1).strip()
                        stats['categories'][category] += 1
                    
                    # Estatísticas horárias
                    hour_key = log_dt.strftime('%H')
                    stats['hourly'][hour_key] += 1
                    
                    # Estatísticas diárias
                    day_key = log_dt.strftime('%Y-%m-%d')
                    stats['daily'][day_key] += 1
                    
                    # Coletar erros
                    if 'ERROR' in line or 'CRITICAL' in line:
                        stats['errors'].append({
                            'timestamp': log_dt,
                            'message': line
                        })
                    
                    # Coletar métricas de performance
                    if 'PERFORMANCE:' in line:
                        perf_match = re.search(r'executado em ([\\d.]+)ms', line)
                        if perf_match:
                            exec_time = float(perf_match.group(1))
                            stats['performance'].append({
                                'timestamp': log_dt,
                                'time_ms': exec_time,
                                'operation': line
                            })
        
        except Exception as e:
            print(f"⚠️ Erro ao analisar {file_path}: {e}")
    
    def _display_stats(self, stats):
        """Exibe estatísticas analisadas"""
        
        # Níveis de log
        print("📊 DISTRIBUIÇÃO POR NÍVEL:")
        for level, count in stats['levels'].most_common():
            print(f"  {level}: {count:,}")
        print()
        
        # Categorias
        print("🏷️ DISTRIBUIÇÃO POR CATEGORIA:")
        for category, count in stats['categories'].most_common():
            print(f"  {category}: {count:,}")
        print()
        
        # Erros recentes
        if stats['errors']:
            print(f"❌ ÚLTIMOS {min(5, len(stats['errors']))} ERROS:")
            for error in sorted(stats['errors'], key=lambda x: x['timestamp'], reverse=True)[:5]:
                print(f"  {error['timestamp']} - {error['message'][:100]}...")
            print()
        
        # Performance
        if stats['performance']:
            perf_times = [p['time_ms'] for p in stats['performance']]
            avg_time = sum(perf_times) / len(perf_times)
            max_time = max(perf_times)
            
            print("⚡ MÉTRICAS DE PERFORMANCE:")
            print(f"  Operações monitoradas: {len(stats['performance']):,}")
            print(f"  Tempo médio: {avg_time:.2f}ms")
            print(f"  Tempo máximo: {max_time:.2f}ms")
            
            # Operação mais lenta
            slowest = max(stats['performance'], key=lambda x: x['time_ms'])
            print(f"  Operação mais lenta: {slowest['time_ms']:.2f}ms")
            print()
    
    def cleanup_old_logs(self, days=None):
        """Remove logs antigos"""
        days = days or config.logging['max_age_days']
        
        print(f"🧹 LIMPEZA DE LOGS ANTIGOS (>{days} dias)")
        print("=" * 50)
        
        cutoff_date = datetime.now() - timedelta(days=days)
        removed_count = 0
        removed_size = 0
        
        for log_file in self.list_log_files():
            if log_file['modified'] < cutoff_date:
                try:
                    size_mb = log_file['size_mb']
                    log_file['path'].unlink()
                    print(f"✅ Removido: {log_file['name']} ({size_mb:.2f} MB)")
                    removed_count += 1
                    removed_size += size_mb
                except Exception as e:
                    print(f"❌ Erro ao remover {log_file['name']}: {e}")
        
        if removed_count == 0:
            print("✅ Nenhum arquivo antigo encontrado")
        else:
            print(f"\\n🗑️ Removidos {removed_count} arquivos ({removed_size:.2f} MB)")
    
    def rotate_logs(self):
        """Força rotação manual dos logs"""
        print("🔄 ROTAÇÃO MANUAL DE LOGS")
        print("=" * 50)
        
        logger_system.cleanup_old_logs()
        print("✅ Rotação de logs concluída!")


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="Gerenciador de Logs do Eron.IA",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  %(prog)s --status                    # Mostra status dos logs
  %(prog)s --tail general             # Últimas 20 linhas do log geral
  %(prog)s --tail telegram --lines 50 # Últimas 50 linhas do Telegram
  %(prog)s --follow general           # Monitora log em tempo real
  %(prog)s --filter --level ERROR     # Filtra apenas erros
  %(prog)s --filter --category telegram --since 2h  # Telegram últimas 2h
  %(prog)s --stats                    # Análise estatística
  %(prog)s --cleanup                  # Remove logs antigos
  %(prog)s --rotate                   # Força rotação
        """
    )
    
    parser.add_argument('--status', action='store_true', 
                       help='Mostra status do sistema de logs')
    
    parser.add_argument('--tail', metavar='PATTERN',
                       help='Mostra últimas linhas de um log')
    
    parser.add_argument('--lines', type=int, default=20,
                       help='Número de linhas para --tail (padrão: 20)')
    
    parser.add_argument('--follow', metavar='PATTERN',
                       help='Monitora log em tempo real')
    
    parser.add_argument('--filter', action='store_true',
                       help='Filtra logs baseado em critérios')
    
    parser.add_argument('--category', metavar='CAT',
                       help='Filtrar por categoria')
    
    parser.add_argument('--level', metavar='LEVEL',
                       help='Filtrar por nível (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
    
    parser.add_argument('--since', metavar='TIME',
                       help='Filtrar desde tempo (ex: 2h, 1d)')
    
    parser.add_argument('--pattern', metavar='TEXT',
                       help='Filtrar por padrão de texto')
    
    parser.add_argument('--stats', action='store_true',
                       help='Mostra análise estatística dos logs')
    
    parser.add_argument('--days', type=int, default=7,
                       help='Dias para análise estatística (padrão: 7)')
    
    parser.add_argument('--cleanup', action='store_true',
                       help='Remove logs antigos')
    
    parser.add_argument('--rotate', action='store_true',
                       help='Força rotação dos logs')
    
    args = parser.parse_args()
    
    # Se nenhum argumento, mostra ajuda
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    # Inicializar gerenciador
    manager = LogManager()
    
    # Executar ações baseadas nos argumentos
    if args.status:
        manager.show_status()
    
    elif args.tail:
        manager.tail_logs(args.tail, args.lines, False)
    
    elif args.follow:
        manager.tail_logs(args.follow, args.lines, True)
    
    elif args.filter:
        manager.filter_logs(
            args.category, 
            args.level, 
            args.since, 
            args.pattern
        )
    
    elif args.stats:
        manager.analyze_stats(args.days)
    
    elif args.cleanup:
        manager.cleanup_old_logs()
    
    elif args.rotate:
        manager.rotate_logs()


if __name__ == "__main__":
    main()