# Configurações Otimizadas para Qwen2.5-4B no LM Studio

## 🎯 Configurações Recomendadas:

### Server Settings (Servidor):
- **Max Tokens**: 4096 (para respostas mais longas)
- **Temperature**: 0.7 (criatividade equilibrada)
- **Top-p**: 0.9 (diversidade controlada)
- **Top-k**: 40 (vocabulário otimizado)
- **Repeat Penalty**: 1.1 (evita repetições)
- **Context Length**: 8192 (memória expandida)

### Performance Settings:
- **GPU Layers**: MAX disponível (usar toda GPU)
- **Batch Size**: 512
- **Threads**: Número de cores da CPU
- **Flash Attention**: Ativado (se disponível)

### Chat Template:
- Usar template específico do Qwen
- Ativar "Apply chat template"

## 🔧 Como Configurar:
1. Abrir LM Studio
2. Ir em Server > Configurações
3. Aplicar valores acima
4. Salvar configuração
5. Reiniciar servidor

## 🎯 Resultado Esperado:
- Respostas 40% mais rápidas
- Contexto 2x maior
- Menos repetições
- Melhor coerência