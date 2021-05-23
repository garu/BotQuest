BotQuest
=========

[![codecov](https://codecov.io/gh/garu/BotQuest/branch/main/graph/badge.svg?token=ID0ZQCGSTC)](https://codecov.io/gh/garu/BotQuest)

*BotQuest na áááárea galeeeeera!*

Esse bot foi criado para o [Discord do PodQuest](https://discord.gg/6Wrnttn).
Os comandos disponíveis são lidos a partir da pasta "reactions".


Pré-requisitos
--------------

* Python 3
* Registrar uma "app" do tipo "bot" no [Discord](https://discordapp.com/developers) e copiar o token
* criar a variável BOTQUESTID com esse token
* acessar a url https://discordapp.com/api/oauth2/authorize?client_id=SEU_CLIENT_ID&scope=bot&permissions=268438592
  trocando `SEU_CLIENT_ID` pelo client id do bot (não é o token, é o *client id*).
* autorizar o acesso do bot no seu server clicando no botão que aparece ao acessar essa URL.

O número *268438592* acima ativa as seguintes permissões: *manage roles*, *view channels*, *send messages*
e *add reactions*. O bot só precisa dessas, mas se for editar/criar reactions que precisem de permissões diferentes, é só atualizar o número.

Pronto! Depois disso, sempre que você ligar o bot ele vai se auto-conectar nos servidores que autorizaram.


Instalação nativa no seu sistema
--------------------------------

    $ git clone https://github.com/garu/BotQuest BotQuest && cd BotQuest
    $ python3 -m venv env
    $ source env/bin/activate
    $ python -m pip install --upgrade pip
    $ env/bin/pip3 install -r requirements.txt
    $ export BOTQUESTID=...
    $ python3 bot.py


Instalação num container (Docker)
---------------------------------

    $ git clone https://github.com/garu/BotQuest BotQuest && cd BotQuest

Crie um arquivo chamado `.env` no diretório do projeto e coloque apenas uma linha:

    BOTQUESTID=....

Onde "..." é o token do bot no Discord (sem aspas). Depois é só montar e executar o container:

    $ docker build -t botquest .
    $ docker run -d --env-file=.env -v botquestdb:/bot/data botquest


Testes & QA
-----------

Se fizer alguma modificação no código, rode os testes para garantir que está tudo ok. Isso é particularmente importante se quiser nos mandar um pull request!

    $ python3 -m unittest discover

ou, para rodar um teste específico:

    $ python3 -m unittest tests.test_reactions_infinite
    $ python3 -m unittest tests.test_reactions_infinite.TestInfinite.test_valid_reaction

Todos os pull request são testados com:

    $ pip install coverage flake8 pylint bandit

    $ coverage run --source botquest -m unittest discover
    $ coverage report -m (ou só "coverage html")

    $ flake8 .
    $ pylint --rcfile=setup.cfg botquest/ tests/ bot.py
    $ bandit -r -s B311 botquest/ tests/ bot.py
