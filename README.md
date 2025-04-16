# ReservasOnline

Sistema completo para agendamento e gestão inteligente de reservas, desenvolvido com Django, Django Ninja, Celery, Redis e MySQL.

## Visão Geral

ReservasOnline é uma plataforma robusta para agendamento e gestão de reservas, especialmente projetada para pequenos negócios como clínicas, salões e espaços de eventos. O sistema oferece:

- Agendamento inteligente com verificação de disponibilidade
- Notificações automáticas por e-mail
- Dashboard administrativo com relatórios
- Avaliações de serviços
- Lista de espera automática

## Tecnologias Utilizadas

- **Backend**: Django 4.2 com Django Ninja (API REST)
- **Banco de Dados**: MySQL 8.0
- **Cache e Broker**: Redis 7.0
- **Tarefas Assíncronas**: Celery 5.3
- **Conteinerização**: Docker e Docker Compose
- **Autenticação**: JWT (JSON Web Tokens)

## Estrutura do Projeto

O projeto está organizado em várias aplicações Django:

- **accounts**: Gerenciamento de usuários e autenticação
- **reservas**: Agendamento e gerenciamento de reservas
- **avaliacoes**: Sistema de avaliações de serviços
- **notificacoes**: Sistema de notificações por e-mail
- **admin_dashboard**: Painéis administrativos e relatórios
- **core**: Funcionalidades compartilhadas entre aplicações

## Requisitos

- Docker e Docker Compose
- Python 3.11+ (para desenvolvimento local)
- Node.js 16+ (para frontend, se aplicável)

## Instalação e Execução

### Com Docker (Recomendado)

1. Clone o repositório:
   ```bash
   git clone https://github.com/seuusuario/reservas-online.git
   cd reservas-online
   ```

2. Configure o arquivo .env (use o .env.example como base):
   ```bash
   cp .env.example .env
   # Edite o arquivo .env com suas configurações
   ```

3. Inicie os contêineres:
   ```bash
   docker-compose up -d
   ```

4. Crie um superusuário:
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

5. Acesse a aplicação:
   - API: http://localhost:8000/api/v1/
   - Documentação da API: http://localhost:8000/api/docs/ (apenas em ambiente de desenvolvimento)
   - Admin do Django: http://localhost:8000/admin/

### Desenvolvimento Local (sem Docker)

1. Clone o repositório:
   ```bash
   git clone https://github.com/seuusuario/reservas-online.git
   cd reservas-online
   ```

2. Crie e ative um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate     # Windows
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure as variáveis de ambiente ou crie um arquivo .env

5. Execute as migrações:
   ```bash
   python manage.py migrate
   ```

6. Crie um superusuário:
   ```bash
   python manage.py createsuperuser
   ```

7. Inicie o servidor:
   ```bash
   python manage.py runserver
   ```

8. Em uma nova janela de terminal, inicie o Celery:
   ```bash
   celery -A ReservasOnline worker -l info
   ```

9. Em outra janela de terminal, inicie o Celery Beat:
   ```bash
   celery -A ReservasOnline beat -l info
   ```

## Principais Funcionalidades

### Autenticação e Usuários
- Registro com validação de senha forte
- Login com JWT (access e refresh tokens)
- Perfis para clientes, prestadores e administradores
- Preferências de idioma e notificações

### Prestadores e Disponibilidade
- Definição de dias e horários disponíveis
- Configuração de tempo médio de atendimento
- Intervalos entre reservas
- Definição de pausas e dias indisponíveis

### Reservas
- Criação de reservas com verificação de disponibilidade
- Confirmação automática ou manual
- Cancelamento com notificação para lista de espera
- Exportação para Excel/CSV

### Notificações
- E-mails de confirmação, lembrete e avaliação
- Templating HTML personalizado
- Envio assíncrono via Celery
- Templates em múltiplos idiomas

### Relatórios e Administração
- Dashboard com estatísticas gerais
- Relatórios semanais automáticos
- Logs de atividades críticas
- Visualização de métricas de desempenho

## Tarefas Automatizadas (Celery)

- Envio de lembretes 24h antes da reserva
- Solicitação de avaliação após o término
- Cancelamento automático de reservas não confirmadas
- Notificação para usuários em lista de espera
- Geração e envio de relatórios semanais
- Arquivamento de reservas antigas

## Segurança

- Autenticação JWT com tempos configuráveis
- Autorização baseada em função
- Senhas com requisitos de segurança
- Proteção CSRF e CORS
- Registro de atividades críticas

## Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Implemente suas mudanças
4. Execute os testes
5. Faça commit das alterações (`git commit -m 'Adiciona nova funcionalidade'`)
6. Envie para o Github (`git push origin feature/nova-funcionalidade`)
7. Abra um Pull Request

## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo LICENSE para detalhes. 