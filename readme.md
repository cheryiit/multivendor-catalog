# case study UNIFIED_VENDOR_CATALOG
# Future implemantion plan of Architect and Structure
___
# System Architect
___
```mermaid
%%{
  init: {
    'theme': 'base',
    'themeVariables': {
      'background': '#ffffff',
      'primaryTextColor': '#000000',
      'lineColor': '#000000',
      'fontFamily': 'arial',
      'clusterBkg': '#ffffff',
      'clusterBorder': '#000000'
    }
  }
}%%
graph TD
    A[Flutter Mobile App] -->|1- Request product data| B[FastAPI Backend]
    B -->|2- Check local data| C[SQLite]
    B -->|3- Data not found| D[Kafka]
    D -->|4- Process message| E[Flink]
    E -->|5- Retrieve data| F[External Vendor APIs]
    E -->|6- Transform & unify data| E
    E -->|7- Store unified data| C
    C <-->|8- Sync data| G[PostgreSQL]

    subgraph "Local-First Architecture"
        B
        C
        D
        E
    end

    subgraph "External Systems"
        F
    end

    subgraph "Long-term Storage"
        G
    end

    H[Debezium] -->|Data replication| C
    H -->|Data replication| G
    I[SymmetricDS] -->|Data synchronization| C
    I -->|Data synchronization| G

    subgraph "Hexagonal Architecture"
        J[Domain Logic]
        K[Adapters]
        L[Ports]
        J --- K
        J --- L
        K -->|Input| B
        K -->|Output| C
        K -->|Output| D
        L -->|API| F
    end

    B -->|9- Return unified data to user| A
    C -->|10- Quick data access| B
    G -->|11- Analytics & reporting| M[Business Intelligence Tools]

    classDef primary fill:#f9f,stroke:#333,stroke-width:4px;
    classDef secondary fill:#bbf,stroke:#333,stroke-width:2px;
    classDef external fill:#ffa,stroke:#333,stroke-width:2px;

    class A,B,C,D,E primary;
    class G,H,I,J,K,L secondary;
    class F,M external;
```
___
# System Structure based Architect
```mermaid
%%{
  init: {
    'theme': 'base',
    'themeVariables': {
      'background': '#ffffff',
      'primaryTextColor': '#000000',
      'lineColor': '#000000',
      'fontFamily': 'arial',
      'clusterBkg': '#ffffff',
      'clusterBorder': '#000000'
    }
  }
}%%
graph TD
    subgraph Project ["Project"]
        subgraph MobileApp ["Mobile App"]
            A[mobile_app/lib/main.dart] --> B[screens]
            A --> C[widgets]
            A --> D[services]
            D --> E[API Services]
        end

        subgraph Backend ["Backend"]
            F[backend/app/main.py] --> G[api/routes.py]
            F --> H[core/config.py]
            F --> I[core/database.py]
            
            subgraph HexagonalArchitecture ["Hexagonal Architecture"]
                J[domain/entities] --> K[domain/use_cases]
                K --> L[adapters/controllers]
                K --> M[adapters/repositories]
                L --> N[ports/input_ports]
                M --> O[ports/output_ports]
            end
            
            G --> L
            I --> M
        end

        subgraph StreamProcessing ["Stream Processing"]
            P[stream_processing/flink_jobs/data_transformation.py]
            Q[stream_processing/flink_jobs/api_fetcher.py]
            R[stream_processing/kafka_config/topics.yml]
        end

        subgraph Databases ["Databases"]
            S[databases/sqlite/init_schema.sql]
            T[databases/postgresql/init_schema.sql]
        end

        subgraph DataSync ["Data Sync"]
            U[data_sync/debezium/connector_config.json]
            V[data_sync/symmetricds/sync_config.properties]
        end

        subgraph Deployment ["Deployment"]
            W[deployment/docker-compose.yml]
            X[deployment/kubernetes/backend-deployment.yaml]
            Y[deployment/kubernetes/flink-deployment.yaml]
            Z[deployment/kubernetes/database-deployment.yaml]
        end

        %% Interactions
        E -.-> |HTTP Requests| G
        O -.-> |Database Queries| S
        O -.-> |Database Queries| T
        Q -.-> |Fetch Data| ExternalAPI[External Vendor APIs]
        P -.-> |Process Data| Q
        P -.-> |Send/Receive Messages| R
        U -.-> |Replicate Data| S
        U -.-> |Replicate Data| T
        V -.-> |Sync Data| S
        V -.-> |Sync Data| T
        W -.-> |Deploy| F
        W -.-> |Deploy| P
        W -.-> |Deploy| Q
        X -.-> |Deploy| F
        Y -.-> |Deploy| P
        Y -.-> |Deploy| Q
        Z -.-> |Deploy| S
        Z -.-> |Deploy| T
    end

    %% Styling
    classDef mobileApp fill:#f9f,stroke:#333,stroke-width:2px;
    classDef backend fill:#bbf,stroke:#333,stroke-width:2px;
    classDef streamProcessing fill:#bfb,stroke:#333,stroke-width:2px;
    classDef database fill:#fbb,stroke:#333,stroke-width:2px;
    classDef dataSync fill:#fbf,stroke:#333,stroke-width:2px;
    classDef deployment fill:#bff,stroke:#333,stroke-width:2px;
    classDef groupBox fill:#ffffff,stroke:#000000,stroke-width:2px;

    class A,B,C,D,E mobileApp;
    class F,G,H,I,J,K,L,M,N,O backend;
    class P,Q,R streamProcessing;
    class S,T database;
    class U,V dataSync;
    class W,X,Y,Z deployment;
    class Project,MobileApp,Backend,HexagonalArchitecture,StreamProcessing,Databases,DataSync,Deployment groupBox;
```
___
# Current structure:
```
multivendor-catalog/
    .gitattributes
    docker-compose.yml
    readme.md
    requirements.txt
    backend/
        app/
            Dockerfile
            main.py
            api/
                routes.py
            core/
                config.py
                database.py
                kafka_producer.py
                postgres_database.py
        flink_jobs/
            debezium_sync.py
            flink_job.py
            debezium_connectors/
                debezium-postgres-connector.json
                debezium-sqlite-connector.json
    databases/
        postgresql/
            init_postgres_schema.sql
        sqlite/
            init_schema.sql
            products.db
            seed_data.sql
    flink/
        Dockerfile
    mobile_app/
        assets/
            images/
                image.png
        lib/
            main.dart
            screens/
                product_list_screen.dart
            services/
    multivendor-catalog/
        .gitattributes
```
