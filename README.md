# Rede de Talentos Senac Sergipe • Módulo de Migração de Dados

Módulo em Python desenvolvido para migrar dados do banco de dados legado (`[RedeDeTalentos].[dbo]`) para o novo esquema relacional (`RedeDeTalentos_DEV` / Microsoft SQL Server 2022), construído com rigor arquitetural seguindo **Clean Architecture**, **Arquitetura Hexagonal (Ports & Adapters)**, **SOLID** e **Clean Code**.

---

## 🧱 Arquitetura do Sistema

O ecossistema divide-se em 4 camadas com dependência apontando estritamente para dentro:

```
[ Interface (CLI) ]
        ↓
[ Application (Use Cases, DTOs, Factories) ]
        ↓
    [ Domain (Entities, Value Objects, Ports) ]
        ↑
[ Infrastructure (Adapters: SQL Repositories, IdMapper, Logger) ]
```

### Regras de Negócio e Transição de Schema:
1. **Descontinuação do Papel de Recruiter**:
   - No schema novo, **não existe** tabela `Recruiter` e nem role `RECRUITER` no RBAC.
   - Toda a oportunidade de emprego (`job`) pertence diretamente à organização contratante (`company_id`).
   - A coluna `RecrutadorId` da tabela antiga de vagas foi completamente eliminada.
   - Vagas legadas têm seu `company_id` resolvido via `EmpresaId`, com fallback automático pelo vínculo do recrutador à empresa caso `EmpresaId` esteja nulo.
   - Contas de recrutadores na tabela `Usuario` são filtradas e não geram contas ativas no novo banco.
2. **Normalização em 3FN**:
   - Dados corporativos de `[Empresa]` foram decompostos nas entidades `company`, `address`, `contact` e `phone`.
3. **Mapeamento de Currículos**:
   - As tabelas `experience`, `language` e `qualification` no novo schema vinculam-se diretamente a `user_id` (UUID do egresso), resolvido a partir do `AlunoId` legado.
4. **Consolidação de Trilha de Auditoria**:
   - As tabelas `[LogAdmin]`, `[LogJob]` e `[LogUser]` são unificadas na tabela única `log`.
5. **Idempotência e Reprodutibilidade**:
   - Utilização de `UUIDv5` determinístico gerado sobre namespace institucional para garantir consistência em reexecuções parciais ou integrais.

---

## 🚀 Instalação e Execução

### Pré-requisitos
- Python 3.11+
- ODBC Driver 18 (ou 17) for SQL Server

### Configuração de Ambiente
1. Copie o arquivo de exemplo de ambiente:
```bash
cp .env.example .env
```
2. Ajuste as credenciais dos bancos de dados no `.env` se necessário.

### Executando com o Ambiente Virtual
No Windows:
```cmd
run_migration.bat --help
```

Ou diretamente via Python:
```bash
# Ativar venv
.venv\Scripts\activate

# Validar conexões com os bancos
python main.py --verify

# Simular migração (Dry-Run: sem gravar no banco de destino)
python main.py --dry-run

# Executar migração completa
python main.py

# Executar etapa específica (ex: apenas usuários, apenas vagas)
python main.py --step users
python main.py --step jobs
```

---

## 🧪 Testes Automatizados

Para executar os testes unitários e de integração:
```bash
.venv\Scripts\pytest -v
```

