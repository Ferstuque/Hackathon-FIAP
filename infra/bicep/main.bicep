// ---------------------------------------------------------------------------
// IaC - HACKATHON FIAP (SOAT + IADT)
// Deploy Automatizado via GitHub Actions
// ---------------------------------------------------------------------------

param location string = resourceGroup().location
param environmentName string = 'hackathon-fiap-env'
param dbUser string = 'psqladmin'
@secure()
param dbPassword string

// 1. Log Analytics & Application Insights (Observabilidade - Requisito SOAT/IADT)
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: '${environmentName}-logs'
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
  }
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: '${environmentName}-appinsights'
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalytics.id
  }
}

// 2. Azure Storage Account (Para Uploads de Diagramas e Fila Assíncrona)
resource storageAccount 'Microsoft.Storage/storageAccounts@2022-09-01' = {
  name: 'diagstorage${uniqueString(resourceGroup().id)}'
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
}

resource queueServices 'Microsoft.Storage/storageAccounts/queueServices@2022-09-01' = {
  parent: storageAccount
  name: 'default'
}

resource analysisQueue 'Microsoft.Storage/storageAccounts/queueServices/queues@2022-09-01' = {
  parent: queueServices
  name: 'analysis-queue'
}

resource dlqQueue 'Microsoft.Storage/storageAccounts/queueServices/queues@2022-09-01' = {
  parent: queueServices
  name: 'dlq-queue'
}

// 3. PostgreSQL Flexible Server (Persistência Segregada - JSONB)
resource postgresServer 'Microsoft.DBforPostgreSQL/flexibleServers@2022-12-01-preview' = {
  name: '${environmentName}-db'
  location: location
  sku: {
    name: 'Standard_B1ms'
    tier: 'Burstable'
  }
  properties: {
    administratorLogin: dbUser
    administratorLoginPassword: dbPassword
    version: '15'
  }
}

// (As definições de AKS/Container Apps e APIM entram na expansão da infra)
