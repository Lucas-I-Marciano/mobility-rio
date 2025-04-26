from sqlmodel import SQLModel, Field, Column, String, Numeric, DateTime, Time, Boolean, func, Index
from decimal import Decimal
import datetime

class UserAlert(SQLModel, table=True):
    # Nome explícito da tabela (opcional se o nome da classe em minúsculo for igual)
    __tablename__ = "user_alerts"

    # Colunas da Tabela
    id: int | None = Field(default=None, primary_key=True)
    user_email: str = Field(
        sa_column=Column(String(255), nullable=False, index=True) # Define tipo e tamanho no DB
    )
    bus_line: str = Field(sa_column=Column(String(50), nullable=False))
    stop_latitude: Decimal = Field(
        sa_column=Column(Numeric(10, 7), nullable=False) # NUMERIC(precision, scale)
    )
    stop_longitude: Decimal = Field(
        sa_column=Column(Numeric(10, 7), nullable=False)
    )
    time_window_start: datetime.time = Field(
        sa_column=Column(Time, nullable=False) # Mapeia para o tipo TIME do SQL
    )
    time_window_end: datetime.time = Field(
        sa_column=Column(Time, nullable=False)
    )
    alert_active: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, default=True) # Define default no DB
    )
    created_at: datetime.datetime | None = Field(
        default=None, # O valor será gerado pelo DB na criação
        sa_column=Column(
            DateTime(timezone=True), # TIMESTAMPTZ usa timezone
            nullable=False,
            server_default=func.now() # Equivalente a DEFAULT NOW() no DB
        )
    )
    updated_at: datetime.datetime | None = Field(
        default=None, # O valor será gerado pelo DB na criação/atualização
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(), # Default na criação
            onupdate=func.now()        # Atualiza automaticamente no DB
        )
    )

    # Definição de índices compostos ou mais complexos
    __table_args__ = (
        Index(
            "idx_user_alerts_active_time", # Nome do índice
            "alert_active",                # Colunas no índice
            "time_window_start",
            "time_window_end",
        ),
        # O índice idx_user_alerts_email foi criado com 'index=True' no campo user_email
    )