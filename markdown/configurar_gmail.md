# Guia Passo a Passo: Configurar Gmail para Scripts Python

Este guia detalha como configurar sua conta Gmail para permitir que scripts Python enviem e-mails ou interajam com sua conta de forma segura.

## Pré-requisitos

- **Conta Gmail:** Você precisará ter acesso à conta Gmail que deseja que o script utilize.

## Passos de Configuração (MUITO IMPORTANTE)

**Use Senhas de App (Método Recomendado):** Por razões de segurança, o Gmail exige o uso de "Senhas de App" específicas para scripts, em vez da sua senha principal.

1.  Acesse sua [Conta do Google](https://myaccount.google.com/).
2.  Navegue até **Segurança** no menu à esquerda.
3.  Na seção "Como fazer login no Google", clique em **Verificação em duas etapas**. (Você precisa ter a Verificação em duas etapas ativada para usar Senhas de App).
4.  Role a página até o final e clique em **Senhas de app**. Pode ser necessário fazer login novamente.
5.  Em "Selecionar app", escolha **Outro (nome personalizado)**.
6.  Dê um nome descritivo (ex: "Script Python Email") e clique em **Gerar**.
7.  **Copie a senha de 16 caracteres gerada.** Esta é a senha específica para o seu script.
8.  **Cole a senha de 16 caracteres gerada** como o valor da variável `GMAIL_APP_PASSWORD` dentro do arquivo `.env` do seu projeto.
    _(Observação: O script Python precisa carregar essa variáveis deste arquivo `.env`.)_
9.  Defina o valor da variável `SENDER_EMAIL`do arquivo `.env` com esse e-mail configurado.

## Lembrete de Segurança

- **Proteja Sua Senha de App:** Trate-a como uma senha normal, mas lembre-se que ela é _diferente_ da sua senha principal do Gmail. Não a compartilhe e não a coloque diretamente no seu script ou a envie para o controle de versão (como o Git).
- **Use Métodos Seguros:** Armazenar segredos como Senhas de App em variáveis de ambiente (através de arquivos `.env` ou variáveis do sistema) é uma boa prática para desenvolvimento
