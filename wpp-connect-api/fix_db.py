import asyncio
import os
import sys
import subprocess
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Adiciona o diretório atual ao path para importar módulos do app
sys.path.append(os.getcwd())

try:
    from app.core.config import settings
except ImportError:
    # Fallback caso a execução seja feita de fora do diretório wpp-connect-api
    sys.path.append(os.path.join(os.getcwd(), 'wpp-connect-api'))
    from app.core.config import settings

# Lista de tabelas esperadas na schema public
EXPECTED_TABLES = {"tenants", "messages", "audit_logs", "webhook_events", "users"}

async def check_and_fix():
    print("--- Iniciando Verificação de Integridade do Banco de Dados ---")
    
    # 1. Verificação
    # Mascarando a senha para exibição
    safe_url = settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else "..."
    print(f"Conectando ao banco de dados: ...@{safe_url}")
    
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    
    found_tables = set()
    
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
            ))
            found_tables = {row[0] for row in result.fetchall()}
            
        print(f"Tabelas encontradas: {', '.join(found_tables)}")
        
        # 2. Diagnóstico
        # Filtra apenas as tabelas que estamos monitorando
        missing_tables = EXPECTED_TABLES - found_tables
        
        if not missing_tables:
            # Verifica se pelo menos as tabelas esperadas estão lá (pode haver outras como alembic_version)
            if EXPECTED_TABLES.issubset(found_tables):
                 print("✅ Status: Banco de dados íntegro. Todas as tabelas esperadas estão presentes.")
            else:
                 # Caso raro onde found_tables não tem nada mas missing_tables também não (se EXPECTED fosse vazio)
                 print("✅ Status: Verificação concluída.")
            return

        print(f"⚠️  Tabelas faltando: {', '.join(missing_tables)}")
        
        # 3. Correção Automática
        print("🔄 Executando correções automáticas (Alembic Upgrade)...")
        
        # Executa o alembic via subprocess para evitar conflitos de event loop
        # e garantir que o ambiente de execução das migrações seja isolado
        process = subprocess.run(
            ["alembic", "upgrade", "head"], 
            capture_output=True, 
            text=True,
            cwd=os.getcwd() # Assume que o script é rodado da raiz do projeto api
        )
        
        if process.returncode == 0:
            print("✅ Migrações aplicadas com sucesso!")
            if process.stdout:
                print("--- Log do Alembic ---")
                print(process.stdout)
                print("----------------------")
        else:
            print("❌ Erro ao aplicar migrações:")
            print(process.stderr)
            
    except Exception as e:
        print(f"❌ Erro crítico durante a verificação: {str(e)}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    # Fix para Windows SelectorEventLoopPolicy se necessário
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    asyncio.run(check_and_fix())
