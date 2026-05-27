# TASK: setup-llm-bedrock

GOAL: Crear módulo compartido que inicializa ChatBedrockConverse desde .env para todos los agentes
FILES: agents/00_setup_llm.py
CONTRACT: def get_llm(model: str = "anthropic.claude-sonnet-4-5-20251001-v1:0") -> ChatBedrockConverse
DONE WHEN: grep -q "ChatBedrockConverse" agents/00_setup_llm.py && grep -q "BEDROCK_API_KEY" agents/00_setup_llm.py
ROLLBACK: git revert HEAD

# Contexto
- Leer .env con python-dotenv
- Si BEDROCK_API_KEY no está configurado o empieza con "<" → raise ValueError
- AWS_DEFAULT_REGION default: us-east-1
- Importar: from langchain_aws import ChatBedrockConverse
