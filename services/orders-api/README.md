# Orders-api

API REST da plataforma de pedidos em FastAPI

## Testes

Os testes ficam na pasta tests/ e rodam com o pytest, com este comando:

```
uv run pytest
```

Os testes não precisam do Docker e nem de ter uma conta na AWS, eles rodam em qualquer máquina, porém, precisa ter o uv instalado.

## Como os testes lidam com o banco de dados

-  Testes das regras e das rotas:
Estão nos arquivos test_users_api.py, test_orders_api.py, test_services.py ...
Usam sempre os repositórios em memória para fazer os testes. Cada teste começa com os dados vazios, logo, são independentes

-  Testes do repositório do Dynamodb:
Está no arquivo test_dynamo_repositories.py.
Precisa usar o moto, que simula um Dynamodb da AWS dentro do próprio teste. O código testado é o repositório de verdade, só o banco de dados que é falso.

## Quando usar o moto

O moto é para ser usado para testes automáticos. Ele é muito rápido, cada teste simula um banco vazio e novo e não depende de nada estar rodando previamente e fora do teste. Assim, ele não depende de um Dynamodb para funcionar, já que ele cria um falso só para testes.

## Quando usar o Dynamodb local

O Dynamodb local é para ser usado quando queremos rodar a API de verdade e testá-la a mão. Assim, podendo conferir o comportamento dos dados e dos testes em um banco de dados real, porém local, no seu próprio computador, sem precisar acessar o Dynamo da AWS. Vale testar sempre em um banco real local depois de uma mudança brusca no código, como mudar um repositório, uma vez que ele é mais fiel do que o moto. 