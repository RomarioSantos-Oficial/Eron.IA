"""
Utilitário de Gerenciamento de Moderação - Eron.IA
==================================================

Ferramenta de linha de comando para gerenciar o sistema de moderação de conteúdo.

Funcionalidades:
- Visualizar estatísticas de moderação
- Gerenciar padrões de detecção
- Administrar usuários (desbloquear, perdoar, etc.)
- Relatórios de segurança
- Testes de conteúdo
- Backup e manutenção

Uso:
python tools/moderation_manager.py --help

Autor: Eron.IA System
Data: 2024
"""

import argparse
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import json
import sqlite3

# Adicionar diretório pai para imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from src.adult_content_moderator import moderator, analyze_content, get_moderation_stats
    from core.config import config
except ImportError as e:
    print(f"❌ Erro ao importar dependências: {e}")
    sys.exit(1)


class ModerationManager:
    """Gerenciador do sistema de moderação"""
    
    def __init__(self):
        self.moderator = moderator
        self.db_path = moderator.db_path
        self.patterns_db_path = moderator.patterns_db_path
    
    def show_stats(self, days=7):
        """Mostra estatísticas detalhadas de moderação"""
        print(f"📊 ESTATÍSTICAS DE MODERAÇÃO - ÚLTIMOS {days} DIAS")
        print("=" * 60)
        
        stats = get_moderation_stats(days)
        current = stats['current_stats']
        
        # Estatísticas atuais
        print("📈 **HOJE:**")
        print(f"   Verificações: {current['total_checks_today']:,}")
        print(f"   Bloqueios: {current['blocks_today']:,}")
        print(f"   Avisos: {current['warnings_today']:,}")
        print()
        
        # Estatísticas do período
        print(f"📋 **ÚLTIMOS {days} DIAS:**")
        action_stats = stats['action_stats']
        
        total_actions = sum(action_stats.values())
        print(f"   Total de ações: {total_actions:,}")
        
        for key, count in sorted(action_stats.items(), key=lambda x: x[1], reverse=True):
            severity, action = key.split('_', 1)
            print(f"   {severity.capitalize()} - {action.capitalize()}: {count:,}")
        
        print()
        
        # Top violadores
        top_violators = stats['top_violators']
        if top_violators:
            print("🚨 **TOP VIOLADORES:**")
            for i, violator in enumerate(top_violators[:5], 1):
                status_emoji = {"active": "✅", "quarantined": "⏸️", "blocked": "🚫", "banned": "⛔"}
                emoji = status_emoji.get(violator['status'], "❓")
                print(f"   {i}. {emoji} User {violator['user_id']}: {violator['violations']} violações ({violator['severe']} severas)")
    
    def list_patterns(self):
        """Lista padrões de detecção configurados"""
        print("🔍 PADRÕES DE DETECÇÃO CONFIGURADOS")
        print("=" * 60)
        
        with sqlite3.connect(self.patterns_db_path) as conn:
            cursor = conn.execute('''
                SELECT id, pattern, pattern_type, severity, is_regex, is_active, description
                FROM content_patterns
                ORDER BY severity DESC, pattern_type
            ''')
            
            patterns_by_severity = {'severe': [], 'moderate': [], 'mild': []}
            
            for row in cursor.fetchall():
                pattern_id, pattern, type_, severity, is_regex, is_active, description = row
                status = "✅" if is_active else "❌"
                regex_mark = "📝" if is_regex else "🔤"
                
                patterns_by_severity[severity].append({
                    'id': pattern_id,
                    'pattern': pattern,
                    'type': type_,
                    'regex': is_regex,
                    'active': is_active,
                    'description': description,
                    'display': f"   {status} {regex_mark} [{type_}] {pattern[:50]}... - {description}"
                })
        
        for severity in ['severe', 'moderate', 'mild']:
            if patterns_by_severity[severity]:
                print(f"\n🔴 **{severity.upper()}** ({len(patterns_by_severity[severity])} padrões):")
                for pattern in patterns_by_severity[severity]:
                    print(pattern['display'])
    
    def test_content(self, content):
        """Testa conteúdo específico"""
        print(f"🧪 TESTE DE CONTEÚDO")
        print("=" * 60)
        print(f"📝 **Texto:** '{content}'")
        print()
        
        result = analyze_content(content, user_id="test_user")
        
        # Mostrar resultado
        severity_colors = {
            'clean': '🟢',
            'mild': '🟡',
            'moderate': '🟠',
            'severe': '🔴'
        }
        
        severity_emoji = severity_colors.get(result['severity'], '❓')
        
        print(f"{severity_emoji} **Severidade:** {result['severity'].upper()}")
        print(f"⚡ **Confiança:** {result['confidence']:.1%}")
        print(f"🎯 **Ação:** {result['action']}")
        print(f"📋 **Razão:** {result['reason']}")
        
        if result['flagged_words']:
            print(f"🚩 **Palavras flagradas:** {', '.join(result['flagged_words'])}")
        
        # Mensagem de feedback
        from src.adult_content_moderator import get_user_feedback_message
        feedback = get_user_feedback_message(result)
        if feedback:
            print(f"\n💬 **Feedback ao usuário:**")
            print(f"   {feedback}")
    
    def show_user_status(self, user_id):
        """Mostra status de um usuário específico"""
        print(f"👤 STATUS DO USUÁRIO: {user_id}")
        print("=" * 60)
        
        status = self.moderator._get_user_status(user_id)
        
        if status['violation_count'] == 0:
            print("✅ **Usuário limpo** - Nenhuma violação registrada")
            return
        
        # Informações do usuário
        print(f"📊 **Violações totais:** {status['violation_count']}")
        print(f"🔴 **Violações severas:** {status['severe_violations']}")
        print(f"📅 **Última violação:** {status['last_violation']}")
        print(f"⚠️ **Avisos enviados:** {status['warnings_sent']}")
        
        # Status atual
        status_info = {
            'active': '✅ Ativo',
            'quarantined': '⏸️ Em quarentena',
            'blocked': '🚫 Bloqueado',
            'banned': '⛔ Banido'
        }
        
        print(f"🏷️ **Status:** {status_info.get(status['status'], status['status'])}")
        
        # Informações de restrição
        if status['quarantine_until']:
            quarantine_until = datetime.fromisoformat(status['quarantine_until'])
            if datetime.now() < quarantine_until:
                print(f"⏰ **Quarentena até:** {quarantine_until.strftime('%d/%m/%Y %H:%M')}")
        
        if status['ban_until']:
            ban_until = datetime.fromisoformat(status['ban_until'])
            if datetime.now() < ban_until:
                print(f"⏰ **Bloqueado até:** {ban_until.strftime('%d/%m/%Y %H:%M')}")
        
        # Histórico recente
        self._show_user_recent_logs(user_id)
    
    def _show_user_recent_logs(self, user_id, limit=5):
        """Mostra logs recentes de um usuário"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT timestamp, severity, action_taken, reason, content_snippet
                FROM moderation_logs
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (user_id, limit))
            
            logs = cursor.fetchall()
            if logs:
                print(f"\n📋 **ÚLTIMOS {len(logs)} EVENTOS:**")
                for timestamp, severity, action, reason, snippet in logs:
                    dt = datetime.fromisoformat(timestamp)
                    print(f"   {dt.strftime('%d/%m %H:%M')} - {severity.upper()} - {action} - {snippet[:30]}...")
    
    def unblock_user(self, user_id):
        """Desbloqueia um usuário"""
        print(f"🔓 DESBLOQUEANDO USUÁRIO: {user_id}")
        print("=" * 60)
        
        with sqlite3.connect(self.db_path) as conn:
            # Verificar status atual
            cursor = conn.execute('''
                SELECT status, violation_count FROM user_violations WHERE user_id = ?
            ''', (user_id,))
            
            row = cursor.fetchone()
            if not row:
                print("❌ Usuário não encontrado no sistema de moderação")
                return
            
            current_status, violations = row
            
            if current_status == 'active':
                print("✅ Usuário já está ativo")
                return
            
            # Desbloquear
            conn.execute('''
                UPDATE user_violations 
                SET status = 'active', quarantine_until = NULL, ban_until = NULL
                WHERE user_id = ?
            ''', (user_id,))
            
            print(f"✅ Usuário desbloqueado com sucesso!")
            print(f"   Status anterior: {current_status}")
            print(f"   Violações mantidas: {violations}")
            print(f"   ⚠️ Violações não foram resetadas - use --reset-violations para limpar histórico")
    
    def reset_user_violations(self, user_id):
        """Reseta violações de um usuário"""
        print(f"🧹 RESETANDO VIOLAÇÕES: {user_id}")
        print("=" * 60)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT violation_count, severe_violations FROM user_violations WHERE user_id = ?
            ''', (user_id,))
            
            row = cursor.fetchone()
            if not row:
                print("❌ Usuário não encontrado")
                return
            
            old_violations, old_severe = row
            
            # Resetar contador
            conn.execute('''
                UPDATE user_violations 
                SET violation_count = 0, severe_violations = 0, warnings_sent = 0
                WHERE user_id = ?
            ''', (user_id,))
            
            print(f"✅ Violações resetadas!")
            print(f"   Violações removidas: {old_violations} ({old_severe} severas)")
    
    def add_pattern(self, pattern, pattern_type, severity, is_regex=False, description=""):
        """Adiciona novo padrão de detecção"""
        print(f"➕ ADICIONANDO PADRÃO")
        print("=" * 60)
        
        with sqlite3.connect(self.patterns_db_path) as conn:
            try:
                conn.execute('''
                    INSERT INTO content_patterns 
                    (pattern, pattern_type, severity, is_regex, description)
                    VALUES (?, ?, ?, ?, ?)
                ''', (pattern, pattern_type, severity, is_regex, description))
                
                print(f"✅ Padrão adicionado com sucesso!")
                print(f"   Padrão: {pattern}")
                print(f"   Tipo: {pattern_type}")
                print(f"   Severidade: {severity}")
                print(f"   Regex: {'Sim' if is_regex else 'Não'}")
                print(f"   Descrição: {description}")
                
                # Recarregar padrões
                self.moderator.load_patterns()
                print("🔄 Padrões recarregados!")
                
            except Exception as e:
                print(f"❌ Erro ao adicionar padrão: {e}")
    
    def toggle_pattern(self, pattern_id):
        """Ativa/desativa um padrão"""
        with sqlite3.connect(self.patterns_db_path) as conn:
            # Verificar status atual
            cursor = conn.execute('SELECT is_active, pattern FROM content_patterns WHERE id = ?', (pattern_id,))
            row = cursor.fetchone()
            
            if not row:
                print(f"❌ Padrão ID {pattern_id} não encontrado")
                return
            
            current_active, pattern = row
            new_active = not current_active
            
            # Atualizar
            conn.execute('UPDATE content_patterns SET is_active = ? WHERE id = ?', (new_active, pattern_id))
            
            status = "ativado" if new_active else "desativado"
            print(f"✅ Padrão '{pattern[:30]}...' {status}")
            
            # Recarregar padrões
            self.moderator.load_patterns()
    
    def export_report(self, days=30, format='json'):
        """Exporta relatório de moderação"""
        print(f"📄 EXPORTANDO RELATÓRIO ({days} dias)")
        print("=" * 60)
        
        since_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            # Dados do relatório
            cursor = conn.execute('''
                SELECT timestamp, user_id, severity, action_taken, reason, content_snippet
                FROM moderation_logs
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
            ''', (since_date.isoformat(),))
            
            logs = []
            for row in cursor.fetchall():
                logs.append({
                    'timestamp': row[0],
                    'user_id': row[1],
                    'severity': row[2],
                    'action': row[3],
                    'reason': row[4],
                    'content_snippet': row[5]
                })
            
            # Estatísticas
            stats = get_moderation_stats(days)
            
            report = {
                'generated_at': datetime.now().isoformat(),
                'period_days': days,
                'total_events': len(logs),
                'statistics': stats,
                'events': logs
            }
        
        # Salvar relatório
        filename = f"moderation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"
        filepath = Path("reports") / filename
        filepath.parent.mkdir(exist_ok=True)
        
        if format == 'json':
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Relatório exportado: {filepath}")
        print(f"   Eventos incluídos: {len(logs):,}")
        print(f"   Período: {days} dias")
    
    def cleanup_old_data(self, days=90):
        """Limpa dados antigos"""
        print(f"🧹 LIMPEZA DE DADOS ANTIGOS (>{days} dias)")
        print("=" * 60)
        
        result = self.moderator.cleanup_old_logs(days)
        
        print(f"✅ Limpeza concluída:")
        print(f"   Logs removidos: {result['logs_deleted']:,}")
        print(f"   Cache limpo: {result['cache_deleted']:,}")


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="Gerenciador de Moderação do Eron.IA",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  %(prog)s --stats                          # Estatísticas dos últimos 7 dias
  %(prog)s --stats --days 30               # Estatísticas dos últimos 30 dias
  %(prog)s --patterns                      # Lista padrões configurados
  %(prog)s --test "texto para testar"      # Testa conteúdo específico
  %(prog)s --user 12345                    # Status de usuário específico
  %(prog)s --unblock 12345                 # Desbloqueia usuário
  %(prog)s --reset-violations 12345        # Reseta violações
  %(prog)s --add-pattern "palavra" spam severe  # Adiciona padrão
  %(prog)s --export-report                 # Exporta relatório
  %(prog)s --cleanup                       # Limpa dados antigos
        """
    )
    
    parser.add_argument('--stats', action='store_true',
                       help='Mostra estatísticas de moderação')
    
    parser.add_argument('--days', type=int, default=7,
                       help='Número de dias para estatísticas (padrão: 7)')
    
    parser.add_argument('--patterns', action='store_true',
                       help='Lista padrões de detecção')
    
    parser.add_argument('--test', metavar='CONTENT',
                       help='Testa conteúdo específico')
    
    parser.add_argument('--user', metavar='USER_ID',
                       help='Mostra status de usuário específico')
    
    parser.add_argument('--unblock', metavar='USER_ID',
                       help='Desbloqueia usuário')
    
    parser.add_argument('--reset-violations', metavar='USER_ID',
                       help='Reseta violações do usuário')
    
    parser.add_argument('--add-pattern', nargs=4, 
                       metavar=('PATTERN', 'TYPE', 'SEVERITY', 'DESCRIPTION'),
                       help='Adiciona padrão: pattern type severity description')
    
    parser.add_argument('--toggle-pattern', type=int, metavar='ID',
                       help='Ativa/desativa padrão por ID')
    
    parser.add_argument('--export-report', action='store_true',
                       help='Exporta relatório de moderação')
    
    parser.add_argument('--cleanup', action='store_true',
                       help='Limpa dados antigos')
    
    args = parser.parse_args()
    
    # Se nenhum argumento, mostra ajuda
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    # Inicializar gerenciador
    manager = ModerationManager()
    
    # Executar ações
    if args.stats:
        manager.show_stats(args.days)
    
    elif args.patterns:
        manager.list_patterns()
    
    elif args.test:
        manager.test_content(args.test)
    
    elif args.user:
        manager.show_user_status(args.user)
    
    elif args.unblock:
        manager.unblock_user(args.unblock)
    
    elif args.reset_violations:
        manager.reset_user_violations(args.reset_violations)
    
    elif args.add_pattern:
        pattern, type_, severity, description = args.add_pattern
        manager.add_pattern(pattern, type_, severity, description=description)
    
    elif args.toggle_pattern:
        manager.toggle_pattern(args.toggle_pattern)
    
    elif args.export_report:
        manager.export_report(args.days)
    
    elif args.cleanup:
        manager.cleanup_old_data()


if __name__ == "__main__":
    main()