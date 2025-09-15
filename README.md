# Sistema de Agendamento MVP 📅# Sistema de Agendamento MVP



Sistema de agendamento Django com interface mobile-first, horários dinâmicos e integração WhatsApp.Um sistema simples e funcional para agendamento de serviços com integração ao WhatsApp.



## 🚀 Funcionalidades## 🚀 Funcionalidades



### ✅ Core Features### Área do Cliente (Pública)

- **Horários Dinâmicos**: Slots gerados automaticamente por regra (configurável)- ✅ Listagem de serviços disponíveis

- **Interface Mobile-First**: Design responsivo otimizado para dispositivos móveis- ✅ Agendamento simples com seleção de data/horário

- **Integração WhatsApp**: Mensagens automáticas para confirmação de agendamentos- ✅ Redirecionamento automático para WhatsApp com dados preenchidos

- **Painel Admin Moderno**: Interface administrativa com Jazzmin theme- ✅ Consulta de agendamentos por telefone

- **Atomicidade**: Prevenção de conflitos de horários com constraints de banco

### Área Administrativa (Login obrigatório)

### 📱 Interface do Cliente- ✅ Dashboard com métricas em tempo real

- Seleção de serviços em cards visuais- ✅ Agenda do dia com todos os agendamentos

- Calendário intuitivo para escolha de data- ✅ Edição/remarque de agendamentos

- Grade de horários com slots disponíveis/ocupados- ✅ Métricas semanais (quantidade, faturamento, ocupação)

- Formulário de agendamento simplificado- ✅ Gerenciamento de slots de horários

- Redirecionamento automático para WhatsApp

## 🛠️ Tecnologias

### 🛠 Painel Administrativo

- Dashboard com estatísticas em tempo real- **Django 5.1** - Framework web

- Gestão de agendamentos com filtros por data- **SQLite** - Banco de dados (desenvolvimento)

- Edição inline de agendamentos- **Bootstrap 5.3** - Interface responsiva

- Interface moderna e amigável (Jazzmin)- **Bootstrap Icons** - Ícones

- Visualização de agenda diária- **Python 3.13** - Linguagem de programação



## 🏗 Tecnologias## 📋 Pré-requisitos



- **Backend**: Django 5.2.3- Python 3.8+

- **Database**: SQLite (fácil deploy/desenvolvimento)- Pip (gerenciador de pacotes Python)

- **Frontend**: Bootstrap 5 + Templates responsivos

- **Admin Theme**: django-jazzmin## ⚡ Instalação e Execução

- **Python**: 3.13+

### 1. Clone/Baixe o projeto

## 📋 Pré-requisitos```bash

# Navegue até a pasta do projeto

- Python 3.8+cd site-agendamento2.0

- pip```

- Git

### 2. Ative o ambiente virtual (já criado)

## 🚀 Instalação e Execução```bash

# Windows

### 1. Clone o repositório.\\venv\\Scripts\\Activate.ps1

```bash

git clone https://github.com/Igorls34/site-agendamento.git# Ou se estiver usando cmd

cd site-agendamento.\\venv\\Scripts\\activate.bat

``````



### 2. Crie e ative o ambiente virtual### 3. Execute as migrações (já feitas)

```bash```bash

python -m venv venvpython manage.py migrate

```

# Windows

venv\Scripts\activate### 4. Carregue os dados iniciais (já feitos)

```bash

# Linux/Macpython manage.py seed_data

source venv/bin/activate```

```

### 5. Execute o servidor

### 3. Instale as dependências```bash

```bashpython manage.py runserver

pip install -r requirements.txt```

```

### 6. Acesse a aplicação

### 4. Configure o banco de dados- **Site público**: http://127.0.0.1:8000/

```bash- **Admin Django**: http://127.0.0.1:8000/admin/

python manage.py migrate- **Dashboard personalizado**: http://127.0.0.1:8000/admin-dashboard/

```

## 👤 Credenciais de Acesso

### 5. Crie um superusuário (opcional)

```bash**Administrador:**

python manage.py createsuperuser- **Usuário**: admin

```- **Senha**: admin123



### 6. Execute o servidor## 🎯 Como Usar

```bash

python manage.py runserver### Para Clientes:

```1. Acesse a página inicial

2. Escolha um serviço

### 7. Acesse o sistema3. Selecione data e horário disponível

- **Site principal**: http://127.0.0.1:8000/4. Preencha nome e telefone

- **Admin**: http://127.0.0.1:8000/admin/5. Confirme o agendamento

6. Será redirecionado para WhatsApp automaticamente

## ⚙️ Configuração7. Para consultar agendamentos: use "Meus Agendamentos" no menu



### Horários de Funcionamento### Para Administradores:

Edite em `agendamento/settings.py`:1. Faça login com admin/admin123

```python2. Use o Dashboard para ver métricas

DEFAULT_DAILY_TIMES = ['09:00', '10:00', '11:00', '14:00', '15:00', '16:00']3. Acesse "Agenda do Dia" para gerenciar agendamentos

```4. Use "Gerenciar Slots" para criar/remover horários

5. Edite agendamentos conforme necessário

### WhatsApp Business

Configure seu número em `agendamento/settings.py`:## 📊 Dados Iniciais

```python

WHATSAPP_BUSINESS_NUMBER = "5524998190280"  # Formato: código do país + DDD + númeroO sistema vem com:

```- **3 serviços pré-cadastrados** (Serviço 1, 2, 3)

- **36 slots de horário** para os próximos 7 dias

### Timezone- **Usuário admin** configurado

```python- **Horários**: 9h, 10h, 11h, 14h, 15h, 16h (segunda a sábado)

TIME_ZONE = 'America/Sao_Paulo'

```## 🔧 Configurações



## 📱 URLs Principais### Número do WhatsApp

Edite o arquivo `bookings/views.py`, linha 48:

| URL | Descrição |```python

|-----|-----------|whatsapp_number = "5511999999999"  # Substitua pelo número real

| `/` | Página inicial - seleção de serviços |```

| `/agendar/` | Formulário de agendamento |

| `/meus-agendamentos/` | Lista de agendamentos do cliente |### Novos Serviços

| `/admin/` | Painel administrativo |Use o Django Admin em http://127.0.0.1:8000/admin/ para:

| `/admin/dashboard/` | Dashboard customizado |- Adicionar/editar serviços

- Gerenciar horários disponíveis

## 🎨 Personalização- Ver todos os agendamentos



### Adicionando Novos Serviços### Novos Horários

1. Acesse o admin em `/admin/`1. Acesse Django Admin → Schedules

2. Vá em "Serviços" 2. Adicione novos slots com data/horário

3. Adicione nome, duração e preço3. Marque como "Is available"

4. Os serviços aparecerão automaticamente na página inicial

## 📱 Fluxo do WhatsApp

### Modificando Templates

Os templates estão em `bookings/templates/`:Após confirmar um agendamento, o cliente é redirecionado para:

- `agenda.html` - Página inicial```

- `agendar.html` - Formulário de agendamentohttps://wa.me/5511999999999?text=Olá, meu nome é João, gostaria de confirmar meu agendamento para Serviço 1 no dia 15/09/2025 às 10:00. Telefone: (11) 99999-9999

- `meus_agendamentos.html` - Lista de agendamentos```



## 🔧 Estrutura do Projeto## 🎨 Design



```- Interface limpa e neutra

site-agendamento/- Responsiva (funciona em mobile)

├── agendamento/          # Configurações Django- Cores: azul primário (#0066cc)

│   ├── settings.py       # Configurações principais- Ícones Bootstrap Icons

│   ├── urls.py          # URLs do projeto- Foco na usabilidade

│   └── wsgi.py          # WSGI config

├── bookings/            # App principal## 📈 Métricas Disponíveis

│   ├── models.py        # Modelos (Service, Booking)

│   ├── views.py         # Views principais- Agendamentos do dia

│   ├── services.py      # Lógica de horários dinâmicos- Agendamentos da semana

│   ├── utils.py         # Utilitários (WhatsApp, etc)- Faturamento semanal estimado

│   ├── admin.py         # Configuração do admin- Slots livres hoje

│   ├── templates/       # Templates HTML- Histórico de agendamentos

│   └── migrations/      # Migrações do banco

├── requirements.txt     # Dependências Python## 🔒 Segurança

├── manage.py           # Script de gerenciamento Django

└── README.md           # Este arquivo- Login obrigatório apenas para área admin

```- CSRF protection ativo

- Dados mínimos coletados (LGPD friendly)

## 📊 Modelos de Dados- Validações de entrada



### Service (Serviços)## 🚀 Próximos Passos (Fora do MVP)

- `name`: Nome do serviço

- `price_cents`: Preço em centavos- [ ] Integração com Google Calendar

- `duration_minutes`: Duração em minutos- [ ] API do WhatsApp para notificações automáticas

- [ ] Pagamentos online

### Booking (Agendamentos)- [ ] Multi-profissional

- `service`: Serviço agendado- [ ] Relatórios avançados

- `customer_name`: Nome do cliente- [ ] App mobile

- `customer_phone`: Telefone do cliente

- `date`: Data do agendamento## 📞 Suporte

- `start_time`: Horário de início

- `end_time`: Horário de fimPara dúvidas ou problemas:

- `status`: Status (PENDING, CONFIRMED, CANCELLED)1. Verifique se o ambiente virtual está ativo

2. Confirme que todas as dependências estão instaladas

## 🔒 Segurança3. Verifique os logs do Django para erros



- Constraints de banco previnem agendamentos duplicados---

- Validação de horários disponíveis antes do agendamento

- Transações atômicas para integridade dos dados**Sistema desenvolvido com foco em simplicidade e funcionalidade imediata!** 🎉
- Sanitização de inputs de formulário

## 🚀 Deploy

Para deploy em produção:

1. Configure `DEBUG = False`
2. Defina `ALLOWED_HOSTS`
3. Configure banco de produção (PostgreSQL recomendado)
4. Configure servidor web (Nginx + Gunicorn)
5. Configure HTTPS
6. Configure variáveis de ambiente para dados sensíveis

## 📝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 💬 Suporte

Para suporte, entre em contato via WhatsApp: +55 24 99819-0280

---

Desenvolvido com ❤️ usando Django