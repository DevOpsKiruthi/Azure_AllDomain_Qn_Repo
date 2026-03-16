"""
azure_mcp_core.py — Azure Rules Engine v6.0
Generates:
  1. Realistic scenario-based descriptions exactly matching real assessment question format
  2. Accurate Azure Policy JSON per service (correct resource types + SKU constraints)
  3. Real Node.js validation scripts matching the scaffolding pattern

Description format (from sample analysis):
  "As a {ROLE} [at a {COMPANY}], you are [responsible for|tasked with] {CONTEXT}.
   {SENTENCE_2}.

  Task Details:
  * {task1}
  * {task2}
  ...

  Specifications:
  * {Key}: {Value}
  ..."
"""

import json
import random
from datetime import datetime
from typing import Dict, List, Optional, Any


# ─── HELPERS ──────────────────────────────────────────────────────────────────

def _pick(lst: list) -> str:
    return random.choice(lst)

def _fill(s: str, resolved: Dict[str, str]) -> str:
    for k, v in resolved.items():
        s = s.replace("{" + k + "}", v)
    return s

def _resolve(tmpl: Dict, region: str) -> Dict[str, str]:
    r: Dict[str, str] = {"region": region}
    for k, opts in tmpl.get("vars", {}).items():
        r[k] = _pick(opts)
    return r


# ─── SCENARIO TEMPLATES ───────────────────────────────────────────────────────
# Format exactly matches sample descriptions:
#   opening   : full first paragraph (1-2 sentences)
#   task_intro: "Task Details:" or "Follow the steps below to complete the task:"
#   tasks     : list of bullet strings (filled with {var})
#   spec_intro: "Specifications:"
#   specs     : ordered list of (Key, value_template) pairs
#   regions   : pick one randomly
#   vars      : {var_name: [option1, option2, ...]}

SCENARIO_TEMPLATES: Dict[str, Dict] = {

    # ── Container Instances ───────────────────────────────────────────────────
    "container_instances": {
        "openings": [
            (
                "As an Azure Cloud Engineer, you are tasked with creating an Azure Container Instance "
                "with specific configurations to host a sample application. "
                "The container instance should be set up to run continuously and handle requests efficiently."
            ),
            (
                "As a DevOps Engineer, you have been asked to deploy a containerized workload on Azure "
                "using Azure Container Instances. "
                "The container must be configured with the correct compute allocation and restart behavior."
            ),
        ],
        "task_intro": "Task Details:",
        "tasks": [
            'Create an Azure Container Instance with your "Resource Group Name".',
            "Deploy the container instance in the {region} region.",
            "Use the image {container_image}",
            "Allocate {cpu} vCPU to the container instance.",
            "Allocate {memory} GB of memory to the container instance.",
            'Set the restart policy of the container instance to "{restart_policy}".',
        ],
        "spec_intro": "Specifications:",
        "specs": [
            ("Container Instance Name", "resource group name"),
            ("Region", "{region}"),
            ("Container Image", "{container_image}"),
            ("CPU", "{cpu} vCPU"),
            ("Memory", "{memory} GB"),
            ("Restart Policy", "{restart_policy}"),
        ],
        "regions": ["Central India", "East US", "West US 2", "Southeast Asia"],
        "vars": {
            "container_image": [
                "mcr.microsoft.com/azuredocs/aci-helloworld",
                "mcr.microsoft.com/azuredocs/aci-tutorial-app",
                "nginx:latest",
            ],
            "cpu":            ["1", "2"],
            "memory":         ["1", "2"],
            "restart_policy": ["Always", "Never", "OnFailure"],
        },
    },

    # ── Storage Accounts ──────────────────────────────────────────────────────
    "storage_accounts": {
        "openings": [
            (
                "As an Azure administrator, you have been tasked with configuring an Azure Storage account "
                "to support your company's file storage requirements. "
                "Your goal is to set up the Storage account with specific configurations to ensure "
                "secure and efficient file storage and retrieval."
            ),
            (
                "As a Cloud Storage Engineer at a media company, you are responsible for provisioning "
                "an Azure Storage account to store application assets and user-uploaded content. "
                "The account must be configured for optimal performance and durability."
            ),
            (
                "As a DevOps Engineer, you have been asked to set up a centralized Azure Storage account "
                "as the persistent backend for a data processing pipeline. "
                "Configure the account to ensure high availability and cost-effective access."
            ),
        ],
        "task_intro": "Follow the steps below to complete the task:",
        "tasks": [
            "Create an Azure Storage account with the same name of the Resource group given to you.",
            "Set the location to {region}.",
            "Configure the Storage account to use the Standard performance tier.",
            "Enable the Locally-redundant storage (LRS) replication option for enhanced data durability.",
            "Set the account access tier to 'Hot' to optimize for frequent access to the stored data.",
            'Create a Queue named "{queue_name}" in the storage account and add a message "{queue_msg}" in the queue.',
            'Unselect the option "Encode the message body in Base64"',
        ],
        "spec_intro": "Specifications:",
        "specs": [
            ("Storage Account Name", "Same as Resource Group Name"),
            ("Location", "{region}"),
            ("Performance Tier", "Standard"),
            ("Replication", "Locally-redundant storage (LRS)"),
            ("Access Tier", "Hot"),
            ("Queue Name", "{queue_name}"),
            ("Queue Message", "{queue_msg}"),
            ("Base64 Encoding", "Disabled"),
        ],
        "regions": ["West US 2", "East US", "Central India", "West Europe", "Southeast Asia"],
        "vars": {
            "queue_name": ["queue1", "tasks", "messages", "jobs"],
            "queue_msg":  ["hi", "hello", "start", "ping"],
        },
    },

    # ── Key Vault ─────────────────────────────────────────────────────────────
    "key_vault": {
        "openings": [
            (
                "As a DevOps Engineer, you are responsible for managing secure storage and access "
                "to secrets, keys, and certificates. "
                "You have been tasked with creating and configuring an Azure Key Vault with specific "
                "properties to ensure security and proper management."
            ),
            (
                "As an Azure Security Engineer at a financial services company, you are tasked with "
                "provisioning an Azure Key Vault to store application credentials, TLS certificates, "
                "and encryption keys. "
                "The vault must be hardened against unauthorized access and data loss."
            ),
            (
                "As a Cloud Administrator, you are setting up centralized secret management for a "
                "production workload running on Azure. "
                "Your task is to create and configure a Key Vault with the required security properties."
            ),
        ],
        "task_intro": "Task Details:",
        "tasks": [
            "Create an Azure Key Vault with the same name as the Resource Group provided to you.",
            "Set the location to {region}.",
            "Configure the Azure Key Vault as '{tier}' tier.",
            "Set the days to retain deleted vaults as '{retention_days}'.",
            "Disable public access to the created Azure Key Vault.",
        ],
        "spec_intro": "Specifications:",
        "specs": [
            ("Name", "[Your Resource Group Name]"),
            ("Location", "{region}"),
            ("Tier", "{tier}"),
            ("Days to Retain Deleted Vaults", "{retention_days}"),
            ("Public Access", "Disabled"),
        ],
        "regions": ["West US3", "East US 2", "North Europe", "Southeast Asia", "West Europe"],
        "vars": {
            "tier":           ["Standard", "Premium"],
            "retention_days": ["30", "60", "90"],
        },
    },

    # ── Logic Apps ────────────────────────────────────────────────────────────
    "logic_apps": {
        "openings": [
            (
                "As a DevOps Engineer at a retail company, you are responsible for managing various "
                "workflows and automation tasks. "
                "You have implemented Azure Logic Apps to handle different business operations. "
                "Your task is to evaluate and configure a specific Logic App to ensure it is set up "
                "correctly with basic properties and triggers."
            ),
            (
                "As an Integration Developer, you are tasked with building an automated approval workflow "
                "using Azure Logic Apps. "
                "The Logic App must be configured with the correct plan, location, and an HTTP trigger "
                "to receive incoming requests."
            ),
            (
                "As an Automation Engineer at a healthcare company, you are responsible for configuring "
                "Azure Logic Apps to integrate internal systems. "
                "Your task is to set up a Logic App with the required plan and trigger configuration."
            ),
        ],
        "task_intro": "Task Details:",
        "tasks": [
            "Choose the Resource Group listed for you.",
            "Configure a Logic App named with your Resource Group name, choosing the {plan} Plan.",
            'Set the location of the Logic App to "{region}".',
            'Change the current state of the Logic App to "Enabled".',
            'Create an HTTP trigger to respond to HTTP requests, selecting the Trigger type as "{trigger_type}".',
        ],
        "spec_intro": "Specifications:",
        "specs": [
            ("Name", "[Your Resource Group Name]"),
            ("Plan", "{plan} Plan"),
            ("Location", "{region}"),
            ("State", "Enabled"),
            ("Trigger Type", "{trigger_type}"),
        ],
        "regions": ["East US", "West US 2", "North Europe", "Southeast Asia", "West Europe"],
        "vars": {
            "plan":         ["Consumption", "Standard"],
            "trigger_type": ["Request", "Recurrence", "HTTP"],
        },
    },

    # ── Virtual Machines ──────────────────────────────────────────────────────
    "virtual_machines": {
        "openings": [
            (
                "As an Azure Cloud Engineer, you are tasked with provisioning a Virtual Machine "
                "to host a web application backend for your organization. "
                "The VM must be configured with the correct size, image, and network access rules."
            ),
            (
                "As an Infrastructure Engineer at a logistics company, you are responsible for "
                "deploying a Virtual Machine to run a legacy batch processing application on Azure. "
                "The VM must be set up with appropriate compute resources and security settings."
            ),
            (
                "As a Systems Administrator, you have been tasked with deploying an Azure Virtual Machine "
                "as a development environment for your engineering team. "
                "Configure the VM with the required specifications and ensure SSH access is enabled."
            ),
        ],
        "task_intro": "Task Details:",
        "tasks": [
            "Create an Azure Virtual Machine with the same name as the Resource Group provided.",
            "Set the region to {region}.",
            "Use the image '{vm_image}' for the operating system.",
            "Select the '{vm_size}' VM size.",
            "Configure authentication using SSH public key.",
            "Attach a new OS disk of type '{disk_type}'.",
            "Set the inbound port rules to allow HTTP (80) and SSH (22).",
            "Enable Boot Diagnostics using a managed storage account.",
        ],
        "spec_intro": "Specifications:",
        "specs": [
            ("Virtual Machine Name", "[Your Resource Group Name]-vm"),
            ("Region", "{region}"),
            ("Image", "{vm_image}"),
            ("VM Size", "{vm_size}"),
            ("Authentication", "SSH Public Key"),
            ("OS Disk Type", "{disk_type}"),
            ("Inbound Ports", "HTTP (80), SSH (22)"),
            ("Boot Diagnostics", "Enabled"),
        ],
        "regions": ["East US", "West US 2", "Central India", "UK South", "Southeast Asia"],
        "vars": {
            "vm_image":    [
                "Ubuntu Server 22.04 LTS",
                "Ubuntu Server 20.04 LTS",
                "Windows Server 2022 Datacenter",
            ],
            "vm_size":     ["Standard_B2s", "Standard_D2s_v3", "Standard_B1ms"],
            "disk_type":   ["Standard SSD (LRS)", "Premium SSD (LRS)", "Standard HDD (LRS)"],
        },
    },

    # ── AKS ───────────────────────────────────────────────────────────────────
    "aks": {
        "openings": [
            (
                "As a DevOps Engineer, you are tasked with deploying a managed Kubernetes cluster "
                "on Azure to orchestrate containerized microservices. "
                "The cluster must be configured with the correct node pool settings, RBAC, and monitoring."
            ),
            (
                "As a Platform Engineer at a SaaS company, you are responsible for provisioning "
                "an Azure Kubernetes Service (AKS) cluster to host multiple application workloads. "
                "Configure the cluster to meet the company's availability and security requirements."
            ),
        ],
        "task_intro": "Task Details:",
        "tasks": [
            "Create an Azure Kubernetes Service (AKS) cluster named after your Resource Group (append '-aks').",
            "Set the region to {region}.",
            "Configure the node pool with {node_count} nodes using the '{node_size}' VM size.",
            "Set the Kubernetes version to {k8s_version}.",
            "Enable RBAC on the cluster.",
            "Configure the network plugin as '{network_plugin}'.",
            "Enable the Container Insights monitoring add-on.",
            "Set the OS disk size to {disk_size} GB per node.",
        ],
        "spec_intro": "Specifications:",
        "specs": [
            ("Cluster Name", "[Resource Group Name]-aks"),
            ("Region", "{region}"),
            ("Node Count", "{node_count}"),
            ("Node VM Size", "{node_size}"),
            ("Kubernetes Version", "{k8s_version}"),
            ("RBAC", "Enabled"),
            ("Network Plugin", "{network_plugin}"),
            ("Monitoring", "Container Insights Enabled"),
            ("OS Disk Size", "{disk_size} GB"),
        ],
        "regions": ["East US 2", "West US 2", "North Europe", "Southeast Asia"],
        "vars": {
            "node_count":      ["2", "3", "1"],
            "node_size":       ["Standard_DS2_v2", "Standard_B2ms", "Standard_D4s_v3"],
            "k8s_version":     ["1.28.5", "1.27.9", "1.29.2"],
            "network_plugin":  ["kubenet", "Azure CNI"],
            "disk_size":       ["128", "256", "100"],
        },
    },

    # ── Azure SQL ─────────────────────────────────────────────────────────────
    "sql": {
        "openings": [
            (
                "As a Database Administrator, you are responsible for provisioning a managed relational "
                "database on Azure to serve as the persistent store for an e-commerce application. "
                "The database must be configured with the appropriate service tier, firewall rules, "
                "and data protection settings."
            ),
            (
                "As an Azure Data Engineer at a financial services firm, you have been tasked with "
                "deploying an Azure SQL Database to store transactional data. "
                "Ensure the database is secured, backed up appropriately, and accessible only to "
                "authorized Azure services."
            ),
        ],
        "task_intro": "Task Details:",
        "tasks": [
            "Create an Azure SQL Server named after your Resource Group (append '-sqlserver').",
            "Set the location to {region}.",
            "Set the SQL Server Admin login to '{admin_login}'.",
            "Create a SQL Database named '{db_name}' on the server.",
            "Select the '{service_tier}' service tier.",
            "Configure the firewall to allow Azure services to access the server.",
            "Enable Transparent Data Encryption (TDE) on the database.",
            "Set the backup retention to {backup_days} days.",
        ],
        "spec_intro": "Specifications:",
        "specs": [
            ("SQL Server Name", "[Resource Group Name]-sqlserver"),
            ("Location", "{region}"),
            ("Admin Login", "{admin_login}"),
            ("Database Name", "{db_name}"),
            ("Service Tier", "{service_tier}"),
            ("Firewall", "Allow Azure Services"),
            ("TDE", "Enabled"),
            ("Backup Retention", "{backup_days} days"),
        ],
        "regions": ["East US", "West US 2", "West Europe", "Southeast Asia"],
        "vars": {
            "admin_login":    ["sqladmin", "azureuser", "dbadmin"],
            "db_name":        ["assessmentdb", "appdb", "proddb", "coredb"],
            "service_tier":   ["General Purpose (GP_Gen5_2)", "Basic (B)", "Standard (S1)"],
            "backup_days":    ["7", "14", "30"],
        },
    },

    # ── App Service ───────────────────────────────────────────────────────────
    "app_service": {
        "openings": [
            (
                "As a Web Developer at a startup, you are tasked with deploying a web application "
                "using Azure App Service. "
                "Your goal is to configure the App Service with the correct runtime, plan tier, "
                "and application settings for production use."
            ),
            (
                "As a DevOps Engineer, you are responsible for migrating an on-premises web application "
                "to Azure App Service. "
                "Configure the App Service Plan, runtime stack, and security settings as required."
            ),
        ],
        "task_intro": "Task Details:",
        "tasks": [
            "Create an Azure App Service with the same name as your Resource Group.",
            "Create an App Service Plan in the '{plan_tier}' tier.",
            "Set the region to {region}.",
            "Set the runtime stack to '{runtime}'.",
            "Enable HTTPS-only access on the App Service.",
            "Set the minimum TLS version to 1.2.",
            "Configure the application setting '{app_setting_key}' with the appropriate connection string.",
        ],
        "spec_intro": "Specifications:",
        "specs": [
            ("App Service Name", "[Your Resource Group Name]"),
            ("App Service Plan Tier", "{plan_tier}"),
            ("Region", "{region}"),
            ("Runtime Stack", "{runtime}"),
            ("HTTPS Only", "Enabled"),
            ("Minimum TLS Version", "1.2"),
            ("App Setting", "{app_setting_key}"),
        ],
        "regions": ["East US", "West US 2", "Southeast Asia", "West Europe"],
        "vars": {
            "plan_tier":       ["Basic (B1)", "Standard (S1)", "Free (F1)"],
            "runtime":         ["Node.js 20 LTS", "Python 3.11", ".NET 8", "Java 17"],
            "app_setting_key": ["WEBSITE_RUN_FROM_PACKAGE", "STORAGE_CONNECTION_STRING", "API_KEY"],
        },
    },

    # ── Azure Functions ───────────────────────────────────────────────────────
    "functions": {
        "openings": [
            (
                "As a Serverless Developer, you are tasked with implementing event-driven processing "
                "using Azure Functions for a mobile application backend. "
                "The Function App must be configured with the correct hosting plan, runtime, and "
                "an HTTP trigger to accept incoming requests."
            ),
            (
                "As a DevOps Engineer at a logistics company, you are responsible for automating "
                "order processing workflows using Azure Functions. "
                "Configure the Function App with the appropriate settings and monitoring."
            ),
        ],
        "task_intro": "Task Details:",
        "tasks": [
            "Create an Azure Function App named after your Resource Group (append '-func').",
            "Set the region to {region}.",
            "Select the '{hosting_plan}' hosting plan.",
            "Set the runtime to '{runtime}' version {runtime_version}.",
            "Create an HTTP-triggered function named '{function_name}'.",
            "Set the authorization level to '{auth_level}'.",
            "Link the Function App to a Storage Account for internal state management.",
            "Enable Application Insights for monitoring and diagnostics.",
        ],
        "spec_intro": "Specifications:",
        "specs": [
            ("Function App Name", "[Resource Group Name]-func"),
            ("Region", "{region}"),
            ("Hosting Plan", "{hosting_plan}"),
            ("Runtime", "{runtime} {runtime_version}"),
            ("Function Name", "{function_name}"),
            ("Authorization Level", "{auth_level}"),
            ("Monitoring", "Application Insights Enabled"),
        ],
        "regions": ["East US", "West Europe", "Southeast Asia", "Central India"],
        "vars": {
            "hosting_plan":     ["Consumption Plan", "Premium Plan (EP1)"],
            "runtime":          ["Node.js", "Python", ".NET"],
            "runtime_version":  ["20", "3.11", "8"],
            "function_name":    ["HttpTrigger1", "ProcessRequest", "ApiHandler"],
            "auth_level":       ["Function", "Anonymous", "Admin"],
        },
    },

    # ── Event Hubs ────────────────────────────────────────────────────────────
    "event_hubs": {
        "openings": [
            (
                "As a Data Engineer, you are responsible for setting up a real-time event streaming "
                "pipeline using Azure Event Hubs. "
                "Your task is to provision an Event Hub namespace and configure the required "
                "partitions, retention, and consumer groups for a high-throughput IoT workload."
            ),
            (
                "As a Platform Engineer at a retail company, you are tasked with building an event "
                "streaming backbone using Azure Event Hubs to process clickstream data. "
                "Configure the namespace and Event Hub with the appropriate throughput and retention settings."
            ),
        ],
        "task_intro": "Task Details:",
        "tasks": [
            "Create an Event Hubs Namespace named after your Resource Group (append '-ehns').",
            "Set the region to {region}.",
            "Select the '{sku}' pricing tier.",
            "Set throughput units to {throughput}.",
            "Create an Event Hub named '{hub_name}' within the namespace.",
            "Set the partition count to {partitions}.",
            "Set the message retention to {retention} day(s).",
            "Create a consumer group named '{consumer_group}'.",
        ],
        "spec_intro": "Specifications:",
        "specs": [
            ("Namespace Name", "[Resource Group Name]-ehns"),
            ("Region", "{region}"),
            ("Pricing Tier", "{sku}"),
            ("Throughput Units", "{throughput}"),
            ("Event Hub Name", "{hub_name}"),
            ("Partition Count", "{partitions}"),
            ("Message Retention", "{retention} day(s)"),
            ("Consumer Group", "{consumer_group}"),
        ],
        "regions": ["East US", "West US 2", "West Europe", "Southeast Asia"],
        "vars": {
            "sku":            ["Standard", "Basic", "Premium"],
            "throughput":     ["1", "2", "4"],
            "hub_name":       ["assessment-hub", "telemetry", "events", "stream"],
            "partitions":     ["4", "8", "2"],
            "retention":      ["1", "3", "7"],
            "consumer_group": ["$Default", "analytics", "processor"],
        },
    },

    # ── Azure DNS ─────────────────────────────────────────────────────────────
    "dns": {
        "openings": [
            (
                "As a Network Engineer, you are tasked with configuring Azure DNS to manage domain "
                "records for a corporate website. "
                "Your goal is to create a DNS zone and configure the required record sets to ensure "
                "the domain resolves correctly."
            ),
            (
                "As an Azure Administrator, you are responsible for migrating DNS management to "
                "Azure DNS for centralized control of your organization's domain records. "
                "Configure the DNS zone with all required record types and update the domain registrar."
            ),
        ],
        "task_intro": "Task Details:",
        "tasks": [
            "Create an Azure DNS Zone for the domain '{zone_name}'.",
            "Set the resource group to the one provided to you.",
            "Create an A record pointing '@' to IP address {a_record_ip} with TTL {ttl} seconds.",
            "Create a CNAME record for 'www' pointing to '{cname_target}' with TTL {ttl} seconds.",
            "Create a TXT record for domain ownership verification.",
            "Note the Name Server (NS) records assigned by Azure and update your domain registrar.",
        ],
        "spec_intro": "Specifications:",
        "specs": [
            ("DNS Zone", "{zone_name}"),
            ("A Record", "@ → {a_record_ip} (TTL: {ttl}s)"),
            ("CNAME Record", "www → {cname_target} (TTL: {ttl}s)"),
            ("TXT Record", "Domain ownership verification"),
            ("NS Records", "Assigned by Azure — update registrar"),
        ],
        "regions": ["Global (Azure DNS is global)"],
        "vars": {
            "zone_name":    ["contoso.com", "fabrikam.net", "assessmentdomain.com"],
            "a_record_ip":  ["52.168.1.1", "40.112.10.5", "20.94.10.8"],
            "cname_target": ["contoso.azurewebsites.net", "fabrikam.azurefd.net"],
            "ttl":          ["300", "600", "3600"],
        },
    },

    # ── Cosmos DB ─────────────────────────────────────────────────────────────
    "cosmos_db": {
        "openings": [
            (
                "As an Azure Data Engineer, you are tasked with provisioning a globally distributed "
                "NoSQL database using Azure Cosmos DB for a multi-region e-commerce application. "
                "The account must be configured with geo-redundancy and the appropriate API and "
                "throughput settings."
            ),
            (
                "As a Backend Developer at a gaming company, you are responsible for setting up "
                "Azure Cosmos DB as the document store for a real-time leaderboard service. "
                "Configure the account with low-latency access and a container with the correct "
                "partition key."
            ),
        ],
        "task_intro": "Task Details:",
        "tasks": [
            "Create an Azure Cosmos DB account named after your Resource Group (append '-cosmos').",
            "Set the location to {region}.",
            "Select the '{api}' API.",
            "Choose the '{capacity_mode}' capacity mode.",
            "Enable geo-redundancy by adding a secondary read region in '{secondary_region}'.",
            "Create a database named '{db_name}'.",
            "Create a container named '{container_name}' with partition key '/{partition_key}'.",
            "Set the throughput to {throughput} RU/s.",
        ],
        "spec_intro": "Specifications:",
        "specs": [
            ("Account Name", "[Resource Group Name]-cosmos"),
            ("Region", "{region}"),
            ("API", "{api}"),
            ("Capacity Mode", "{capacity_mode}"),
            ("Secondary Region", "{secondary_region}"),
            ("Database Name", "{db_name}"),
            ("Container Name", "{container_name}"),
            ("Partition Key", "/{partition_key}"),
            ("Throughput", "{throughput} RU/s"),
        ],
        "regions": ["East US", "West US 2", "West Europe", "Southeast Asia"],
        "vars": {
            "api":              ["Core (SQL)", "MongoDB", "Gremlin"],
            "capacity_mode":    ["Provisioned Throughput", "Serverless"],
            "secondary_region": ["West US 2", "North Europe", "East Asia"],
            "db_name":          ["assessmentdb", "appdata", "coredb"],
            "container_name":   ["items", "records", "documents", "users"],
            "partition_key":    ["id", "userId", "category", "tenantId"],
            "throughput":       ["400", "1000", "4000"],
        },
    },

    # ── Virtual Networks ──────────────────────────────────────────────────────
    "virtual_networks": {
        "openings": [
            (
                "As a Network Engineer, you are tasked with setting up an Azure Virtual Network "
                "to isolate application tiers for a multi-tier web application. "
                "Configure the VNet with the correct address space, subnets, and an NSG to "
                "control inbound and outbound traffic."
            ),
            (
                "As an Azure Administrator at a manufacturing company, you are responsible for "
                "provisioning network infrastructure for a production workload. "
                "Your task is to create a Virtual Network with appropriate subnets and network "
                "security rules."
            ),
        ],
        "task_intro": "Task Details:",
        "tasks": [
            "Create an Azure Virtual Network named '{vnet_name}'.",
            "Set the region to {region}.",
            "Configure the address space as '{address_space}'.",
            "Create a subnet named '{subnet_name}' with address range '{subnet_range}'.",
            "Create a Network Security Group (NSG) named '{nsg_name}' and associate it with the subnet.",
            "Add an inbound security rule to allow HTTP (port 80) traffic.",
            "Add an inbound security rule to allow HTTPS (port 443) traffic.",
        ],
        "spec_intro": "Specifications:",
        "specs": [
            ("VNet Name", "{vnet_name}"),
            ("Region", "{region}"),
            ("Address Space", "{address_space}"),
            ("Subnet Name", "{subnet_name}"),
            ("Subnet Range", "{subnet_range}"),
            ("NSG Name", "{nsg_name}"),
            ("Inbound Rules", "Allow HTTP (80), HTTPS (443)"),
        ],
        "regions": ["East US", "West US 2", "Central India", "North Europe"],
        "vars": {
            "vnet_name":     ["health-vnet", "app-vnet", "prod-vnet"],
            "address_space": ["10.0.0.0/16", "172.16.0.0/16", "192.168.0.0/16"],
            "subnet_name":   ["app-subnet", "web-subnet", "default"],
            "subnet_range":  ["10.0.1.0/24", "172.16.1.0/24", "192.168.1.0/24"],
            "nsg_name":      ["app-nsg", "web-nsg", "default-nsg"],
        },
    },

    # ── Service Bus ───────────────────────────────────────────────────────────
    "service_bus": {
        "openings": [
            (
                "As an Integration Engineer, you are tasked with implementing reliable message-based "
                "communication between microservices using Azure Service Bus. "
                "Configure the namespace and queue with the correct settings for guaranteed "
                "message delivery and dead-letter handling."
            ),
            (
                "As a Backend Developer at an e-commerce company, you are responsible for setting up "
                "Azure Service Bus to handle asynchronous order processing. "
                "Create the Service Bus namespace and configure a queue with appropriate "
                "lock duration and dead-letter settings."
            ),
        ],
        "task_intro": "Task Details:",
        "tasks": [
            "Create a Service Bus Namespace named after your Resource Group (append '-sbns').",
            "Set the region to {region}.",
            "Select the '{sku}' pricing tier.",
            "Create a Queue named '{queue_name}'.",
            "Enable Dead Letter Queue on message expiration.",
            "Set the message lock duration to '{lock_duration}'.",
            "Set the maximum message size to {max_size} KB.",
        ],
        "spec_intro": "Specifications:",
        "specs": [
            ("Namespace Name", "[Resource Group Name]-sbns"),
            ("Region", "{region}"),
            ("Pricing Tier", "{sku}"),
            ("Queue Name", "{queue_name}"),
            ("Dead Letter Queue", "Enabled on expiration"),
            ("Lock Duration", "{lock_duration}"),
            ("Max Message Size", "{max_size} KB"),
        ],
        "regions": ["East US", "West US 2", "North Europe", "Southeast Asia"],
        "vars": {
            "sku":           ["Standard", "Premium", "Basic"],
            "queue_name":    ["assessment-queue", "orders", "tasks", "notifications"],
            "lock_duration": ["PT1M", "PT5M", "PT30S"],
            "max_size":      ["256", "1024", "64"],
        },
    },

    # ── NSG ───────────────────────────────────────────────────────────────────
    "nsg": {
        "openings": [
            (
                "As a Network Security Engineer, you are responsible for securing network traffic "
                "to a virtual machine deployment using Azure Network Security Groups. "
                "Your task is to create an NSG with specific inbound rules and associate it with "
                "the target subnet."
            ),
            (
                "As an Azure Administrator, you are implementing perimeter security for an application "
                "subnet using Network Security Groups. "
                "Configure the NSG rules to enforce least-privilege access and block unnecessary traffic."
            ),
        ],
        "task_intro": "Task Details:",
        "tasks": [
            "Create a Network Security Group named '{nsg_name}'.",
            "Set the region to {region}.",
            "Add an inbound rule to allow SSH (port 22) with priority {ssh_priority}.",
            "Add an inbound rule to allow HTTP (port 80) from any source with priority {http_priority}.",
            "Add an inbound rule to allow HTTPS (port 443) from any source with priority {https_priority}.",
            "Associate the NSG with the subnet '{subnet_name}'.",
        ],
        "spec_intro": "Specifications:",
        "specs": [
            ("NSG Name", "{nsg_name}"),
            ("Region", "{region}"),
            ("Inbound Rule: SSH",   "Port 22 (Priority {ssh_priority})"),
            ("Inbound Rule: HTTP",  "Port 80, Any Source (Priority {http_priority})"),
            ("Inbound Rule: HTTPS", "Port 443, Any Source (Priority {https_priority})"),
            ("Associated Subnet", "{subnet_name}"),
        ],
        "regions": ["East US", "West US 2", "Central India", "West Europe"],
        "vars": {
            "nsg_name":      ["app-nsg", "web-nsg", "vm-nsg"],
            "subnet_name":   ["app-subnet", "default", "web-subnet"],
            "ssh_priority":  ["100", "110", "120"],
            "http_priority": ["200", "210", "300"],
            "https_priority":["210", "220", "310"],
        },
    },

    # ── App Service + VNet + Storage (combined) ───────────────────────────────
    "app_service_vnet": {
        "openings": [
            (
                "As a Cloud Engineer, you are tasked with deploying a health monitoring web application "
                "on Azure App Service with Virtual Network integration and a blob storage backend. "
                "The application must communicate with storage privately through the VNet and must be "
                "configured with the correct application settings."
            ),
            (
                "As a Platform Engineer, you are responsible for setting up a secure web application "
                "architecture using Azure App Service, a Virtual Network for private connectivity, "
                "and Azure Storage for persistent data. "
                "Ensure all components are integrated correctly."
            ),
        ],
        "task_intro": "Task Details:",
        "tasks": [
            "Create an Azure App Service with the same name as your Resource Group.",
            "Create a Virtual Network named '{vnet_name}' with subnet '{subnet_name}'.",
            "Configure VNet Integration on the App Service to connect to '{vnet_name}/{subnet_name}'.",
            "Create a Storage Account named with your Resource Group name + 'health'.",
            "Set the Storage Account performance tier to Standard with LRS replication and Hot access tier.",
            "Create a Blob container named '{container_name}' in the storage account.",
            "Add the application setting '{app_setting_key}' with the Storage Account connection string.",
        ],
        "spec_intro": "Specifications:",
        "specs": [
            ("App Service Name",  "[Your Resource Group Name]"),
            ("VNet Name",         "{vnet_name}"),
            ("Subnet",            "{subnet_name}"),
            ("Storage Account",   "[Resource Group Name]health"),
            ("Storage Tier",      "Standard LRS, Hot"),
            ("Blob Container",    "{container_name}"),
            ("App Setting",       "{app_setting_key}"),
        ],
        "regions": ["East US", "West US 2", "Central India", "North Europe"],
        "vars": {
            "vnet_name":       ["health-vnet", "app-vnet", "prod-vnet"],
            "subnet_name":     ["app-subnet", "web-subnet", "default"],
            "container_name":  ["reports", "data", "assets"],
            "app_setting_key": ["STORAGE_CONNECTION_STRING", "BLOB_STORAGE_URL"],
        },
    },
}


# ─── DIFFICULTY ADDITIONS ─────────────────────────────────────────────────────
# Appended to tasks/specs when difficulty > beginner

DIFFICULTY_TASKS = {
    "intermediate": [
        "Enable diagnostic settings and send logs to a Log Analytics Workspace.",
        "Apply resource tags: environment=dev, owner=[your name], cost-center=training.",
    ],
    "advanced": [
        "Enable diagnostic settings and send logs to a Log Analytics Workspace.",
        "Configure a private endpoint to remove public internet exposure.",
        "Apply Azure Policy to enforce compliance at the subscription scope.",
        "Set up automated metric alerts for resource health and performance thresholds.",
        "Apply resource tags: environment=prod, owner=[your name], cost-center=training.",
    ],
}

DIFFICULTY_SPECS = {
    "intermediate": [
        ("Diagnostic Logs", "Enabled → Log Analytics Workspace"),
        ("Tags", "environment, owner, cost-center"),
    ],
    "advanced": [
        ("Diagnostic Logs", "Enabled → Log Analytics Workspace"),
        ("Private Endpoint", "Configured"),
        ("Azure Policy", "Compliance enforcement enabled"),
        ("Metric Alerts", "Health + performance thresholds"),
        ("Tags", "environment, owner, cost-center"),
    ],
}


# ─── DESCRIPTION BUILDER ──────────────────────────────────────────────────────

def build_description(service_slugs: List[str], difficulty: str = "intermediate",
                      custom_scenario: str = "") -> Dict:
    """
    Returns { description, task_details[], specifications{}, title, role, region }

    Output format exactly matches the sample assessment questions:
      As a {ROLE} [at a {COMPANY}], you are [responsible for|tasked with] {CONTEXT}.
      {SENTENCE_2}.

      Task Details:
      * task1
      * task2

      Specifications:
      * Key: Value
    """
    # ── Custom scenario passthrough ───────────────────────────────────────────
    if custom_scenario:
        return {
            "description":    custom_scenario,
            "task_details":   [],
            "specifications": {},
            "title":          f"Custom Assessment — {difficulty.title()}",
            "role":           "Azure Engineer",
            "region":         "East US",
        }

    # ── Resolve template ──────────────────────────────────────────────────────
    primary = service_slugs[0]
    tmpl    = SCENARIO_TEMPLATES.get(primary)

    # Fallback for services without a template
    if not tmpl:
        display = SERVICE_CATALOGUE.get(primary, {}).get("display_name", primary)
        return {
            "description": (
                f"As an Azure Cloud Engineer, you are tasked with deploying and configuring "
                f"{display} on Microsoft Azure following best practices and organizational policies.\n\n"
                f"Task Details:\n"
                f"* Deploy {display} with your Resource Group name.\n"
                f"* Configure all required settings as per the specifications below.\n\n"
                f"Specifications:\n"
                f"* Resource Name: [Your Resource Group Name]\n"
                f"* Region: East US"
            ),
            "task_details":   [f"Deploy {display} with required configuration."],
            "specifications": {"Resource Name": "[Your Resource Group Name]", "Region": "East US"},
            "title":          f"Azure {display.removeprefix('Azure ')} Assessment — {difficulty.title()}",
            "role":           "Azure Cloud Engineer",
            "region":         "East US",
        }

    # ── Pick random variants ──────────────────────────────────────────────────
    opening = _pick(tmpl["openings"])
    region  = _pick(tmpl["regions"])
    resolved = _resolve(tmpl, region)

    task_intro = tmpl.get("task_intro", "Task Details:")
    spec_intro = tmpl.get("spec_intro", "Specifications:")

    tasks = [_fill(t, resolved) for t in tmpl["tasks"]]
    specs  = [(_fill(k, resolved), _fill(v, resolved)) for k, v in tmpl["specs"]]

    # ── Append combined service tasks ─────────────────────────────────────────
    for slug in service_slugs[1:]:
        t2 = SCENARIO_TEMPLATES.get(slug)
        if t2:
            r2 = _resolve(t2, region)
            tasks += [_fill(t, r2) for t in t2["tasks"]]
            specs += [(_fill(k, r2), _fill(v, r2)) for k, v in t2["specs"]]

    # ── Append difficulty extras ──────────────────────────────────────────────
    if difficulty in DIFFICULTY_TASKS:
        tasks += DIFFICULTY_TASKS[difficulty]
        specs += DIFFICULTY_SPECS[difficulty]

    # ── Build display names ───────────────────────────────────────────────────
    display_names = [SERVICE_CATALOGUE.get(s, {}).get("display_name", s) for s in service_slugs]

    # ── Render description text ───────────────────────────────────────────────
    lines = [opening, "", task_intro]
    for t in tasks:
        lines.append(f"* {t}")
    lines += ["", spec_intro]
    for k, v in specs:
        lines.append(f"* {k}: {v}")

    # Role extracted from opening sentence
    role = opening.split(",")[0].replace("As a ", "").replace("As an ", "").strip()

    return {
        "description":    "\n".join(lines),
        "task_details":   tasks,
        "specifications": dict(specs),
        "title":          f"Azure {' + '.join(n.removeprefix('Azure ') for n in display_names)} Assessment — {difficulty.title()}",
        "role":           role,
        "region":         region,
    }


# ─── POLICY RESOURCE TYPES ────────────────────────────────────────────────────
# Exact resource types per service with access action permissions

SERVICE_CATALOGUE: Dict = {
    # ── Container Instances ───────────────────────────────────────────────────
    "container_instances": {
        "display_name": "Azure Container Instances", "category": "Containers",
        "sdks": [{"pkg": "@azure/arm-containerinstance", "class": "ContainerInstanceManagementClient", "var": "aciClient"}],
        "resource_types": [
            "Microsoft.ContainerInstance/containerGroups",
            "Microsoft.ContainerInstance/containerGroups/containers",
            "Microsoft.Network/virtualNetworks",
            "Microsoft.Network/virtualNetworks/subnets",
            "Microsoft.Network/networkProfiles",
            "Microsoft.Resources/deployments",
        ],
        "sku_constraints": [],
        "default_names": {
            "containerGroupName": "resourceGroupName",
            "containerImage": '"mcr.microsoft.com/azuredocs/aci-helloworld"',
        },
        "checks": [
            {"weightage": 0.4, "name": "Container Group Exists",    "fn": "check_aci_exists"},
            {"weightage": 0.3, "name": "Container Image Correct",   "fn": "check_aci_image"},
            {"weightage": 0.2, "name": "CPU and Memory Allocation", "fn": "check_aci_resources"},
            {"weightage": 0.1, "name": "Restart Policy is Always",  "fn": "check_aci_restart_policy"},
        ],
    },

    "app_service": {
        "display_name": "App Service", "category": "Web",
        "sdks": [{"pkg": "@azure/arm-appservice", "class": "WebSiteManagementClient", "var": "webClient"}],
        "resource_types": [
            "Microsoft.Web/serverfarms",
            "Microsoft.Web/serverfarms/*",
            "Microsoft.Web/sites",
            "Microsoft.Web/sites/config",
            "Microsoft.Web/sites/hostNameBindings/*",
            "Microsoft.Web/sites/functions/*",
            "Microsoft.Web/sites/sourcecontrols",
            "Microsoft.Web/sites/basicPublishingCredentialsPolicies",
            "Microsoft.AppService/apiApps/*",
            "Microsoft.GitHub/*",
            "Microsoft.ServiceLinker/linkers",
            "Microsoft.Resources/deployments",
            "Microsoft.OperationalInsights/register/action",
        ],
        "sku_constraints": [],
        "default_names": {"appServiceName": "resourceGroupName", "appSetting1": '"WEBSITE_RUN_FROM_PACKAGE"'},
        "checks": [
            {"weightage": 0.4, "name": "App Service Exists",        "fn": "check_app_service_exists"},
            {"weightage": 0.3, "name": "App Service Plan Exists",    "fn": "check_app_service_plan_exists"},
            {"weightage": 0.3, "name": "Application Settings Exist", "fn": "check_app_settings"},
        ],
    },

    "virtual_networks": {
        "display_name": "Virtual Networks", "category": "Networking",
        "sdks": [{"pkg": "@azure/arm-network", "class": "NetworkManagementClient", "var": "networkClient"}],
        "resource_types": [
            "Microsoft.Network/virtualNetworks",
            "Microsoft.Network/virtualNetworks/subnets",
            "Microsoft.Network/networkSecurityGroups",
            "Microsoft.Network/networkSecurityGroups/securityRules",
            "Microsoft.Network/privateDnsZones",
            "Microsoft.Network/privateEndpoints",
            "Microsoft.Network/privateEndpoints/privateDnsZoneGroups",
            "Microsoft.Network/privateDnsZones/virtualNetworkLinks",
            "Microsoft.Network/networkInterfaces",
            "Microsoft.Network/publicIPAddresses",
            "Microsoft.Resources/deployments",
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
            "Microsoft.Storage/storageAccounts",
            "Microsoft.Storage/storageAccounts/blobServices",
            "Microsoft.Storage/storageAccounts/blobServices/containers",
            "Microsoft.Storage/storageAccounts/fileServices",
            "Microsoft.Storage/storageAccounts/fileServices/shares",
            "Microsoft.Storage/storageAccounts/queueServices",
            "Microsoft.Storage/storageAccounts/queueServices/queues",
            "Microsoft.Storage/storageAccounts/tableServices",
            "Microsoft.Storage/storageAccounts/tableServices/tables",
            "Microsoft.Resources/deployments",
        ],
        "sku_constraints": [
            {"anyOf": [
                {"allOf": [
                    {"field": "type", "equals": "Microsoft.Storage/storageAccounts"},
                    {"not": {"allOf": [
                        {"field": "Microsoft.Storage/storageAccounts/sku.tier",   "equals": "Standard"},
                        {"field": "Microsoft.Storage/storageAccounts/accessTier", "equals": "Hot"},
                    ]}}
                ]},
                {"allOf": [
                    {"field": "type", "equals": "Microsoft.Storage/storageAccounts"},
                    {"not": {"field": "Microsoft.Storage/storageAccounts/sku.name",
                             "in": ["Standard_LRS", "Standard_GRS", "Standard_RAGRS", "Standard_ZRS"]}}
                ]},
            ]}
        ],
        "default_names": {
            "storageAccountName": 'resourceGroupName + "health"',
            "containerName": '"reports"',
            "queueName": '"queue1"',
        },
        "checks": [
            {"weightage": 0.3, "name": "Storage Account Exists",    "fn": "check_storage_exists"},
            {"weightage": 0.3, "name": "Blob Container Exists",     "fn": "check_blob_container"},
            {"weightage": 0.2, "name": "Queue Exists",              "fn": "check_storage_queue"},
            {"weightage": 0.2, "name": "Storage SKU is Standard",   "fn": "check_storage_sku"},
        ],
    },

    "virtual_machines": {
        "display_name": "Virtual Machines", "category": "Compute",
        "sdks": [
            {"pkg": "@azure/arm-compute", "class": "ComputeManagementClient", "var": "computeClient"},
            {"pkg": "@azure/arm-network",  "class": "NetworkManagementClient",  "var": "networkClient"},
        ],
        "resource_types": [
            "Microsoft.Compute/virtualMachines",
            "Microsoft.Compute/virtualMachines/extensions",
            "Microsoft.Compute/virtualMachineScaleSets",
            "Microsoft.Compute/availabilitySets",
            "Microsoft.Compute/disks",
            "Microsoft.Compute/snapshots",
            "Microsoft.Network/networkInterfaces",
            "Microsoft.Network/publicIPAddresses",
            "Microsoft.Network/virtualNetworks",
            "Microsoft.Network/virtualNetworks/subnets",
            "Microsoft.Network/networkSecurityGroups",
            "Microsoft.Resources/deployments",
        ],
        "sku_constraints": [],
        "default_names": {"vmName": 'resourceGroupName + "-vm"'},
        "checks": [
            {"weightage": 0.4, "name": "Virtual Machine Exists", "fn": "check_vm_exists"},
            {"weightage": 0.3, "name": "VM is Running",          "fn": "check_vm_running"},
            {"weightage": 0.3, "name": "VM NIC Exists",          "fn": "check_vm_nic"},
        ],
    },

    "sql": {
        "display_name": "Azure SQL Database", "category": "Database",
        "sdks": [{"pkg": "@azure/arm-sql", "class": "SqlManagementClient", "var": "sqlClient"}],
        "resource_types": [
            "Microsoft.Sql/servers",
            "Microsoft.Sql/servers/databases",
            "Microsoft.Sql/servers/firewallRules",
            "Microsoft.Sql/servers/elasticPools",
            "Microsoft.Sql/servers/auditingSettings",
            "Microsoft.Sql/servers/securityAlertPolicies",
            "Microsoft.Sql/servers/vulnerabilityAssessments",
            "Microsoft.Resources/deployments",
        ],
        "sku_constraints": [],
        "default_names": {
            "sqlServerName": 'resourceGroupName + "-sqlserver"',
            "sqlDbName": '"assessmentdb"',
        },
        "checks": [
            {"weightage": 0.4, "name": "SQL Server Exists",        "fn": "check_sql_server_exists"},
            {"weightage": 0.4, "name": "SQL Database Exists",      "fn": "check_sql_db_exists"},
            {"weightage": 0.2, "name": "Firewall Rule Configured", "fn": "check_sql_firewall"},
        ],
    },

    "key_vault": {
        "display_name": "Key Vault", "category": "Security",
        "sdks": [{"pkg": "@azure/arm-keyvault", "class": "KeyVaultManagementClient", "var": "kvClient"}],
        "resource_types": [
            "Microsoft.KeyVault/vaults",
            "Microsoft.KeyVault/vaults/secrets",
            "Microsoft.KeyVault/vaults/keys",
            "Microsoft.KeyVault/vaults/certificates",
            "Microsoft.KeyVault/vaults/accessPolicies",
            "Microsoft.ManagedIdentity/userAssignedIdentities",
            "Microsoft.Resources/deployments",
        ],
        "sku_constraints": [],
        "default_names": {"keyVaultName": 'resourceGroupName + "-kv"'},
        "checks": [
            {"weightage": 0.4, "name": "Key Vault Exists",          "fn": "check_keyvault_exists"},
            {"weightage": 0.3, "name": "Soft Delete Enabled",       "fn": "check_keyvault_softdelete"},
            {"weightage": 0.3, "name": "Access Policy Configured",  "fn": "check_keyvault_access_policy"},
        ],
    },

    "aks": {
        "display_name": "Azure Kubernetes Service", "category": "Containers",
        "sdks": [{"pkg": "@azure/arm-containerservice", "class": "ContainerServiceClient", "var": "aksClient"}],
        "resource_types": [
            "Microsoft.ContainerService/managedClusters",
            "Microsoft.ContainerService/managedClusters/agentPools",
            "Microsoft.ContainerRegistry/registries",
            "Microsoft.ContainerRegistry/registries/replications",
            "Microsoft.Network/virtualNetworks",
            "Microsoft.Network/virtualNetworks/subnets",
            "Microsoft.Network/loadBalancers",
            "Microsoft.Network/publicIPAddresses",
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
            "Microsoft.EventHub/namespaces",
            "Microsoft.EventHub/namespaces/eventhubs",
            "Microsoft.EventHub/namespaces/eventhubs/consumergroups",
            "Microsoft.EventHub/namespaces/authorizationRules",
            "Microsoft.EventHub/namespaces/networkRuleSets",
            "Microsoft.Resources/deployments",
        ],
        "sku_constraints": [],
        "default_names": {
            "ehNamespaceName": 'resourceGroupName + "-ehns"',
            "ehName": '"assessment-hub"',
        },
        "checks": [
            {"weightage": 0.4, "name": "Event Hub Namespace Exists", "fn": "check_eh_namespace"},
            {"weightage": 0.4, "name": "Event Hub Exists",           "fn": "check_eh_exists"},
            {"weightage": 0.2, "name": "Consumer Group Exists",      "fn": "check_eh_consumer_group"},
        ],
    },

    "dns": {
        "display_name": "Azure DNS", "category": "Networking",
        "sdks": [{"pkg": "@azure/arm-dns", "class": "DnsManagementClient", "var": "dnsClient"}],
        "resource_types": [
            "Microsoft.Network/dnsZones",
            "Microsoft.Network/dnsZones/A",
            "Microsoft.Network/dnsZones/AAAA",
            "Microsoft.Network/dnsZones/CNAME",
            "Microsoft.Network/dnsZones/MX",
            "Microsoft.Network/dnsZones/NS",
            "Microsoft.Network/dnsZones/SOA",
            "Microsoft.Network/dnsZones/TXT",
            "Microsoft.Network/privateDnsZones",
            "Microsoft.Network/privateDnsZones/virtualNetworkLinks",
            "Microsoft.Resources/deployments",
        ],
        "sku_constraints": [],
        "default_names": {"zoneName": '"contoso.com"'},
        "checks": [
            {"weightage": 0.4, "name": "DNS Zone Exists",          "fn": "check_dns_zone"},
            {"weightage": 0.3, "name": "A Record Configured",      "fn": "check_dns_a_record"},
            {"weightage": 0.3, "name": "CNAME Record Configured",  "fn": "check_dns_cname"},
        ],
    },

    "logic_apps": {
        "display_name": "Logic Apps", "category": "Serverless",
        "sdks": [{"pkg": "@azure/arm-logic", "class": "LogicManagementClient", "var": "logicClient"}],
        "resource_types": [
            "Microsoft.Logic/workflows",
            "Microsoft.Logic/workflows/runs",
            "Microsoft.Logic/workflows/triggers",
            "Microsoft.Logic/integrationAccounts",
            "Microsoft.Web/connections",
            "Microsoft.Web/customApis",
            "Microsoft.Resources/deployments",
            "Microsoft.OperationalInsights/register/action",
        ],
        "sku_constraints": [],
        "default_names": {"workflowName": "resourceGroupName"},
        "checks": [
            {"weightage": 0.5, "name": "Logic App Workflow Exists", "fn": "check_logic_app_exists"},
            {"weightage": 0.3, "name": "Workflow is Enabled",       "fn": "check_logic_app_enabled"},
            {"weightage": 0.2, "name": "Trigger Configured",        "fn": "check_logic_app_trigger"},
        ],
    },

    "cosmos_db": {
        "display_name": "Cosmos DB", "category": "Database",
        "sdks": [{"pkg": "@azure/arm-cosmosdb", "class": "CosmosDBManagementClient", "var": "cosmosClient"}],
        "resource_types": [
            "Microsoft.DocumentDB/databaseAccounts",
            "Microsoft.DocumentDB/databaseAccounts/sqlDatabases",
            "Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers",
            "Microsoft.DocumentDB/databaseAccounts/mongodbDatabases",
            "Microsoft.DocumentDB/databaseAccounts/mongodbDatabases/collections",
            "Microsoft.DocumentDB/databaseAccounts/gremlinDatabases",
            "Microsoft.DocumentDB/databaseAccounts/tables",
            "Microsoft.DocumentDB/databaseAccounts/cassandraKeyspaces",
            "Microsoft.Resources/deployments",
        ],
        "sku_constraints": [],
        "default_names": {
            "cosmosAccountName": 'resourceGroupName + "-cosmos"',
            "dbName": '"assessmentdb"',
        },
        "checks": [
            {"weightage": 0.5, "name": "Cosmos DB Account Exists",  "fn": "check_cosmos_exists"},
            {"weightage": 0.3, "name": "Database Exists",           "fn": "check_cosmos_db"},
            {"weightage": 0.2, "name": "Geo-Redundancy Enabled",    "fn": "check_cosmos_geo"},
        ],
    },

    "service_bus": {
        "display_name": "Service Bus", "category": "Messaging",
        "sdks": [{"pkg": "@azure/arm-servicebus", "class": "ServiceBusManagementClient", "var": "sbClient"}],
        "resource_types": [
            "Microsoft.ServiceBus/namespaces",
            "Microsoft.ServiceBus/namespaces/queues",
            "Microsoft.ServiceBus/namespaces/topics",
            "Microsoft.ServiceBus/namespaces/topics/subscriptions",
            "Microsoft.ServiceBus/namespaces/authorizationRules",
            "Microsoft.ServiceBus/namespaces/networkRuleSets",
            "Microsoft.Resources/deployments",
        ],
        "sku_constraints": [],
        "default_names": {
            "sbNamespaceName": 'resourceGroupName + "-sbns"',
            "queueName": '"assessment-queue"',
        },
        "checks": [
            {"weightage": 0.4, "name": "Service Bus Namespace Exists", "fn": "check_sb_namespace"},
            {"weightage": 0.4, "name": "Queue Exists",                 "fn": "check_sb_queue"},
            {"weightage": 0.2, "name": "Dead Letter Queue Configured", "fn": "check_sb_dlq"},
        ],
    },

    "nsg": {
        "display_name": "Network Security Groups", "category": "Networking",
        "sdks": [{"pkg": "@azure/arm-network", "class": "NetworkManagementClient", "var": "networkClient"}],
        "resource_types": [
            "Microsoft.Network/networkSecurityGroups",
            "Microsoft.Network/networkSecurityGroups/securityRules",
            "Microsoft.Network/virtualNetworks",
            "Microsoft.Network/virtualNetworks/subnets",
            "Microsoft.Network/networkWatchers",
            "Microsoft.Network/networkWatchers/flowLogs",
            "Microsoft.Resources/deployments",
        ],
        "sku_constraints": [],
        "default_names": {"nsgName": 'resourceGroupName + "-nsg"'},
        "checks": [
            {"weightage": 0.5, "name": "NSG Exists",                  "fn": "check_nsg_exists"},
            {"weightage": 0.3, "name": "Inbound Rules Configured",    "fn": "check_nsg_inbound_rules"},
            {"weightage": 0.2, "name": "NSG Associated with Subnet",  "fn": "check_nsg_subnet"},
        ],
    },

    "functions": {
        "display_name": "Azure Functions", "category": "Serverless",
        "sdks": [{"pkg": "@azure/arm-appservice", "class": "WebSiteManagementClient", "var": "webClient"}],
        "resource_types": [
            "Microsoft.Web/sites",
            "Microsoft.Web/sites/functions",
            "Microsoft.Web/sites/functions/*",
            "Microsoft.Web/serverfarms",
            "Microsoft.Web/sites/config",
            "Microsoft.Storage/storageAccounts",
            "Microsoft.Storage/storageAccounts/blobServices",
            "Microsoft.Insights/components",
            "Microsoft.OperationalInsights/workspaces",
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

    # Combined: App Service + VNet + Storage (exact scaffolding example)
    "app_service_vnet": {
        "display_name": "App Service + Virtual Network", "category": "Web + Networking",
        "sdks": [
            {"pkg": "@azure/arm-appservice", "class": "WebSiteManagementClient", "var": "webClient"},
            {"pkg": "@azure/arm-storage",    "class": "StorageManagementClient",  "var": "storageClient"},
            {"pkg": "@azure/arm-network",    "class": "NetworkManagementClient",  "var": "networkClient"},
        ],
        "resource_types": [
            "Microsoft.Web/serverfarms", "Microsoft.Web/serverfarms/*",
            "Microsoft.Web/sites", "Microsoft.Web/sites/config",
            "Microsoft.Web/sites/hostNameBindings/*", "Microsoft.Web/sites/functions/*",
            "Microsoft.Web/sites/sourcecontrols",
            "Microsoft.Web/sites/basicPublishingCredentialsPolicies",
            "Microsoft.AppService/apiApps/*", "Microsoft.GitHub/*",
            "Microsoft.Storage/storageAccounts",
            "Microsoft.Storage/storageAccounts/blobServices",
            "Microsoft.Storage/storageAccounts/blobServices/containers",
            "Microsoft.Storage/storageAccounts/fileServices",
            "Microsoft.Storage/storageAccounts/queueServices",
            "Microsoft.Network/virtualNetworks",
            "Microsoft.Network/virtualNetworks/subnets",
            "Microsoft.Network/networkSecurityGroups",
            "Microsoft.Network/privateDnsZones",
            "Microsoft.Network/privateEndpoints",
            "Microsoft.Network/privateEndpoints/privateDnsZoneGroups",
            "Microsoft.Network/privateDnsZones/virtualNetworkLinks",
            "Microsoft.Network/networkInterfaces",
            "Microsoft.Network/publicIPAddresses",
            "Microsoft.DocumentDB/databaseAccounts",
            "Microsoft.DocumentDB/databaseAccounts/sqlDatabases",
            "Microsoft.ServiceLinker/linkers",
            "Microsoft.Resources/deployments",
            "Microsoft.OperationalInsights/register/action",
        ],
        "sku_constraints": [
            {"anyOf": [
                {"allOf": [
                    {"field": "type", "equals": "Microsoft.Storage/storageAccounts"},
                    {"not": {"allOf": [
                        {"field": "Microsoft.Storage/storageAccounts/sku.tier",   "equals": "Standard"},
                        {"field": "Microsoft.Storage/storageAccounts/accessTier", "equals": "Hot"},
                    ]}}
                ]},
                {"allOf": [
                    {"field": "type", "equals": "Microsoft.Storage/storageAccounts"},
                    {"not": {"field": "Microsoft.Storage/storageAccounts/sku.name",
                             "in": ["Standard_LRS","Standard_GRS","Standard_RAGRS","Standard_ZRS"]}}
                ]},
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
        // ✅ {IDX}. Check if App Service is connected to the VNet
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
                if (container.name === containerName) { containerExists = true; break; }
            }
            if (containerExists) {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `Blob Container ${containerName} does not exist`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error fetching Blob Container: ${error.message}`;
        }""",

    "check_storage_queue": """\
        // ✅ {IDX}. Check if the Queue exists
        try {
            const queues = storageClient.queue.list(resourceGroupName, storageAccountName);
            let found = false;
            for await (const q of queues) {
                if (q.name === queueName) { found = true; break; }
            }
            if (found) {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `Queue ${queueName} does not exist`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error fetching Queue: ${error.message}`;
        }""",

    "check_storage_sku": """\
        // ✅ {IDX}. Check Storage Account SKU
        try {
            const storage = await storageClient.storageAccounts.getProperties(resourceGroupName, storageAccountName);
            const validSkus = ["Standard_LRS", "Standard_GRS", "Standard_RAGRS", "Standard_ZRS"];
            if (validSkus.includes(storage.sku?.name)) {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `Storage SKU ${storage.sku?.name} is not in approved list`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error checking Storage SKU: ${error.message}`;
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
                validationResult[{IDX}].error = `Soft delete not enabled on ${keyVaultName}`;
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
                validationResult[{IDX}].error = `RBAC is not enabled on ${aksClusterName}`;
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
                validationResult[{IDX}].error = `No CNAME records in zone ${zoneName}`;
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
        // ✅ {IDX}. Check Logic App triggers configured
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
            validationResult[{IDX}].error = `Error fetching Cosmos DB: ${error.message}`;
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
            if ((account.locations || []).length > 1) {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `Cosmos DB ${cosmosAccountName} does not have geo-redundancy`;
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
        // ✅ {IDX}. Check dead letter queue on expiration
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
            const inbound = (nsg.securityRules || []).filter(r => r.direction === "Inbound");
            if (inbound.length > 0) {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `No inbound rules on NSG ${nsgName}`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error checking NSG rules: ${error.message}`;
        }""",

    "check_nsg_subnet": """\
        // ✅ {IDX}. Check NSG is associated with a subnet
        try {
            const nsg = await networkClient.networkSecurityGroups.get(resourceGroupName, nsgName);
            if ((nsg.subnets || []).length > 0) {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `NSG ${nsgName} not associated with any subnet`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error checking NSG subnet: ${error.message}`;
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
                validationResult[{IDX}].error = `Function App ${functionAppName} not Running (state: ${app.state})`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error checking Function App state: ${error.message}`;
        }""",


    "check_aci_exists": """        // ✅ {IDX}. Check if the Container Group exists
        try {
            const cg = await aciClient.containerGroups.get(resourceGroupName, containerGroupName);
            if (cg && cg.name === containerGroupName) {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `Container Group ${containerGroupName} does not exist`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error fetching Container Group: ${error.message}`;
        }""",

    "check_aci_image": """        // ✅ {IDX}. Check container image is correct
        try {
            const cg = await aciClient.containerGroups.get(resourceGroupName, containerGroupName);
            const containers = cg.containers || [];
            const imageMatch = containers.some(c => c.image === containerImage);
            if (imageMatch) {
                validationResult[{IDX}].status = true;
            } else {
                const images = containers.map(c => c.image).join(", ");
                validationResult[{IDX}].error = `Container image mismatch. Found: ${images}, Expected: ${containerImage}`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error checking container image: ${error.message}`;
        }""",

    "check_aci_resources": """        // ✅ {IDX}. Check CPU and memory allocation
        try {
            const cg = await aciClient.containerGroups.get(resourceGroupName, containerGroupName);
            const containers = cg.containers || [];
            const resourcesOk = containers.every(c => {
                const res = c.resources?.requests;
                return res && res.cpu >= 1 && res.memoryInGB >= 1;
            });
            if (resourcesOk) {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `Container resource allocation does not meet minimum requirements (1 vCPU, 1 GB)`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error checking container resources: ${error.message}`;
        }""",

    "check_aci_restart_policy": """        // ✅ {IDX}. Check restart policy is Always
        try {
            const cg = await aciClient.containerGroups.get(resourceGroupName, containerGroupName);
            if (cg.restartPolicy === "Always") {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `Restart policy is '${cg.restartPolicy}', expected 'Always'`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error checking restart policy: ${error.message}`;
        }""",

    "check_function_app_settings": """\
        // ✅ {IDX}. Check Function App application settings
        try {
            const settings = await webClient.webApps.listApplicationSettings(resourceGroupName, functionAppName);
            const props = settings.properties || {};
            if (Object.keys(props).length > 0) {
                validationResult[{IDX}].status = true;
            } else {
                validationResult[{IDX}].error = `No application settings on ${functionAppName}`;
            }
        } catch (error) {
            validationResult[{IDX}].error = `Error fetching Function App settings: ${error.message}`;
        }""",
}


# ─── SCRIPT BUILDER ──────────────────────────────────────────────────────────

def build_validation_script(service_slugs: List[str], custom_names: Dict = None) -> str:
    configs = [SERVICE_CATALOGUE[s] for s in service_slugs if s in SERVICE_CATALOGUE]
    if not configs:
        return "// No valid services found"

    seen_pkgs: set = set()
    sdk_imports, client_inits = [], []
    for cfg in configs:
        for sdk in cfg["sdks"]:
            if sdk["pkg"] not in seen_pkgs:
                seen_pkgs.add(sdk["pkg"])
                sdk_imports.append(f'const {{ {sdk["class"]} }} = require("{sdk["pkg"]}");')
                client_inits.append(f'const {sdk["var"]} = new {sdk["class"]}(credentials, subscriptionId);')

    names: Dict[str, str] = {}
    for cfg in configs:
        names.update(cfg.get("default_names", {}))
    if custom_names:
        names.update(custom_names)

    all_checks = []
    for cfg in configs:
        all_checks.extend(cfg.get("checks", []))

    vr_lines = ["let validationResult = ["]
    for chk in all_checks:
        vr_lines.append(f"    {{ weightage: {chk['weightage']}, name: \"{chk['name']}\", status: false, error: '' }},")
    vr_lines.append("];")

    name_decls = [f"const {var} = {expr};" for var, expr in names.items()]

    check_body = []
    for idx, chk in enumerate(all_checks):
        snippet = CHECK_SNIPPETS.get(chk.get("fn", ""))
        if snippet:
            check_body.append(snippet.replace("{IDX}", str(idx)))
            check_body.append("")

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
        "\n".join("        " + l if l.strip() else "" for l in "\n".join(check_body).splitlines()),
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
        return {"if": all_of[0], "then": {"effect": "deny"}}
    return {"if": {"allOf": all_of}, "then": {"effect": "deny"}}


# ─── BUILD FROM EXACT FIELD VALUES ────────────────────────────────────────────

def build_from_fields(service_display: str, field_values: dict,
                      difficulty: str = "beginner",
                      role: str = "", context: str = "") -> dict:
    """
    Generate description + specs using EXACT values the user entered.
    No randomness. field_values comes directly from the Streamlit form.
    Returns same shape as build_description():
      { description, task_details[], specifications{}, title, role, region }
    """
    from service_fields import SERVICE_FIELDS, render_tasks, render_specs

    tmpl = SERVICE_FIELDS.get(service_display, {})
    if not tmpl:
        return build_description(
            [service_display.lower().replace(" ", "_")], difficulty, ""
        )

    # Pick role and context — use provided or first option
    chosen_role    = role    or tmpl["role_options"][0]
    chosen_context = context or tmpl["context_options"][0]

    task_intro = tmpl.get("task_intro", "Task Details:")
    tasks      = render_tasks(service_display, field_values)
    specs      = render_specs(service_display, field_values)

    # Difficulty extras
    diff_tasks = {
        "intermediate": [
            "Enable diagnostic settings and send logs to a Log Analytics Workspace.",
            "Apply resource tags: environment=dev, owner=[your name], cost-center=training.",
        ],
        "advanced": [
            "Enable diagnostic settings and send logs to a Log Analytics Workspace.",
            "Configure a private endpoint to remove public internet exposure.",
            "Apply Azure Policy to enforce compliance at the subscription scope.",
            "Set up automated metric alerts for resource health and performance.",
            "Apply resource tags: environment=prod, owner=[your name], cost-center=training.",
        ],
    }
    diff_specs = {
        "intermediate": [
            ("Diagnostic Logs", "Enabled → Log Analytics Workspace"),
            ("Tags", "environment, owner, cost-center"),
        ],
        "advanced": [
            ("Diagnostic Logs", "Enabled → Log Analytics Workspace"),
            ("Private Endpoint", "Configured"),
            ("Azure Policy", "Compliance enforcement enabled"),
            ("Alerts", "Health + performance thresholds"),
            ("Tags", "environment, owner, cost-center"),
        ],
    }
    if difficulty in diff_tasks:
        tasks = tasks + diff_tasks[difficulty]
        for k, v in diff_specs[difficulty]:
            specs[k] = v

    # Build description text
    lines = [
        f"As a {chosen_role}, you are responsible for {chosen_context}",
        "",
        task_intro,
    ]
    for t in tasks:
        lines.append(f"* {t}")
    lines += ["", "Specifications:"]
    for k, v in specs.items():
        lines.append(f"* {k}: {v}")

    region = field_values.get("region", "East US")
    slug   = service_display.lower().replace(" ", "_")
    display_name = SERVICE_CATALOGUE.get(slug, {}).get("display_name", service_display)

    return {
        "description":    "\n".join(lines),
        "task_details":   tasks,
        "specifications": specs,
        "title": f"Azure {display_name.removeprefix('Azure ')} Assessment — {difficulty.title()}",
        "role":   chosen_role,
        "region": region,
    }


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
        cfg = SERVICE_CATALOGUE.get(slugs[0], {}) if slugs else {}
        return {"slug": slugs[0], **cfg} if cfg else None

    def generate_policy(self, services: Any) -> Dict:
        slugs = self._resolve_slugs(services)
        rule  = build_policy_json(slugs)
        names = [SERVICE_CATALOGUE.get(s, {}).get("display_name", s) for s in slugs]
        rt: List[str] = []
        seen: set = set()
        for slug in slugs:
            for r in SERVICE_CATALOGUE.get(slug, {}).get("resource_types", []):
                if r not in seen:
                    seen.add(r); rt.append(r)
        return {
            "policy_type":    "resource_restriction",
            "description":    f"Azure Policy for {', '.join(names)}. Denies resource types not in the approved list.",
            "resource_types": rt,
            "policy_json":    rule,
            "session":        "",
        }

    def generate_validation_script(self, services: Any, specifications: Dict = None) -> Dict:
        slugs  = self._resolve_slugs(services)
        script = build_validation_script(slugs, specifications)
        checks = []
        for slug in slugs:
            checks.extend(SERVICE_CATALOGUE.get(slug, {}).get("checks", []))
        test_cases = [{"name": c["name"], "description": c["name"],
                       "weightage": c["weightage"], "code": ""} for c in checks]
        pkgs: set = set()
        for slug in slugs:
            for sdk in SERVICE_CATALOGUE.get(slug, {}).get("sdks", []):
                pkgs.add(sdk["pkg"])
        return {
            "language":    "javascript",
            "dependencies": ["@azure/identity", "dotenv"] + sorted(pkgs),
            "test_cases":  test_cases,
            "full_script": script,
            "content":     script,
        }

    def generate_question(self, services: Any, difficulty: str = "intermediate",
                          scenario: str = "") -> str:
        slugs = self._resolve_slugs(services)
        result = build_description(slugs, difficulty, scenario)
        return result["description"]

    def generate_assessment_meta(self, services: Any, difficulty: str = "intermediate",
                                 scenario: str = "") -> Dict:
        """Returns full description dict with task_details, specifications, title, role, region."""
        slugs = self._resolve_slugs(services)
        return build_description(slugs, difficulty, scenario)


    def generate_from_fields(self, service_display: str, field_values: dict,
                              difficulty: str = "beginner",
                              role: str = "", context: str = "") -> dict:
        """
        Main entry point when user fills the form with exact resource details.
        Returns full assessment dict: meta + policy + script all using exact values.
        """
        # Description and specs from exact form values
        meta = build_from_fields(service_display, field_values, difficulty, role, context)

        # Policy and script from slug
        slugs  = self._resolve_slugs([service_display])
        policy = self.generate_policy(slugs)
        script = self.generate_validation_script(slugs, field_values)

        return {
            "meta":   meta,
            "policy": policy,
            "script": script,
        }


rules_engine = AzureRulesEngine()


if __name__ == "__main__":
    import sys
    slugs = sys.argv[1:] if len(sys.argv) > 1 else ["key_vault"]
    print(f"\n=== Description for {slugs} ===\n")
    meta = rules_engine.generate_assessment_meta(slugs, "intermediate")
    print(meta["description"])
    print(f"\n=== Policy JSON ===\n")
    p = rules_engine.generate_policy(slugs)
    print(json.dumps(p["policy_json"], indent=2))