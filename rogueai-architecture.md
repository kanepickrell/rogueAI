# RogueAI Architecture

```mermaid
flowchart TD
    classDef core fill:#4a66ac,stroke:#000000,color:#fff
    classDef offense fill:#ff6b6b,stroke:#000000,color:#000000
    classDef defense fill:#45b7d1,stroke:#000000,color:#000000
    classDef support fill:blue,stroke:#333

    RogueAI(("rogueAI Platform")):::core

    subgraph "Offensive Loop"
        ExpPath["Processes given range, solves for TTP exploit path"]:::offense
        GenMod["Generates attack module: C2 AutoLib + AI/ML + Traffic Generation"]:::offense
        Execute["Executes attack scenario"]:::offense
        Collect["Collects artifacts"]:::offense
    end

    Range318["318th Range Automation Development"]:::support
    Range90["90th UE/Realism Development"]:::support

    RogueAI --> ExpPath
    ExpPath --> GenMod
    GenMod --> Execute
    Execute --> Collect
    Collect -->|"Reinforcement Learning Data"| RogueAI


    Range318 -->|"Range/Network Configuration"| RogueAI

    Range318 -->|"Environment"| Execute
    Range90 -->|"User Emulation/Traffic Generation"| GenMod


    %% subgraph "Defensive Loop"
    %%     CPTData["CPT Data Analysis"]:::defense
    %%     DefGen["Defense Hardening Generation"]:::defense
    %%     ValTest["Validation Testing"]:::defense
    %% end

    %% RogueAI --> CPTData
    %% CPTData --> DefGen
    %% DefGen --> ValTest
    %% ValTest -->|"Defense Results"| RogueAI

    %% DefGen -->|"Hardening Config"| Range318
    %% ValTest -->|"Defense Patterns"| Range90