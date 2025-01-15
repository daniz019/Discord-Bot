# 🤖 Quantum Discord Bot

<div align="center">
  
  [![Discord](https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.com/developers/applications)
  [![Python Version](https://img.shields.io/badge/Python-3.12+-FFD43B?style=for-the-badge&logo=python&logoColor=306998)](https://www.python.org/downloads/)
  [![MySQL Version](https://img.shields.io/badge/MySQL-8.0-00758F?style=for-the-badge&logo=mysql&logoColor=white)](https://www.mysql.com/downloads/)
  
  [![Licença](https://img.shields.io/badge/Licença-MIT-28A745?style=for-the-badge)](https://opensource.org/licenses/MIT)

</div>

<p align="center">
  Bot do Discord desenvolvido para gerenciar acessos de usuários, períodos de teste e resets de HWID para o projeto <a href="https://github.com/daniz019/Valorant-TriggerBot">Quantum TriggerBot</a>.
</p>

## ⚡ Funcionalidades

- Sistema de Registro de Usuários
- Gerenciamento de Períodos de Teste (3 horas)
- Sistema de Reset de HWID
- Detecção de HWIDs Duplicados
- Limpeza Automática de Testes Expirados
- Sistema de Logs Completo
- Proteção Anti-Abuso

## 💻 Requisitos do Sistema

- Python 3.12 ou superior
- MySQL 8.0 ou superior
- Token do Bot Discord

## 📝 Guia de Instalação

### 1. Configuração do Bot Discord
1. Acesse o [Portal de Desenvolvedores do Discord](https://discord.com/developers/applications)
2. Clique em "New Application" e dê um nome
3. Vá para a seção "Bot" e clique em "Add Bot"
4. Copie o token do seu bot (Necessário para configuração)
5. Vá para OAuth2 > URL Generator
6. Selecione "bot" e as permissões necessárias
7. Use a URL gerada para convidar o bot para seu servidor

### 2. Configuração do Banco de Dados
1. Baixe e instale o AppServ em [https://www.appserv.org/en/](https://www.appserv.org/en/)
2. Durante a instalação, defina sua senha root do MySQL
3. Abra o phpMyAdmin (geralmente em http://localhost/phpMyAdmin)
4. Crie um novo banco de dados chamado `users`
5. Importe o arquivo `users.sql` fornecido neste repositório

### 3. Configuração do Projeto

1. Clone o repositório:
```bash
git clone https://github.com/daniz019/Discord-Bot.git
```

2. Entre na pasta do projeto:
```bash
cd Discord-Bot
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

### 4. Configuração do Ambiente
O projeto inclui um arquivo `config.env`. Edite-o com suas informações:
```env
# Token do seu bot do Discord
DISCORD_TOKEN=seu_token_aqui

# Configuração do banco de dados
DB_USER=seu_usuario_mysql
DB_PASSWORD=sua_senha_mysql
DB_HOST=localhost
```

## 🗄️ Estrutura do Banco de Dados

<details>
<summary>Tabelas do Sistema</summary>

### Tabela `logins`
- ID do Usuário (Chave Primária)
- Nome de Usuário do Discord
- HWID
- Status do Teste
- Data de Expiração
- Data do Último Reset

### Tabela `excluded_users`
- ID do Usuário
- Nome de Usuário do Discord
- HWID
- Data de Exclusão
</details>

## 🛠️ Comandos do Bot

| Comando | Descrição | Permissão | Cooldown |
|---------|-----------|-----------|----------|
| `/register_user` | Registra novo usuário | Admin | - |
| `/reset_hwid` | Reseta HWID do usuário | Usuário | 7 dias |
| `/start_trial` | Inicia período de teste (3h) | Usuário | Uma vez por usuário |

## 🔒 Recursos de Segurança

- Sistema de Detecção de HWID Duplicado
- Banimento Automático em Caso de Fraude
- Registro de Usuários Banidos na Tabela `excluded_users`
- Interrupção Automática do TriggerBot em Caso de Violação

## 📄 Licença

<div align="center">

[![Licença MIT](https://img.shields.io/badge/Licença%20MIT-28A745?style=for-the-badge&logo=github&logoColor=white)](https://opensource.org/licenses/MIT)

</div>

Este projeto está licenciado sob a [Licença MIT](https://opensource.org/licenses/MIT) - veja o arquivo [LICENSE](LICENSE) para mais detalhes.

A Licença MIT é uma licença de software permissiva que permite:
- ✅ Uso comercial
- ✅ Modificação
- ✅ Distribuição
- ✅ Uso privado

Com as seguintes condições:
- ⚠️ Deve incluir o aviso de copyright
- ⚠️ Deve incluir a licença
- ℹ️ Não oferece nenhuma garantia

Copyright © 2025 Discord-Bot
