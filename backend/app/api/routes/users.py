from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select

from app.db import get_session
from app.schemas.users import UserCreate, UserRead, UserUpdate, DeleteResponse # Importa modelos/schemas
from app.db.user import User
from app.utils.security import get_password_hash, verify_password 
from app.schemas.endpoint_tags import EndpointTags

router = APIRouter(
    prefix="/users",
    tags=[EndpointTags.USERS],   
)

session_dependency = Annotated[Session, Depends(get_session)] 

# --- CREATE ---
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserRead)
def create_user(
    *,
    session: session_dependency,
    user_in: UserCreate # Recebe dados do corpo da requisição validados pelo UserCreate
):
    """
    Cria um novo usuário no sistema.
    - Verifica se username e email já existem.
    - Hashea a senha antes de salvar.
    """
    # Verificar se username já existe
    existing_user = session.exec(select(User).where(User.username == user_in.username)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username já registrado."
        )

    # Verificar se email já existe
    existing_email = session.exec(select(User).where(User.email == user_in.email)).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já registrado."
        )

    # Hashear a senha
    hashed_password = get_password_hash(user_in.password)

    # Criar o objeto do banco de dados (sem a senha em texto plano)
    # Usar model_dump() para converter o Pydantic model em dict, excluindo 'password'
    user_data = user_in.model_dump(exclude={"password"})
    db_user = User(**user_data, hashed_password=hashed_password)

    # Salvar no banco
    try:
        session.add(db_user)
        session.commit()
        session.refresh(db_user) # Atualiza db_user com o ID gerado pelo banco
    except Exception as e: # Captura genérica (pode ser mais específica, ex: IntegrityError)
        session.rollback()
        # Logar o erro 'e' seria ideal aqui
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao salvar usuário no banco de dados."
        )

    # Retorna os dados do usuário criado (usando UserRead para não expor o hash)
    return db_user

# --- READ (Multiple) ---
@router.get("/", response_model=List[UserRead])
def read_users(
    *,
    session: session_dependency,
    skip: int = Query(0, ge=0, description="Número de registros a pular (paginação)"),
    limit: int = Query(100, ge=1, le=200, description="Número máximo de registros a retornar")
):
    """
    Retorna uma lista de usuários com paginação.
    """
    statement = select(User).offset(skip).limit(limit)
    users = session.exec(statement).all()
    return users

# --- READ (Single) ---
@router.get("/{user_id}", response_model=UserRead)
def read_user(
    *,
    session: session_dependency,
    user_id: int
):
    """
    Retorna os detalhes de um usuário específico pelo ID.
    """
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    return db_user

# --- UPDATE ---
@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    *,
    session: session_dependency,
    user_id: int,
    user_in: UserUpdate # Recebe os dados para atualizar
):
    """
    Atualiza os dados de um usuário existente (username, email, senha).
    Permite atualização parcial (PATCH).
    """
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

    # Pega os dados enviados no corpo, excluindo os não definidos (None)
    update_data = user_in.model_dump(exclude_unset=True)

    if not update_data:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhum dado fornecido para atualização."
        )

    # Verificar conflitos de username/email se eles foram enviados para atualização
    if "username" in update_data and update_data["username"] != db_user.username:
        existing_user = session.exec(select(User).where(User.username == update_data["username"])).first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Novo username já registrado.")

    if "email" in update_data and update_data["email"] != db_user.email:
        existing_email = session.exec(select(User).where(User.email == update_data["email"])).first()
        if existing_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Novo email já registrado.")

    # Hashear a nova senha se ela foi fornecida
    if "password" in update_data:
        hashed_password = get_password_hash(update_data["password"])
        # Atualiza o campo correto no objeto do banco
        db_user.hashed_password = hashed_password
        # Remove a senha em texto plano dos dados a serem atualizados diretamente
        del update_data["password"]

    # Atualiza os outros campos do objeto db_user
    for key, value in update_data.items():
        setattr(db_user, key, value)

    # Salva as alterações
    try:
        session.add(db_user) # Adiciona o objeto modificado à sessão
        session.commit()
        session.refresh(db_user) # Recarrega os dados do banco
    except Exception as e:
        session.rollback()
        # Logar o erro 'e'
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar usuário no banco de dados."
        )

    return db_user

# --- DELETE ---
@router.delete("/{user_id}", response_model=DeleteResponse) # Ou status_code=204 e sem response_model
def delete_user(
    *,
    session: session_dependency,
    user_id: int
):
    """
    Deleta um usuário existente pelo ID.
    """
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

    try:
        session.delete(db_user)
        session.commit()
    except Exception as e:
        session.rollback()
        # Logar o erro 'e'
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao deletar usuário do banco de dados."
        )

    # Opção 1: Retornar mensagem com 200 OK
    return {"message": f"Usuário com ID {user_id} deletado com sucesso"}
    # Opção 2: Retornar 204 No Content (precisa ajustar a assinatura da função e o decorator)
    # from fastapi import Response
    # return Response(status_code=status.HTTP_204_NO_CONTENT)