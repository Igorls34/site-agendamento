#!/bin/bash
echo "🚀 === INICIANDO DEPLOY RAILWAY ==="

echo "🔄 Executando setup de produção..."
python setup_production.py

if [ $? -eq 0 ]; then
    echo "✅ Setup concluído com sucesso!"
    echo "🚀 Iniciando servidor Gunicorn..."
    gunicorn agendamento.wsgi --bind 0.0.0.0:$PORT
else
    echo "❌ Erro no setup! Abortando deploy."
    exit 1
fi