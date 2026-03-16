"""
service_fields.py — Per-service field definitions for the assessment form.

Each service defines exactly what the user must fill in.
These values drive the description, policy, and validation script — no randomness.

Field schema:
  key        : internal key used in templates
  label      : shown in the UI form
  type       : text | select | number
  options    : list (for select type)
  default    : pre-filled default value
  help       : tooltip text shown in UI
  required   : True/False
  spec_label : how it appears in Specifications block
"""

from typing import Dict, List, Any

# ─── FIELD REGISTRY ──────────────────────────────────────────────────────────

SERVICE_FIELDS: Dict[str, Dict] = {

    # ── Container Instances ───────────────────────────────────────────────────
    "Azure Container Instances": {
        "role_options": [
            "Azure Cloud Engineer",
            "DevOps Engineer",
            "Platform Engineer",
        ],
        "context_options": [
            "creating an Azure Container Instance with specific configurations to host a sample application. The container instance should be set up to run continuously and handle requests efficiently.",
            "deploying a containerized workload on Azure using Azure Container Instances. The container must be configured with the correct compute allocation and restart behavior.",
            "provisioning a container-based microservice on Azure Container Instances. The container must meet defined resource limits and availability requirements.",
        ],
        "fields": [
            {"key": "region",           "label": "Region",           "type": "select",  "required": True,  "spec_label": "Region",
             "options": ["Central India","East US","West US 2","Southeast Asia","West Europe","North Europe"],
             "default": "Central India"},
            {"key": "container_image",  "label": "Container Image",  "type": "text",    "required": True,  "spec_label": "Container Image",
             "default": "mcr.microsoft.com/azuredocs/aci-helloworld",
             "help": "e.g. mcr.microsoft.com/azuredocs/aci-helloworld"},
            {"key": "cpu",              "label": "CPU (vCPU)",       "type": "select",  "required": True,  "spec_label": "CPU",
             "options": ["1","2","4"],"default": "1"},
            {"key": "memory",           "label": "Memory (GB)",      "type": "select",  "required": True,  "spec_label": "Memory",
             "options": ["1","2","4","8"],"default": "1"},
            {"key": "restart_policy",   "label": "Restart Policy",   "type": "select",  "required": True,  "spec_label": "Restart Policy",
             "options": ["Always","Never","OnFailure"],"default": "Always"},
            {"key": "os_type",          "label": "OS Type",          "type": "select",  "required": False, "spec_label": "OS Type",
             "options": ["Linux","Windows"],"default": "Linux"},
        ],
        "task_template": [
            'Create an Azure Container Instance with your "Resource Group Name".',
            "Deploy the container instance in the {region} region.",
            "Use the image {container_image}",
            "Allocate {cpu} vCPU to the container instance.",
            "Allocate {memory} GB of memory to the container instance.",
            'Set the restart policy of the container instance to "{restart_policy}".',
            "Set the OS type to {os_type}.",
        ],
        "task_intro": "Task Details:",
        "policy_extra_info": "Allows deployment of Container Instances only. Denies all other resource types.",
    },

    # ── Storage Accounts ──────────────────────────────────────────────────────
    "Storage Accounts": {
        "role_options": [
            "Azure administrator",
            "Cloud Storage Engineer",
            "DevOps Engineer",
        ],
        "context_options": [
            "configuring an Azure Storage account to support your company's file storage requirements. Your goal is to set up the Storage account with specific configurations to ensure secure and efficient file storage and retrieval.",
            "provisioning an Azure Storage account to store application assets and user-uploaded content. The account must be configured for optimal performance and durability.",
            "setting up a centralized Azure Storage account as the persistent backend for a data processing pipeline. Configure the account to ensure high availability and cost-effective access.",
        ],
        "fields": [
            {"key": "region",            "label": "Region",              "type": "select",  "required": True,  "spec_label": "Location",
             "options": ["West US 2","East US","Central India","West Europe","Southeast Asia","North Europe","East US 2"],
             "default": "West US 2"},
            {"key": "performance_tier",  "label": "Performance Tier",    "type": "select",  "required": True,  "spec_label": "Performance Tier",
             "options": ["Standard","Premium"],"default": "Standard"},
            {"key": "replication",       "label": "Replication",         "type": "select",  "required": True,  "spec_label": "Replication",
             "options": ["LRS","GRS","RAGRS","ZRS","GZRS"],"default": "LRS"},
            {"key": "access_tier",       "label": "Access Tier",         "type": "select",  "required": True,  "spec_label": "Access Tier",
             "options": ["Hot","Cool","Cold","Archive"],"default": "Hot"},
            {"key": "queue_name",        "label": "Queue Name",          "type": "text",    "required": True,  "spec_label": "Queue Name",
             "default": "queue1"},
            {"key": "queue_message",     "label": "Queue Message",       "type": "text",    "required": True,  "spec_label": "Queue Message",
             "default": "hi"},
            {"key": "blob_container",    "label": "Blob Container Name", "type": "text",    "required": False, "spec_label": "Blob Container",
             "default": "","help": "Leave blank to skip blob container creation"},
        ],
        "task_template": [
            "Create an Azure Storage account with the same name of the Resource group given to you.",
            "Set the location to {region}.",
            "Configure the Storage account to use the {performance_tier} performance tier.",
            "Enable the Locally-redundant storage ({replication}) replication option for enhanced data durability.",
            "Set the account access tier to '{access_tier}' to optimize for frequent access to the stored data.",
            'Create a Queue named "{queue_name}" in the storage account and add a message "{queue_message}" in the queue.',
            'Unselect the option "Encode the message body in Base64"',
        ],
        "task_template_with_blob": [
            "Create an Azure Storage account with the same name of the Resource group given to you.",
            "Set the location to {region}.",
            "Configure the Storage account to use the {performance_tier} performance tier.",
            "Enable the Locally-redundant storage ({replication}) replication option for enhanced data durability.",
            "Set the account access tier to '{access_tier}' to optimize for frequent access to the stored data.",
            'Create a Blob container named "{blob_container}" in the storage account.',
            'Create a Queue named "{queue_name}" in the storage account and add a message "{queue_message}" in the queue.',
            'Unselect the option "Encode the message body in Base64"',
        ],
        "task_intro": "Follow the steps below to complete the task:",
        "policy_extra_info": "Storage must use Standard tier with Hot access tier. LRS/GRS/RAGRS/ZRS replication only.",
    },

    # ── Key Vault ─────────────────────────────────────────────────────────────
    "Key Vault": {
        "role_options": [
            "DevOps Engineer",
            "Azure Security Engineer",
            "Cloud Administrator",
        ],
        "context_options": [
            "managing secure storage and access to secrets, keys, and certificates. You have been tasked with creating and configuring an Azure Key Vault with specific properties to ensure security and proper management.",
            "provisioning an Azure Key Vault to store application credentials, TLS certificates, and encryption keys. The vault must be hardened against unauthorized access and data loss.",
            "setting up centralized secret management for a production workload running on Azure. Your task is to create and configure a Key Vault with the required security properties.",
        ],
        "fields": [
            {"key": "region",          "label": "Region",                     "type": "select",  "required": True,  "spec_label": "Location",
             "options": ["West US3","East US 2","North Europe","Southeast Asia","West Europe","Central India","East US"],
             "default": "West US3"},
            {"key": "tier",            "label": "Pricing Tier",               "type": "select",  "required": True,  "spec_label": "Tier",
             "options": ["Standard","Premium"],"default": "Standard"},
            {"key": "retention_days",  "label": "Days to Retain Deleted Vaults","type": "select", "required": True, "spec_label": "Days to Retain Deleted Vaults",
             "options": ["7","14","30","60","90"],"default": "30"},
            {"key": "public_access",   "label": "Public Network Access",      "type": "select",  "required": True,  "spec_label": "Public Access",
             "options": ["Disabled","Enabled"],"default": "Disabled"},
            {"key": "soft_delete",     "label": "Soft Delete",                "type": "select",  "required": False, "spec_label": "Soft Delete",
             "options": ["Enabled","Disabled"],"default": "Enabled"},
            {"key": "purge_protection","label": "Purge Protection",           "type": "select",  "required": False, "spec_label": "Purge Protection",
             "options": ["Enabled","Disabled"],"default": "Disabled"},
        ],
        "task_template": [
            "Create an Azure Key Vault with the same name as the Resource Group provided to you.",
            "Set the location to {region}.",
            "Configure the Azure Key Vault as '{tier}' tier.",
            "Set the days to retain deleted vaults as '{retention_days}'.",
            "{public_access_task}",
        ],
        "task_intro": "Task Details:",
        "policy_extra_info": "Allows Key Vault and related identity resources only. All other resource types are denied.",
    },

    # ── Logic Apps ────────────────────────────────────────────────────────────
    "Logic Apps": {
        "role_options": [
            "DevOps Engineer",
            "Integration Developer",
            "Automation Engineer",
        ],
        "context_options": [
            "managing various workflows and automation tasks. You have implemented Azure Logic Apps to handle different business operations. Your task is to evaluate and configure a specific Logic App to ensure it is set up correctly with basic properties and triggers.",
            "building an automated approval workflow using Azure Logic Apps. The Logic App must be configured with the correct plan, location, and an HTTP trigger to receive incoming requests.",
            "configuring Azure Logic Apps to integrate internal systems. Your task is to set up a Logic App with the required plan and trigger configuration.",
        ],
        "fields": [
            {"key": "region",       "label": "Location",      "type": "select", "required": True,  "spec_label": "Location",
             "options": ["East US","West US 2","North Europe","Southeast Asia","West Europe","Central India","East US 2"],
             "default": "East US"},
            {"key": "plan",         "label": "Plan",          "type": "select", "required": True,  "spec_label": "Plan",
             "options": ["Consumption","Standard"],"default": "Consumption"},
            {"key": "state",        "label": "State",         "type": "select", "required": True,  "spec_label": "State",
             "options": ["Enabled","Disabled"],"default": "Enabled"},
            {"key": "trigger_type", "label": "Trigger Type",  "type": "select", "required": True,  "spec_label": "Trigger Type",
             "options": ["Request","Recurrence","HTTP","Event Grid","Service Bus"],"default": "Request"},
        ],
        "task_template": [
            "Choose the Resource Group listed for you.",
            "Configure a Logic App named with your Resource Group name, choosing the {plan} Plan.",
            'Set the location of the Logic App to "{region}".',
            'Change the current state of the Logic App to "{state}".',
            'Create an HTTP trigger to respond to HTTP requests, selecting the Trigger type as "{trigger_type}".',
        ],
        "task_intro": "Task Details:",
        "policy_extra_info": "Allows Logic App workflows, integration accounts, and web connections. All others denied.",
    },

    # ── Virtual Machines ──────────────────────────────────────────────────────
    "Virtual Machines": {
        "role_options": [
            "Azure Cloud Engineer",
            "Infrastructure Engineer",
            "Systems Administrator",
        ],
        "context_options": [
            "provisioning a Virtual Machine to host a web application backend for your organization. The VM must be configured with the correct size, image, and network access rules.",
            "deploying a Virtual Machine to run a legacy batch processing application on Azure. The VM must be set up with appropriate compute resources and security settings.",
            "deploying an Azure Virtual Machine as a development environment for your engineering team. Configure the VM with the required specifications and ensure SSH access is enabled.",
        ],
        "fields": [
            {"key": "region",       "label": "Region",          "type": "select", "required": True,  "spec_label": "Region",
             "options": ["East US","West US 2","Central India","UK South","Southeast Asia","North Europe","East US 2"],
             "default": "East US"},
            {"key": "vm_size",      "label": "VM Size",         "type": "select", "required": True,  "spec_label": "VM Size",
             "options": ["Standard_B1ms","Standard_B2s","Standard_B2ms","Standard_D2s_v3","Standard_D4s_v3","Standard_F2s_v2"],
             "default": "Standard_B2s"},
            {"key": "vm_image",     "label": "OS Image",        "type": "select", "required": True,  "spec_label": "Image",
             "options": ["Ubuntu Server 22.04 LTS","Ubuntu Server 20.04 LTS","Windows Server 2022 Datacenter","Windows Server 2019 Datacenter","Red Hat Enterprise Linux 9"],
             "default": "Ubuntu Server 22.04 LTS"},
            {"key": "disk_type",    "label": "OS Disk Type",    "type": "select", "required": True,  "spec_label": "OS Disk Type",
             "options": ["Standard SSD (LRS)","Premium SSD (LRS)","Standard HDD (LRS)","Premium SSD v2 (LRS)"],
             "default": "Standard SSD (LRS)"},
            {"key": "disk_size_gb", "label": "OS Disk Size (GB)","type":"select", "required": False, "spec_label": "OS Disk Size",
             "options": ["30","64","128","256","512"],"default": "30"},
            {"key": "inbound_ports","label": "Inbound Ports",   "type": "select", "required": True,  "spec_label": "Inbound Ports",
             "options": ["HTTP (80), SSH (22)","HTTPS (443), SSH (22)","RDP (3389)","HTTP (80), HTTPS (443), SSH (22)","None"],
             "default": "HTTP (80), SSH (22)"},
            {"key": "auth_type",    "label": "Authentication",  "type": "select", "required": False, "spec_label": "Authentication",
             "options": ["SSH Public Key","Password"],"default": "SSH Public Key"},
        ],
        "task_template": [
            "Create an Azure Virtual Machine with the same name as the Resource Group provided.",
            "Set the region to {region}.",
            "Use the image '{vm_image}' for the operating system.",
            "Select the '{vm_size}' VM size.",
            "Configure authentication using {auth_type}.",
            "Attach a new OS disk of type '{disk_type}' with {disk_size_gb} GB.",
            "Set the inbound port rules to allow {inbound_ports}.",
            "Enable Boot Diagnostics using a managed storage account.",
        ],
        "task_intro": "Task Details:",
        "policy_extra_info": "Allows VM, disk, NIC, VNet, NSG, and public IP resources. All others denied.",
    },

    # ── Azure Kubernetes Service ───────────────────────────────────────────────
    "Azure Kubernetes Service": {
        "role_options": [
            "DevOps Engineer",
            "Kubernetes Administrator",
            "Platform Engineer",
        ],
        "context_options": [
            "deploying a managed Kubernetes cluster on Azure to orchestrate containerized microservices. The cluster must be configured with the correct node pool settings, RBAC, and monitoring.",
            "provisioning an Azure Kubernetes Service (AKS) cluster to host multiple application workloads. Configure the cluster to meet the company's availability and security requirements.",
            "setting up an AKS cluster for a CI/CD pipeline that deploys containerized applications. Ensure the cluster is configured with the correct Kubernetes version and networking.",
        ],
        "fields": [
            {"key": "region",          "label": "Region",           "type": "select", "required": True,  "spec_label": "Region",
             "options": ["East US 2","West US 2","North Europe","Southeast Asia","Central India","East US"],
             "default": "East US 2"},
            {"key": "k8s_version",     "label": "Kubernetes Version","type": "select", "required": True,  "spec_label": "Kubernetes Version",
             "options": ["1.29.2","1.28.5","1.27.9","1.26.10"],"default": "1.28.5"},
            {"key": "node_count",      "label": "Node Count",       "type": "select", "required": True,  "spec_label": "Node Count",
             "options": ["1","2","3","5"],"default": "2"},
            {"key": "node_size",       "label": "Node VM Size",     "type": "select", "required": True,  "spec_label": "Node VM Size",
             "options": ["Standard_DS2_v2","Standard_B2ms","Standard_D4s_v3","Standard_D2s_v3"],
             "default": "Standard_DS2_v2"},
            {"key": "os_disk_size",    "label": "OS Disk Size (GB)","type": "select", "required": False, "spec_label": "OS Disk Size",
             "options": ["100","128","256"],"default": "128"},
            {"key": "network_plugin",  "label": "Network Plugin",   "type": "select", "required": True,  "spec_label": "Network Plugin",
             "options": ["kubenet","Azure CNI"],"default": "kubenet"},
        ],
        "task_template": [
            "Create an Azure Kubernetes Service (AKS) cluster named after your Resource Group (append '-aks').",
            "Set the region to {region}.",
            "Configure the node pool with {node_count} node(s) using the '{node_size}' VM size.",
            "Set the Kubernetes version to {k8s_version}.",
            "Enable RBAC on the cluster.",
            "Configure the network plugin as '{network_plugin}'.",
            "Set the OS disk size to {os_disk_size} GB per node.",
            "Enable the Container Insights monitoring add-on.",
        ],
        "task_intro": "Task Details:",
        "policy_extra_info": "Allows AKS cluster, node pool, container registry, VNet, load balancer, and public IP resources.",
    },

    # ── Azure SQL Database ────────────────────────────────────────────────────
    "Azure SQL Database": {
        "role_options": [
            "Database Administrator",
            "Azure Data Engineer",
            "Backend Developer",
        ],
        "context_options": [
            "provisioning a managed relational database on Azure to serve as the persistent store for an e-commerce application. The database must be configured with the appropriate service tier, firewall rules, and data protection settings.",
            "deploying an Azure SQL Database to store transactional data. Ensure the database is secured, backed up appropriately, and accessible only to authorized Azure services.",
            "setting up a production Azure SQL Database for a SaaS application. Configure the server, database, and all required security settings.",
        ],
        "fields": [
            {"key": "region",        "label": "Region",           "type": "select", "required": True,  "spec_label": "Location",
             "options": ["East US","West US 2","West Europe","Southeast Asia","Central India","North Europe","East US 2"],
             "default": "East US"},
            {"key": "admin_login",   "label": "Admin Login",      "type": "text",   "required": True,  "spec_label": "Admin Login",
             "default": "sqladmin"},
            {"key": "db_name",       "label": "Database Name",    "type": "text",   "required": True,  "spec_label": "Database Name",
             "default": "assessmentdb"},
            {"key": "service_tier",  "label": "Service Tier",     "type": "select", "required": True,  "spec_label": "Service Tier",
             "options": ["General Purpose (GP_Gen5_2)","Basic (B)","Standard (S1)","Standard (S3)","Business Critical (BC_Gen5_2)"],
             "default": "Basic (B)"},
            {"key": "backup_days",   "label": "Backup Retention (days)","type":"select","required": True, "spec_label": "Backup Retention",
             "options": ["7","14","30","35"],"default": "7"},
            {"key": "tde",           "label": "Transparent Data Encryption","type":"select","required": False,"spec_label": "TDE",
             "options": ["Enabled","Disabled"],"default": "Enabled"},
        ],
        "task_template": [
            "Create an Azure SQL Server named after your Resource Group (append '-sqlserver').",
            "Set the location to {region}.",
            "Set the SQL Server Admin login to '{admin_login}'.",
            "Create a SQL Database named '{db_name}' on the server.",
            "Select the '{service_tier}' service tier.",
            "Configure the firewall to allow Azure services to access the server.",
            "Enable Transparent Data Encryption (TDE) on the database.",
            "Set the backup retention to {backup_days} days.",
        ],
        "task_intro": "Task Details:",
        "policy_extra_info": "Allows SQL Server, database, elastic pool, firewall rules, and audit settings. All others denied.",
    },

    # ── App Service ───────────────────────────────────────────────────────────
    "App Service": {
        "role_options": [
            "DevOps Engineer",
            "Web Developer",
            "Cloud Engineer",
        ],
        "context_options": [
            "deploying a web application using Azure App Service. Your goal is to configure the App Service with the correct runtime, plan tier, and application settings for production use.",
            "migrating an on-premises web application to Azure App Service. Configure the App Service Plan, runtime stack, and security settings as required.",
            "hosting a REST API backend on a managed PaaS platform using Azure App Service. Configure the service for production-grade availability and security.",
        ],
        "fields": [
            {"key": "region",          "label": "Region",             "type": "select", "required": True,  "spec_label": "Region",
             "options": ["East US","West US 2","Southeast Asia","West Europe","Central India","North Europe"],
             "default": "East US"},
            {"key": "plan_tier",       "label": "App Service Plan Tier","type":"select","required": True,  "spec_label": "App Service Plan Tier",
             "options": ["Free (F1)","Basic (B1)","Basic (B2)","Standard (S1)","Standard (S2)","Premium (P1v3)"],
             "default": "Basic (B1)"},
            {"key": "runtime",         "label": "Runtime Stack",      "type": "select", "required": True,  "spec_label": "Runtime Stack",
             "options": ["Node.js 20 LTS","Python 3.11","Python 3.12",".NET 8","Java 17","PHP 8.2"],
             "default": "Node.js 20 LTS"},
            {"key": "https_only",      "label": "HTTPS Only",         "type": "select", "required": False, "spec_label": "HTTPS Only",
             "options": ["Enabled","Disabled"],"default": "Enabled"},
            {"key": "min_tls",         "label": "Minimum TLS Version","type": "select", "required": False, "spec_label": "Minimum TLS Version",
             "options": ["1.0","1.1","1.2","1.3"],"default": "1.2"},
            {"key": "app_setting_key", "label": "App Setting Key",    "type": "text",   "required": False, "spec_label": "App Setting",
             "default": "WEBSITE_RUN_FROM_PACKAGE",
             "help": "Key name for the application setting to configure"},
        ],
        "task_template": [
            "Create an Azure App Service with the same name as your Resource Group.",
            "Create an App Service Plan in the '{plan_tier}' tier.",
            "Set the region to {region}.",
            "Set the runtime stack to '{runtime}'.",
            "Enable HTTPS-only access on the App Service.",
            "Set the minimum TLS version to {min_tls}.",
            "Configure the application setting '{app_setting_key}' with the appropriate value.",
        ],
        "task_intro": "Task Details:",
        "policy_extra_info": "Allows App Service, service plan, and associated configuration resources.",
    },

    # ── Azure Functions ───────────────────────────────────────────────────────
    "Azure Functions": {
        "role_options": [
            "Serverless Developer",
            "DevOps Engineer",
            "Cloud Engineer",
        ],
        "context_options": [
            "implementing event-driven processing using Azure Functions for a mobile application backend. The Function App must be configured with the correct hosting plan, runtime, and an HTTP trigger to accept incoming requests.",
            "automating order processing workflows using Azure Functions. Configure the Function App with the appropriate settings and monitoring.",
            "building a serverless API backend using Azure Functions. The Function App must be set up with the correct runtime version and authorization settings.",
        ],
        "fields": [
            {"key": "region",          "label": "Region",           "type": "select", "required": True,  "spec_label": "Region",
             "options": ["East US","West Europe","Southeast Asia","Central India","West US 2","North Europe"],
             "default": "East US"},
            {"key": "hosting_plan",    "label": "Hosting Plan",     "type": "select", "required": True,  "spec_label": "Hosting Plan",
             "options": ["Consumption Plan","Premium Plan (EP1)","Dedicated (App Service)"],
             "default": "Consumption Plan"},
            {"key": "runtime",         "label": "Runtime",          "type": "select", "required": True,  "spec_label": "Runtime",
             "options": ["Node.js 20","Python 3.11","Python 3.12",".NET 8","Java 17"],
             "default": "Node.js 20"},
            {"key": "function_name",   "label": "Function Name",    "type": "text",   "required": True,  "spec_label": "Function Name",
             "default": "HttpTrigger1"},
            {"key": "auth_level",      "label": "Authorization Level","type":"select","required": True,  "spec_label": "Authorization Level",
             "options": ["Function","Anonymous","Admin"],"default": "Function"},
        ],
        "task_template": [
            "Create an Azure Function App named after your Resource Group (append '-func').",
            "Set the region to {region}.",
            "Select the '{hosting_plan}' hosting plan.",
            "Set the runtime to '{runtime}'.",
            "Create an HTTP-triggered function named '{function_name}'.",
            "Set the authorization level to '{auth_level}'.",
            "Link the Function App to a Storage Account for internal state management.",
            "Enable Application Insights for monitoring and diagnostics.",
        ],
        "task_intro": "Task Details:",
        "policy_extra_info": "Allows Function App, App Service plan, storage account, and Application Insights resources.",
    },

    # ── Event Hubs ────────────────────────────────────────────────────────────
    "Event Hubs": {
        "role_options": [
            "Data Engineer",
            "Platform Engineer",
            "Streaming Architect",
        ],
        "context_options": [
            "setting up a real-time event streaming pipeline using Azure Event Hubs. Your task is to provision an Event Hub namespace and configure the required partitions, retention, and consumer groups for a high-throughput IoT workload.",
            "building an event streaming backbone using Azure Event Hubs to process clickstream data. Configure the namespace and Event Hub with the appropriate throughput and retention settings.",
            "provisioning Azure Event Hubs to ingest telemetry data from IoT devices. The namespace must be configured with the correct SKU and the Event Hub with appropriate partition count.",
        ],
        "fields": [
            {"key": "region",          "label": "Region",             "type": "select", "required": True,  "spec_label": "Region",
             "options": ["East US","West US 2","West Europe","Southeast Asia","Central India","North Europe"],
             "default": "East US"},
            {"key": "sku",             "label": "Pricing Tier",       "type": "select", "required": True,  "spec_label": "Pricing Tier",
             "options": ["Basic","Standard","Premium"],"default": "Standard"},
            {"key": "throughput",      "label": "Throughput Units",   "type": "select", "required": True,  "spec_label": "Throughput Units",
             "options": ["1","2","4","8","10"],"default": "1"},
            {"key": "hub_name",        "label": "Event Hub Name",     "type": "text",   "required": True,  "spec_label": "Event Hub Name",
             "default": "assessment-hub"},
            {"key": "partitions",      "label": "Partition Count",    "type": "select", "required": True,  "spec_label": "Partition Count",
             "options": ["2","4","8","16","32"],"default": "4"},
            {"key": "retention",       "label": "Message Retention (days)","type":"select","required": True, "spec_label": "Message Retention",
             "options": ["1","3","7"],"default": "1"},
            {"key": "consumer_group",  "label": "Consumer Group Name","type": "text",   "required": False, "spec_label": "Consumer Group",
             "default": "$Default"},
        ],
        "task_template": [
            "Create an Event Hubs Namespace named after your Resource Group (append '-ehns').",
            "Set the region to {region}.",
            "Select the '{sku}' pricing tier.",
            "Set throughput units to {throughput}.",
            "Create an Event Hub named '{hub_name}' within the namespace.",
            "Set the partition count to {partitions}.",
            "Set the message retention to {retention} day(s).",
            "Create a consumer group named '{consumer_group}'.",
        ],
        "task_intro": "Task Details:",
        "policy_extra_info": "Allows Event Hub namespace, event hubs, consumer groups, and authorization rules.",
    },

    # ── Azure DNS ─────────────────────────────────────────────────────────────
    "Azure DNS": {
        "role_options": [
            "Network Engineer",
            "Azure Administrator",
            "Cloud Architect",
        ],
        "context_options": [
            "configuring Azure DNS to manage domain records for a corporate website. Your goal is to create a DNS zone and configure the required record sets to ensure the domain resolves correctly.",
            "migrating DNS management to Azure DNS for centralized control of your organization's domain records. Configure the DNS zone with all required record types.",
            "setting up an Azure DNS zone for a public-facing application. Configure A, CNAME, and TXT records as required.",
        ],
        "fields": [
            {"key": "zone_name",    "label": "DNS Zone (domain)",  "type": "text",   "required": True,  "spec_label": "DNS Zone",
             "default": "contoso.com"},
            {"key": "a_record_ip",  "label": "A Record IP Address","type": "text",   "required": True,  "spec_label": "A Record IP",
             "default": "52.168.1.1",
             "help": "IP address for the root @ A record"},
            {"key": "cname_target", "label": "CNAME Target",       "type": "text",   "required": True,  "spec_label": "CNAME Target",
             "default": "contoso.azurewebsites.net",
             "help": "Target hostname for www CNAME record"},
            {"key": "ttl",          "label": "TTL (seconds)",      "type": "select", "required": True,  "spec_label": "TTL",
             "options": ["60","300","600","3600"],"default": "300"},
        ],
        "task_template": [
            "Create an Azure DNS Zone for the domain '{zone_name}'.",
            "Set the resource group to the one provided to you.",
            "Create an A record pointing '@' to IP address {a_record_ip} with TTL {ttl} seconds.",
            "Create a CNAME record for 'www' pointing to '{cname_target}' with TTL {ttl} seconds.",
            "Create a TXT record for domain ownership verification.",
            "Note the Name Server (NS) records assigned by Azure and update your domain registrar.",
        ],
        "task_intro": "Task Details:",
        "policy_extra_info": "Allows DNS zone and all DNS record types (A, AAAA, CNAME, MX, NS, SOA, TXT). All others denied.",
    },

    # ── Cosmos DB ─────────────────────────────────────────────────────────────
    "Cosmos DB": {
        "role_options": [
            "Azure Data Engineer",
            "Backend Developer",
            "Database Administrator",
        ],
        "context_options": [
            "provisioning a globally distributed NoSQL database using Azure Cosmos DB for a multi-region application. The account must be configured with geo-redundancy and the appropriate API and throughput settings.",
            "setting up Azure Cosmos DB as the document store for a real-time leaderboard service. Configure the account with low-latency access and a container with the correct partition key.",
            "deploying an Azure Cosmos DB account to serve as the primary data store for a mobile application. Configure the database and containers with appropriate throughput and partitioning.",
        ],
        "fields": [
            {"key": "region",           "label": "Region",               "type": "select", "required": True,  "spec_label": "Region",
             "options": ["East US","West US 2","West Europe","Southeast Asia","Central India","North Europe"],
             "default": "East US"},
            {"key": "api",              "label": "API",                  "type": "select", "required": True,  "spec_label": "API",
             "options": ["Core (SQL)","MongoDB","Gremlin","Table","Cassandra"],
             "default": "Core (SQL)"},
            {"key": "capacity_mode",    "label": "Capacity Mode",        "type": "select", "required": True,  "spec_label": "Capacity Mode",
             "options": ["Provisioned Throughput","Serverless"],"default": "Provisioned Throughput"},
            {"key": "secondary_region", "label": "Secondary Region",     "type": "select", "required": True,  "spec_label": "Secondary Region",
             "options": ["West US 2","North Europe","East Asia","UK South","Southeast Asia"],
             "default": "West US 2"},
            {"key": "db_name",          "label": "Database Name",        "type": "text",   "required": True,  "spec_label": "Database Name",
             "default": "assessmentdb"},
            {"key": "container_name",   "label": "Container Name",       "type": "text",   "required": True,  "spec_label": "Container Name",
             "default": "items"},
            {"key": "partition_key",    "label": "Partition Key",        "type": "text",   "required": True,  "spec_label": "Partition Key",
             "default": "id",
             "help": "Partition key path without leading /"},
            {"key": "throughput",       "label": "Throughput (RU/s)",    "type": "select", "required": False, "spec_label": "Throughput",
             "options": ["400","1000","4000","10000"],"default": "400"},
        ],
        "task_template": [
            "Create an Azure Cosmos DB account named after your Resource Group (append '-cosmos').",
            "Set the location to {region}.",
            "Select the '{api}' API.",
            "Choose the '{capacity_mode}' capacity mode.",
            "Enable geo-redundancy by adding a secondary read region in '{secondary_region}'.",
            "Create a database named '{db_name}'.",
            "Create a container named '{container_name}' with partition key '/{partition_key}'.",
            "Set the throughput to {throughput} RU/s.",
        ],
        "task_intro": "Task Details:",
        "policy_extra_info": "Allows Cosmos DB account and all API-specific database/container resources.",
    },

    # ── Virtual Networks ──────────────────────────────────────────────────────
    "Virtual Networks": {
        "role_options": [
            "Network Engineer",
            "Azure Administrator",
            "Cloud Architect",
        ],
        "context_options": [
            "setting up an Azure Virtual Network to isolate application tiers for a multi-tier web application. Configure the VNet with the correct address space, subnets, and an NSG to control traffic.",
            "provisioning network infrastructure for a production workload on Azure. Your task is to create a Virtual Network with appropriate subnets and network security rules.",
            "configuring a hub-spoke Virtual Network topology for your organization. Create the VNet with the required address space and subnet configuration.",
        ],
        "fields": [
            {"key": "region",        "label": "Region",           "type": "select", "required": True,  "spec_label": "Region",
             "options": ["East US","West US 2","Central India","North Europe","West Europe","Southeast Asia"],
             "default": "East US"},
            {"key": "vnet_name",     "label": "VNet Name",        "type": "text",   "required": True,  "spec_label": "VNet Name",
             "default": "health-vnet"},
            {"key": "address_space", "label": "Address Space",    "type": "select", "required": True,  "spec_label": "Address Space",
             "options": ["10.0.0.0/16","172.16.0.0/16","192.168.0.0/16","10.1.0.0/16"],
             "default": "10.0.0.0/16"},
            {"key": "subnet_name",   "label": "Subnet Name",      "type": "text",   "required": True,  "spec_label": "Subnet Name",
             "default": "app-subnet"},
            {"key": "subnet_range",  "label": "Subnet Range",     "type": "select", "required": True,  "spec_label": "Subnet Range",
             "options": ["10.0.1.0/24","10.0.2.0/24","172.16.1.0/24","192.168.1.0/24"],
             "default": "10.0.1.0/24"},
            {"key": "nsg_name",      "label": "NSG Name",         "type": "text",   "required": False, "spec_label": "NSG Name",
             "default": "app-nsg"},
        ],
        "task_template": [
            "Create an Azure Virtual Network named '{vnet_name}'.",
            "Set the region to {region}.",
            "Configure the address space as '{address_space}'.",
            "Create a subnet named '{subnet_name}' with address range '{subnet_range}'.",
            "Create a Network Security Group (NSG) named '{nsg_name}' and associate it with the subnet.",
            "Add an inbound security rule to allow HTTP (port 80) traffic.",
            "Add an inbound security rule to allow HTTPS (port 443) traffic.",
        ],
        "task_intro": "Task Details:",
        "policy_extra_info": "Allows VNet, subnets, NSG, private DNS, private endpoints, NIC, and public IP resources.",
    },

    # ── Service Bus ───────────────────────────────────────────────────────────
    "Service Bus": {
        "role_options": [
            "Integration Engineer",
            "Backend Developer",
            "Messaging Architect",
        ],
        "context_options": [
            "implementing reliable message-based communication between microservices using Azure Service Bus. Configure the namespace and queue with the correct settings for guaranteed message delivery and dead-letter handling.",
            "setting up Azure Service Bus to handle asynchronous order processing. Create the Service Bus namespace and configure a queue with appropriate lock duration and dead-letter settings.",
            "configuring Azure Service Bus as the messaging backbone for a distributed application. Set up the namespace, queue, and required access policies.",
        ],
        "fields": [
            {"key": "region",         "label": "Region",              "type": "select", "required": True,  "spec_label": "Region",
             "options": ["East US","West US 2","North Europe","Southeast Asia","West Europe","Central India"],
             "default": "East US"},
            {"key": "sku",            "label": "Pricing Tier",        "type": "select", "required": True,  "spec_label": "Pricing Tier",
             "options": ["Basic","Standard","Premium"],"default": "Standard"},
            {"key": "queue_name",     "label": "Queue Name",          "type": "text",   "required": True,  "spec_label": "Queue Name",
             "default": "assessment-queue"},
            {"key": "lock_duration",  "label": "Lock Duration",       "type": "select", "required": True,  "spec_label": "Lock Duration",
             "options": ["PT30S","PT1M","PT5M","PT10M"],"default": "PT1M"},
            {"key": "max_size",       "label": "Max Message Size (KB)","type":"select","required": True,  "spec_label": "Max Message Size",
             "options": ["256","1024","4096"],"default": "256"},
        ],
        "task_template": [
            "Create a Service Bus Namespace named after your Resource Group (append '-sbns').",
            "Set the region to {region}.",
            "Select the '{sku}' pricing tier.",
            "Create a Queue named '{queue_name}'.",
            "Enable Dead Letter Queue on message expiration.",
            "Set the message lock duration to '{lock_duration}'.",
            "Set the maximum message size to {max_size} KB.",
        ],
        "task_intro": "Task Details:",
        "policy_extra_info": "Allows Service Bus namespace, queues, topics, subscriptions, and authorization rules.",
    },

    # ── Network Security Groups ───────────────────────────────────────────────
    "Network Security Groups": {
        "role_options": [
            "Network Security Engineer",
            "Azure Administrator",
            "Security Architect",
        ],
        "context_options": [
            "securing network traffic to a virtual machine deployment using Azure Network Security Groups. Your task is to create an NSG with specific inbound rules and associate it with the target subnet.",
            "implementing perimeter security for an application subnet using Network Security Groups. Configure the NSG rules to enforce least-privilege access and block unnecessary traffic.",
            "configuring NSG rules to enforce least-privilege network access for a production workload. Create the NSG, define the required rules, and associate it with the correct subnet.",
        ],
        "fields": [
            {"key": "region",         "label": "Region",            "type": "select", "required": True,  "spec_label": "Region",
             "options": ["East US","West US 2","Central India","West Europe","North Europe","Southeast Asia"],
             "default": "East US"},
            {"key": "nsg_name",       "label": "NSG Name",          "type": "text",   "required": True,  "spec_label": "NSG Name",
             "default": "app-nsg"},
            {"key": "allow_ssh",      "label": "Allow SSH (22)",    "type": "select", "required": True,  "spec_label": "Allow SSH",
             "options": ["Yes","No"],"default": "Yes"},
            {"key": "allow_http",     "label": "Allow HTTP (80)",   "type": "select", "required": True,  "spec_label": "Allow HTTP",
             "options": ["Yes","No"],"default": "Yes"},
            {"key": "allow_https",    "label": "Allow HTTPS (443)", "type": "select", "required": True,  "spec_label": "Allow HTTPS",
             "options": ["Yes","No"],"default": "Yes"},
            {"key": "allow_rdp",      "label": "Allow RDP (3389)",  "type": "select", "required": False, "spec_label": "Allow RDP",
             "options": ["Yes","No"],"default": "No"},
            {"key": "subnet_name",    "label": "Associate with Subnet","type":"text","required": False, "spec_label": "Associated Subnet",
             "default": "app-subnet"},
        ],
        "task_template": [
            "Create a Network Security Group named '{nsg_name}'.",
            "Set the region to {region}.",
            "{ssh_rule_task}",
            "{http_rule_task}",
            "{https_rule_task}",
            "Associate the NSG with the subnet '{subnet_name}'.",
        ],
        "task_intro": "Task Details:",
        "policy_extra_info": "Allows NSG, security rules, VNet, subnet, network watcher, and flow log resources.",
    },
}


# ─── HELPER: render tasks with actual field values ────────────────────────────

def render_tasks(service_display: str, field_values: Dict[str, str]) -> List[str]:
    """Render task list replacing {key} with actual values from form."""
    tmpl = SERVICE_FIELDS.get(service_display, {})
    
    # Special handling for services with conditional tasks
    if service_display == "Storage Accounts":
        if field_values.get("blob_container", "").strip():
            task_list = tmpl.get("task_template_with_blob", tmpl["task_template"])
        else:
            task_list = tmpl["task_template"]
    elif service_display == "Key Vault":
        task_list = list(tmpl["task_template"])
        # Replace public_access_task placeholder
        if field_values.get("public_access") == "Disabled":
            pa_task = "Disable public access to the created Azure Key Vault."
        else:
            pa_task = "Enable public access on the Azure Key Vault."
        task_list = [t if t != "{public_access_task}" else pa_task for t in task_list]
    elif service_display == "Network Security Groups":
        task_list = []
        base = tmpl["task_template"]
        for t in base:
            if t == "{ssh_rule_task}":
                if field_values.get("allow_ssh") == "Yes":
                    task_list.append("Add an inbound rule to allow SSH (port 22) from your IP.")
            elif t == "{http_rule_task}":
                if field_values.get("allow_http") == "Yes":
                    task_list.append("Add an inbound rule to allow HTTP (port 80) from any source.")
            elif t == "{https_rule_task}":
                if field_values.get("allow_https") == "Yes":
                    task_list.append("Add an inbound rule to allow HTTPS (port 443) from any source.")
            else:
                task_list.append(t)
    else:
        task_list = list(tmpl.get("task_template", []))

    rendered = []
    for task in task_list:
        for k, v in field_values.items():
            task = task.replace("{" + k + "}", str(v))
        rendered.append(task)
    return rendered


def render_specs(service_display: str, field_values: Dict[str, str]) -> Dict[str, str]:
    """Build ordered specifications dict from field values."""
    tmpl = SERVICE_FIELDS.get(service_display, {})
    specs = {"Name": "[Your Resource Group Name]"}
    for field in tmpl.get("fields", []):
        val = field_values.get(field["key"], "")
        if val:
            # Special formatting per field
            if field["key"] == "cpu":
                specs[field["spec_label"]] = f"{val} vCPU"
            elif field["key"] == "memory":
                specs[field["spec_label"]] = f"{val} GB"
            elif field["key"] == "disk_size_gb":
                specs[field["spec_label"]] = f"{val} GB"
            elif field["key"] == "os_disk_size":
                specs[field["spec_label"]] = f"{val} GB"
            elif field["key"] == "backup_days":
                specs[field["spec_label"]] = f"{val} days"
            elif field["key"] == "throughput" and service_display == "Cosmos DB":
                specs[field["spec_label"]] = f"{val} RU/s"
            elif field["key"] == "partition_key":
                specs[field["spec_label"]] = f"/{val}"
            elif field["key"] == "replication":
                specs[field["spec_label"]] = f"Locally-redundant storage ({val})"
            else:
                specs[field["spec_label"]] = val
    return specs