#requires -Version 5.1
[CmdletBinding()]
param([string]$OutFile = '.\snapshot.json')
$ErrorActionPreference = 'Stop'
# Fail closed: no report is written if collection fails. No remote queries.
$os = Get-CimInstance -ClassName Win32_OperatingSystem
$disks = @(Get-CimInstance -ClassName Win32_LogicalDisk -Filter 'DriveType=3' | ForEach-Object {
    if ($_.Size -gt 0) {
        [ordered]@{ free_percent = [math]::Round(100 * $_.FreeSpace / $_.Size, 1) }
    }
})
$interfaces = @(Get-NetIPConfiguration | Where-Object { $_.NetAdapter.Status -eq 'Up' } | ForEach-Object {
    $addresses = @($_.IPv4Address | ForEach-Object { $_.IPAddress })
    [ordered]@{
        has_ipv4 = ($addresses.Count -gt 0)
        has_apipa = (@($addresses | Where-Object { $_ -like '169.254.*' }).Count -gt 0)
        has_gateway = (@($_.IPv4DefaultGateway | Where-Object { $_.NextHop }).Count -gt 0)
        has_dns = (@($_.DNSServer | ForEach-Object { $_.ServerAddresses } | Where-Object { $_ }).Count -gt 0)
    }
})
$data = [ordered]@{
    schema_version = 1
    memory_free_percent = [math]::Round(100 * $os.FreePhysicalMemory / $os.TotalVisibleMemorySize, 1)
    disks = $disks
    interfaces = $interfaces
}
# Deliberate allowlist: no name, username, IP, MAC, SSID, serial or raw errors.
$data | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $OutFile -Encoding UTF8
Write-Output 'Snapshot written locally. Review before sharing.'
