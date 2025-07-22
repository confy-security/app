# Confy App

Cliente desktop para o sistema Confy de comunicação criptografada.

### 🔧 Configurando o ambiente de desenvolvimento

Antes de iniciar você deve ter as seguintes ferramentas instaladas:

- [GIT](https://git-scm.com/)
- [Poetry](https://python-poetry.org/docs/#installation)
- [Python 3.13+](https://www.python.org/downloads/)

#### Clone o repositório

```bash
   git clone https://github.com/confy-security/app.git
   cd app
```

#### Configure o Poetry para criar um ambiente virtual dentro do diretório do projeto

```bash
   poetry config virtualenvs.create true
   poetry config virtualenvs.in-project true
```

Assim, o ambiente virtual será criado dentro do diretório `.venv` do projeto.

#### Instale as dependências do projeto

```bash
   poetry install
```

#### Ative o ambiente virtual

No Windows:

```bash
   .venv\Scripts\Activate.ps1
```

Ou no Linux:

```bash
   source .venv/bin/activate
```

Agora você pode começar a desenvolver o aplicativo Confy :)