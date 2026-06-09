# Portal de Gestao de Inventario e Vendas

Sistema simples de PDV para pequenos comercios, feito em Django para estudo e apresentacao em sala.

## Tecnologias usadas

- Python
- Django 5.2
- Django Class Based Views
- SQLite
- Django REST Framework
- Bootstrap
- Chart.js
- Autenticacao nativa do Django

## Instalar dependencias

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Rodar migracoes

```bash
python manage.py makemigrations
python manage.py migrate
```

## Criar superusuario

```bash
python manage.py createsuperuser
```

## Criar grupos de usuarios

```bash
python manage.py criar_grupos
```

Depois, acesse o admin e coloque cada usuario em um dos grupos:

- Administrador
- Gerente
- Vendedor

## Usuarios para teste e apresentacao

Como o arquivo `db.sqlite3` nao deve ser enviado para o GitHub, crie os usuarios de teste depois de rodar as migracoes.

Primeiro crie os grupos:

```bash
python manage.py criar_grupos
```

Depois crie os usuarios de teste:

```bash
python manage.py criar_usuarios_teste
```

Depois desse comando, os usuarios ficam assim:

| Login | Senha | Grupo | Observacao |
| --- | --- | --- | --- |
| admin | 123456 | Administrador | Superusuario, acessa o sistema e o admin do Django. |
| gerente | 123456 | Gerente | Pode cadastrar produtos, alterar precos, estornar vendas e acessar relatorios. |
| vendedor | 123456 | Vendedor | Pode visualizar produtos, registrar vendas e consultar historico. |

Nos testes automaticos do projeto tambem aparecem usuarios temporarios criados apenas durante a execucao dos testes:

- `vendedor` com senha `123`
- `gerente` com senha `123`
- `vendedor_api` com senha `123`
- `gerente_api` com senha `123`

Esses usuarios de teste nao ficam gravados no banco principal depois dos testes.

## Carregar produtos de exemplo

```bash
python manage.py loaddata fixtures/produtos_exemplo.json
```

## Rodar servidor

```bash
python manage.py runserver
```

## Acessar o sistema

- Sistema: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/
- API de produtos: http://127.0.0.1:8000/api/produtos/

## Como testar a API

Com usuario autenticado no navegador, acesse:

```text
GET /api/produtos/
GET /api/produtos/?nome=arroz
GET /api/produtos/?codigo_barras=789
GET /api/produtos/?ativo=true
```

Gerentes e administradores tambem podem usar:

```text
POST /api/produtos/
PUT /api/produtos/<id>/
PATCH /api/produtos/<id>/
DELETE /api/produtos/<id>/
```

O DELETE desativa o produto em vez de apagar definitivamente, preservando historico.

## Permissoes

- Vendedor: visualiza produtos, registra vendas e consulta historico.
- Gerente: faz tudo que vendedor faz, cadastra produtos, altera precos, estorna vendas e acessa relatorios.
- Administrador: acesso total, incluindo admin do Django quando tambem for superusuario.

## Funcionalidades principais

- Dashboard com indicadores do dia.
- Cadastro, listagem, edicao, detalhe e desativacao de produtos.
- Destaque visual para produtos com estoque baixo.
- Venda com varios itens.
- Baixa automatica de estoque ao finalizar venda.
- Bloqueio de venda acima do estoque disponivel.
- Estorno com devolucao de produtos ao estoque.
- Relatorio diario de fechamento de caixa.
- Grafico anual com Chart.js.
- API REST completa para catalogo de produtos.
