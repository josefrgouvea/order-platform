#!/bin/sh
set -e

ENDPOINT="http://dynamodb:8000"

echo "Esperando o DynamoDB ficar pronto..."
until aws dynamodb list-tables --endpoint-url "$ENDPOINT" > /dev/null 2>&1; do
  sleep 1
done

create_table() {
  name="$1"
  shift
  if aws dynamodb describe-table --table-name "$name" --endpoint-url "$ENDPOINT" > /dev/null 2>&1; then
    echo "Tabela $name já existe."
  else
    echo "Criando a tabela $name..."
    aws dynamodb create-table --table-name "$name" --endpoint-url "$ENDPOINT" "$@" > /dev/null
  fi
}

create_table users \
  --attribute-definitions \
    AttributeName=user_id,AttributeType=S \
    AttributeName=email,AttributeType=S \
  --key-schema AttributeName=user_id,KeyType=HASH \
  --global-secondary-indexes \
    'IndexName=email-index,KeySchema=[{AttributeName=email,KeyType=HASH}],Projection={ProjectionType=ALL}' \
  --billing-mode PAY_PER_REQUEST

create_table orders \
  --attribute-definitions \
    AttributeName=order_id,AttributeType=S \
    AttributeName=user_id,AttributeType=S \
    AttributeName=created_at,AttributeType=S \
  --key-schema AttributeName=order_id,KeyType=HASH \
  --global-secondary-indexes \
    'IndexName=user-orders-index,KeySchema=[{AttributeName=user_id,KeyType=HASH},{AttributeName=created_at,KeyType=RANGE}],Projection={ProjectionType=ALL}' \
  --billing-mode PAY_PER_REQUEST

create_table notifications \
  --attribute-definitions \
    AttributeName=user_id,AttributeType=S \
    AttributeName=sk,AttributeType=S \
  --key-schema \
    AttributeName=user_id,KeyType=HASH \
    AttributeName=sk,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST

echo "Tabelas prontas."