"""
azure_mcp_core.py — Azure Rules Engine
Generates validation scripts and policy JSON that EXACTLY match the
scaffolding pattern in Dec25_MS3_StAppVnet_Q4 (StAppVnet_Q4.js + webappSC_policy.json)
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any

SERVICE_CATALOGUE: Dict = {
    "app_service": {
        "display_name": "App Service", "category": "Web",
        "sdks": [{"pkg": "@azure/arm-appservice", "class": "WebSiteManagementClient", "var": "webClient"}],
        "resource_types": [
            "Microsoft.Web/serverfarms","Microsoft.Web/serverfarms/*","Microsoft.Web/sites",
            "Microsoft.Web/sites/config","Microsoft.Web/sites/hostNameBindings/*",
            "Microsoft.Web/sites/functions/*","Microsoft.Web/sites/sourcecontrols",
            "Microsoft.Web/sites/basicPublishingCredentialsPolicies",
            "Microsoft.AppService/apiApps/*","Microsoft.GitHub/*",
            "Microsoft.ServiceLinker/linkers","Microsoft.Resources/deployments",
            "Microsoft.OperationalInsights/register/action",
        ],
        "sku_constraints": [],
        "default_names": {"appServiceName": "resourceGroupName", "appSetting1": '"WEBSITE_RUN_FROM_PACKAGE"'},
        "checks": [
            {"weightage": 0.4, "name": "App Service Exists",       "fn": "check_app_service_exists"},
            {"weightage": 0.3, "name": "App Service Plan Exists",   "fn": "check_app_service_plan_exists"},
            {"weightage": 0.3, "name": "Application Settings Exist","fn": "check_app_settings"},
        ],
    },
    "virtual_networks": {
        "display_name": "Virtual Networks", "category": "Networking",
        "sdks": [{"pkg": "@azure/arm-network", "class": "NetworkManagementClient", "var": "networkClient"}],
        "resource_types": [
            "Microsoft.Network/virtualNetworks","Microsoft.Network/virtualNetworks/subnets",
            "Microsoft.Network/networkSecurityGroups","Microsoft.Network/privateDnsZones",
            "Microsoft.Network/privateEndpoints","Microsoft.Network/privateEndpoints/privateDnsZoneGroups",
            "Microsoft.Network/privateDnsZones/virtualNetworkLinks",
            "Microsoft.Network/networkInterfaces","Microsoft.Network/publicIpAddresses",
        ],
        "sku_constraints": [],
        "default_names": {"virtualnetworkname": '"health-vnet"', "subnetName": '"app-subnet"'},
        "checks": [
            {"weightage": 0.5, "name": "Virtual Network Exists", "fn": "check_vnet_exists"},
            {"weightage": 0.5, "name": "Subnet Exists",          "fn": "check_subnet_exists"},
        ],
    },
    "storage_accounts": {
        "display_name": "Storage Accounts", "category": "Storage",
        "sdks": [{"pkg": "@azure/arm-storage", "class": "StorageManagementClient", "var": "storageClient"}],
        "resource_types": [
            "Microsoft.Storage/storageAccounts","Microsoft.Storage/storageAccounts/fileServices",
            "Microsoft.Storage/storageAccounts/blobServices",
            "Microsoft.Storage/storageAccounts/blobServices/containers",
        ],
        "sku_constraints": [
            {"anyOf": [
                {"allOf": [
                    {"field": "type", "equals": "Microsoft.Storage/storageAccounts"},
                    {"not": {"allOf": [
                        {"field": "Microsoft.Storage/storageAccounts/sku.tier", "equals": "Standard"},
                        {"field": "Microsoft.Storage/storageAccounts/accessTier", "equals": "Hot"}
                    ]}}
                ]},
                {"allOf": [
                    {"field": "type", "equals": "Microsoft.Storage/storageAccounts"},
                    {"not": {"field": "Microsoft.Storage/storageAccounts/sku.name",
                             "in": ["Standard_LRS","Standard_GRS","Standard_RAGRS","Standard_ZRS"]}}
                ]}
            ]}
        ],
        "default_names": {"storageAccountName": 'resourceGroupName + "health"', "containerName": '"reports"'},
        "checks": [
            {"weightage": 0.4, "name": "Storage Account Exists", "fn": "check_storage_exists"},
            {"weightage": 0.4, "name": "Blob Container Exists",  "fn": "check_blob_container"},
            {"weightage": 0.2, "name": "Storage SKU is Standard","fn": "check_storage_sku"},
        ],
    },
    "virtual_machines": {
        "display_name": "Virtual Machines", "category": "Compute",
        "sdks": [
            {"pkg": "@azure/arm-compute", "class": "ComputeManagementClient", "var": "computeClient"},
            {"pkg": "@azure/arm-network",  "class": "NetworkManagementClient",  "var": "networkClient"},
        ],
        "resource_types": [
            "Microsoft.Compute/virtualMachines","Microsoft.Compute/virtualMachineScaleSets",
            "Microsoft.Compute/availabilitySets","Microsoft.Compute/disks",
            "Microsoft.Network/networkInterfaces","Microsoft.Network/publicIPAddresses",
            "Microsoft.Network/virtualNetworks","Microsoft.Network/networkSecurityGroups",
            "Microsoft.Resources/deployments",
        ],
        "sku_constraints": [],
        "default_names": {"vmName": 'resourceGroupName + "-vm"'},
        "checks": [
            {"weightage": 0.4, "name": "Virtual Machine Exists","fn": "check_vm_exists"},
            {"weightage": 0.3, "name": "VM is Running",         "fn": "check_vm_running"},
            {"weightage": 0.3, "name": "VM NIC Exists",         "fn": "check_vm_nic"},
        ],
    },
    "sql": {
        "display_name": "Azure SQL Database", "category": "Database",
        "sdks": [{"pkg": "@azure/arm-sql", "class": "SqlManagementClient", "var": "sqlClient"}],
        "resource_types": [
            "Microsoft.Sql/servers","Microsoft.Sql/servers/databases",
            "Microsoft.Sql/servers/firewallRules","Microsoft.Sql/servers/elasticPools",
            "Microsoft.Resources/deployments",
        ],
        "sku_constraints": [],
        "default_names": {"sqlServerName": 'resourceGroupName + "-sqlserver"', "sqlDbName": '"assessmentdb"'},
        "checks": [
            {"weightage": 0.4, "name": "SQL Server Exists",       "fn": "check_sql_server_exists"},
            {"weightage": 0.4, "name": "SQL Database Exists",     "fn": "check_sql_db_exists"},
            {"weightage": 0.2, "name": "Firewall Rule Configured","fn": "check_sql_firewall"},
        ],
    },
    "key_vault": {
        "display_name": "Key Vault", "category": "Security",
        "sdks": [{"pkg": "@azure/arm-keyvault", "class": "KeyVaultManagementClient", "var": "kvClient"}],
        "resource_types": [
            "Microsoft.KeyVault/vaults","Microsoft.KeyVault/vaults/secrets",
            "Microsoft.KeyVault/vaults/keys","Microsoft.ManagedIdentity/userAssignedIdentities",
            "Microsoft.Resources/deployments",
        ],
        "sku_constraints": [],
        "default_names": {"keyVaultName": 'resourceGroupName + "-kv"'},
        "checks": [
            {"weightage": 0.4, "name": "Key Vault Exists",            "fn": "check_keyvault_exists"},
            {"weightage": 0.3, "name": "Soft Delete Enabled",         "fn": "check_keyvault_softdelete"},
            {"weightage": 0.3, "name": "Access Policy Configured",    "fn": "check_keyvault_access_policy"},
        ],
    },
    "aks": {
        "display_name": "Azure Kubernetes Service", "category": "Containers",
        "sdks": [{"pkg": "@azure/arm-containerservice", "class": "ContainerServiceClient", "var": "aksClient"}],
        "resource_types": [
            "Microsoft.ContainerService/managedClusters",
            "Microsoft.ContainerService/managedClusters/agentPools",
            "Microsoft.ContainerRegistry/registries",
            "Microsoft.Network/virtualNetworks","Microsoft.Network/virtualNetworks/subnets",
            "Microsoft.Resources/deployments",
        ],
        "sku_constraints": [],
        "default_names": {"aksClusterName": 'resourceGroupName + "-aks"'},
        "checks": [
            {"weightage": 0.5, "name": "AKS Cluster Exists",  "fn": "check_aks_exists"},
            {"weightage": 0.3, "name": "Node Pool Running",    "fn": "check_aks_nodepool"},
            {"weightage": 0.2, "name": "RBAC Enabled",         "fn": "check_aks_rbac"},
        ],
    },
    "event_hubs": {
        "display_name": "Event Hubs", "category": "Messaging",
        "sdks": [{"pkg": "@azure/arm-eventhub", "class": "EventHubManagementClient", "var": "ehClient"}],
        "resource_types": [
            "Microsoft.EventHub/namespaces","Microsoft.EventHub/namespaces/eventhubs",
            "Microsoft.EventHub/namespaces/eventhubs/consumergroups",
            "Microsoft.Resources/deployments",
        ],
        "sku_constraints": [],
        "default_names": {"ehNamespaceName": 'resourceGroupName + "-ehns"', "ehName": '"assessment-hub"'},
        "checks": [
            {"weightage": 0.4, "name": "Event Hub Namespace Exists","fn": "check_eh_namespace"},
            {"weightage": 0.4, "name": "Event Hub Exists",          "fn": "check_eh_exists"},
            {"weightage": 0.2, "name": "Consumer Group Exists",     "fn": "check_eh_consumer_group"},
        ],
    },
    "dns": {
        "display_name": "Azure DNS", "category": "Networking",
        "sdks": [{"pkg": "@azure/arm-dns", "class": "DnsManagementClient", "var": "dnsClient"}],
        "resource_types": [
            "Microsoft.Network/dnsZones","Microsoft.Network/dnsZones/A",
            "Microsoft.Network/dnsZones/CNAME","Microsoft.Network/dnsZones/TXT",
            "Microsoft.Network/privateDnsZones",
        ],
        "sku_constraints": [],
        "default_names": {"zoneName": '"contoso.com"'},
        "checks": [
            {"weightage": 0.4, "name": "DNS Zone Exists",         "fn": "check_dns_zone"},
            {"weightage": 0.3, "name": "A Record Configured",     "fn": "check_dns_a_record"},
            {"weightage": 0.3, "name": "CNAME Record Configured", "fn": "check_dns_cname"},
        ],
    },
    "logic_apps": {
        "display_name": "Logic Apps", "category": "Serverless",
        "sdks": [{"pkg": "@azure/arm-logic", "class": "LogicManagementClient", "var": "logicClient"}],
        "resource_types": [
            "Microsoft.Logic/workflows","Microsoft.Logic/integrationAccounts",
            "Microsoft.Web/connections","Microsoft.Resources/deployments",
        ],
        "sku_constraints": [],
        "default_names": {"workflowName": 'resourceGroupName + "-workflow"'},
        "checks": [
            {"weightage": 0.5, "name": "Logic App Workflow Exists","fn": "check_logic_app_exists"},
            {"weightage": 0.3, "name": "Workflow is Enabled",      "fn": "check_logic_app_enabled"},
            {"weightage": 0.2, "name": "Trigger Configured",       "fn": "check_logic_app_trigger"},
        ],
    },
    "cosmos_db": {
        "display_name": "Cosmos DB", "category": "Database",
        "sdks": [{"pkg": "@azure/arm-cosmosdb", "class": "CosmosDBManagementClient", "var": "cosmosClient"}],
        "resource_types": [
            "Microsoft.DocumentDB/databaseAccounts",
            "Microsoft.DocumentDB/databaseAccounts/services/read",
            "Microsoft.DocumentDB/databaseAccounts/services/write",
            "Microsoft.DocumentDB/databaseAccounts/services/delete",
            "Microsoft.DocumentDb/databaseAccounts/mongodbDatabases",
            "Microsoft.Resources/deployments",
        ],
        "sku_constraints": [],
        "default_names": {"cosmosAccountName": 'resourceGroupName + "-cosmos"', "dbName": '"assessmentdb"'},
        "checks": [
            {"weightage": 0.5, "name": "Cosmos DB Account Exists", "fn": "check_cosmos_exists"},
            {"weightage": 0.3, "name": "Database Exists",          "fn": "check_cosmos_db"},
            {"weightage": 0.2, "name": "Geo-Redundancy Enabled",   "fn": "check_cosmos_geo"},
        ],
    },
    "service_bus": {
        "display_name": "Service Bus", "category": "Messaging",
        "sdks": [{"pkg": "@azure/arm-servicebus", "class": "ServiceBusManagementClient", "var": "sbClient"}],
        "resource_types": [
            "Microsoft.ServiceBus/namespaces","Microsoft.ServiceBus/namespaces/queues",
            "Microsoft.ServiceBus/namespaces/topics","Microsoft.Resources/deployments",
        ],
        "sku_constraints": [],
        "default_names": {"sbNamespaceName": 'resourceGroupName + "-sbns"', "queueName": '"assessment-queue"'},
        "checks": [
            {"weightage": 0.4, "name": "Service Bus Namespace Exists","fn": "check_sb_namespace"},
            {"weightage": 0.4, "name": "Queue Exists",                "fn": "check_sb_queue"},
            {"weightage": 0.2, "name": "Dead Letter Queue Configured","fn": "check_sb_dlq"},
        ],
    },
    "nsg": {
        "display_name": "Network Security Groups", "category": "Networking",
        "sdks": [{"pkg": "@azure/arm-network", "class": "NetworkManagementClient", "var": "networkClient"}],
        "resource_types": [
            "Microsoft.Network/networkSecurityGroups",
            "Microsoft.Network/networkSecurityGroups/securityRules",
            "Microsoft.Network/virtualNetworks","Microsoft.Resources/deployments",
        ],
        "sku_constraints": [],
        "default_names": {"nsgName": 'resourceGroupName + "-nsg"'},
        "checks": [
            {"weightage": 0.5, "name": "NSG Exists",                   "fn": "check_nsg_exists"},
            {"weightage": 0.3, "name": "Inbound Rules Configured",     "fn": "check_nsg_inbound_rules"},
            {"weightage": 0.2, "name": "NSG Associated with Subnet",   "fn": "check_nsg_subnet"},
        ],
    },
    "functions": {
        "display_name": "Azure Functions", "category": "Serverless",
        "sdks": [{"pkg": "@azure/arm-appservice", "class": "WebSiteManagementClient", "var": "webClient"}],
        "resource_types": [
            "Microsoft.Web/sites","Microsoft.Web/serverfarms",
            "Microsoft.Web/sites/functions/*","Microsoft.Storage/storageAccounts",
            "Microsoft.Resources/deployments",
        ],
        "sku_constraints": [],
        "default_names": {"functionAppName": 'resourceGroupName + "-func"'},
        "checks": [
            {"weightage": 0.4, "name": "Function App Exists",         "fn": "check_function_app_exists"},
            {"weightage": 0.3, "name": "Function App is Running",     "fn": "check_function_app_running"},
            {"weightage": 0.3, "name": "Function App Settings Exist", "fn": "check_function_app_settings"},
        ],
    },
    # ── COMBINED: App Service + VNet + Storage (exact scaffolding example) ────
    "app_service_vnet": {
        "display_name": "App Service + Virtual Network", "category": "Web + Networking",
        "sdks": [
            {"pkg": "@azure/arm-appservice", "class": "WebSiteManagementClient", "var": "webClient"},
            {"pkg": "@azure/arm-storage",    "class": "StorageManagementClient",  "var": "storageClient"},
            {"pkg": "@azure/arm-network",    "class": "NetworkManagementClient",  "var": "networkClient"},
        ],
        "resource_types": [
            "Microsoft.Web/serverfarms","Microsoft.Web/serverfarms/*","Microsoft.Web/sites",
            "Microsoft.Web/sites/config","Microsoft.Web/sites/hostNameBindings/*",
            "Microsoft.Web/sites/functions/*","Microsoft.Web/sites/sourcecontrols",
            "Microsoft.Web/sites/basicPublishingCredentialsPolicies",
            "Microsoft.AppService/apiApps/*","Microsoft.GitHub/*",
            "Microsoft.Storage/storageAccounts","Microsoft.Storage/storageAccounts/fileServices",
            "Microsoft.Storage/storageAccounts/blobServices",
            "Microsoft.Storage/storageAccounts/blobServices/containers",
            "Microsoft.Network/virtualNetworks","Microsoft.Network/virtualNetworks/subnets",
            "Microsoft.Network/networkSecurityGroups","Microsoft.Network/privateDnsZones",
            "Microsoft.Network/privateEndpoints",
            "Microsoft.Network/privateEndpoints/privateDnsZoneGroups",
            "Microsoft.Network/privateDnsZones/virtualNetworkLinks",
            "Microsoft.Network/networkInterfaces","Microsoft.Network/publicIpAddresses",
            "Microsoft.DocumentDB/databaseAccounts",
            "Microsoft.DocumentDB/databaseAccounts/services/read",
            "Microsoft.DocumentDB/databaseAccounts/services/write",
            "Microsoft.DocumentDB/databaseAccounts/services/delete",
            "Microsoft.DocumentDb/databaseAccounts/mongodbDatabases",
            "Microsoft.ServiceLinker/linkers","Microsoft.Resources/deployments",
            "Microsoft.OperationalInsights/register/action",
        ],
        "sku_constraints": [
            {"anyOf": [
                {"allOf": [
                    {"field": "type", "equals": "Microsoft.Storage/storageAccounts"},
                    {"not": {"allOf": [
                        {"field": "Microsoft.Storage/storageAccounts/sku.tier",   "equals": "Standard"},
                        {"field": "Microsoft.Storage/storageAccounts/accessTier", "equals": "Hot"}
                    ]}}
                ]},
                {"allOf": [
                    {"field": "type", "equals": "Microsoft.Storage/storageAccounts"},
                    {"not": {"field": "Microsoft.Storage/storageAccounts/sku.name",
                             "in": ["Standard_LRS","Standard_GRS","Standard_RAGRS","Standard_ZRS"]}}
                ]}
            ]}
        ],
        "default_names": {
            "appServiceName":     "resourceGroupName",
            "virtualnetworkname": '"health-vnet"',
            "subnetName":         '"app-subnet"',
            "storageAccountName": 'resourceGroupName + "health"',
            "containerName":      '"reports"',
            "appSetting1":        '"STORAGE_CONNECTION_STRING"',
        },
        "checks": [
            {"weightage": 0.1, "name": "App Service Exists",                        "fn": "check_app_service_exists"},
            {"weightage": 0.1, "name": "App Service is connected with health-vnet", "fn": "check_vnet_integration"},
            {"weightage": 0.1, "name": "Virtual Network Exists",                    "fn": "check_vnet_exists"},
            {"weightage": 0.1, "name": "Subnet Exists",                             "fn": "check_subnet_exists"},
            {"weightage": 0.2, "name": "Storage Account Exists",                    "fn": "check_storage_exists"},
            {"weightage": 0.2, "name": "Blob Container Exists",                     "fn": "check_blob_container"},
            {"weightage": 0.2, "name": "Application Settings Exist",                "fn": "check_app_settings"},
        ],
    },
}

_DISPLAY_TO_SLUG: Dict[str, str] = {v["display_name"].lower(): k for k, v in SERVICE_CATALOGUE.items()}


# ─── CHECK SNIPPETS ───────────────────────────────────────────────────────────
# Exact pattern from StAppVnet_Q4.js: one try/catch per check, validationResult[IDX]

CHECK_SNIPPETS: Dict[str, str] = {
    "check_app_service_exists": """\
        // ✅ {IDX}. Check if the App Service exists
        try {
            const app = await webClient.webApps.get(resourceGroupName, appServiceName);
            if (app && app.name === appServiceName) {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `App Service ${appServiceName} does not exist`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error fetching App Service: ${error.message}`;
        }""",

    "check_vnet_integration": """\
        // ✅ {IDX}. Check if App Service is connected specifically to health-vnet
        try {
            const vnetConnections = await webClient.webApps.listVnetConnections(resourceGroupName, appServiceName);
            const connectedToCorrectVnet = vnetConnections.some(conn =>
                conn.vnetResourceId && conn.vnetResourceId.includes(`/virtualNetworks/${virtualnetworkname}/subnets/${subnetName}`)
            );
            if (connectedToCorrectVnet) {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `App Service is NOT connected to ${virtualnetworkname}`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error fetching App Service VNet Connection: ${error.message}`;
        }""",

    "check_vnet_exists": """\
        // ✅ {IDX}. Check if the Virtual Network exists
        try {
            const vnet = await networkClient.virtualNetworks.get(resourceGroupName, virtualnetworkname);
            if (vnet && vnet.name === virtualnetworkname) {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `Virtual Network ${virtualnetworkname} does not exist`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error fetching Virtual Network: ${error.message}`;
        }""",

    "check_subnet_exists": """\
        // ✅ {IDX}. Check if subnet exists
        try {
            const subnet = await networkClient.subnets.get(resourceGroupName, virtualnetworkname, subnetName);
            if (subnet && subnet.name === subnetName) {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `Subnet ${subnetName} does not exist`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error fetching Subnet: ${error.message}`;
        }""",

    "check_storage_exists": """\
        // ✅ {IDX}. Check if the Storage Account exists
        try {
            const storage = await storageClient.storageAccounts.getProperties(resourceGroupName, storageAccountName);
            if (storage && storage.name === storageAccountName) {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `Storage Account ${storageAccountName} does not exist`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error fetching Storage Account: ${error.message}`;
        }""",

    "check_blob_container": """\
        // ✅ {IDX}. Check if the Blob Container exists
        try {
            const containerIterator = storageClient.blobContainers.list(resourceGroupName, storageAccountName);
            let containerExists = false;
            for await (const container of containerIterator) {
                if (container.name === containerName) {
                    containerExists = true;
                    break;
                }
            }
            if (containerExists) {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `Blob Container ${containerName} does not exist`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error fetching Blob Container: ${error.message}`;
        }""",

    "check_app_settings": """\
        // ✅ {IDX}. Check if the Application Settings exist
        try {
            const appSettings = await webClient.webApps.listApplicationSettings(resourceGroupName, appServiceName);
            const settings = appSettings.properties || {};
            if (settings[appSetting1]) {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `Required Application Settings not found`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error fetching App Settings: ${error.message}`;
        }""",

    "check_app_service_plan_exists": """\
        // ✅ {IDX}. Check if App Service Plan exists
        try {
            const plans = webClient.appServicePlans.listByResourceGroup(resourceGroupName);
            let found = false;
            for await (const plan of plans) { found = true; break; }
            if (found) {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `No App Service Plan found in ${resourceGroupName}`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error fetching App Service Plan: ${error.message}`;
        }""",

    "check_vm_exists": """\
        // ✅ {IDX}. Check if Virtual Machine exists
        try {
            const vm = await computeClient.virtualMachines.get(resourceGroupName, vmName);
            if (vm && vm.name === vmName) {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `VM ${vmName} does not exist`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error fetching VM: ${error.message}`;
        }""",

    "check_vm_running": """\
        // ✅ {IDX}. Check if VM is running
        try {
            const instanceView = await computeClient.virtualMachines.instanceView(resourceGroupName, vmName);
            const running = instanceView.statuses?.some(s => s.code === "PowerState/running");
            if (running) {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `VM ${vmName} is not in running state`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error checking VM state: ${error.message}`;
        }""",

    "check_vm_nic": """\
        // ✅ {IDX}. Check VM network interface
        try {
            const nics = networkClient.networkInterfaces.listByResourceGroup(resourceGroupName);
            let found = false;
            for await (const nic of nics) { found = true; break; }
            if (found) {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `No NIC found in ${resourceGroupName}`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error fetching NIC: ${error.message}`;
        }""",

    "check_sql_server_exists": """\
        // ✅ {IDX}. Check if SQL Server exists
        try {
            const server = await sqlClient.servers.get(resourceGroupName, sqlServerName);
            if (server && server.name === sqlServerName) {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `SQL Server ${sqlServerName} does not exist`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error fetching SQL Server: ${error.message}`;
        }""",

    "check_sql_db_exists": """\
        // ✅ {IDX}. Check if SQL Database exists
        try {
            const db = await sqlClient.databases.get(resourceGroupName, sqlServerName, sqlDbName);
            if (db && db.name === sqlDbName) {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `SQL Database ${sqlDbName} does not exist`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error fetching SQL Database: ${error.message}`;
        }""",

    "check_sql_firewall": """\
        // ✅ {IDX}. Check SQL firewall rules
        try {
            const rules = sqlClient.firewallRules.listByServer(resourceGroupName, sqlServerName);
            let found = false;
            for await (const rule of rules) { found = true; break; }
            if (found) {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `No firewall rules configured on ${sqlServerName}`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error fetching firewall rules: ${error.message}`;
        }""",

    "check_keyvault_exists": """\
        // ✅ {IDX}. Check if Key Vault exists
        try {
            const kv = await kvClient.vaults.get(resourceGroupName, keyVaultName);
            if (kv && kv.name === keyVaultName) {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `Key Vault ${keyVaultName} does not exist`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error fetching Key Vault: ${error.message}`;
        }""",

    "check_keyvault_softdelete": """\
        // ✅ {IDX}. Check Key Vault soft delete
        try {
            const kv = await kvClient.vaults.get(resourceGroupName, keyVaultName);
            if (kv.properties?.enableSoftDelete) {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `Soft delete is not enabled on ${keyVaultName}`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error checking soft delete: ${error.message}`;
        }""",

    "check_keyvault_access_policy": """\
        // ✅ {IDX}. Check Key Vault access policies
        try {
            const kv = await kvClient.vaults.get(resourceGroupName, keyVaultName);
            const policies = kv.properties?.accessPolicies || [];
            if (policies.length > 0) {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `No access policies configured on ${keyVaultName}`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error checking access policies: ${error.message}`;
        }""",

    "check_aks_exists": """\
        // ✅ {IDX}. Check if AKS cluster exists
        try {
            const cluster = await aksClient.managedClusters.get(resourceGroupName, aksClusterName);
            if (cluster && cluster.name === aksClusterName) {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `AKS Cluster ${aksClusterName} does not exist`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error fetching AKS Cluster: ${error.message}`;
        }""",

    "check_aks_nodepool": """\
        // ✅ {IDX}. Check AKS node pool is running
        try {
            const cluster = await aksClient.managedClusters.get(resourceGroupName, aksClusterName);
            const pools = cluster.agentPoolProfiles || [];
            const running = pools.some(p => p.provisioningState === "Succeeded");
            if (running) {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `AKS node pool is not in Succeeded state`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error checking AKS node pool: ${error.message}`;
        }""",

    "check_aks_rbac": """\
        // ✅ {IDX}. Check AKS RBAC is enabled
        try {
            const cluster = await aksClient.managedClusters.get(resourceGroupName, aksClusterName);
            if (cluster.enableRBAC) {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `RBAC is not enabled on AKS cluster ${aksClusterName}`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error checking AKS RBAC: ${error.message}`;
        }""",

    "check_eh_namespace": """\
        // ✅ {IDX}. Check if Event Hub namespace exists
        try {
            const ns = await ehClient.namespaces.get(resourceGroupName, ehNamespaceName);
            if (ns && ns.name === ehNamespaceName) {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `Event Hub Namespace ${ehNamespaceName} does not exist`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error fetching Event Hub Namespace: ${error.message}`;
        }""",

    "check_eh_exists": """\
        // ✅ {IDX}. Check if Event Hub exists
        try {
            const eh = await ehClient.eventHubs.get(resourceGroupName, ehNamespaceName, ehName);
            if (eh && eh.name === ehName) {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `Event Hub ${ehName} does not exist`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error fetching Event Hub: ${error.message}`;
        }""",

    "check_eh_consumer_group": """\
        // ✅ {IDX}. Check Event Hub consumer group
        try {
            const groups = ehClient.consumerGroups.listByEventHub(resourceGroupName, ehNamespaceName, ehName);
            let found = false;
            for await (const g of groups) { found = true; break; }
            if (found) {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `No consumer groups found on ${ehName}`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error fetching consumer groups: ${error.message}`;
        }""",

    "check_dns_zone": """\
        // ✅ {IDX}. Check if DNS Zone exists
        try {
            const zone = await dnsClient.zones.get(resourceGroupName, zoneName);
            if (zone && zone.name === zoneName) {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `DNS Zone ${zoneName} does not exist`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error fetching DNS Zone: ${error.message}`;
        }""",

    "check_dns_a_record": """\
        // ✅ {IDX}. Check A record exists
        try {
            const record = await dnsClient.recordSets.get(resourceGroupName, zoneName, "@", "A");
            if (record) {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `A record not found in zone ${zoneName}`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error fetching A record: ${error.message}`;
        }""",

    "check_dns_cname": """\
        // ✅ {IDX}. Check CNAME record exists
        try {
            const records = dnsClient.recordSets.listByType(resourceGroupName, zoneName, "CNAME");
            let found = false;
            for await (const r of records) { found = true; break; }
            if (found) {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `No CNAME records found in zone ${zoneName}`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error fetching CNAME records: ${error.message}`;
        }""",

    "check_logic_app_exists": """\
        // ✅ {IDX}. Check if Logic App workflow exists
        try {
            const workflow = await logicClient.workflows.get(resourceGroupName, workflowName);
            if (workflow && workflow.name === workflowName) {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `Logic App ${workflowName} does not exist`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error fetching Logic App: ${error.message}`;
        }""",

    "check_logic_app_enabled": """\
        // ✅ {IDX}. Check if Logic App is enabled
        try {
            const workflow = await logicClient.workflows.get(resourceGroupName, workflowName);
            if (workflow.state === "Enabled") {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `Logic App ${workflowName} is not Enabled (state: ${workflow.state})`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error checking Logic App state: ${error.message}`;
        }""",

    "check_logic_app_trigger": """\
        // ✅ {IDX}. Check Logic App triggers
        try {
            const triggers = logicClient.workflowTriggers.list(resourceGroupName, workflowName);
            let found = false;
            for await (const t of triggers) { found = true; break; }
            if (found) {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `No triggers configured on ${workflowName}`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error fetching Logic App triggers: ${error.message}`;
        }""",

    "check_cosmos_exists": """\
        // ✅ {IDX}. Check if Cosmos DB account exists
        try {
            const account = await cosmosClient.databaseAccounts.get(resourceGroupName, cosmosAccountName);
            if (account && account.name === cosmosAccountName) {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `Cosmos DB account ${cosmosAccountName} does not exist`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error fetching Cosmos DB account: ${error.message}`;
        }""",

    "check_cosmos_db": """\
        // ✅ {IDX}. Check if Cosmos database exists
        try {
            const db = await cosmosClient.sqlResources.getSqlDatabase(resourceGroupName, cosmosAccountName, dbName);
            if (db && db.name === dbName) {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `Cosmos database ${dbName} does not exist`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error fetching Cosmos database: ${error.message}`;
        }""",

    "check_cosmos_geo": """\
        // ✅ {IDX}. Check Cosmos DB geo-redundancy
        try {
            const account = await cosmosClient.databaseAccounts.get(resourceGroupName, cosmosAccountName);
            const locations = account.locations || [];
            if (locations.length > 1) {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `Cosmos DB account ${cosmosAccountName} does not have geo-redundancy`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error checking Cosmos geo-redundancy: ${error.message}`;
        }""",

    "check_sb_namespace": """\
        // ✅ {IDX}. Check if Service Bus namespace exists
        try {
            const ns = await sbClient.namespaces.get(resourceGroupName, sbNamespaceName);
            if (ns && ns.name === sbNamespaceName) {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `Service Bus Namespace ${sbNamespaceName} does not exist`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error fetching Service Bus Namespace: ${error.message}`;
        }""",

    "check_sb_queue": """\
        // ✅ {IDX}. Check if Service Bus queue exists
        try {
            const queue = await sbClient.queues.get(resourceGroupName, sbNamespaceName, queueName);
            if (queue && queue.name === queueName) {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `Queue ${queueName} does not exist`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error fetching Service Bus queue: ${error.message}`;
        }""",

    "check_sb_dlq": """\
        // ✅ {IDX}. Check dead letter queue configuration
        try {
            const queue = await sbClient.queues.get(resourceGroupName, sbNamespaceName, queueName);
            if (queue.properties?.deadLetteringOnMessageExpiration) {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `Dead letter queue not configured on ${queueName}`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error checking DLQ: ${error.message}`;
        }""",

    "check_nsg_exists": """\
        // ✅ {IDX}. Check if NSG exists
        try {
            const nsg = await networkClient.networkSecurityGroups.get(resourceGroupName, nsgName);
            if (nsg && nsg.name === nsgName) {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `NSG ${nsgName} does not exist`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error fetching NSG: ${error.message}`;
        }""",

    "check_nsg_inbound_rules": """\
        // ✅ {IDX}. Check NSG inbound security rules
        try {
            const nsg = await networkClient.networkSecurityGroups.get(resourceGroupName, nsgName);
            const rules = nsg.securityRules || [];
            const hasInbound = rules.some(r => r.direction === "Inbound");
            if (hasInbound) {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `No inbound rules configured on NSG ${nsgName}`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error checking NSG rules: ${error.message}`;
        }""",

    "check_nsg_subnet": """\
        // ✅ {IDX}. Check NSG is associated with a subnet
        try {
            const nsg = await networkClient.networkSecurityGroups.get(resourceGroupName, nsgName);
            const subnets = nsg.subnets || [];
            if (subnets.length > 0) {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `NSG ${nsgName} is not associated with any subnet`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error checking NSG subnet association: ${error.message}`;
        }""",

    "check_function_app_exists": """\
        // ✅ {IDX}. Check if Function App exists
        try {
            const app = await webClient.webApps.get(resourceGroupName, functionAppName);
            if (app && app.name === functionAppName) {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `Function App ${functionAppName} does not exist`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error fetching Function App: ${error.message}`;
        }""",

    "check_function_app_running": """\
        // ✅ {IDX}. Check if Function App is running
        try {
            const app = await webClient.webApps.get(resourceGroupName, functionAppName);
            if (app.state === "Running") {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `Function App ${functionAppName} is not Running (state: ${app.state})`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error checking Function App state: ${error.message}`;
        }""",

    "check_function_app_settings": """\
        // ✅ {IDX}. Check Function App application settings
        try {
            const settings = await webClient.webApps.listApplicationSettings(resourceGroupName, functionAppName);
            const props = settings.properties || {};
            if (Object.keys(props).length > 0) {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `No application settings found on ${functionAppName}`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error fetching Function App settings: ${error.message}`;
        }""",

    "check_storage_sku": """\
        // ✅ {IDX}. Check Storage Account SKU
        try {
            const storage = await storageClient.storageAccounts.getProperties(resourceGroupName, storageAccountName);
            const validSkus = ["Standard_LRS", "Standard_GRS", "Standard_RAGRS", "Standard_ZRS"];
            if (validSkus.includes(storage.sku?.name)) {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `Storage Account SKU ${storage.sku?.name} is not in approved list`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error checking Storage SKU: ${error.message}`;
        }""",
}


# ─── SCRIPT BUILDER ──────────────────────────────────────────────────────────

def build_validation_script(service_slugs: List[str], custom_names: Dict = None) -> str:
    configs = [SERVICE_CATALOGUE[s] for s in service_slugs if s in SERVICE_CATALOGUE]
    if not configs:
        return "// No valid services found"

    display_names = [c["display_name"] for c in configs]

    # Unique SDKs
    seen_pkgs: set = set()
    sdk_imports, client_inits = [], []
    for cfg in configs:
        for sdk in cfg["sdks"]:
            if sdk["pkg"] not in seen_pkgs:
                seen_pkgs.add(sdk["pkg"])
                sdk_imports.append(f'const {{ {sdk["class"]} }} = require("{sdk["pkg"]}");')
                client_inits.append(f'const {sdk["var"]} = new {sdk["class"]}(credentials, subscriptionId);')

    # Merge names
    names: Dict[str, str] = {}
    for cfg in configs:
        names.update(cfg.get("default_names", {}))
    if custom_names:
        names.update(custom_names)

    # Merge checks
    all_checks = []
    for cfg in configs:
        all_checks.extend(cfg.get("checks", []))

    # validationResult array
    vr_lines = ["let validationResult = ["]
    for chk in all_checks:
        vr_lines.append(f"    {{ weightage: {chk['weightage']}, name: \"{chk['name']}\", status: false, error: '' }},")
    vr_lines.append("];")

    # name declarations
    name_decls = [f"const {var} = {expr};" for var, expr in names.items()]

    # check body
    check_body = []
    for idx, chk in enumerate(all_checks):
        snippet = CHECK_SNIPPETS.get(chk.get("fn", ""))
        if snippet:
            check_body.append(snippet.replace("{IDX}", str(idx)))
            check_body.append("")

    # function name
    first = service_slugs[0].replace("_", " ").title().replace(" ", "")
    func_name = f"evaluate{first}Properties"

    lines = [
        f'const {{ ClientSecretCredential }} = require("@azure/identity");',
        *sdk_imports,
        "require('dotenv').config();",
        "",
        "// Azure AD authentication details",
        "const tenantId          = process.env.tenantId;",
        "const clientId          = process.env.clientId;",
        "const clientSecret      = process.env.clientSecret;",
        "const subscriptionId    = process.env.subscriptionId;",
        "const resourceGroupName = process.env.resourceGroupName;",
        "",
        *name_decls,
        "",
        *vr_lines,
        "",
        "const credentials = new ClientSecretCredential(tenantId, clientId, clientSecret);",
        *client_inits,
        "",
        f"async function {func_name}() {{",
        "    try {",
        "",
        "\n".join("        " + line if line.strip() else "" for line in "\n".join(check_body).splitlines()),
        "",
        "        return validationResult;",
        "",
        "    } catch (error) {",
        "        validationResult.forEach((item, index) => {",
        "            if (!item.status && !item.error) {",
        "                validationResult[index].error = `Unexpected error: ${error.message}`;",
        "            }",
        "        });",
        "    }",
        "",
        "    return validationResult;",
        "}",
        "",
        "(async () => {",
        f"    const result = await {func_name}();",
        "    console.log(result);",
        "    return result;",
        "})();",
    ]
    return "\n".join(lines)


# ─── POLICY BUILDER ──────────────────────────────────────────────────────────

def build_policy_json(service_slugs: List[str]) -> Dict:
    configs = [SERVICE_CATALOGUE[s] for s in service_slugs if s in SERVICE_CATALOGUE]
    if not configs:
        return {}

    seen: set = set()
    resource_types = []
    for cfg in configs:
        for rt in cfg.get("resource_types", []):
            if rt not in seen:
                seen.add(rt); resource_types.append(rt)

    sku_constraints = []
    for cfg in configs:
        sku_constraints.extend(cfg.get("sku_constraints", []))

    all_of = [{"not": {"field": "type", "in": resource_types}}] + sku_constraints

    if len(all_of) == 1:
        rule = {"if": all_of[0], "then": {"effect": "deny"}}
    else:
        rule = {"if": {"allOf": all_of}, "then": {"effect": "deny"}}

    return rule


# ─── RULES ENGINE ─────────────────────────────────────────────────────────────

class AzureRulesEngine:
    def __init__(self):
        self.services = SERVICE_CATALOGUE

    def _resolve_slugs(self, services: Any) -> List[str]:
        if isinstance(services, str):
            services = [services]
        slugs = []
        for s in services:
            key = s.lower().strip().replace(" ", "_").replace("-", "_")
            if key in SERVICE_CATALOGUE:
                slugs.append(key); continue
            dn = _DISPLAY_TO_SLUG.get(s.lower().strip())
            if dn:
                slugs.append(dn); continue
            m = next((k for k in SERVICE_CATALOGUE if key in k or k in key), None)
            if m:
                slugs.append(m)
        return slugs or ["app_service"]

    def get_service_names(self) -> List[str]:
        return [v["display_name"] for v in SERVICE_CATALOGUE.values()]

    def get_service_info(self, service: str) -> Optional[Dict]:
        slugs = self._resolve_slugs([service])
        if not slugs:
            return None
        cfg = SERVICE_CATALOGUE.get(slugs[0], {})
        return {"slug": slugs[0], **cfg} if cfg else None

    def generate_policy(self, services: Any) -> Dict:
        slugs = self._resolve_slugs(services)
        rule = build_policy_json(slugs)
        names = [SERVICE_CATALOGUE.get(s, {}).get("display_name", s) for s in slugs]
        rt: List[str] = []
        seen: set = set()
        for slug in slugs:
            for r in SERVICE_CATALOGUE.get(slug, {}).get("resource_types", []):
                if r not in seen:
                    seen.add(r); rt.append(r)
        return {
            "policy_type": "resource_restriction",
            "description": f"Azure Policy for {', '.join(names)}. Denies resource types not in the approved list.",
            "resource_types": rt,
            "policy_json": rule,
            "session": "",
        }

    def generate_validation_script(self, services: Any, specifications: Dict = None) -> Dict:
        slugs = self._resolve_slugs(services)
        script = build_validation_script(slugs, specifications)
        checks = []
        for slug in slugs:
            checks.extend(SERVICE_CATALOGUE.get(slug, {}).get("checks", []))
        test_cases = [{"name": c["name"], "description": c["name"], "weightage": c["weightage"], "code": ""} for c in checks]
        pkgs: set = set()
        for slug in slugs:
            for sdk in SERVICE_CATALOGUE.get(slug, {}).get("sdks", []):
                pkgs.add(sdk["pkg"])
        return {
            "language": "javascript",
            "dependencies": ["@azure/identity", "dotenv"] + sorted(pkgs),
            "test_cases": test_cases,
            "full_script": script,
            "content": script,
        }

    def generate_question(self, services: Any, difficulty: str = "intermediate", scenario: str = "") -> str:
        slugs = self._resolve_slugs(services)
        names = [SERVICE_CATALOGUE.get(s, {}).get("display_name", s) for s in slugs]
        ctx = {"beginner": "following standard configuration", "intermediate": "implementing HA and security hardening", "advanced": "designing for DR and enterprise compliance"}.get(difficulty, "with appropriate configuration")
        desc = f"Configure and deploy {' + '.join(names)} on Microsoft Azure, {ctx}."
        if scenario:
            desc += f"\n\nScenario: {scenario}"
        return desc


rules_engine = AzureRulesEngine()


if __name__ == "__main__":
    import sys
    slugs = sys.argv[1:] if len(sys.argv) > 1 else ["app_service_vnet"]
    print(f"\n=== Policy JSON for {slugs} ===\n")
    p = rules_engine.generate_policy(slugs)
    print(json.dumps(p["policy_json"], indent=2))
    print(f"\n=== Validation Script for {slugs} ===\n")
    s = rules_engine.generate_validation_script(slugs)
    print(s["full_script"])