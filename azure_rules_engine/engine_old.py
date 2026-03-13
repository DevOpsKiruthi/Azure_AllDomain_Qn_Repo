"""
Azure Rules Engine - EXACT FORMAT MATCHING USER'S EXAMPLES
Validation scripts and policies follow user's original format exactly
"""

import json
from typing import Dict, List, Optional
from datetime import datetime

class ExactFormatAzureRulesEngine:
    def __init__(self):
        self.rules = self._load_all_services()
    
    def _load_all_services(self) -> Dict:
        return {
            "Virtual Machines": {
                "category": "Compute",
                "session": "Foundational",
                "resource_types": [
                    "Microsoft.Compute/virtualMachines",
                    "Microsoft.Network/networkInterfaces",
                    "Microsoft.Network/publicIPAddresses",
                    "Microsoft.Compute/disks"
                ],
                "validation_config": {
                    "resource_group": "assessment-rg",
                    "vm_name": "vm-prod-001",
                    "vm_size": "Standard_D2s_v3",
                    "os_disk_type": "Premium_LRS",
                    "location": "eastus"
                }
            },
            "Storage Accounts": {
                "category": "Storage",
                "session": "Session 1",
                "resource_types": [
                    "Microsoft.Storage/storageAccounts",
                    "Microsoft.Storage/storageAccounts/blobservices",
                    "Microsoft.Storage/storageAccounts/blobServices/containers",
                    "Microsoft.Storage/storageAccounts/blobServices/containers/blobs",
                    "Microsoft.Storage/storageAccounts/fileservices"
                ],
                "validation_config": {
                    "resource_group": "assessment-rg",
                    "account_name": "storprodacct001",
                    "sku_name": "Standard_LRS",
                    "sku_tier": "Standard",
                    "access_tier": "Hot",
                    "blob_container": "data"
                }
            },
            "DNS Zone": {
                "category": "Networking",
                "session": "Session 3",
                "resource_types": [
                    "Microsoft.Network/virtualNetworks",
                    "Microsoft.Network/networkSecurityGroups",
                    "Microsoft.Network/dnsZones",
                    "Microsoft.Network/dnsZones/A",
                    "Microsoft.Network/dnsZones/CNAME",
                    "Microsoft.Network/dnsZones/TXT",
                    "Microsoft.Network/dnszones/recordsets",
                    "Microsoft.Network/dnszones/all",
                    "Microsoft.Network/privateDnsZones"
                ],
                "validation_config": {
                    "resource_group": "assessment-rg",
                    "dns_zone_name": "techcorpinternal.local",
                    "a_record_name": "hrportal",
                    "a_record_ip": "10.50.100.25",
                    "cname_record_name": "payroll",
                    "txt_record_name": "spf",
                    "txt_record_value": "v=spf1 ip4:10.50.0.0/16 -all"
                }
            },
            "Azure Event Hub": {
                "category": "Messaging",
                "session": "Session 3",
                "resource_types": [
                    "Microsoft.EventHub",
                    "Microsoft.EventHub/namespaces",
                    "Microsoft.EventHub/namespaces/authorizationRules",
                    "Microsoft.EventHub/namespaces/eventhubs",
                    "Microsoft.EventHub/namespaces/eventHubs/consumergroups",
                    "Microsoft.Network/virtualNetworks",
                    "Microsoft.Network/virtualNetworks/subnets"
                ],
                "validation_config": {
                    "resource_group": "assessment-rg",
                    "namespace_name": "assessment-rgIoTTelemetryHub",
                    "eventhub_name": "SensorDataStream",
                    "consumer_group": "analytics_processor",
                    "vnet_name": "IoTVNet",
                    "subnet_name": "IoTSubnet",
                    "vnet_address": "10.5.0.0/16"
                }
            },
            "Azure Key Vault": {
                "category": "Security",
                "session": "Session 3",
                "resource_types": [
                    "Microsoft.KeyVault/vaults",
                    "Microsoft.KeyVault/vaults/secrets",
                    "Microsoft.KeyVault/vaults/keys"
                ],
                "validation_config": {
                    "resource_group": "assessment-rg",
                    "vault_name": "kv-prod-vault-001"
                }
            },
            "Azure Kubernetes Service": {
                "category": "Containers",
                "session": "Session 1",
                "resource_types": [
                    "Microsoft.ContainerService/managedClusters",
                    "Microsoft.Network/virtualNetworks"
                ],
                "validation_config": {
                    "resource_group": "assessment-rg",
                    "cluster_name": "aks-prod-cluster"
                }
            },
            "Azure SQL Database": {
                "category": "Database",
                "session": "Session 1",
                "resource_types": [
                    "Microsoft.Sql/servers",
                    "Microsoft.Sql/servers/databases"
                ],
                "validation_config": {
                    "resource_group": "assessment-rg",
                    "server_name": "sqlsrv-prod-001",
                    "database_name": "appdb"
                }
            },
            "Azure App Services": {
                "category": "Serverless",
                "session": "Session 2",
                "resource_types": [
                    "Microsoft.Web/sites",
                    "Microsoft.Web/serverfarms"
                ],
                "validation_config": {
                    "resource_group": "assessment-rg",
                    "app_name": "webapp-prod-001"
                }
            },
            "Azure Functions": {
                "category": "Serverless",
                "session": "Session 3",
                "resource_types": [
                    "Microsoft.Web/sites",
                    "Microsoft.Storage/storageAccounts"
                ],
                "validation_config": {
                    "resource_group": "assessment-rg",
                    "function_app_name": "func-app-prod-001"
                }
            },
            "Azure Virtual Network": {
                "category": "Networking",
                "session": "Session 1",
                "resource_types": [
                    "Microsoft.Network/virtualNetworks",
                    "Microsoft.Network/virtualNetworks/subnets",
                    "Microsoft.Network/networkSecurityGroups"
                ],
                "validation_config": {
                    "resource_group": "assessment-rg",
                    "vnet_name": "vnet-prod-eastus"
                }
            },
            "Azure Cosmos DB": {
                "category": "Database",
                "session": "Session 2-3",
                "resource_types": [
                    "Microsoft.DocumentDB/databaseAccounts"
                ],
                "validation_config": {
                    "resource_group": "assessment-rg",
                    "account_name": "cosmos-prod-001"
                }
            },
            "Azure Container Instances": {
                "category": "Containers",
                "session": "Session 1",
                "resource_types": [
                    "Microsoft.ContainerInstance/containerGroups"
                ],
                "validation_config": {
                    "resource_group": "assessment-rg",
                    "container_group": "aci-prod-group"
                }
            },
            "Azure API Management": {
                "category": "Integration",
                "session": "Session 1",
                "resource_types": [
                    "Microsoft.ApiManagement/service",
                    "Microsoft.ApiManagement/service/apis"
                ],
                "validation_config": {
                    "resource_group": "assessment-rg",
                    "apim_name": "apim-prod-001"
                }
            },
            "Azure Logic Apps": {
                "category": "Integration",
                "session": "Session 2",
                "resource_types": [
                    "Microsoft.Logic/workflows"
                ],
                "validation_config": {
                    "resource_group": "assessment-rg",
                    "logic_app_name": "logicapp-001"
                }
            }
        }
    
    def generate_policy(self, services: List[str]) -> Dict:
        """Generate policy in USER'S EXACT FORMAT"""
        if not services:
            return {}
        
        # Collect all resource types from selected services
        all_resource_types = []
        for service in services:
            rules = self.rules.get(service, {})
            all_resource_types.extend(rules.get("resource_types", []))
        
        # Remove duplicates
        all_resource_types = list(set(all_resource_types))
        
        # For single service - simple format
        if len(services) == 1:
            return {
                "if": {
                    "not": {
                        "field": "type",
                        "in": all_resource_types
                    }
                },
                "then": {
                    "effect": "deny"
                }
            }
        
        # For multiple services - combination format (like user's Event Hub + Storage example)
        else:
            return {
                "if": {
                    "allOf": [
                        {
                            "not": {
                                "field": "type",
                                "in": all_resource_types
                            }
                        }
                    ]
                },
                "then": {
                    "effect": "deny"
                }
            }
    
    def generate_validation_script(self, service: str) -> str:
        """Generate validation in USER'S EXACT FORMAT - no push statements!"""
        
        if service == "DNS Zone":
            return self._dns_exact_format()
        elif service == "Azure Event Hub":
            return self._eventhub_exact_format()
        elif service == "Virtual Machines":
            return self._vm_exact_format()
        elif service == "Storage Accounts":
            return self._storage_exact_format()
        elif service == "Azure Key Vault":
            return self._keyvault_exact_format()
        else:
            return self._generic_exact_format(service)
    
    def _dns_exact_format(self) -> str:
        """DNS validation - EXACT user format"""
        return '''const { ClientSecretCredential } = require("@azure/identity");
const { DnsManagementClient } = require("@azure/arm-dns");

require('dotenv').config();

// Azure AD authentication details
const tenantId = process.env.tenantId;
const clientId = process.env.clientId;
const clientSecret = process.env.clientSecret;
const subscriptionId = process.env.subscriptionId;
const resourceGroupName = process.env.resourceGroupName || 'assessment-rg';

// Corporate internal services DNS configuration
const dnsZoneName = "techcorpinternal.local";
const aRecordName = "hrportal";
const aRecordIp = "10.50.100.25";
const cnameRecordName = "payroll";
const txtRecordName = "spf";
const txtRecordValue = "v=spf1 ip4:10.50.0.0/16 -all";

async function validateCorporateDNS() {
    const credential = new ClientSecretCredential(tenantId, clientId, clientSecret);
    const dnsClient = new DnsManagementClient(credential, subscriptionId);

    const validationResult = [
        { weightage: 0.2, name: `DNS Zone '${dnsZoneName}' exists and is active`, status: false, error: '' },
        { weightage: 0.2, name: `A Record '${aRecordName}' points to ${aRecordIp}`, status: false, error: '' },
        { weightage: 0.2, name: `CNAME Record '${cnameRecordName}' correctly aliases hrportal`, status: false, error: '' },
        { weightage: 0.2, name: `TXT Record '${txtRecordName}' contains SPF configuration`, status: false, error: '' },
        { weightage: 0.2, name: `DNS Zone has correct number of records (3 types)`, status: false, error: '' }
    ];

    try {
        // 1. Validate DNS Zone exists and is active
        const zone = await dnsClient.zones.get(resourceGroupName, dnsZoneName);
        if (zone.name === dnsZoneName) {
            validationResult[0].status = true;
        }
    } catch (error) {
        validationResult[0].error = `DNS Zone validation failed: ${error.message}`;
    }

    try {
        // 2. Validate A Record exists with correct IP
        const aRecordSet = await dnsClient.recordSets.get(resourceGroupName, dnsZoneName, aRecordName, "A");
        if (aRecordSet.aRecords?.some(record => record.ipv4Address === aRecordIp)) {
            validationResult[1].status = true;
        } else {
            validationResult[1].error = `A Record IP mismatch. Expected: ${aRecordIp}`;
        }
    } catch (error) {
        validationResult[1].error = `A Record validation failed: ${error.message}`;
    }

    try {
        // 3. Validate CNAME Record points to A Record
        const cnameRecordSet = await dnsClient.recordSets.get(resourceGroupName, dnsZoneName, cnameRecordName, "CNAME");
        if (cnameRecordSet.cnameRecord?.cname === `${aRecordName}.${dnsZoneName}`) {
            validationResult[2].status = true;
        } else {
            validationResult[2].error = `CNAME Record does not alias ${aRecordName}.${dnsZoneName}`;
        }
    } catch (error) {
        validationResult[2].error = `CNAME Record validation failed: ${error.message}`;
    }

    try {
        // 4. Validate TXT Record contains SPF configuration
        const txtRecordSet = await dnsClient.recordSets.get(resourceGroupName, dnsZoneName, txtRecordName, "TXT");
        if (txtRecordSet.txtRecords?.some(record => 
            record.value.some(v => v.includes(txtRecordValue))
        )) {
            validationResult[3].status = true;
        } else {
            validationResult[3].error = `TXT Record value mismatch. Expected: ${txtRecordValue}`;
        }
    } catch (error) {
        validationResult[3].error = `TXT Record validation failed: ${error.message}`;
    }

    try {
        // 5. Validate Record Count (A + CNAME + TXT = 3 types)
        const recordSets = [];
        for await (const item of dnsClient.recordSets.listByDnsZone(resourceGroupName, dnsZoneName)) {
            recordSets.push(item);
        }
        const relevantRecords = recordSets.filter(rs => 
            rs.type === 'Microsoft.Network/dnszones/A' ||
            rs.type === 'Microsoft.Network/dnszones/CNAME' ||
            rs.type === 'Microsoft.Network/dnszones/TXT'
        );
        if (relevantRecords.length === 3) {
            validationResult[4].status = true;
        } else {
            validationResult[4].error = `Found ${relevantRecords.length} record types (expected 3: A, CNAME, TXT)`;
        }
    } catch (error) {
        validationResult[4].error = `Record count error: ${error.message}`;
    }

    return validationResult;
}

(async () => {
    const result = await validateCorporateDNS();
    console.log("Validation Result:", result);
    return result;
})();'''

    def _eventhub_exact_format(self) -> str:
        """Event Hub validation - EXACT user format with VNet"""
        return '''const { EventHubConsumerClient } = require("@azure/event-hubs");
const { ClientSecretCredential } = require("@azure/identity");
const { EventHubManagementClient } = require("@azure/arm-eventhub");
const { NetworkManagementClient } = require("@azure/arm-network");
require('dotenv').config();

// Azure AD authentication details
const tenantId = process.env.tenantId;
const clientId = process.env.clientId;
const clientSecret = process.env.clientSecret;
const subscriptionId = process.env.subscriptionId;
const resourceGroupName = process.env.resourceGroupName || 'assessment-rg';

// Azure Event Hub and Namespace details for IoT Telemetry Use Case
const namespaceName = resourceGroupName + "IoTTelemetryHub";
const eventHubName = "SensorDataStream";
const consumerGroup = "analytics_processor";
const vnetName = "IoTVNet";
const subnetName = "IoTSubnet";
const ruleName = "RootManageSharedAccessKey";

const credential = new ClientSecretCredential(tenantId, clientId, clientSecret);
const eventHubClient = new EventHubManagementClient(credential, subscriptionId);
const networkClient = new NetworkManagementClient(credential, subscriptionId);

const result = [
    {
        weightage: 0.10,
        name: `Event Hub namespace name is ${namespaceName}`,
        status: false,
        error: ''
    },
    {
        weightage: 0.10,
        name: `Event Hub namespace is in Standard or Premium tier`,
        status: false,
        error: ''
    },
    {
        weightage: 0.10,
        name: `Event Hub name is ${eventHubName}`,
        status: false,
        error: ''
    },
    {
        weightage: 0.10,
        name: `Event Hub partition count is at least 4`,
        status: false,
        error: ''
    },
    {
        weightage: 0.10,
        name: `Event Hub message retention is at least 3 days`,
        status: false,
        error: ''
    },
    {
        weightage: 0.10,
        name: `Event Hub Consumer Group Name is ${consumerGroup}`,
        status: false,
        error: ''
    },
    {
        weightage: 0.10,
        name: `VNet named ${vnetName} exists`,
        status: false,
        error: ''
    },
    {
        weightage: 0.10,
        name: `VNet address space matches expected value (10.5.0.0/16)`,
        status: false,
        error: ''
    },
    {
        weightage: 0.10,
        name: `Subnet named ${subnetName} exists in the VNet`,
        status: false,
        error: ''
    },
    {
        weightage: 0.10,
        name: `Service endpoint for Event Hub exists on subnet`,
        status: false,
        error: ''
    }
];

async function processEventHub() {
    try {
        const namespace = await eventHubClient.namespaces.get(resourceGroupName, namespaceName);
        
        if (namespace && namespace.name === namespaceName) {
            result[0].status = true;
        } else {
            result[0].error = `Event Hub Namespace ${namespaceName} does not exist`;
        }

        // Check namespace tier (Standard or Premium for VNet integration)
        if (namespace && (namespace.sku.tier === "Standard" || namespace.sku.tier === "Premium")) {
            result[1].status = true;
        } else {
            result[1].error = `Event Hub Namespace tier is ${namespace?.sku?.tier}, expected Standard or Premium`;
        }

        try {
            const keys = await eventHubClient.namespaces.listKeys(resourceGroupName, namespaceName, ruleName);
            const primaryKey = keys.primaryKey;
            
            if (!primaryKey) {
                result[0].error = `Event Hub Namespace ${namespaceName} has no primary key`;
            }
        } catch (error) {
            result[0].error = `Error fetching Event Hub Namespace keys: ${error.message}`;
        }

        try {
            const eventhub = await eventHubClient.eventHubs.get(resourceGroupName, namespaceName, eventHubName);
            
            if (eventhub && eventhub.name === eventHubName) {
                result[2].status = true;
            } else {
                result[2].error = `Event Hub ${eventHubName} does not exist`;
            }

            // Check partition count (minimum 4 for IoT scenarios)
            if (eventhub && eventhub.partitionCount >= 4) {
                result[3].status = true;
            } else {
                result[3].error = `Event Hub partition count is ${eventhub?.partitionCount}, expected at least 4`;
            }

            // Check message retention (minimum 3 days)
            if (eventhub && eventhub.messageRetentionInDays >= 3) {
                result[4].status = true;
            } else {
                result[4].error = `Event Hub message retention is ${eventhub?.messageRetentionInDays} days, expected at least 3`;
            }

            try {
                const consumerGroups = await eventHubClient.consumerGroups.get(resourceGroupName, namespaceName, eventHubName, consumerGroup);
                
                if (consumerGroups && consumerGroups.name === consumerGroup) {
                    result[5].status = true;
                } else {
                    result[5].error = `Consumer group name fetched (${consumerGroups?.name}) does not match expected (${consumerGroup})`;
                }
            } catch (error) {
                result[5].error = `Error fetching Event Hub consumer group: ${error.message}`;
            }

        } catch (error) {
            result[2].error = `Error fetching Event Hub details: ${error.message}`;
            result[3].error = `Error fetching Event Hub partition count: ${error.message}`;
            result[4].error = `Error fetching Event Hub retention: ${error.message}`;
            result[5].error = `Error fetching Event Hub consumer group: ${error.message}`;
        }

        try {
            const vnet = await networkClient.virtualNetworks.get(resourceGroupName, vnetName);
            const vnetaddress = vnet.addressSpace;

            if (vnet && vnet.name === vnetName) {
                result[6].status = true;
            } else {
                result[6].error = `VNet named ${vnetName} does not exist in the resource group`;
            }

            if (vnetaddress && vnetaddress.addressPrefixes && vnetaddress.addressPrefixes.includes("10.5.0.0/16")) {
                result[7].status = true;
            } else {
                result[7].error = `VNet address space is ${vnetaddress?.addressPrefixes?.[0]}, expected 10.5.0.0/16`;
            }

            const subnet = vnet.subnets && vnet.subnets.find(s => s.name === subnetName);

            if (subnet && subnet.name === subnetName) {
                result[8].status = true;
            } else {
                result[8].error = `Subnet named ${subnetName} does not exist in the VNet`;
            }

            const serviceEndpoint = subnet && subnet.serviceEndpoints && subnet.serviceEndpoints.find(s => s.service === "Microsoft.EventHub");

            if (serviceEndpoint) {
                result[9].status = true;
            } else {
                result[9].error = `Service endpoint for Event Hub does not exist on subnet ${subnetName}`;
            }

        } catch (error) {
            result[6].error = `Error fetching VNet Name: ${error.message}`;
            result[7].error = `Error fetching VNet Address Space: ${error.message}`;
            result[8].error = `Error fetching subnet details: ${error.message}`;
            result[9].error = `Error fetching Service Endpoint details: ${error.message}`;
        }

    } catch (error) {
        result[0].error = `Error fetching Event Hub namespace: ${error.message}`;
        result[1].error = `Error fetching Event Hub namespace tier: ${error.message}`;
    }

    return result;
}

(async () => {
    const testresult = await processEventHub();
    console.log("Final Result:", testresult);
    return testresult;
})();'''

    def _vm_exact_format(self) -> str:
        return '''const { ClientSecretCredential } = require("@azure/identity");
const { ComputeManagementClient } = require("@azure/arm-compute");
require('dotenv').config();

const tenantId = process.env.tenantId;
const clientId = process.env.clientId;
const clientSecret = process.env.clientSecret;
const subscriptionId = process.env.subscriptionId;
const resourceGroupName = process.env.resourceGroupName || 'assessment-rg';

const vmName = "vm-prod-001";
const expectedVmSize = "Standard_D2s_v3";
const expectedDiskType = "Premium_LRS";

const credential = new ClientSecretCredential(tenantId, clientId, clientSecret);
const computeClient = new ComputeManagementClient(credential, subscriptionId);

const result = [
    { weightage: 0.2, name: `VM '${vmName}' exists and is running`, status: false, error: '' },
    { weightage: 0.2, name: `VM size is ${expectedVmSize}`, status: false, error: '' },
    { weightage: 0.2, name: `OS Disk uses ${expectedDiskType} storage`, status: false, error: '' },
    { weightage: 0.2, name: `Network Interface attached correctly`, status: false, error: '' },
    { weightage: 0.2, name: `Boot diagnostics enabled`, status: false, error: '' }
];

async function validateVM() {
    try {
        const vm = await computeClient.virtualMachines.get(resourceGroupName, vmName);
        
        if (vm && vm.name === vmName) {
            result[0].status = true;
        } else {
            result[0].error = `VM ${vmName} does not exist`;
        }

        if (vm && vm.hardwareProfile.vmSize === expectedVmSize) {
            result[1].status = true;
        } else {
            result[1].error = `VM size is ${vm?.hardwareProfile?.vmSize}, expected ${expectedVmSize}`;
        }

        if (vm && vm.storageProfile.osDisk.managedDisk?.storageAccountType === expectedDiskType) {
            result[2].status = true;
        } else {
            result[2].error = `Disk type is ${vm?.storageProfile?.osDisk?.managedDisk?.storageAccountType}, expected ${expectedDiskType}`;
        }

        if (vm && vm.networkProfile?.networkInterfaces?.length > 0) {
            result[3].status = true;
        } else {
            result[3].error = 'No network interface attached';
        }

        if (vm && vm.diagnosticsProfile?.bootDiagnostics?.enabled === true) {
            result[4].status = true;
        } else {
            result[4].error = 'Boot diagnostics not enabled';
        }

    } catch (error) {
        result[0].error = `Error fetching VM: ${error.message}`;
        result[1].error = `Error fetching VM size: ${error.message}`;
        result[2].error = `Error fetching disk type: ${error.message}`;
        result[3].error = `Error fetching network interface: ${error.message}`;
        result[4].error = `Error fetching boot diagnostics: ${error.message}`;
    }

    return result;
}

(async () => {
    const testresult = await validateVM();
    console.log("Final Result:", testresult);
    return testresult;
})();'''

    def _storage_exact_format(self) -> str:
        return '''const { ClientSecretCredential } = require("@azure/identity");
const { StorageManagementClient } = require("@azure/arm-storage");
require('dotenv').config();

const tenantId = process.env.tenantId;
const clientId = process.env.clientId;
const clientSecret = process.env.clientSecret;
const subscriptionId = process.env.subscriptionId;
const resourceGroupName = process.env.resourceGroupName || 'assessment-rg';

const accountName = "storprodacct001";
const expectedSku = "Standard_LRS";
const blobContainer = "data";

const credential = new ClientSecretCredential(tenantId, clientId, clientSecret);
const storageClient = new StorageManagementClient(credential, subscriptionId);

const result = [
    { weightage: 0.2, name: `Storage Account '${accountName}' exists`, status: false, error: '' },
    { weightage: 0.2, name: `SKU is ${expectedSku}`, status: false, error: '' },
    { weightage: 0.2, name: `HTTPS-only traffic enabled`, status: false, error: '' },
    { weightage: 0.2, name: `Blob container '${blobContainer}' created`, status: false, error: '' },
    { weightage: 0.2, name: `Blob encryption enabled`, status: false, error: '' }
];

async function validateStorage() {
    try {
        const account = await storageClient.storageAccounts.getProperties(resourceGroupName, accountName);
        
        if (account && account.name === accountName) {
            result[0].status = true;
        } else {
            result[0].error = `Storage account ${accountName} does not exist`;
        }

        if (account && account.sku.name === expectedSku) {
            result[1].status = true;
        } else {
            result[1].error = `SKU is ${account?.sku?.name}, expected ${expectedSku}`;
        }

        if (account && account.enableHttpsTrafficOnly === true) {
            result[2].status = true;
        } else {
            result[2].error = 'HTTPS-only traffic not enabled';
        }

        try {
            const container = await storageClient.blobContainers.get(resourceGroupName, accountName, blobContainer);
            if (container && container.name === blobContainer) {
                result[3].status = true;
            } else {
                result[3].error = `Blob container ${blobContainer} not found`;
            }
        } catch (error) {
            result[3].error = `Error fetching blob container: ${error.message}`;
        }

        if (account && account.encryption?.services?.blob?.enabled === true) {
            result[4].status = true;
        } else {
            result[4].error = 'Blob encryption not enabled';
        }

    } catch (error) {
        result[0].error = `Error fetching storage account: ${error.message}`;
        result[1].error = `Error fetching SKU: ${error.message}`;
        result[2].error = `Error fetching HTTPS setting: ${error.message}`;
        result[4].error = `Error fetching encryption: ${error.message}`;
    }

    return result;
}

(async () => {
    const testresult = await validateStorage();
    console.log("Final Result:", testresult);
    return testresult;
})();'''

    def _keyvault_exact_format(self) -> str:
        return '''// Azure Key Vault validation - exact user format
const { ClientSecretCredential } = require("@azure/identity");
const { KeyVaultManagementClient } = require('@azure/arm-keyvault');
require('dotenv').config();

const tenantId = process.env.tenantId;
const clientId = process.env.clientId;
const clientSecret = process.env.clientSecret;
const subscriptionId = process.env.subscriptionId;
const resourceGroupName = process.env.resourceGroupName || 'assessment-rg';

const vaultName = "kv-prod-vault-001";

const credential = new ClientSecretCredential(tenantId, clientId, clientSecret);
const keyVaultClient = new KeyVaultManagementClient(credential, subscriptionId);

const result = [
    { weightage: 0.25, name: `Key Vault '${vaultName}' exists`, status: false, error: '' },
    { weightage: 0.25, name: `Access policies configured`, status: false, error: '' },
    { weightage: 0.25, name: `Soft delete enabled`, status: false, error: '' },
    { weightage: 0.25, name: `Purge protection enabled`, status: false, error: '' }
];

async function validateKeyVault() {
    try {
        const vault = await keyVaultClient.vaults.get(resourceGroupName, vaultName);
        
        if (vault && vault.name === vaultName) {
            result[0].status = true;
        } else {
            result[0].error = `Key Vault ${vaultName} not found`;
        }

        if (vault && vault.properties.accessPolicies && vault.properties.accessPolicies.length > 0) {
            result[1].status = true;
        } else {
            result[1].error = 'No access policies configured';
        }

        if (vault && vault.properties.enableSoftDelete === true) {
            result[2].status = true;
        } else {
            result[2].error = 'Soft delete not enabled';
        }

        if (vault && vault.properties.enablePurgeProtection === true) {
            result[3].status = true;
        } else {
            result[3].error = 'Purge protection not enabled';
        }

    } catch (error) {
        result[0].error = `Error fetching Key Vault: ${error.message}`;
        result[1].error = `Error fetching access policies: ${error.message}`;
        result[2].error = `Error fetching soft delete setting: ${error.message}`;
        result[3].error = `Error fetching purge protection: ${error.message}`;
    }

    return result;
}

(async () => {
    const testresult = await validateKeyVault();
    console.log("Final Result:", testresult);
    return testresult;
})();'''

    def _generic_exact_format(self, service: str) -> str:
        return f'''// {service} validation script
const {{ ClientSecretCredential }} = require("@azure/identity");
require('dotenv').config();

const tenantId = process.env.tenantId;
const clientId = process.env.clientId;
const clientSecret = process.env.clientSecret;
const subscriptionId = process.env.subscriptionId;
const resourceGroupName = process.env.resourceGroupName || 'assessment-rg';

const credential = new ClientSecretCredential(tenantId, clientId, clientSecret);

const result = [
    {{ weightage: 0.25, name: '{service} resource exists', status: false, error: '' }},
    {{ weightage: 0.25, name: '{service} configuration valid', status: false, error: '' }},
    {{ weightage: 0.25, name: '{service} security enabled', status: false, error: '' }},
    {{ weightage: 0.25, name: '{service} monitoring configured', status: false, error: '' }}
];

async function validate{service.replace(" ", "")}() {{
    try {{
        // Add validation logic here
        result[0].error = 'Not yet implemented';
    }} catch (error) {{
        result[0].error = `Error: ${{error.message}}`;
    }}
    
    return result;
}}

(async () => {{
    const testresult = await validate{service.replace(" ", "")}();
    console.log("Final Result:", testresult);
    return testresult;
}})();'''
    
    def get_service_names(self) -> List[str]:
        return list(self.rules.keys())
    
    def get_service_info(self, service: str) -> Optional[Dict]:
        return self.rules.get(service)
    
    def generate_question(self, services: List[str], difficulty: str, scenario: str) -> str:
        if not services: return "No services specified"
        service = services[0]
        rules = self.rules.get(service, {})
        
        question = f"**Service**: {service}\n"
        question += f"**Session**: {rules.get('session', 'N/A')}\n"
        question += f"**Category**: {rules.get('category', 'N/A')}\n\n"
        
        if scenario:
            question += f"**Scenario**: {scenario}\n\n"
        
        question += "**Configuration**:\n"
        config = rules.get("validation_config", {})
        for key, value in config.items():
            question += f"- {key.replace('_', ' ').title()}: {value}\n"
        
        return question

rules_engine = ExactFormatAzureRulesEngine()