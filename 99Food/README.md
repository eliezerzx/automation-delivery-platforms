🚧 ---- EM DESENVOLVIMENTO ---- 🚧

# Estrutura do Projeto - Automação Cardápio


```
99food-automation-python/
│
├── README.md                    # Documentação principal
├── requirements.txt             # Dependências do projeto
├── .gitignore                   # Arquivos ignorados pelo git
├── main.py                      # Ponto de entrada do programa
│
├── config/                      # Configurações
│   ├── coordenadas.json
│   └── painel.json
│
├── data/                        # Dados de entrada
│   ├── pizza.txt
│   └── complemento.txt
│
├── logs/                        # Logs da aplicação
│   └── automacao.log
│
├── services/                    # Serviços/Lógica principal
│   ├── __init__.py
│   ├── automacao.py            # Lógica de automação unificada
│   ├── painel.py               # Painel Tkinter
│   └── complemento.py
│
├── utils/                       # Utilitários reutilizáveis
│   ├── __init__.py
│   ├── coordenada.py
│   ├── som.py                  # Renomeado de somErro.py
│   └── logger.py               # Logging centralizado
│
└── docs/                        # Documentação técnica
    ├── DESENVOLVIMENTO.md
    └── API.md
```

