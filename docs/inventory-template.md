# Cloud Migration Inventory Template

Use this template to collect the minimum information required to assess virtual machines for cloud migration.

## Client Information

| Field | Value |
| --- | --- |
| Client name |  |
| Business unit |  |
| Technical contact |  |
| Cloud target | Azure / Huawei Cloud |
| Target region |  |
| Assessment date |  |

## Required VM Inventory Fields

| Field | Description | Example |
| --- | --- | --- |
| vm_name | Current server or VM name | erp-app-01 |
| application_name | Application or service hosted by the VM | ERP |
| environment | prod, qa, dev, test | prod |
| business_owner | Owner of the business process | Finance |
| technical_owner | Infrastructure or application owner | IT Operations |
| operating_system | windows or linux | windows |
| os_version | OS version and build | Windows Server 2019 |
| current_platform | VMware, Hyper-V, physical, cloud | VMware |
| datacenter_location | Current location | Mexico City DC1 |
| cpu_cores | Allocated vCPU count | 8 |
| memory_gb | Allocated RAM in GB | 32 |
| storage_gb | Total allocated disk in GB | 500 |
| disk_count | Number of attached disks | 3 |
| average_cpu_percent | 30-day average CPU usage | 55 |
| peak_cpu_percent | 30-day peak CPU usage | 82 |
| average_memory_percent | 30-day average memory usage | 68 |
| peak_memory_percent | 30-day peak memory usage | 91 |
| average_disk_iops | Average disk IOPS | 1200 |
| average_disk_throughput_mbps | Average disk throughput | 80 |
| network_in_mbps | Average inbound network traffic | 25 |
| network_out_mbps | Average outbound network traffic | 18 |
| criticality | low, medium, high, mission_critical | high |
| uptime_requirement | Business uptime expectation | 99.9% |
| rpo_minutes | Maximum acceptable data loss | 60 |
| rto_minutes | Maximum acceptable recovery time | 240 |
| backup_policy | Current backup frequency and retention | Daily, 30 days |
| maintenance_window | Approved change window | Sunday 01:00-04:00 |
| uses_active_directory | true or false | true |
| domain_joined | true or false | true |
| requires_static_ip | true or false | true |
| requires_vpn_connectivity | true or false | true |
| internet_access_required | true or false | false |
| listening_ports | Ports exposed by the VM | 443;3389 |
| dependency_flows | Source, destination, port dependencies | erp-app-01->sql-prod-01:1433 |
| compliance_requirements | PCI, ISO, HIPAA, internal policy | ISO 27001 |
| migration_notes | Known risks, constraints, special handling | Requires vendor validation |

## Questions For The Client

1. Which applications are business-critical and cannot tolerate extended downtime?
2. Which servers are part of the same application dependency group?
3. Are there hardcoded IP addresses, DNS records, certificates, or firewall rules?
4. Which workloads require Active Directory, LDAP, DNS, file shares, or database connectivity?
5. What is the approved maintenance window for each application?
6. What are the RPO and RTO requirements?
7. Are there regulatory or data residency requirements?
8. Which workloads can be rehosted as-is, and which require modernization?

## Assessment Outputs

With this inventory, CloudForge AI can generate:

- Initial target sizing.
- Migration risk level.
- Recommended migration strategy.
- Network and dependency validation checklist.
- Cloud readiness score.
- Terraform planning inputs.
- AI-generated migration recommendations.
