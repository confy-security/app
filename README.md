<h1 align="center">
  <a href="https://github.com/confy-security/app" target="_blank" rel="noopener noreferrer">
    <picture>
      <img width="80" src="confy/assets/icon.png">
    </picture>
  </a>
  <br>
  Confy Desktop
</h1>

<p align="center">Cliente desktop para o sistema Confy de comunicação criptografada.</p>

<div align="center">

[![GitHub License](https://img.shields.io/github/license/confy-security/app?color=blue
)](/LICENSE)
[![Visitors](https://api.visitorbadge.io/api/visitors?path=confy-security%2Fapp&label=repository%20visits&countColor=%231182c3&style=flat)](https://github.com/confy-security/app)
  
</div>

## 🔧 Configurando o ambiente de desenvolvimento

Antes de iniciar você deve ter as seguintes ferramentas instaladas:

- [GIT](https://git-scm.com/)
- [Poetry](https://python-poetry.org/docs/#installation)
- [Python 3.13.5](https://www.python.org/downloads/)

> [!IMPORTANT]
> Devido as dependências da aplicação, recomendamos que use especificamente a versão 3.13.5 (mais recente) do Python durante o desenvolvimento.

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

## ✨ Comandos úteis

- `task run` - executa a aplicação.
- `task test` - executa os testes.
- `task build` - faz o build do aplicativo.
- `task package` - empacota o aplicativo em um binário nativo para o SO atual.

> [!NOTE]
> Lembre-se que você deve estar com o ambiente virtual ativado antes de executar os comandos.
