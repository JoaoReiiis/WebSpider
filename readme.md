# Web Crawler de Mobilidade Urbana

Este é um projeto de web crawler desenvolvido com o framework Scrapy em Python. O seu principal objetivo é navegar de forma inteligente pela web para descobrir e extrair dados de páginas e artigos relacionados a temas de mobilidade urbana, cidades inteligentes e tecnologias associadas.

## 🚀 Visão Geral

O crawler inicia sua jornada a partir de uma lista pré-definida de URLs (`start_urls`) e, de forma autônoma, navega entre os links que encontra. Ele utiliza um sistema de pontuação para decidir quais links são mais relevantes, priorizando aqueles cujos endereços ou textos âncora contenham palavras-chave sobre mobilidade.

Os dados coletados são processados e armazenados em duas etapas (ou camadas), garantindo tanto a preservação do dado bruto quanto a disponibilidade de uma versão limpa e estruturada.

## 📊 Estrutura dos Dados Coletados

Os dados são salvos em um banco de dados MongoDB em duas coleções distintas, seguindo uma arquitetura de dados em camadas: Bronze e Silver.

### 🥉 Camada Bronze (`mobilidade_bronze`)

Esta camada armazena os dados brutos, exatamente como foram coletados, sem nenhum tipo de processamento pesado. Serve como uma fonte de verdade e permite o reprocessamento dos dados no futuro.

-   `id` (String): Um identificador único para o registro (UUID).
-   `seed_url` (String): A URL inicial que originou a cadeia de rastreamento.
-   `source_domain` (String): O domínio da `seed_url`.
-   `url` (String): A URL da página que foi coletada.
-   `page_date` (String): A data de publicação extraída dos metadados da página.
-   `raw_html` (String): O conteúdo HTML completo da página.
-   `content_length` (Integer): O tamanho do conteúdo da página em bytes.
-   `redirect_chain` (List): Uma lista de URLs que mostra o caminho de redirecionamentos até a URL final.
-   `parent_url` (String): A URL da página que continha o link para a página atual.
-   `depth` (Integer): O nível de profundidade da navegação a partir da URL inicial.

### 🥈 Camada Silver (`mobilidade_silver`)

Esta camada contém dados processados, limpos e enriquecidos, prontos para análise e consumo. Os dados aqui são extraídos do HTML bruto da camada Bronze.

-   `silver_id` (String): Um identificador único para o registro Silver (UUID).
-   `bronze_id` (String): O `id` do registro correspondente na camada Bronze.
-   `url` (String): A URL da página.
-   `source_domain` (String): O domínio da `seed_url`.
-   `crawl_date` (DateTime): A data e hora em que a página foi processada.
-   `title` (String): O título do artigo ou da página.
-   `description` (String): A meta descrição da página.
-   `lang` (String): O idioma detectado da página (ex: "pt").
-   `readable_text` (String): O texto principal do artigo, limpo de tags HTML e elementos desnecessários.
-   `text_length` (Integer): O número de caracteres do `readable_text`.
-   `published_date` (DateTime): A data de publicação do artigo, quando disponível.
-   `links_internal` (List): Uma lista de links encontrados na página que apontam para o mesmo domínio.
-   `links_external` (List): Uma lista de links encontrados que apontam para outros domínios.

## 📋 Pré-requisitos

Antes de começar, certifique-se de que você tem os seguintes softwares instalados:

-   [Python 3.8+](https://www.python.org/downloads/)
-   [MongoDB](https://www.mongodb.com/try/download/community) (o banco de dados precisa estar em execução)

## ⚙️ Instalação

Siga os passos abaixo para configurar o ambiente de desenvolvimento:

1.  **Clone o repositório:**
    ```bash
    git clone <URL_DO_SEU_REPOSITORIO>
    cd WebCrawler
    ```

2.  **Crie e ative um ambiente virtual (Recomendado):**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # No Windows, use: .venv\Scripts\activate
    ```

3.  **Instale as dependências do projeto:**
    ```
    Scrapy
    pymongo
    goose3
    lxml
    ...
    ```
    Em seguida, instale-o com o pip:
    ```bash
    pip install {nome da dependências}
    ```

## 🔧 Configuração

As principais configurações do crawler podem ser ajustadas no arquivo `WebCrawler/mobilidade/mobilidade/settings.py`.

-   **Conexão com o Banco de Dados:**
    -   `MONGO_URI`: A string de conexão do seu MongoDB.
    -   `MONGO_DATABASE`: O nome do banco de dados a ser utilizado.

-   **Palavras-chave e URLs:**
    -   Para alterar as URLs iniciais, modifique a lista `start_urls` no arquivo `WebCrawler/mobilidade/mobilidade/spiders/spider.py`.
    -   Para ajustar os temas de interesse, edite as listas `MOB_KEYWORDS` (termos positivos) e `MOB_NEGATIVE_KEYWORDS` (termos a serem evitados) no arquivo de `settings.py`.

## ▶️ Como Executar

1.  **Inicie o serviço do MongoDB** na sua máquina.

2.  **Navegue até o diretório do projeto Scrapy:**
    ```bash
    cd WebCrawler/mobilidade
    ```

3.  **Execute o crawler** com o seguinte comando no seu terminal:
    ```bash
    scrapy crawl mobilidade
    ```

O crawler começará a execução, e você verá os logs da atividade no terminal. Os dados coletados serão salvos automaticamente no MongoDB.
