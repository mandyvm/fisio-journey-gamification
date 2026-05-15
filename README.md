# FisioJourney - TCC Eng. Computação

Este repositório contém os scripts de Captura de Movimento (Mocap) em Python e a lógica da Unity para exercícios de reabilitação.

## Máquina de Estados: Exercício de Extensão de Joelho

Abaixo está a lógica de transição de estados do exercício de extensão de joelho:

```mermaid
stateDiagram-v2
    classDef repouso fill:#f9f9f9,stroke:#333,stroke-width:2px;
    classDef acao fill:#e1f5fe,stroke:#0288d1,stroke-width:2px;
    classDef avaliacao fill:#fff3e0,stroke:#f57c00,stroke-width:2px;

    [*] --> REPOUSO : Início do Exercício
    
    REPOUSO --> EXTENSAO : Paciente inicia a extensão da perna
    
    state EXTENSAO {
        [*] --> BuscandoAlvo
        BuscandoAlvo --> ColisaoRegistrada : Pé atinge a bolinha
    }
    
    EXTENSAO --> AVALIACAO : Paciente retorna a perna (Flexão)
    
    state AVALIACAO {
        state "Checagem de Condição" as if_state <<choice>>
        [*] --> if_state
        
        if_state --> ACERTO : Flag de Colisão = TRUE
        if_state --> ERRO : Flag de Colisão = FALSE
    }
    
    ACERTO --> REPOUSO : Feedback Positivo (Brilho + Frase) \n Atualiza Placar
    ERRO --> REPOUSO : Feedback Negativo (Bola some) \n Registra Falha