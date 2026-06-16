# Estrutura do Projeto - Automação Cardápio

## 📁 Organização das Pastas

```
99food-automation-python/
│
├── 📄 README.md                 # Documentação principal do projeto
├── 📄 requirements.txt          # Dependências Python (pip install -r requirements.txt)
├── 📄 .gitignore               # Arquivos ignorados pelo Git
├── 📄 menu.py                  # Ponto de entrada principal
│
├── 📁 config/                  # Configurações da aplicação
│   ├── coordenadas.json        # Coordenadas de clique (auto-gerado)
│   └── painel.json            # Config do painel Tkinter (auto-gerado)
│
├── 📁 data/                    # Dados de entrada
│   ├── pizza.txt              # Lista de pizzas para processar
│   └── complemento.txt        # Lista de complementos
│
├── 📁 logs/                    # Logs de execução
│   └── automacao.log          # Log principal da automação
│
├── 📁 services/                # Serviços e lógica principal
│   ├── __init__.py            # Package inicializador
│   ├── automacao.py           # Lógica de automação (A CRIAR)
│   ├── painel_tkinter.py      # Painel gráfico Tkinter
│   ├── cria_cardapioNEW.py    # Automação principal
│   ├── criar_cardapio.py      # Versão antiga (DEPRECADA)
│   └── criar_complemento.py   # Processamento de complementos
│
├── 📁 utils/                   # Utilitários reutilizáveis
│   ├── __init__.py            # Package inicializador
│   ├── coordenada.py          # Captura de coordenadas
│   └── som.py                 # Sons (antes era somErro.py)
│
├── 📁 docs/                    # Documentação técnica
│   ├── ESTRUTURA.md           # Este arquivo
│   └── DESENVOLVIMENTO.md     # Guia de desenvolvimento (A CRIAR)
│
└── 📁 .git/                    # Controle de versão Git

```

## 📝 Descrição das Pastas

### `config/`
Armazena arquivos de configuração em JSON:
- **coordenadas.json**: Posições X,Y para cliques (gerado automaticamente)
- **painel.json**: Configurações do painel Tkinter (arquivo, velocidade, etc)

### `data/`
Dados de entrada para processar:
- **pizza.txt**: Lista de pizzas (uma por linha)
- **complemento.txt**: Lista de complementos

### `logs/`
Arquivos de log para debugging e auditoria:
- **automacao.log**: Registro de todas as execuções

### `services/`
Serviços e lógica principal da aplicação:
- **painel_tkinter.py** ⭐: Interface gráfica principal
- **cria_cardapioNEW.py** ⭐: Lógica de automação (a versão nova)
- criar_cardapio.py: Versão antiga (pode ser removida)
- criar_complemento.py: Processamento de complementos

### `utils/`
Utilitários reutilizáveis:
- **coordenada.py**: Captura posição do mouse
- **som.py**: Toca sons de sucesso/erro

## 🚀 Como Usar

### Primeira vez
```bash
# Instalar dependências
pip install -r requirements.txt

# Executar o programa
python menu.py
```

### Estrutura de imports
```python
# Importar de serviços
from services import painel_tkinter
from services import cria_cardapioNEW

# Importar de utilitários
from utils import coordenada
from utils import som
```

## 📋 Arquivos a Remover (opcional)

- `services/criar_cardapio.py` - Versão antiga, substituída por `cria_cardapioNEW.py`
- `interfaces/` - Pasta antiga de interfaces

## 🔄 Mudanças Aplicadas

✅ Centralizado logs em `logs/`
✅ Centralizado configs em `config/`
✅ Renomeado `somErro.py` → `som.py`
✅ Criado `.gitignore`
✅ Criado `requirements.txt`
✅ Adicionado `__init__.py` em packages
✅ Criada pasta `docs/`

## 📌 Próximos Passos

- [ ] Remover `services/criar_cardapio.py` (versão antiga)
- [ ] Remover pasta `interfaces/` se não usar mais
- [ ] Consolidar lógica em `services/automacao.py`
- [ ] Adicionar mais logging centralizado
- [ ] Criar testes unitários

