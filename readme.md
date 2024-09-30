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
    subgraph Project ["Project"]
        subgraph "Mobile App"
            A[mobile_app/lib/main.dart] --> B[screens]
            A --> C[widgets]
            A --> D[services]
            D --> E[API Services]
        end

        subgraph "Backend"
            F[backend/app/main.py] --> G[api/routes.py]
            F --> H[core/config.py]
            F --> I[core/database.py]
            
            subgraph "Hexagonal Architecture"
                J[domain/entities] --> K[domain/use_cases]
                K --> L[adapters/controllers]
                K --> M[adapters/repositories]
                L --> N[ports/input_ports]
                M --> O[ports/output_ports]
            end
            
            G --> L
            I --> M
        end

        subgraph "Stream Processing"
            P[stream_processing/flink_jobs/data_transformation.py]
            Q[stream_processing/flink_jobs/api_fetcher.py]
            R[stream_processing/kafka_config/topics.yml]
        end

        subgraph "Databases"
            S[databases/sqlite/init_schema.sql]
            T[databases/postgresql/init_schema.sql]
        end

        subgraph "Data Sync"
            U[data_sync/debezium/connector_config.json]
            V[data_sync/symmetricds/sync_config.properties]
        end

        subgraph "Deployment"
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
    classDef subgraph fill:#ffffff,stroke:#000000,stroke-width:2px;

    class A,B,C,D,E mobileApp;
    class F,G,H,I,J,K,L,M,N,O backend;
    class P,Q,R streamProcessing;
    class S,T database;
    class U,V dataSync;
    class W,X,Y,Z deployment;
    class Project,"Mobile App","Backend","Hexagonal Architecture","Stream Processing","Databases","Data Sync","Deployment" subgraph;
```
___
# System Structure based Architect
```mermaid
graph TD
    subgraph "Mobile App"
        A[mobile_app/lib/main.dart] --> B[screens]
        A --> C[widgets]
        A --> D[services]
        D --> E[API Services]
    end

    subgraph "Backend"
        F[backend/app/main.py] --> G[api/routes.py]
        F --> H[core/config.py]
        F --> I[core/database.py]
        
        subgraph "Hexagonal Architecture"
            J[domain/entities] --> K[domain/use_cases]
            K --> L[adapters/controllers]
            K --> M[adapters/repositories]
            L --> N[ports/input_ports]
            M --> O[ports/output_ports]
        end
        
        G --> L
        I --> M
    end

    subgraph "Stream Processing"
        P[stream_processing/flink_jobs/data_transformation.py]
        Q[stream_processing/flink_jobs/api_fetcher.py]
        R[stream_processing/kafka_config/topics.yml]
    end

    subgraph "Databases"
        S[databases/sqlite/init_schema.sql]
        T[databases/postgresql/init_schema.sql]
    end

    subgraph "Data Sync"
        U[data_sync/debezium/connector_config.json]
        V[data_sync/symmetricds/sync_config.properties]
    end

    subgraph "Deployment"
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

    %% Styling
    classDef mobileApp fill:#f9f,stroke:#333,stroke-width:2px;
    classDef backend fill:#bbf,stroke:#333,stroke-width:2px;
    classDef streamProcessing fill:#bfb,stroke:#333,stroke-width:2px;
    classDef database fill:#fbb,stroke:#333,stroke-width:2px;
    classDef dataSync fill:#fbf,stroke:#333,stroke-width:2px;
    classDef deployment fill:#bff,stroke:#333,stroke-width:2px;

    class A,B,C,D,E mobileApp;
    class F,G,H,I,J,K,L,M,N,O backend;
    class P,Q,R streamProcessing;
    class S,T database;
    class U,V dataSync;
    class W,X,Y,Z deployment;
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
