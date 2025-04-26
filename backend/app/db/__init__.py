from sqlmodel import create_engine, SQLModel, Session, text
from sqlalchemy.exc import OperationalError 
import os

DATABASE_URL = os.getenv('DATABASE_URL')

engine = create_engine(
    DATABASE_URL, 
)

def get_session():
    with Session(engine) as session:
        yield session

def create_all_table_and_db():
    print(f"Executing create_all_table_and_db for engine configured for: {engine.url}")

    max_retries = 10
    retry_delay = 3 # segundos

    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1}/{max_retries}: Connecting to database...")
            with Session(engine) as session:
                # 1. Testar conexão básica
                print("Testing basic connection...")
                session.execute(text("SELECT 1"))
                print("Basic connection successful.")

                # Se conectou, prossiga com a criação da tabela
                # 2. Tentar criar tabelas
                print("Attempting SQLModel.metadata.create_all...")
                SQLModel.metadata.create_all(bind=engine)
                print("SQLModel.metadata.create_all command executed.")

                # 3. Commit explícito (pode não ser necessário para DDL, mas seguro)
                # session.commit() # Commit pode não ser necessário para create_all, depende do backend e autocommit.
                # print("Session committed (or DDL auto-committed).")

                # 4. Verificar se a tabela existe
                print("Checking for table existence...")
                result = session.execute(text(
                    "SELECT EXISTS ("
                    "SELECT FROM information_schema.tables "
                    "WHERE table_schema = 'public' AND table_name = 'user_alerts')"
                )).scalar()
                print(f"Table 'user_alerts' exists check result: {result}")

                print("Database setup successful!")
                return # Sai da função se tudo deu certo

        except OperationalError as e:
            # Erro específico de conexão ou operação no DB
            print(f"!!! Connection/Operational Error (Attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("!!! Max retries reached. Could not connect to database.")
                raise # Re-levanta a exceção se todas as tentativas falharam
        except Exception as e:
             # Captura outros erros inesperados
            print(f"!!! An unexpected error occurred during table creation process: {e}")
            import traceback
            traceback.print_exc()
            raise # Re-levanta a exceção

    # Se o loop terminar sem sucesso (embora o raise deva impedir isso)
    print("!!! Database setup failed after all retries.")