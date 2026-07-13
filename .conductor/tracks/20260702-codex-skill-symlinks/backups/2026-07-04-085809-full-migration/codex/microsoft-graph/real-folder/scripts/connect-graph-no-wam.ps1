<#
.SYNOPSIS
    Connect to Microsoft Graph without MSAL/WAM account-picker prompts.

.DESCRIPTION
    Uses the OAuth2 client_credentials flow directly with a certificate-signed JWT
    client assertion, then connects Microsoft Graph PowerShell with a pre-minted
    SecureString access token.

    This intentionally bypasses Microsoft.Graph/Identity/MSAL token acquisition.
    On 2026-05-04, Connect-MgGraph -CertificateThumbprint successfully connected
    as AppOnly, but still triggered Microsoft Web Account Manager (WAM) account
    picker popups for Dave's multiple Microsoft accounts. User-level environment
    variables such as MSAL_DISABLE_WAM=true and AZURE_PS_DISABLE_WAM=true did not
    reliably suppress the picker. Direct REST token minting did.

    This script does not change normal browser sign-in behavior. It only affects
    this PowerShell process and this programmatic Graph connection.

.PARAMETER ClientId
    Entra app registration client ID.

.PARAMETER TenantId
    Entra tenant ID.

.PARAMETER CertThumbprint
    Thumbprint of the app-only certificate in Cert:\CurrentUser\My.

.PARAMETER Scope
    OAuth scope. Defaults to https://graph.microsoft.com/.default.

.PARAMETER PassThru
    Return the Microsoft Graph context after connecting.

.EXAMPLE
    . "C:\Users\DaveWitkin\.opencode-lazy-vault\microsoft-graph\scripts\connect-graph-no-wam.ps1"
    Connect-GraphNoWam -ClientId $ClientId -TenantId $TenantId -CertThumbprint $CertThumbprint
    Get-MgUserMessage -UserId "dave.witkin@packagedagile.com" -Top 1
#>

[CmdletBinding()]
param(
    [string]$CommandClientId,
    [string]$CommandTenantId,
    [string]$CommandCertThumbprint,
    [string]$CommandScope = 'https://graph.microsoft.com/.default',
    [switch]$Connect,
    [switch]$PassThru
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function ConvertTo-Base64Url {
    param([Parameter(Mandatory)][byte[]]$Bytes)
    return [Convert]::ToBase64String($Bytes).TrimEnd('=').Replace('+', '-').Replace('/', '_')
}

function Get-GraphNoWamAccessToken {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$ClientId,
        [Parameter(Mandatory)][string]$TenantId,
        [Parameter(Mandatory)][string]$CertThumbprint,
        [string]$Scope = 'https://graph.microsoft.com/.default'
    )

    # Best-effort guard for any module imports that might otherwise initialize WAM.
    $env:MSAL_DISABLE_WAM = 'true'
    $env:AZURE_PS_DISABLE_WAM = 'true'
    $env:MSAL_ENABLE_WAM = 'false'

    $cert = Get-Item -Path "Cert:\CurrentUser\My\$CertThumbprint" -ErrorAction SilentlyContinue
    if (-not $cert) {
        throw "Certificate thumbprint $CertThumbprint not found in Cert:\CurrentUser\My"
    }
    if ($cert.NotAfter -lt (Get-Date)) {
        throw "Certificate $CertThumbprint expired on $($cert.NotAfter)"
    }

    $rsa = [System.Security.Cryptography.X509Certificates.RSACertificateExtensions]::GetRSAPrivateKey($cert)
    if (-not $rsa) {
        throw "Certificate $CertThumbprint does not expose an RSA private key to the current user"
    }

    $tokenEndpoint = "https://login.microsoftonline.com/$TenantId/oauth2/v2.0/token"
    $now = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()

    $header = @{
        alg = 'RS256'
        typ = 'JWT'
        x5t = ConvertTo-Base64Url -Bytes $cert.GetCertHash()
    }
    $payload = @{
        aud = $tokenEndpoint
        iss = $ClientId
        sub = $ClientId
        jti = [Guid]::NewGuid().ToString()
        nbf = $now
        exp = ($now + 300)
    }

    $headerJson = $header | ConvertTo-Json -Compress
    $payloadJson = $payload | ConvertTo-Json -Compress
    $headerB64 = ConvertTo-Base64Url -Bytes ([System.Text.Encoding]::UTF8.GetBytes($headerJson))
    $payloadB64 = ConvertTo-Base64Url -Bytes ([System.Text.Encoding]::UTF8.GetBytes($payloadJson))
    $signInput = "$headerB64.$payloadB64"
    $signature = $rsa.SignData(
        [System.Text.Encoding]::ASCII.GetBytes($signInput),
        [System.Security.Cryptography.HashAlgorithmName]::SHA256,
        [System.Security.Cryptography.RSASignaturePadding]::Pkcs1
    )
    $assertion = "$signInput.$(ConvertTo-Base64Url -Bytes $signature)"

    $response = Invoke-RestMethod -Uri $tokenEndpoint -Method POST -ContentType 'application/x-www-form-urlencoded' -TimeoutSec 30 -Body @{
        client_id             = $ClientId
        client_assertion_type = 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer'
        client_assertion      = $assertion
        scope                 = $Scope
        grant_type            = 'client_credentials'
    }

    return $response.access_token
}

function ConvertTo-SecureToken {
    param([Parameter(Mandatory)][string]$AccessToken)
    $secureToken = [System.Security.SecureString]::new()
    foreach ($char in $AccessToken.ToCharArray()) {
        $secureToken.AppendChar($char)
    }
    $secureToken.MakeReadOnly()
    return $secureToken
}

function Connect-GraphNoWam {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$ClientId,
        [Parameter(Mandatory)][string]$TenantId,
        [Parameter(Mandatory)][string]$CertThumbprint,
        [string]$Scope = 'https://graph.microsoft.com/.default',
        [switch]$PassThru
    )

    Import-Module Microsoft.Graph.Authentication -ErrorAction Stop

    $accessToken = Get-GraphNoWamAccessToken -ClientId $ClientId -TenantId $TenantId -CertThumbprint $CertThumbprint -Scope $Scope
    $secureToken = ConvertTo-SecureToken -AccessToken $accessToken
    Connect-MgGraph -AccessToken $secureToken -NoWelcome -ErrorAction Stop

    if ($PassThru) {
        return Get-MgContext
    }
}

if ($Connect) {
    if (-not $CommandClientId -or -not $CommandTenantId -or -not $CommandCertThumbprint) {
        throw 'When using -Connect, provide -CommandClientId, -CommandTenantId, and -CommandCertThumbprint.'
    }
    Connect-GraphNoWam -ClientId $CommandClientId -TenantId $CommandTenantId -CertThumbprint $CommandCertThumbprint -Scope $CommandScope -PassThru:$PassThru
}
