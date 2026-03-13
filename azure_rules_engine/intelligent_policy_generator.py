"""
Intelligent Azure Policy Generator
Analyzes scenario descriptions and generates comprehensive policies
"""

from typing import Dict, List, Optional
import re


class IntelligentPolicyGenerator:
    """Generates comprehensive policies based on scenario analysis"""
    
    def __init__(self):
        # Comprehensive resource type mappings
        self.resource_mappings = {
            # Azure Functions
            "function": [
                "Microsoft.Web/sites/hostNameBindings/*",
                "Microsoft.Web/sites/functions",
                "Microsoft.Web/sites",
                "Microsoft.Web/serverfarms",
                "Microsoft.Web/sites/sourcecontrols",
                "Microsoft.Web/sites/config",
                "Microsoft.Web/sites/functions/*",
                "Microsoft.Web/sites/basicPublishingCredentialsPolicies",
                "Microsoft.Storage/storageAccounts",
                "Microsoft.Storage/storageAccounts/blobServices",
                "Microsoft.Storage/storageAccounts/fileServices",
                "Microsoft.OperationalInsights/register/action"
            ],
            
            # Event Hub
            "eventhub": [
                "Microsoft.EventHub",
                "Microsoft.EventHub/namespaces",
                "Microsoft.EventHub/namespaces/authorizationRules/listkeys",
                "Microsoft.EventHub/namespaces/authorizationRules",
                "Microsoft.EventHub/namespaces/eventhubs",
                "Microsoft.EventHub/namespaces/write",
                "Microsoft.EventHub/register",
                "Microsoft.EventHub/namespaces/networkrulesets/write",
                "Microsoft.EventHub/namespaces/disasterRecoveryConfig",
                "Microsoft.EventHub/namespaces/disasterRecoveryConfigs/authorizationRules",
                "Microsoft.EventHub/unregister",
                "Microsoft.EventHub/sku/regions",
                "Microsoft.EventHub/operations",
                "Microsoft.EventHub/namespaces/eventhubs/authorizationRules",
                "Microsoft.EventHub/namespaces/eventhubs/authorizationRules/listkeys",
                "Microsoft.EventHub/namespaces/eventHubs/consumergroups",
                "Microsoft.EventHub/namespaces/SchemaGroups"
            ],
            
            # Key Vault
            "keyvault": [
                "Microsoft.KeyVault/vaults",
                "Microsoft.KeyVault/vaults/secrets",
                "Microsoft.KeyVault/vaults/keys",
                "Microsoft.KeyVault/vaults/certificates",
                "Microsoft.Network/privateEndpoints",
                "Microsoft.Network/privateDnsZones",
                "Microsoft.Network/privateDnsZones/virtualNetworkLinks"
            ],
            
            # SQL Database
            "sql": [
                "Microsoft.Sql/servers",
                "Microsoft.Sql/servers/firewallrules",
                "Microsoft.Sql/servers/connectionPolicies",
                "Microsoft.Sql/servers/databases",
                "Microsoft.Sql/servers/virtualNetworkRules",
                "Microsoft.Sql/servers/virtualNetworkRules/write",
                "Microsoft.Sql/servers/advancedThreatProtectionSettings",
                "Microsoft.Sql/servers/sqlVulnerabilityAssessments"
            ],
            
            # App Service
            "appservice": [
                "Microsoft.Web/serverfarms",
                "Microsoft.Web/serverfarms/*",
                "Microsoft.Web/sites",
                "Microsoft.Web/sites/config",
                "Microsoft.Web/sites/hostNameBindings/*",
                "Microsoft.Web/sites/sourcecontrols",
                "Microsoft.Web/sites/basicPublishingCredentialsPolicies",
                "Microsoft.AppService/apiApps/*",
                "Microsoft.GitHub/*"
            ],
            
            # Cosmos DB
            "cosmosdb": [
                "Microsoft.DocumentDB/databaseAccounts",
                "Microsoft.DocumentDB/databaseAccounts/services/read",
                "Microsoft.DocumentDB/databaseAccounts/services/write",
                "Microsoft.DocumentDB/databaseAccounts/services/delete",
                "Microsoft.DocumentDb/databaseAccounts/mongodbDatabases",
                "Microsoft.ServiceLinker/linkers"
            ],
            
            # Storage Account
            "storage": [
                "Microsoft.Storage/storageAccounts",
                "Microsoft.Storage/storageAccounts/blobservices",
                "Microsoft.Storage/storageAccounts/blobServices/containers",
                "Microsoft.Storage/storageAccounts/blobServices/containers/blobs",
                "Microsoft.Storage/storageAccounts/fileservices",
                "Microsoft.Storage/storageAccounts/fileServices/shares",
                "Microsoft.Storage/storageAccounts/queueServices",
                "Microsoft.Storage/storageAccounts/tableServices"
            ],
            
            # Logic Apps
            "logicapps": [
                "Microsoft.Logic/workflows",
                "Microsoft.Logic/integrationAccounts",
                "Microsoft.Storage/storageAccounts",
                "Microsoft.Web/connections"
            ],
            
            # API Management
            "apim": [
                "Microsoft.ApiManagement/service",
                "Microsoft.ApiManagement/service/apis",
                "Microsoft.ApiManagement/service/apis/operations",
                "Microsoft.ApiManagement/service/products",
                "Microsoft.ApiManagement/register",
                "Microsoft.ApiManagement/unregister"
            ],
            
            # Container Instances
            "aci": [
                "Microsoft.ContainerInstance/containerGroups",
                "Microsoft.Resources/deployments"
            ],
            
            # Azure Kubernetes Service
            "aks": [
                "Microsoft.ContainerService/managedClusters",
                "Microsoft.Network/virtualNetworks",
                "Microsoft.Network/virtualNetworks/subnets",
                "Microsoft.ManagedIdentity/userAssignedIdentities"
            ],
            
            # Virtual Network
            "vnet": [
                "Microsoft.Network/virtualNetworks",
                "Microsoft.Network/virtualNetworks/subnets",
                "Microsoft.Network/networkSecurityGroups",
                "Microsoft.Network/networkSecurityGroups/securityRules",
                "Microsoft.Network/networkInterfaces",
                "Microsoft.Network/publicIpAddresses"
            ],
            
            # DNS
            "dns": [
                "Microsoft.Network/dnsZones",
                "Microsoft.Network/dnsZones/A",
                "Microsoft.Network/dnsZones/CNAME",
                "Microsoft.Network/dnsZones/TXT",
                "Microsoft.Network/dnszones/recordsets",
                "Microsoft.Network/dnszones/all",
                "Microsoft.Network/privateDnsZones",
                "Microsoft.Network/privateDnsZones/virtualNetworkLinks",
                "Microsoft.Network/privateDnsZones/ALL",
                "Microsoft.Network/privateDnsZones/recordsets",
                "Microsoft.Network/privateDnsZones/CNAME",
                "Microsoft.Network/privateDnsZones/A",
                "Microsoft.Network/privateDnsZones/TXT"
            ],
            
            # Virtual Machines
            "vm": [
                "Microsoft.Compute/virtualMachines",
                "Microsoft.Compute/disks",
                "Microsoft.Compute/sshPublicKeys",
                "Microsoft.Network/networkInterfaces",
                "Microsoft.Network/publicIpAddresses"
            ]
        }
        
        # Always include these common resources
        self.common_resources = [
            "Microsoft.Resources/deployments",
            "Microsoft.Resources",
            "Microsoft.Network/virtualNetworks",
            "Microsoft.Network/virtualNetworks/subnets"
        ]
    
    def analyze_scenario(self, scenario: str, services: List[str]) -> List[str]:
        """Analyze scenario description and determine required resources"""
        scenario_lower = scenario.lower() if scenario else ""
        detected_resources = set()
        
        # Add common resources
        detected_resources.update(self.common_resources)
        
        # Map service names to resource types
        service_keywords = {
            "Azure Functions": "function",
            "Azure Event Hub": "eventhub",
            "Azure Key Vault": "keyvault",
            "Azure SQL Database": "sql",
            "Azure App Services": "appservice",
            "Azure Cosmos DB": "cosmosdb",
            "Storage Accounts": "storage",
            "Azure Virtual Network": "vnet",
            "DNS Zone": "dns",
            "Virtual Machines": "vm",
            "Azure Logic Apps": "logicapps",
            "Azure API Management": "apim",
            "Azure Container Instances": "aci",
            "Azure Kubernetes Service": "aks"
        }
        
        # Add resources based on selected services
        for service in services:
            keyword = service_keywords.get(service)
            if keyword and keyword in self.resource_mappings:
                detected_resources.update(self.resource_mappings[keyword])
        
        # Detect from scenario description
        keywords_in_scenario = {
            "function": ["function", "serverless", "trigger", "http trigger"],
            "eventhub": ["event hub", "telemetry", "stream", "iot"],
            "keyvault": ["key vault", "secret", "certificate", "vault"],
            "sql": ["sql", "database", "patient", "clinic"],
            "appservice": ["web app", "app service", "website"],
            "cosmosdb": ["cosmos", "nosql", "mongodb"],
            "storage": ["storage", "blob", "file share", "snapshot", "$web", "static website"],
            "vnet": ["vnet", "network", "subnet", "service endpoint"],
            "dns": ["dns", "domain", "record"],
            "vm": ["virtual machine", "vm"]
        }
        
        for keyword, triggers in keywords_in_scenario.items():
            if any(trigger in scenario_lower for trigger in triggers):
                if keyword in self.resource_mappings:
                    detected_resources.update(self.resource_mappings[keyword])
        
        # Remove duplicates and sort
        return sorted(list(detected_resources))
    
    def generate_storage_constraints(self) -> Dict:
        """Generate storage constraints"""
        # Always return storage constraints when this method is called
        # The caller (generate_comprehensive_policy) decides when to call it
        constraints = {
            "anyOf": [
                {
                    "allOf": [
                        {
                            "field": "type",
                            "equals": "Microsoft.Storage/storageAccounts"
                        },
                        {
                            "not": {
                                "allOf": [
                                    {
                                        "field": "Microsoft.Storage/storageAccounts/sku.tier",
                                        "equals": "Standard"
                                    },
                                    {
                                        "field": "Microsoft.Storage/storageAccounts/accessTier",
                                        "equals": "Hot"
                                    }
                                ]
                            }
                        }
                    ]
                },
                {
                    "allOf": [
                        {
                            "field": "type",
                            "equals": "Microsoft.Storage/storageAccounts"
                        },
                        {
                            "not": {
                                "field": "Microsoft.Storage/storageAccounts/sku.name",
                                "in": [
                                    "Standard_LRS",
                                    "Standard_GRS",
                                    "Standard_RAGRS",
                                    "Standard_ZRS"
                                ]
                            }
                        }
                    ]
                }
            ]
        }
        
        return constraints
    
    def generate_comprehensive_policy(self, services: List[str], scenario: str = "") -> Dict:
        """Generate comprehensive policy with all necessary resource types"""
        
        # Get all required resource types
        resource_types = self.analyze_scenario(scenario, services)
        
        # Check if we need storage constraints - check both scenario AND services
        needs_constraints = (
            "Storage Accounts" in services or
            "Azure Functions" in services or
            "Azure Logic Apps" in services or
            (scenario and ("storage" in scenario.lower() or "sku" in scenario.lower()))
        )
        
        storage_constraints = self.generate_storage_constraints() if needs_constraints else None
        
        # Single service - simple policy
        if len(services) == 1 and not storage_constraints:
            return {
                "if": {
                    "not": {
                        "field": "type",
                        "in": resource_types
                    }
                },
                "then": {
                    "effect": "deny"
                }
            }
        
        # Multiple services or has constraints - complex policy
        policy = {
            "if": {
                "allOf": [
                    {
                        "not": {
                            "field": "type",
                            "in": resource_types
                        }
                    }
                ]
            },
            "then": {
                "effect": "deny"
            }
        }
        
        # Add storage constraints if needed
        if storage_constraints:
            policy["if"]["allOf"].append(storage_constraints)
        
        return policy


# Global instance
intelligent_policy_generator = IntelligentPolicyGenerator()